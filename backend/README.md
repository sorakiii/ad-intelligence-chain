# AI 广告平台后端服务

## 项目概述

本项目是一个基于 Flask 的 AI 广告平台后端服务，集成了多种 AI 服务和功能，包括智能对话、视频生成、图像生成、HTML 生成等。采用微服务架构设计，支持异步任务处理和分布式部署。

### 核心功能

- 🤖 **智能对话系统**: 基于 Dify 平台的多角色对话服务
- 🎬 **视频生成**: 集成视频生成 API，支持异步处理和状态跟踪
- 🎨 **图像生成**: 集成 Midjourney API，支持图像创作
- 📄 **HTML 生成**: 智能生成 HTML 页面
- 📊 **数据分析**: 完整的用户行为和使用统计分析
- 🔐 **用户认证**: JWT 令牌认证和权限管理
- 📱 **短信服务**: 验证码发送和用户验证
- ☁️ **文件存储**: 华为云 OBS 对象存储集成

## 技术栈

- **Web 框架**: Flask 2.x
- **数据库**: PostgreSQL (生产) / SQLite (开发)
- **ORM**: SQLAlchemy + Flask-SQLAlchemy
- **异步任务**: Celery + Redis
- **认证**: Flask-JWT-Extended
- **文件存储**: 华为云 OBS
- **容器化**: Docker + Docker Compose
- **API 文档**: REST API

## 项目结构

```
backend/
├── app/                          # 应用主目录
│   ├── __init__.py              # Flask 应用工厂
│   ├── config.py                # 配置管理
│   ├── requirements.txt         # Python 依赖
│   ├── api/                     # API 路由层
│   │   ├── auth.py             # 认证相关 API
│   │   ├── chat.py             # 对话服务 API
│   │   ├── video.py            # 视频生成 API
│   │   ├── mj.py               # Midjourney API
│   │   ├── html.py             # HTML 生成 API
│   │   ├── analytics.py        # 数据分析 API
│   │   └── roles.py            # 角色管理 API
│   ├── models/                  # 数据模型层
│   │   ├── user.py             # 用户模型
│   │   ├── chat.py             # 对话模型
│   │   ├── video_task.py       # 视频任务模型
│   │   ├── mj_task.py          # MJ 任务模型
│   │   ├── role.py             # 角色模型
│   │   ├── message_html.py     # HTML 消息模型
│   │   └── verification.py     # 验证码模型
│   ├── services/                # 服务层
│   │   ├── auth.py             # 认证服务
│   │   ├── dify_service.py     # Dify 平台服务
│   │   ├── mj_service.py       # Midjourney 服务
│   │   ├── branch_service.py   # 分支服务
│   │   └── sms.py              # 短信服务
│   ├── tasks/                   # 异步任务
│   │   ├── video_tasks.py      # 视频处理任务
│   │   ├── mj_tasks.py         # 图像处理任务
│   │   └── html_tasks.py       # HTML 生成任务
│   └── utils/                   # 工具模块
│       ├── logger.py           # 日志工具
│       ├── response.py         # 响应工具
│       ├── file.py             # 文件工具
│       └── time.py             # 时间工具
├── run.py                       # 应用启动入口
├── celery_config.py            # Celery 配置
├── celery_worker.py            # Celery Worker 启动
├── migrations/                 # 数据库迁移文件
├── tests/                      # 测试文件
├── logs/                       # 日志目录
├── Dockerfile                  # 生产环境容器配置
├── Dockerfile.dev              # 开发环境容器配置
└── README.md                   # 项目文档
```

## 系统架构

### 整体架构图

```mermaid
graph TB
    Client[客户端应用] --> Nginx[Nginx 负载均衡]
    Nginx --> Flask[Flask 应用服务器]
    Flask --> PostgreSQL[(PostgreSQL 数据库)]
    Flask --> Redis[(Redis 缓存/队列)]
    Flask --> OBS[华为云 OBS 存储]
    
    Redis --> Celery[Celery Worker]
    Celery --> Beat[Celery Beat 定时任务]
    
    Flask --> Dify[Dify AI 平台]
    Flask --> MJ[Midjourney API]
    Flask --> Video[视频生成 API]
    Flask --> SMS[短信服务 API]
    
    subgraph "外部服务"
        Dify
        MJ
        Video
        SMS
    end
    
    subgraph "核心服务"
        Flask
        Celery
        Beat
    end
    
    subgraph "数据存储"
        PostgreSQL
        Redis
        OBS
    end
```

### 数据流程图

```mermaid
sequenceDiagram
    participant C as 客户端
    participant F as Flask API
    participant D as 数据库
    participant R as Redis
    participant CE as Celery
    participant AI as AI 服务

    C->>F: 发送请求 (聊天/生成)
    F->>D: 保存用户数据
    F->>AI: 调用 AI 服务
    AI->>F: 返回结果/任务ID
    
    alt 同步返回
        F->>C: 直接返回结果
    else 异步处理
        F->>R: 推送任务到队列
        F->>C: 返回任务ID
        CE->>R: 获取任务
        CE->>AI: 处理任务
        AI->>CE: 返回处理结果
        CE->>D: 更新任务状态
        C->>F: 轮询任务状态
        F->>D: 查询任务状态
        F->>C: 返回最新状态
    end
```

