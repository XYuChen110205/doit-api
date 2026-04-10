"""笔记路由"""
from fastapi import APIRouter, Query, Depends
from app.response import success, error
from app.services.note_service import get_note_by_date, get_notes_list, create_or_update_note, delete_note
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/notes", tags=["Notes"])


@router.get("")
async def api_get_note(
    date: str = Query(..., description="日期 YYYY-MM-DD"),
    current_user: User = Depends(get_current_user)
):
    """N1: 获取某日笔记"""
    note = await get_note_by_date(current_user.id, date)
    if not note:
        return success(data=None, message="该日期暂无笔记")
    return success(data=note)


@router.get("/list")
async def api_get_notes_list(
    limit: int = Query(100, description="返回数量限制"),
    current_user: User = Depends(get_current_user)
):
    """N3: 获取笔记列表"""
    notes = await get_notes_list(current_user.id, limit)
    return success(data=notes)


@router.put("")
async def api_create_or_update_note(
    body: dict,
    current_user: User = Depends(get_current_user)
):
    """N2: 创建或更新笔记"""
    note_date = body.get("note_date")
    content = body.get("content", "")
    
    if not note_date:
        return error(400, "note_date 不能为空")
    
    note = await create_or_update_note(current_user.id, note_date, content)
    return success(data=note, message="笔记已保存")


@router.delete("")
async def api_delete_note(
    date: str = Query(..., description="日期 YYYY-MM-DD"),
    current_user: User = Depends(get_current_user)
):
    """N4: 删除笔记"""
    deleted = await delete_note(current_user.id, date)
    if not deleted:
        return error(404, "笔记不存在")
    return success(message="笔记已删除")
