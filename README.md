# ToDo API

簡易ToDo管理のためのREST API（FastAPI実装）

## 概要

このプロジェクトは、FastAPIを使用したシンプルなToDo管理APIです。インメモリでデータを管理し、基本的なCRUD操作を提供します。

**主な機能:**
- ToDoの新規作成
- ToDoの全件取得
- ToDoの完了化
- ToDoの削除（論理削除）

## 技術スタック

- **Python**: 3.13以上
- **FastAPI**: 0.115.0以上
- **Pydantic**: 2.0以上
- **Uvicorn**: ASGIサーバー
- **uv**: Pythonパッケージ・プロジェクトマネージャー

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd todo-app-demo
```

### 2. 依存関係のインストール

このプロジェクトは`uv`を使用しています。

```bash
# uvがインストールされていない場合
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 依存関係のインストール
uv sync
```

## 起動方法

### 開発サーバーの起動

```bash
uv run uvicorn app.main:app --reload
```

サーバーが起動したら、以下のURLでアクセスできます：

- **APIエンドポイント**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API使用例

### 1. ToDoの作成

```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title": "買い物に行く", "description": "牛乳とパンを買う"}'
```

### 2. ToDoの全件取得

```bash
curl -X GET "http://localhost:8000/todos"
```

### 3. ToDoの完了化

```bash
curl -X PATCH "http://localhost:8000/todos/1/complete"
```

### 4. ToDoの削除

```bash
curl -X DELETE "http://localhost:8000/todos/1"
```

## テストの実行

```bash
# 全テストの実行
uv run pytest tests/ -v

# カバレッジ付きで実行
uv run pytest tests/ --cov=app --cov-report=html
```

## プロジェクト構成

```
todo-app-demo/
├── .docs/                    # プロジェクトドキュメント
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPIアプリケーションのエントリーポイント
│   ├── models.py            # Pydanticモデル定義
│   ├── database.py          # インメモリデータストア管理
│   ├── routers/
│   │   └── todos.py         # ToDoエンドポイントの実装
│   └── utils/
│       └── datetime_utils.py # タイムスタンプ生成ユーティリティ
├── tests/                   # テストファイル
├── pyproject.toml           # プロジェクト設定
└── README.md
```

## データモデル

### ToDoCreate（リクエストモデル）

```json
{
  "title": "買い物に行く",
  "description": "牛乳とパンを買う"
}
```

### ToDo（レスポンスモデル）

```json
{
  "id": 1,
  "title": "買い物に行く",
  "description": "牛乳とパンを買う",
  "completed": false,
  "is_active": true,
  "created_at": "2025-10-30T10:30:00+09:00",
  "updated_at": "2025-10-30T10:30:00+09:00"
}
```

## 注意事項

- **データの永続化**: このAPIはインメモリでデータを管理します。サーバー再起動時にすべてのデータが失われます。
- **認証・認可**: デモ用途のため、認証機能は実装されていません。
- **論理削除**: ToDoの削除は論理削除（`is_active`フラグの変更）で行われ、データは保持されます。

## ライセンス

このプロジェクトはデモ・学習用途です。

## 参考資料

- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [Pydantic v2ドキュメント](https://docs.pydantic.dev/latest/)
- [uv公式ドキュメント](https://docs.astral.sh/uv/)