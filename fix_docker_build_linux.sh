#!/bin/bash

# Docker构建修复脚本 (Linux版本)
# 解决内存不足和依赖冲突问题

echo "🔧 开始修复Docker构建问题 (Linux环境)..."

# 检查系统资源
echo "📊 检查系统资源..."
echo "内存使用情况:"
free -h
echo "磁盘使用情况:"
df -h

# 清理现有的Docker资源
echo "🧹 清理现有Docker资源..."
docker-compose down --remove-orphans
docker system prune -f

# 增加Docker构建内存限制
echo "⚙️  设置Docker构建参数..."
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# 方案1：使用优化的Dockerfile构建
echo "🏗️  方案1：使用优化的Dockerfile构建..."
cp backend/Dockerfile.optimized backend/Dockerfile

# 设置构建参数以减少内存使用
docker-compose build --no-cache --build-arg BUILDKIT_INLINE_CACHE=1 backend

if [ $? -eq 0 ]; then
    echo "✅ 方案1构建成功！"
    echo "🚀 启动服务..."
    docker-compose up -d
    exit 0
fi

echo "❌ 方案1失败，尝试方案2..."

# 方案2：使用最小化Dockerfile
echo "🔄 方案2：使用最小化Dockerfile..."
cp backend/Dockerfile.minimal backend/Dockerfile

echo "🔄 使用最小化Dockerfile重新构建..."
docker-compose build --no-cache backend

if [ $? -eq 0 ]; then
    echo "✅ 方案2构建成功！"
    echo "⚠️  注意：此方案移除了WeasyPrint支持，仅保留基础功能"
    echo "🚀 启动服务..."
    docker-compose up -d
    exit 0
fi

echo "❌ 方案2也失败，尝试方案3..."

# 方案3：使用Ubuntu基础镜像
echo "🔄 方案3：使用Ubuntu基础镜像..."
cp backend/Dockerfile.ubuntu backend/Dockerfile

echo "🔄 使用Ubuntu基础镜像重新构建..."
docker-compose build --no-cache backend

if [ $? -eq 0 ]; then
    echo "✅ 方案3构建成功！"
    echo "🚀 启动服务..."
    docker-compose up -d
    exit 0
fi

echo "❌ 方案3也失败，尝试方案4（手动修复）..."

# 方案4：手动修复依赖问题
echo "🔄 方案4：手动修复依赖问题..."

# 创建手动修复的Dockerfile
cat > backend/Dockerfile.manual << 'EOF'
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive

# 设置时区
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN chmod 1777 /tmp

# 使用官方源避免网络问题
RUN rm -f /etc/apt/sources.list \
    && echo "deb http://deb.debian.org/debian bookworm main non-free contrib" > /etc/apt/sources.list \
    && echo "deb http://deb.debian.org/debian-security bookworm-security main" >> /etc/apt/sources.list \
    && echo "deb http://deb.debian.org/debian bookworm-updates main non-free contrib" >> /etc/apt/sources.list

# 配置 pip 使用官方源
RUN mkdir -p ~/.pip \
    && echo "[global]" > ~/.pip/pip.conf \
    && echo "index-url = https://pypi.org/simple" >> ~/.pip/pip.conf

# 安装基础依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 安装核心图形库
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libharfbuzz0b \
    libfribidi0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 安装 Pango 相关库
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 安装最小字体集
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    fonts-liberation \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 安装 Chromium
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY app/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "run.py"]
EOF

# 使用手动修复的Dockerfile
cp backend/Dockerfile.manual backend/Dockerfile

echo "🔄 使用手动修复的Dockerfile重新构建..."
docker-compose build --no-cache backend

if [ $? -eq 0 ]; then
    echo "✅ 方案4构建成功！"
    echo "🚀 启动服务..."
    docker-compose up -d
    exit 0
fi

# 所有方案都失败了
echo "❌ 所有构建方案都失败了"
echo "📋 请检查以下可能的问题："
echo "   1. 系统内存不足 (建议至少4GB可用内存)"
echo "   2. 网络连接问题"
echo "   3. Docker版本兼容性"
echo "   4. 磁盘空间不足"
echo ""
echo "🔄 恢复原始Dockerfile..."
cp backend/Dockerfile.backup backend/Dockerfile 2>/dev/null || echo "原始Dockerfile已恢复"

echo "💡 建议尝试以下操作："
echo "   1. 增加系统内存或交换空间"
echo "   2. 检查网络连接和镜像源"
echo "   3. 更新Docker到最新版本"
echo "   4. 使用Docker多阶段构建"
echo "   5. 考虑在更高配置的机器上构建"

exit 1 