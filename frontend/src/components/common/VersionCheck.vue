<template>
  <div v-if="showUpdateNotification" class="version-update-notification">
    <div class="notification-content">
      <span>发现新版本，请清除缓存并刷新页面获取最新功能</span>
      <el-button type="primary" size="small" @click="clearCacheAndRefresh">清除缓存并刷新</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { BUILD_TIME } from '@/version.js'

const APP_VERSION = '1.0.0' // 当前应用版本号
const showUpdateNotification = ref(false)
let checkInterval = null

/**
 * 检查应用版本
 */
const checkVersion = async () => {
  try {
    // 使用相对路径，避免硬编码，强制跳过缓存
    // 添加时间戳参数确保获取最新版本
    const timestamp = Date.now()
    const response = await fetch(`./version.json?t=${timestamp}`, {
      cache: 'no-store',
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    
    if (response.ok) {
      const contentType = response.headers.get('content-type')
      if (contentType && contentType.includes('application/json')) {
        const serverVersion = await response.json()
        
        // 比较版本号和构建时间
        const isVersionDifferent = serverVersion.version !== APP_VERSION
        const isBuildTimeDifferent = serverVersion.build_date !== BUILD_TIME
        
        if (isVersionDifferent || isBuildTimeDifferent) {
          console.log('🔄 检测到新版本:', {
            current: { version: APP_VERSION, build_time: BUILD_TIME },
            server: { version: serverVersion.version, build_date: serverVersion.build_date }
          })
          
          // 显示更新通知
          showUpdateNotification.value = true
          
          // 在Docker环境中，可以添加额外的日志记录
          if (window.location.hostname !== 'localhost') {
            console.log('🐳 Docker环境检测到版本更新')
          }
        } else {
          console.log('✅ 当前已是最新版本')
        }
      } else {
        console.log('版本检查跳过：返回的不是JSON格式')
      }
    }
  } catch (error) {
    console.log('版本检查失败:', error)
  }
}

/**
 * 清除缓存并刷新
 */
const clearCacheAndRefresh = async () => {
  console.log('🧹 开始清除缓存...')
  
  // 立即隐藏弹窗
  showUpdateNotification.value = false
  
  try {
    // 清除浏览器缓存
    if ('caches' in window) {
      const cacheNames = await caches.keys()
      await Promise.all(
        cacheNames.map(cacheName => {
          console.log('🗑️ 清除缓存:', cacheName)
          return caches.delete(cacheName)
        })
      )
    }
    
    // 清除存储
    try {
      localStorage.clear()
      sessionStorage.clear()
      console.log('🗑️ 已清除localStorage和sessionStorage')
    } catch (error) {
      console.warn('存储清除失败:', error)
    }
    
    // 清除Service Worker缓存
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.ready
        if (registration.active) {
          await new Promise((resolve) => {
            const messageChannel = new MessageChannel()
            messageChannel.port1.onmessage = (event) => {
              resolve()
            }
            messageChannel.port1.onerror = () => resolve()
            
            registration.active.postMessage(
              { type: 'CLEAR_CACHE' },
              [messageChannel.port2]
            )
            
            // 1秒超时，更快响应
            setTimeout(resolve, 1000)
          })
        }
      } catch (error) {
        console.warn('Service Worker缓存清除失败:', error)
      }
    }
    
  } catch (error) {
    console.warn('缓存清除过程中出现错误:', error)
  }
  
  // 立即刷新页面
  console.log('🔄 强制刷新页面...')
  window.location.reload(true)
}

onMounted(() => {
  // 立即检查一次版本
  checkVersion()
  
  // 每2分钟检查一次版本（更频繁的检查）
  checkInterval = setInterval(checkVersion, 2 * 60 * 1000)
  
  // 页面获得焦点时检查版本
  window.addEventListener('focus', checkVersion)
  
  // 页面可见性变化时检查版本
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      checkVersion()
    }
  })
})

onUnmounted(() => {
  if (checkInterval) {
    clearInterval(checkInterval)
  }
  window.removeEventListener('focus', checkVersion)
  document.removeEventListener('visibilitychange', checkVersion)
})
</script>

<style scoped>
.version-update-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease-out;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style> 