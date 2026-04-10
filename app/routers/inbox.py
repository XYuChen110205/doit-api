"""收集箱路由"""
from fastapi import APIRouter, Depends
from app.response import success, error
from app.services.inbox_service import (
    create_inbox, list_inbox, convert_inbox_to_task, delete_inbox
)
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/inbox", tags=["Inbox"])


@router.post("")
async def api_create_inbox(
    body: dict,
    current_user: User = Depends(get_current_user)
):
    """I1: 快速添加到收集箱"""
    content = body.get("content", "").strip()
    if not content:
        return error(400, "content 不能为空")
    
    item = await create_inbox(current_user.id, content)
    return success(data=item, message="已添加到收集箱")


@router.get("")
async def api_list_inbox(current_user: User = Depends(get_current_user)):
    """I2: 列出全部收集箱条目，按创建时间倒序"""
    items = await list_inbox(current_user.id)
    return success(data=items)


@router.post("/{inbox_id}/convert")
async def api_convert_inbox(
    inbox_id: int,
    current_user: User = Depends(get_current_user)
):
    """I3: 将收集箱条目转为任务"""
    task = await convert_inbox_to_task(current_user.id, inbox_id)
    if not task:
        return error(404, "收集箱条目不存在")
    return success(data=task, message="已转为任务")


@router.delete("/{inbox_id}")
async def api_delete_inbox(inbox_id: int):
    """I4: 删除收集箱条目"""
    deleted = await delete_inbox(inbox_id)
    if not deleted:
        return error(404, "收集箱条目不存在")
    return success(message="已删除")
