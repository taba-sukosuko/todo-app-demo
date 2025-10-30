"""
インメモリデータストアの管理

このモジュールは、ToDoデータをメモリ上で管理するための
グローバル変数と操作関数を提供します。
"""

from typing import Optional


# グローバル変数：ToDoデータベース（辞書形式）
# キー: ToDo ID（int）、値: ToDoデータ（dict）
todos_db: dict[int, dict] = {}

# グローバル変数：次に割り当てるID
next_id: int = 1


def get_all_active_todos() -> list[dict]:
    """
    有効なすべてのToDoを取得（is_active=True のみ）

    Returns:
        list[dict]: 有効なToDoのリスト（ID昇順）
    """
    active_todos = [todo for todo in todos_db.values() if todo.get("is_active", False)]
    # ID昇順でソート
    return sorted(active_todos, key=lambda x: x["id"])


def get_todo_by_id(todo_id: int) -> Optional[dict]:
    """
    指定されたIDのToDoを取得

    Args:
        todo_id (int): ToDo ID

    Returns:
        Optional[dict]: 指定されたIDのToDoデータ、または None（存在しない場合）
    """
    return todos_db.get(todo_id)


def create_todo(todo_data: dict) -> dict:
    """
    新しいToDoを作成

    Args:
        todo_data (dict): ToDoデータ（id, created_at, updated_at は自動設定）

    Returns:
        dict: 作成されたToDoデータ
    """
    global next_id

    # 新しいIDを割り当て
    todo_data["id"] = next_id
    next_id += 1

    # データベースに保存
    todos_db[todo_data["id"]] = todo_data

    return todo_data


def update_todo(todo_id: int, updates: dict) -> Optional[dict]:
    """
    指定されたIDのToDoを更新

    Args:
        todo_id (int): ToDo ID
        updates (dict): 更新するフィールドと値

    Returns:
        Optional[dict]: 更新後のToDoデータ、または None（存在しない場合）
    """
    todo = todos_db.get(todo_id)
    if todo is None:
        return None

    # 更新を適用
    todo.update(updates)

    return todo


def clear_database() -> None:
    """
    データベースを初期化（テスト用）

    すべてのToDoデータを削除し、next_idを1にリセットします。
    """
    global next_id
    todos_db.clear()
    next_id = 1