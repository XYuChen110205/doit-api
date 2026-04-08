"""FastAPI 应用入口"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import database, create_tables
from app.response import success
from app.routers.tasks import router as tasks_router
from app.routers.notes import router as notes_router
from app.routers.inbox import router as inbox_router
from app.routers.stats import router as stats_router
from app.routers.tags import router as tags_router
from app.routers.settings import router as settings_router
from app.routers.task_tags import router as task_tags_router
from app.routers.courses import router as courses_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    await database.connect()
    yield
    await database.disconnect()


# 检测是否在 Vercel 环境
is_vercel = os.environ.get('VERCEL') == '1'

if is_vercel:
    # Vercel 环境：简化初始化
    app = FastAPI(title="Todo System API")
else:
    # 本地/Railway 环境：正常使用 lifespan
    app = FastAPI(title="Todo System API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)
app.include_router(notes_router)
app.include_router(inbox_router)
app.include_router(stats_router)
app.include_router(tags_router)
app.include_router(settings_router)
app.include_router(task_tags_router)
app.include_router(courses_router)


@app.get("/api/health")
async def health_check():
    return success(data={"status": "running"})
