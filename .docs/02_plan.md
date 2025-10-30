# ToDo API 実装計画書

## 1. プロジェクト概要

FastAPIを使用した簡易ToDo管理REST APIの実装。インメモリでデータを管理し、CRUDの基本操作を提供します。

### 目的
- AI仕様書駆動開発（SDD）のワークフローの実践
- 将来のクライアントアプリ開発の基盤構築
- シンプルかつ明確なAPI設計のベストプラクティス実装

## 2. 技術スタック

| 技術 | バージョン | 用途 |
|------|-----------|------|
| Python | 3.13以上 | プログラミング言語 |
| uv | 最新 | Pythonパッケージ・プロジェクトマネージャー |
| FastAPI | 0.115.0以上 | Webフレームワーク |
| Pydantic | 2.0以上 | データバリデーション |
| uvicorn | 最新 | ASGIサーバー |

### 追加パッケージ（開発用）
- `pytest` - ユニットテスト
- `httpx` - テストクライアント（FastAPIテスト用）
- `pytest-asyncio` - 非同期テスト対応

## 3. プロジェクト構成

```
todo-app-demo/
├── .docs/
│   ├── initial_instruction.md  # 初期指示書
│   ├── 01_spec.md              # API仕様書
│   ├── 02_plan.md              # 実装計画書（本ファイル）
│   └── 03_tasks.md             # タスクリスト
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPIアプリケーションのエントリーポイント
│   ├── models.py            # Pydanticモデル定義
│   ├── database.py          # インメモリデータストア管理
│   ├── routers/
│   │   ├── __init__.py
│   │   └── todos.py         # ToDoエンドポイントの実装
│   └── utils/
│       ├── __init__.py
│       └── datetime_utils.py # タイムスタンプ生成ユーティリティ
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # pytestの共通設定
│   ├── test_todos_create.py # POST /todos のテスト
│   ├── test_todos_list.py   # GET /todos のテスト
│   ├── test_todos_complete.py # PATCH /todos/{id}/complete のテスト
│   └── test_todos_delete.py # DELETE /todos/{id} のテスト
├── pyproject.toml           # uvによる依存関係管理・プロジェクト設定
├── uv.lock                  # uvのロックファイル（自動生成）
├── .python-version          # Python バージョン指定（uv用）
├── .gitignore
└── README.md
```

## 4. 実装方針

### 4.1 データ管理

#### インメモリストレージ
```python
# app/database.py
todos_db: dict[int, dict] = {}
next_id: int = 1
```

**特徴:**
- `dict[int, dict]` 形式でO(1)の高速検索を実現
- グローバル変数で管理（単一プロセス想定）
- サーバー再起動でデータは消失（意図的な仕様）

#### ID生成戦略
- 初期値: 1
- インクリメント方式: `next_id`変数を使用
- 削除後も再利用しない（論理削除のため）

### 4.2 タイムスタンプ管理

**実装例:**
```python
# app/utils/datetime_utils.py
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

def get_current_jst_time() -> datetime:
    """JSTの現在時刻を秒単位精度で取得"""
    return datetime.now(JST).replace(microsecond=0)
```

**仕様:**
- タイムゾーン: JST (UTC+09:00)
- 形式: ISO 8601 (`YYYY-MM-DDTHH:MM:SS+09:00`)
- 精度: 秒単位（マイクロ秒は切り捨て）

### 4.3 論理削除

- `is_active` フィールドで管理
- 削除時: `is_active = False` に変更
- 取得時: `is_active = True` のみフィルタリング
- 更新・削除時: `is_active = False` は404扱い

### 4.4 べき等性

| エンドポイント | べき等性 | 動作 |
|---------------|---------|------|
| PATCH /todos/{id}/complete | あり | 既に完了済みの場合、データを変更せず200 OK |
| DELETE /todos/{id} | なし | 既に削除済みの場合、404 Not Found |

### 4.5 バリデーション戦略

#### Pydanticによる自動バリデーション
- `Field()` による制約（min_length, max_length, ge など）
- カスタムバリデータ（`@field_validator`）

#### カスタムバリデーションルール
1. **title:** 空白文字のみ禁止
2. **description:** 空文字列禁止（`None` は許可）
3. **id:** 1以上の正の整数

### 4.6 エラーハンドリング

