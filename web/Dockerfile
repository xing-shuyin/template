# ============================================================
# Dockerfile - 前端 Vue.js 构建 + Nginx 服务
# 多阶段构建
# ============================================================

# ---- 构建阶段 ----
FROM node:22-alpine AS build-stage

WORKDIR /app

# 复制依赖配置文件
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# 安装 pnpm 和依赖
RUN corepack enable && corepack prepare pnpm@latest --activate && \
    pnpm install --frozen-lockfile

# 复制源代码
COPY . .

# 构建生产版本
RUN pnpm build

# ---- 运行阶段 ----
FROM nginx:stable-alpine AS production-stage

# 从构建阶段复制构建产物
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制自定义 Nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 确保配置文件正确
RUN rm -f /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
