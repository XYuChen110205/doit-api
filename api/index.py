# Vercel Serverless 入口文件
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 强制刷新输出
sys.stdout.write(f"[Index] Python version: {sys.version}\n")
sys.stdout.write(f"[Index] Current directory: {os.getcwd()}\n")
sys.stdout.write(f"[Index] VERCEL env: {os.environ.get('VERCEL')}\n")
sys.stdout.write(f"[Index] DATABASE_URL exists: {bool(os.environ.get('DATABASE_URL'))}\n")
sys.stdout.write(f"[Index] DATABASE_URL_Doit exists: {bool(os.environ.get('DATABASE_URL_Doit'))}\n")
sys.stdout.flush()

# 在导入 app 之前先创建表
try:
    from app.database import create_tables
    create_tables()
    sys.stdout.write("[Index] Database tables created successfully\n")
except Exception as e:
    sys.stdout.write(f"[Index] ERROR creating tables: {e}\n")
    import traceback
    traceback.print_exc()
sys.stdout.flush()

try:
    from app.main import app
    sys.stdout.write("[Index] App imported successfully\n")
except Exception as e:
    sys.stdout.write(f"[Index] ERROR importing app: {e}\n")
    import traceback
    traceback.print_exc()
    raise
sys.stdout.flush()

# Vercel 需要这个 handler
handler = app