#### 400 Bad Request
- Pydanticバリデーションエラー → FastAPIのデフォルト形式
- パスパラメータエラー → FastAPIのデフォルト形式

#### 404 Not Found
- カスタム `ErrorResponse` モデル使用
- `error_code: "TODO_NOT_FOUND"`

#### 500 Internal Server Error
- カスタム `ErrorResponse` モデル使用
- `error_code: "INTERNAL_ERROR"`
- 例外ハンドラでキャッチして統一レスポンス

## 5. データフロー

### 5.1 POST /todos - ToDo作成

```
クライアント
  ↓ (リクエスト)
FastAPIバリデーション（Pydantic ToDoCreate）
  ↓ (バリデーション成功)
ID生成（next_id++）
  ↓
タイムスタンプ生成（created_at, updated_at）
  ↓
todos_db に保存
  ↓
ToDoオブジェクト返却（201 Created）
```

### 5.2 GET /todos - ToDo全件取得

```
クライアント
  ↓ (リクエスト)
todos_db から全ToDoを取得
  ↓
is_active = True でフィルタリング
  ↓
ID昇順でソート
  ↓
ToDoリスト返却（200 OK）
```

### 5.3 PATCH /todos/{id}/complete - ToDo完了化

```
クライアント
  ↓ (リクエスト)
パスパラメータバリデーション（id >= 1）
  ↓
todos_db から該当ToDoを検索
  ↓
存在確認 & is_active確認
  ↓ (存在しない or is_active=False)
404 Not Found
  ↓ (存在 & is_active=True)
completed状態確認
  ↓ (既に completed=True)
データ変更なし、現在の状態を返却（べき等）
  ↓ (completed=False)
completed = True に更新
updated_at を更新
  ↓
更新後のToDoオブジェクト返却（200 OK）
```

### 5.4 DELETE /todos/{id} - ToDo削除

```
クライアント
  ↓ (リクエスト)
パスパラメータバリデーション（id >= 1）
  ↓
todos_db から該当ToDoを検索
  ↓
存在確認 & is_active確認
  ↓ (存在しない or is_active=False)
404 Not Found
  ↓ (存在 & is_active=True)
is_active = False に変更
updated_at を更新
  ↓
削除後のToDoオブジェクト返却（200 OK）
```

## 6. エラーハンドリング戦略

### 6.1 エラー種別と対応

| エラー種別 | HTTPステータス | レスポンス形式 | 実装方法 |
|-----------|---------------|---------------|---------|
| バリデーションエラー | 400 | FastAPIデフォルト | Pydantic自動処理 |
| ToDo未存在 | 404 | ErrorResponse | カスタム例外 |
| サーバーエラー | 500 | ErrorResponse | 例外ハンドラ |

### 6.2 カスタム例外

```python
# app/models.py
class ToDoNotFoundException(Exception):
    def __init__(self, todo_id: int):
        self.todo_id = todo_id
        super().__init__(f"ToDo with id {todo_id} not found")
```

### 6.3 例外ハンドラ

```python
# app/main.py
@app.exception_handler(ToDoNotFoundException)
async def todo_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "error_code": "TODO_NOT_FOUND"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error occurred",
            "error_code": "INTERNAL_ERROR"
        }
    )
```

## 7. テスト戦略

### 7.1 テストレベル

#### ユニットテスト
- 各エンドポイントの正常系・異常系をテスト
- pytest + FastAPI TestClient を使用

#### テストカバレッジ目標
- 90%以上のコードカバレッジ

### 7.2 テストケース設計

#### POST /todos
- ✓ 正常系: タイトルと説明付きで作成
- ✓ 正常系: タイトルのみで作成
- ✓ 異常系: タイトル未指定
- ✓ 異常系: タイトルが空白文字のみ
- ✓ 異常系: タイトルが201文字以上
- ✓ 異常系: 説明が空文字列
- ✓ 異常系: 説明が1001文字以上

#### GET /todos
- ✓ 正常系: データが0件の場合
- ✓ 正常系: データが複数件の場合（ID昇順確認）
- ✓ 正常系: 論理削除されたToDoは含まれない

#### PATCH /todos/{id}/complete
- ✓ 正常系: 未完了→完了への変更
- ✓ 正常系: 既に完了済み（べき等性確認）
- ✓ 異常系: 存在しないID
- ✓ 異常系: 論理削除済みのID
- ✓ 異常系: 不正なパスパラメータ（文字列、負の数など）

