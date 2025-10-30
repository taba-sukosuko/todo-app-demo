# ToDo API 仕様書

## 概要

簡易ToDo管理のためのREST API仕様書です。本APIはFastAPIで実装され、インメモリでデータを管理します。

- **ベースURL:** `http://localhost:8000`
- **API バージョン:** 1.0.0
- **パッケージマネージャー:** uv（Pythonパッケージ・プロジェクトマネージャー）
- **Python バージョン:** 3.13以上
- **FastAPI バージョン:** 0.115.0以上
- **Pydantic バージョン:** 2.0以上
- **認証:** なし（ローカル開発用デモ）
- **文字エンコーディング:** UTF-8
- **タイムゾーン:** Asia/Tokyo (JST, UTC+09:00)
- **Content-Type:** すべてのリクエスト/レスポンスで `application/json` を使用

---

## データモデル

### Pydanticモデル定義

#### `ToDoCreate` (リクエストモデル)

```python
from pydantic import BaseModel, Field, field_validator

class ToDoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="ToDoのタイトル")
    description: str | None = Field(None, max_length=1000, description="ToDoの詳細説明（オプション）")

    @field_validator('title')
    @classmethod
    def title_must_not_be_whitespace_only(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError('Title must not be whitespace only')
        return v

    @field_validator('description')
    @classmethod
    def description_must_not_be_empty_string(cls, v: str | None) -> str | None:
        if v == "":
            raise ValueError('Description must be null, not empty string')
        return v
```

**バリデーションルール:**
- `title`: 1文字以上200文字以内（必須）、空白文字のみは不可
- `description`: 1000文字以内（オプション）、空文字列は不可、未指定時は`null`として扱う

#### `ToDo` (レスポンスモデル)

```python
from datetime import datetime
from pydantic import BaseModel, Field

class ToDo(BaseModel):
    id: int = Field(..., description="ToDoの一意なID（1から開始）", ge=1)
    title: str = Field(..., description="ToDoのタイトル")
    description: str | None = Field(None, description="ToDoの詳細説明")
    completed: bool = Field(default=False, description="完了状態（True: 完了、False: 未完了）")
    is_active: bool = Field(default=True, description="有効状態（True: 有効、False: 論理削除済み）")
    created_at: datetime = Field(..., description="作成日時（ISO 8601形式、秒単位精度、JST）")
    updated_at: datetime = Field(..., description="更新日時（ISO 8601形式、秒単位精度、JST）")
```

**フィールド詳細:**
- `id`: 1から開始する自動インクリメントID、削除後も再利用しない
- `is_active`: 論理削除フラグ（`False`の場合は削除済み）
- `created_at`, `updated_at`: `YYYY-MM-DDTHH:MM:SS+09:00` 形式（例: `2025-10-30T10:30:00+09:00`）

#### `ErrorResponse` (404/500エラー用)

```python
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="エラーの詳細メッセージ")
    error_code: str | None = Field(None, description="エラーコード（オプション）")
```

**注意:** バリデーションエラー（400）はFastAPIのデフォルト形式を使用します（後述）。

---

## エンドポイント一覧

### 1. ToDoの新規作成

**エンドポイント:** `POST /todos`

**概要:** 新しいToDoアイテムを作成します。

#### リクエスト

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**

```json
{
  "title": "買い物に行く",
  "description": "牛乳とパンを買う"
}
```

**Pydanticモデル:** `ToDoCreate`

**リクエスト例（descriptionなし）:**
```json
{
  "title": "買い物に行く"
}
```

#### レスポンス

##### 201 Created (成功)

作成されたToDoオブジェクトを返します。

**Body (JSON):**

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

**Pydanticモデル:** `ToDo`

**注意:**
- `created_at`と`updated_at`は作成時に同じ値が設定されます
- `id`は1から開始し、自動的にインクリメントされます
- `completed`と`is_active`はデフォルトで`false`と`true`に設定されます

##### 400 Bad Request (バリデーションエラー)

リクエストボディが不正な場合。FastAPIのデフォルトエラー形式で返却されます。

**Body (JSON) - 例1: titleが未指定:**

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "title"],
      "msg": "Field required",
      "input": {"description": "牛乳とパンを買う"}
    }
  ]
}
```

**Body (JSON) - 例2: titleが空白文字のみ:**

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "title"],
      "msg": "Value error, Title must not be whitespace only",
      "input": "   "
    }
  ]
}
```

