# Docker构建问题修复指南

## 问题描述

在构建Docker镜像时遇到以下错误：

```
E: Unable to correct problems, you have held broken packages.
E: The following information from --solver 3.0 may provide additional context:
   Unable to satisfy dependencies. Reached two conflicting decisions:
   1. libglib2.0-0t64:amd64 is selected for removal because:
      1. libglib2.0-0:amd64=2.66.8-1+deb11u6 is selected for install
      2. libglib2.0-0t64:amd64 Breaks libglib2.0-0 (< 2.80.0-7~)
         [selected libglib2.0-0:amd64=2.66.8-1+deb11u6]
   2. libglib2.0-0t64:amd64 is selected for install because:
      1. libpango-1.0-0:amd64=1.56.3-1 Depends libglib2.0-0t64 (>= 2.80.0)
```

## 问题原因

这是由于Debian Bullseye (Debian 11) 中 `libglib2.0-0` 和 `libpango-1.0-0` 包版本不兼容导致的依赖冲突。

## 解决方案

### 方案1：修复现有Dockerfile（推荐）

已经修复了 `backend/Dockerfile`，主要改进：

1. **分步安装依赖**：避免一次性安装所有包导致的冲突
2. **指定兼容版本**：使用 `libpango-1.0-0=1.46.2-3` 和 `libglib2.0-0=2.66.8-1+deb11u6`
3. **优化安装顺序**：先安装基础依赖，再安装图形库
4. **版本锁定**：确保所有Pango相关包使用相同版本

### 方案2：使用Debian 12基础镜像

如果方案1失败，可以使用 `backend/Dockerfile.alternative`：

1. **更新基础镜像**：使用 Python 3.11 + Debian 12 (Bookworm)
2. **避免版本冲突**：Debian 12 中的包版本更加兼容

### 方案3：最小化依赖（移除WeasyPrint）

使用 `backend/Dockerfile.minimal`：

1. **移除复杂图形库**：不安装WeasyPrint相关依赖
2. **保留基础功能**：仅安装必要的系统依赖和Chromium
3. **快速构建**：避免所有依赖冲突问题

### 方案4：使用Ubuntu基础镜像

使用 `backend/Dockerfile.ubuntu`：

1. **切换基础系统**：从Debian切换到Ubuntu
2. **避免Debian冲突**：Ubuntu的包管理更加稳定
3. **保持完整功能**：支持WeasyPrint和Chromium

## 使用方法

### 自动修复（推荐）

运行PowerShell脚本：

```powershell
.\fix_docker_build.ps1
```

脚本会自动尝试所有4种方案，直到成功为止。

### 手动修复

1. **清理Docker资源**：
   ```bash
   docker-compose down --remove-orphans
   docker system prune -f
   ```

2. **尝试方案1**：
   ```bash
   docker-compose build --no-cache backend
   ```

3. **如果失败，尝试其他方案**：
   ```bash
   # 方案2：Debian 12
   cp backend/Dockerfile backend/Dockerfile.backup
   cp backend/Dockerfile.alternative backend/Dockerfile
   docker-compose build --no-cache backend
   
   # 方案3：最小化
   cp backend/Dockerfile.minimal backend/Dockerfile
   docker-compose build --no-cache backend
   
   # 方案4：Ubuntu
   cp backend/Dockerfile.ubuntu backend/Dockerfile
   docker-compose build --no-cache backend
   ```

## 技术细节

### 依赖冲突分析

- **libglib2.0-0**: 2.66.8-1+deb11u6 (Debian 11)
- **libpango-1.0-0**: 1.56.3-1 需要 libglib2.0-0t64 (>= 2.80.0)
- **libpangocairo-1.0-0**: 需要与libpango-1.0-0版本一致
- **冲突原因**: 版本不兼容，Debian 11 的 libglib2.0-0 版本过低

### 修复策略

1. **版本锁定**：指定兼容的包版本组合
2. **分步安装**：避免依赖解析器同时处理冲突的包
3. **镜像升级**：使用更新的Debian版本
4. **系统切换**：从Debian切换到Ubuntu
5. **依赖简化**：移除不必要的复杂依赖

## 验证修复

构建成功后，检查服务状态：

```bash
docker-compose ps
docker-compose logs backend
```

## 注意事项

1. **备份原始文件**：修复脚本会自动备份原始Dockerfile
2. **网络环境**：确保能访问中国科技大学镜像源
3. **系统资源**：构建过程需要足够的磁盘空间和内存
4. **Docker版本**：建议使用 Docker 20.10+ 和 docker-compose 2.0+
5. **功能影响**：方案3会移除WeasyPrint支持

## 常见问题

### Q: 修复后仍然失败？
A: 脚本会自动尝试4种方案，如果都失败，检查网络连接和Docker版本

### Q: 如何回滚到原始版本？
A: 运行 `cp backend/Dockerfile.backup backend/Dockerfile`

### Q: 可以跳过某些依赖吗？
A: 方案3会移除WeasyPrint，但保留Chromium功能

### Q: Ubuntu方案有什么优势？
A: Ubuntu的包管理更稳定，依赖冲突较少

### Q: 哪种方案最适合生产环境？
A: 推荐方案1或方案4，它们保持完整功能且稳定性较好 