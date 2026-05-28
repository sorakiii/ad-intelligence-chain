<template>
  <div class="recent-history">
    <div class="list-header">
      <h2>最近打开</h2>
    </div>

    <div class="list-content">
      <el-empty
        v-if="!loading && !sessions.length"
        description="暂无最近打开的会话"
      />
      <div v-else-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
        <el-skeleton :rows="3" animated />
        <el-skeleton :rows="3" animated />
      </div>
      <div v-else class="session-items">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="session-item"
          @click="openSession(session)"
        >
          <div class="session-main">
            <div class="session-header">
              <div class="role-info">
                <el-avatar
                  :size="40"
                  :src="session.role_icon"
                  :alt="session.title"
                />
                <div class="role-meta">
                  <div class="title-wrapper">
                    <span class="session-title">{{ session.title }}</span>
                  </div>
                  <span class="session-type">{{
                    session.type === "single_role"
                      ? "单角色会话"
                      : session.type === "targeted"
                      ? "定向需求会话"
                      : "超级战队会话"
                  }}</span>
                </div>
              </div>
              <div class="session-time">
                {{ formatTime(session.last_time) }}
              </div>
            </div>
            <div class="session-message">{{ session.last_message }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getRecentSessions } from "@/api/chat";
import { formatTime } from "@/utils/time";
const router = useRouter();
const loading = ref(true);
const sessions = ref([]);

// 加载最近会话
const loadRecentSessions = async () => {
  try {
    loading.value = true;
    const response = await getRecentSessions(5); // 获取10条最近记录
    if (response.data) {
      sessions.value = response.data.sessions;
    }
  } catch (error) {
    console.error("获取最近会话失败:", error);
  } finally {
    loading.value = false;
  }
};

// 打开会话
const openSession = (session) => {
  router.push(`/workspace/history/single-role/${session.id}`);
};

onMounted(() => {
  loadRecentSessions();
});
</script>

<style scoped>
.recent-history {
  height: 100%;
  padding: 24px;
  background: white;
  border-radius: 12px;
}

.list-header {
  margin-bottom: 24px;
}

.list-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.loading-container {
  padding: 20px;
}

.session-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.session-item {
  padding: 16px;
  border-radius: 8px;
  background: var(--bg-color);
  cursor: pointer;
  transition: all 0.2s ease;
}

.session-item:hover {
  background: var(--bg-hover);
}

.session-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.role-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.session-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
}

.session-type {
  font-size: 12px;
  color: var(--text-secondary);
}

.session-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.session-message {
  font-size: 14px;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.list-content {
  height: calc(
    100% - 72px
  ); /* 减去header的高度(24px + 24px margin-bottom)和padding(24px) */
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
}

/* 自定义滚动条样式 */
.list-content::-webkit-scrollbar {
  width: 6px;
}

.list-content::-webkit-scrollbar-track {
  background: transparent;
}

.list-content::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.list-content::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.3);
}
</style>
