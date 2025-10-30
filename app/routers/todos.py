"""
ToDoエンドポイントの実装

このモジュールは、ToDoに関するすべてのCRUD操作のエンドポイントを提供します。
"""

from typing import Annotated

from fastapi import APIRouter, Path, status

from app.models import ToDoCreate, ToDo, ToDoNotFoundException
from app.database import (
    get_all_active_todos,
    get_todo_by_id,
    create_todo,
    update_todo,
)
from app.utils.datetime_utils import get_current_jst_time


# APIRouterの作成
router = APIRouter(
    prefix="/todos",
    tags=["ToDos"],
)


@router.post("", response_model=ToDo, status_code=status.HTTP_201_CREATED)
async def create_new_todo(todo_create: ToDoCreate) -> ToDo:
    """
    ToDoの新規作成

    新しいToDoアイテムを作成します。

    Args:
        todo_create (ToDoCreate): 作成するToDoの情報

    Returns:
        ToDo: 作成されたToDoオブジェクト

    Raises:
        400 Bad Request: リクエストボディが不正な場合
        500 Internal Server Error: サーバー内部エラー
    """
    # 現在のタイムスタンプを取得
    now = get_current_jst_time()

    # ToDoデータを構築
    todo_data = {
        "title": todo_create.title,
        "description": todo_create.description,
        "completed": False,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }

    # データベースに保存（IDは自動割り当て）
    created_todo = create_todo(todo_data)

    return ToDo(**created_todo)


@router.get("", response_model=list[ToDo])
async def get_all_todos() -> list[ToDo]:
    """
    ToDoの全件取得

    すべての有効なToDoアイテムを取得します（論理削除されたものは除外）。

    Returns:
        list[ToDo]: ToDoのリスト（ID昇順）

    Raises:
        500 Internal Server Error: サーバー内部エラー
    """
    # 有効なすべてのToDoを取得
    active_todos = get_all_active_todos()

    return [ToDo(**todo) for todo in active_todos]


@router.patch("/{id}/complete", response_model=ToDo)
async def complete_todo(
    id: Annotated[int, Path(ge=1, description="対象となるToDoのID")]
) -> ToDo:
    """
    ToDoの完了化

    指定されたIDのToDoを「完了」状態にします。
    このエンドポイントはべき等です（既に完了済みの場合、データは変更されません）。

    Args:
        id (int): 対象となるToDoのID（1以上）

    Returns:
        ToDo: 更新されたToDoオブジェクト

    Raises:
        400 Bad Request: パスパラメータが不正な場合
        404 Not Found: 指定されたIDのToDoが存在しない、または論理削除済み
        500 Internal Server Error: サーバー内部エラー
    """
    # ToDoを取得
    todo = get_todo_by_id(id)

    # 存在確認とis_activeチェック
    if todo is None or not todo.get("is_active", False):
        raise ToDoNotFoundException(id)

    # 既に完了済みの場合は何もしない（べき等性）
    if todo.get("completed", False):
        return ToDo(**todo)

    # 完了状態に更新
    updates = {
        "completed": True,
        "updated_at": get_current_jst_time(),
    }
    updated_todo = update_todo(id, updates)

    return ToDo(**updated_todo)


@router.delete("/{id}", response_model=ToDo)
async def delete_todo(
    id: Annotated[int, Path(ge=1, description="削除対象となるToDoのID")]
) -> ToDo:
    """
    ToDoの削除（論理削除）

    指定されたIDのToDoを論理削除します（is_activeをFalseに変更）。
    このエンドポイントはべき等ではありません（既に削除済みの場合、404を返します）。

    Args:
        id (int): 削除対象となるToDoのID（1以上）

    Returns:
        ToDo: 削除されたToDoオブジェクト

    Raises:
        400 Bad Request: パスパラメータが不正な場合
        404 Not Found: 指定されたIDのToDoが存在しない、または論理削除済み
        500 Internal Server Error: サーバー内部エラー
    """
    # ToDoを取得
    todo = get_todo_by_id(id)

    # 存在確認とis_activeチェック
    if todo is None or not todo.get("is_active", False):
        raise ToDoNotFoundException(id)

    # 論理削除（is_activeをFalseに変更）
    updates = {
        "is_active": False,
        "updated_at": get_current_jst_time(),
    }
    deleted_todo = update_todo(id, updates)

    return ToDo(**deleted_todo)
