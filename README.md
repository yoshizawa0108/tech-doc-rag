# Tech Doc RAG

技術ドキュメントへの質問に答えるRAG API。

ローカルの技術ドキュメントとWeb検索を組み合わせ、質問に関連する情報を検索して回答を生成する。

## 構成

- **FastAPI** — APIサーバー
- **ChromaDB** — ベクトルDB
- **sentence-transformers** — 埋め込みモデル（all-MiniLM-L6-v2）
- **DuckDuckGo Search** — Web検索フォールバック
- **Groq / llama-3.3-70b** — LLM（無料利用枠あり）

## アーキテクチャ

```text
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

距離スコアとLLMの2段階でフォールバックを判定。ハルシネーションを抑えつつ、適切なソースから回答する。

## 必要環境

- Python 3.14
- [uv](https://docs.astral.sh/uv/)

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/yoshizawa0108/tech-doc-rag.git
cd tech-doc-rag
```

### 2. 依存パッケージをインストール

```bash
uv sync
```

`.venv` が自動作成され、必要なパッケージがインストールされる。

### 3. 環境変数を設定

プロジェクトのルートに `.env` を作成する。

```env
GROQ_API_KEY=your_api_key_here
```

APIキーは [Groq Console](https://console.groq.com/keys) から取得できる。

## 起動

### ドキュメント取り込み

初回起動時やローカルドキュメントを更新したときに実行する。

```bash
make ingest
```

### APIサーバー起動

```bash
make run
```

サーバー起動後、以下からAPIドキュメントを確認できる。

- http://127.0.0.1:8000/docs

## 開発用コマンド

```bash
# テスト
make test

# Lint
make lint

# コードフォーマット
make format
```

テストは `tests/` に配置し、外部APIや検索処理をモックして実行します。

## API

### POST `/api/ask`

質問に対する回答を生成する。

**リクエスト**

```json
{
  "query": "認証方式について教えて"
}
```

**レスポンス（ローカルdocsから回答）**

```json
{
  "query": "認証方式について教えて",
  "answer": "JWTを使用する。",
  "source_type": "local",
  "sources": [
    {
      "file": "api_spec.md",
      "chunk_id": 0
    }
  ]
}
```

**レスポンス（Webフォールバック）**

```json
{
  "query": "RAGとは",
  "answer": "RAGとはRetrieval-Augmented Generationの略で...",
  "source_type": "web",
  "sources": [
    {
      "url": "https://...",
      "title": "..."
    }
  ]
}
```

### GET `/api/search?q=xxx`

ChromaDBの検索結果と生スコアを返すデバッグ用エンドポイント。
