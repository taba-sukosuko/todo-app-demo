"""
GET /todos エンドポイントのテスト
"""


def test_get_todos_empty(client):
    """正常系: データが0件の場合"""
    response = client.get("/todos")

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_todos_multiple_items(client):
    """正常系: データが複数件の場合（ID昇順確認）"""
    # 3つのToDoを作成
    client.post("/todos", json={"title": "ToDo 3"})
    client.post("/todos", json={"title": "ToDo 1"})
    client.post("/todos", json={"title": "ToDo 2"})

    response = client.get("/todos")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    # ID昇順でソートされていることを確認
    assert data[0]["id"] == 1
    assert data[0]["title"] == "ToDo 3"
    assert data[1]["id"] == 2
    assert data[1]["title"] == "ToDo 1"
    assert data[2]["id"] == 3
    assert data[2]["title"] == "ToDo 2"


def test_get_todos_excludes_deleted(client):
    """正常系: 論理削除されたToDoは含まれない"""
    # 3つのToDoを作成
    client.post("/todos", json={"title": "ToDo 1"})
    client.post("/todos", json={"title": "ToDo 2"})
    client.post("/todos", json={"title": "ToDo 3"})

    # 2番目のToDoを削除
    client.delete("/todos/2")

    response = client.get("/todos")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # 削除されたToDoは含まれない
    ids = [todo["id"] for todo in data]
    assert 1 in ids
    assert 2 not in ids
    assert 3 in ids


def test_get_todos_with_completed_and_active(client):
    """正常系: 完了済みToDoも取得される"""
    # 2つのToDoを作成
    client.post("/todos", json={"title": "ToDo 1"})
    client.post("/todos", json={"title": "ToDo 2"})

    # 1番目のToDoを完了
    client.patch("/todos/1/complete")

    response = client.get("/todos")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # 1番目は完了、2番目は未完了
    assert data[0]["id"] == 1
    assert data[0]["completed"] is True
    assert data[1]["id"] == 2
    assert data[1]["completed"] is False
