<!-- 
  @file 角色卡片组件
  @description 展示单个AI角色的信息卡片
-->
<template>
  <div class="role-card" @click="$emit('start-chat')" :class="{ loading }">
    <div class="skeleton" v-if="loading">
      <div class="skeleton-icon"></div>
      <div class="skeleton-content">
        <div class="skeleton-title"></div>
        <div class="skeleton-desc"></div>
        <div class="skeleton-tags"></div>
      </div>
    </div>
    <template v-else>
      <div class="role-action">
        <button class="start-chat-btn" @click="$emit('start-chat')">开始对话</button>
      </div>
      
      <!-- 主图标区域 -->
      <div class="role-main-icon">
        <!-- 原有的主图标 -->
        <div class="main-icon">
          <!-- 图片类型图标 -->
          <img 
            v-if="isImageUrl(icon)" 
            :src="icon" 
            :alt="title"
            @error="handleImageError"
            @load="handleImageLoad"
            :class="{ 'image-loading': imageLoading }"
            loading="lazy"
          >
          <!-- emoji或文本图标 -->
          <span v-else-if="icon" class="fallback-icon">{{ icon }}</span>
          <!-- 默认图标 -->
          <span v-else class="default-icon">{{ getFallbackIcon(title) }}</span>
        </div>
        
        <!-- 新图标书签 -->
        <div v-if="hasNewIcons" class="icon-badges">
          <div 
            v-for="(iconItem, index) in displayIcons" 
            :key="`badge-${index}`"
            class="icon-badge"
            :class="`badge-${iconItem.type}`"
            :title="getIconLabel(iconItem.type)"
          >
            <component :is="getIconComponent(iconItem.type)" class="badge-icon" />
          </div>
        </div>
      </div>
      
      <div>
        <h3 class="role-title">{{ title }}</h3>
        <p class="role-desc">{{ description }}</p>
      </div>
      <div class="role-tags">
        <span 
          v-for="tag in tags" 
          :key="tag" 
          class="role-tag"
        >
          {{ tag }}
        </span>
      </div>
      <div class="role-stats">
        <div class="stat-item">
          <span>✨</span>
          <span>评分: {{ rating }}</span>
        </div>
        <div class="stat-item">
          <span>📊</span>
          <span>已服务: {{ serviceCount }}次</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  Monitor, 
  VideoPlay, 
  Picture,
  Document,
  Present
} from '@element-plus/icons-vue'

interface RoleIcon {
  type: 'web' | 'video' | 'image' | 'pdf' | 'ppt' | 'default'
  icon: string
}

const props = defineProps<{
  id: number
  icon: string  // 保留向后兼容
  icons?: RoleIcon[]  // 新的多图标字段
  title: string
  description: string
  tags: string[]
  rating: number
  serviceCount: number
  category: string
  loading?: boolean
}>()

defineEmits(['start-chat'])

// 检查是否有新的图标数组
const hasNewIcons = computed(() => {
  return props.icons && props.icons.length > 0
})

// 处理显示的图标列表（仅用于新图标书签）
const displayIcons = computed(() => {
  if (hasNewIcons.value) {
    return props.icons!
  }
  return []
})

// 图标组件映射
const iconComponents = {
  web: Monitor,      // 网页图标
  video: VideoPlay,  // 视频图标  
  image: Picture,    // 图片图标
  pdf: Document,     // PDF图标
  ppt: Present,      // PPT图标
  default: Monitor   // 默认图标
}

// 获取图标组件
const getIconComponent = (type: string) => {
  return iconComponents[type as keyof typeof iconComponents] || Monitor
}

// 图标标签映射
const iconLabels = {
  web: '网页',
  video: '视频', 
  image: '图片',
  pdf: 'PDF',
  ppt: 'PPT',
  default: '默认'
}

// 获取图标标签
const getIconLabel = (type: string) => {
  return iconLabels[type as keyof typeof iconLabels] || '默认'
}

// 检查是否是图片URL
const isImageUrl = (url: string) => {
  if (!url) return false
  
  // 支持华为云 OBS URL
  const obsPattern = /^https?:\/\/[^/]+\.obs\.[^/]+\.(huaweicloud\.com|myhuaweicloud\.com)/
  // 支持常规图片 URL
  const imagePattern = /\.(jpg|jpeg|png|webp|avif|gif|svg|bmp|tiff)(\?.*)?$/i
  // 支持data URL
  const dataUrlPattern = /^data:image\//
  
  return obsPattern.test(url) || imagePattern.test(url) || dataUrlPattern.test(url)
}

// 获取备用图标（emoji）
const getFallbackIcon = (title: string) => {
  // 预设的emoji映射
  const emojiMap: Record<string, string> = {
    '全能创意助手': '🌐',
    '用户调研洞察策略专家': '🌐', 
    '房琪爆款短视频脚本': '🎬',
    '广告海报创意总监': '🖼️',
    // 通用映射
    '营销': '📢',
    '设计': '🎨',
    '写作': '✍️',
    '数据': '📊',
    '策划': '📋',
    '分析': '🔍',
    '创意': '💡',
    '技术': '💻',
    '视频': '🎬',
    '图片': '🖼️',
    '网页': '🌐',
    'HTML': '🌐',
    '海报': '🖼️'
  }

  // 尝试从标题中匹配emoji
  for (const [key, emoji] of Object.entries(emojiMap)) {
    if (title.includes(key)) {
      return emoji
    }
  }

  // 如果没有匹配的emoji，返回标题首字
  return title.charAt(0)
}

