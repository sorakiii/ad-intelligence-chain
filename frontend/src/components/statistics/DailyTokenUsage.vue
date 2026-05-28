<template>
  <div class="token-usage">
    <div class="chart-header">
      <div class="title-section">
        <h3>每日Token使用量</h3>
        <div class="pulse-dot"></div>
      </div>
    </div>

    <div class="chart-info" v-loading="loading">
      <div class="info-card">
        <div class="info-icon">
          <i class="el-icon-data-analysis"></i>
        </div>
        <div class="info-content">
          <span class="label">总Token消耗</span>
          <animated-number class="value" :value="usedToken" :duration="1000" />
        </div>
        <div class="trend-indicator positive">
          <i class="el-icon-top"></i>
          <span>{{ usedTokenPercentChange }}</span>
        </div>
      </div>
    </div>

    <div class="chart-container" v-loading="loading">
      <v-chart
        class="chart"
        :option="chartOption"
        :theme="chartTheme"
        autoresize
      />
      <div
        class="data-point-indicator"
        v-if="activeDataPoint"
        :style="dataPointStyle"
      >
        <div class="data-value">{{ activeDataPoint.value }} tokens</div>
        <div class="data-date">{{ activeDataPoint.date }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h, watch } from "vue";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { LineChart, BarChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
} from "echarts/components";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import axios from "axios";
import { useUserStore } from "@/stores/user";
import request from "@/utils/request";
import AnimatedNumber from "@/components/common/AnimatedNumber.vue";

// 定义 props
const props = defineProps({
  startDate: {
    type: String,
    required: true,
  },
  endDate: {
    type: String,
    required: true,
  },
});

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
]);

const router = useRouter();

const activeDataPoint = ref(null);
const loading = ref(false);
const totalToken = ref(0);
const usedToken = ref(0);
const dailyStats = ref([]);
const hasPermission = ref(false);

const userStore = useUserStore();

const dataPointStyle = computed(() => {
  if (!activeDataPoint.value) return {};
  return {
    left: `${activeDataPoint.value.xPos}px`,
    top: `${activeDataPoint.value.yPos}px`,
  };
});

/**
 * 获取统计数据
 */
const fetchStats = async () => {
  loading.value = true;
  try {
    const [totalResponse, dailyResponse] = await Promise.all([
      request.get("/api/analytics/total-usage", {
        params: {
          start_date: props.startDate,
          end_date: props.endDate,
        },
      }),
      request.get("/api/analytics/daily-stats", {
        params: {
          start_date: props.startDate,
          end_date: props.endDate,
        },
      }),
    ]);
    totalToken.value = totalResponse.data.total_token;
    usedToken.value = totalResponse.data.used_token;
    dailyStats.value = dailyResponse.data;

    const rawData = dailyStats.value;
    const allDates = getAllDates(
      rawData[0].date,
      rawData[rawData.length - 1].date
    );
    const filledData = fillMissingWithZero(rawData, allDates);
    dailyStats.value = filledData;
  } catch (error) {
    // 不显示错误消息，正常展示空状态
    console.log("获取统计数据失败或无数据:", error);
    totalToken.value = 0;
    usedToken.value = 0;
    dailyStats.value = [];
  } finally {
    loading.value = false;
  }
};

/**
 * 用前一天的值填充缺失日期
 * @param {Array} rawData - 原始数据数组
 * @param {Array} allDates - 完整日期数组
 * @returns {Array} 填充后的数据
 */
function fillMissingWithZero(rawData, allDates) {
  const dateMap = Object.fromEntries(
    rawData.map((item) => [item.date, Number(item.token_usage)])
  );
  return allDates.map((date) => ({
    date,
    token_usage: dateMap[date] !== undefined ? dateMap[date] : 0,
  }));
}

/**
 * 生成起止日期之间的所有日期字符串
 * @param {string} startDate - 起始日期（yyyy-mm-dd）
 * @param {string} endDate - 结束日期（yyyy-mm-dd）
 * @returns {string[]} 日期数组
 */
