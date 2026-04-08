"""统计业务逻辑"""
from datetime import datetime, timedelta
from app.database import database, tasks


async def get_weekly_stats(date_str: str) -> dict:
    """获取指定日期所在周的统计信息"""
    # 解析日期
    date = datetime.strptime(date_str, "%Y-%m-%d")
    
    # 计算本周的开始（周一）和结束（周日）
    weekday = date.weekday()  # 0=周一, 6=周日
    week_start = date - timedelta(days=weekday)
    week_end = week_start + timedelta(days=6)
    
    start_str = week_start.strftime("%Y-%m-%d")
    end_str = week_end.strftime("%Y-%m-%d")
    
    # 查询本周所有任务
    query = tasks.select().where(
        tasks.c.due_date >= start_str,
        tasks.c.due_date <= end_str
    )
    rows = await database.fetch_all(query)
    task_list = [dict(r._mapping) for r in rows]
    
    # 统计数据
    total_tasks = len(task_list)
    completed_tasks = sum(1 for t in task_list if t["status"] == "done")
    completion_rate = round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0
    
    # 每日统计
    daily_breakdown = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        day_tasks = [t for t in task_list if t["due_date"] == day_str]
        daily_breakdown.append({
            "date": day_str,
            "total": len(day_tasks),
            "completed": sum(1 for t in day_tasks if t["status"] == "done")
        })
    
    return {
        "period": "week",
        "start_date": start_str,
        "end_date": end_str,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": completion_rate,
        "daily_breakdown": daily_breakdown
    }


async def get_monthly_stats(date_str: str) -> dict:
    """获取指定日期所在月的统计信息"""
    # 解析日期
    date = datetime.strptime(date_str, "%Y-%m-%d")
    year = date.year
    month = date.month
    
    # 计算月初和月末
    month_start = datetime(year, month, 1)
    if month == 12:
        month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = datetime(year, month + 1, 1) - timedelta(days=1)
    
    start_str = month_start.strftime("%Y-%m-%d")
    end_str = month_end.strftime("%Y-%m-%d")
    
    # 查询当月所有任务
    query = tasks.select().where(
        tasks.c.due_date >= start_str,
        tasks.c.due_date <= end_str
    )
    rows = await database.fetch_all(query)
    task_list = [dict(r._mapping) for r in rows]
    
    # 统计数据
    total_tasks = len(task_list)
    completed_tasks = sum(1 for t in task_list if t["status"] == "done")
    completion_rate = round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0
    
    # 每周统计
    weekly_breakdown = []
    current_week_start = month_start
    week_num = 1
    
    while current_week_start <= month_end:
        current_week_end = min(current_week_start + timedelta(days=6), month_end)
        week_start_str = current_week_start.strftime("%Y-%m-%d")
        week_end_str = current_week_end.strftime("%Y-%m-%d")
        
        week_tasks = [t for t in task_list if week_start_str <= t["due_date"] <= week_end_str]
        weekly_breakdown.append({
            "week": week_num,
            "start_date": week_start_str,
            "end_date": week_end_str,
            "total": len(week_tasks),
            "completed": sum(1 for t in week_tasks if t["status"] == "done")
        })
        
        current_week_start = current_week_end + timedelta(days=1)
        week_num += 1
    
    return {
        "period": "month",
        "start_date": start_str,
        "end_date": end_str,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": completion_rate,
        "weekly_breakdown": weekly_breakdown
    }
