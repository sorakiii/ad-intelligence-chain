<!-- 
  @file 主布局组件
  @description 包含导航栏和侧边栏的主布局
-->
<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-left">
        <div class="brand" @click="handleBrandClick">AI广告智链</div>
        <div class="nav-menu">
          <router-link
            to="/workspace/single-role"
            :class="{
              active:
                currentPath.startsWith('/workspace') &&
                !currentPath.includes('/statistics'),
            }"
            >工作台</router-link
          >
          <router-link
            v-if="isAdmin"
            to="/workspace/statistics"
            class="nav-item-with-badge"
            :class="{ active: currentPath.includes('/statistics') }"
          >
            <span
              class="nav-link"
              :class="{ active: currentPath.includes('/statistics') }"
              >数据分析</span
            >
          </router-link>
          <div class="nav-item-with-badge">
            <span class="nav-link disabled">资源中心</span>
            <span class="dev-badge">开发中</span>
          </div>
          <router-link
            to="/settings"
            :class="{ active: currentPath.includes('/settings') }"
            >系统设置</router-link
          >
        </div>
      </div>
      <div class="header-right">
        <el-dropdown>
          <span class="user-info">
            <span class="icon">🏠</span>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleLogout">
                <img
                  src="@/assets/icons/out.svg"
                  class="logout-icon"
                  alt="退出登录"
                />
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 侧边栏 -->
      <div class="sidebar" :class="{ collapsed: isCollapsed }">
        <template v-if="!isCollapsed">
          <!-- 侧边栏切换按钮 - 展开状态 -->
          <div class="sidebar-header">
            <div class="sidebar-header-title">导航菜单</div>
            <div class="sidebar-toggle-fixed" @click="toggleSidebar">
              <el-icon :size="16"><ArrowLeft /></el-icon>
            </div>
          </div>

          <div class="sidebar-section">
            <div class="sidebar-title">项目类型</div>
            <ul class="sidebar-menu">
              <li
                :class="{ active: currentPath === '/workspace/single-role' }"
                @click="switchContent('/workspace/single-role')"
              >
                单角色服务
              </li>
              <li class="menu-item-with-badge">
                <span>定向需求服务</span>
                <span class="dev-badge-small">开发中</span>
              </li>
              <li class="menu-item-with-badge">
                <span>超级战队服务</span>
                <span class="dev-badge-small">开发中</span>
              </li>
            </ul>
          </div>

          <div class="sidebar-section">
            <div class="sidebar-title">历史记录</div>
            <ul class="sidebar-menu">
              <li
                :class="{
                  active:
                    currentPath === '/workspace/history/single-role' ||
                    (route.name === 'chatDetail' &&
                      route.params.type === 'single-role'),
                }"
                @click="switchContent('/workspace/history/single-role')"
              >
                单角色会话
              </li>
              <li class="menu-item-with-badge">
                <span>定向需求会话</span>
                <span class="dev-badge-small">开发中</span>
              </li>
              <li class="menu-item-with-badge">
                <span>超级战队会话</span>
                <span class="dev-badge-small">开发中</span>
              </li>
            </ul>
          </div>

          <div class="sidebar-section">
            <div class="sidebar-title">最近打开</div>
            <ul class="sidebar-menu recent-sessions">
              <li v-if="recentSessions.length === 0" class="empty-state">
                暂无最近会话
              </li>
              <li
                v-else
                v-for="session in recentSessions"
                :key="session.id"
                class="session-item"
                @click="openSession(session)"
              >
                <div class="session-info">
                  <div class="session-header">
                    <span class="session-title">{{ session.title }}</span>
                    <span class="session-type">{{
                      session.type === "single_role"
                        ? "单角色会话"
                        : session.type === "targeted"
                        ? "定向需求会话"
                        : "超级战队会话"
                    }}</span>
                  </div>
                  <div class="session-meta">
                    <span class="session-time">{{
                      formatTime(session.last_time)
                    }}</span>
                  </div>
                  <div class="session-message">{{ session.last_message }}</div>
                </div>
              </li>
            </ul>
          </div>
        </template>
        <div v-else class="sidebar-collapsed-menu">
          <!-- 侧边栏切换按钮 - 收起状态 -->
          <div class="sidebar-toggle-fixed collapsed" @click="toggleSidebar">
            <el-icon :size="16"><ArrowRight /></el-icon>
          </div>

          <div
            class="sidebar-section-icon"
            @click="switchContent('/workspace/single-role')"
            :class="{ active: currentPath === '/workspace/single-role' }"
          >
            <el-icon :size="20"><Operation /></el-icon>
            <div class="icon-tooltip">项目类型</div>
          </div>
          <div
            class="sidebar-section-icon"
            @click="switchContent('/workspace/history/single-role')"
            :class="{
              active: currentPath === '/workspace/history/single-role',
            }"
          >
            <el-icon :size="20"><Document /></el-icon>
            <div class="icon-tooltip">历史记录</div>
          </div>
          <div
            class="sidebar-section-icon"
            @click="switchContent('/workspace/history/recent')"
            :class="{ active: currentPath === '/workspace/history/recent' }"
          >
            <el-icon :size="20"><Clock /></el-icon>
            <div class="icon-tooltip">最近打开</div>
          </div>
        </div>
      </div>

      <div class="workspace" :class="{ expanded: isCollapsed }">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Operation,
  Document,
  Clock,
  ArrowRight,
  ArrowLeft,
} from "@element-plus/icons-vue";
import { getRecentSessions } from "@/api/chat";
import { useUserStore } from "@/stores/user";
import { formatTime } from "@/utils/time";
const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const isCollapsed = ref(false);
const showRecentPanel = ref(false);
const recentSessions = ref([]);
const isAdmin = computed(() => userStore.checkAdminPermission);
// 计算当前路径
const currentPath = computed(() => route.path);

