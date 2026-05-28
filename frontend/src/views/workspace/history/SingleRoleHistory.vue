<!-- 
  @file 单角色会话历史记录视图
  @description 显示单角色服务的历史会话记录
-->
<template>
  <div class="history-view">
    <!-- 会话列表 -->
    <div class="session-list" :class="{ collapsed: sessionListCollapsed }">
      <!-- 收起/展开按钮 -->
      <div class="collapse-btn" @click="sessionListCollapsed = !sessionListCollapsed">
        <el-icon>
          <ArrowLeft v-if="!sessionListCollapsed" />
          <ArrowRight v-else />
        </el-icon>
      </div>
      <!-- 仅收起时显示头像列表 -->
      <div v-if="sessionListCollapsed" class="collapsed-avatar-list">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="collapsed-avatar-item"
          :class="{ active: currentSession?.id === session.id }"
          @click="openSession(session)"
        >
          <el-avatar :size="40" :src="session.role_icon" :alt="session.role_name" />
        </div>
      </div>
      <!-- 展开时显示原内容 -->
      <template v-else>
        <div class="list-header">
          <h2>单角色会话历史</h2>
          <div class="filter-tabs">
            <div
              class="filter-tab"
              :class="{ active: filter === 'all' }"
              @click="filter = 'all'"
            >
              全部会话
            </div>
            <div
              class="filter-tab"
              :class="{ active: filter === 'starred' }"
              @click="filter = 'starred'"
            >
              <el-icon><Star /></el-icon>
              已收藏
            </div>
            <div
              class="filter-tab"
              :class="{ active: filter === 'archived' }"
              @click="filter = 'archived'"
            >
              <el-icon><Folder /></el-icon>
              已归档
            </div>
          </div>
        </div>

        <div class="list-content">
          <el-empty
            v-if="!loading && !sessions.length"
            description="暂无会话记录"
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
              :class="{ active: currentSession?.id === session.id }"
              @click="openSession(session)"
            >
              <div class="session-main">
                <div class="session-header">
                  <div class="role-info" @click.stop="openSession(session)">
                    <el-avatar
                      :size="40"
                      :src="session.role_icon"
                      :alt="session.role_name"
                    />
                    <div class="role-meta">
                      <div class="title-wrapper">
                        <span
                          v-if="!isEditing || editingSessionId !== session.id"
                          class="role-name"
                          >{{ session.title }}</span
                        >
                        <el-input
                          v-else
                          v-model="editingTitle"
                          size="small"
                          v-focus
                          @blur="handleRename(session)"
                          @keyup.enter="handleRename(session)"
                          @keyup.esc="cancelEditing"
                          placeholder="请输入会话标题"
                        />
                      </div>
                      <div class="role-name-display">
                        <span class="role-value">{{
                          session.role_name || "未知角色"
                        }}</span>
                      </div>
                      <span class="session-time">{{
                        formatTime(session.last_time)
                      }}</span>
                    </div>
                  </div>
                  <div class="session-actions">
                    <div class="action-group">
                      <el-button
                        class="action-btn star-btn"
                        :class="{ active: session.is_starred }"
                        :icon="session.is_starred ? Star : StarFilled"
                        circle
                        @click.stop="toggleStar(session)"
                      />
                      <el-button
                        class="action-btn archive-btn"
                        :class="{ active: session.is_archived }"
                        :icon="session.is_archived ? Folder : FolderOpened"
                        circle
                        @click.stop="toggleArchive(session)"
                      />
                      <el-dropdown
                        trigger="click"
                        @command="handleCommand($event, session)"
                      >
                        <el-button
                          class="action-btn more-btn"
                          :icon="More"
                          circle
                        />
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item command="rename"
                              >重命名</el-dropdown-item
                            >
                            <el-dropdown-item command="delete" divided>
                              <span style="color: var(--el-color-danger)"
                                >删除</span
                              >
                            </el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </div>
                  </div>
                </div>
                <div class="session-content" @click="openSession(session)">
                  <p class="last-message">{{ session.lastMessage }}</p>
                  <div class="session-footer">
                    <span class="message-count"
                      >共 {{ session.message_count }} 条对话</span
                    >
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="list-footer">
          <div class="pagination-left">
            <span class="total">{{ total }} 条会话</span>
          </div>
          <el-pagination
            v-model:current-page="page"
            :page-size="size"
            :total="total"
            layout="prev, pager, next"
            :disabled="loading"
            @current-change="handlePageChange"
            small
          />
          <div class="pagination-right">
            <el-select
              v-model="size"
              size="small"
              @change="handleSizeChange"
              :disabled="loading"
              class="page-size-select"
            >
              <el-option
                v-for="item in [10, 20, 50]"
                :key="item"
                :label="`${item}条/页`"
                :value="item"
              />
            </el-select>
          </div>
        </div>
      </template>
    </div>

    <!-- 会话详情 -->
    <div class="session-detail">
      <router-view v-slot="{ Component }" :key="route.params.sessionId">
        <component :is="Component" :session="currentSession">
          <div class="message-avatar">
            <el-avatar
              :src="currentSession?.roleIcon"
              :alt="currentSession?.roleName"
            />
          </div>
          <div class="message-content">
            <div class="message-header">
              <span class="sender">{{
                currentSession?.roleName || "AI助手"
              }}</span>
              <span class="time">{{
                formatTime(currentSession?.lastTime)
              }}</span>
            </div>
            <div class="message-text">{{ currentSession?.lastMessage }}</div>
            <div v-if="currentSession?.fileIds?.length" class="message-files">
              <!-- TODO: 实现文件展示 -->
            </div>
            <div
              v-if="currentSession?.type === 'assistant'"
              class="message-feedback"
            >
              <el-rate
                v-model="currentSession.feedback_rating"
                :max="1"
                :colors="['#409EFF', '#909399', '#909399']"
                @change="handleFeedback(currentSession)"
              />
            </div>
          </div>
        </component>
      </router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import {
  getSessionList,
  toggleSessionStar,
  toggleSessionArchive,
  renameSession,
  deleteSession,
} from "@/api/chat";
import type { Session, SessionFilter } from "@/types/chat";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Star,
  StarFilled,
  Folder,
  FolderOpened,
  More,
  ArrowLeft,
  ArrowRight,
} from "@element-plus/icons-vue";
import config from "@/config";
import { showErrorMessage, showSuccessMessage } from "@/utils/message";
import { formatTime } from "@/utils/time";

