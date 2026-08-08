import chromadb
import os
client = chromadb.PersistentClient(path=os.path.join(os.getcwd(), "bns_chroma_db"))
col = client.get_collection("bns_sections")
print(f"Total sections in DB: {col.count()}")
results = col.get()
sections = []
for m in results["metadatas"]:
    sections.append(f"Section {m['section']}: {m['title']}")
sections.sort(key=lambda x: int(x.split(":")[0].replace("Section ", "").strip()) if x.split(":")[0].replace("Section ", "").strip().isdigit() else 0)
for s in sections:
    print(s)
