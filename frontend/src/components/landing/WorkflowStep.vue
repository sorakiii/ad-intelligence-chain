<template>
  <div class="step">
    <div class="step-number">{{ number }}</div>
    <h3 class="step-title">{{ title }}</h3>
    <p class="step-desc">{{ description }}</p>
  </div>
</template>

<script setup>
defineProps({
  number: Number,
  title: String,
  description: String
})
</script>

<style scoped>
.step {
  text-align: center;
  position: relative;
  z-index: 1;
  transform: translateY(0);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.step-number {
  width: 64px;
  height: 64px;
  background: var(--gradient-light);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  color: var(--primary-color);
  margin: 0 auto 24px;
  position: relative;
}

.step-number::before {
  content: '';
  position: absolute;
  inset: -2px;
  background: var(--gradient-primary);
  border-radius: 50%;
  z-index: -1;
}

.step-title {
  font-size: 18px;
  margin-bottom: 8px;
}

.step-desc {
  color: var(--text-secondary);
  font-size: 14px;
  max-width: 250px;
  margin: 0 auto;
  line-height: 1.6;
}
</style> 