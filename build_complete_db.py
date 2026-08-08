
import os
import sys
import io
import ssl
import urllib3
import json
import chromadb
from sentence_transformers import SentenceTransformer
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
def build_complete_database():
    print("=" * 60)
    print("  NYAYA SAHAYAK - COMPLETE BNS DATABASE BUILDER")
    print("  Building ALL 358 sections...")
    print("=" * 60)
    all_sections = []
    hf_success = False
    try:
        print("\n[1/4] Attempting to download complete BNS from HuggingFace...")
        from datasets import load_dataset
        dataset = load_dataset("GSMS-B/indian-legal-sections-bns-bnss-bsa-2023", data_files="bns_sections.json")
        hf_data = dataset['train']
        for item in hf_data:
            sec_num = item.get("section_number", item.get("Section", ""))
            title = item.get("section_title", item.get("title", "Unknown Title"))
            desc = item.get("text", item.get("description", ""))
            if sec_num and desc:
                all_sections.append({
                    "section_number": str(sec_num),
                    "title": str(title),
                    "description": str(desc)
                })
        if len(all_sections) >= 300:
            hf_success = True
            print(f"    [+] HuggingFace: Downloaded {len(all_sections)} sections successfully!")
        else:
            print(f"    [-] HuggingFace: Only got {len(all_sections)} sections. Will supplement with local data.")
    except Exception as e:
        print(f"    [-] HuggingFace download failed: {e}")
        print("    [*] Will use local fallback data instead.")
    if not hf_success:
        print("\n[2/4] Loading local BNS sections 1-237...")
        from bns_sections_1_to_237 import bns_sections_1_to_237
        existing_nums = {s["section_number"] for s in all_sections}
        added_count = 0
        for sec in bns_sections_1_to_237:
            if sec["section_number"] not in existing_nums:
                all_sections.append(sec)
                existing_nums.add(sec["section_number"])
                added_count += 1
        print(f"    [+] Added {added_count} sections from local data (1-237)")
        print("    [*] Loading existing sections 238-358 from current database...")
        try:
            db_path = os.path.join(os.path.dirname(__file__), "bns_chroma_db")
            old_client = chromadb.PersistentClient(path=db_path)
            old_collection = old_client.get_collection(name="bns_sections")
            old_results = old_collection.get()
            old_added = 0
            for i, meta in enumerate(old_results['metadatas']):
                sec_num = meta['section']
                if sec_num not in existing_nums:
                    doc_text = old_results['documents'][i]
                    desc_part = doc_text.split(". ", 1)[1] if ". " in doc_text else doc_text
                    all_sections.append({
                        "section_number": sec_num,
                        "title": meta['title'],
                        "description": desc_part
                    })
                    existing_nums.add(sec_num)
                    old_added += 1
            print(f"    [+] Added {old_added} sections from existing database (238-358)")
        except Exception as e:
            print(f"    [-] Could not read existing DB: {e}")
    print(f"\n    >>> TOTAL SECTIONS TO EMBED: {len(all_sections)}")
    print("\n[3/4] Rebuilding ChromaDB vector database...")
    db_path = os.path.join(os.path.dirname(__file__), "bns_chroma_db")
    client = chromadb.PersistentClient(path=db_path)
    try:
        client.delete_collection(name="bns_sections")
        print("    [*] Deleted old collection.")
    except:
        pass
    collection = client.create_collection(name="bns_sections")
    print("    [*] Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    docs = []
    metadatas = []
    ids = []
    try:
        from bns_enrichment_data import BNS_ENRICHMENT
    except ImportError:
        BNS_ENRICHMENT = {}
    for i, sec in enumerate(all_sections):
        sec_num = str(sec['section_number'])
        title = str(sec['title'])
        desc = str(sec['description'])
        enrich = BNS_ENRICHMENT.get(sec_num, {})
        ipc_eq = enrich.get("ipc_eq", "Unknown")
        punishment = enrich.get("punishment", "Unknown")
        chapter = enrich.get("chapter", "Unknown")
        keywords = enrich.get("keywords", "")
        text_to_embed = f"Section {sec_num}: {title}. {desc} IPC Equivalent: {ipc_eq}. Punishment: {punishment}. Keywords: {keywords}"
        docs.append(text_to_embed)
        metadatas.append({
            "section": sec_num,
            "title": title,
            "chapter": chapter,
            "ipc_eq": ipc_eq,
            "punishment": punishment,
            "cognizable": enrich.get("cognizable", "Unknown"),
            "bailable": enrich.get("bailable", "Unknown")
        })
        ids.append(f"sec_{sec_num}_{i}")
    print("\n[4/4] Generating vector embeddings... (This is CPU intensive)")
    vectors = model.encode(docs, show_progress_bar=True)
    print("    [*] Saving to database...")
    batch_size = 100
    for start in range(0, len(docs), batch_size):
        end = min(start + batch_size, len(docs))
        collection.add(
            documents=docs[start:end],
            embeddings=vectors[start:end].tolist(),
            metadatas=metadatas[start:end],
            ids=ids[start:end]
        )
    print(f"\n{'=' * 60}")
    print(f"  SUCCESS! Database rebuilt with {len(docs)} BNS sections!")
    print(f"  Database path: {db_path}")
    print(f"{'=' * 60}")
    verify_col = client.get_collection(name="bns_sections")
    print(f"\n  Verification: {verify_col.count()} sections in database.")
    print("\n  Quick test: Searching for 'kidnapping of minor girl'...")
    test_vec = model.encode(["kidnapping of minor girl missing from home"]).tolist()
    test_results = verify_col.query(query_embeddings=test_vec, n_results=3)
    for i, meta in enumerate(test_results['metadatas'][0]):
        print(f"    Result {i+1}: Section {meta['section']} - {meta['title']}")
if __name__ == "__main__":
    build_complete_database()
