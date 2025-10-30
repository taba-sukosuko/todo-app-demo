"""
POST /todos エンドポイントのテスト
"""

import pytest


def test_create_todo_with_description(client):
    """正常系: タイトルと説明付きでToDoを作成"""
    response = client.post(
        "/todos",
        json={"title": "買い物に行く", "description": "牛乳とパンを買う"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "買い物に行く"
    assert data["description"] == "牛乳とパンを買う"
    assert data["completed"] is False
    assert data["is_active"] is True
    assert "created_at" in data
    assert "updated_at" in data
    assert data["created_at"] == data["updated_at"]


def test_create_todo_without_description(client):
    """正常系: タイトルのみでToDoを作成"""
    response = client.post(
        "/todos",
        json={"title": "買い物に行く"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "買い物に行く"
    assert data["description"] is None
    assert data["completed"] is False
    assert data["is_active"] is True


def test_create_todo_missing_title(client):
    """異常系: タイトル未指定"""
    response = client.post(
        "/todos",
        json={"description": "牛乳とパンを買う"}
    )

    assert response.status_code == 422  # FastAPIのバリデーションエラー
    data = response.json()
    assert "detail" in data


def test_create_todo_title_whitespace_only(client):
    """異常系: タイトルが空白文字のみ"""
    response = client.post(
        "/todos",
        json={"title": "   ", "description": "牛乳とパンを買う"}
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # エラーメッセージに「Title must not be whitespace only」が含まれることを確認
    detail_str = str(data["detail"])
    assert "Title must not be whitespace only" in detail_str


def test_create_todo_title_too_long(client):
    """異常系: タイトルが201文字以上"""
    long_title = "a" * 201
    response = client.post(
        "/todos",
        json={"title": long_title}
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_create_todo_description_empty_string(client):
    """異常系: 説明が空文字列"""
    response = client.post(
        "/todos",
        json={"title": "買い物に行く", "description": ""}
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # エラーメッセージに「Description must be null, not empty string」が含まれることを確認
    detail_str = str(data["detail"])
    assert "Description must be null, not empty string" in detail_str


def test_create_todo_description_too_long(client):
    """異常系: 説明が1001文字以上"""
    long_description = "a" * 1001
    response = client.post(
        "/todos",
        json={"title": "買い物に行く", "description": long_description}
    )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_create_multiple_todos(client):
    """正常系: 複数のToDoを作成してIDが自動インクリメントされることを確認"""
    # 1つ目のToDo
    response1 = client.post(
        "/todos",
        json={"title": "ToDo 1"}
    )
    assert response1.status_code == 201
    assert response1.json()["id"] == 1

    # 2つ目のToDo
    response2 = client.post(
        "/todos",
        json={"title": "ToDo 2"}
    )
    assert response2.status_code == 201
    assert response2.json()["id"] == 2

    # 3つ目のToDo
    response3 = client.post(
        "/todos",
        json={"title": "ToDo 3"}
    )
    assert response3.status_code == 201
    assert response3.json()["id"] == 3
