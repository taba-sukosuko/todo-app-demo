"""
Pydanticモデルとカスタム例外の定義

このモジュールは、ToDo APIで使用するすべてのデータモデルと
カスタム例外クラスを定義します。
"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ToDoCreate(BaseModel):
    """ToDo作成リクエストモデル"""

    title: str = Field(..., min_length=1, max_length=200, description="ToDoのタイトル")
    description: str | None = Field(None, max_length=1000, description="ToDoの詳細説明（オプション）")

    @field_validator('title')
    @classmethod
    def title_must_not_be_whitespace_only(cls, v: str) -> str:
        """タイトルが空白文字のみでないことを検証"""
        if v.strip() == "":
            raise ValueError('Title must not be whitespace only')
        return v

    @field_validator('description')
    @classmethod
    def description_must_not_be_empty_string(cls, v: str | None) -> str | None:
        """説明が空文字列でないことを検証（Noneは許可）"""
        if v == "":
            raise ValueError('Description must be null, not empty string')
        return v


class ToDo(BaseModel):
    """ToDoレスポンスモデル"""

    id: int = Field(..., description="ToDoの一意なID（1から開始）", ge=1)
    title: str = Field(..., description="ToDoのタイトル")
    description: str | None = Field(None, description="ToDoの詳細説明")
    completed: bool = Field(default=False, description="完了状態（True: 完了、False: 未完了）")
    is_active: bool = Field(default=True, description="有効状態（True: 有効、False: 論理削除済み）")
    created_at: datetime = Field(..., description="作成日時（ISO 8601形式、秒単位精度、JST）")
    updated_at: datetime = Field(..., description="更新日時（ISO 8601形式、秒単位精度、JST）")


class ErrorResponse(BaseModel):
    """エラーレスポンスモデル（404/500エラー用）"""

    detail: str = Field(..., description="エラーの詳細メッセージ")
    error_code: str | None = Field(None, description="エラーコード（オプション）")


class ToDoNotFoundException(Exception):
    """ToDo未発見カスタム例外

    指定されたIDのToDoが存在しない、または論理削除済みの場合に送出されます。
    """

    def __init__(self, todo_id: int):
        self.todo_id = todo_id
        super().__init__(f"ToDo with id {todo_id} not found")