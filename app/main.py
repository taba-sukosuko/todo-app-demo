"""
FastAPIアプリケーションのエントリーポイント

このモジュールは、FastAPIアプリケーションを初期化し、
ルーターの登録とエラーハンドラの設定を行います。
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.models import ToDoNotFoundException
from app.routers import todos


# FastAPIアプリケーションの作成
app = FastAPI(
    title="ToDo API",
    version="1.0.0",
    description="簡易ToDo管理のためのREST API（インメモリ実装）",
)


# ToDoルーターの登録
app.include_router(todos.router)


# カスタム例外ハンドラ：ToDoNotFoundException（404）
@app.exception_handler(ToDoNotFoundException)
async def todo_not_found_handler(request: Request, exc: ToDoNotFoundException) -> JSONResponse:
    """
    ToDoが見つからない場合のエラーハンドラ

    Args:
        request (Request): HTTPリクエスト
        exc (ToDoNotFoundException): カスタム例外

    Returns:
        JSONResponse: 404エラーレスポンス
    """
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "error_code": "TODO_NOT_FOUND"
        }
    )


# 汎用例外ハンドラ：すべての予期しない例外（500）
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    すべての予期しないエラーのハンドラ

    Args:
        request (Request): HTTPリクエスト
        exc (Exception): 例外

    Returns:
        JSONResponse: 500エラーレスポンス
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error occurred",
            "error_code": "INTERNAL_ERROR"
        }
    )


# ヘルスチェックエンドポイント
@app.get("/", tags=["Health"])
async def health_check():
    """
    APIヘルスチェック

    Returns:
        dict: ステータスメッセージ
    """
    return {
        "status": "ok",
        "message": "ToDo API is running"
    }
