<template>
  <div class="user-module-usage">
    <div class="chart-header">
      <h3>用户模块使用详情</h3>
      <div class="header-actions">
        <div class="search-wrapper">
          <el-input
            v-model="searchUser"
            placeholder="搜索用户名或手机号"
            size="small"
            class="search-input"
            clearable
          >
            <template #prefix>
              <el-icon class="search-icon"><Search /></el-icon>
            </template>
          </el-input>
          <div class="search-glow"></div>
        </div>
      </div>
    </div>

    <div class="user-cards-container" v-loading="loading">
      <div v-if="paginatedUsers.length === 0" class="empty-state">
        <i class="el-icon-data-line"></i>
        <p>{{ loading ? '加载中...' : (searchUser ? '未找到匹配的用户' : '暂无使用数据') }}</p>
      </div>
      
      <div v-for="user in paginatedUsers" :key="user.phone" class="user-card">
        <div class="ranking-badge">{{ getUserRanking(user) }}</div>
        <div class="user-card-header">
          <div class="user-avatar">
            <span>{{ user.phone.substring(0, 1) }}</span>
          </div>
          <div class="user-info">
            <div class="user-name">{{ user.user_name || '未设置用户名' }}</div>
            <div class="user-phone">{{ formatPhoneNumber(user.phone) }}</div>
            <div class="total-token">
              <span class="token-label">总Token: </span>
              <span class="token-value">{{ formatBigNumber(getTotalTokensRaw(user)) }}</span>
            </div>
            <div class="user-stats">
              <div class="stat-item">
                <i class="el-icon-message"></i>
                <span>消息数: {{ getTotalMessages(user) }}</span>
              </div>
              <div class="stat-item">
                <i class="el-icon-cpu"></i>
                <span>模块数: {{ user.roles.length }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modules-container">
          <div class="modules-title">使用的模块</div>
          <div class="modules-grid">
            <div 
              v-for="role in sortRolesByUsage(user.roles)" 
              :key="role.role_id" 
              class="module-item"
              :class="getUsageClass(role.token_usage)"
            >
              <div class="module-icon">
                <img v-if="role.icon" :src="role.icon" alt="" />
                <i v-else class="el-icon-chat-dot-square"></i>
              </div>
              <div class="module-details">
                <div class="module-name">{{ role.title }}</div>
                <div class="usage-stats">
                  <div class="usage-stat">
                    <span class="stat-label">次数:</span>
                    <span class="stat-value">{{ role.message_count }}</span>
                  </div>
                  <div class="usage-stat">
                    <span class="stat-label">Token:</span>
                    <span class="stat-value">{{ formatBigNumber(role.token_usage) }}</span>
                  </div>
                </div>
                <div class="progress-container">
                  <div class="progress-bar">
                    <div 
                      class="progress-fill" 
                      :style="{ width: `${getModulePercentage(role.token_usage, user)}%` }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="pagination-container" v-if="filteredUsers.length > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="filteredUsers.length"
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
import { useUserStore } from "@/stores/user";
import { Search } from "@element-plus/icons-vue";
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

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const searchUser = ref("");
const tableData = ref([]);
const allUsers = ref([]);
const hasPermission = ref(false);
const currentPage = ref(1);
const pageSize = 5;

/**
 * 获取用户角色使用数据
 */
const fetchUserRoleUsage = async () => {
  loading.value = true;
  try {
    // 添加调试信息
    console.log('前端发送的日期参数:', {
      start_date: props.startDate,
      end_date: props.endDate
    });
    
    const response = await request.get("/api/analytics/user-role-usage", {
      params: {
        start_date: props.startDate,
        end_date: props.endDate,
      },
    });
    
    // 对数据进行排序处理
    const sortedData = response.data
      .map(user => {
        // 计算用户总Token
        const totalToken = user.roles.reduce((sum, role) => sum + role.token_usage, 0);
        return { ...user, totalToken };
      })
      .sort((a, b) => b.totalToken - a.totalToken);
    
    tableData.value = sortedData;
    allUsers.value = sortedData;
    
    // 添加调试信息
    console.log('API返回的数据:', sortedData);
  } catch (error) {
    // 不显示错误消息，正常展示空状态
    console.log("获取用户角色使用数据失败或无数据:", error);
    tableData.value = [];
    allUsers.value = [];
  } finally {
    loading.value = false;
  }
};

// 根据搜索过滤的用户列表
const filteredUsers = computed(() => {
  if (!searchUser.value) {
    return tableData.value;
  }
  
  const searchTerm = searchUser.value.toLowerCase();
  return tableData.value.filter((user) => 
    user.phone.toLowerCase().includes(searchTerm) ||
    (user.user_name && user.user_name.toLowerCase().includes(searchTerm))
  );
});

// 分页显示的用户
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  const end = start + pageSize;
  return filteredUsers.value.slice(start, end);
});

