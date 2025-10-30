# ToDo API 実装タスクリスト

## 進捗概要

- **総タスク数:** 46
- **完了:** 0
- **進行中:** 0
- **未着手:** 46

---

## Phase 1: プロジェクトセットアップ (8タスク)

### 1.1 プロジェクト構造の作成

- [ ] `app/` ディレクトリの作成
- [ ] `app/__init__.py` の作成
- [ ] `app/routers/` ディレクトリの作成
- [ ] `app/routers/__init__.py` の作成
- [ ] `app/utils/` ディレクトリの作成
- [ ] `app/utils/__init__.py` の作成
- [ ] `tests/` ディレクトリの作成
- [ ] `tests/__init__.py` の作成

### 1.2 依存関係の定義

- [ ] uvのインストール確認
  - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Windows: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

- [ ] プロジェクトの初期化
  - `uv init` でプロジェクト初期化
  - `.python-version` ファイルの作成（3.13以上を指定）

- [ ] 本番用依存パッケージの追加
  - `uv add "fastapi>=0.115.0"`
  - `uv add "uvicorn[standard]"`

- [ ] 開発用依存パッケージの追加
  - `uv add --dev pytest`
  - `uv add --dev httpx`
  - `uv add --dev pytest-asyncio`

### 1.3 プロジェクトドキュメント

- [ ] `README.md` の作成
  - プロジェクト概要
  - セットアップ手順
  - 起動方法
  - API使用例

- [ ] `.gitignore` の作成
  - Python標準（`__pycache__/`, `*.py[cod]`, `.pytest_cache/` など）
  - uv関連（`.venv/`、`uv.lock` は含めるかプロジェクト方針次第）

---

## Phase 2: データモデル実装 (6タスク)

### 2.1 Pydanticモデルの定義

- [ ] `app/models.py` の作成

- [ ] `ToDoCreate` モデルの実装
  - `title` フィールド定義（Field, min_length=1, max_length=200）
  - `description` フィールド定義（Field, max_length=1000, optional）

- [ ] `ToDoCreate` のバリデータ実装
  - `@field_validator('title')`: 空白文字のみチェック
  - `@field_validator('description')`: 空文字列禁止チェック

- [ ] `ToDo` モデルの実装
  - 全フィールド定義（id, title, description, completed, is_active, created_at, updated_at）
  - Field制約の追加（id >= 1 など）

- [ ] `ErrorResponse` モデルの実装
  - `detail` フィールド定義
  - `error_code` フィールド定義（optional）

- [ ] カスタム例外クラスの実装
  - `ToDoNotFoundException` の定義

---

## Phase 3: データベース層実装 (3タスク)

### 3.1 インメモリデータストア

- [ ] `app/database.py` の作成

- [ ] グローバル変数の定義
  - `todos_db: dict[int, dict] = {}`
  - `next_id: int = 1`

- [ ] データベース操作関数の実装
  - `get_all_active_todos()`: is_active=True のToDo取得、ID昇順ソート
  - `get_todo_by_id(todo_id: int)`: 指定IDのToDo取得
  - `create_todo(todo_data: dict)`: ToDo作成、ID自動割り当て
  - `update_todo(todo_id: int, updates: dict)`: ToDo更新
  - `clear_database()`: テスト用DB初期化関数

---

## Phase 4: ユーティリティ実装 (2タスク)

### 4.1 タイムスタンプユーティリティ

- [ ] `app/utils/datetime_utils.py` の作成

- [ ] タイムスタンプ関数の実装
  - `JST` タイムゾーン定義（`timezone(timedelta(hours=9))`）
  - `get_current_jst_time()`: 現在時刻取得（秒単位精度）

---

## Phase 5: エンドポイント実装 (10タスク)

### 5.1 FastAPIアプリケーション初期化

- [ ] `app/main.py` の作成
  - FastAPIアプリケーションインスタンス作成
  - メタデータ設定（title, version, description）

- [ ] エラーハンドラの実装
  - `ToDoNotFoundException` 用ハンドラ（404）
  - 汎用例外ハンドラ（500）

### 5.2 ToDoルーターの実装

- [ ] `app/routers/todos.py` の作成
  - APIRouterインスタンス作成

### 5.3 POST /todos - ToDo作成

- [ ] エンドポイント関数の実装
  - リクエストボディバリデーション（ToDoCreate）
  - ID生成（next_id使用）
  - タイムスタンプ生成（created_at, updated_at）
  - データベースへ保存
  - 201 Createdレスポンス

### 5.4 GET /todos - ToDo全件取得

