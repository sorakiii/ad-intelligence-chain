<template>
  <div class="chat-sessions">
    <!-- 会话列表头部 -->
    <div class="sessions-header">
      <h2>会话列表</h2>
      <div class="header-actions">
        <button class="filter-btn" @click="showFilterMenu = !showFilterMenu">
          <span>{{ currentFilter.label }}</span>
          <span class="arrow-down">▼</span>
        </button>
        <!-- 筛选菜单 -->
        <div class="filter-menu" v-if="showFilterMenu">
          <div
            v-for="filter in filters"
            :key="filter.value"
            class="filter-item"
            :class="{ active: currentFilter.value === filter.value }"
            @click="selectFilter(filter)"
          >
            {{ filter.label }}
          </div>
        </div>
      </div>
    </div>

    <!-- 会话列表 -->
    <div class="sessions-list">
      <div
        v-for="session in filteredSessions"
        :key="session.id"
        class="session-item"
        :class="{ active: currentSession?.id === session.id }"
        @click="selectSession(session)"
      >
        <!-- 角色头像 -->
        <div class="session-avatar">
          <img
            v-if="isImageUrl(session.role_icon)"
            :src="session.role_icon"
            :alt="session.role_name"
            @error="handleImageError"
          />
          <span v-else class="fallback-icon">{{
            getFallbackIcon(session.role_name)
          }}</span>
        </div>

        <!-- 会话信息 -->
        <div class="session-info">
          <div class="session-title">
            <span
              class="title-text"
              :contenteditable="editingSessionId === session.id"
              @blur="handleTitleBlur($event, session)"
              @keydown.enter.prevent="handleTitleEnter($event, session)"
              ref="titleEditor"
              >{{ session.title }}</span
            >
            <div class="session-actions">
              <button
                class="action-btn star-btn"
                :class="{ active: session.isStarred }"
                @click.stop="toggleStar(session)"
              >
                ⭐
              </button>
              <button
                class="action-btn more-btn"
                @click.stop="showSessionMenu(session)"
              >
                ⋮
              </button>
            </div>
          </div>
          <div class="session-meta">
            <span class="role-name">{{ session.role_name }}</span>
            <span class="message-count">{{ session.message_count }}条对话</span>
            <span class="last-time">{{ formatTime(session.last_time) }}</span>
          </div>
          <div class="last-message">{{ session.last_message }}</div>
        </div>

        <!-- 会话操作菜单 -->
        <div
          v-if="activeMenuSessionId === session.id"
          class="session-menu"
          @click.stop
        >
          <div class="menu-item" @click="renameSession(session)">
            <span>✏️</span>重命名
          </div>
          <div class="menu-item" @click="archiveSession(session)">
            <span>📦</span>{{ session.isArchived ? "取消归档" : "归档" }}
          </div>
          <div class="menu-item delete" @click="deleteSession(session)">
            <span>🗑️</span>删除
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredSessions.length === 0" class="empty-state">
      <div class="empty-icon">💭</div>
      <div class="empty-text">暂无会话记录</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { formatTime } from "@/utils/time";

// 会话类型定义
interface ChatSession {
  id: string;
  title: string;
  role_id: string;
  role_name: string;
  role_icon: string;
  last_message: string;
  last_time: number;
  message_count: number;
  is_starred: boolean;
  is_archived: boolean;
}

// Props 定义
const props = defineProps<{
  sessions: ChatSession[];
  currentSession?: ChatSession;
}>();

const emit = defineEmits<{
  (e: "select", session: ChatSession): void;
  (e: "rename", session: ChatSession, newTitle: string): void;
  (e: "delete", session: ChatSession): void;
  (e: "star", session: ChatSession): void;
  (e: "archive", session: ChatSession): void;
}>();

// 状态管理
const showFilterMenu = ref(false);
const activeMenuSessionId = ref<string | null>(null);
const editingSessionId = ref<string | null>(null);
const titleEditor = ref<HTMLElement | null>(null);

// 筛选选项
const filters = [
  { label: "全部会话", value: "all" },
  { label: "已收藏", value: "starred" },
  { label: "已归档", value: "archived" },
];
const currentFilter = ref(filters[0]);

// 筛选会话列表
const filteredSessions = computed(() => {
  return props.sessions.filter((session) => {
    switch (currentFilter.value.value) {
      case "starred":
        return session.is_starred;
      case "archived":
        return session.is_archived;
      default:
        return !session.is_archived;
    }
  });
});

// 选择筛选器
const selectFilter = (filter: (typeof filters)[0]) => {
  currentFilter.value = filter;
  showFilterMenu.value = false;
};

// 选择会话
const selectSession = (session: ChatSession) => {
  emit("select", session);
};

