<template>
  <div class="slider-captcha">
    <!-- 验证码图片区域 -->
    <div class="captcha-image-container" ref="imageContainer">
      <img 
        :src="captchaImage" 
        alt="验证码" 
        class="captcha-image"
        @load="onImageLoad"
      />
      
      <!-- 滑块拼图 -->
      <div 
        class="slider-puzzle" 
        :style="{ 
          left: `${sliderLeft}px`, 
          top: `${puzzleY}px`,
          backgroundImage: `url(${captchaImage})`,
          backgroundPosition: `-${targetX}px -${puzzleY}px`
        }"
      ></div>
      
      <!-- 目标位置指示 -->
      <div 
        class="target-position" 
        :style="{ 
          left: `${targetX}px`, 
          top: `${puzzleY}px` 
        }"
      ></div>
    </div>
    
    <!-- 滑块区域 -->
    <div class="slider-container">
      <div 
        class="slider-track"
        :class="{ 'success': verified, 'error': failed }"
      >
        <div 
          class="slider-button"
          ref="sliderButton"
          :style="{ left: `${sliderLeft}px` }"
          @mousedown="startDrag"
          @touchstart="startDrag"
          :class="{ 
            'success': verified, 
            'error': failed,
            'dragging': isDragging 
          }"
        >
          <i class="el-icon-arrow-right" v-if="!verified && !failed"></i>
          <i class="el-icon-check" v-if="verified"></i>
          <i class="el-icon-close" v-if="failed"></i>
        </div>
        <div class="slider-text" v-if="!isDragging && !verified">
          向右滑动完成验证
        </div>
      </div>
    </div>
    
    <!-- 刷新按钮 -->
    <div class="refresh-button" @click="refreshCaptcha">
      <i class="el-icon-refresh"></i>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'

const props = defineProps({
  // 验证码图片URL
  imageUrl: {
    type: String,
    default: '/captcha-placeholder.svg'
  },
  // 验证误差范围（像素）
  tolerance: {
    type: Number,
    default: 5
  }
})

const emit = defineEmits(['verified', 'failed', 'refresh'])

// 状态变量
const imageContainer = ref(null)
const sliderButton = ref(null)
const isDragging = ref(false)
const sliderLeft = ref(0)
const startX = ref(0)
const maxLeft = ref(0)
const verified = ref(false)
const failed = ref(false)
const targetX = ref(0)
const puzzleY = ref(0)
const puzzleSize = 40 // 拼图大小

// 计算属性
const captchaImage = computed(() => props.imageUrl)

// 图片加载完成后初始化
const onImageLoad = () => {
  if (!imageContainer.value) return
  
  const containerWidth = imageContainer.value.clientWidth
  maxLeft.value = containerWidth - puzzleSize
  
  // 随机生成目标位置
  targetX.value = Math.floor(Math.random() * (maxLeft.value - 50)) + 50
  puzzleY.value = Math.floor(Math.random() * (imageContainer.value.clientHeight - puzzleSize))
}

// 开始拖动
const startDrag = (e) => {
  if (verified.value) return
  
  isDragging.value = true
  failed.value = false
  
  // 记录起始位置
  startX.value = e.type === 'mousedown' ? e.clientX : e.touches[0].clientX
  
  // 添加移动和结束事件监听
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  document.addEventListener('touchmove', onDrag)
  document.addEventListener('touchend', stopDrag)
  
  // 阻止默认行为和冒泡
  e.preventDefault()
  e.stopPropagation()
}

// 拖动中
const onDrag = (e) => {
  if (!isDragging.value) return
  
  // 计算移动距离
  const currentX = e.type === 'mousemove' ? e.clientX : e.touches[0].clientX
  let moveX = currentX - startX.value
  
  // 限制在有效范围内
  let newLeft = Math.max(0, Math.min(moveX, maxLeft.value))
  sliderLeft.value = newLeft
  
  // 阻止默认行为
  e.preventDefault()
}

// 停止拖动
const stopDrag = () => {
  if (!isDragging.value) return
  
  isDragging.value = false
  
  // 移除事件监听
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
  
  // 验证位置
  verifyPosition()
}

// 验证位置是否正确
const verifyPosition = () => {
  const diff = Math.abs(sliderLeft.value - targetX.value)
  
  if (diff <= props.tolerance) {
    // 验证成功
    verified.value = true
    emit('verified', true)
  } else {
    // 验证失败
    failed.value = true
    emit('verified', false)
    
    // 失败动画后重置
    setTimeout(() => {
      sliderLeft.value = 0
      failed.value = false
    }, 1000)
  }
}

// 刷新验证码
const refreshCaptcha = () => {
  sliderLeft.value = 0
  verified.value = false
  failed.value = false
  
  // 重新生成目标位置
  if (imageContainer.value) {
    targetX.value = Math.floor(Math.random() * (maxLeft.value - 50)) + 50
    puzzleY.value = Math.floor(Math.random() * (imageContainer.value.clientHeight - puzzleSize))
  }
  
  emit('refresh')
}

// 组件卸载时清理事件监听
onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
})

// 组件挂载时初始化
onMounted(() => {
  // 如果图片已加载，初始化目标位置
  if (imageContainer.value) {
    onImageLoad()
  }
})

// 暴露方法给父组件
defineExpose({
  refresh: refreshCaptcha,
  isVerified: () => verified.value
})
</script>

<style scoped>
.slider-captcha {
  width: 100%;
  max-width: 320px;
  margin: 0 auto;
  position: relative;
}

.captcha-image-container {
  width: 100%;
  height: 160px;
  position: relative;
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.captcha-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.slider-puzzle {
  position: absolute;
  width: 40px;
  height: 40px;
  background-size: cover;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  z-index: 2;
}

.target-position {
  position: absolute;
  width: 40px;
  height: 40px;
  border: 2px dashed rgba(255, 255, 255, 0.8);
  border-radius: 4px;
  z-index: 1;
}

.slider-container {
  margin-top: 16px;
  width: 100%;
  height: 40px;
}

.slider-track {
  width: 100%;
  height: 40px;
  background-color: #f5f5f5;
  border-radius: 20px;
  position: relative;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s;
}

.slider-track.success {
  background-color: #67c23a;
}

.slider-track.error {
  background-color: #f56c6c;
}

.slider-button {
  width: 40px;
  height: 40px;
  background-color: #fff;
  border-radius: 50%;
  position: absolute;
  top: 0;
  left: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  transition: all 0.3s;
  z-index: 3;
}

.slider-button.dragging {
  transform: scale(1.1);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.slider-button.success {
  background-color: #67c23a;
  color: white;
}

.slider-button.error {
  background-color: #f56c6c;
  color: white;
}

.slider-text {
  position: absolute;
  width: 100%;
  text-align: center;
  line-height: 40px;
  color: #999;
  font-size: 14px;
  user-select: none;
}

.refresh-button {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 30px;
  height: 30px;
  background-color: rgba(0, 0, 0, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  z-index: 4;
  transition: all 0.3s;
}

.refresh-button:hover {
  background-color: rgba(0, 0, 0, 0.5);
  transform: rotate(180deg);
}
</style> 