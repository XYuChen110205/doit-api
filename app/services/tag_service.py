"""标签业务逻辑"""
from app.database import database, tags


async def list_tags(user_id: int) -> list[dict]:
    """G1: 获取所有标签"""
    query = tags.select().where(tags.c.user_id == user_id).order_by(tags.c.id)
    rows = await database.fetch_all(query)
    return [dict(r._mapping) for r in rows]


async def create_tag(user_id: int, name: str, color: str = "#7BAFCC") -> dict:
    """G2: 创建标签"""
    # 检查是否已存在
    existing = await database.fetch_one(
        tags.select().where(tags.c.user_id == user_id, tags.c.name == name)
    )
    if existing:
        return dict(existing._mapping)
    
    query = tags.insert().values(user_id=user_id, name=name, color=color)
    last_id = await database.execute(query)
    return await get_tag_by_id(last_id)


async def get_tag_by_id(tag_id: int) -> dict | None:
    """根据ID获取标签"""
    query = tags.select().where(tags.c.id == tag_id)
    row = await database.fetch_one(query)
    return dict(row._mapping) if row else None


async def delete_tag(tag_id: int) -> bool:
    """G3: 删除标签"""
    existing = await get_tag_by_id(tag_id)
    if not existing:
        return False
    
    # 删除关联的 task_tags 记录
    from app.database import task_tags
    await database.execute(
        task_tags.delete().where(task_tags.c.tag_id == tag_id)
    )
    
    # 删除标签
    query = tags.delete().where(tags.c.id == tag_id)
    await database.execute(query)
    return True
