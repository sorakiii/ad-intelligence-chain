# 广告智链 Ad Intelligence Chain

> 中文说明优先。English documentation is available below.

广告智链是一个开源的 AI 广告创作与协作平台，面向广告团队、内容创作者、AI 应用研究者和开发者。项目由 Vue 3 前端与 Flask 后端组成，集成多角色 AI 对话、HTML 页面生成、Midjourney 图像生成、文生视频任务、用户认证、统计分析、异步任务队列和对象存储能力。

它适合用来研究「AI 参与广告生产」的工程链路，也可以继续扩展为企业内部的广告创意工作台、AI Agent 协作平台或多模型内容生产系统。

## 功能特性

- 多角色 AI 对话与会话管理
- 广告策略、产品验证、定向服务等工作区页面
- HTML 内容生成与实时预览
- Midjourney 图像生成任务管理
- 文生视频任务创建、状态跟踪与 URL 刷新
- 用户注册、登录、短信验证码与 JWT 权限认证
- Token 使用量、用户使用量、角色使用情况等统计分析
- Celery + Redis 异步任务队列
- 华为云 OBS 文件上传与预览链接生成
- Docker / Docker Compose 部署配置

## 技术栈

- 前端：Vue 3、Vite 6、Pinia、Vue Router、Element Plus、ECharts、Quill、Axios
- 后端：Python、Flask、SQLAlchemy、Flask-JWT-Extended、Celery、Redis、Alembic
- 数据库：MySQL / PostgreSQL / SQLite，按环境配置
- 存储：华为云 OBS
- 部署：Docker、Docker Compose、Nginx、Gunicorn

## 项目结构

```text
.
├── backend/                  # Flask API、模型、服务、任务队列与迁移
│   ├── app/
│   │   ├── api/              # API 路由
│   │   ├── models/           # 数据模型
│   │   ├── services/         # Dify、MJ、短信、认证等服务
│   │   ├── tasks/            # Celery 异步任务
│   │   └── utils/            # 工具函数
│   ├── migrations/           # Alembic 数据库迁移
│   └── tests/                # 后端测试
├── frontend/                 # Vue 3 + Vite 前端应用
│   └── src/
├── specs/                    # 功能设计与接口调研文档
├── docker-compose.yml        # 生产/部署编排示例
├── docker-compose.dev.yml    # 开发环境编排示例
└── 环境变量与密钥配置说明.md      # 环境变量与密钥配置说明
```

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- npm
- Redis
- MySQL / PostgreSQL / SQLite
- 可选：Docker 与 Docker Compose
- 你计划使用的 AI、短信、对象存储服务密钥

### 1. 克隆项目

```bash
git clone https://github.com/sorakiii/ad-intelligence-chain.git
cd ad-intelligence-chain
```

### 2. 配置后端环境变量

复制后端环境变量模板：

```bash
cp backend/app/.env.example backend/app/.env
```

然后按需填写数据库、Redis、JWT、Dify、DashScope、Midjourney、短信、OBS 等配置。完整说明见 `环境变量与密钥配置说明.md`。

不要把真实密钥提交到仓库。

### 3. 启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
python run.py
```

后端默认服务端口以环境变量和 `backend/app/config.py` 为准，常用本地地址为 `http://localhost:5002`。

### 4. 启动前端

另开一个终端：

```bash
cd frontend
npm install
npm run dev
```

前端开发服务默认运行在 `http://localhost:3005`。

### 5. Docker Compose 启动

项目提供 `docker-compose.yml` 与 `docker-compose.dev.yml`。根据自己的数据库、Redis、域名、证书与环境变量配置后，可使用：

```bash
docker compose up -d --build
```

## 环境变量

完整变量列表以 `backend/app/.env.example`、`frontend/.env.example` 和 `环境变量与密钥配置说明.md` 为准。常见变量包括：

