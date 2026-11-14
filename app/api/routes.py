from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.rag.generate import answer
from app.rag.retrieve import search_docs

router = APIRouter()


class AskRequest(BaseModel):
    query: str


# ── メインエンドポイント ──────────────────────────────
@router.post("/ask")
def ask(req: AskRequest):
    try:
        result = answer(req.query)
        return {
            "query": req.query,
            "answer": result["answer"],
            "source_type": result["source_type"],  # "local" | "web"
            "sources": result["sources"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── デバッグ用: 生の検索結果を返す（既存を維持）────────
@router.get("/search")
def search(q: str):
    results = search_docs(q)
    return {
        "query": q,
        "results": results,
    }
