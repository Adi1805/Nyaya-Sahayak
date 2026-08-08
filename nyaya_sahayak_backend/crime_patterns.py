import re
from typing import List, Dict, Any
def get_bns_meta(sec_id: str, enrichment_data: Dict[str, Any]) -> Dict[str, Any]:
    if sec_id in enrichment_data:
        meta = enrichment_data[sec_id]
    else:
        base_sec = sec_id.split('(')[0]
        if base_sec in enrichment_data:
            meta = enrichment_data[base_sec]
        else:
            return None
    return {
        "section_number": f"Section {sec_id}",
        "chapter_name": meta.get('chapter', 'Unknown Chapter'),
        "short_title": meta.get('title', f"Offence under Section {sec_id}")[:40] + ("..." if len(meta.get('title', '')) > 40 else ""),
        "punishment": meta.get('punishment', 'Unknown'),
        "ipc_equivalent": meta.get('ipc_eq', 'Unknown'),
        "cognizable": meta.get('cognizable', 'Unknown'),
        "bailable": meta.get('bailable', 'Unknown'),
        "full_text": meta.get('keywords', '')
    }
def detect_crime_patterns(facts: dict, narrative: str, enrichment_data: dict) -> List[Dict[str, Any]]:
    must_include = []
    reasons = {}
    def add_section(sec_id: str, reason: str, confidence: str = "Very High (95-100%)"):
        if sec_id not in reasons:
            meta = get_bns_meta(sec_id, enrichment_data)
            if meta:
                meta['confidence'] = confidence
                meta['reason'] = reason
                must_include.append(meta)
                reasons[sec_id] = reason
    text = f"{narrative} {facts.get('case_title', '')} {facts.get('legal_concepts', '')} {facts.get('weapons', '')} {facts.get('injuries', '')} {facts.get('motive', '')}".lower()
    if any(k in text for k in ['gang', 'group', 'multiple', 'accomplice', 'together', 'mob', 'syndicate', 'network', 'ring']):
        add_section("3", "Universal Principle: Common intention applies due to multiple perpetrators acting together.")
        add_section("61", "Universal Principle: Criminal conspiracy applies due to orchestrated group involvement and planning.")
    if any(k in text for k in ['confined', 'tied', 'locked', 'warehouse', 'captive', 'detained', 'held hostage']):
        add_section("127", "Universal Principle: Victim was physically confined or locked in against their will.")
    elif any(k in text for k in ['blocked', 'restrained', 'stopped from moving', 'prevented from leaving']):
        add_section("126", "Universal Principle: Victim was wrongfully restrained from proceeding.")
    if any(k in text for k in ['threat to kill', 'kill you', 'death threat', 'murder threat', 'laash milegi']):
        add_section("351", "Universal Principle: Direct threat to cause death or grievous hurt was made.")
    elif any(k in text for k in ['threat', 'warned', 'intimidated', 'scared', 'consequences']):
        add_section("351", "Universal Principle: Criminal intimidation was used against the victim.")
    if any(k in text for k in ['destroyed evidence', 'tampered', 'deleted cctv', 'burned clothes', 'washed blood']):
        add_section("238", "Universal Principle: Attempted to cause disappearance of evidence of the offence.")
    if any(k in text for k in ['ransom', 'extortion of money', 'kidnap for money']):
        add_section("140", "Pattern: Kidnapping for ransom, demanding money for safe release.")
        add_section("308", "Pattern: Extortion by putting person in fear of death or hurt.")
    elif any(k in text for k in ['kidnap', 'abduct', 'forcibly taken']):
        add_section("137", "Pattern: Kidnapping or abducting from lawful guardianship or by force.")
    if any(k in text for k in ['rape', 'sexual assault', 'forced sex']):
        if any(w in text for w in ['gang rape', 'multiple men', 'gangraped']):
            add_section("70", "Pattern: Gang rape by multiple individuals.")
        else:
            add_section("63", "Pattern: Rape or sexual assault.")
        if any(w in text for w in ['minor', 'child', 'under 18', 'under 12', 'years old']):
            add_section("65", "Pattern: Rape of a minor under 18 years of age.")
    if any(k in text for k in ['dowry', 'stridhan', 'in-laws', 'husband beaten']):
        add_section("85", "Pattern: Cruelty by husband or relatives for dowry/property.")
        if any(w in text for w in ['suicide', 'died', 'burnt', 'poison']):
            add_section("80", "Pattern: Dowry death due to cruelty.")
    if any(k in text for k in ['acid', 'corrosive', 'thrown acid']):
        add_section("124", "Pattern: Voluntarily throwing acid or corrosive substance.")
    if any(k in text for k in ['harassment', 'unwanted advances', 'sexual remarks', 'eve teasing']):
        add_section("75", "Pattern: Sexual harassment.")
    if any(k in text for k in ['stalking', 'following', 'monitoring']):
        add_section("76", "Pattern: Stalking or repeatedly following a woman.")
    if any(k in text for k in ['murder', 'killed intentionally', 'stabbed to death']):
        if 'mob' in text or 'lynch' in text:
            add_section("103", "Pattern: Murder by a group or mob (Lynching).")
        else:
            add_section("103", "Pattern: Intentional murder.")
    if any(k in text for k in ['hit and run', 'rash driving', 'fatal accident', 'accident death']):
        add_section("106", "Pattern: Causing death by negligence (Hit and Run).")
        add_section("281", "Pattern: Rash or negligent driving on a public way.")
    if any(k in text for k in ['attempt to murder', 'tried to kill', 'fired at']):
        add_section("109", "Pattern: Attempted murder with intent to cause death.")
    if any(k in text for k in ['grievous hurt', 'fracture', 'broken bone', 'permanent damage', 'disfigured']):
        if any(w in text for w in ['weapon', 'gun', 'knife', 'rod', 'bat', 'sword']):
            add_section("122", "Pattern: Voluntarily causing grievous hurt by dangerous weapons.")
        else:
            add_section("117", "Pattern: Voluntarily causing grievous hurt.")
    elif any(k in text for k in ['hurt', 'beaten', 'slapped', 'punched', 'bruise', 'bloodied']):
        if any(w in text for w in ['weapon', 'gun', 'knife', 'rod', 'bat', 'sword']):
            add_section("118", "Pattern: Voluntarily causing hurt by dangerous weapons.")
        else:
            add_section("115", "Pattern: Voluntarily causing simple hurt.")
    if any(k in text for k in ['dacoity', 'armed gang robbery']):
        add_section("310", "Pattern: Dacoity committed by 5 or more persons.")
    elif any(k in text for k in ['robbery', 'robbed', 'looted', 'gunpoint robbery']):
        add_section("309", "Pattern: Robbery involving theft and fear of instant hurt.")
        if any(w in text for w in ['weapon', 'gun', 'knife', 'armed']):
            add_section("311", "Pattern: Robbery with attempt to cause death or grievous hurt.")
    if any(k in text for k in ['snatching', 'chain snatching', 'phone snatched', 'bag snatched']):
        add_section("304", "Pattern: Snatching property from a person.")
    elif any(k in text for k in ['theft', 'stolen', 'stole', 'shoplifting', 'pickpocket']):
        add_section("303", "Pattern: Theft of movable property.")
    if any(k in text for k in ['extortion', 'hafta', 'protection money']):
        add_section("308", "Pattern: Extortion by putting person in fear of injury.")
    if any(k in text for k in ['embezzlement', 'breach of trust', 'misappropriation', 'entrusted funds']):
        add_section("316", "Pattern: Criminal Breach of Trust.")
        if any(w in text for w in ['clerk', 'servant', 'employee', 'manager', 'accountant']):
            add_section("316", "Pattern: Criminal Breach of Trust by clerk or employee.")
    if any(k in text for k in ['cheating', 'fraud', 'scam', 'duped', 'tricked', 'fake company']):
        add_section("318", "Pattern: Cheating and dishonestly inducing delivery of property.")
        if any(w in text for w in ['impersonation', 'identity fraud', 'fake id', 'pretending']):
            add_section("319", "Pattern: Cheating by personation.")
    if any(k in text for k in ['mischief', 'vandalism', 'property damage', 'destroyed']):
        if any(w in text for w in ['fire', 'arson', 'burned']):
            add_section("326", "Pattern: Mischief by fire or explosive substance.")
        else:
            add_section("324", "Pattern: Mischief causing damage to property.")
    if any(k in text for k in ['trespass', 'broke in', 'illegal entry', 'encroachment']):
        if 'night' in text:
            add_section("333", "Pattern: House-breaking by night.")
        else:
            add_section("329", "Pattern: Criminal trespass into property.")
    if any(k in text for k in ['forgery', 'fake document', 'forged signature', 'fake certificate']):
        add_section("336", "Pattern: Forgery of a document.")
        if 'cheating' in text or 'fraud' in text:
            add_section("340", "Pattern: Forgery for the purpose of cheating.")
    if any(k in text for k in ['fake currency', 'counterfeit note', 'fake money']):
        add_section("178", "Pattern: Counterfeiting currency notes.")
    if any(k in text for k in ['falsified accounts', 'cooked books', 'fake ledger']):
        add_section("344", "Pattern: Falsification of accounts by clerk or officer.")
    if any(k in text for k in ['riot', 'mob violence', 'stone pelting', 'clash']):
        add_section("189", "Pattern: Rioting by unlawful assembly.")
        if 'weapon' in text or 'armed' in text:
            add_section("190", "Pattern: Rioting armed with a deadly weapon.")
    if any(k in text for k in ['bribe', 'corruption', 'illegal gratification']):
        add_section("199", "Pattern: Public servant taking gratification other than legal remuneration.")
    special_acts = []
    if any(k in text for k in ['gun', 'pistol', 'katta', 'firearm', 'bullet', 'shoot']):
        special_acts.append("Arms Act, 1959 (Sec 25/27) - Possession and use of firearms.")
    if any(k in text for k in ['whatsapp', 'upi', 'cyber', 'online', 'website', 'app', 'email']):
        special_acts.append("Information Technology Act, 2000 (Sec 66/66D) - Cyber crimes and online cheating.")
    if any(k in text for k in ['drugs', 'ganja', 'cocaine', 'heroin', 'meth', 'charas', 'narcotics', 'contraband']):
        special_acts.append("NDPS Act, 1985 - Possession and trafficking of narcotics.")
    if any(k in text for k in ['child', 'minor', 'under 18']) and any(k in text for k in ['rape', 'assault', 'molest']):
        special_acts.append("POCSO Act, 2012 - Sexual offences against minors.")
    if any(k in text for k in ['caste', 'dalit', 'slur', 'untouchability']):
        special_acts.append("SC/ST (Prevention of Atrocities) Act, 1989 - Atrocities against marginalized communities.")
    if any(k in text for k in ['domestic violence', 'wife beaten', 'protection order']):
        special_acts.append("Domestic Violence Act, 2005 - Protection of women from domestic violence.")
    if special_acts:
        must_include.append({
            "section_number": "Special Acts",
            "chapter_name": "Additional Statutory Acts",
            "short_title": "Applicable Special Laws",
            "punishment": "Various",
            "ipc_equivalent": "N/A",
            "cognizable": "Depends on Act",
            "bailable": "Depends on Act",
            "full_text": "APPLICABLE SPECIAL ACTS MUST BE INCLUDED:\n" + "\n".join(special_acts),
            "confidence": "Very High (95-100%)",
            "reason": "Specific keywords triggered mandatory inclusion of these special statutory acts."
        })
    return must_include
