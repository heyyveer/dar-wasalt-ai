
import json
import hashlib
import re
from pathlib import Path

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_id(source, url, content):
    value = f"{source}|{url}|{content}"
    return hashlib.sha256(value.encode()).hexdigest()[:16]

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def load_json(filename):
    path = RAW_DIR / filename

    if not path.exists():
        print(f"[MISSING] {path}")
        return []

    with path.open(encoding="utf-8") as file:
        return json.load(file)


def build_darglobal_documents(records):
    documents = []

    for record in records:
        paragraphs = [
            clean_text(p)
            for p in record["text"].split("\n")
            if len(clean_text(p)) > 100
        ]

        for paragraph in paragraphs:
            # Use the announcement's opening sentence as its title
            title = re.split(r"(?<=[.!?])\s+", paragraph, maxsplit=1)[0]

            documents.append({
                "id": generate_id(
                    record["source"],
                    record["url"],
                    paragraph
                ),
                "source": record["source"],
                "category": "news",
                "title": title[:180],
                "url": record["url"],
                "content": paragraph
            })

    return documents


def build_wasalt_documents(records):
    documents = []

    for record in records:
        content = clean_text(record["text"])

        if len(content) < 100:
            continue

        url = record["url"]

        if "/corporate" in url:
            category = "company_information"
        elif "properties-for-sale" in url:
            category = "property_search_information"
        else:
            category = "platform_information"

        documents.append({
            "id": generate_id(
                record["source"],
                url,
                content
            ),
            "source": record["source"],
            "category": category,
            "title": record["title"],
            "url": url,
            "content": content
        })

    return documents


def run():
    dar_records = load_json("darglobal.json")
    wasalt_records = load_json("wasalt.json")

    documents = (
        build_darglobal_documents(dar_records)
        + build_wasalt_documents(wasalt_records)
    )

    unique_documents = {
        doc["id"]: doc for doc in documents
    }

    documents = list(unique_documents.values())

    output_path = OUTPUT_DIR / "documents.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(documents, file, indent=2, ensure_ascii=False)

    print("Total documents:", len(documents))
    print("Saved:", output_path)

if __name__ == "__main__":
    run()
