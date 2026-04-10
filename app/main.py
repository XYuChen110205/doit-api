"""FastAPI 应用入口"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.database import database, create_tables
from app.response import success

print("[Main] Starting to load routers...")

try:
    from app.routers.tasks import router as tasks_router
    print("[Main] tasks_router loaded")
except Exception as e:
    print(f"[Main] ERROR loading tasks_router: {e}")
    tasks_router = None

try:
    from app.routers.notes import router as notes_router
    print("[Main] notes_router loaded")
except Exception as e:
    print(f"[Main] ERROR loading notes_router: {e}")
    notes_router = None

try:
    from app.routers.inbox import router as inbox_router
    print("[Main] inbox_router loaded")
except Exception as e:
    print(f"[Main] ERROR loading inbox_router: {e}")
    inbox_router = None

try:
    from app.routers.stats import router as stats_router
    print("[Main] stats_router loaded")
except Exception as e:
    print(f"[Main] ERROR loading stats_router: {e}")
    stats_router = None

try:
    from app.routers.tags import router as tags_router
    print("[Main] tags_router loaded")
except Exception as e:
    print(f"[Main] ERROR loading tags_router: {e}")
    tags_router = None

try:
    from app.routers.settings import router as settings_router
    print("[Main] settings_router loaded")
except Exception as e:
    print(f"[Main] ERROR loading settings_router: {e}")
    settings_router = None

try:
    from app.routers.task_tags import router as task_tags_router
    print("[Main] task_tags_router loaded")
except Exception as e:
    print(f"[Main] ERROR loading task_tags_router: {e}")
    task_tags_router = None

try:
    from app.routers.courses import router as courses_router
    print("[Main] courses_router loaded")
except Exception as e:
    print(f"[Main] ERROR loading courses_router: {e}")
    courses_router = None

try:
    from app.routers.auth import router as auth_router
    print("[Main] auth_router loaded")
except Exception as e:
    print(f"[Main] ERROR loading auth_router: {e}")
    import traceback
    traceback.print_exc()
    auth_router = None

# 检测是否在 Vercel 环境
is_vercel = os.environ.get('VERCEL') == '1'

print(f"[Main] VERCEL env: {os.environ.get('VERCEL')}")
print(f"[Main] is_vercel: {is_vercel}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    await database.connect()
    yield
    await database.disconnect()


# 创建 FastAPI 应用
if is_vercel:
    # Vercel 环境：不使用 lifespan，手动处理数据库连接
    app = FastAPI(title="Todo System API")
else:
    # 本地环境：正常使用 lifespan
    app = FastAPI(title="Todo System API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel 环境：使用中间件管理数据库连接
if is_vercel:
    @app.middleware("http")
    async def db_connection_middleware(request: Request, call_next):
        # 确保数据库已连接
        if not database.is_connected:
            await database.connect()
        response = await call_next(request)
        return response

# 只加载成功导入的路由
routers_loaded = []
if tasks_router:
    app.include_router(tasks_router)
    routers_loaded.append("tasks")
if notes_router:
    app.include_router(notes_router)
    routers_loaded.append("notes")
if inbox_router:
    app.include_router(inbox_router)
    routers_loaded.append("inbox")
if stats_router:
    app.include_router(stats_router)
    routers_loaded.append("stats")
if tags_router:
    app.include_router(tags_router)
    routers_loaded.append("tags")
if settings_router:
    app.include_router(settings_router)
    routers_loaded.append("settings")
if task_tags_router:
    app.include_router(task_tags_router)
    routers_loaded.append("task_tags")
if courses_router:
    app.include_router(courses_router)
    routers_loaded.append("courses")
if auth_router:
    app.include_router(auth_router)
    routers_loaded.append("auth")

print(f"[Main] Routers loaded: {', '.join(routers_loaded)}")

@app.get("/api/health")
async def health_check():
    return success(data={"status": "running"})

@app.get("/")
async def root():
    return success(data={"message": "Todo API is running", "docs": "/docs"})
