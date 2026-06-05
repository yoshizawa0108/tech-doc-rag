from ddgs import DDGS
import chromadb
from sentence_transformers import SentenceTransformer

chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="tech_docs")
model = SentenceTransformer("all-MiniLM-L6-v2")

DISTANCE_THRESHOLD = 1.1

def get_embedding(text: str):
    return model.encode(text).tolist()

def search_docs(query: str, top_k: int = 3) -> dict:
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    best_distance = min(results["distances"][0])

    if best_distance < DISTANCE_THRESHOLD:
        return {
            "source": "local",
            "contexts": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0],
        }
    else:
        web_results = _web_search(query)
        return {
            "source": "web",
            "contexts": [r["body"] for r in web_results],
            "metadatas": [{"url": r["href"], "title": r["title"]} for r in web_results],
            "distances": [],
        }

def _web_search(query: str, max_results: int = 3) -> list[dict]:
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))