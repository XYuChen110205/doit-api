"""标签路由"""
from fastapi import APIRouter, Depends
from app.response import success, error
from app.services.tag_service import list_tags, create_tag, delete_tag
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/tags", tags=["Tags"])


@router.get("")
async def api_list_tags(current_user: User = Depends(get_current_user)):
    """G1: 获取所有标签"""
    tags_list = await list_tags(current_user.id)
    return success(data=tags_list)


@router.post("")
async def api_create_tag(
    body: dict,
    current_user: User = Depends(get_current_user)
):
    """G2: 创建标签"""
    name = body.get("name", "").strip()
    if not name:
        return error(400, "标签名称不能为空")
    
    color = body.get("color", "#7BAFCC")
    tag = await create_tag(current_user.id, name, color)
    return success(data=tag, message="标签已创建")


@router.delete("/{tag_id}")
async def api_delete_tag(tag_id: int):
    """G3: 删除标签"""
    deleted = await delete_tag(tag_id)
    if not deleted:
        return error(404, "标签不存在")
    return success(message="标签已删除")