- `SQLALCHEMY_DATABASE_URI`
- `REDIS_URL`
- `JWT_SECRET_KEY`
- `DIFY_API_URL`
- `DIFY_API_KEY`
- `DIFY_API_KEY_HTML_ZIP`
- `DIFY_API_KEY_HTML_RAW`
- `DIFY_API_KEY_VIDEO_SCRIPT`
- `DIFY_API_KEY_MJ_PROMPT`
- `DASHSCOPE_API_KEY`
- `MJ_API_URL`
- `MJ_API_KEY`
- `MJ_APP_KEY`
- `SMS_ACCOUNT`
- `SMS_PASSWORD`
- `SMS_SIGN_NAME`
- `OBS_ACCESS_KEY`
- `OBS_SECRET_KEY`
- `OBS_ENDPOINT`
- `OBS_BUCKET`
- `VITE_API_URL`
- `VITE_EQMJ_HOME`

前端变量必须使用 `VITE_` 前缀，并且不得包含任何服务端密钥。

## API 与模块说明

后端主要模块：

- `backend/app/api/auth.py`：注册、登录、验证码、JWT
- `backend/app/api/chat.py`：多角色 AI 对话、文件上传、会话管理
- `backend/app/api/html.py`：HTML 生成与预览
- `backend/app/api/mj.py`：Midjourney 图像生成任务
- `backend/app/api/video.py`：视频生成任务
- `backend/app/api/analytics.py`：统计分析
- `backend/app/api/roles.py`：AI 角色管理

更详细的后端说明见 `backend/README.md`，前端说明见 `frontend/README.md`。

## 安全说明

- 不要提交 `.env`、`.env.*`、真实 API Key、短信账号、OBS AK/SK、数据库连接串或生产日志。
- `frontend/.env.development` 与 `frontend/.env.production` 默认被忽略；公开配置请放在 `frontend/.env.example`。
- `backend/logs/`、`__pycache__/`、构建产物与本地调试文件默认不进入仓库。
- 若项目曾在私有开发阶段使用真实密钥，公开部署或 fork 前建议先轮换密钥。
- `blackgroud/` 当前按实验目录处理，默认不发布。

## 开发命令

前端：

```bash
cd frontend
npm install
npm run dev
npm run build
```

后端：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
python run.py
```

## 后续可扩展方向

- 补充一键初始化脚本与 Docker 环境示例
- 将 Dify、MJ、视频、短信、OBS Provider 抽象为更清晰的插件层
- 为核心 API、任务队列与 Provider 适配器补充自动化测试
- 增加在线演示数据与无需真实密钥的 Mock 模式
- 补充部署到云服务器的完整文档

## 许可证

MIT License。详见 `LICENSE`。

---

# Ad Intelligence Chain English Documentation

Ad Intelligence Chain is an open-source AI advertising creation and collaboration platform. It combines a Vue 3 frontend with a Flask backend and includes multi-role AI chat, HTML generation, Midjourney image tasks, text-to-video tasks, authentication, analytics, async job queues, and object-storage integrations.

The project is useful for studying AI-assisted advertising workflows, and can be extended into an internal creative workstation, AI Agent collaboration platform, or multi-model content production system.

## Features

- Multi-role AI chat and session management
- Advertising strategy and product-validation workspaces
- HTML generation and live preview
- Midjourney image-generation task management
- Text-to-video task management and URL refresh jobs
- User registration, login, SMS verification, and JWT auth
- Token, user, and role usage analytics
- Celery + Redis async task queues
- Huawei Cloud OBS upload and preview URL support
- Docker / Docker Compose deployment files

## Tech Stack

- Frontend: Vue 3, Vite 6, Pinia, Vue Router, Element Plus, ECharts, Quill, Axios
- Backend: Python, Flask, SQLAlchemy, Flask-JWT-Extended, Celery, Redis, Alembic
- Database: MySQL / PostgreSQL / SQLite depending on configuration
- Storage: Huawei Cloud OBS
- Deployment: Docker, Docker Compose, Nginx, Gunicorn

## Quick Start

```bash
git clone https://github.com/sorakiii/ad-intelligence-chain.git
cd ad-intelligence-chain
```

Backend:

```bash
cp backend/app/.env.example backend/app/.env
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
python run.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Read `环境变量与密钥配置说明.md` before using real credentials. Never commit secrets.

## License

MIT License. See `LICENSE`.
