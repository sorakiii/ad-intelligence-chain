@echo off
REM 适配您的部署流程: down -> build -> up -d
REM 自动生成版本号并部署

setlocal enabledelayedexpansion

echo 🚀 AI广告平台部署脚本
echo =====================

REM 生成版本信息
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%"

set BUILD_VERSION=%YYYY%.%MM%.%DD%.%HH%%Min%
set BUILD_DATE=%YYYY%-%MM%-%DD%T%HH%:%Min%:00.000Z

echo 📋 版本号: %BUILD_VERSION%
echo 📅 构建时间: %BUILD_DATE%
echo.

REM 设置环境变量
set BUILD_VERSION=%BUILD_VERSION%
set BUILD_DATE=%BUILD_DATE%

REM 1. 停止服务
echo 🛑 停止服务...
docker-compose down

REM 2. 构建并启动
echo 🔨 构建并启动服务...
docker-compose up --build -d

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 📊 服务状态:
docker-compose ps

echo.
echo 🎉 部署完成！
echo 🌐 前端地址: http://localhost
echo 📋 当前版本: %BUILD_VERSION%
echo.
echo 💡 用户将在2分钟内收到版本更新提示
