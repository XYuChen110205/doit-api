"""设置路由 - 数据导出等"""
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.database import database, tasks, notes, inbox

router = APIRouter(prefix="/api", tags=["Settings"])


@router.get("/export")
async def api_export_data(format: str = Query("json", description="导出格式")):
    """导出所有数据"""
    # 查询所有任务
    task_rows = await database.fetch_all(tasks.select())
    task_list = [dict(r._mapping) for r in task_rows]
    
    # 查询所有笔记
    note_rows = await database.fetch_all(notes.select())
    note_list = [dict(r._mapping) for r in note_rows]
    
    # 查询所有收集箱条目
    inbox_rows = await database.fetch_all(inbox.select())
    inbox_list = [dict(r._mapping) for r in inbox_rows]
    
    export_data = {
        "export_time": __import__('datetime').datetime.now().isoformat(),
        "tasks": task_list,
        "notes": note_list,
        "inbox": inbox_list
    }
    
    if format == "json":
        return JSONResponse(
            content=export_data,
            headers={
                "Content-Disposition": "attachment; filename=todo_export.json"
            }
        )
    
    return {"code": 400, "message": "不支持的导出格式", "data": None}
