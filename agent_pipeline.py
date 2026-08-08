import os
import json
import ssl
import urllib3
import requests
import chromadb
from typing import TypedDict, List
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from ai_provider import call_llm_with_prompt
old_request = requests.Session.request
def new_request(self, method, url, **kwargs):
    kwargs['verify'] = False
    return old_request(self, method, url, **kwargs)
requests.Session.request = new_request
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
print("[Agent Pipeline] Loading Global ML Models...")
GLOBAL_DB_PATH = os.path.join(os.path.dirname(__file__), "bns_chroma_db")
GLOBAL_CHROMA_CLIENT = chromadb.PersistentClient(path=GLOBAL_DB_PATH)
GLOBAL_BNS_COLLECTION = GLOBAL_CHROMA_CLIENT.get_collection(name="bns_sections")
GLOBAL_EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
print("[Agent Pipeline] ML Models Loaded.")
import httpx
old_httpx_client_init = httpx.Client.__init__
def new_httpx_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    old_httpx_client_init(self, *args, **kwargs)
httpx.Client.__init__ = new_httpx_client_init
old_httpx_async_client_init = httpx.AsyncClient.__init__
def new_httpx_async_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    old_httpx_async_client_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = new_httpx_async_client_init
class LegalState(TypedDict):
    narrative: str
    state: str
    district: str
    police_station: str
    extracted_facts: dict
    retrieved_sections: List[dict]
    final_fir: str
def extract_facts(state: LegalState):
    print("[*] Investigator Agent: Extracting facts...")
    prompt = ChatPromptTemplate.from_template(
        "You are an expert Indian Police Investigator. Extract key facts from this incident narrative.\n"
        "Return a strict JSON object with NO markdown wrapping, NO code blocks, and NO other text.\n"
        "Ensure keys match exactly: 'case_title', 'complainant', 'accused', 'incident_time', 'location', 'weapons', 'injuries', 'motive', 'stolen_items', 'legal_concepts'.\n"
        "For 'case_title', provide a very short, 3-6 word title summarizing the case (e.g. 'Armed Robbery at Shop').\n"
        "For 'legal_concepts', provide a comma-separated list of the abstract criminal themes present (e.g., 'domestic violence, wrongful confinement, cheating, kidnapping, hit and run').\n"
        "Keep ALL other values extremely concise (max 3-5 words) so they fit perfectly in small UI cards.\n"
        "If a fact is missing, put 'Unknown'.\n\n"
        "Narrative: {narrative}"
    )
    result = call_llm_with_prompt(prompt, {"narrative": state["narrative"]}, is_json=True, temperature=0)
    if result is None:
        print(f"Investigator AI Error (Likely Rate Limit). Falling back to mock data.")
        facts = {
            "case_title": "Aggravated Robbery",
            "complainant": "Victim",
            "accused": "Unknown assailant",
            "incident_time": "Recently",
            "location": state.get("police_station", "Local Area"),
            "weapons": "Blunt object",
            "injuries": "Minor",
            "motive": "Theft",
            "stolen_items": "Valuables",
            "legal_concepts": "robbery, theft, assault"
        }
    else:
        facts = result
    return {"extracted_facts": facts}
