from fastapi.testclient import TestClient

from app.api import routes
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Tech Doc RAG is running"}


def test_ask_returns_answer(monkeypatch):
    def fake_answer(query):
        return {
            "answer": "JWTを使用します。",
            "source_type": "local",
            "sources": [{"title": "認証仕様"}],
        }

    monkeypatch.setattr(routes, "answer", fake_answer)

    response = client.post(
        "/api/ask",
        json={"query": "認証方式は？"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "query": "認証方式は？",
        "answer": "JWTを使用します。",
        "source_type": "local",
        "sources": [{"title": "認証仕様"}],
    }


def test_search_returns_results(monkeypatch):
    def fake_search_docs(query):
        return {
            "source": "local",
            "contexts": ["JWTを使用する"],
            "metadatas": [{"title": "認証仕様"}],
            "distances": [0.5],
        }

    monkeypatch.setattr(routes, "search_docs", fake_search_docs)

    response = client.get(
        "/api/search",
        params={"q": "認証方式"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "query": "認証方式",
        "results": {
            "source": "local",
            "contexts": ["JWTを使用する"],
            "metadatas": [{"title": "認証仕様"}],
            "distances": [0.5],
        },
    }


def test_ask_returns_500_when_answer_fails(monkeypatch):
    def fake_answer(query):
        raise RuntimeError("テスト用エラー")

    monkeypatch.setattr(routes, "answer", fake_answer)

    response = client.post(
        "/api/ask",
        json={"query": "認証方式は？"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "テスト用エラー"}
