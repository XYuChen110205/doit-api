"""数据库连接与建表"""
import databases
import sqlalchemy
import os
from pathlib import Path

# 优先使用环境变量中的数据库 URL（生产环境）
# 格式: postgresql://user:password@host:port/database
DATABASE_URL = os.getenv("DATABASE_URL", "")

# 如果没有环境变量，使用本地 SQLite（开发环境）
if not DATABASE_URL:
    DB_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = DB_DIR / "todo.db"
    DATABASE_URL = f"sqlite:///{DB_PATH}"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# ---- 任务表 ----
tasks = sqlalchemy.Table(
    "tasks", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("title", sqlalchemy.String(500), nullable=False),
    sqlalchemy.Column("detail", sqlalchemy.Text, default=""),
    sqlalchemy.Column("task_type", sqlalchemy.String(20), default="todo"),
    sqlalchemy.Column("status", sqlalchemy.String(20), default="pending"),
    sqlalchemy.Column("priority", sqlalchemy.Integer, default=0),
    sqlalchemy.Column("due_date", sqlalchemy.String(10), default=None),
    sqlalchemy.Column("start_time", sqlalchemy.String(19), default=None),
    sqlalchemy.Column("end_time", sqlalchemy.String(19), default=None),
    sqlalchemy.Column("source", sqlalchemy.String(20), default="direct"),
    sqlalchemy.Column("created_at", sqlalchemy.String(19)),
    sqlalchemy.Column("completed_at", sqlalchemy.String(19), default=None),
    sqlalchemy.Column("archived", sqlalchemy.Boolean, default=False),
)

# ---- 笔记表 ----
notes = sqlalchemy.Table(
    "notes", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("content", sqlalchemy.Text, default=""),
    sqlalchemy.Column("note_date", sqlalchemy.String(10), nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.String(19)),
    sqlalchemy.Column("updated_at", sqlalchemy.String(19)),
)

# ---- 收集箱 ----
inbox = sqlalchemy.Table(
    "inbox", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("content", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.String(19)),
)

# ---- 标签表 ----
tags = sqlalchemy.Table(
    "tags", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("name", sqlalchemy.String(50), unique=True, nullable=False),
    sqlalchemy.Column("color", sqlalchemy.String(7), default="#2C7A92"),
)

# ---- 任务-标签关联 ----
task_tags = sqlalchemy.Table(
    "task_tags", metadata,
    sqlalchemy.Column("task_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    sqlalchemy.Column("tag_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

# ---- 附件表 ----
attachments = sqlalchemy.Table(
    "attachments", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("note_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("notes.id", ondelete="CASCADE")),
    sqlalchemy.Column("file_path", sqlalchemy.String(500), nullable=False),
    sqlalchemy.Column("file_name", sqlalchemy.String(200)),
    sqlalchemy.Column("created_at", sqlalchemy.String(19)),
)

# ---- 课程表 ----
courses = sqlalchemy.Table(
    "courses", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("name", sqlalchemy.String(200), nullable=False),
    sqlalchemy.Column("code", sqlalchemy.String(50), default=""),
    sqlalchemy.Column("hours", sqlalchemy.Integer, default=48),
    sqlalchemy.Column("day", sqlalchemy.String(10), nullable=False),  # mon, tue, wed, thu, fri
    sqlalchemy.Column("period", sqlalchemy.Integer, nullable=False),  # 1-12
    sqlalchemy.Column("weeks", sqlalchemy.String(50), default="1-17周"),
    sqlalchemy.Column("room", sqlalchemy.String(200), default=""),
    sqlalchemy.Column("teacher", sqlalchemy.String(100), default=""),
    sqlalchemy.Column("target", sqlalchemy.String(100), default=""),
    sqlalchemy.Column("color", sqlalchemy.String(7), default="#E3F2FD"),
    sqlalchemy.Column("term", sqlalchemy.String(20), default="2024-2025-1"),
    sqlalchemy.Column("created_at", sqlalchemy.String(19)),
    sqlalchemy.Column("updated_at", sqlalchemy.String(19)),
)

# ---- 课程表设置 ----
schedule_settings = sqlalchemy.Table(
    "schedule_settings", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("user_id", sqlalchemy.String(50), default="default"),
    sqlalchemy.Column("background", sqlalchemy.Text, default=""),
    sqlalchemy.Column("background_opacity", sqlalchemy.Float, default=0.15),
    sqlalchemy.Column("table_opacity", sqlalchemy.Float, default=0.95),
    sqlalchemy.Column("bg_position_x", sqlalchemy.Float, default=50),
    sqlalchemy.Column("bg_position_y", sqlalchemy.Float, default=50),
    sqlalchemy.Column("bg_scale", sqlalchemy.Integer, default=100),
    sqlalchemy.Column("notification_enabled", sqlalchemy.Boolean, default=False),
    sqlalchemy.Column("updated_at", sqlalchemy.String(19)),
)


def create_tables():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    metadata.create_all(engine)
    engine.dispose()