// 图片加载状态
const imageLoading = ref(true)

// 图片预加载函数
const preloadImage = (src: string): Promise<boolean> => {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => resolve(true)
    img.onerror = () => resolve(false)
    // 针对Edge浏览器，添加随机参数避免缓存问题
    img.src = navigator.userAgent.includes('Edg') && src.includes('obs.') 
      ? `${src}${src.includes('?') ? '&' : '?'}_t=${Date.now()}` 
      : src
  })
}

const handleImageLoad = () => {
  imageLoading.value = false
}

const handleImageError = (e: Event) => {
  const target = e.target as HTMLImageElement
  console.error('Image load failed:', target.src)
  imageLoading.value = false
  
  // Edge浏览器特殊处理：尝试重新加载一次
  if (navigator.userAgent.includes('Edg') && target.dataset.retryCount !== '1') {
    target.dataset.retryCount = '1'
    setTimeout(() => {
      target.src = target.src
    }, 1000)
  }
}
</script>

<style scoped>
.role-card {
  background: white;
  border-radius: 20px;
  padding: 32px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.role-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.1);
  border-color: rgba(59, 130, 246, 0.15);
}

.role-action {
  position: absolute;
  top: 24px;
  right: 24px;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  z-index: 10;
}

.role-card:hover .role-action {
  opacity: 1;
  pointer-events: auto;
}

.start-chat-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25);
  letter-spacing: 0.3px;
}

.start-chat-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
}

.role-main-icon {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  position: relative;
  width: 100%;
}

.main-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.15));
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  overflow: hidden;
  position: relative;
  margin-right: 12px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.main-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

.main-icon .fallback-icon,
.main-icon .default-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  font-size: 28px;
  color: #3b82f6;
}

.image-loading {
  opacity: 0.5;
  transition: opacity 0.3s;
}

/* 书签样式 */
.icon-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  flex: 1;
}

.icon-badge {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
}

.icon-badge .badge-icon {  
  font-size: 14px;
  color: white;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

/* 不同类型书签的颜色 */
.icon-badge.badge-web {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.icon-badge.badge-video {
  background: linear-gradient(135deg, #ec4899, #be185d);
}

.icon-badge.badge-image {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.icon-badge.badge-pdf {
  background: linear-gradient(135deg, #f97316, #ea580c);
}

.icon-badge.badge-ppt {
  background: linear-gradient(135deg, #eab308, #ca8a04);
}

.icon-badge.badge-default {
  background: linear-gradient(135deg, #64748b, #475569);
}

.icon-badge:hover {
  transform: translateY(-2px) scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.icon-badge:active {
  transform: translateY(-1px) scale(1.05);
  transition-duration: 0.1s;
}

/* 书签Tooltip和响应式优化 */
@media (max-width: 768px) {
  .role-card {
    padding: 28px;
    border-radius: 24px;
  }
  
  .main-icon {
    width: 56px;
    height: 56px;
    font-size: 28px;
    margin-right: 16px;
  }
  
  .icon-badge {
    width: 28px;
    height: 28px;
    gap: 5px;
  }
  
  .icon-badge .badge-icon {
    font-size: 14px;
  }
  
  .role-title {
    font-size: 22px;
  }
  
  .role-desc {
    font-size: 15px;
  }
}

/* 微妙的高光效果 */
.icon-badge::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), transparent 50%);
  border-radius: inherit;
  pointer-events: none;
}

.role-title {
  font-size: 22px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 12px;
  line-height: 1.3;
  letter-spacing: -0.2px;
}

.role-desc {
  font-size: 15px;
  line-height: 1.65;
  color: #6b7280;
  margin-bottom: 20px;
  min-height: 48px;
  font-weight: 400;
}

.role-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.role-tag {
  padding: 8px 16px;
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.08), rgba(33, 150, 243, 0.12));
  color: #1976d2;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(33, 150, 243, 0.15);
}

.role-tag:hover {
  background: linear-gradient(135deg, #2196f3, #1976d2);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.role-stats {
  display: flex;
  justify-content: space-between;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  margin-top: 4px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
}

.skeleton {
  width: 100%;
  height: 100%;
  display: flex;
  gap: 16px;
  padding: 20px;
}

.skeleton-icon {
  width: 48px;
  height: 48px;
  background: #f0f0f0;
  border-radius: 12px;
  animation: pulse 1.5s infinite;
}

.skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-title {
  height: 24px;
  width: 60%;
  background: #f0f0f0;
  border-radius: 4px;
  animation: pulse 1.5s infinite;
}

.skeleton-desc {
  height: 16px;
  width: 100%;
  background: #f0f0f0;
  border-radius: 4px;
  animation: pulse 1.5s infinite;
}

.skeleton-tags {
  display: flex;
  gap: 8px;
}

.skeleton-tags::before,
.skeleton-tags::after {
  content: '';
  height: 24px;
  width: 64px;
  background: #f0f0f0;
  border-radius: 12px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.image-loading {
  animation: imageLoading 1.5s infinite;
}
</style> 