/**
 * 获取用户排名
 */
const getUserRanking = (user) => {
  const index = tableData.value.findIndex(u => u.phone === user.phone);
  return index + 1;
};

/**
 * 格式化手机号，中间四位显示为*
 */
const formatPhoneNumber = (phone) => {
  if (!phone || phone.length < 11) return phone;
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
};

/**
 * 获取标签类型
 */
const getUsageClass = (usage) => {
  if (usage >= 10000) {
    return "high-usage";
  } else if (usage >= 5000) {
    return "medium-usage";
  } else if (usage >= 1000) {
    return "normal-usage";
  } else {
    return "low-usage";
  }
};

/**
 * 获取用户的总消息数
 */
const getTotalMessages = (user) => {
  return user.roles.reduce((total, role) => total + role.message_count, 0);
};

/**
 * 获取用户的原始总Token使用量（无格式化）
 */
const getTotalTokensRaw = (user) => {
  if (!user || !user.roles) return 0;
  return user.roles.reduce((sum, role) => {
    // 确保token_usage是数字，如果是字符串则解析它
    const usage = typeof role.token_usage === 'string' 
      ? parseFloat(role.token_usage.replace(/[^0-9.e+-]/g, '')) 
      : role.token_usage;
    return sum + (isNaN(usage) ? 0 : usage);
  }, 0);
};

/**
 * 按使用量排序角色
 */
const sortRolesByUsage = (roles) => {
  return [...roles].sort((a, b) => b.token_usage - a.token_usage);
};

/**
 * 格式化大数字为友好显示
 * @param {number|string} num - 需要格式化的数字
 * @returns {string} 格式化后的字符串
 */
const formatBigNumber = (num) => {
  if (!num) return '0';
  
  // 将输入转换为字符串
  const numStr = String(num);
  
  // 首先检查是否已经有单位后缀（如T、B、M、K）
  const unitMatch = numStr.match(/^(.*)(T|B|M|K)$/i);
  if (unitMatch) {
    // 递归调用，但先去掉单位
    return formatBigNumber(unitMatch[1]);
  }
  
  // 处理科学计数法格式
  if (numStr.includes('e+')) {
    const parts = numStr.split('e+');
    const base = parseFloat(parts[0]);
    const exponent = parseInt(parts[1]);
    
    // 根据指数大小选择适当的单位
    if (exponent >= 36) return (base).toFixed(1) + 'U'; // undecillion (10^36)
    if (exponent >= 33) return (base).toFixed(1) + 'D'; // decillion (10^33)
    if (exponent >= 30) return (base).toFixed(1) + 'N'; // nonillion (10^30)
    if (exponent >= 27) return (base).toFixed(1) + 'O'; // octillion (10^27)
    if (exponent >= 24) return (base).toFixed(1) + 'S'; // septillion (10^24)
    if (exponent >= 21) return (base).toFixed(1) + 'X'; // sextillion (10^21)
    if (exponent >= 18) return (base).toFixed(1) + 'Q'; // quintillion (10^18)
    if (exponent >= 15) return (base).toFixed(1) + 'q'; // quadrillion (10^15)
    if (exponent >= 12) return (base).toFixed(1) + 'T'; // trillion (10^12)
    if (exponent >= 9) return (base).toFixed(1) + 'B'; // billion (10^9)
    if (exponent >= 6) return (base).toFixed(1) + 'M'; // million (10^6)
    if (exponent >= 3) return (base).toFixed(1) + 'K'; // thousand (10^3)
    return base.toFixed(1);
  }

  // 处理常规数字
  const numValue = parseFloat(numStr);
  if (isNaN(numValue)) return '0';
  
  if (numValue >= 1_000_000_000_000) {
    return (numValue / 1_000_000_000_000).toFixed(1) + 'T';
  } else if (numValue >= 1_000_000_000) {
    return (numValue / 1_000_000_000).toFixed(1) + 'B';
  } else if (numValue >= 1_000_000) {
    return (numValue / 1_000_000).toFixed(1) + 'M';
  } else if (numValue >= 1_000) {
    return (numValue / 1_000).toFixed(1) + 'K';
  } else {
    return numValue.toFixed(0);
  }
};

/**
 * 计算模块使用量百分比进度条
 */
const getModulePercentage = (value, user) => {
  if (!user.roles.length) return 0;
  const max = Math.max(...user.roles.map((role) => role.token_usage));
  return max ? Math.floor((value / max) * 100) : 0;
};

// 监听日期范围变化
watch(
  () => [props.startDate, props.endDate],
  () => {
    if (props.startDate && props.endDate) {
      fetchUserRoleUsage();
    }
  },
  { immediate: true }
);

// 监听搜索词变化
watch(searchUser, () => {
  currentPage.value = 1; // 重置分页
});