**Body (JSON) - 例3: descriptionが空文字列:**

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "description"],
      "msg": "Value error, Description must be null, not empty string",
      "input": ""
    }
  ]
}
```

**Body (JSON) - 例4: 複数のエラー:**

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": ""
    },
    {
      "type": "string_too_long",
      "loc": ["body", "description"],
      "msg": "String should have at most 1000 characters",
      "input": "a very long string..."
    }
  ]
}
```

**形式:** FastAPIデフォルト形式（`detail`は配列）

##### 500 Internal Server Error (サーバーエラー)

サーバー側で予期しないエラーが発生した場合。

**Body (JSON):**

```json
{
  "detail": "Internal server error occurred",
  "error_code": "INTERNAL_ERROR"
}
```

**Pydanticモデル:** `ErrorResponse`

---

### 2. ToDoの全件取得

**エンドポイント:** `GET /todos`

**概要:** すべての有効なToDoアイテムを取得します（論理削除されたものは除外）。

#### リクエスト

パラメータなし。

#### レスポンス

##### 200 OK (成功)

ToDoのリストを**ID昇順**で返します。

**Body (JSON):**

```json
[
  {
    "id": 1,
    "title": "買い物に行く",
    "description": "牛乳とパンを買う",
    "completed": false,
    "is_active": true,
    "created_at": "2025-10-30T10:30:00+09:00",
    "updated_at": "2025-10-30T10:30:00+09:00"
  },
  {
    "id": 2,
    "title": "レポート作成",
    "description": null,
    "completed": true,
    "is_active": true,
    "created_at": "2025-10-30T09:15:00+09:00",
    "updated_at": "2025-10-30T11:00:00+09:00"
  }
]
```

**Pydanticモデル:** `list[ToDo]`

**注意:**
- **`is_active=True`のToDoのみ**返却されます（論理削除されたものは含まれません）
- リストは**ID昇順**でソートされます
- データが0件の場合は空の配列`[]`を返します

##### 500 Internal Server Error (サーバーエラー)

サーバー側で予期しないエラーが発生した場合。

**Body (JSON):**

```json
{
  "detail": "Internal server error occurred",
  "error_code": "INTERNAL_ERROR"
}
```

**Pydanticモデル:** `ErrorResponse`

---

### 3. ToDoの完了化

**エンドポイント:** `PATCH /todos/{id}/complete`

**概要:** 指定されたIDのToDoを「完了」状態にします。

**べき等性:** このエンドポイントはべき等です。すでに`completed=True`のToDoに対して実行しても、200 OKを返し、`updated_at`は更新されません。

#### リクエスト

**パスパラメータ:**
- `id` (integer, required): 対象となるToDoのID（1以上の正の整数）

**例:**
```
PATCH /todos/1/complete
```

#### レスポンス

##### 200 OK (成功)

更新されたToDoオブジェクトを返します。

**Body (JSON) - 未完了→完了の場合:**

```json
{
  "id": 1,
  "title": "買い物に行く",
  "description": "牛乳とパンを買う",
  "completed": true,
  "is_active": true,
  "created_at": "2025-10-30T10:30:00+09:00",
  "updated_at": "2025-10-30T11:30:00+09:00"
}
```

**Body (JSON) - すでに完了済みの場合（べき等）:**

```json
{
  "id": 1,
  "title": "買い物に行く",
  "description": "牛乳とパンを買う",
  "completed": true,
  "is_active": true,
  "created_at": "2025-10-30T10:30:00+09:00",
  "updated_at": "2025-10-30T11:30:00+09:00"
}
```

**注意:**
- `completed=False`から`True`に変更された場合、`updated_at`が更新されます
- すでに`completed=True`の場合、**データは変更されず、`updated_at`も更新されません**（べき等）

**Pydanticモデル:** `ToDo`

##### 400 Bad Request (パスパラメータが不正)

パスパラメータ`id`が不正な形式の場合（例: 文字列、負の数、0など）。

**Body (JSON) - 例1: IDが文字列:**

```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["path", "id"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "abc"
    }
  ]
}
```

**Body (JSON) - 例2: IDが負の数:**

```json
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": ["path", "id"],
      "msg": "Input should be greater than or equal to 1",
      "input": "-1"
    }
  ]
}
```

**形式:** FastAPIデフォルト形式（`detail`は配列）

##### 404 Not Found (ToDoが存在しない、または論理削除済み)

指定されたIDのToDoが存在しない、または`is_active=False`（論理削除済み）の場合。

**Body (JSON):**