## 核心功能模块

### 1. 智能对话系统 (`app/api/chat.py`)

**功能特性**:
- 多角色对话支持
- 会话管理（创建、删除、重命名、归档）
- 文件上传与处理
- 消息反馈和评分
- 建议问题生成
- 分支对话管理

**核心 API**:
```http
GET    /api/chat/sessions              # 获取会话列表
POST   /api/chat/messages              # 发送消息
GET    /api/chat/sessions/{id}/messages # 获取会话消息
POST   /api/chat/files/upload          # 上传文件
DELETE /api/chat/sessions/{id}         # 删除会话
```

### 2. 视频生成服务 (`app/api/video.py`)

**功能特性**:
- 异步视频生成
- 任务状态跟踪
- 视频 URL 自动刷新
- 批量任务处理

**核心 API**:
```http
POST /api/video/generate      # 创建视频生成任务
GET  /api/video/tasks         # 获取任务列表
GET  /api/video/tasks/{id}    # 获取任务详情
```

### 3. 图像生成服务 (`app/api/mj.py`)

**功能特性**:
- Midjourney 图像生成
- 任务状态实时跟踪
- 图像变换和优化
- 历史记录管理

**核心 API**:
```http
POST /api/mj/generate        # 生成图像
GET  /api/mj/tasks           # 获取任务列表
GET  /api/mj/tasks/{id}      # 获取任务状态
```

### 4. HTML 生成服务 (`app/api/html.py`)

**功能特性**:
- 智能 HTML 页面生成
- 模板定制化
- 代码优化
- 实时预览

### 5. 数据分析服务 (`app/api/analytics.py`)

**功能特性**:
- Token 使用统计
- 用户行为分析
- 角色使用情况
- 每日数据报告

**核心 API**:
```http
GET /api/analytics/total-usage     # 总体使用量
GET /api/analytics/user-usage      # 用户使用量
GET /api/analytics/role-usage      # 角色使用统计
GET /api/analytics/daily-stats     # 每日统计
```

### 6. 用户认证系统 (`app/api/auth.py`)

**功能特性**:
- 手机号注册/登录
- 短信验证码
- JWT 令牌认证
- 权限管理

**核心 API**:
```http
POST /auth/send-verification    # 发送验证码
POST /auth/register            # 用户注册
POST /auth/login               # 用户登录
POST /auth/refresh             # 刷新令牌
```

## 异步任务系统

### Celery 配置

项目使用 Celery 处理异步任务，配置文件：`celery_config.py`

**任务队列分类**:
- `default`: 默认队列
- `html_generation`: HTML 生成任务
- `video_processing`: 视频处理任务
- `image_processing`: 图像处理任务

**定时任务**:
- 每分钟检查视频任务状态
- 每天刷新视频 URL
- 每 10 秒检查 MJ 任务状态

### 任务处理流程

```mermaid
graph LR
    A[用户请求] --> B[Flask API]
    B --> C{任务类型}
    C -->|同步| D[直接处理]
    C -->|异步| E[推送到 Redis 队列]
    E --> F[Celery Worker 处理]
    F --> G[更新任务状态]
    G --> H[通知用户]
    
    D --> I[返回结果]
    H --> I
```

## 数据库设计

### 核心表结构

```mermaid
erDiagram
    users {
        int id PK
        string phone
        string password_hash
        int role_id FK
        datetime created_at
        datetime updated_at
    }
    
    roles {
        int id PK
        string title
        string description
        string icon
        string dify_api_key
        datetime created_at
    }
    
    chat_sessions {
        int id PK
        int user_id FK
        int role_id FK
        string title
        string conversation_id
        datetime last_time
        int message_count
        boolean is_starred
        boolean is_archived
    }
    
    chat_messages {
        int id PK
        int session_id FK
        string content
        string role
        int input_tokens
        int output_tokens
        datetime created_at
    }
    
    video_tasks {
        int id PK
        int user_id FK
        string task_id
        string prompt
        string status
        string video_url
        datetime created_at
        datetime updated_at
    }
    
    mj_tasks {
        int id PK
        int user_id FK
        string task_id
        string prompt
        string status
        string image_url
        datetime created_at
    }
    
    users ||--o{ chat_sessions : "has many"
    users ||--o{ video_tasks : "has many"
    users ||--o{ mj_tasks : "has many"
    roles ||--o{ chat_sessions : "used in"
    chat_sessions ||--o{ chat_messages : "contains"
```

## 环境配置

### 1. 开发环境设置

```bash
# 1. 克隆项目
git clone <repository-url>
cd backend

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r app/requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置必要参数
```

