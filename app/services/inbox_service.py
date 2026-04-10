"""收集箱业务逻辑"""
from datetime import datetime
from app.database import database, inbox, tasks


async def create_inbox(user_id: int, content: str) -> dict:
    """I1: 快速添加到收集箱"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = inbox.insert().values(
        user_id=user_id,
        content=content,
        created_at=now
    )
    last_id = await database.execute(query)
    return await get_inbox_by_id(last_id)


async def get_inbox_by_id(inbox_id: int) -> dict | None:
    """根据ID获取收集箱条目"""
    query = inbox.select().where(inbox.c.id == inbox_id)
    row = await database.fetch_one(query)
    return dict(row._mapping) if row else None


async def list_inbox(user_id: int) -> list[dict]:
    """I2: 列出全部收集箱条目，按创建时间倒序"""
    query = inbox.select().where(inbox.c.user_id == user_id).order_by(inbox.c.created_at.desc())
    rows = await database.fetch_all(query)
    return [dict(r._mapping) for r in rows]


async def convert_inbox_to_task(user_id: int, inbox_id: int) -> dict | None:
    """I3: 将收集箱条目转为任务（事务性操作）"""
    # 读取 inbox 条目
    inbox_item = await get_inbox_by_id(inbox_id)
    if not inbox_item:
        return None
    
    # 使用 inbox 内容作为 title 创建任务
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 创建任务，due_date 设为今天
    today = datetime.now().strftime("%Y-%m-%d")
    task_query = tasks.insert().values(
        user_id=user_id,
        title=inbox_item["content"],
        detail="",
        task_type="todo",
        status="pending",
        priority=0,
        due_date=today,
        start_time=None,
        end_time=None,
        source="inbox",
        created_at=now,
    )
    task_id = await database.execute(task_query)
    
    # 删除 inbox 条目
    delete_query = inbox.delete().where(inbox.c.id == inbox_id)
    await database.execute(delete_query)
    
    # 返回创建的任务
    task_query = tasks.select().where(tasks.c.id == task_id)
    row = await database.fetch_one(task_query)
    return dict(row._mapping) if row else None


async def delete_inbox(inbox_id: int) -> bool:
    """I4: 删除收集箱条目"""
    existing = await get_inbox_by_id(inbox_id)
    if not existing:
        return False
    query = inbox.delete().where(inbox.c.id == inbox_id)
    await database.execute(query)
    return True