// 切换侧边栏状态
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

// 切换内容
const switchContent = (path) => {
  router.push(path);
};

// 处理品牌点击
const handleBrandClick = () => {
  router.push("/?allowReturn=false");
};

// 处理登出
const handleLogout = async () => {
  try {
    await userStore.logout();
    ElMessage.success("退出成功");
    router.push("/login");
  } catch (error) {
    console.error("退出失败:", error);
    ElMessage.error("退出失败");
  }
};

// 加载最近会话
const loadRecentSessions = async () => {
  try {
    const response = await getRecentSessions(5); // 限制获取5条
    if (response.data) {
      recentSessions.value = response.data.sessions;
    }
  } catch (error) {
    console.error("获取最近会话失败:", error);
  }
};

// 打开会话
const openSession = (session) => {
  router.push({
    name: "chatDetail",
    params: {
      type: session.type,
      sessionId: session.id,
    },
  });
};

onMounted(async () => {
  await userStore.checkAdminPermission();
  await userStore.checkLoginStatus();
  const canUse = await userStore.checkUserPermission();
  if (!canUse) {
    // 不能使用
    ElMessage.warning("没有权限或已过期");
    router.push("/?allowReturn=false");
  }
  await loadRecentSessions();
});
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  background: var(--bg-color);
  max-width: 100vw;
  margin: 0 auto;
  font-size: 14px;
  display: flex;
  flex-direction: column;
}

.header {
  height: 60px;
  background: white;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.brand {
  font-size: 24px;
  font-weight: bold;
  color: #4e6ef2;
  margin-right: 20px;
  cursor: pointer;
  user-select: none;
  transition: opacity 0.3s;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}

.brand:hover {
  opacity: 0.8;
}

.nav-menu {
  display: flex;
  gap: 32px;
  align-items: center;
}

.nav-item-with-badge {
  position: relative;
  display: inline-flex;
  align-items: center;
  opacity: 0.8;
}

.nav-item-with-badge:hover .nav-link.disabled {
  background: var(--bg-color);
  color: var(--text-secondary);
  cursor: not-allowed;
}

.dev-badge {
  position: absolute;
  top: -8px;
  right: -20px;
  background: linear-gradient(45deg, #ff9a9e, #fad0c4);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(255, 154, 158, 0.2);
  animation: pulse 2s infinite;
}

.dev-badge-small {
  background: linear-gradient(45deg, #ff9a9e, #fad0c4);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  margin-left: 8px;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(255, 154, 158, 0.2);
  animation: pulse 2s infinite;
}

.menu-item-with-badge {
  display: flex;
  align-items: center;
  justify-content: space-between;
  opacity: 0.8;
  cursor: not-allowed !important;
}

.menu-item-with-badge:hover {
  background: var(--bg-color) !important;
  color: var(--text-primary) !important;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s ease;
  padding: 8px 16px;
  border-radius: 6px;
  position: relative;
}

.nav-link.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: var(--bg-color);
}

/* 顶部导航菜单激活状态 */
.nav-menu a:hover,
.nav-menu a.active,
.nav-menu .nav-item-with-badge.active .nav-link {
  color: var(--primary-color);
  font-weight: 700;
}

/* 统一默认状态下的字体样式 */
.nav-menu a,
.nav-menu .nav-item-with-badge .nav-link {
  color: #909399;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s ease;
  padding: 8px 16px;
  border-radius: 6px;
  position: relative;
  font-weight: 400;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}

.nav-item-with-badge a {
  margin-right: 24px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.notification {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  transition: background-color 0.2s ease;
  margin-bottom: 2px;
}

.notification:hover {
  background: var(--bg-color);
}

.icon {
  font-size: 20px;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  transition: background-color 0.2s ease;
  margin-bottom: 2px;
}

.user-info:hover {
  background: var(--bg-color);
}

.user-info .icon {
  border: none;
  outline: none;
}

:deep(.el-dropdown) {
  border: none !important;
  outline: none !important;
}

:deep(.el-dropdown:focus-visible) {
  outline: none !important;
  box-shadow: none !important;
}

:deep(.el-dropdown__popper) {
  border: none !important;
  outline: none !important;
}

:deep(.el-popper) {
  border: none !important;
  outline: none !important;
}

.main-content {
  margin-top: 60px;
  padding: 24px;
  display: flex;
  gap: 24px;
  height: calc(100vh - 60px);
  overflow: hidden;
  position: relative;
}

/* 侧边栏头部 */
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 4px;
}

.sidebar-header-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}

/* 固定的侧边栏切换按钮 */
.sidebar-toggle-fixed {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: var(--bg-color);
  transition: all 0.2s ease;
}

.sidebar-toggle-fixed:hover {
  background: rgba(0, 102, 255, 0.05);
  color: var(--primary-color);
}

.sidebar-toggle-fixed.collapsed {
  margin-bottom: 24px;
  background: var(--bg-color);
  border-radius: 4px;
  width: 40px;
  height: 40px;
}

/* 左侧边栏 */
.sidebar {
  width: 280px;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  height: calc(100vh - 108px);
  display: flex;
  flex-direction: column;
  gap: 32px;
  transition: all 0.3s ease;
  flex-shrink: 0;
  position: relative;
}

.sidebar.collapsed {
  width: 56px;
  padding: 20px 8px;
  overflow: visible;
}

.sidebar-collapsed-menu {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  position: relative;
  z-index: 5; /* 确保基础容器有合适的层级 */
}

.sidebar-section-icon {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;
  z-index: 10; /* 添加较高的 z-index */
}

.sidebar-section-icon:hover,
.sidebar-section-icon.active {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.recent-sessions-collapsed {
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 1000;
  margin-left: 8px;
}

.recent-session-item-collapsed {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.recent-session-item-collapsed:hover {
  background: var(--el-color-primary-light-7);
  transform: translateX(2px);
}

/* 添加小箭头 */
.recent-sessions-collapsed::before {
  content: "";
  position: absolute;
  left: -6px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  border-right: 6px solid white;
}

.icon-tooltip {
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  margin-left: 8px;
  pointer-events: none;
  z-index: 20; /* 确保 tooltip 在最上层 */
}

.sidebar-section-icon:hover .icon-tooltip {
  opacity: 1;
  visibility: visible;
}

/* 当显示最近会话时隐藏tooltip */
.sidebar-section-icon:hover .recent-sessions-collapsed + .icon-tooltip {
  opacity: 0;
  visibility: hidden;
}

.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
}

.sidebar-section:not(:last-child)::after {
  content: "";
  position: absolute;
  bottom: -20px;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--border-color);
}

.sidebar-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  padding: 0 12px;
  margin-bottom: 4px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}

