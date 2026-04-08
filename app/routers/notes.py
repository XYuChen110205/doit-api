"""笔记路由"""
from fastapi import APIRouter, Query
from app.response import success, error
from app.services.note_service import get_note_by_date, create_or_update_note

router = APIRouter(prefix="/api/notes", tags=["Notes"])


@router.get("")
async def api_get_note(date: str = Query(..., description="日期 YYYY-MM-DD")):
    """N1: 获取某日笔记"""
    note = await get_note_by_date(date)
    if not note:
        return success(data=None, message="该日期暂无笔记")
    return success(data=note)


@router.put("")
async def api_create_or_update_note(body: dict):
    """N2: 创建或更新笔记"""
    note_date = body.get("note_date")
    content = body.get("content", "")
    
    if not note_date:
        return error(400, "note_date 不能为空")
    
    note = await create_or_update_note(note_date, content)
    return success(data=note, message="笔记已保存")
