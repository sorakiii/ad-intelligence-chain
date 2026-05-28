<template>
  <div class="module-stats">
    <div class="chart-header">
      <h3>模块使用统计</h3>
      <div class="select-wrapper">
        <el-select
          v-model="timeRange"
          size="small"
          class="tech-select"
          v-loading="loading"
        >
          <el-option label="今日" value="today" />
          <el-option label="本周" value="week" />
          <el-option label="本月" value="month" />
        </el-select>
        <div class="select-glow"></div>
      </div>
    </div>

    <div class="charts-container" v-loading="loading">
      <div class="pie-chart chart-card" :class="{ visible: !loading }">
        <h4>使用人数分布</h4>
        <div class="pie-chart-container">
          <v-chart class="chart" :option="usersPieOption" autoresize />
        </div>
      </div>
      <div class="bar-chart chart-card" :class="{ visible: !loading }">
        <h4>使用量分布</h4>
        <v-chart class="chart" :option="usageBarOption" autoresize />
      </div>
    </div>

    <div class="role-ranking-title">
      <h4>角色使用排行榜</h4>
    </div>
    
    <div class="role-ranking" v-loading="loading">
      <div 
        v-for="(role, index) in sortedRoles" 
        :key="role.role_id"
        class="role-item"
        :class="{ 'top-three': index < 3 }"
      >
        <div class="rank-badge" :class="`rank-${index + 1}`">{{ index + 1 }}</div>
        <div class="role-avatar">
          <img :src="role.icon" alt="" class="avatar-img" />
        </div>
        <div class="role-info">
          <div class="role-name">{{ role.title }}</div>
          <div class="stats-info">
            <div class="stat-item">
              <span class="stat-label">使用人数:</span>
              <span class="stat-value">{{ role.unique_users }}人</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">使用量:</span>
              <span class="stat-value">{{ formatNumber(role.token_usage) }}</span>
            </div>
          </div>
          <div class="progress-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${getPercentage(role.token_usage)}%` }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import VChart from "vue-echarts";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { PieChart, BarChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
} from "echarts/components";
import request from "@/utils/request";

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

// 注册必要的组件
use([
  CanvasRenderer,
  PieChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
]);

const router = useRouter();
const userStore = useUserStore();
const timeRange = ref("today");
const loading = ref(false);
const roleStats = ref([]);
const hasPermission = ref(false);

/**
 * 获取角色使用统计
 */
const fetchRoleStats = async () => {
  loading.value = true;
  try {
    const response = await request.get("/api/analytics/role-usage", {
      params: {
        start_date: props.startDate,
        end_date: props.endDate,
      },
    });
    roleStats.value = response.data.map((item) => ({
      ...item,
      token_usage: Number(item.token_usage) || 0,
      message_count: Number(item.message_count) || 0,
      unique_users: Number(item.unique_users) || 0,
    }));
    console.log("roleStats", roleStats.value);
  } catch (error) {
    // 不显示错误消息，正常展示空状态
    console.log("获取角色使用统计失败或无数据:", error);
    roleStats.value = [];
  } finally {
    loading.value = false;
  }
};

/**
 * 将数组分组
 * @param {Array} arr - 原始数组
 * @param {number} size - 每组大小
 * @returns {Array[]} 分组后的二维数组
 */
function chunkArray(arr, size) {
  const result = [];
  for (let i = 0; i < arr.length; i += size) {
    result.push(arr.slice(i, i + size));
  }
  return result;
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
      fetchRoleStats();
    }
  },
  { immediate: true }
);

// 获取开始日期
const getStartDate = () => {
  const now = new Date();
  const startDate = new Date();

  switch (timeRange.value) {
    case "today":
      startDate.setHours(0, 0, 0, 0);
      break;
    case "week":
      startDate.setDate(now.getDate() - 7);
      break;
    case "month":
      startDate.setMonth(now.getMonth() - 1);
      break;
  }

  return startDate.toISOString().split("T")[0];
};

const highlightStyle = computed(() => {
  if (!selectedBar.value) return {};
  return {
    left: `${selectedBar.value.position}%`,
    height: `${selectedBar.value.height}%`,
    opacity: 1,
  };
});

