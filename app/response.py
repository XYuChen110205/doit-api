"""
统一返回格式
所有接口都用这个格式返回，前端只需要写一套解析逻辑
"""

from typing import Any


def success(data: Any = None, message: str = "ok") -> dict:
    return {
        "code": 200,
        "message": message,
        "data": data,
    }


def error(code: int = 400, message: str = "请求错误") -> dict:
    return {
        "code": code,
        "message": message,
        "data": None,
    }
