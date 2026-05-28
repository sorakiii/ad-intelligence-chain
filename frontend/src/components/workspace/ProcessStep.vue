<!-- 
  @file 流程步骤组件
  @description 展示工作流程的步骤
-->
<template>
  <div class="process-step">
    <div class="step-number">{{ number }}</div>
    <div class="step-content">
      <div class="step-icon">{{ icon }}</div>
      <h3 class="step-title">{{ title }}</h3>
      <p class="step-desc">{{ description }}</p>
      <div class="step-details" v-if="details">
        <div 
          v-for="detail in details" 
          :key="detail.title"
          class="detail-item"
        >
          <span class="detail-icon">{{ detail.icon }}</span>
          <div class="detail-content">
            <h4 class="detail-title">{{ detail.title }}</h4>
            <p class="detail-desc">{{ detail.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  number: Number,
  icon: String,
  title: String,
  description: String,
  details: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.process-step {
  display: flex;
  gap: 24px;
  position: relative;
}

.step-number {
  width: 32px;
  height: 32px;
  background: var(--gradient-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
  padding: 24px;
  background: white;
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.step-icon {
  width: 40px;
  height: 40px;
  background: var(--bg-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-bottom: 16px;
}

.step-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.step-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 16px;
}

.step-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.detail-item {
  display: flex;
  gap: 12px;
}

.detail-icon {
  font-size: 16px;
  color: var(--primary-color);
}

.detail-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.detail-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

@media (max-width: 640px) {
  .process-step {
    flex-direction: column;
  }
  
  .step-number {
    margin-bottom: -16px;
    margin-left: 16px;
    z-index: 1;
  }
}
</style> 