def retrieve_laws(state: LegalState):
    print("[*] Magistrate Agent: Multi-Querying BNS Vector Database...")
    facts = state["extracted_facts"]
    narrative = str(state.get('narrative', ''))
    from crime_pattern_engine import detect_crime_patterns
    pattern_result = detect_crime_patterns(narrative, facts)
    injected_sections = pattern_result["injected_sections"]
    special_acts = pattern_result["special_acts"]
    companion_guidance = pattern_result["companion_guidance"]
    extra_queries = pattern_result.get("extra_queries", [])
    mandatory_section_ids = pattern_result.get("mandatory_sections", [])
    forbidden_section_ids = pattern_result.get("forbidden_sections", set())
    all_metas = {}
    all_docs = {}
    for sec_id, entry in injected_sections.items():
        all_metas[sec_id] = entry["meta"]
        all_docs[sec_id] = entry["doc"]
    q1 = narrative[:500] if len(narrative) > 500 else narrative
    q2 = f"{facts.get('case_title', '')}. {facts.get('motive', '')}. {facts.get('injuries', '')}."
    q3 = f"Weapons: {facts.get('weapons', '')}. Injuries: {facts.get('injuries', '')}. Stolen items: {facts.get('stolen_items', '')}."
    q4 = facts.get('legal_concepts', '')
    all_queries = [q1, q2, q3, q4] + extra_queries
    for q in all_queries:
        if not q or len(q.strip()) < 3:
            continue
        vec = GLOBAL_EMBED_MODEL.encode([q]).tolist()
        res = GLOBAL_BNS_COLLECTION.query(query_embeddings=vec, n_results=6)
        if res and res['documents'] and len(res['documents']) > 0:
            docs_list = res['documents'][0]
            metas_list = res['metadatas'][0]
            for i in range(len(docs_list)):
                sec_id = metas_list[i].get('section')
                if sec_id and sec_id not in all_metas and sec_id not in forbidden_section_ids:
                    all_metas[sec_id] = metas_list[i]
                    all_docs[sec_id] = docs_list[i]
    raw_sections = []
    for sec_id, meta in all_metas.items():
        doc = all_docs[sec_id]
        chap = meta.get('chapter', 'Unknown Chapter')
        punish = meta.get('punishment', 'Unknown')
        ipc = meta.get('ipc_eq', 'Unknown')
        cog = meta.get('cognizable', 'Unknown')
        bail = meta.get('bailable', 'Unknown')
        subsection_hint = ""
        if sec_id in injected_sections:
            entry = injected_sections[sec_id]
            if entry["display_section"] != sec_id:
                subsection_hint = f" [USE SUBSECTION: {entry['display_section']}]"
        raw_sections.append(
            f"Section {sec_id}{subsection_hint}: {meta.get('title', '')}\n"
            f"Chapter: {chap} | IPC Eq: {ipc} | Cognizable: {cog} | Bailable: {bail}\n"
            f"Punishment: {punish}\n"
            f"Text: {doc[:300]}...\n"
        )
    print("[*] Magistrate Agent: Calling Enhanced LLM Prompt with Pattern Engine Guidance...")
    companion_text = companion_guidance if companion_guidance else "No additional companion guidance."
    prompt = ChatPromptTemplate.from_template(
        "You are an elite Indian Senior Public Prosecutor specializing in the Bharatiya Nyaya Sanhita (BNS, 2024).\n"
        "I will provide an incident narrative and a list of authoritative statutory BNS sections retrieved from our legal database.\n\n"
        "YOUR DUTY: Select the 5 to 9 MOST applicable BNS sections from the candidates below that fully cover ALL offences in the narrative.\n\n"
        "CRITICAL RULES:\n"
        "1. DO NOT HALLUCINATE: You must ONLY select from the Candidate Sections provided. DO NOT invent sections.\n"
        "2. COPY METADATA EXACTLY: The chapter_name, punishment, ipc_equivalent, cognizable, and bailable fields MUST be copied EXACTLY as written in the Candidate Section data. DO NOT modify them.\n"
        "3. MULTIPLE OFFENCES: Ensure you capture ALL distinct offences — assault, threats, confinement, conspiracy, etc. must each have their own section.\n"
        "4. SUBSECTION PRECISION: If a Candidate Section shows [USE SUBSECTION: X], you MUST use that exact subsection number in section_number (e.g., 'Section 308(4)' NOT 'Section 308').\n"
        "5. NO REDUNDANCY: Do NOT include a generic section if a more specific one covers it (e.g., if Section 140 covers kidnapping for ransom, do NOT also add Section 137 for basic kidnapping).\n"
        "6. COMPANION SECTIONS: For group crimes with multiple accused, ALWAYS include conspiracy and common intention. For victims held captive, ALWAYS include wrongful confinement.\n\n"
        "{companion_text}\n\n"
        "Return ONLY a strict JSON array of objects without markdown.\n"
        "Each object MUST have these exact keys:\n"
        "- section_number (e.g., 'Section 85', 'Section 308(4)') — USE EXACT SUBSECTION where indicated\n"
        "- chapter_name (copy exactly from candidate)\n"
        "- short_title (a 3-6 word summary)\n"
        "- punishment (copy exactly from candidate)\n"
        "- ipc_equivalent (copy exactly from candidate)\n"
        "- cognizable (copy exactly from candidate)\n"
        "- bailable (copy exactly from candidate)\n"
        "- full_text (a 2-3 sentence description of how this section applies)\n"
        "- confidence ('Very High (95-100%)' or 'High (85-95%)')\n"
        "- reason (A crisp 2-3 sentence legal justification)\n\n"
        "Incident Narrative:\n{narrative}\n\n"
        "Candidate Sections:\n{raw_sections}"
    )
    result = call_llm_with_prompt(prompt, {
        "narrative": narrative,
        "raw_sections": "\n".join(raw_sections),
        "companion_text": companion_text
    }, is_json=True, temperature=0)
    if result is None:
        print("[*] Magistrate Agent primary call failed. Using DB fallback.")
        formatted_sections = []
        count = 0
        for sec_id, meta in all_metas.items():
            if count >= 5: break
            formatted_sections.append({
                "section_number": f"Section {sec_id}",
                "chapter_name": meta.get('chapter', 'Unknown Chapter'),
                "short_title": meta.get('title', '')[:40] + "...",
                "punishment": meta.get('punishment', 'Unknown'),
                "ipc_equivalent": meta.get('ipc_eq', 'Unknown'),
                "cognizable": meta.get('cognizable', 'Unknown'),
                "bailable": meta.get('bailable', 'Unknown'),
                "full_text": all_docs[sec_id][:300] + "..."
            })
            count += 1
    else:
        formatted_sections = result
    print("[*] Universal Validator: Checking generated sections against Database Authority...")
    validated_sections = []
    if isinstance(formatted_sections, list):
        for item in formatted_sections:
            if not isinstance(item, dict):
                continue
            raw_sec = str(item.get("section_number", ""))
            sec_clean = raw_sec.replace("Section", "").replace(" ", "").strip()
            if "&" in sec_clean or "and" in sec_clean:
                sec_clean = sec_clean.split("&")[0].split("and")[0].strip()
            ipc_to_bns_map = {
                "120B": "61", "39": "61", "420": "318", "498A": "85",
                "304A": "106", "279": "281", "408": "316", "409": "316",
                "477A": "344", "384": "308", "506": "351", "307": "109",
                "34": "3", "302": "103", "376": "63", "354": "74",
                "304B": "80", "342": "127", "343": "128", "365": "140",
                "379": "303", "392": "309", "395": "310", "397": "311",
                "406": "314", "468": "340", "471": "340"
            }
            if sec_clean.upper() in ipc_to_bns_map:
                sec_clean = ipc_to_bns_map[sec_clean.upper()]
            base_sec = sec_clean.split("(")[0].strip()
            if base_sec in all_metas:
                db_meta = all_metas[base_sec]
                item["section_number"] = f"Section {sec_clean}"
                item["chapter_name"] = db_meta.get('chapter', item.get("chapter_name"))
                item["punishment"] = db_meta.get('punishment', item.get("punishment"))
                item["ipc_equivalent"] = db_meta.get('ipc_eq', item.get("ipc_equivalent"))
                item["cognizable"] = db_meta.get('cognizable', item.get("cognizable"))
                item["bailable"] = db_meta.get('bailable', item.get("bailable"))
                validated_sections.append(item)
            else:
                print(f"[*] Validator rejected hallucinated section: {raw_sec} (base: {base_sec})")
    existing_bases = set()
    for sec in validated_sections:
        raw = str(sec.get("section_number", "")).replace("Section", "").replace(" ", "").strip()
        existing_bases.add(raw.split("(")[0])
    for sec_id in mandatory_section_ids:
        if sec_id not in existing_bases and sec_id in injected_sections:
            entry = injected_sections[sec_id]
            print(f"[*] Enforcing mandatory section: Section {entry['display_section']} ({entry['title']})")
            validated_sections.append({
                "section_number": f"Section {entry['display_section']}",
                "chapter_name": entry["meta"].get("chapter", "Unknown"),
                "short_title": entry["title"][:40],
                "punishment": entry["meta"].get("punishment", "Unknown"),
                "ipc_equivalent": entry["meta"].get("ipc_eq", "Unknown"),
                "cognizable": entry["meta"].get("cognizable", "Unknown"),
                "bailable": entry["meta"].get("bailable", "Unknown"),
                "full_text": entry["doc"][:300],
                "confidence": "Very High (95-100%)",
                "reason": entry["reason"],
            })
            existing_bases.add(sec_id)
    if len(validated_sections) < 3:
        print("[*] Validator supplementing insufficient results with top DB matches...")
        for sec_id, meta in all_metas.items():
            if len(validated_sections) >= 5: break
            if sec_id not in existing_bases:
                validated_sections.append({
                    "section_number": f"Section {sec_id}",
                    "chapter_name": meta.get('chapter', 'Unknown Chapter'),
                    "short_title": meta.get('title', '')[:40] + "...",
                    "punishment": meta.get('punishment', 'Unknown'),
                    "ipc_equivalent": meta.get('ipc_eq', 'Unknown'),
                    "cognizable": meta.get('cognizable', 'Unknown'),
                    "bailable": meta.get('bailable', 'Unknown'),
                    "full_text": all_docs[sec_id][:300] + "...",
                    "confidence": "High (85-95%)",
                    "reason": "Direct semantic match from BNS Legal Database."
                })
                existing_bases.add(sec_id)
    for sa in special_acts:
        validated_sections.append(sa)
        print(f"[*] Appended Special Act: {sa.get('section_number')}")
    print(f"[*] Final output: {len(validated_sections)} sections total")
    return {"retrieved_sections": validated_sections}
