<!-- 
  @file 顶部导航栏组件
  @description 工作区顶部导航栏,包含面包屑、搜索和用户信息
-->
<template>
  <nav class="top-nav">
    <div class="nav-left">
      <div class="breadcrumb">
        <span 
          v-for="(item, index) in breadcrumbs" 
          :key="index"
          class="breadcrumb-item"
        >
          {{ item }}
          <span v-if="index < breadcrumbs.length - 1" class="separator">/</span>
        </span>
      </div>
    </div>

    <div class="nav-center">
      <div class="search-bar">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          placeholder="搜索项目、服务或帮助..."
          v-model="searchQuery"
        >
      </div>
    </div>

    <div class="nav-right">
      <div class="nav-item">
        <span class="icon">🔔</span>
        <span class="badge">2</span>
      </div>
      <div class="nav-item">
        <span class="icon">💬</span>
      </div>
      <div class="user-info">
        <img 
          src="@/assets/avatar.png" 
          alt="用户头像"
          class="avatar"
        >
        <span class="username">张三</span>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const searchQuery = ref('')

// 根据路由生成面包屑
const breadcrumbs = computed(() => {
  const paths = route.path.split('/').filter(Boolean)
  return ['工作台', ...paths.map(path => {
    // 将路径转换为显示名称
    const nameMap = {
      'workspace': '工作区',
      'super-team': '超级战队服务',
      'single-role': '单角色服务',
      'targeted-service': '定向需求服务',
      'history': '历史记录'
    }
    return nameMap[path] || path
  })]
})
</script>

<style scoped>
.top-nav {
  height: 64px;
  background: white;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-left {
  min-width: 200px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.breadcrumb-item:last-child {
  color: var(--text-primary);
  font-weight: 500;
}

.separator {
  color: var(--border-color);
}

.nav-center {
  flex: 1;
  max-width: 600px;
  margin: 0 40px;
}

.search-bar {
  position: relative;
  width: 100%;
}

.search-bar input {
  width: 100%;
  height: 40px;
  padding: 8px 16px 8px 40px;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  font-size: 14px;
  background: var(--bg-color);
  transition: all 0.2s ease;
}

.search-bar input:focus {
  outline: none;
  border-color: var(--primary-color);
  background: white;
  box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1);
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 16px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-item {
  position: relative;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: var(--bg-color);
}

.icon {
  font-size: 18px;
}

.badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background: #ff4d4f;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
  border: 2px solid white;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 20px;
  transition: all 0.2s ease;
}

.user-info:hover {
  background: var(--bg-color);
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.username {
  font-size: 14px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .nav-center {
    display: none;
  }
  
  .nav-item {
    display: none;
  }
  
  .username {
    display: none;
  }
}
</style> 