```json
{
  "detail": "ToDo with id 999 not found",
  "error_code": "TODO_NOT_FOUND"
}
```

**Pydanticモデル:** `ErrorResponse`

**注意:**
- 存在しないIDと論理削除済みのIDは同じエラーメッセージで返されます（セキュリティ上の理由）

##### 500 Internal Server Error (サーバーエラー)

サーバー側で予期しないエラーが発生した場合。

**Body (JSON):**

```json
{
  "detail": "Internal server error occurred",
  "error_code": "INTERNAL_ERROR"
}
```

**Pydanticモデル:** `ErrorResponse`

---

### 4. ToDoの削除（論理削除）

**エンドポイント:** `DELETE /todos/{id}`

**概要:** 指定されたIDのToDoを論理削除します（`is_active`を`False`に変更）。

**べき等性:** このエンドポイントはべき等ではありません。すでに`is_active=False`（論理削除済み）のToDoに対して実行すると、404 Not Foundを返します。

#### リクエスト

**パスパラメータ:**
- `id` (integer, required): 削除対象となるToDoのID（1以上の正の整数）

**例:**
```
DELETE /todos/1
```

#### レスポンス

##### 200 OK (成功)

ToDoが正常に削除されました。レスポンスボディには削除されたToDoオブジェクトを返します。

**Body (JSON) - 有効→削除の場合:**

```json
{
  "id": 1,
  "title": "買い物に行く",
  "description": "牛乳とパンを買う",
  "completed": false,
  "is_active": false,
  "created_at": "2025-10-30T10:30:00+09:00",
  "updated_at": "2025-10-30T12:00:00+09:00"
}
```

**注意:**
- `is_active=True`から`False`に変更された場合、`updated_at`が更新されます
- **ステータスコードは204ではなく200 OKを返します**（レスポンスボディあり）

**Pydanticモデル:** `ToDo`

##### 400 Bad Request (パスパラメータが不正)

パスパラメータ`id`が不正な形式の場合（例: 文字列、負の数、0など）。

**Body (JSON) - 例1: IDが文字列:**

```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["path", "id"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "abc"
    }
  ]
}
```

**Body (JSON) - 例2: IDが負の数:**

```json
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": ["path", "id"],
      "msg": "Input should be greater than or equal to 1",
      "input": "-1"
    }
  ]
}
```

**形式:** FastAPIデフォルト形式（`detail`は配列）

##### 404 Not Found (ToDoが存在しない、または論理削除済み)

指定されたIDのToDoが存在しない、または`is_active=False`（論理削除済み）の場合。

**Body (JSON):**

```json
{
  "detail": "ToDo with id 999 not found",
  "error_code": "TODO_NOT_FOUND"
}
```

**Pydanticモデル:** `ErrorResponse`

**注意:**
- 存在しないIDと論理削除済みのIDは同じエラーメッセージで返されます（セキュリティ上の理由）

##### 500 Internal Server Error (サーバーエラー)

サーバー側で予期しないエラーが発生した場合。

**Body (JSON):**

```json
{
  "detail": "Internal server error occurred",
  "error_code": "INTERNAL_ERROR"
}
```

**Pydanticモデル:** `ErrorResponse`

---

## HTTPステータスコード一覧

| ステータスコード | 説明 | 使用エンドポイント |
|---|---|---|
| 200 OK | リクエストが成功し、レスポンスボディにデータが含まれる | GET /todos, PATCH /todos/{id}/complete, DELETE /todos/{id} |
| 201 Created | リソースが正常に作成された | POST /todos |
| 400 Bad Request | リクエストのバリデーションエラー、またはパスパラメータが不正 | POST /todos, PATCH /todos/{id}/complete, DELETE /todos/{id} |
| 404 Not Found | 指定されたリソースが存在しない、または論理削除済み | PATCH /todos/{id}/complete, DELETE /todos/{id} |
| 500 Internal Server Error | サーバー内部エラー | すべてのエンドポイント |

---

## エラーハンドリング

### バリデーションエラー（400）

バリデーションエラーは**FastAPIのデフォルト形式**で返されます。

**形式:**
```json
{
  "detail": [
    {
      "type": "エラータイプ",
      "loc": ["エラー箇所"],
      "msg": "エラーメッセージ",
      "input": "入力値"
    }
  ]
}
```

**主なエラータイプ:**
- `missing`: 必須フィールドが未指定
- `value_error`: カスタムバリデーションエラー（空白文字のみ、空文字列など）
- `string_too_short`: 文字列が短すぎる
- `string_too_long`: 文字列が長すぎる
- `int_parsing`: 整数への変換失敗
- `greater_than_equal`: 数値が最小値未満

