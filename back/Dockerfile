# ============================================================
# Dockerfile - 后端 FastAPI 服务
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖配置文件
COPY pyproject.toml .

# 安装 Python 依赖（利用 Docker 缓存层）
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    alembic \
    asyncpg \
    bcrypt \
    email-validator \
    fastapi \
    Jinja2 \
    loguru \
    Pillow \
    psycopg2-binary \
    pydantic \
    pydantic_settings \
    PyJWT \
    requests \
    "sqlalchemy[asyncio]" \
    sqlmodel \
    "uvicorn[standard]" \
    python-multipart \
    httpx \
    langchain \
    langchain-openai \
    langchain-anthropic \
    langchain-community

# ============================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

# 安装运行时系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 阶段复制已安装的包
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY . .

# 创建日志和媒体目录
RUN mkdir -p /app/log /app/media

# 赋予入口脚本执行权限
RUN chmod +x docker-entrypoint.sh

# 暴露端口
EXPOSE 8090

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8090/docs')" || exit 1

# 使用入口脚本启动
ENTRYPOINT ["/app/docker-entrypoint.sh"]
