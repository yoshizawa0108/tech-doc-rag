import os

from dotenv import load_dotenv
from groq import Groq

from app.rag.retrieve import search_docs

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def answer(query: str) -> dict:
    retrieved = search_docs(query)
    context_text = "\n\n".join(retrieved["contexts"])

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたは技術ドキュメントのQ&Aアシスタントです。"
                    "必ず提供されたコンテキストの情報だけを使って答えてください。"
                    "コンテキストに答えがない場合は「該当なし」とだけ答えてください。"
                    "コンテキスト外の知識で補完しないでください。"
                    "回答はコンテキストから該当箇所を抜き出すだけでよいです。説明不要。"
                ),
            },
            {"role": "user", "content": f"コンテキスト:\n{context_text}\n\n質問: {query}"},
        ],
    )

    answer_text = response.choices[0].message.content

    # ローカルで答えられなかった場合はWebで再検索
    if "該当なし" in answer_text and retrieved["source"] == "local":
        from app.rag.retrieve import _web_search

        web_results = _web_search(query)
        web_context = "\n\n".join([r["body"] for r in web_results])

        web_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": f"コンテキスト:\n{web_context}\n\n質問: {query}"}
            ],
        )

        return {
            "answer": web_response.choices[0].message.content,
            "source_type": "web",
            "sources": [{"url": r["href"], "title": r["title"]} for r in web_results],
        }

    return {
        "answer": answer_text,
        "source_type": retrieved["source"],
        "sources": retrieved["metadatas"],
    }