// 饼图配置
const usersPieOption = computed(() => ({
  tooltip: { 
    trigger: "item",
    backgroundColor: "rgba(255, 255, 255, 0.95)",
    borderColor: "#eee",
    borderWidth: 1,
    textStyle: { color: "#333" },
    formatter: (params) => {
      return `<div style="font-weight:bold">${params.name}</div>
              <div style="margin-top:5px">使用人数：${params.value}</div>
              <div>占比：${params.percent}%</div>`;
    }
  },
  legend: { 
    type: 'scroll',
    orient: 'horizontal',
    bottom: 0, 
    left: 'center',
    itemWidth: 12,
    itemHeight: 12,
    pageButtonPosition: 'end',
    pageButtonItemGap: 5,
    pageButtonGap: 10,
    pageIconColor: '#0066FF',
    pageIconInactiveColor: '#ccc',
    pageIconSize: 12,
    textStyle: {
      color: "#666",
      fontSize: 12
    }
  },
  grid: {
    top: 10,
    bottom: 80 // 为图例留出更多空间
  },
  series: [
    {
      name: "使用人数",
      type: "pie",
      radius: ["35%", "60%"], // 稍微减小环形图尺寸
      center: ['50%', '45%'], // 将图表向上移动一些
      itemStyle: {
        borderRadius: 4,
        borderColor: "#fff",
        borderWidth: 2,
        shadowBlur: 10,
        shadowColor: "rgba(0, 0, 0, 0.1)"
      },
      label: {
        show: true,
        position: 'outside', // 将标签放到外部
        formatter: "{b}: {c}人",
        fontSize: 11,
        fontWeight: "bold",
        alignTo: 'edge',
        edgeDistance: 10,
        lineHeight: 15
      },
      labelLine: {
        length: 10,
        length2: 10,
        smooth: true
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 20,
          shadowOffsetX: 0,
          shadowColor: "rgba(0, 0, 0, 0.2)"
        },
        label: {
          fontWeight: "bold",
          fontSize: 13
        }
      },
      data: roleStats.value.map((role) => ({
        value: role.unique_users,
        name: role.title,
      })),
    },
  ],
  color: [
    "#0066FF", "#7EB0FF", "#45B7D1", "#4ECDC4", 
    "#FF6B6B", "#FFD166", "#06D6A0", "#118AB2",
    "#073B4C", "#8338EC"
  ]
}));

console.log("usersPieOption", usersPieOption.value);

// 柱状图配置
const usageBarOption = computed(() => ({
  tooltip: {
    trigger: "axis",
    axisPointer: {
      type: "shadow",
      shadowStyle: {
        color: "rgba(0, 102, 255, 0.05)"
      }
    },
    backgroundColor: "rgba(255, 255, 255, 0.95)",
    borderColor: "#eee",
    borderWidth: 1,
    textStyle: { color: "#333" },
    formatter: (params) => {
      const data = params[0];
      return `<div style="font-weight:bold;margin-bottom:5px;">${data.name}</div>
              <div>Token使用量：${new Intl.NumberFormat("zh-CN").format(data.value)}</div>`;
    }
  },
  grid: {
    left: "3%",
    right: "4%",
    bottom: "15%",
    top: "5%",
    containLabel: true,
  },
  xAxis: {
    type: "category",
    data: roleStats.value.map((role) => role.title),
    axisLine: {
      lineStyle: {
        color: "#eee",
      },
    },
    axisTick: { show: false },
    axisLabel: {
      interval: 0,
      rotate: 45,
      fontSize: 12,
      color: "#333",
      margin: 14,
      fontWeight: "500",
      formatter: (value) => {
        if (value.length > 8) {
          return value.substring(0, 8) + "...";
        }
        return value;
      }
    }
  },
  yAxis: {
    type: "value",
    splitLine: {
      lineStyle: {
        type: "dashed",
        color: "#eee",
      },
    },
    axisLabel: {
      formatter: (value) => {
        if (value >= 1000000) {
          return (value / 1000000).toFixed(1) + "M";
        } else if (value >= 1000) {
          return (value / 1000).toFixed(0) + "K";
        }
        return value;
      }
    }
  },
  series: [
    {
      data: roleStats.value.map((role) => role.token_usage),
      type: "bar",
      barWidth: "50%",
      itemStyle: {
        color: function (params) {
          const colors = ["#0066FF", "#4C8EFF", "#7EB0FF", "#45B7D1", "#4ECDC4", "#FFD166", "#FF6B6B"];
          return colors[params.dataIndex % colors.length];
        },
        borderRadius: [6, 6, 0, 0],
        shadowColor: "rgba(0, 0, 0, 0.1)",
        shadowBlur: 4,
        shadowOffsetY: 2
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: "rgba(0, 0, 0, 0.2)"
        }
      },
      label: {
        show: true,
        position: "top",
        formatter: (params) => {
          if (params.value > 10000) {
            return (params.value / 1000).toFixed(0) + "K";
          }
          return params.value;
        },
        fontSize: 12,
        color: "#666"
      },
      animationDelay: (idx) => idx * 100,
      animationDuration: 1000
    },
  ],
}));

/**
 * 基于名称生成固定的随机颜色
 * @param {string} name - 名称
 * @returns {string} 颜色代码
 */
function getRandomColor(name) {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }

  const h = Math.abs(hash % 360);
  const s = 70 + Math.abs((hash >> 8) % 30);
  const l = 65;

  return `hsl(${h}, ${s}%, ${l}%)`;
}

