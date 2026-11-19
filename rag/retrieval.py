
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

DB_PATH = "chroma_db"
COLLECTION_NAME = "dar_wasalt_knowledge"

embedding_function = DefaultEmbeddingFunction()

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function
)


def retrieve(
    query,
    top_k=5,
    source_filter=None,
    max_distance=None
):
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    if max_distance is not None and max_distance < 0:
        raise ValueError("max_distance cannot be negative.")

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    query_args = {
        "query_texts": [query],
        "n_results": min(top_k, total_chunks)
    }

    if source_filter:
        query_args["where"] = {
            "source": source_filter
        }

    results = collection.query(**query_args)

    retrieved_documents = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for content, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        if max_distance is not None and distance > max_distance:
            continue

        retrieved_documents.append({
            "content": content,
            "metadata": metadata,
            "distance": distance
        })

    return retrieved_documents


if __name__ == "__main__":
    query = "What projects is DarGlobal developing?"

    results = retrieve(
        query,
        top_k=5
    )

    print("\nRETRIEVAL RESULTS")
    print("=" * 60)

    for index, result in enumerate(results, start=1):
        print(f"\nRESULT {index}")
        print("Source:", result["metadata"]["source"])
        print("Title:", result["metadata"]["title"])
        print("Distance:", round(result["distance"], 4))
        print("Content:", result["content"][:500])
