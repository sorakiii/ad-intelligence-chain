<!-- 
  @file 数据分析页面
  @description 展示系统各项数据统计信息
-->
<template>
  <div class="statistics-page" v-loading="loading">
    <div v-if="hasPermission" class="statistics-container">
      <div class="filter-bar">
        <div class="time-selector">
          <button
            v-for="option in timeOptions"
            :key="option.value"
            :class="['time-button', { active: timeRange === option.value }]"
            @click="setTimeRange(option.value)"
          >
            <span class="button-label">{{ option.label }}</span>
            <span
              class="button-arrow"
              :class="{ active: timeRange === option.value }"
              >▶</span
            >
            <span
              v-if="timeRange === option.value"
              class="button-progress"
            ></span>
          </button>
        </div>
        <div class="date-picker-container">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :shortcuts="dateShortcuts"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
          />
        </div>
      </div>

      <el-row :gutter="20" class="mt-20" v-if="startDate && endDate">
        <el-col :span="24">
          <daily-token-usage
            class="stat-card"
            :start-date="startDate"
            :end-date="endDate"
          />
        </el-col>
      </el-row>

      <el-row :gutter="20" class="mt-20" v-if="startDate && endDate">
        <el-col :span="24">
          <user-daily-usage
            class="stat-card"
            :start-date="startDate"
            :end-date="endDate"
          />
        </el-col>
      </el-row>

      <el-row :gutter="20" class="mt-20" v-if="startDate && endDate">
        <el-col :span="24">
          <module-usage-stats
            class="stat-card"
            :start-date="startDate"
            :end-date="endDate"
          />
        </el-col>
      </el-row>

      <el-row :gutter="20" class="mt-20" v-if="startDate && endDate">
        <el-col :span="24">
          <user-module-usage
            class="stat-card"
            :start-date="startDate"
            :end-date="endDate"
          />
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useUserStore } from "@/stores/user";
import PageHeader from "@/components/workspace/PageHeader.vue";
import DailyTokenUsage from "@/components/statistics/DailyTokenUsage.vue";
import UserDailyUsage from "@/components/statistics/UserDailyUsage.vue";
import ModuleUsageStats from "@/components/statistics/ModuleUsageStats.vue";
import UserModuleUsage from "@/components/statistics/UserModuleUsage.vue";

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const hasPermission = ref(false);

// 日期相关
const dateRange = ref<[string, string] | null>(null);
const lastValidRange = ref<[string, string] | null>(null);
const startDate = ref<string>("");
const endDate = ref<string>("");

// 日期快捷选项
const dateShortcuts = [
  {
    text: "最近一周",
    value: () => {
      const end = new Date();
      const start = new Date();
      
      // 设置结束时间为今天的23:59:59
      end.setHours(23, 59, 59, 999);
      
      // 设置开始时间为6天前的00:00:00（包含今天，所以往前推6天）
      const daysToSubtract = 6; // 7天 - 1 = 6天
      start.setTime(end.getTime() - 3600 * 1000 * 24 * daysToSubtract);
      start.setHours(0, 0, 0, 0);
      
      return [start, end];
    },
  },
  {
    text: "最近一个月",
    value: () => {
      const end = new Date();
      const start = new Date();
      
      // 设置结束时间为今天的23:59:59
      end.setHours(23, 59, 59, 999);
      
      // 设置开始时间为29天前的00:00:00（包含今天，所以往前推29天）
      const daysToSubtract = 29; // 30天 - 1 = 29天
      start.setTime(end.getTime() - 3600 * 1000 * 24 * daysToSubtract);
      start.setHours(0, 0, 0, 0);
      
      return [start, end];
    },
  },
  {
    text: "最近三个月",
    value: () => {
      const end = new Date();
      const start = new Date();
      
      // 设置结束时间为今天的23:59:59
      end.setHours(23, 59, 59, 999);
      
      // 设置开始时间为89天前的00:00:00（包含今天，所以往前推89天）
      const daysToSubtract = 89; // 90天 - 1 = 89天
      start.setTime(end.getTime() - 3600 * 1000 * 24 * daysToSubtract);
      start.setHours(0, 0, 0, 0);
      
      return [start, end];
    },
  },
  {
    text: "测试数据范围",
    value: () => {
      return ['2025-08-01', '2025-08-31'];
    },
  },
];

// 处理日期变化
const handleDateChange = (val: [string, string] | null) => {
  if (val && val[0] === val[1]) {
    ElMessage.warning("开始日期和结束日期不能为同一天，请重新选择！");
    // 恢复到上一次合法的区间
    dateRange.value = lastValidRange.value;
    return;
  }
  // 合法则保存
  lastValidRange.value = val;
  if (val) {
    startDate.value = val[0];
    endDate.value = val[1];
  } else {
    startDate.value = "";
    endDate.value = "";
  }
};

// 检查管理员权限
const checkAdminPermission = async () => {
  try {
    const isAdmin = await userStore.checkAdminPermission();
    if (isAdmin) {
      hasPermission.value = true;
      
      // 设置默认日期范围为最近7天（确保包含今天）
      const end = new Date();
      const start = new Date();
      
      // 设置结束时间为今天的23:59:59
      end.setHours(23, 59, 59, 999);
      
      // 设置开始时间为6天前的00:00:00（包含今天，所以往前推6天）
      const daysToSubtract = 6; // 7天 - 1 = 6天
      start.setTime(end.getTime() - 3600 * 1000 * 24 * daysToSubtract);
      start.setHours(0, 0, 0, 0);
      
      // 修复时区问题：使用本地时间格式化日期
      const formatLocalDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      };
      
      dateRange.value = [
        formatLocalDate(start),
        formatLocalDate(end),
      ];
      
      console.log('默认日期范围:', dateRange.value);
      handleDateChange(dateRange.value);
    } else {
      ElMessage.error("您没有权限访问此页面");
      router.push("/workspace/single-role");
    }
  } catch (error) {
    console.error("检查权限失败:", error);
    ElMessage.error("检查权限失败");
    router.push("/workspace/single-role");
  }
};

