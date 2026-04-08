"""任务标签关联路由"""
from fastapi import APIRouter
from app.response import success, error
from app.services.task_tag_service import (
    get_task_tags, add_tag_to_task, remove_tag_from_task
)

router = APIRouter(prefix="/api/tasks", tags=["TaskTags"])


@router.get("/{task_id}/tags")
async def api_get_task_tags(task_id: int):
    """获取任务的所有标签"""
    tags_list = await get_task_tags(task_id)
    return success(data=tags_list)


@router.post("/{task_id}/tags")
async def api_add_tag_to_task(task_id: int, body: dict):
    """给任务添加标签"""
    tag_id = body.get("tag_id")
    if not tag_id:
        return error(400, "tag_id 不能为空")
    
    await add_tag_to_task(task_id, tag_id)
    return success(message="标签已添加")


@router.delete("/{task_id}/tags/{tag_id}")
async def api_remove_tag_from_task(task_id: int, tag_id: int):
    """移除任务的标签"""
    removed = await remove_tag_from_task(task_id, tag_id)
    if not removed:
        return error(404, "标签关联不存在")
    return success(message="标签已移除")
