"""任务标签关联业务逻辑"""
from app.database import database, task_tags, tags


async def get_task_tags(task_id: int) -> list[dict]:
    """获取任务的所有标签"""
    query = task_tags.join(tags, task_tags.c.tag_id == tags.c.id).select().where(
        task_tags.c.task_id == task_id
    )
    rows = await database.fetch_all(query)
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "color": row["color"]
        }
        for row in rows
    ]


async def add_tag_to_task(task_id: int, tag_id: int) -> bool:
    """给任务添加标签"""
    # 检查是否已关联
    existing = await database.fetch_one(
        task_tags.select().where(
            task_tags.c.task_id == task_id,
            task_tags.c.tag_id == tag_id
        )
    )
    if existing:
        return True
    
    query = task_tags.insert().values(task_id=task_id, tag_id=tag_id)
    await database.execute(query)
    return True


async def remove_tag_from_task(task_id: int, tag_id: int) -> bool:
    """移除任务的标签"""
    query = task_tags.delete().where(
        task_tags.c.task_id == task_id,
        task_tags.c.tag_id == tag_id
    )
    result = await database.execute(query)
    return result > 0


async def get_tasks_with_tags(task_list: list[dict]) -> list[dict]:
    """为任务列表添加标签信息"""
    for task in task_list:
        task["tags"] = await get_task_tags(task["id"])
    return task_list
