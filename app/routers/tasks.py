"""任务路由"""
from fastapi import APIRouter, Query, Depends
from app.response import success, error
from app.services.task_service import (
    create_task, get_tasks_by_date, update_task, delete_task, get_tasks_by_range
)
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.post("")
async def api_create_task(
    body: dict,
    current_user: User = Depends(get_current_user)
):
    if not body.get("title"):
        return error(400, "title 不能为空")
    task = await create_task(current_user.id, body)
    return success(data=task, message="任务已创建")


@router.get("")
async def api_get_tasks(
    date: str = Query(None, description="日期 YYYY-MM-DD"),
    start_date: str = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期 YYYY-MM-DD"),
    current_user: User = Depends(get_current_user)
):
    if date:
        tasks_list = await get_tasks_by_date(current_user.id, date)
    elif start_date and end_date:
        tasks_list = await get_tasks_by_range(current_user.id, start_date, end_date)
    else:
        return error(400, "请提供 date 或 start_date+end_date 参数")
    return success(data=tasks_list)


@router.patch("/{task_id}")
async def api_update_task(task_id: int, body: dict):
    task = await update_task(task_id, body)
    if not task:
        return error(404, "任务不存在")
    return success(data=task, message="任务已更新")


@router.delete("/{task_id}")
async def api_delete_task(task_id: int):
    deleted = await delete_task(task_id)
    if not deleted:
        return error(404, "任务不存在")
    return success(message="任务已删除")