def draft_fir(state: LegalState):
    print("[*] Clerk Agent: Drafting official FIR...")
    import random
    from datetime import datetime
    now = datetime.now()
    current_year = now.strftime("%Y")
    current_month = now.strftime("%m")
    current_date = now.strftime("%d/%m/%Y")
    current_time = now.strftime("%H:%M")
    fir_no = f"{current_year}/{current_month}/{random.randint(1000, 9999)}"
    prompt = ChatPromptTemplate.from_template(
        "You are an expert Indian Police Clerk. Draft a formal First Information Report (FIR) based on the given narrative and facts.\n"
        "Return a strict JSON object with NO markdown wrapping, NO code blocks, and NO other text.\n"
        "Ensure keys match exactly:\n"
        "- complainant_name\n"
        "- father_husband_name\n"
        "- dob_year\n"
        "- occupation\n"
        "- address\n"
        "- phone\n"
        "- accused_details (list of dicts with keys 'name', 'relative_name', 'address')\n"
        "- property_details (list of dicts with keys 'category', 'type', 'particulars', 'value')\n"
        "- total_property_value\n"
        "- fir_narrative (highly professional, legal narrative based on facts, without formatting)\n"
        "- occurrence_date\n"
        "- occurrence_time\n"
        "- occurrence_day\n\n"
        "Facts: {facts}\n"
        "Narrative: {narrative}\n"
        "Do not hallucinate extra facts. If missing, put 'Unknown' or 'Nil'.\n"
    )
    variables_dict = {
        "facts": json.dumps(state.get("extracted_facts", {})),
        "narrative": state.get("narrative", "")
    }
    result = call_llm_with_prompt(prompt, variables_dict, is_json=True, temperature=0.2)
    if result is None:
        print(f"Clerk AI Error (Likely Rate Limit). Generating fallback FIR.")
        result = {
            "complainant_name": "Victim", "father_husband_name": "Unknown", "dob_year": "Unknown", "occupation": "Unknown",
            "address": "Unknown", "phone": "Unknown", "accused_details": [], "property_details": [], "total_property_value": "Nil",
            "fir_narrative": "System rate limited. Fallback FIR.", "occurrence_date": current_date, "occurrence_time": current_time, "occurrence_day": "Unknown"
        }
    sections_html = ""
    for idx, sec in enumerate(state.get("retrieved_sections", [])):
        sec_num = sec.get("section_number", "")
        sections_html += f"<tr><td style='border: 1px solid black; padding: 8px 12px;'>{idx+1}</td><td style='border: 1px solid black; padding: 8px 12px;'>BNS 2023</td><td style='border: 1px solid black; padding: 8px 12px;'>{sec_num}</td></tr>"
    if not sections_html:
        sections_html = "<tr><td colspan='3' style='border: 1px solid black; padding: 8px 12px;'>-</td></tr>"
    accused_html = ""
    for idx, acc in enumerate(result.get("accused_details", [])):
        accused_html += f"<tr><td style='border: 1px solid black; padding: 8px 12px;'>{idx+1}</td><td style='border: 1px solid black; padding: 8px 12px;'>{acc.get('name', '')}</td><td style='border: 1px solid black; padding: 8px 12px;'></td><td style='border: 1px solid black; padding: 8px 12px;'>{acc.get('relative_name', '')}</td><td style='border: 1px solid black; padding: 8px 12px;'>{acc.get('address', '')}</td></tr>"
    if not accused_html:
        accused_html = "<tr><td colspan='5' style='border: 1px solid black; padding: 8px 12px;'>Nil</td></tr>"
    prop_html = ""
    for idx, prop in enumerate(result.get("property_details", [])):
        prop_html += f"<tr><td style='border: 1px solid black; padding: 8px 12px;'>{idx+1}</td><td style='border: 1px solid black; padding: 8px 12px;'>{prop.get('category', '')}</td><td style='border: 1px solid black; padding: 8px 12px;'>{prop.get('type', '')}</td><td style='border: 1px solid black; padding: 8px 12px;'>{prop.get('particulars', '')}</td><td style='border: 1px solid black; padding: 8px 12px;'>{prop.get('value', '')}</td></tr>"
    if not prop_html:
        prop_html = "<tr><td colspan='5' style='border: 1px solid black; padding: 8px 12px;'>Nil</td></tr>"
    selected_state = state.get("state", "")
    if selected_state == "Maharashtra":
        lang = {
            "form_id": "I.I.F.-I (एकीकृत अन्वेषण फॉर्म - १)",
            "title": "FIRST INFORMATION REPORT / प्रथम खबर अहवाल",
            "subtitle": "(Under Section 173 of BNSS, 2023) / (कलम १७३ भारतीय नागरिक सुरक्षा संहिता, २०२३)",
            "district": "District (जिल्हा)", "ps": "P.S. (पोलीस ठाणे)", "year": "Year (वर्ष)",
            "fir_no": "FIR No. (प्रथम खबर क्र.)", "fir_datetime": "Date and Time of FIR (प्र. ख. दिनांक आणि वेळ)",
            "acts_sections": "Acts &amp; Sections (अधिनियम व कलम)",
            "sno": "S.No. (अ.क्र.)", "acts": "Acts (अधिनियम)", "sections": "Sections (कलम)",
            "occurrence": "Occurrence of Offence (गुन्ह्याची घटना)", "date": "Date (दिनांक)", "time": "Time (वेळ)",
            "info_received": "Information received at P.S. (पो. ठाण्यावर माहिती मिळाल्याचे)",
            "info_type": "Type of Information (माहितीचा प्रकार)", "written": "Written (लेखी)",
            "complainant": "Complainant/Informant (तक्रारदार / माहिती देणारा)",
            "name": "Name (नाव)", "father": "Father's/Husband's Name (पिता/पती यांचे नाव)",
            "dob": "Date/Year of Birth (जन्म तारीख / वर्ष)", "nationality": "Nationality (राष्ट्रीयत्व)",
            "occupation": "Occupation (व्यवसाय)",
            "addr_type": "Address Type (पत्ता प्रकार)", "address": "Address (पत्ता)",
            "accused": "Details of known/suspected/unknown accused (ज्ञात / संशयित / अज्ञात आरोपीचे संपूर्ण तपशील)",
            "acc_name": "Name (नाव)", "acc_rel": "Relative's Name (नातेवाईकाचे नाव)", "acc_addr": "Present Address (वर्तमान पत्ता)",
            "property": "Property details (मालमत्ता तपशील)",
            "prop_cat": "Property Category (मालमत्ता वर्ग)", "prop_type": "Property Type (मालमत्ता प्रकार)",
            "prop_part": "Particulars (संबंधीत मालमत्तेचा तपशील)", "prop_val": "Value in Rs (रू. मध्ये)",
            "total_prop": "Total value of property (मालमत्तेचे एकूण मूल्य)",
            "inquest": "Inquest Report / U.D. case No. (मरणान्वेषण अहवाल/अकस्मात मृत्यू प्रकरण क्र.)",
            "fir_contents": "First Information contents (प्रथम खबर मजकूर)",
        }
    elif selected_state == "Gujarat":
        lang = {
            "form_id": "I.I.F.-I (એકીકૃત અન્વેષણ ફોર્મ - ૧)",
            "title": "FIRST INFORMATION REPORT / પ્રથમ માહિતી અહેવાલ",
            "subtitle": "(Under Section 173 of BNSS, 2023) / (કલમ ૧૭૩ ભારતીય નાગરિક સુરક્ષા સંહિતા, ૨૦૨૩)",
            "district": "District (જિલ્લો)", "ps": "P.S. (પોલીસ સ્ટેશન)", "year": "Year (વર્ષ)",
            "fir_no": "FIR No. (પ્ર. મા. અ. નં.)", "fir_datetime": "Date and Time of FIR (પ્ર.મા.અ. તારીખ અને સમય)",
            "acts_sections": "Acts &amp; Sections (અધિનિયમ અને કલમ)",
            "sno": "S.No. (ક્રમ)", "acts": "Acts (અધિનિયમ)", "sections": "Sections (કલમ)",
            "occurrence": "Occurrence of Offence (ગુનાની ઘટના)", "date": "Date (તારીખ)", "time": "Time (સમય)",
            "info_received": "Information received at P.S. (પો.સ્ટે. માં મળેલી માહિતી)",
            "info_type": "Type of Information (માહિતીનો પ્રકાર)", "written": "Written (લેખિત)",
            "complainant": "Complainant/Informant (ફરિયાદી/માહિતી આપનાર)",
            "name": "Name (નામ)", "father": "Father's/Husband's Name (પિતા/પતિનું નામ)",
            "dob": "Date/Year of Birth (જન્મ તારીખ/વર્ષ)", "nationality": "Nationality (રાષ્ટ્રીયતા)",
            "occupation": "Occupation (વ્યવસાય)",
            "addr_type": "Address Type (સરનામાનો પ્રકાર)", "address": "Address (સરનામું)",
            "accused": "Details of accused (જાણીતા/શંકાસ્પદ/અજાણ્યા આરોપીની વિગતો)",
            "acc_name": "Name (નામ)", "acc_rel": "Relative's Name (સંબંધીનું નામ)", "acc_addr": "Present Address (હાલનું સરનામું)",
            "property": "Property details (મિલકતની વિગતો)",
            "prop_cat": "Property Category (મિલકત વર્ગ)", "prop_type": "Property Type (મિલકતનો પ્રકાર)",
            "prop_part": "Particulars (વિગતો)", "prop_val": "Value in Rs (રૂ. માં મૂલ્ય)",
            "total_prop": "Total value of property (મિલકતનું કુલ મૂલ્ય)",
            "inquest": "Inquest Report / U.D. case No. (ઇન્ક્વેસ્ટ રિપોર્ટ/યુ.ડી. કેસ નં.)",
            "fir_contents": "First Information contents (પ્રથમ માહિતી વિગતો)",
        }
    elif selected_state == "Tamil Nadu":
        lang = {
            "form_id": "I.I.F.-I (ஒருங்கிணைந்த விசாரணை படிவம் - 1)",
            "title": "FIRST INFORMATION REPORT / முதல் தகவல் அறிக்கை",
            "subtitle": "(Under Section 173 of BNSS, 2023) / (பிரிவு 173 BNSS, 2023)",
            "district": "District (மாவட்டம்)", "ps": "P.S. (காவல் நிலையம்)", "year": "Year (ஆண்டு)",
            "fir_no": "FIR No. (மு.த.அ. எண்)", "fir_datetime": "Date and Time of FIR (மு.த.அ. தேதி மற்றும் நேரம்)",
            "acts_sections": "Acts &amp; Sections (சட்டங்கள் &amp; பிரிவுகள்)",
            "sno": "S.No. (வ.எண்)", "acts": "Acts (சட்டங்கள்)", "sections": "Sections (பிரிவுகள்)",
            "occurrence": "Occurrence of Offence (குற்றம் நிகழ்ந்தவை)", "date": "Date (தேதி)", "time": "Time (நேரம்)",
            "info_received": "Information received at P.S. (கா.நி. இல் பெறப்பட்ட தகவல்)",
            "info_type": "Type of Information (தகவல் வகை)", "written": "Written (எழுதப்பட்ட)",
            "complainant": "Complainant/Informant (புகார்தாரர்/தகவல் கொடுப்பவர்)",
            "name": "Name (பெயர்)", "father": "Father's/Husband's Name (தந்தை/கணவர் பெயர்)",
            "dob": "Date/Year of Birth (பிறந்த தேதி/ஆண்டு)", "nationality": "Nationality (தேசியம்)",
            "occupation": "Occupation (தொழில்)",
            "addr_type": "Address Type (முகவரி வகை)", "address": "Address (முகவரி)",
            "accused": "Details of accused (குற்றம் சாட்டப்பட்டவரின் விவரங்கள்)",
            "acc_name": "Name (பெயர்)", "acc_rel": "Relative's Name (உறவினர் பெயர்)", "acc_addr": "Present Address (தற்போதைய முகவரி)",
            "property": "Property details (சொத்து விவரங்கள்)",
            "prop_cat": "Property Category (சொத்து வகை)", "prop_type": "Property Type (சொத்து வகை)",
            "prop_part": "Particulars (விவரங்கள்)", "prop_val": "Value in Rs (ரூபாயில் மதிப்பு)",
            "total_prop": "Total value of property (சொத்தின் மொத்த மதிப்பு)",
            "inquest": "Inquest Report / U.D. case No. (விசாரணை அறிக்கை/யு.டி வழக்கு எண்)",
            "fir_contents": "First Information contents (முதல் தகவல் விவரங்கள்)",
        }
    elif selected_state == "Punjab":
        lang = {
            "form_id": "I.I.F.-I (ਏਕੀਕ੍ਰਿਤ ਜਾਂਚ ਫਾਰਮ - 1)",
            "title": "FIRST INFORMATION REPORT / ਪਹਿਲੀ ਸੂਚਨਾ ਰਿਪੋਰਟ",
            "subtitle": "(Under Section 173 of BNSS, 2023) / (ਧਾਰਾ 173 BNSS, 2023)",
            "district": "District (ਜ਼ਿਲ੍ਹਾ)", "ps": "P.S. (ਪੁਲਿਸ ਸਟੇਸ਼ਨ)", "year": "Year (ਸਾਲ)",
            "fir_no": "FIR No. (ਐਫ.ਆਈ.ਆਰ. ਨੰ.)", "fir_datetime": "Date and Time of FIR (ਐਫ.ਆਈ.ਆਰ. ਦੀ ਮਿਤੀ ਅਤੇ ਸਮਾਂ)",
            "acts_sections": "Acts &amp; Sections (ਐਕਟ ਅਤੇ ਧਾਰਾਵਾਂ)",
            "sno": "S.No. (ਲੜੀ ਨੰ.)", "acts": "Acts (ਐਕਟ)", "sections": "Sections (ਧਾਰਾਵਾਂ)",
            "occurrence": "Occurrence of Offence (ਅਪਰਾਧ ਦੀ ਘਟਨਾ)", "date": "Date (ਮਿਤੀ)", "time": "Time (ਸਮਾਂ)",
            "info_received": "Information received at P.S. (ਪੁਲਿਸ ਸਟੇਸ਼ਨ 'ਤੇ ਪ੍ਰਾਪਤ ਜਾਣਕਾਰੀ)",
            "info_type": "Type of Information (ਜਾਣਕਾਰੀ ਦੀ ਕਿਸਮ)", "written": "Written (ਲਿਖਤੀ)",
            "complainant": "Complainant/Informant (ਸ਼ਿਕਾਇਤਕਰਤਾ/ਸੂਚਨਾਕਾਰ)",
            "name": "Name (ਨਾਮ)", "father": "Father's/Husband's Name (ਪਿਤਾ/ਪਤੀ ਦਾ ਨਾਮ)",
            "dob": "Date/Year of Birth (ਜਨਮ ਮਿਤੀ/ਸਾਲ)", "nationality": "Nationality (ਰਾਸ਼ਟਰੀਅਤਾ)",
            "occupation": "Occupation (ਕਿੱਤਾ)",
            "addr_type": "Address Type (ਪਤੇ ਦੀ ਕਿਸਮ)", "address": "Address (ਪਤਾ)",
            "accused": "Details of accused (ਦੋਸ਼ੀ ਦੇ ਵੇਰਵੇ)",
            "acc_name": "Name (ਨਾਮ)", "acc_rel": "Relative's Name (ਰਿਸ਼ਤੇਦਾਰ ਦਾ ਨਾਮ)", "acc_addr": "Present Address (ਮੌਜੂਦਾ ਪਤਾ)",
            "property": "Property details (ਜਾਇਦਾਦ ਦੇ ਵੇਰਵੇ)",
            "prop_cat": "Property Category (ਜਾਇਦਾਦ ਦੀ ਸ਼੍ਰੇਣੀ)", "prop_type": "Property Type (ਜਾਇਦਾਦ ਦੀ ਕਿਸਮ)",
            "prop_part": "Particulars (ਵੇਰਵੇ)", "prop_val": "Value in Rs (ਰੁਪਏ ਵਿੱਚ ਮੁੱਲ)",
            "total_prop": "Total value of property (ਜਾਇਦਾਦ ਦਾ ਕੁੱਲ ਮੁੱਲ)",
            "inquest": "Inquest Report / U.D. case No. (ਇਨਕੁਐਸਟ ਰਿਪੋਰਟ/ਯੂ.ਡੀ. ਕੇਸ ਨੰ.)",
            "fir_contents": "First Information contents (ਪਹਿਲੀ ਸੂਚਨਾ ਸਮੱਗਰੀ)",
        }
    elif selected_state == "Kerala":
        lang = {
            "form_id": "I.I.F.-I (ഏകീകൃത അന്വേഷണ ഫോം - 1)",
            "title": "FIRST INFORMATION REPORT / പ്രഥമ വിവര റിപ്പോർട്ട്",
            "subtitle": "(Under Section 173 of BNSS, 2023) / (വകുപ്പ് 173 BNSS, 2023)",
            "district": "District (ജില്ല)", "ps": "P.S. (പോലീസ് സ്റ്റേഷൻ)", "year": "Year (വർഷം)",
            "fir_no": "FIR No. (എഫ്.ഐ.ആർ നമ്പർ)", "fir_datetime": "Date and Time of FIR (എഫ്.ഐ.ആർ തീയതിയും സമയവും)",
            "acts_sections": "Acts &amp; Sections (നിയമങ്ങളും വകുപ്പുകളും)",
            "sno": "S.No. (ക്രമ നമ്പർ)", "acts": "Acts (നിയമങ്ങൾ)", "sections": "Sections (വകുപ്പുകൾ)",
            "occurrence": "Occurrence of Offence (കുറ്റം നടന്നത്)", "date": "Date (തീയതി)", "time": "Time (സമയം)",
            "info_received": "Information received at P.S. (പോലീസ് സ്റ്റേഷനിൽ വിവരം ലഭിച്ചത്)",
            "info_type": "Type of Information (വിവരത്തിന്റെ തരം)", "written": "Written (രേഖാമൂലം)",
            "complainant": "Complainant/Informant (പരാതിക്കാരൻ/വിവരം നൽകിയ ആൾ)",
            "name": "Name (പേര്)", "father": "Father's/Husband's Name (പിതാവിന്റെ/ഭർത്താവിന്റെ പേര്)",
            "dob": "Date/Year of Birth (ജനനത്തീയതി/വർഷം)", "nationality": "Nationality (ദേശീയത)",
            "occupation": "Occupation (തൊഴിൽ)",
            "addr_type": "Address Type (വിലാസത്തിന്റെ തരം)", "address": "Address (വിലാസം)",
            "accused": "Details of accused (പ്രതിയുടെ വിവരങ്ങൾ)",
            "acc_name": "Name (പേര്)", "acc_rel": "Relative's Name (ബന്ധുവിന്റെ പേര്)", "acc_addr": "Present Address (നിലവിലെ വിലാസം)",
            "property": "Property details (വസ്തു വിവരങ്ങൾ)",
            "prop_cat": "Property Category (വസ്തുവിന്റെ വിഭാഗം)", "prop_type": "Property Type (വസ്തുവിന്റെ തരം)",
            "prop_part": "Particulars (വിശദാംശങ്ങൾ)", "prop_val": "Value in Rs (രൂപയിൽ മൂല്യം)",
            "total_prop": "Total value of property (വസ്തുവിന്റെ മൊത്തം മൂല്യം)",
            "inquest": "Inquest Report / U.D. case No. (ഇൻക്വസ്റ്റ് റിപ്പോർട്ട്/യു.ഡി കേസ് നമ്പർ)",
            "fir_contents": "First Information contents (പ്രഥമ വിവര ഉള്ളടക്കം)",
        }
    else:
        lang = {
            "form_id": "I.I.F.-I (एकीकृत अन्वेषण फॉर्म - 1)",
            "title": "FIRST INFORMATION REPORT / प्रथम सूचना रिपोर्ट",
            "subtitle": "(Under Section 173 of BNSS, 2023) / (धारा १७३ भारतीय नागरिक सुरक्षा संहिता, २०२३)",
            "district": "District (जिला)", "ps": "P.S. (थाना)", "year": "Year (वर्ष)",
            "fir_no": "FIR No. (प्र.सू.रि. क्र.)", "fir_datetime": "Date and Time of FIR (प्र.सू.रि. दिनांक एवं समय)",
            "acts_sections": "Acts &amp; Sections (अधिनियम एवं धारा)",
            "sno": "S.No. (क्र.सं.)", "acts": "Acts (अधिनियम)", "sections": "Sections (धारा)",
            "occurrence": "Occurrence of Offence (अपराध की घटना)", "date": "Date (दिनांक)", "time": "Time (समय)",
            "info_received": "Information received at P.S. (थाने पर सूचना प्राप्त)",
            "info_type": "Type of Information (सूचना का प्रकार)", "written": "Written (लिखित)",
            "complainant": "Complainant/Informant (शिकायतकर्ता / सूचनादाता)",
            "name": "Name (नाम)", "father": "Father's/Husband's Name (पिता/पति का नाम)",
            "dob": "Date/Year of Birth (जन्म तिथि / वर्ष)", "nationality": "Nationality (राष्ट्रीयता)",
            "occupation": "Occupation (व्यवसाय)",
            "addr_type": "Address Type (पता प्रकार)", "address": "Address (पता)",
            "accused": "Details of known/suspected/unknown accused (ज्ञात / संदिग्ध / अज्ञात अभियुक्त का पूर्ण विवरण)",
            "acc_name": "Name (नाम)", "acc_rel": "Relative's Name (रिश्तेदार का नाम)", "acc_addr": "Present Address (वर्तमान पता)",
            "property": "Property details (संपत्ति विवरण)",
            "prop_cat": "Property Category (संपत्ति श्रेणी)", "prop_type": "Property Type (संपत्ति प्रकार)",
            "prop_part": "Particulars (संबंधित संपत्ति का विवरण)", "prop_val": "Value in Rs (रू. में)",
            "total_prop": "Total value of property (संपत्ति का कुल मूल्य)",
            "inquest": "Inquest Report / U.D. case No. (मृत्यु जांच रिपोर्ट / यू.डी. प्रकरण क्र.)",
            "fir_contents": "First Information contents (प्रथम सूचना विवरण)",
        }
    title_parts = lang["title"].split("/")
    title_main = title_parts[0].strip()
    title_sub = title_parts[1].strip() if len(title_parts) > 1 else ""
    subtitle_parts = lang["subtitle"].split("/")
    subtitle_main = subtitle_parts[0].strip()
    subtitle_sub = subtitle_parts[1].strip() if len(subtitle_parts) > 1 else ""
    html_template = f
    return {"final_fir": html_template}
def build_agent_graph():
    workflow = StateGraph(LegalState)
    workflow.add_node("investigator", extract_facts)
    workflow.add_node("magistrate", retrieve_laws)
    workflow.add_node("clerk", draft_fir)
    workflow.set_entry_point("investigator")
    workflow.add_edge("investigator", "magistrate")
    workflow.add_edge("magistrate", "clerk")
    workflow.add_edge("clerk", END)
    return workflow.compile()
app = build_agent_graph()
