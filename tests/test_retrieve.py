from app.rag import retrieve


class FakeCollection:
    def __init__(self, results):
        self.results = results
        self.query_args = None

    def query(self, **kwargs):
        self.query_args = kwargs
        return self.results


def test_search_docs_returns_local_results(monkeypatch):
    fake_results = {
        "documents": [["JWTを使用する"]],
        "metadatas": [[{"title": "認証仕様"}]],
        "distances": [[0.5]],
    }
    fake_collection = FakeCollection(fake_results)

    monkeypatch.setattr(retrieve, "collection", fake_collection)
    monkeypatch.setattr(retrieve, "get_embedding", lambda query: [0.1, 0.2])
    monkeypatch.setattr(
        retrieve,
        "_web_search",
        lambda query: (_ for _ in ()).throw(AssertionError("Web検索は呼ばれない")),
    )

    result = retrieve.search_docs("認証方式")

    assert result["source"] == "local"
    assert result["contexts"] == ["JWTを使用する"]
    assert result["metadatas"] == [{"title": "認証仕様"}]
    assert result["distances"] == [0.5]
    assert fake_collection.query_args["n_results"] == 3


def test_search_docs_falls_back_to_web(monkeypatch):
    fake_results = {
        "documents": [["関連情報なし"]],
        "metadatas": [[{"title": "参考資料"}]],
        "distances": [[1.5]],
    }
    fake_collection = FakeCollection(fake_results)
    web_results = [
        {
            "body": "RAGは検索拡張生成です。",
            "href": "https://example.com/rag",
            "title": "RAGの解説",
        }
    ]

    monkeypatch.setattr(retrieve, "collection", fake_collection)
    monkeypatch.setattr(retrieve, "get_embedding", lambda query: [0.1, 0.2])
    monkeypatch.setattr(retrieve, "_web_search", lambda query: web_results)

    result = retrieve.search_docs("RAGとは")

    assert result["source"] == "web"
    assert result["contexts"] == ["RAGは検索拡張生成です。"]
    assert result["metadatas"] == [
        {
            "url": "https://example.com/rag",
            "title": "RAGの解説",
        }
    ]
    assert result["distances"] == []