function getAllDates(startDate, endDate) {
  const dates = [];
  let current = new Date(startDate);
  const end = new Date(endDate);
  while (current <= end) {
    dates.push(current.toISOString().split("T")[0]);
    current.setDate(current.getDate() + 1);
  }
  return dates;
}

// 检查管理员权限
const checkAdminPermission = async () => {
  hasPermission.value = await userStore.checkAdminPermission();
};

// 监听日期变化
watch(
  () => [props.startDate, props.endDate],
  () => {
    if (props.startDate && props.endDate) {
      fetchStats();
    }
  },
  { immediate: true }
);

// 生成日期标签
const generateDateLabels = () => {
  return dailyStats.value.map((stat) =>
    new Date(stat.date).toLocaleDateString("zh-CN", {
      month: "short",
      day: "numeric",
    })
  );
};

// 生成数据
const generateData = () => {
  return dailyStats.value.map((stat) => stat.token_usage);
};

// 模拟数据点悬停效果
onMounted(async () => {
  await checkAdminPermission();
  await fetchStats();
});

// 顶层定义
const chartData = computed(() =>
  dailyStats.value.map((stat) => Number(stat.token_usage))
);
const dateLabels = computed(() =>
  dailyStats.value.map((stat) =>
    new Date(stat.date).toLocaleDateString("zh-CN", {
      month: "short",
      day: "numeric",
    })
  )
);
const maxToken = computed(() => Math.max(...chartData.value));
const minToken = computed(() => Math.min(...chartData.value));
const yAxisMax = computed(() => maxToken.value * 1.2);
const yAxisMin = computed(() => minToken.value * 0.8);

const chartOption = computed(() => ({
  tooltip: {
    trigger: "axis",
    backgroundColor: "rgba(255, 255, 255, 0.9)",
    borderColor: "#eee",
    borderWidth: 1,
    textStyle: { color: "#333" },
    formatter: "{b}: {c} tokens",
    axisPointer: {
      type: 'shadow',
      shadowStyle: {
        color: 'rgba(0, 102, 255, 0.1)'
      }
    }
  },
  grid: {
    left: "3%",
    right: "4%",
    bottom: "12%",
    containLabel: true,
  },
  xAxis: {
    type: "category",
    data: dailyStats.value.map(stat => stat.date),
    axisLine: { lineStyle: { color: "#eee" } },
    axisTick: { show: false },
    axisLabel: {
      formatter: (value) => {
        const date = new Date(value);
        return `${date.getMonth() + 1}-${date.getDate()}`;
      },
      interval: (index, value) => {
        if (index === 0 || index === dailyStats.value.length - 1) {
          return true;
        }
        
        if (dailyStats.value.length <= 10) {
          return true;
        } else if (dailyStats.value.length <= 31) {
          return index % 3 === 0;
        } else {
          return index % 7 === 0;
        }
      },
      rotate: 0,
      fontSize: 12,
      fontWeight: 'bold',
      color: '#333333',
      margin: 14,
      padding: [3, 5],
      backgroundColor: 'rgba(255, 255, 255, 0.8)',
      borderRadius: 2,
      verticalAlign: 'top',
      lineHeight: 15,
      borderWidth: 1,
      borderColor: '#eee',
      shadowBlur: 2,
      shadowColor: 'rgba(0,0,0,0.1)'
    }
  },
  yAxis: {
    type: "value",
    min: 0,
    scale: false,
    splitLine: { lineStyle: { color: "#eee", type: "dashed" } },
    axisLabel: {
      formatter: (value) => {
        if (value >= 1000000) {
          return (value / 1000000).toFixed(1) + 'M';
        } else if (value >= 1000) {
          return (value / 1000).toFixed(0) + 'K';
        }
        return value;
      }
    }
  },
  series: [
    {
      data: chartData.value,
      type: "bar",
      barWidth: "60%",
      itemStyle: {
        color: new Function('params', `
          const colors = ['#0066FF', '#4C8EFF', '#7EB0FF'];
          return colors[params.dataIndex % colors.length];
        `),
        borderRadius: [6, 6, 0, 0],
      },
      emphasis: {
        itemStyle: {
          color: '#005CE6',
          borderWidth: 1,
          borderColor: '#0066FF',
          shadowBlur: 10,
          shadowColor: 'rgba(0, 102, 255, 0.3)'
        }
      },
      label: {
        show: true,
        position: 'top',
        formatter: (params) => {
          if (params.value > 10000) {
            return (params.value / 1000).toFixed(0) + 'K';
          }
          return params.value;
        },
        fontSize: 10,
        color: '#666'
      }
    },
  ],
}));

