from app.rag.chunk import split_text


def test_split_text_splits_by_markdown_headers():
    text = """# 認証API

## 概要
認証APIの概要です。

## 認証方式
JWTを使用します。

## エラー処理
401を返します。
"""

    result = split_text(text)

    assert len(result) == 3
    assert "認証API 概要" in result[0]
    assert "認証API 認証方式" in result[1]
    assert "認証API エラー処理" in result[2]


def test_split_text_adds_overview_to_all_chunks():
    text = """# 認証API

## 概要
認証APIの概要です。

## 認証方式
JWTを使用します。

## エラー処理
401を返します。
"""

    result = split_text(text)

    assert len(result) == 3
    assert all("認証APIの概要です。" in chunk for chunk in result)


def test_split_text_without_overview():
    text = """# 認証API

## 認証方式
JWTを使用します。
"""

    result = split_text(text)

    assert len(result) == 1
    assert "JWTを使用します。" in result[0]


def test_split_text_with_empty_text():
    result = split_text("")

    assert result == []