### 404/500エラー

404と500エラーは**独自の`ErrorResponse`モデル**で返されます。

**形式:**
```json
{
  "detail": "エラーの詳細メッセージ",
  "error_code": "エラーコード（オプション）"
}
```

**主なエラーコード:**
- `TODO_NOT_FOUND`: 指定されたToDoが見つからない、または論理削除済み
- `INTERNAL_ERROR`: サーバー内部エラー

---

## 実装上の注意事項

### 1. データ管理
- **インメモリ管理:** すべてのToDoデータはメモリ上で管理されます。
- **永続化なし:** サーバー再起動時にすべてのデータは失われます。
- **データ構造:** 以下の具体的な実装方法を使用します：

```python
from datetime import datetime, timezone, timedelta
from typing import Optional

# グローバル変数として辞書形式で管理
todos_db: dict[int, dict] = {}

# ToDoデータの構造例:
# {
#     1: {
#         "id": 1,
#         "title": "買い物に行く",
#         "description": "牛乳とパンを買う",
#         "completed": False,
#         "is_active": True,
#         "created_at": datetime(...),
#         "updated_at": datetime(...)
#     },
#     2: { ... }
# }
```

**実装の詳細:**
- **データストレージ:** `dict[int, dict]` 形式で、キーはToDo ID、値はToDoデータの辞書
- **ID検索:** `O(1)`で高速検索が可能
- **全件取得:** `todos_db.values()`で全ToDoを取得し、`is_active=True`でフィルタリング
- **グローバル変数名:** `todos_db` を推奨（他の名前でも可）

### 2. ID生成
- **開始値:** IDは1から開始します。
- **自動インクリメント:** 新規作成時に現在の最大ID+1を付与します。
- **再利用なし:** 論理削除されたToDoのIDは再利用しません。
- **実装例:** `max(todos_db.keys(), default=0) + 1`
- **上限値:** 制限なし（Pythonの`int`型は任意精度整数のため、メモリが許す限り増加可能）

### 3. タイムスタンプ
- **形式:** `YYYY-MM-DDTHH:MM:SS+09:00`（ISO 8601、JST、秒単位精度）
- **生成方法:** `datetime.now(timezone(timedelta(hours=9))).replace(microsecond=0)`
- **シリアライズ:** Pydantic v2のデフォルト動作により、`datetime`オブジェクトは自動的にISO 8601形式の文字列に変換されます。特別な設定は不要です。
- **作成時:** `created_at`と`updated_at`は同じ値
- **更新時:** 実際にデータが変更された場合のみ`updated_at`を更新
- **注意:** 必ずタイムゾーン情報付きの`datetime`オブジェクト（`tzinfo`付き）を使用してください。

### 4. 論理削除
- **フィールド:** `is_active`（boolean）を使用
- **削除処理:** `is_active`を`False`に変更（データは残る）
- **GET時:** `is_active=True`のToDoのみ返却
- **PATCH/DELETE時:** `is_active=False`のToDoは404扱い

### 5. べき等性の実装
- **PATCH /todos/{id}/complete:** `completed=True`の場合は何もせず現在の状態を返す（べき等）
- **DELETE /todos/{id}:** `is_active=False`の場合は404を返す（べき等ではない）

### 6. バリデーション
- **title:** `v.strip() == ""`の場合はValueErrorを送出
- **description:** `v == ""`の場合はValueErrorを送出（`None`と`null`は許可）
- **パスパラメータ:** `Path(..., ge=1)`で1以上を強制

### 7. 並行処理
- **単一プロセス想定:** 本仕様では並行アクセスの考慮は不要です。
- **ロック不要:** インメモリ操作のみのため、ロック機構は実装しません。

### 8. ソート
- **GET /todos:** 返却時に`sorted(todos, key=lambda x: x.id)`でID昇順にソート

---

## OpenAPI仕様（参考）

FastAPIは自動的にOpenAPI仕様を生成します。以下のエンドポイントで確認可能です：

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

---

## バージョン履歴

| バージョン | 日付 | 変更内容 |
|---|---|---|
| 1.0.0 | 2025-10-30 | 初版リリース |

---

## 補足

この仕様書はAI仕様書駆動開発（SDD）のワークフローに基づいて作成されており、今後のクライアントアプリ開発の基盤となることを目的としています。
