"""数据库连接与建表"""
import databases
import sqlalchemy
import os
from pathlib import Path

# 检测是否在 Vercel 环境
is_vercel = os.environ.get('VERCEL') == '1'

if is_vercel:
    # Vercel 环境使用内存数据库（因为文件系统不持久化，且外部数据库连接可能受限）
    DATABASE_URL = "sqlite:///:memory:"
else:
    # 本地环境使用文件数据库
    DB_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = DB_DIR / "todo.db"
    DATABASE_URL = f"sqlite:///{DB_PATH}"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# ---- 任务表 ----
tasks = sqlalchemy.Table(
    "tasks", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
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
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    sqlalchemy.Column("content", sqlalchemy.Text, default=""),
    sqlalchemy.Column("note_date", sqlalchemy.String(10), nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.String(19)),
    sqlalchemy.Column("updated_at", sqlalchemy.String(19)),
)

# ---- 收集箱 ----
inbox = sqlalchemy.Table(
    "inbox", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    sqlalchemy.Column("content", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.String(19)),
)

# ---- 标签表 ----
tags = sqlalchemy.Table(
    "tags", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    sqlalchemy.Column("name", sqlalchemy.String(50), nullable=False),
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
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
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
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    sqlalchemy.Column("background", sqlalchemy.Text, default=""),
    sqlalchemy.Column("background_opacity", sqlalchemy.Float, default=0.15),
    sqlalchemy.Column("table_opacity", sqlalchemy.Float, default=0.95),
    sqlalchemy.Column("bg_position_x", sqlalchemy.Float, default=50),
    sqlalchemy.Column("bg_position_y", sqlalchemy.Float, default=50),
    sqlalchemy.Column("bg_scale", sqlalchemy.Integer, default=100),
    sqlalchemy.Column("notification_enabled", sqlalchemy.Boolean, default=False),
    sqlalchemy.Column("updated_at", sqlalchemy.String(19)),
)

# ---- 用户表 ----
users = sqlalchemy.Table(
    "users", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("username", sqlalchemy.String(50), unique=True, nullable=False),
    sqlalchemy.Column("email", sqlalchemy.String(100), unique=True, nullable=False),
    sqlalchemy.Column("hashed_password", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("avatar", sqlalchemy.String(500), default=None),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=sqlalchemy.func.now()),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, default=None),
)


def create_tables():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    metadata.create_all(engine)
    engine.dispose()
