<template>
  <div class="animated-number-container">
    <span class="animated-number" :class="{ flash: isFlashing }">{{
      displayValue
    }}</span>
    <div v-if="showProgress" class="progress-bar-bg">
      <div class="progress-bar-fg" :style="{ width: progress + '%' }"></div>
    </div>
    <i
      v-if="icon"
      :class="['animated-icon', icon, { 'icon-animate': isFlashing }]"
    ></i>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";

/**
 * @typedef {Object} Props
 * @property {number} value - 目标数字
 * @property {number} [duration=1000] - 动画时长（毫秒）
 * @property {function} [formatter] - 格式化函数
 */

/** @type {Props} */
const props = defineProps({
  value: { type: Number, required: true },
  duration: { type: Number, default: 1000 },
  formatter: { type: Function, default: (v) => Math.round(v) },
  progress: { type: Number, default: 0 },
  icon: { type: String, default: null },
  showProgress: { type: Boolean, default: false },
});

const displayValue = ref(props.formatter(props.value));
let startValue = props.value;
let startTime = null;
let animationFrame = null;
const isFlashing = ref(false);

const animate = (timestamp) => {
  if (!startTime) startTime = timestamp;
  const progress = Math.min((timestamp - startTime) / props.duration, 1);
  displayValue.value = props.formatter(
    startValue + (props.value - startValue) * progress
  );
  if (progress < 1) {
    animationFrame = requestAnimationFrame(animate);
  } else {
    displayValue.value = props.formatter(props.value);
    startValue = props.value;
    startTime = null;
    isFlashing.value = false;
  }
};

watch(
  () => props.value,
  (newVal, oldVal) => {
    startValue = oldVal;
    startTime = null;
    isFlashing.value = true;
    cancelAnimationFrame(animationFrame);
    animationFrame = requestAnimationFrame(animate);
  }
);

onMounted(() => {
  displayValue.value = props.formatter(props.value);
});
</script>

<style scoped>
.animated-number {
  font-size: 2rem;
  font-weight: bold;
  color: #3a8dff;
  transition: color 0.3s;
}
.animated-number.flash {
  animation: flash-glow 0.6s;
}
@keyframes flash-glow {
  0% {
    text-shadow: 0 0 8px #3a8dff, 0 0 16px #a0cfff;
  }
  100% {
    text-shadow: none;
  }
}
.progress-bar-bg {
  width: 100%;
  height: 4px;
  background: rgba(58, 141, 255, 0.1);
  border-radius: 2px;
  margin-top: 4px;
  overflow: hidden;
}
.progress-bar-fg {
  height: 100%;
  background: linear-gradient(90deg, #3a8dff, #a0cfff);
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.animated-icon {
  margin-left: 8px;
  color: #3a8dff;
  transition: transform 0.3s;
}
.icon-animate {
  animation: icon-bounce 0.6s;
}
@keyframes icon-bounce {
  0% {
    transform: scale(1);
  }
  30% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}
</style>