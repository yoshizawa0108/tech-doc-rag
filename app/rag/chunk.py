from langchain_text_splitters import MarkdownHeaderTextSplitter

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "title"),
        ("##", "section"),
    ]
)


def split_text(text: str):
    docs = splitter.split_text(text)

    # タイトル直下の概要を全チャンクに付与する
    overview = next((d.page_content for d in docs if d.metadata.get("section") == "概要"), "")

    return [
        (
            f"{d.metadata.get('title', '')} "
            f"{d.metadata.get('section', '')}\n"
            f"{overview}\n"
            f"{d.page_content}"
        )
        for d in docs
    ]