/**
 * 计算环比增长率
 * @param {number} current 当前周期值
 * @param {number} previous 上一周期值
 * @returns {string} 百分比字符串
 */
function calcPercentChange(current, previous) {
  if (previous === 0) return current === 0 ? "0%" : "+100%";
  const change = ((current - previous) / previous) * 100;
  return (change >= 0 ? "+" : "") + change.toFixed(1) + "%";
}
</script>

<style scoped>
.token-usage {
  background: var(--gradient-light);
  border-radius: 16px;
  padding: 24px;
  height: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.token-usage::before {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  background: radial-gradient(
    circle,
    rgba(0, 102, 255, 0.05) 0%,
    transparent 70%
  );
  border-radius: 50%;
  z-index: 0;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: var(--primary-color);
  border-radius: 50%;
  animation: pulse 2s infinite;
  position: relative;
}

.pulse-dot::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 16px;
  height: 16px;
  background: transparent;
  border: 1px solid var(--primary-color);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  animation: pulseRing 2s infinite;
}

.time-selector {
  display: flex;
  gap: 8px;
  background: rgba(0, 0, 0, 0.03);
  padding: 4px;
  border-radius: 8px;
  position: relative;
}

.time-button {
  position: relative;
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  z-index: 1;
}

.time-button.active {
  color: var(--primary-color);
}

.button-indicator {
  position: absolute;
  bottom: -2px;
  left: 50%;
  width: 0;
  height: 2px;
  background: var(--primary-color);
  transition: all 0.3s ease;
  transform: translateX(-50%);
}

.time-button.active .button-indicator {
  width: 20px;
}

.hover-effect {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(0, 102, 255, 0.1);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: all 0.5s ease;
  z-index: -1;
}

.time-button:hover .hover-effect {
  width: 120%;
  height: 120%;
  opacity: 1;
}

.time-button.loading::before {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  width: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    var(--primary-color),
    transparent
  );
  animation: loading 1s infinite linear;
}

.chart-info {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.info-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  position: relative;
  overflow: hidden;
}

.info-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    transparent 0%,
    rgba(255, 255, 255, 0.1) 50%,
    transparent 100%
  );
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.info-card:hover::before {
  transform: translateX(100%);
}

.info-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  position: relative;
  overflow: hidden;
}

.info-icon::after {
  content: "";
  position: absolute;
  top: -10px;
  left: -10px;
  width: 20px;
  height: 20px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  filter: blur(5px);
  animation: floatEffect 4s infinite ease-in-out;
}

.info-content {
  flex: 1;
}

.trend-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.trend-indicator.positive {
  color: #67c23a;
}

.trend-indicator.negative {
  color: #f56c6c;
}

.chart-container {
  height: 300px;
  position: relative;
  z-index: 100;
}

.chart {
  height: 100%;
}

.data-point-indicator {
  position: absolute;
  transform: translate(-50%, -100%);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 8px 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border-left: 3px solid var(--primary-color);
  pointer-events: none;
  z-index: 10;
}

.data-point-indicator::after {
  content: "";
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 5px solid white;
}

.data-value {
  font-weight: bold;
  color: var(--primary-color);
}

.data-date {
  font-size: 12px;
  color: var(--text-secondary);
}

@keyframes loading {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes floatEffect {
  0%,
  100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(15px, 15px);
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 0.5;
  }
}

@keyframes pulseRing {
  0% {
    transform: translate(-50%, -50%) scale(0.7);
    opacity: 0;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.3);
    opacity: 0;
  }
}
</style>