// 检查管理员权限并加载数据
onMounted(async () => {
  await checkAdminPermission();
  if (props.startDate && props.endDate) {
    await fetchUserRoleUsage();
  }
});

// 检查管理员权限
const checkAdminPermission = async () => {
  hasPermission.value = await userStore.checkAdminPermission();
};
</script>

<style scoped>
.user-module-usage {
  min-height: 500px;
  height: auto;
  background: var(--gradient-light, linear-gradient(to bottom right, #f8f9fa, #f1f2f6));
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  position: relative;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  position: relative;
}

.search-wrapper {
  position: relative;
  transition: all 0.3s ease;
}

.search-input {
  min-width: 240px;
  font-size: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border-radius: 8px;
  overflow: hidden;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  padding: 0 12px;
  background: rgba(255, 255, 255, 0.9);
}

.search-input:hover {
  transform: translateY(-2px);
}

.search-glow {
  position: absolute;
  bottom: -3px;
  left: 10%;
  width: 80%;
  height: 4px;
  background: linear-gradient(90deg, transparent, rgba(0, 102, 255, 0.3), transparent);
  border-radius: 2px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.search-wrapper:hover .search-glow {
  opacity: 1;
}

.search-icon {
  color: #0066FF;
  font-size: 16px;
}

.user-cards-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.ranking-badge {
  position: absolute;
  top: 0;
  right: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
  color: #606266;
  border-radius: 0 12px 0 8px;
  font-weight: bold;
  box-shadow: -2px 2px 6px rgba(0, 0, 0, 0.05);
}

.user-card:nth-child(1) .ranking-badge {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: white;
}

.user-card:nth-child(2) .ranking-badge {
  background: linear-gradient(135deg, #C0C0C0, #A9A9A9);
  color: white;
}

.user-card:nth-child(3) .ranking-badge {
  background: linear-gradient(135deg, #CD7F32, #8B4513);
  color: white;
}

.user-card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 16px;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0066FF, #4ECDC4);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  box-shadow: 0 4px 10px rgba(0, 102, 255, 0.2);
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
}

.user-phone {
  font-size: 14px;
  font-weight: 400;
  color: #666;
  margin-bottom: 6px;
}

.total-token {
  font-size: 18px;
  font-weight: 700;
  color: #0066FF;
  margin-bottom: 8px;
  background: linear-gradient(90deg, rgba(0, 102, 255, 0.1), transparent);
  padding: 4px 12px;
  border-radius: 6px;
  display: inline-block;
}

.user-card:nth-child(1) .total-token {
  color: #FF8C00;
  background: linear-gradient(90deg, rgba(255, 140, 0, 0.1), transparent);
}

.user-card:nth-child(2) .total-token {
  color: #778899;
  background: linear-gradient(90deg, rgba(119, 136, 153, 0.1), transparent);
}

.user-card:nth-child(3) .total-token {
  color: #8B4513;
  background: linear-gradient(90deg, rgba(139, 69, 19, 0.1), transparent);
}

.user-stats {
  display: flex;
  gap: 20px;
  color: #666;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.modules-container {
  padding-top: 4px;
}

.modules-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 12px;
  color: #333;
  position: relative;
  display: inline-block;
}

.modules-title::after {
  content: "";
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, var(--primary-color, #0066ff), transparent);
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.module-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  transition: all 0.3s ease;
}

.module-item:hover {
  background: #f0f2f5;
  transform: translateY(-2px);
}

.module-item.high-usage {
  border-left: 3px solid #F56C6C;
}

.module-item.medium-usage {
  border-left: 3px solid #E6A23C;
}

.module-item.normal-usage {
  border-left: 3px solid #409EFF;
}

.module-item.low-usage {
  border-left: 3px solid #67C23A;
}

.module-icon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.module-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.module-details {
  flex: 1;
}

.module-name {
  font-weight: 500;
  font-size: 14px;
  margin-bottom: 6px;
  color: #333;
}

.usage-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
}

.usage-stat {
  display: flex;
  align-items: center;
  gap: 4px;
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
  height: 4px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color, #0066ff);
  border-radius: 2px;
  transition: width 0.5s ease;
}

.high-usage .progress-fill {
  background: linear-gradient(90deg, #F56C6C, #FF9F9F);
}

.medium-usage .progress-fill {
  background: linear-gradient(90deg, #E6A23C, #FFD166);
}

.normal-usage .progress-fill {
  background: linear-gradient(90deg, #409EFF, #7EB0FF);
}

.low-usage .progress-fill {
  background: linear-gradient(90deg, #67C23A, #9FE288);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  border: 1px dashed #dcdfe6;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #DCDFE6;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .user-stats {
    flex-direction: column;
    gap: 8px;
  }
  
  .modules-grid {
    grid-template-columns: 1fr;
  }
}
</style>