<template>
  <div class="user-usage">
    <div class="chart-header">
      <h3>用户Token使用量排行Top10</h3>
    </div>

    <div class="user-list" v-loading="loading">
      <div 
        v-for="(user, index) in topUsers" 
        :key="index"
        class="user-item"
        :class="{ 'top-three': index < 3 }"
      >
        <div class="rank-badge" :class="`rank-${index + 1}`">{{ index + 1 }}</div>
        <div class="user-info">
          <div class="user-header">
            <div class="username">{{ user.userName || '未设置' }}</div>
            <div class="phone-number">{{ user.username }}</div>
          </div>
          <div class="progress-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${getPercentage(user.tokenUsage)}%` }"></div>
            </div>
            <div class="token-count">{{ formatNumber(user) }}</div>
          </div>
        </div>
      </div>
      
      <div class="empty-state" v-if="topUsers.length === 0 && !loading">
        <i class="el-icon-data-line"></i>
        <p>暂无使用数据</p>
      </div>
    </div>

    <div class="pagination-container" v-if="tableData.value?.length > 10">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="tableData.value?.length || 0"
        layout="prev, pager, next"
        background
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import request from "@/utils/request";
import { useUserStore } from "@/stores/user";

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

const router = useRouter();
const loading = ref(false);
const tableData = ref([]);
const userStore = useUserStore();
const hasPermission = ref(false);
const currentPage = ref(1);
const pageSize = 10;

// 获取前10名用户
const topUsers = computed(() => {
  return tableData.value
    .slice()
    .sort((a, b) => b.tokenUsage - a.tokenUsage)
    .slice(0, 10);
});

/**
 * 格式化数字为易读格式
 */
const formatNumber = (row) => {
  const num = row.tokenUsage;
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
  if (!tableData.value.length) return 0;
  const max = Math.max(...tableData.value.map((item) => item.tokenUsage));
  return max ? Math.floor((value / max) * 100) : 0;
};

// 检查管理员权限
const checkAdminPermission = async () => {
  hasPermission.value = await userStore.checkAdminPermission();
};

// 获取用户使用数据
const fetchUserUsage = async () => {
  loading.value = true;
  try {
    const response = await request.get("/api/analytics/user-usage", {
      params: {
        start_date: props.startDate,
        end_date: props.endDate,
      },
    });
    if (!response.data) {
      console.log("返回的数据格式不正确或无数据:", response);
      tableData.value = [];
      return;
    }

    tableData.value = response.data.map((user) => ({
      username: user.phone || "未知用户",
      userName: user.user_name || null,
      tokenUsage: Number(user.token_usage) || 0,
      requestCount: user.request_count || 0,
    }));
  } catch (error) {
    // 不显示错误消息，正常展示空状态
    console.log("获取用户使用数据失败或无数据:", error);
    tableData.value = [];
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await checkAdminPermission();
  await fetchUserUsage();
});

// 监听日期变化
watch(
  () => [props.startDate, props.endDate],
  () => {
    if (props.startDate && props.endDate) {
      fetchUserUsage();
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.user-usage {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 600px;
  background: var(--gradient-light, linear-gradient(to bottom right, #f8f9fa, #f1f2f6));
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.user-usage::after {
  content: "";
  position: absolute;
  bottom: -100px;
  right: -100px;
  width: 200px;
  height: 200px;
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

.user-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
  flex: 1;
  overflow-y: auto;
  padding: 4px;
}

.user-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.user-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 6px;
  height: 100%;
  background: transparent;
  transition: all 0.3s ease;
}

.user-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.user-item.top-three {
  background: linear-gradient(to right, rgba(255, 255, 255, 0.9), white);
}

.user-item.top-three::before {
  background: var(--primary-color, #0066ff);
}

.user-item:nth-child(1)::before {
  background: linear-gradient(to bottom, #FFD700, #FFA500);
}

.user-item:nth-child(2)::before {
  background: linear-gradient(to bottom, #C0C0C0, #A9A9A9);
}

.user-item:nth-child(3)::before {
  background: linear-gradient(to bottom, #CD7F32, #8B4513);
}

.rank-badge {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 20px;
  background: #f0f2f5;
  color: #606266;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
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

.user-info {
  flex: 1;
}

.user-header {
  margin-bottom: 10px;
}

.username {
  font-weight: 600;
  color: #303133;
  font-size: 15px;
  margin-bottom: 4px;
}

.phone-number {
  font-size: 12px;
  color: #909399;
  font-weight: 400;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
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
  border-radius: 4px;
  transition: width 0.8s ease;
  animation: progressAnimation 1s linear infinite;
}

.user-item:nth-child(1) .progress-fill {
  background: linear-gradient(90deg, #FFD700, #FFA500);
}

.user-item:nth-child(2) .progress-fill {
  background: linear-gradient(90deg, #C0C0C0, #A9A9A9);
}

.user-item:nth-child(3) .progress-fill {
  background: linear-gradient(90deg, #CD7F32, #8B4513);
}

.token-count {
  font-size: 16px;
  color: var(--primary-color, #0066ff);
  font-weight: 600;
  min-width: 70px;
  text-align: right;
}

.user-item:nth-child(1) .token-count {
  color: #FFA500;
}

.user-item:nth-child(2) .token-count {
  color: #A9A9A9;
}

.user-item:nth-child(3) .token-count {
  color: #8B4513;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: auto;
  padding-top: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #909399;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #DCDFE6;
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