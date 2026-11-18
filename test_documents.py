import json

with open("data/processed/documents.json", encoding="utf-8") as f:
    documents = json.load(f)

for doc in documents:
    print("\nID:", doc["id"])
    print("Source:", doc["source"])
    print("Category:", doc["category"])
    print("Title:", doc["title"])
    print("Content:", doc["content"][:200])