#### DELETE /todos/{id}
- ✓ 正常系: 有効なToDoの削除
- ✓ 異常系: 存在しないID
- ✓ 異常系: 既に論理削除済みのID
- ✓ 異常系: 不正なパスパラメータ（文字列、負の数など）

### 7.3 テストフィクスチャ

```python
# tests/conftest.py
@pytest.fixture
def client():
    """FastAPI TestClientのフィクスチャ"""
    from app.main import app
    from app.database import clear_database

    clear_database()  # 各テスト前にDBクリア
    return TestClient(app)
```

## 8. 開発手順

### Phase 1: 基盤構築

#### 1. uvのインストール（未インストールの場合）
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. プロジェクトの初期化
```bash
# プロジェクトディレクトリを作成
mkdir todo-app-demo
cd todo-app-demo

# uvでプロジェクトを初期化
uv init

# Pythonバージョンを指定（3.13以上）
echo "3.13" > .python-version
```

#### 3. 依存関係の追加
```bash
# 本番用依存パッケージ
uv add "fastapi>=0.115.0"
uv add "uvicorn[standard]"

# 開発用依存パッケージ
uv add --dev pytest
uv add --dev httpx
uv add --dev pytest-asyncio
```

#### 4. プロジェクトディレクトリ構造の作成
```bash
mkdir -p app/routers app/utils tests .docs
touch app/__init__.py app/routers/__init__.py app/utils/__init__.py tests/__init__.py
```

#### 5. .gitignore の作成
Python標準の除外ルール + uv関連ファイル

#### 6. README.md の作成
プロジェクト概要、セットアップ手順、起動方法を記述

### Phase 2: コア実装
1. データモデル定義（models.py）
2. インメモリDB実装（database.py）
3. タイムスタンプユーティリティ実装（datetime_utils.py）
4. FastAPIアプリケーション初期化（main.py）

### Phase 3: エンドポイント実装
1. POST /todos の実装
2. GET /todos の実装
3. PATCH /todos/{id}/complete の実装
4. DELETE /todos/{id} の実装
5. エラーハンドリングの統合

### Phase 4: テスト実装
1. テストフレームワークセットアップ
2. 各エンドポイントのテスト実装
3. エッジケースのテスト追加

### Phase 5: ドキュメント整備
1. README.md の充実化
2. コメントの追加
3. OpenAPI仕様の確認

### Phase 6: 動作確認
1. ローカルサーバー起動テスト
   ```bash
   uv run uvicorn app.main:app --reload
   ```
2. Swagger UI での手動テスト
   - http://localhost:8000/docs でアクセス確認
3. 全テストの実行と確認
   ```bash
   uv run pytest tests/ -v
   ```

## 9. 実装上の注意事項

### 9.1 Pythonバージョン固有の機能
- Union型のショートハンド記法（`str | None`）を使用
- Python 3.13以上が必須

### 9.2 Pydantic v2 の特徴
- `@field_validator` デコレータの使用（v1の `@validator` から変更）
- 自動JSONシリアライズ（datetime → ISO 8601文字列）

### 9.3 FastAPI のベストプラクティス
- ルーターによるエンドポイント分離
- Pydanticモデルによる型安全性確保
- 例外ハンドラによる統一的なエラーレスポンス

### 9.4 コーディング規約
- PEP 8 に準拠
- 型ヒントを必ず付与
- docstring を適切に記述（Google Style）

## 10. 今後の拡張性

本実装はデモ・学習用途を想定していますが、以下の拡張が考えられます：

### データ永続化
- SQLite / PostgreSQL への移行
- SQLAlchemy ORM の導入

### 認証・認可
- JWT認証の追加
- ユーザー管理機能

### 追加機能
- ToDoの更新（PUT/PATCH）
- タグ・カテゴリ機能
- 期限管理

### フロントエンド統合
- React / Vue.js クライアントの実装
- WebSocket によるリアルタイム更新

## 11. 参考資料

- [FastAPI 公式ドキュメント](https://fastapi.tiangolo.com/)
- [Pydantic v2 ドキュメント](https://docs.pydantic.dev/latest/)
- [Python datetime ドキュメント](https://docs.python.org/ja/3/library/datetime.html)
- [REST API設計のベストプラクティス](https://restfulapi.net/)

---

**最終更新:** 2025-10-30
**ステータス:** 実装準備完了