onMounted(async () => {
  await checkAdminPermission();
  await fetchRoleStats();
});

// 监听时间范围变化
watch(timeRange, () => {
  fetchRoleStats();
});

// 按使用量排序的角色列表
const sortedRoles = computed(() => {
  return roleStats.value
    .slice()
    .sort((a, b) => b.token_usage - a.token_usage);
});

/**
 * 格式化数字为易读格式
 */
const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(0) + 'K';
  }
  return new Intl.NumberFormat("zh-CN").format(num);
};

/**
 * 计算使用量百分比进度条
 */
const getPercentage = (value) => {
  if (!roleStats.value.length) return 0;
  const max = Math.max(...roleStats.value.map((item) => item.token_usage));
  return max ? Math.floor((value / max) * 100) : 0;
};
</script>

<style scoped>
.module-stats {
  min-height: 500px;
  height: auto;
  background: var(--gradient-light, linear-gradient(to bottom right, #f8f9fa, #f1f2f6));
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.module-stats::before {
  content: "";
  position: absolute;
  left: -50px;
  top: -50px;
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, rgba(0, 102, 255, 0.03) 0%, transparent 70%);
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

.select-wrapper {
  position: relative;
}

.tech-select {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.tech-select:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 102, 255, 0.15);
}

.select-glow {
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary-color, #0066ff), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.select-wrapper:hover .select-glow {
  opacity: 1;
}

.charts-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  width: 100%;
  min-height: 320px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.5s cubic-bezier(0.165, 0.84, 0.44, 1);
  transform: translateY(20px);
  opacity: 0;
  position: relative;
  overflow: hidden;
}

.chart-card.visible {
  transform: translateY(0);
  opacity: 1;
}

.chart-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px);
}

.chart-card::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, var(--primary-color, #0066ff), #4ecdc4);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.chart-card:hover::after {
  opacity: 1;
}

h4 {
  text-align: center;
  margin-bottom: 18px;
  color: var(--text-primary, #303133);
  position: relative;
  display: inline-block;
  left: 50%;
  transform: translateX(-50%);
  font-size: 16px;
  font-weight: 600;
}

h4::after {
  content: "";
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary-color, #0066ff), transparent);
}

.pie-chart-container {
  position: relative;
  height: 380px;
  padding-bottom: 30px;
}

.chart {
  height: 100% !important;
  width: 100% !important;
  background: white !important;
}

.role-ranking-title {
  margin: 20px 0 10px 0;
}

.role-ranking-title h4 {
  margin: 0;
  padding: 0;
  left: 0;
  transform: none;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #303133);
}

.role-ranking {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.role-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.role-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.role-item.top-three {
  background: linear-gradient(to right, rgba(255, 255, 255, 0.95), white);
}

.role-item.top-three::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  width: 100%;
  background: linear-gradient(90deg, var(--primary-color, #0066ff), #4ecdc4);
}

.rank-badge {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  background: #f0f2f5;
  color: #606266;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.rank-1 {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: white;
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(255, 165, 0, 0.3);
}

.rank-2 {
  background: linear-gradient(135deg, #C0C0C0, #A9A9A9);
  color: white;
  box-shadow: 0 3px 6px rgba(169, 169, 169, 0.3);
}

.rank-3 {
  background: linear-gradient(135deg, #CD7F32, #8B4513);
  color: white;
  box-shadow: 0 3px 6px rgba(139, 69, 19, 0.3);
}

.role-avatar {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.role-info {
  flex: 1;
}

.role-name {
  font-weight: 600;
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
}

.stats-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.stat-label {
  color: #909399;
}

.stat-value {
  font-weight: 500;
  color: #0066FF;
}

.progress-container {
  width: 100%;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
  overflow: hidden;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
}

.progress-fill {
  height: 100%;
  background: var(--primary-color, #0066ff);
  background-image: linear-gradient(
    90deg, 
    rgba(255, 255, 255, 0.15) 25%, 
    transparent 25%, 
    transparent 50%, 
    rgba(255, 255, 255, 0.15) 50%, 
    rgba(255, 255, 255, 0.15) 75%, 
    transparent 75%, 
    transparent
  );
  background-size: 20px 20px;
  border-radius: 3px;
  transition: width 0.8s ease;
  animation: progressAnimation 1s linear infinite;
}

.role-item:nth-child(1) .progress-fill {
  background: linear-gradient(90deg, #FFD700, #FFA500);
}

.role-item:nth-child(2) .progress-fill {
  background: linear-gradient(90deg, #C0C0C0, #A9A9A9);
}

.role-item:nth-child(3) .progress-fill {
  background: linear-gradient(90deg, #CD7F32, #8B4513);
}

@media (max-width: 768px) {
  .role-ranking {
    grid-template-columns: 1fr;
  }
}

@keyframes progressAnimation {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 20px 0;
  }
}
</style>