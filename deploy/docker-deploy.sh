#!/bin/bash
# ============================================================
# Docker 快速部署脚本
# 使用方式: bash deploy/docker-deploy.sh
# ============================================================

set -e

echo "=========================================="
echo "  Blog Docker 部署脚本"
echo "=========================================="

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: 未安装 Docker，请先安装 Docker${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}错误: 未安装 Docker Compose，请先安装 Docker Compose${NC}"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}未发现 .env 文件，正在从 .env.docker 创建...${NC}"
    cp .env.docker .env
    echo -e "${YELLOW}请编辑 .env 文件，修改以下配置:${NC}"
    echo "  1. SECRET_KEY - 随机密钥"
    echo "  2. PG_PASSWORD - 数据库密码"
    echo "  3. REDIS_PASSWORD - Redis 密码"
    echo "  4. FIRST_SUPERUSER_PASSWORD - 管理员密码"
    echo ""
    echo -e "${YELLOW}编辑完成后重新运行此脚本。${NC}"
    exit 0
fi

echo -e "${GREEN}[1/4] 构建镜像...${NC}"
docker compose build --pull

echo -e "${GREEN}[2/4] 启动服务...${NC}"
docker compose up -d

echo -e "${GREEN}[3/4] 等待服务就绪...${NC}"
echo "  等待数据库就绪..."
sleep 10

echo -e "${GREEN}[4/4] 部署完成!${NC}"
echo ""
echo "=========================================="
echo "  服务状态:"
docker compose ps
echo ""
echo "=========================================="
echo -e "  访问地址: ${GREEN}http://localhost${NC}"
echo -e "  Supervisor: ${GREEN}http://localhost:9001${NC} (如已配置)"
echo ""
echo "  常用命令:"
echo "  docker compose logs -f     # 查看日志"
echo "  docker compose down        # 停止服务"
echo "  docker compose restart     # 重启服务"
echo "  docker compose ps          # 查看状态"
echo "=========================================="
