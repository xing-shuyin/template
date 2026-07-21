# Blog 管理系统

基于 FastAPI + Vue 3 的全栈后台管理系统，集成 AI 对话能力，支持 Docker 一键部署。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI + SQLModel (异步) |
| 数据库 | PostgreSQL 16 |
| 缓存 | Redis 7 |
| 前端框架 | Vue 3 + Vite |
| UI 组件库 | Element Plus |
| 图表 | ECharts 6 |
| AI 对话 | LangChain (OpenAI / Anthropic) + Vercel AI SDK |
| 部署 | Docker Compose + Nginx |

## 功能特性

- 🔐 **用户认证** — 注册、登录、邮箱验证、密码重置
- 👥 **RBAC 权限** — 用户 / 角色 / 菜单 / 部门管理
- 📄 **动态表单 & 模型** — 可配置的数据模型和表单构建
- 📁 **文件管理** — 图标库、媒体上传
- 💬 **AI 聊天** — 集成多种 LLM 的对话功能
- 📊 **数据可视化** — ECharts 图表展示
- 📝 **操作日志** — 登录日志、接口调用记录

## 项目结构

```
├── docker-compose.yml        # Docker Compose 编排
├── docker-deploy.sh          # 一键部署脚本
├── .env.docker               # Docker 环境变量模板
├── nginx.conf                # Nginx 配置
├── supervisor.conf           # Supervisor 进程管理
├── back/                     # 后端 (FastAPI)
│   ├── main.py               # 应用入口
│   ├── settings.py           # 配置管理
│   ├── models.py             # 数据模型
│   ├── db.py                 # 数据库连接
│   ├── cache.py              # 缓存连接
│   ├── security.py           # 安全认证
│   ├── middleware.py         # 中间件
│   ├── handler.py            # 异常处理
│   ├── utils.py              # 工具函数
│   ├── Dockerfile            # 后端镜像
│   ├── alembic/              # 数据库迁移
│   ├── media/                # 静态资源 & 邮件模板
│   └── src/                  # 路由模块
│       ├── routers.py        # 路由注册
│       ├── user.py           # 用户接口
│       ├── login.py          # 登录接口
│       ├── chat.py           # AI 对话接口
│       └── deps.py           # 依赖注入
├── web/                      # 前端 (Vue 3)
│   ├── Dockerfile            # 前端镜像
│   ├── nginx.conf            # 前端 Nginx 配置
│   └── src/
│       ├── App.vue           # 根组件
│       ├── views/            # 页面视图
│       │   ├── login.vue     # 登录页
│       │   ├── index.vue     # 首页
│       │   ├── chat.vue      # AI 聊天页
│       │   └── admin/        # 管理后台
│       │       └── system/   # 系统管理(用户/角色/菜单/部门等)
│       ├── components/       # 公共组件
│       │   ├── admin/        # 管理组件(表格/表单/菜单树等)
│       │   └── common/       # 通用组件(图表/选择器等)
│       └── utils/            # 工具函数(路由/请求/权限等)
└── deploy/
    └── DOCKER_DEPLOY.md      # Docker 部署详细文档
```

## 本地开发

### 环境要求

- Python >= 3.12
- Node.js >= 18 + pnpm
- PostgreSQL 16
- Redis 7

### 后端

```bash
cd back

# 安装依赖
uv sync

# 配置环境变量 (参考 .env.example)
cp .env.example .env

# 数据库迁移
uv run alembic upgrade head

# 启动开发服务器
uv run uvicorn main:app --reload --port 8090
```

### 前端

```bash
cd web

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

## Docker 部署

### 环境要求

- [Docker](https://docs.docker.com/engine/install/) >= 24.0
- [Docker Compose](https://docs.docker.com/compose/install/) >= 2.20

### 快速部署

```bash
# 1. 首次运行（自动创建 .env 模板）
bash docker-deploy.sh
# 脚本会提示编辑 .env 中的密钥和密码

# 2. 修改 .env 后再次运行
bash docker-deploy.sh
```

### 手动部署

```bash
# 创建并编辑环境变量
cp .env.docker .env
# 至少修改: SECRET_KEY, PG_PASSWORD, REDIS_PASSWORD, FIRST_SUPERUSER_PASSWORD

# 构建并启动
docker compose up -d

# 查看状态
docker compose ps
```

### 访问服务

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost |
| API 文档 (Swagger) | http://localhost/api/docs |
| 健康检查 | http://localhost/health |

## 服务架构

```
┌─────────────────────────────────────────────────────┐
│                    Docker 网络 (blog-network)         │
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐ │
│  │          │   │          │   │                  │ │
│  │ Postgres │   │  Redis   │   │   Backend        │ │
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

## 常用命令

```bash
# 启动 / 停止
docker compose up -d              # 后台启动
docker compose down               # 停止服务
docker compose down -v            # 停止并删除数据 (⚠️ 清空数据库)
docker compose restart            # 重启所有服务

# 构建
docker compose build              # 重新构建镜像
docker compose up -d --build      # 构建并启动

# 日志
docker compose logs -f            # 实时日志
docker compose logs -f backend    # 后端日志
docker compose logs -f frontend   # 前端日志

# 进入容器
docker compose exec backend bash          # 后端容器
docker compose exec postgres psql -U postgres -d blog   # 数据库
docker compose exec redis redis-cli -a <密码>           # Redis

# 备份恢复
docker compose exec postgres pg_dump -U postgres -d blog > backup.sql
docker compose exec -T postgres psql -U postgres -d blog < backup.sql
```

## 数据持久化

数据存储在 Docker 卷中，容器重建不会丢失：

| 卷名 | 用途 |
|------|------|
| `blog-postgres-data` | PostgreSQL 数据库文件 |
| `blog-redis-data` | Redis 持久化数据 |
| `blog-media-data` | 上传的媒体文件 |
| `blog-backend-logs` | 后端日志 |

## 生产环境检查清单

- [ ] 修改 `SECRET_KEY` 为强随机字符串
- [ ] 修改所有默认密码（数据库、Redis、管理员）
- [ ] 确认 `IS_PRODUCTION=true`
- [ ] 数据库和 Redis 端口仅绑定 `127.0.0.1`
- [ ] 配置 HTTPS（Nginx + Let's Encrypt）
- [ ] 在 `docker-compose.yml` 中配置资源限制
- [ ] 配置 Docker 日志轮转 (`max-size`, `max-file`)

## 故障排查

```bash
# 容器无法启动
docker compose logs                  # 查看所有日志
docker compose ps                    # 查看服务状态

# 数据库连接失败
docker compose logs postgres         # 检查 PostgreSQL 日志
docker compose exec backend bash     # 进入后端手动测试连接

# 端口冲突
lsof -i :80                         # 检查 80 端口占用
```
