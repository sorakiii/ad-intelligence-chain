<template>
  <header class="app-header">
    <div class="header-left">
      <div class="logo" @click="handleLogoClick">AI广告智链</div>
    </div>
    
    <div class="header-right">
      <template v-if="userStore.isLoggedIn">
        <el-dropdown trigger="click">
          <div class="user-info">
            <el-avatar :size="32" :src="userStore.avatar">
              {{ userStore.nickname?.charAt(0) }}
            </el-avatar>
            <span class="username">{{ userStore.nickname }}</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
      <template v-else>
        <el-button type="text" @click="$router.push('/login')">登录</el-button>
        <el-button type="primary" @click="$router.push('/register')">注册</el-button>
      </template>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const handleLogoClick = () => {
  // 如果当前已经在 Landing 页面，不做任何操作
  if (router.currentRoute.value.path === '/') {
    return
  }
  
  // 如果用户已登录，提示是否确认退出工作区
  if (userStore.isLoggedIn) {
    ElMessageBox.confirm(
      '确定要退出工作区返回首页吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      // 用户确认后跳转到 Landing 页面
      router.push('/')
    }).catch(() => {
      // 用户取消，不做任何操作
    })
  } else {
    // 未登录状态直接跳转
    router.push('/')
  }
}

const handleLogout = async () => {
  try {
    await userStore.logout()
    ElMessage.success('退出成功')
    router.push('/login')
  } catch (error) {
    console.error('退出失败:', error)
    ElMessage.error('退出失败')
  }
}
</script>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #eee;
  position: relative;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: var(--primary-color);
  cursor: pointer;
  user-select: none;
  transition: opacity 0.3s;
}

.logo:hover {
  opacity: 0.8;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7f9;
}

.username {
  font-size: 14px;
  color: #333;
}

:deep(.el-dropdown-menu__item) {
  padding: 8px 20px;
}
</style> 