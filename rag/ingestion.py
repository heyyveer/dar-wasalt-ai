
import json
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

DATA_PATH = Path("data/processed/documents.json")
DB_PATH = "chroma_db"
COLLECTION_NAME = "dar_wasalt_knowledge"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

def chunk_text(text):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks

def run():
    with DATA_PATH.open(encoding="utf-8") as file:
        documents = json.load(file)

    model = SentenceTransformer("all-MiniLM-L6-v2")

    client = chromadb.PersistentClient(path=DB_PATH)

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    ids = []
    texts = []
    metadatas = []

    for document in documents:
        chunks = chunk_text(document["content"])

        for index, chunk in enumerate(chunks):
            chunk_id = f"{document['id']}_{index}"

            ids.append(chunk_id)
            texts.append(chunk)

            metadatas.append({
                "source": document["source"],
                "category": document["category"],
                "title": document["title"],
                "url": document["url"],
                "document_id": document["id"]
            })

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings.tolist()
    )

    print("\nINGESTION COMPLETE")
    print("Documents:", len(documents))
    print("Chunks:", len(texts))
    print("Vector count:", collection.count())

if __name__ == "__main__":
    run()
