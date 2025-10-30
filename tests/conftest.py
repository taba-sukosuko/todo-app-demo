"""
pytestの共通設定とフィクスチャ

このモジュールは、テスト全体で使用されるフィクスチャを提供します。
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import clear_database


@pytest.fixture
def client():
    """
    FastAPI TestClientのフィクスチャ

    各テスト実行前にデータベースをクリアし、
    クリーンな状態でテストを実行できるようにします。

    Returns:
        TestClient: FastAPIのテストクライアント
    """
    # データベースをクリア
    clear_database()

    # TestClientを返す
    return TestClient(app)
