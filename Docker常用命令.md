# Docker 常用命令

面向本仓库（含 `docker-compose.yml` 与 `docker-compose.dev.yml`）的快速备忘。

## 镜像与容器

| 说明 | 命令 |
|------|------|
| 查看运行中容器 | `docker ps` |
| 查看全部容器 | `docker ps -a` |
| 查看本地镜像 | `docker images` |
| 进入容器 Shell | `docker exec -it <容器名或ID> sh`（Alpine）或 `bash` |
| 查看容器日志（跟随） | `docker logs -f <容器名或ID>` |
| 停止容器 | `docker stop <容器名或ID>` |
| 删除已停止容器 | `docker rm <容器名或ID>` |
| 删除镜像 | `docker rmi <镜像名或ID>` |

## Docker Compose（V2 推荐写法）

Compose 文件在根目录时，可在项目根执行：

### 生产向编排（`docker-compose.yml`）

```bash
# 后台启动全部服务
docker compose -f docker-compose.yml up -d

# 前台启动（看日志）
docker compose -f docker-compose.yml up

# 停止并删除容器（保留卷）
docker compose -f docker-compose.yml down

# 重新构建再启动
docker compose -f docker-compose.yml up -d --build

# 查看服务状态
docker compose -f docker-compose.yml ps

# 查看某服务日志
docker compose -f docker-compose.yml logs -f backend
```

### 开发向编排（`docker-compose.dev.yml`）

含 **frontend**（`npm run dev`）、**backend**（Flask + debugpy）、多个 **Celery worker**、**celery_beat**、**redis**；源码通过卷挂载到容器，改代码后一般热重载或重启对应服务即可。

**端口速查（宿主 → 容器）**

| 服务 | 业务端口 | 调试端口 |
|------|----------|----------|
| frontend | 3005 | 9229（Node 调试） |
| backend | 5002 | 5678（debugpy） |
| celery_worker | — | 5679 |
| celery_worker_html | — | 5680 |
| celery_worker_video | — | 5681 |
| redis | 由 Docker **随机分配**宿主端口映射到容器 6379（避免与本机固定 6379 冲突）；查实际端口：`docker compose -f docker-compose.dev.yml ps` |

**实时、分别看前端与后端日志**

- `logs` **不带** `-f`：只打印当前已有日志，打完就退出，**不是**实时流。
- 要**实时**且**前后端分开**：Compose 不能在同一终端里分屏；请在项目根开 **两个** 终端，各执行一条（`Ctrl+C` 只停止跟日志，**不会**停止容器）。

```bash
# 终端 A：仅前端
docker compose -f docker-compose.dev.yml logs -f frontend

# 终端 B：仅后端
docker compose -f docker-compose.dev.yml logs -f backend
```

上屏时若不想从很久以前开始刷，可加 `--tail`（例如只看最近 100 行再接实时）：

```bash
docker compose -f docker-compose.dev.yml logs -f --tail=100 frontend
docker compose -f docker-compose.dev.yml logs -f --tail=100 backend
```

在 **Windows PowerShell** 且当前目录已是项目根时，可新开一个窗口专门跟前端（本窗口再跑上面的后端命令即可）：

```powershell
Start-Process powershell -WorkingDirectory (Get-Location).Path -ArgumentList '-NoExit', '-NoProfile', '-Command', 'docker compose -f docker-compose.dev.yml logs -f frontend'
```

```bash
# 首次或 Dockerfile 变更后：构建并后台启动全部服务
docker compose -f docker-compose.dev.yml up -d --build

# 仅后台启动（镜像已存在）
docker compose -f docker-compose.dev.yml up -d

# 前台启动（所有服务日志打在终端，Ctrl+C 停止）
docker compose -f docker-compose.dev.yml up

# 查看容器与端口映射
docker compose -f docker-compose.dev.yml ps

# 停止并删除容器（默认保留命名卷，如 redis-data、celerybeat-data）
docker compose -f docker-compose.dev.yml down

# 停止并删容器且删卷（Redis / Celery Beat 持久化数据会清空，慎用）
docker compose -f docker-compose.dev.yml down -v

# 跟日志（单服务，-f 表示 follow，持续实时输出；不加 -f 只会打印已有历史后退出）
docker compose -f docker-compose.dev.yml logs -f frontend
docker compose -f docker-compose.dev.yml logs -f backend

# 跟日志（多服务，同一终端里混在一起，每行前会有服务名前缀）
docker compose -f docker-compose.dev.yml logs -f backend celery_worker

# 仅重启某一服务（改环境变量或 compose 后常用）
docker compose -f docker-compose.dev.yml restart backend

# 进入容器 Shell（backend 一般为 sh；若镜像带 bash 可换 bash）
docker compose -f docker-compose.dev.yml exec backend sh
docker compose -f docker-compose.dev.yml exec frontend sh
```

### 通用

```bash
# 仅构建不启动
docker compose build

# 指定文件构建
docker compose -f docker-compose.dev.yml build

# 进入 compose 中的服务（示例：backend）
docker compose -f docker-compose.dev.yml exec backend sh
```

## 清理与排错

| 说明 | 命令 |
|------|------|
| 未使用镜像/容器/网络清理（慎用） | `docker system prune` |
| 连同未使用卷清理（更激进） | `docker system prune -a --volumes` |
| 端口被占用时 | 在 Windows 上检查占用：`netstat -ano | findstr :6379`，或改 compose 里 `ports` 映射 |

## 本仓库提示

- **本机已跑 Redis 且占用 6379** 时，`docker-compose.yml` 里 Redis 的 `6379:6379` 会冲突；可关本机 Redis、改宿主端口，或改用 `docker-compose.dev.yml`（Redis 仅暴露容器端口时由 Docker 分配宿主端口）。
- 开发调试常用 **`docker-compose.dev.yml`**（含 debugpy、前端 dev 端口等）。