const router = useRouter();
const route = useRoute();
const filter = ref<SessionFilter>("all");
const page = ref(1);
const size = ref(20);
const total = ref(0);
const sessions = ref<Session[]>([]);
const loading = ref(false);
const currentSession = ref<Session | null>(null);
const isEditing = ref(false);
const editingTitle = ref("");
const editingSessionId = ref("");

// 添加总数统计
const totalCounts = ref({
  all: 0,
  starred: 0,
  archived: 0,
});

const file = ref(null);
const uploading = ref(false);

/**
 * 控制会话列表展开/收起
 * @type {import('vue').Ref<boolean>}
 */
const sessionListCollapsed = ref(false);

// 加载会话列表
const loadSessions = async () => {
  if (loading.value) return;
  loading.value = true;
  try {
    // 加载当前筛选条件的会话
    const response = await getSessionList({
      type: "single_role",
      filter: filter.value,
      page: page.value,
      size: size.value,
    });

    if (response?.data) {
      sessions.value = response.data.sessions || [];
      total.value = response.data.total || 0;

      // 更新对应的计数
      if (filter.value === "all") {
        totalCounts.value.all = response.data.total;
      } else if (filter.value === "starred") {
        totalCounts.value.starred = response.data.total;
      } else if (filter.value === "archived") {
        totalCounts.value.archived = response.data.total;
      }
    } else {
      sessions.value = [];
      total.value = 0;
    }
  } catch (error) {
    console.error("获取会话列表失败:", error);
    ElMessage.error("获取会话列表失败");
    sessions.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
};

// 初始加载时获取所有计数
const loadAllCounts = async () => {
  try {
    // 获取全部会话数量
    const allResponse = await getSessionList({
      type: "single_role",
      filter: "all",
      page: 1,
      size: 1,
    });
    totalCounts.value.all = allResponse?.data?.total || 0;

    // 获取已收藏会话数量
    const starredResponse = await getSessionList({
      type: "single_role",
      filter: "starred",
      page: 1,
      size: 1,
    });
    totalCounts.value.starred = starredResponse?.data?.total || 0;

    // 获取已归档会话数量
    const archivedResponse = await getSessionList({
      type: "single_role",
      filter: "archived",
      page: 1,
      size: 1,
    });
    totalCounts.value.archived = archivedResponse?.data?.total || 0;
  } catch (error) {
    console.error("获取会话计数失败:", error);
  }
};

onMounted(() => {
  loadAllCounts();
  loadSessions();
});

// 切换收藏状态
const toggleStar = async (session: Session) => {
  try {
    await toggleSessionStar(session.id, !session.isStarred);
    session.isStarred = !session.isStarred;
    ElMessage.success(session.isStarred ? "已收藏" : "已取消收藏");
  } catch (error) {
    console.error("收藏操作失败:", error);
    ElMessage.error("操作失败");
  }
};

// 切换归档状态
const toggleArchive = async (session: Session) => {
  try {
    await toggleSessionArchive(session.id, !session.isArchived);
    session.isArchived = !session.isArchived;
    ElMessage.success(session.isArchived ? "已归档" : "已取消归档");
  } catch (error) {
    console.error("归档操作失败:", error);
    ElMessage.error("操作失败");
  }
};

// 打开会话
const openSession = (session: Session) => {
  currentSession.value = session;
  router.push({
    name: "chatDetail",
    params: { sessionId: session.id, activeBranchId: session.active_branch_id },
  });
};

// 处理分页大小变化
const handleSizeChange = (newSize: number) => {
  size.value = newSize;
  page.value = 1;
  loadSessions();
};

// 处理页码变化
const handlePageChange = (newPage: number) => {
  page.value = newPage;
  loadSessions();
};

// 监听筛选条件变化
watch(
  () => filter.value,
  (newFilter) => {
    page.value = 1;
    loadSessions();
  },
  { immediate: true }
);

// 开始编辑
const startEditing = (session: Session) => {
  editingSessionId.value = session.id;
  editingTitle.value = session.title;
  isEditing.value = true;
};

// 取消编辑
const cancelEditing = () => {
  isEditing.value = false;
  editingTitle.value = "";
  editingSessionId.value = "";
};

// 处理重命名
const handleRename = async (session: Session) => {
  if (!editingTitle.value.trim()) {
    cancelEditing();
    return;
  }

  try {
    const { data } = await renameSession(session.id, {
      title: editingTitle.value.trim(),
      autoGenerate: false,
    });

    if (data) {
      session.title = data.title;
      ElMessage.success("重命名成功");
    }
  } catch (error) {
    console.error("重命名失败:", error);
    ElMessage.error("重命名失败");
  } finally {
    cancelEditing();
  }
};

// 处理删除
const handleDelete = async (session: Session) => {
  try {
    await ElMessageBox.confirm(
      "确定要删除这个会话吗？删除后无法恢复。",
      "删除确认",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await deleteSession(session.id);
    showSuccessMessage("删除成功");
    loadSessions();
  } catch (error) {
    if (error !== "cancel") {
      console.error("删除失败:", error);
      showErrorMessage("删除失败");
    }
  }
};

// 处理下拉菜单命令
const handleCommand = (command: string, session: Session) => {
  switch (command) {
    case "rename":
      startEditing(session);
      break;
    case "delete":
      handleDelete(session);
      break;
  }
};

const handleFileChange = (event) => {
  const selectedFile = event.target.files[0];
  if (selectedFile) {
    file.value = selectedFile;
  }
};

const uploadFile = async () => {
  if (!file.value) {
    ElMessage.warning("请选择一个文件");
    return;
  }

  const formData = new FormData();
  formData.append("file", file.value);

  try {
    uploading.value = true;
    const response = await fetch(`${config.baseURL}/api/chat/files`, {
      method: "POST",
      body: formData,
    });

    const result = await response.json();
    if (result.code === 0) {
      ElMessage.success("上传成功");
      // Handle success (e.g., store file info)
    } else {
      ElMessage.error(result.message || "上传失败");
    }
  } catch (error) {
    ElMessage.error("上传失败");
  } finally {
    uploading.value = false;
  }
};

const handleFeedback = (session: Session) => {
  // Implementation of handleFeedback function
};
</script>

<style scoped>
.history-view {
  height: 100%;
  display: flex;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  border: 5px solid var(--el-border-color-light);
}

.session-list {
  width: 360px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--el-border-color-light);
  background: white;
  z-index: 1;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  transition: width 0.2s;
  position: relative;
}

.list-header {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
  background: var(--el-fill-color-blank);
}

.list-header h2 {
  margin: 0 0 12px;
  font-size: 20px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.filter-tabs {
  display: flex;
  gap: 8px;
  padding: 4px 0;
  justify-content: space-around;
}

.filter-tab {
  padding: 8px 16px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 8px;
  background: var(--el-fill-color-blank);
  border: 1px solid var(--el-border-color-light);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
}

.filter-tab:hover {
  background: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-5);
}

.filter-tab.active {
  background: var(--el-color-primary);
  color: white;
  border-color: var(--el-color-primary);
}

.filter-tab .el-icon {
  font-size: 16px;
  margin-right: 4px;
}

.filter-tab .count {
  font-size: 13px;
  font-weight: 600;
  background: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
  white-space: nowrap;
}

.list-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.session-items {
  padding: 20px;
}

.session-item {
  padding: 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.session-item:hover {
  background: var(--el-fill-color-light);
  border-color: var(--el-border-color);
}

.session-item.active {
  background: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary-light-7);
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
  margin-bottom: 12px;
}

.role-info {
  display: flex;
  gap: 12px;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.role-meta {
  flex: 1;
  min-width: 0;
}

.title-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.role-name {
  font-weight: 500;
  font-size: 15px;
  color: var(--el-text-color-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 4px 8px;
  margin: -4px -8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.role-name:hover {
  background: var(--el-fill-color);
}

.role-name-display {
  margin: 2px 0 4px 0;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.role-label {
  color: var(--el-text-color-secondary);
  font-weight: 400;
}

.role-value {
  color: var(--el-color-primary);
  font-weight: 500;
  background: var(--el-color-primary-light-9);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.session-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.session-actions {
  display: flex;
  opacity: 0;
  transition: opacity 0.2s;
}

.action-group {
  display: inline-flex;
  gap: 8px;
  background: var(--el-fill-color-light);
  padding: 2px;
  border-radius: 6px;
}

.session-item:hover .session-actions {
  opacity: 1;
}

.action-btn {
  padding: 6px;
  height: 28px;
  width: 28px;
  border: none;
  color: var(--el-text-color-secondary);
  background: transparent;
  margin: 0;
}

.action-btn:hover {
  background: white;
  color: var(--el-color-primary);
}

.star-btn.active {
  color: var(--el-color-warning);
  background: white;
}

.archive-btn.active {
  color: var(--el-color-info);
  background: white;
}

.more-btn:hover {
  color: var(--el-color-primary);
}

.session-content {
  padding-left: 52px;
}

.last-message {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-regular);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.5;
}

.session-footer {
  margin-top: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.list-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--el-fill-color-blank);
}

.pagination-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.pagination-right {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.total {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

:deep(.el-pagination) {
  justify-content: center;
  --el-pagination-button-width: 28px;
  --el-pagination-button-height: 28px;
  white-space: nowrap;
}

.page-size-select {
  width: 95px;
}

.page-size-select :deep(.el-input__wrapper) {
  padding: 0 8px;
}

.page-size-select :deep(.el-input__inner) {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.loading-container {
  padding: 20px;
}

.session-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: white;
}

:deep(.el-input) {
  width: 300px;
}

:deep(.el-input__inner) {
  font-size: 15px;
  font-weight: 500;
  height: 32px;
  padding: 0 12px;
}

.chat-input {
  border-top: 1px solid var(--el-border-color-light);
  padding: 16px 24px;
  background: white;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.el-input__inner {
  border: 1px solid var(--el-border-color-light);
  box-shadow: none;
  font-size: 14px;
  padding: 8px;
  border-radius: 4px;
}

.el-button {
  height: auto;
  border-radius: 4px;
  background-color: var(--el-color-primary);
  color: white;
}

.el-button:hover {
  background-color: var(--el-color-primary-light);
}

.chat-dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: calc(100% - 48px);
  max-width: 1200px;
  height: 85vh;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  z-index: 1000;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.role-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-info h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 40px;
  background: white;
}

.message-container {
  display: flex;
  padding: 24px 0;
  margin: 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.message-container.assistant {
  background-color: rgb(247, 247, 248);
}

.message-container.user {
  background-color: white;
}

.message-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 32px;
  width: auto;
  display: flex;
  justify-content: flex-start;
}

.user .message-content {
  justify-content: flex-end;
}

.message-text {
  display: inline-block;
  max-width: 80%;
  font-size: 15px;
  line-height: 1.6;
  color: rgb(64, 65, 78);
  white-space: pre-wrap;
  word-wrap: break-word;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgb(247, 247, 248);
}

.user .message-text {
  background: rgb(25, 195, 125);
  color: white;
}

.chat-input {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding: 24px 0;
  background: white;
}

.input-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 32px;
}

.model-selector {
  margin-bottom: 12px;
}

.input-wrapper {
  position: relative;
  background: white;
  border-radius: 12px;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.el-textarea__inner) {
  padding: 16px;
  font-size: 15px;
  line-height: 1.6;
  border: none;
  resize: none;
  box-shadow: none;
}

:deep(.el-textarea__inner:focus) {
  box-shadow: none;
}

:deep(.el-radio-group) {
  display: inline-flex;
  background: #f9f9f9;
  padding: 4px;
  border-radius: 8px;
}

:deep(.el-radio-button__inner) {
  border: none;
  padding: 6px 16px;
  font-size: 13px;
  border-radius: 6px !important;
  box-shadow: none !important;
  background: transparent;
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: white;
  color: #333;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}

:deep(.el-radio-button:first-child .el-radio-button__inner) {
  border-radius: 6px !important;
}

:deep(.el-radio-button:last-child .el-radio-button__inner) {
  border-radius: 6px !important;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 8px 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.el-button {
  padding: 8px 16px;
  height: auto;
  font-size: 14px;
}

.el-button--primary {
  background-color: rgb(25, 195, 125);
  border-color: rgb(25, 195, 125);
}

.el-button--primary:hover {
  background-color: rgb(22, 175, 112);
  border-color: rgb(22, 175, 112);
}

.attachments {
  max-width: 800px;
  margin: 12px auto 0;
  padding: 0 32px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 12px;
}

.file-item .el-button {
  padding: 0;
  color: #999;
}

.file-item .el-button:hover {
  color: #ff4d4f;
}

@media (max-width: 768px) {
  .input-container {
    padding: 0 16px;
  }

  .attachments {
    padding: 0 16px;
  }
}

.collapse-btn {
  position: absolute;
  right: 0;
  top: 10px;
  z-index: 10;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: white;
  border-radius: 8px 0 0 8px;
  box-shadow: -1px 0 4px rgba(0,0,0,0.05);
  border: 1px solid var(--el-border-color-light);
}

.session-list.collapsed {
  width: 60px !important;
  min-width: 60px !important;
}

.session-list.collapsed .list-header,
.session-list.collapsed .list-footer,
.session-list.collapsed .session-items,
.session-list.collapsed .filter-tabs,
.session-list.collapsed .list-content {
  display: none !important;
}

.collapsed-avatar-list {
  margin-top: 48px;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  overflow-y: auto;
  max-height: calc(100vh - 48px);
}

.collapsed-avatar-item {
  cursor: pointer;
  border-radius: 50%;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}

.collapsed-avatar-item.active {
  border-color: var(--el-color-primary);
}
</style> 
