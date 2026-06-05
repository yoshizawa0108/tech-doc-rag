# ログインAPI仕様

## 概要
ユーザー認証にはJWTを使用する。

## エンドポイント
POST /login

## リクエスト
- email: string
- password: string

## レスポンス
- access_token: string

## トークン有効期限
30分