onMounted(async () => {
  await checkAdminPermission();
  lastValidRange.value = dateRange.value;
});

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

const timeOptions = [
  { label: "最近7天", value: "7" },
  { label: "最近30天", value: "30" },
  { label: "最近90天", value: "90" },
];
const timeRange = ref("7");

const setTimeRange = (value: string) => {
  timeRange.value = value;
  const end = new Date();
  const start = new Date();
  
  // 修复：最近N天应该包含今天，从今天往前推N天
  // 设置结束时间为今天的23:59:59
  end.setHours(23, 59, 59, 999);
  
  // 设置开始时间为N天前的00:00:00（包含今天，所以往前推N-1天）
  // 例如：最近7天 = 今天 + 往前6天
  const daysToSubtract = Number(value) - 1;
  start.setTime(end.getTime() - 3600 * 1000 * 24 * daysToSubtract);
  start.setHours(0, 0, 0, 0);
  
  // 修复时区问题：使用本地时间格式化日期
  const formatLocalDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };
  
  dateRange.value = [
    formatLocalDate(start),
    formatLocalDate(end),
  ];
  
  // 添加调试信息
  console.log(`最近${value}天的日期范围:`, dateRange.value);
  console.log('当前日期:', formatLocalDate(new Date()));
  console.log('计算逻辑: 从今天往前推', daysToSubtract, '天');
  console.log('开始时间 (本地):', start.toString());
  console.log('结束时间 (本地):', end.toString());
  console.log('开始时间 (UTC):', start.toISOString());
  console.log('结束时间 (UTC):', end.toISOString());
  
  handleDateChange(dateRange.value);
  lastValidRange.value = dateRange.value;
};
</script>

<style scoped>
.statistics-page {
  min-height: 100%;
  padding: 20px;
}

.statistics-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.date-picker-container {
  background: none;
  padding: 0;
  border-radius: 12px;
  box-shadow: none;
  height: 48px;
  display: flex;
  align-items: center;
}

.el-date-editor.el-input,
.el-date-editor.el-input__wrapper {
  border-radius: 12px !important;
  height: 48px !important;
  background: linear-gradient(90deg, #f0f4ff 0%, #eaf1ff 100%) !important;
  box-shadow: 0 2px 8px rgba(0, 102, 255, 0.04) !important;
  border: none !important;
  font-size: 16px;
}

.statistics {
  height: 100%;
  background: white;
  padding: 24px;
}

.statistics-content {
  margin-top: 24px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.mt-20 {
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .statistics {
    padding: 16px;
  }

  .el-col-12 {
    width: 100%;
  }
}

.module-tags {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.tag-row {
  display: flex;
  gap: 6px;
}
.module-tag {
  background: #e6f7e6;
  color: #3a8d00;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 13px;
}
.module-tag.highlight {
  background: #ffeaea;
  color: #d93026;
}

.quick-range-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.quick-range-bar button {
  padding: 8px 16px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.quick-range-bar button.active {
  background-color: #007bff;
  color: white;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 24px;
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 4px 24px 0 rgba(0, 102, 255, 0.08);
  padding: 18px 32px;
  margin-bottom: 32px;
}

.time-selector {
  display: flex;
  gap: 16px;
}

.time-button {
  position: relative;
  padding: 12px 32px;
  background: linear-gradient(90deg, #f0f4ff 0%, #eaf1ff 100%);
  border: none;
  border-radius: 12px;
  color: #222;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  overflow: hidden;
  transition: box-shadow 0.3s, background 0.3s, color 0.3s;
  box-shadow: 0 2px 8px rgba(0, 102, 255, 0.04);
  height: 48px;
  display: flex;
  align-items: center;
}

.time-button.active {
  background: linear-gradient(90deg, #2e6fff 0%, #00eaff 100%);
  color: #fff;
  box-shadow: 0 4px 16px 0 rgba(0, 102, 255, 0.18);
}

.time-button .button-label {
  z-index: 2;
  position: relative;
}

.time-button .button-arrow {
  margin-left: 8px;
  font-size: 16px;
  color: #b0b8c9;
  transition: color 0.3s, transform 0.3s;
}

.time-button.active .button-arrow {
  color: #fff;
  transform: translateX(4px) scale(1.2);
  animation: arrowFlash 1s infinite alternate;
}

@keyframes arrowFlash {
  0% {
    opacity: 0.7;
  }
  100% {
    opacity: 1;
  }
}

.time-button .button-progress {
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, #00eaff 0%, #2e6fff 100%);
  animation: progressBar 1.2s linear infinite;
}

@keyframes progressBar {
  0% {
    width: 0;
  }
  100% {
    width: 100%;
  }
}

.time-button:hover:not(.active) {
  background: linear-gradient(90deg, #eaf1ff 0%, #d0e7ff 100%);
  color: #2e6fff;
  box-shadow: 0 4px 16px 0 rgba(0, 102, 255, 0.1);
}
</style>