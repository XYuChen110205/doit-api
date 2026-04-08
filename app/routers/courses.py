"""课程表 API 路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.database import database, courses, schedule_settings
from app.response import success, error

router = APIRouter(prefix="/api/courses", tags=["courses"])


class CourseCreate(BaseModel):
    name: str
    code: str = ""
    hours: int = 48
    day: str
    period: int
    weeks: str = "1-17周"
    room: str = ""
    teacher: str = ""
    target: str = ""
    color: str = "#E3F2FD"
    term: str = "2024-2025-1"


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    hours: Optional[int] = None
    day: Optional[str] = None
    period: Optional[int] = None
    weeks: Optional[str] = None
    room: Optional[str] = None
    teacher: Optional[str] = None
    target: Optional[str] = None
    color: Optional[str] = None
    term: Optional[str] = None


class ScheduleSettings(BaseModel):
    background: str = ""
    background_opacity: float = 0.15
    table_opacity: float = 0.95
    bg_position_x: float = 50
    bg_position_y: float = 50
    bg_scale: int = 100
    notification_enabled: bool = False


@router.get("")
async def get_courses(term: Optional[str] = None):
    """获取课程列表"""
    query = courses.select()
    if term:
        query = query.where(courses.c.term == term)
    rows = await database.fetch_all(query)
    return success(data=[dict(row) for row in rows])


@router.post("")
async def create_course(course: CourseCreate):
    """创建课程"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = courses.insert().values(
        name=course.name,
        code=course.code,
        hours=course.hours,
        day=course.day,
        period=course.period,
        weeks=course.weeks,
        room=course.room,
        teacher=course.teacher,
        target=course.target,
        color=course.color,
        term=course.term,
        created_at=now,
        updated_at=now
    )
    try:
        record_id = await database.execute(query)
        return success(data={"id": record_id, **course.dict()})
    except Exception as e:
        return error(message=f"创建失败: {str(e)}")


@router.get("/{course_id}")
async def get_course(course_id: int):
    """获取单个课程"""
    query = courses.select().where(courses.c.id == course_id)
    row = await database.fetch_one(query)
    if not row:
        raise HTTPException(status_code=404, detail="课程不存在")
    return success(data=dict(row))


@router.put("/{course_id}")
async def update_course(course_id: int, course: CourseUpdate):
    """更新课程"""
    query = courses.select().where(courses.c.id == course_id)
    existing = await database.fetch_one(query)
    if not existing:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    update_data = {k: v for k, v in course.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    query = courses.update().where(courses.c.id == course_id).values(**update_data)
    await database.execute(query)
    
    # 返回更新后的数据
    query = courses.select().where(courses.c.id == course_id)
    row = await database.fetch_one(query)
    return success(data=dict(row))


@router.delete("/{course_id}")
async def delete_course(course_id: int):
    """删除课程"""
    query = courses.select().where(courses.c.id == course_id)
    existing = await database.fetch_one(query)
    if not existing:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    query = courses.delete().where(courses.c.id == course_id)
    await database.execute(query)
    return success(message="删除成功")


# ---- 课程表设置 API ----

@router.get("/settings/default")
async def get_schedule_settings():
    """获取课程表设置"""
    query = schedule_settings.select().where(schedule_settings.c.user_id == "default")
    row = await database.fetch_one(query)
    if not row:
        # 返回默认设置
        return success(data={
            "background": "",
            "background_opacity": 0.15,
            "table_opacity": 0.95,
            "bg_position_x": 50,
            "bg_position_y": 50,
            "bg_scale": 100,
            "notification_enabled": False
        })
    return success(data=dict(row))


@router.put("/settings/default")
async def update_schedule_settings(settings: ScheduleSettings):
    """更新课程表设置"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    query = schedule_settings.select().where(schedule_settings.c.user_id == "default")
    existing = await database.fetch_one(query)
    
    if existing:
        # 更新
        query = schedule_settings.update().where(schedule_settings.c.user_id == "default").values(
            background=settings.background,
            background_opacity=settings.background_opacity,
            table_opacity=settings.table_opacity,
            bg_position_x=settings.bg_position_x,
            bg_position_y=settings.bg_position_y,
            bg_scale=settings.bg_scale,
            notification_enabled=settings.notification_enabled,
            updated_at=now
        )
    else:
        # 创建
        query = schedule_settings.insert().values(
            user_id="default",
            background=settings.background,
            background_opacity=settings.background_opacity,
            table_opacity=settings.table_opacity,
            bg_position_x=settings.bg_position_x,
            bg_position_y=settings.bg_position_y,
            bg_scale=settings.bg_scale,
            notification_enabled=settings.notification_enabled,
            updated_at=now
        )
    
    await database.execute(query)
    return success(data=settings.dict())
