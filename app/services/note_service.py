"""笔记业务逻辑"""
from datetime import datetime
from app.database import database, notes


async def get_note_by_date(note_date: str) -> dict | None:
    """根据日期获取笔记"""
    query = notes.select().where(notes.c.note_date == note_date)
    row = await database.fetch_one(query)
    return dict(row._mapping) if row else None


async def create_or_update_note(note_date: str, content: str) -> dict:
    """创建或更新笔记"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing = await get_note_by_date(note_date)
    
    if existing:
        # 更新现有笔记
        query = notes.update().where(notes.c.note_date == note_date).values(
            content=content,
            updated_at=now
        )
        await database.execute(query)
    else:
        # 创建新笔记
        query = notes.insert().values(
            content=content,
            note_date=note_date,
            created_at=now,
            updated_at=now
        )
        await database.execute(query)
    
    return await get_note_by_date(note_date)
