# Vercel Serverless 入口文件
import os
print(f"VERCEL env: {os.environ.get('VERCEL')}")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'not set')}")

from app.main import app

# Vercel 需要这个 handler
handler = app
