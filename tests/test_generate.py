from types import SimpleNamespace

from app.rag import generate, retrieve


class FakeCompletions:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        answer_text = next(self.responses)

        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=answer_text))]
        )


class FakeClient:
    def __init__(self, responses):
        self.completions = FakeCompletions(responses)
        self.chat = SimpleNamespace(completions=self.completions)


def test_answer_returns_local_result(monkeypatch):
    fake_client = FakeClient(["JWTを使用します。"])

    monkeypatch.setattr(generate, "_get_client", lambda: fake_client)
    monkeypatch.setattr(
        generate,
        "search_docs",
        lambda query: {
            "source": "local",
            "contexts": ["認証にはJWTを使用します。"],
            "metadatas": [{"title": "認証仕様"}],
            "distances": [0.5],
        },
    )
    monkeypatch.setattr(
        retrieve,
        "_web_search",
        lambda query: (_ for _ in ()).throw(AssertionError("Web検索は呼ばれない")),
    )

    result = generate.answer("認証方式は？")

    assert result["answer"] == "JWTを使用します。"
    assert result["source_type"] == "local"
    assert result["sources"] == [{"title": "認証仕様"}]
    assert len(fake_client.completions.calls) == 1


def test_answer_falls_back_to_web_when_local_has_no_answer(monkeypatch):
    fake_client = FakeClient(
        [
            "該当なし",
            "RAGは検索拡張生成です。",
        ]
    )
    web_results = [
        {
            "body": "RAGは検索拡張生成です。",
            "href": "https://example.com/rag",
            "title": "RAGの解説",
        }
    ]

    monkeypatch.setattr(generate, "_get_client", lambda: fake_client)
    monkeypatch.setattr(
        generate,
        "search_docs",
        lambda query: {
            "source": "local",
            "contexts": ["関連情報がありません。"],
            "metadatas": [{"title": "技術資料"}],
            "distances": [0.5],
        },
    )
    monkeypatch.setattr(
        retrieve,
        "_web_search",
        lambda query: web_results,
    )

    result = generate.answer("RAGとは？")

    assert result["answer"] == "RAGは検索拡張生成です。"
    assert result["source_type"] == "web"
    assert result["sources"] == [
        {
            "url": "https://example.com/rag",
            "title": "RAGの解説",
        }
    ]
    assert len(fake_client.completions.calls) == 2
