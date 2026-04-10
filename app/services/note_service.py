"""笔记业务逻辑"""
from datetime import datetime
from app.database import database, notes


async def get_note_by_date(user_id: int, note_date: str) -> dict | None:
    """根据日期获取笔记"""
    query = notes.select().where(
        notes.c.user_id == user_id,
        notes.c.note_date == note_date
    )
    row = await database.fetch_one(query)
    return dict(row._mapping) if row else None


async def get_notes_list(user_id: int, limit: int = 100) -> list[dict]:
    """获取笔记列表"""
    query = notes.select().where(
        notes.c.user_id == user_id
    ).order_by(notes.c.note_date.desc()).limit(limit)
    rows = await database.fetch_all(query)
    return [dict(r._mapping) for r in rows]


async def create_or_update_note(user_id: int, note_date: str, content: str) -> dict:
    """创建或更新笔记"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing = await get_note_by_date(user_id, note_date)
    
    if existing:
        # 更新现有笔记
        query = notes.update().where(
            notes.c.user_id == user_id,
            notes.c.note_date == note_date
        ).values(
            content=content,
            updated_at=now
        )
        await database.execute(query)
    else:
        # 创建新笔记
        query = notes.insert().values(
            user_id=user_id,
            content=content,
            note_date=note_date,
            created_at=now,
            updated_at=now
        )
        await database.execute(query)
    
    return await get_note_by_date(user_id, note_date)


async def delete_note(user_id: int, note_date: str) -> bool:
    """删除笔记"""
    query = notes.delete().where(
        notes.c.user_id == user_id,
        notes.c.note_date == note_date
    )
    result = await database.execute(query)
    return result > 0
