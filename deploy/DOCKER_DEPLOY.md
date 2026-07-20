# Docker 快速部署指南

## 环境要求

- [Docker](https://docs.docker.com/engine/install/) (>= 24.0)
- [Docker Compose](https://docs.docker.com/compose/install/) (>= 2.20)

## 快速开始

### 1. 克隆项目并进入目录

```bash
cd e:/template
```

### 2. 配置环境变量

```bash
# 从模板创建环境配置文件
cp .env.docker .env

# 编辑 .env 文件，至少修改以下配置：
# - SECRET_KEY: 生成一个随机密钥
# - PG_PASSWORD: PostgreSQL 数据库密码
# - REDIS_PASSWORD: Redis 密码
# - FIRST_SUPERUSER_PASSWORD: 初始管理员密码
```

### 3. 一键部署

```bash
# Linux / macOS
bash deploy/docker-deploy.sh

# 或手动执行:
docker compose up -d
```

### 4. 访问服务

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost |
| API 文档 | http://localhost/api/docs |
| 健康检查 | http://localhost/health |

## 服务架构

```
┌─────────────────────────────────────────────────────┐
│                    Docker 网络                        │
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐ │
│  │          │   │          │   │                  │ │
│  │ Postgres │───│  Redis   │───│   Backend        │ │
│  │  :5432   │   │  :6379   │   │  (FastAPI)       │ │
│  │          │   │          │   │   :8090           │ │
│  └──────────┘   └──────────┘   └────────┬─────────┘ │
│                                          │           │
│                                  ┌───────▼─────────┐ │
│                                  │                 │ │
│                                  │   Frontend      │ │
│                                  │  (Nginx + Vue)  │ │
│                                  │    :80          │ │
│                                  │                 │ │
│                                  └─────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## 目录结构

```
e:/template/
├── docker-compose.yml       # Docker Compose 编排文件
├── .env                     # 环境变量配置（已忽略 Git）
├── .env.docker              # Docker 环境变量模板
├── .dockerignore            # 根目录 Docker 忽略规则
├── back/
│   ├── Dockerfile           # 后端镜像构建文件
│   └── .dockerignore        # 后端 Docker 忽略规则
├── web/
│   ├── Dockerfile           # 前端镜像构建文件
│   ├── nginx.conf           # Nginx 运行配置
│   └── .dockerignore        # 前端 Docker 忽略规则
└── deploy/
    ├── docker-deploy.sh     # 一键部署脚本
    └── DOCKER_DEPLOY.md     # 本文档
```

## 常用命令

### 启动服务

```bash
# 后台启动所有服务
docker compose up -d

# 查看启动日志
docker compose logs -f

# 构建并启动（修改代码后）
docker compose up -d --build
```

### 停止服务

```bash
# 停止所有服务
docker compose down

# 停止并删除数据卷（⚠️ 会丢失数据库数据）
docker compose down -v
```

### 查看状态

```bash
# 服务状态
docker compose ps

# 实时日志
docker compose logs -f

# 特定服务日志
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

### 重启服务

```bash
# 重启所有服务
docker compose restart

# 重启特定服务
docker compose restart backend
```

### 进入容器

```bash
# 进入后端容器
docker compose exec backend bash

# 进入 PostgreSQL
docker compose exec postgres psql -U postgres -d blog

# 进入 Redis
docker compose exec redis redis-cli -a <密码>
```

## 数据持久化

数据存储在 Docker 卷中，不会因容器重建而丢失：

| 卷名 | 用途 |
|------|------|
| `blog-postgres-data` | PostgreSQL 数据库文件 |
| `blog-redis-data` | Redis 持久化数据 |
| `blog-media-data` | 上传的媒体文件 |
| `blog-backend-logs` | 后端日志 |

```bash
# 查看卷列表
docker volume ls | grep blog-

# 备份数据库
docker compose exec postgres pg_dump -U postgres -d blog > backup.sql

# 恢复数据库
docker compose exec -T postgres psql -U postgres -d blog < backup.sql
```

## 生产环境注意事项

1. **修改密钥**：务必修改 `.env` 中的 `SECRET_KEY` 为强随机字符串
2. **修改密码**：修改所有默认密码（数据库、Redis、管理员）
3. **关闭调试**：确认 `IS_PRODUCTION=true`
4. **限制端口暴露**：数据库和 Redis 端口绑定到 `127.0.0.1`，仅 Nginx 暴露 80 端口
5. **配置 HTTPS**：建议使用 Nginx + Let's Encrypt 配置 HTTPS
6. **资源限制**：可在 `docker-compose.yml` 中为各服务添加 CPU/内存限制
7. **日志轮转**：Docker 默认日志驱动支持轮转，建议配置 `max-size` 和 `max-file`

## 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker compose logs

# 检查 PostgreSQL 日志
docker compose logs postgres

# 检查后端日志
docker compose logs backend
```

### 数据库连接失败

检查 `.env` 中的数据库配置，确保：
- `PG_HOST=postgres`（使用服务名，非 localhost）
- `PG_PASSWORD` 与 `docker-compose.yml` 中的 `POSTGRES_PASSWORD` 一致

### 前端无法访问 API

确认 `web/nginx.conf` 中的 `proxy_pass` 地址为 `http://backend:8090/api/`