- [ ] エンドポイント関数の実装
  - is_active=True のToDo取得
  - ID昇順ソート
  - 200 OKレスポンス（list[ToDo]）

### 5.5 PATCH /todos/{id}/complete - ToDo完了化

- [ ] エンドポイント関数の実装
  - パスパラメータバリデーション（id >= 1）
  - ToDo存在確認（is_active=True）
  - 完了状態チェック（べき等性）
  - completed = True に更新（未完了の場合のみ）
  - updated_at 更新（データ変更時のみ）
  - 200 OKレスポンス

### 5.6 DELETE /todos/{id} - ToDo削除

- [ ] エンドポイント関数の実装
  - パスパラメータバリデーション（id >= 1）
  - ToDo存在確認（is_active=True）
  - is_active = False に変更
  - updated_at 更新
  - 200 OKレスポンス

### 5.7 ルーターの統合

- [ ] `app/main.py` にルーターを登録
  - `app.include_router(todos.router)`

---

## Phase 6: テスト実装 (12タスク)

### 6.1 テストセットアップ

- [ ] `tests/conftest.py` の作成
  - `client` フィクスチャの実装（TestClient + DB初期化）

### 6.2 POST /todos のテスト

- [ ] `tests/test_todos_create.py` の作成

- [ ] 正常系テスト
  - タイトル + 説明付きで作成
  - タイトルのみで作成
  - レスポンスフィールド検証
  - タイムスタンプ形式検証

- [ ] 異常系テスト
  - タイトル未指定（400）
  - タイトルが空白文字のみ（400）
  - タイトルが201文字以上（400）
  - 説明が空文字列（400）
  - 説明が1001文字以上（400）

### 6.3 GET /todos のテスト

- [ ] `tests/test_todos_list.py` の作成

- [ ] 正常系テスト
  - データが0件の場合（空配列）
  - データが複数件の場合（ID昇順確認）
  - 論理削除されたToDoは含まれない確認

### 6.4 PATCH /todos/{id}/complete のテスト

- [ ] `tests/test_todos_complete.py` の作成

- [ ] 正常系テスト
  - 未完了→完了への変更
  - updated_at が更新されることを確認
  - 既に完了済み（べき等性、updated_at不変確認）

- [ ] 異常系テスト
  - 存在しないID（404）
  - 論理削除済みのID（404）
  - 不正なパスパラメータ（文字列、負の数、0）（400）

### 6.5 DELETE /todos/{id} のテスト

- [ ] `tests/test_todos_delete.py` の作成

- [ ] 正常系テスト
  - 有効なToDoの削除
  - is_active が False になることを確認
  - updated_at が更新されることを確認

- [ ] 異常系テスト
  - 存在しないID（404）
  - 既に論理削除済みのID（404）
  - 不正なパスパラメータ（文字列、負の数、0）（400）

---

## Phase 7: ドキュメント整備 (3タスク)

### 7.1 README.md の充実化

- [ ] プロジェクト概要の記述
- [ ] セットアップ手順の詳細化
- [ ] API使用例の追加（curl コマンド例）
- [ ] テスト実行方法の記述

### 7.2 コードコメントの追加

- [ ] 各モジュールの docstring 追加
- [ ] 複雑なロジックへのインラインコメント追加

### 7.3 OpenAPI仕様の確認

- [ ] Swagger UI での動作確認
- [ ] レスポンスモデルの正確性確認

---

## Phase 8: 動作確認・最終調整 (2タスク)

### 8.1 ローカル起動テスト

- [ ] サーバー起動確認
  - `uv run uvicorn app.main:app --reload`
  - http://localhost:8000 でアクセス確認
  - http://localhost:8000/docs でSwagger UI確認

### 8.2 統合テストの実行

- [ ] 全テストの実行
  - `uv run pytest tests/ -v`
  - すべてのテストがパスすることを確認
  - カバレッジレポートの確認（可能であれば）

---

## 進捗管理

### 日次チェックリスト

- [ ] 本日実装したタスクをチェック
- [ ] 実装したコードのテストを実行
- [ ] コミットメッセージの作成
- [ ] 次のタスクの確認

### 完了基準

すべてのタスクがチェックされ、以下の条件を満たすこと：

1. すべてのエンドポイントが仕様通りに動作
2. すべてのテストがパス
3. README.md が充実し、第三者が容易にセットアップできる
4. OpenAPI仕様が正確に生成される
5. コードが PEP 8 に準拠し、型ヒントが適切に付与されている

---

**作成日:** 2025-10-30
**最終更新:** 2025-10-30
**ステータス:** 未着手