// 显示会话菜单
const showSessionMenu = (session: ChatSession) => {
  activeMenuSessionId.value = session.id;
  // 点击外部关闭菜单
  const closeMenu = (e: MouseEvent) => {
    if (!(e.target as Element).closest(".session-menu")) {
      activeMenuSessionId.value = null;
      document.removeEventListener("click", closeMenu);
    }
  };
  document.addEventListener("click", closeMenu);
};

// 重命名会话
const renameSession = (session: ChatSession) => {
  editingSessionId.value = session.id;
  activeMenuSessionId.value = null;
  // 等待 DOM 更新后聚焦
  setTimeout(() => {
    const editor = titleEditor.value;
    if (editor) {
      editor.focus();
      // 选中所有文本
      window.getSelection()?.selectAllChildren(editor);
    }
  });
};

// 处理标题编辑完成
const handleTitleBlur = (event: FocusEvent, session: ChatSession) => {
  const target = event.target as HTMLElement;
  const newTitle = target.innerText.trim();
  if (newTitle && newTitle !== session.title) {
    emit("rename", session, newTitle);
  }
  editingSessionId.value = null;
};

// 处理标题编辑回车
const handleTitleEnter = (event: KeyboardEvent, session: ChatSession) => {
  const target = event.target as HTMLElement;
  target.blur();
};

// 收藏/取消收藏
const toggleStar = (session: ChatSession) => {
  emit("star", session);
};

// 归档/取消归档
const archiveSession = (session: ChatSession) => {
  emit("archive", session);
  activeMenuSessionId.value = null;
};

// 删除会话
const deleteSession = (session: ChatSession) => {
  if (confirm("确定要删除这个会话吗？")) {
    emit("delete", session);
  }
  activeMenuSessionId.value = null;
};

// 图片相关函数
const isImageUrl = (url?: string) => {
  if (!url) return false;
  const obsPattern = /^https?:\/\/[^/]+\.obs\.[^/]+\.(huaweicloud\.com|myhuaweicloud\.com)/;
  const imagePattern = /\.(jpg|jpeg|png|webp|avif|gif|svg|bmp|tiff)(\?.*)?$/i;
  const dataUrlPattern = /^data:image\//;
  return obsPattern.test(url) || imagePattern.test(url) || dataUrlPattern.test(url);
};

const getFallbackIcon = (title?: string) => {
  if (!title) return "👤";
  const emojiMap: Record<string, string> = {
    营销: "📢",
    设计: "🎨",
    写作: "✍️",
    数据: "📊",
    策划: "📋",
    分析: "🔍",
    创意: "💡",
    技术: "💻",
  };
  for (const [key, emoji] of Object.entries(emojiMap)) {
    if (title.includes(key)) return emoji;
  }
  return title.charAt(0);
};

const handleImageError = (e: Event) => {
  const target = e.target as HTMLImageElement;
  target.style.display = "none";
  target.parentElement?.classList.add("show-fallback");
};
</script>

<style scoped>
.chat-sessions {
  width: 300px;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color);
}

.sessions-header {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  height: 56px;
}

.sessions-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  position: relative;
}

.filter-btn {
  padding: 6px 12px;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.arrow-down {
  font-size: 10px;
}

.filter-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.filter-item {
  padding: 8px 16px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  white-space: nowrap;
}

.filter-item:hover {
  background: var(--hover-color);
}

.filter-item.active {
  color: var(--primary-color);
  background: var(--hover-color);
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  height: calc(100% - 48px);
}

.session-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  gap: 12px;
  position: relative;
  transition: all 0.2s ease;
  height: 80px;
  margin-bottom: 8px;
}

.session-item:hover {
  background: var(--hover-color);
}

.session-item.active {
  background: var(--hover-color);
}

.session-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgb(235, 242, 254);
  overflow: hidden;
  flex-shrink: 0;
  align-self: center;
}

.session-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.fallback-icon {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: var(--primary-color);
}

.session-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 4px 0;
}

.session-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-text {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: calc(100% - 60px);
}

[contenteditable="true"].title-text {
  outline: none;
  border-bottom: 2px solid var(--primary-color);
  padding: 0 2px;
}

.session-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .session-actions {
  opacity: 1;
}

.action-btn {
  padding: 4px;
  background: none;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.star-btn.active {
  color: #f59e0b;
}

.session-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.role-name {
  font-weight: 500;
}

.message-count {
  color: #999;
}

.last-time {
  color: #999;
}

.last-message {
  font-size: 14px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  line-height: 1.5;
}

.session-menu {
  position: absolute;
  top: 40px;
  right: 16px;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.menu-item {
  padding: 8px 16px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 8px;
}

.menu-item:hover {
  background: var(--hover-color);
}

.menu-item.delete {
  color: #ef4444;
}

.menu-item.delete:hover {
  background: #fef2f2;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 14px;
}
</style> 