from app.rag.chunk import split_text
from pathlib import Path
from app.rag.retrieve import get_embedding, collection

def load_docs():
    docs_path = Path("docs")

    for file in docs_path.glob("*.md"):
        text = file.read_text(encoding="utf-8")
        chunks = split_text(text)

        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)

            collection.add(
                embeddings=[embedding],
                documents=[chunk],
                ids=[f"{file.stem}_{i}"],
                metadatas=[{
                    "file": file.name,
                    "chunk_id": i
                }]
            )

if __name__ == "__main__":
    load_docs()
    print("ingest done")