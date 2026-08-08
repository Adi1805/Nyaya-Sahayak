import os
import sys
import io
import ssl
import urllib3
import json
import chromadb
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
import requests
old_request = requests.Session.request
def new_request(self, method, url, **kwargs):
    kwargs['verify'] = False
    return old_request(self, method, url, **kwargs)
requests.Session.request = new_request
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
def build_database():
    print("[*] Initializing Nyaya Sahayak Vector Database Builder...")
    db_path = os.path.join(os.path.dirname(__file__), "bns_chroma_db")
    client = chromadb.PersistentClient(path=db_path)
    collection_name = "bns_sections"
    try:
        client.delete_collection(name=collection_name)
    except:
        pass
    collection = client.create_collection(name=collection_name)
    print("[*] Loading embedding model (all-MiniLM-L6-v2)... This may take a minute on first run.")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("[*] Downloading full BNS dataset from Hugging Face...")
    try:
        dataset = load_dataset("GSMS-B/indian-legal-sections-bns-bnss-bsa-2023", data_files="bns_sections.json")
        sections_data = dataset['train']
        print(f"[+] Successfully downloaded {len(sections_data)} sections.")
    except Exception as e:
        print("[-] Could not download from HF directly. Using robust fallback dataset for demonstration...")
        sections_data = [
            {"section_number": "118(1)", "title": "Voluntarily causing hurt or grievous hurt by dangerous weapons or means", "description": "Whoever, except in the case provided for by sub-section (1) of section 122, voluntarily causes hurt by means of any instrument for shooting, stabbing or cutting, or any instrument which, used as a weapon of offence, is likely to cause death... shall be punished with imprisonment for a term which may extend to three years, or with fine, or with both.", "cognizable": "Yes", "bailable": "No"},
            {"section_number": "308(2)", "title": "Extortion", "description": "Whoever commits extortion shall be punished with imprisonment of either description for a term which may extend to seven years, or with fine, or with both.", "cognizable": "Yes", "bailable": "No"},
            {"section_number": "303(2)", "title": "Theft", "description": "Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.", "cognizable": "Yes", "bailable": "Non-Bailable"},
            {"section_number": "324", "title": "Mischief", "description": "Whoever commits mischief shall be punished with imprisonment of either description for a term which may extend to three months, or with fine, or with both.", "cognizable": "No", "bailable": "Bailable"},
            {"section_number": "3(5)", "title": "Common Intention", "description": "When a criminal act is done by several persons in furtherance of the common intention of all, each of such persons is liable for that act in the same manner as if it were done by him alone.", "cognizable": "Depends on main offense", "bailable": "Depends on main offense"},
            {"section_number": "103(1)", "title": "Punishment for Murder", "description": "Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.", "cognizable": "Yes", "bailable": "No"},
            {"section_number": "111", "title": "Organised Crime", "description": "Any continuing unlawful activity including kidnapping, robbery, vehicle theft, extortion, land grabbing, contract killing, economic offences, cyber-crimes... caused by an organised crime syndicate.", "cognizable": "Yes", "bailable": "No"}
        ]
    print("[*] Processing and embedding sections into ChromaDB. Please wait...")
    docs = []
    metadatas = []
    ids = []
    for i, item in enumerate(sections_data):
        sec_num = item.get("section_number", item.get("Section", str(i)))
        title = item.get("section_title", item.get("title", "Unknown Title"))
        desc = item.get("text", item.get("description", ""))
        text_to_embed = f"Section {sec_num}: {title}. {desc}"
        docs.append(text_to_embed)
        metadatas.append({
            "section": str(sec_num),
            "title": str(title)
        })
        ids.append(f"sec_{sec_num}_{i}")
    print("[*] Generating vector embeddings... (This is CPU intensive)")
    vectors = model.encode(docs, show_progress_bar=True)
    print("[*] Saving to database...")
    collection.add(
        documents=docs,
        embeddings=vectors.tolist(),
        metadatas=metadatas,
        ids=ids
    )
    print(f"[+] Success! Database built at '{db_path}'. It contains {len(docs)} embedded laws.")
    print("[+] You can now run 'python query_db.py' to test the AI search.")
if __name__ == "__main__":
    build_database()
