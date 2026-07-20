#!/bin/bash
# ============================================================
# Docker 后端入口脚本
# - 运行数据库迁移
# - 启动 FastAPI 服务
# ============================================================

set -e

echo "=========================================="
echo "  初始化后端服务..."
echo "=========================================="

# 等待数据库就绪
echo "[1/3] 等待数据库就绪..."
python -c "
import time
import psycopg2
import os

db_host = os.environ.get('PG_HOST', 'localhost')
db_port = os.environ.get('PG_PORT', '5432')
db_name = os.environ.get('PG_DATABASE', 'blog')
db_user = os.environ.get('PG_USER', 'postgres')
db_pass = os.environ.get('PG_PASSWORD', '')

for i in range(30):
    try:
        conn = psycopg2.connect(
            host=db_host, port=db_port, dbname=db_name,
            user=db_user, password=db_pass
        )
        conn.close()
        print('  数据库已就绪!')
        break
    except Exception as e:
        if i < 29:
            time.sleep(2)
        else:
            print(f'  数据库连接失败: {e}')
            exit(1)
"

# 运行数据库迁移
echo "[2/4] 运行数据库迁移..."
if alembic upgrade head 2>/dev/null; then
    echo "  数据库迁移完成!"
else
    echo "  警告: Alembic 迁移未执行，尝试直接初始化数据库表..."
    python -c "
from main import app
from db import init_db
init_db(app)
print('  数据库表初始化完成!')
"
fi

# 启动服务
echo "[3/4] 启动 FastAPI 服务..."
echo "=========================================="
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port "${BACK_PORT:-8090}" \
    --proxy-headers \
    --forwarded-allow-ips "*" \
    --log-level info
