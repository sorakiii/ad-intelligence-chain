# AI广告平台 - 部署说明

## 🚀 快速部署

### 一键部署
```bash
# Linux/Mac
./deploy.sh

# Windows
deploy.bat
```

### 手动部署
```bash
# 1. 停止服务
docker-compose down

# 2. 构建并启动（自动生成版本号）
docker-compose up --build -d
```

## 📋 版本管理

- **自动版本号**: 每次部署生成新版本 `YYYY.MM.DD.HHMM`
- **版本检查**: 用户2分钟内自动收到更新提示
- **缓存清理**: 一键清除所有缓存获取最新内容

## 🔧 核心文件

- `deploy.sh` / `deploy.bat` - 部署脚本
- `docker-compose.yml` - Docker配置
- `frontend/scripts/update-version.js` - 版本更新脚本
- `frontend/src/components/common/VersionCheck.vue` - 版本检查组件

## 💡 部署流程

1. **停止服务** → `docker-compose down`
2. **构建镜像** → 自动生成版本号
3. **启动服务** → `docker-compose up --build -d`
4. **用户提示** → 2分钟内收到更新通知

现在每次部署都会自动处理版本更新，用户不再受缓存问题困扰！
