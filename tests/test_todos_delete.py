"""
DELETE /todos/{id} エンドポイントのテスト
"""


def test_delete_todo_success(client):
    """正常系: 有効なToDoの削除"""
    # ToDoを作成
    response = client.post("/todos", json={"title": "買い物に行く"})
    created_todo = response.json()
    todo_id = created_todo["id"]
    created_at = created_todo["created_at"]

    # ToDoを削除
    response = client.delete(f"/todos/{todo_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["is_active"] is False
    assert data["created_at"] == created_at
    # updated_at が更新されていることを確認（同じ秒の場合もあり得る）
    assert data["updated_at"] >= created_at

    # 削除されたToDoが一覧に含まれないことを確認
    response = client.get("/todos")
    todos = response.json()
    assert len(todos) == 0


def test_delete_todo_not_found(client):
    """異常系: 存在しないID"""
    response = client.delete("/todos/999")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "error_code" in data
    assert data["error_code"] == "TODO_NOT_FOUND"
    assert "999" in data["detail"]


def test_delete_already_deleted_todo(client):
    """異常系: 既に論理削除済みのID"""
    # ToDoを作成して削除
    response = client.post("/todos", json={"title": "買い物に行く"})
    todo_id = response.json()["id"]
    client.delete(f"/todos/{todo_id}")

    # 再度削除しようとする（べき等ではない）
    response = client.delete(f"/todos/{todo_id}")

    assert response.status_code == 404
    data = response.json()
    assert "error_code" in data
    assert data["error_code"] == "TODO_NOT_FOUND"


def test_delete_todo_invalid_id_string(client):
    """異常系: 不正なパスパラメータ（文字列）"""
    response = client.delete("/todos/abc")

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_delete_todo_invalid_id_negative(client):
    """異常系: 不正なパスパラメータ（負の数）"""
    response = client.delete("/todos/-1")

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_delete_todo_invalid_id_zero(client):
    """異常系: 不正なパスパラメータ（0）"""
    response = client.delete("/todos/0")

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_delete_multiple_todos(client):
    """正常系: 複数のToDoを削除"""
    # 3つのToDoを作成
    client.post("/todos", json={"title": "ToDo 1"})
    client.post("/todos", json={"title": "ToDo 2"})
    client.post("/todos", json={"title": "ToDo 3"})

    # 1番目と3番目を削除
    client.delete("/todos/1")
    client.delete("/todos/3")

    # 2番目だけが残っていることを確認
    response = client.get("/todos")
    todos = response.json()
    assert len(todos) == 1
    assert todos[0]["id"] == 2
    assert todos[0]["title"] == "ToDo 2"
