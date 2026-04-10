"""任务业务逻辑"""
from datetime import datetime
from app.database import database, tasks
from app.services.task_tag_service import get_task_tags


async def create_task(user_id: int, data: dict) -> dict:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = tasks.insert().values(
        user_id=user_id,
        title=data["title"],
        detail=data.get("detail", ""),
        task_type=data.get("task_type", "todo"),
        status="pending",
        priority=data.get("priority", 0),
        due_date=data.get("due_date"),
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        source=data.get("source", "direct"),
        created_at=now,
    )
    last_id = await database.execute(query)
    task = await get_task_by_id(last_id)
    task["tags"] = []
    return task


async def get_task_by_id(task_id: int) -> dict | None:
    query = tasks.select().where(tasks.c.id == task_id)
    row = await database.fetch_one(query)
    if not row:
        return None
    task = dict(row._mapping)
    task["tags"] = await get_task_tags(task_id)
    return task


async def get_tasks_by_date(user_id: int, date_str: str) -> list[dict]:
    query = tasks.select().where(
        tasks.c.user_id == user_id,
        tasks.c.due_date == date_str
    ).order_by(
        tasks.c.priority.desc(), tasks.c.created_at.asc()
    )
    rows = await database.fetch_all(query)
    tasks_list = [dict(r._mapping) for r in rows]
    # 为每个任务添加标签
    for task in tasks_list:
        task["tags"] = await get_task_tags(task["id"])
    return tasks_list


async def update_task(task_id: int, data: dict) -> dict | None:
    existing = await get_task_by_id(task_id)
    if not existing:
        return None

    update_data = {}
    allowed_fields = ["title", "detail", "task_type", "status", "priority",
                      "due_date", "start_time", "end_time", "archived"]
    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]

    if data.get("status") == "done" and existing["status"] != "done":
        update_data["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if data.get("status") and data["status"] != "done":
        update_data["completed_at"] = None

    if update_data:
        query = tasks.update().where(tasks.c.id == task_id).values(**update_data)
        await database.execute(query)

    return await get_task_by_id(task_id)


async def delete_task(task_id: int) -> bool:
    existing = await get_task_by_id(task_id)
    if not existing:
        return False
    query = tasks.delete().where(tasks.c.id == task_id)
    await database.execute(query)
    return True


async def get_tasks_by_range(user_id: int, start_date: str, end_date: str) -> list[dict]:
    """T5: 按日期范围查询任务"""
    query = tasks.select().where(
        tasks.c.user_id == user_id,
        tasks.c.due_date >= start_date,
        tasks.c.due_date <= end_date
    ).order_by(tasks.c.due_date.asc(), tasks.c.priority.desc())
    rows = await database.fetch_all(query)
    tasks_list = [dict(r._mapping) for r in rows]
    # 为每个任务添加标签
    for task in tasks_list:
        task["tags"] = await get_task_tags(task["id"])
    return tasks_list
