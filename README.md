# Tech Doc RAG

技術ドキュメントへの質問に答えるRAG API。
ローカルdocsとWeb検索を組み合わせて回答。

## 構成

- **FastAPI** — APIサーバー
- **ChromaDB** — ベクトルDB
- **sentence-transformers** — 埋め込みモデル（all-MiniLM-L6-v2）
- **DuckDuckGo Search** — Web検索フォールバック
- **Groq / llama-3.3-70b** — LLM（無料）

## アーキテクチャ

```
質問
 ↓
ChromaDB でローカルdocs検索（距離スコアで関連度を判定）
 ↓ 距離 < 1.1
LLM で回答生成
 ↓ 「該当なし」の場合
DuckDuckGo でWeb検索 → LLM で回答生成
 ↓ 距離 ≥ 1.1 の場合も同様
回答 + ソース明示（local / web）
```

## 設計のポイント

`source_type` で回答ソースを明示。

- ローカルdocsに関連情報あり → `local`
- ローカルdocsで回答不可 → `web`

距離スコアとLLMの2段階でフォールバックを判定。ハルシネーションを防ぎつつ適切なソースから回答。

## セットアップ

```bash
git clone https://github.com/yoshizawa0108/tech-doc-rag
cd tech-doc-rag
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`.env` を作成。

```
GROQ_API_KEY=your_api_key_here
```

> APIキーは https://console.groq.com/keys から無料で取得。

## 起動

```bash
# ドキュメント取り込み（初回のみ）
make ingest

# サーバー起動
make run
```

## API

### POST `/api/ask`

**リクエスト**
```json
{ "query": "認証方式について教えて" }
```

**レスポンス（ローカルdocsから回答）**
```json
{
  "query": "認証方式について教えて",
  "answer": "JWTを使用する。",
  "source_type": "local",
  "sources": [{"file": "api_spec.md", "chunk_id": 0}]
}
```

**レスポンス（Webフォールバック）**
```json
{
  "query": "RAGとは",
  "answer": "RAGとはRetrieval-Augmented Generationの略で...",
  "source_type": "web",
  "sources": [{"url": "https://...", "title": "..."}]
}
```

### GET `/api/search?q=xxx`

ChromaDBの生スコアを返すデバッグ用エンドポイント。