.sidebar-menu {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0 4px;
}

.sidebar-menu li {
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
  color: #909399;
  background: var(--bg-color);
  font-weight: 400;
}

.sidebar-menu li:hover {
  background: rgba(0, 102, 255, 0.05);
  color: var(--primary-color);
  font-weight: 400;
}

.sidebar-menu li.active {
  background: var(--primary-color);
  color: white;
  font-weight: 700;
}

/* 主要工作区 */
.workspace {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  min-width: 0;
  overflow: auto;
  height: calc(100vh - 108px);
  transition: all 0.3s ease;
}

.workspace.expanded {
  width: calc(100% - 56px - 24px);
}

/* 最近会话样式 */
.recent-sessions li {
  padding: 16px;
  border-radius: 8px;
  transition: all 0.2s ease;
  background: var(--bg-color);
  margin-bottom: 12px;
  border: 1px solid var(--border-color);
}

.recent-sessions li:hover {
  background: rgba(0, 102, 255, 0.05);
  border-color: var(--primary-color);
}

.session-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.session-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.session-type {
  font-size: 12px;
  color: var(--text-secondary);
  background: white;
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.session-meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.session-time {
  color: #999;
}

.session-message {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5;
}

/* 响应式布局 */
@media screen and (min-width: 1920px) {
  .main-layout {
    max-width: 1920px;
  }

  .sidebar {
    width: 320px;
  }

  .sidebar.collapsed {
    width: 56px;
  }

  .sidebar-toggle {
    right: -12px;
  }

  .sidebar-header-title {
    font-size: 16px;
  }
}

@media screen and (max-width: 1366px) {
  .main-content {
    padding: 16px;
    gap: 16px;
  }

  .sidebar {
    width: 260px;
    padding: 20px;
    gap: 32px;
  }

  .sidebar.collapsed {
    width: 56px;
    padding: 24px 8px;
  }

  .sidebar-toggle {
    right: -12px;
  }

  .sidebar-section:not(:last-child)::after {
    bottom: -16px;
  }

  .sidebar-header-title {
    font-size: 14px;
  }

  .workspace {
    padding: 20px;
  }
}

.empty-state {
  text-align: center;
  color: var(--el-text-color-secondary);
  padding: 16px;
  font-size: 14px;
}

.session-item {
  cursor: pointer;
  padding: 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.session-item:hover {
  background: var(--el-fill-color-light);
}

.logout-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  vertical-align: middle;
}

/* 确保所有导航文字使用相同的字体系列 */
.nav-menu a,
.nav-menu .nav-item-with-badge .nav-link,
.sidebar-menu li,
.sidebar-title,
.sidebar-header-title {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}

/* 确保其他文本元素也保持一致的字体样式 */
.brand {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}
</style> 
