"""
PATCH /todos/{id}/complete エンドポイントのテスト
"""


def test_complete_todo_success(client):
    """正常系: 未完了→完了への変更"""
    # ToDoを作成
    response = client.post("/todos", json={"title": "買い物に行く"})
    created_todo = response.json()
    created_at = created_todo["created_at"]
    updated_at = created_todo["updated_at"]

    # ToDoを完了
    response = client.patch(f"/todos/{created_todo['id']}/complete")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_todo["id"]
    assert data["completed"] is True
    assert data["is_active"] is True
    assert data["created_at"] == created_at
    # updated_at が更新されていることを確認（同じ秒の場合もあり得る）
    assert data["updated_at"] >= updated_at


def test_complete_todo_idempotent(client):
    """正常系: 既に完了済み（べき等性確認）"""
    # ToDoを作成して完了
    response = client.post("/todos", json={"title": "買い物に行く"})
    todo_id = response.json()["id"]
    client.patch(f"/todos/{todo_id}/complete")

    # 完了済みToDoの状態を取得
    response = client.get("/todos")
    completed_todo = [todo for todo in response.json() if todo["id"] == todo_id][0]
    updated_at_after_first_complete = completed_todo["updated_at"]

    # 再度完了化を試みる（べき等性のテスト）
    response = client.patch(f"/todos/{todo_id}/complete")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["completed"] is True
    # updated_at が更新されていないことを確認（べき等）
    assert data["updated_at"] == updated_at_after_first_complete


def test_complete_todo_not_found(client):
    """異常系: 存在しないID"""
    response = client.patch("/todos/999/complete")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "error_code" in data
    assert data["error_code"] == "TODO_NOT_FOUND"
    assert "999" in data["detail"]


def test_complete_deleted_todo(client):
    """異常系: 論理削除済みのID"""
    # ToDoを作成して削除
    response = client.post("/todos", json={"title": "買い物に行く"})
    todo_id = response.json()["id"]
    client.delete(f"/todos/{todo_id}")

    # 削除済みToDoを完了化しようとする
    response = client.patch(f"/todos/{todo_id}/complete")

    assert response.status_code == 404
    data = response.json()
    assert "error_code" in data
    assert data["error_code"] == "TODO_NOT_FOUND"


def test_complete_todo_invalid_id_string(client):
    """異常系: 不正なパスパラメータ（文字列）"""
    response = client.patch("/todos/abc/complete")

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_complete_todo_invalid_id_negative(client):
    """異常系: 不正なパスパラメータ（負の数）"""
    response = client.patch("/todos/-1/complete")

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_complete_todo_invalid_id_zero(client):
    """異常系: 不正なパスパラメータ（0）"""
    response = client.patch("/todos/0/complete")

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