### 2. 环境变量配置

完整说明见 [docs/环境变量与密钥配置说明.md](../docs/环境变量与密钥配置说明.md)。

在 `app/.env`（或 `app/.env.development`）中配置以下环境变量：

```bash
# 数据库配置
SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost/ai_ad_platform

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# JWT 配置
JWT_SECRET_KEY=your-secret-key

# Dify API 配置
DIFY_API_URL=https://api.dify.ai/v1
DIFY_API_KEY=your-dify-api-key
DIFY_API_KEY_HTML_ZIP=app-your-html-zip-key
DIFY_API_KEY_HTML_RAW=app-your-html-raw-key
DIFY_API_KEY_VIDEO_SCRIPT=app-your-video-script-key
DIFY_API_KEY_MJ_PROMPT=app-your-mj-prompt-key

# DashScope 文生视频
DASHSCOPE_API_KEY=your-dashscope-api-key

# Midjourney API 配置
MJ_API_URL=https://api.midjourney.com
MJ_API_KEY=your-mj-api-key

# 华为云 OBS 配置
OBS_ACCESS_KEY=your-access-key
OBS_SECRET_KEY=your-secret-key
OBS_ENDPOINT=https://obs.cn-north-4.myhuaweicloud.com
OBS_BUCKET=your-bucket-name

# 短信服务配置
SMS_ACCOUNT=your-sms-account
SMS_PASSWORD=your-sms-password
```

## 部署指南

### 1. 本地开发部署

```bash
# 启动 Redis
redis-server

# 启动 Flask 应用
python run.py

# 启动 Celery Worker (新终端)
celery -A celery_worker.celery worker --loglevel=info

# 启动 Celery Beat (新终端)
celery -A celery_worker.celery beat --loglevel=info
```

### 2. Docker 部署

```bash
# 构建镜像
docker build -t ai-ad-platform-backend .

# 运行容器
docker run -d \
  --name ai-ad-backend \
  -p 5002:5002 \
  -e FLASK_ENV=production \
  ai-ad-platform-backend

# 或使用 Docker Compose
docker-compose up -d
```

### 3. 生产环境部署

```bash
# 使用 Gunicorn 启动
gunicorn -w 4 -b 0.0.0.0:5002 run:app

# 配置 Nginx 反向代理
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## API 文档

### 认证

所有 API 请求都需要在 Header 中包含 JWT 令牌：

```http
Authorization: Bearer <your-jwt-token>
```

### 响应格式

所有 API 响应都遵循统一格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    // 响应数据
  }
}
```

### 错误处理

错误响应格式：

```json
{
  "code": 400,
  "message": "错误信息",
  "error": "详细错误描述"
}
```

## 监控与日志

### 日志配置

- 应用日志：`app.log`
- Celery 日志：终端输出
- 数据库日志：PostgreSQL 日志
- Nginx 日志：access.log 和 error.log

### 监控指标

- API 响应时间
- 任务处理时间
- 数据库连接数
- Redis 内存使用
- 系统资源使用

## 性能优化

### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_video_tasks_user_id ON video_tasks(user_id);
CREATE INDEX idx_video_tasks_status ON video_tasks(status);
```

### 2. 缓存策略

- Redis 缓存用户会话信息
- 文件上传缓存
- API 响应缓存

### 3. 异步处理优化

```python
# Celery 配置优化
CELERY_TASK_ROUTES = {
    'app.tasks.video_tasks.*': {'queue': 'video'},
    'app.tasks.mj_tasks.*': {'queue': 'image'},
}

# 任务重试配置
@celery.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def generate_video_task(self, task_data):
    # 任务处理逻辑
    pass
```

## 测试

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_chat.py

# 生成测试覆盖率报告
python -m pytest --cov=app tests/
```

### 测试文件结构

```
tests/
├── test_auth.py          # 认证测试
├── test_chat.py          # 对话测试
├── test_video.py         # 视频生成测试
├── test_mj.py            # 图像生成测试
├── test_analytics.py     # 数据分析测试
└── fixtures/             # 测试数据
```

## 故障排除

### 常见问题

1. **Celery 无法连接到 Redis**
   - 检查 Redis 服务状态
   - 验证 REDIS_URL 配置

2. **数据库连接错误**
   - 检查数据库服务状态
   - 验证数据库连接参数

3. **文件上传失败**
   - 检查 OBS 配置
   - 验证存储桶权限

4. **AI 服务调用失败**
   - 检查 API 密钥配置
   - 验证网络连接

### 调试技巧

```python
# 启用调试模式
export FLASK_ENV=development
export FLASK_DEBUG=1

# 查看详细日志
tail -f app.log

# Celery 调试
celery -A celery_worker.celery inspect active
celery -A celery_worker.celery inspect stats
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目维护者：[Your Name]
- 邮箱：[your.email@example.com]
- 项目地址：[https://github.com/your-username/ai-advertising-platform]