<template>
  <div class="feature-card">
    <div class="feature-icon">{{ icon }}</div>
    <h3 class="feature-title">{{ title }}</h3>
    <p class="feature-desc">{{ description }}</p>
    <div class="feature-stats">
      <div v-for="(stat, index) in stats" :key="index" class="stat-item">
        <div class="stat-icon">{{ stat.icon }}</div>
        <span class="stat-text">{{ stat.text }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  icon: String,
  title: String,
  description: String,
  stats: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.feature-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  transform-origin: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid var(--border-color);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--gradient-primary);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  border-color: var(--primary-color);
}

.feature-card:hover::before {
  opacity: 1;
}

.feature-icon {
  width: 48px;
  height: 48px;
  background: rgba(0, 102, 255, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 16px;
  position: relative;
  transition: all 0.3s ease;
}

.feature-icon::after {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 12px;
  border: 1px solid var(--primary-color);
  opacity: 0.2;
}

.feature-card:hover .feature-icon {
  transform: scale(1.1);
  background: var(--gradient-primary);
  color: white;
}

.feature-title {
  font-size: 18px;
  margin-bottom: 8px;
}

.feature-desc {
  color: var(--text-secondary);
  margin-bottom: 16px;
  line-height: 1.6;
}

.feature-stats {
  display: flex;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-icon {
  font-size: 16px;
}

.stat-text {
  color: var(--text-secondary);
  font-size: 14px;
}
</style> 