#!/bin/bash

# 适配您的部署流程: down -> build -> up -d
# 自动生成版本号并部署

set -e

echo "🚀 AI广告平台部署脚本"
echo "====================="

# 生成版本信息
BUILD_VERSION=$(date +"%Y.%m.%d.%H%M")
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")

echo "📋 版本号: $BUILD_VERSION"
echo "📅 构建时间: $BUILD_DATE"
echo ""

# 设置环境变量
export BUILD_VERSION
export BUILD_DATE

# 1. 停止服务
echo "🛑 停止服务..."
docker-compose down

# 2. 构建并启动
echo "🔨 构建并启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 服务状态:"
docker-compose ps

echo ""
echo "🎉 部署完成！"
echo "🌐 前端地址: http://localhost"
echo "📋 当前版本: $BUILD_VERSION"
echo ""
echo "💡 用户将在2分钟内收到版本更新提示"
