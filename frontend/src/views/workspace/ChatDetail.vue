<template>
  <div class="chat-detail">
    <div class="chat-header">
      <div class="role-info">
        <el-avatar :src="session?.role_icon" :alt="session?.role_name" />
        <div class="title-container">
          <div class="title-wrapper">
            <h2>{{ session?.title || "会话详情" }}</h2>
            <div class="title-actions">
              <el-button
                type="text"
                icon="Refresh"
                @click="refreshSession"
                :loading="loading"
                title="刷新会话信息"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-messages" ref="messagesRef">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
        <el-skeleton style="margin-left: 50%" :rows="2" animated />
        <el-skeleton :rows="2" animated />
        <el-skeleton style="margin-left: 50%" :rows="3" animated />
      </div>

      <template v-else>
        <div v-if="hasMore" class="load-more">
          <el-button :loading="loadingMore" @click="loadMore"
            >加载更多</el-button
          >
        </div>

        <template v-if="messages.length">
          <div
            v-for="message in messages"
            :key="message.id"
            class="message-item"
            :class="[
              message.type,
              {
                inferring: message.inferring,
                edited: message.isEdited,
              },
            ]"
          >
            <div v-if="message.type === 'user'" class="message-header">
              <div class="avatar user-avatar">
                <span class="avatar-placeholder">You</span>
              </div>
              <div class="message-info">
                <div class="message-time">
                  {{ formatTime(message.timestamp) }}
                </div>
              </div>
            </div>

            <div v-else class="message-header">
              <div class="avatar assistant-avatar">
                <img
                  v-if="session?.role_icon"
                  :src="session?.role_icon"
                  alt="AI"
                />
                <span v-else class="avatar-placeholder">{{
                  getFallbackIcon(role?.title)
                }}</span>
              </div>
              <div class="message-info">
                <div class="message-sender">{{ role?.title || "助手" }}</div>
                <div class="message-time">
                  {{ formatTime(message.timestamp) }}
                </div>
              </div>
            </div>

            <div class="message-content-wrapper">
              <div
                v-if="
                  message.type === 'user' ||
                  (message.type === 'assistant' &&
                    message.api_status !== 'error')
                "
                class="message-content"
              >
                <!-- 用户消息显示纯文本 -->
                <template v-if="message.type === 'user'">
                  {{ message.content || "" }}
                </template>
                <!-- 助手消息支持HTML渲染 -->
                <template v-else>
                  <div
                    v-html="
                      message.inferring && !message.content
                        ? '<div class=\'inferring-indicator\'>正在推理中...</div>'
                        : message.content
                        ? formatMessageContent(message.content)
                        : '<div class=\'empty-response\'>暂无回复内容</div>'
                    "
                  ></div>
                </template>
              </div>

              <div
                v-else-if="
                  message.type === 'assistant' && message.api_status === 'error'
                "
                class="error-message"
              >
                {{ message.errorMessage || "响应处理异常，请尝试重新发送消息" }}
              </div>
              <div class="message-actions">
                <template v-if="message.type === 'user'">
                  <el-button
                    class="edit-btn"
                    type="text"
                    size="small"
                    @click="startEditing(message)"
                    :disabled="!!editingMessageId"
                  >
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                </template>
                <el-button
                  class="copy-btn"
                  type="text"
                  size="small"
                  @click="copyText(message.content)"
                >
                  <el-icon><Document /></el-icon>
                  复制
                </el-button>
                <!-- 添加 HTML 预览组件 -->
                <HtmlPreview
                  v-if="
                    message.type === 'assistant' &&
                    (session?.role_id === 27 || session?.role_id === 25)
                  "
                  :message-id="message.message_id"
                  :html="
                    messageHtmlMap[message.id] || {
                      html_code: '',
                      status: '',
                      id: 0,
                      type: 'message',
                      session_id: 0,
                      message_id: 0,
                    }
                  "
                  :content="message.content"
                  :model="selectedModel"
                  :inferring="message.inferring"
                  @update:html="
                    (html) => {
                      messageHtmlMap[message.id] = html;
                    }
                  "
                />

                <el-button
                  v-if="session?.role_id === 28 && message.type === 'assistant'"
                  class="eqmj-btn"
                  type="text"
                  size="small"
                  @click="openEQMJ"
                >
                  <el-icon><Document /></el-icon>
                  跳转EQMJ
                </el-button>

                <!-- 添加版本切换按钮组 -->
                <div
                  class="version-nav"
                  v-if="message.next_branches?.count > 1"
                >
                  <span class="version-counter"
                    >{{ message.next_branches.current_branch_index + 1 }}/{{
                      message.next_branches.count
                    }}</span
                  >
                  <div class="version-buttons">
                    <el-button
                      type="text"
                      :disabled="
                        message.next_branches.current_branch_index === 0
                      "
                      @click="switchToAdjacentBranch(message, -1)"
                      title="查看上一个版本"
                      size="small"
                    >
                      <el-icon><ArrowLeft /></el-icon>
                    </el-button>
                    <el-button
                      type="text"
                      :disabled="
                        message.next_branches.current_branch_index ===
                        message.next_branches.count - 1
                      "
                      @click="switchToAdjacentBranch(message, 1)"
                      title="查看下一个版本"
                      size="small"
                    >
                      <el-icon><ArrowRight /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
              <div v-if="message.files?.length" class="message-files">
                <div
                  v-for="file in message.files"
                  :key="file.dify_file_id"
                  class="file-item"
                >
                  <span class="file-icon">{{ getFileIcon(file.type) }}</span>
                  <span class="file-name" @click="downloadFile(file)">{{
                    file.name
                  }}</span>
                </div>
              </div>
              <!-- 添加视频任务面板组件 -->

              <!-- ... 其他消息内容 ... -->
              <div
                v-if="session?.role_id === 3 && message.type === 'assistant'"
                class="video-tasks-section"
              >
                <VideoTaskPanel
                  :role-id="session.role_id"
                  :tasks="message.videoTasks || []"
                  :message-id="message.message_id"
                  :message-content="message.content"
                  :inferring="message.inferring"
                  @update:tasks="updateMessageTasks(message.message_id, $event)"
                />
              </div>
              <div
                v-if="session?.role_id === 28 && message.type === 'assistant'"
                class="mj-tasks-section"
              >
                <MJTaskPanel
                  :role-id="session.role_id"
                  :tasks="message.mjTasks || []"
                  :message-id="message.message_id"
                  :message-content="message.content"
                  :inferring="message.inferring"
                  @update:tasks="updateMessageTasks(message.message_id, $event)"
                />
              </div>
            </div>
          </div>
          <!-- 添加 HTML 预览组件 -->
          <HtmlPreview
            v-if="
              messages.length > 1 &&
              (session?.role_id === 32 || session?.role_id === 34 || session?.role_id === 39)
            "
            :session-id="session?.id"
            :html="
              messageHtmlMap[session?.id] || {
                html_code: '',
                status: '',
                id: 0,
                type: 'session',
                session_id: session?.id,
                message_id: 0,
                prompt: '',
              }
            "
            :messages="messages.filter((msg) => msg.type === 'assistant')"
            :model="selectedModel"
            :inferring="messages[messages.length - 1].inferring"
            @update:html="
              (html) => {
                messageHtmlMap[session?.id] = html;
              }
            "
          />
        </template>
        <el-empty v-else description="暂无消息记录" />
      </template>
    </div>

    <ChatInputArea
      v-model:messageInput="messageInput"
      v-model:uploadedFiles="uploadedFiles"
      :sending="sending"
      :editing-message-id="editingMessageId"
      :role-id="session?.role_id"
      :active-branch-id="activeBranchId"
      :base-url="config.baseURL"
      :auth-token="getToken()"
      :selectedModel="selectedModel"
      @send="handleSend"
      @cancel-editing="cancelEditing"
      @update:selectedModel="(val) => (selectedModel = val)"
    />

    <ChatDialog
      v-if="isDialogOpen"
      :session="session"
      :session-id="sessionId"
      :role="props.role"
      @close="handleCloseDialog"
      @session-created="handleSessionCreated"
      @session-error="handleSessionError"
      @branch-created="handleBranchCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, computed, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getSessionMessages, sendMessage, switchBranch } from "@/api/chat";
import type { Session, Message } from "@/types/chat";
import { ElMessage } from "element-plus";
import dayjs from "dayjs";
import { marked } from "marked";
import "highlight.js/styles/github.css";
//
import { ArrowLeft, ArrowRight, Document, Edit } from "@element-plus/icons-vue"; // 导入箭头图标
import { copyTextToClipboard } from "@/utils/clipboard";
import VideoTaskPanel from "@/components/workspace/VideoTaskPanel.vue";
import { getMessageVideoTasks } from "@/api/video";
import config from "@/config";
import ChatInputArea from "@/components/workspace/ChatInputArea.vue";
import { getToken } from "@/utils/auth";
import { fa } from "element-plus/es/locales.mjs";
import { showErrorMessage, showSuccessMessage } from "../../utils/message";
import { getMessageMJTasks } from "@/api/mj";
import HtmlPreview from "@/components/workspace/HtmlPreview.vue";
import { getMessageHtmlApi } from "@/api/html";

const props = defineProps<{
  session?: Session;
  role?: {
    id: string;
    title: string;
    icon?: string;
  };
}>();
const isDialogOpen = ref(false);
const route = useRoute();
const router = useRouter();
const sessionId = ref(route.params.sessionId as string);
const session = ref<Session | null>(props.session || null);
const messages = ref<Message[]>([]);
const loading = ref(false);
const loadingMore = ref(false);
const page = ref(1);
const size = ref(1000);
const hasMore = ref(false);
const messagesRef = ref<HTMLElement>();
const userAvatar = "https://example.com/default-avatar.png"; // TODO: 替换为实际的用户头像
const activeBranchId = ref<number>(0); // 当前活跃分支ID

// 调试输出 session 对象
console.log("Session object:", session.value);

// 在组件初始化时输出角色对象
console.log("Role object:", props.role);

// 如果路由参数中有开场白，则添加为第一条消息
if (route.params.openingStatement) {
  messages.value.push({
    id: `assistant_opening_${Date.now()}`,
    content: route.params.openingStatement as string,
    type: "assistant",
    timestamp: Date.now() / 1000,
  });
}

const messageInput = ref("");
const sending = ref(false);

// 在 data 部分添加编辑状态相关变量
const editingMessageId = ref<string | null>(null); // 当前正在编辑的消息ID
const originalMessageContent = ref(""); // 保存原始消息内容，用于取消编辑时恢复
const editingSourceMessage = ref<Message | null>(null); // 保存被编辑的消息对象

const emit = defineEmits([
  "update:session",
  "session-updated",
  "branch-created",
]);

// 获取备用图标
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
    if (title.includes(key)) {
      return emoji;
    }
  }
  return title.charAt(0);
};

// 添加获取视频任务的方法
const fetchVideoTasks = async (messageIds: string[]) => {
  try {
    const response = await getMessageVideoTasks(messageIds.join(","));
    if (response.data) {
      // 遍历消息列表，将视频任务信息添加到对应的消息中
      messages.value = messages.value.map((message) => {
        if (message.type === "assistant" && response.data[message.id]) {
          const videoTasks = response.data[message.id];
          return {
            ...message,
            videoTasks,
          };
        }
        return message;
      });
    }
  } catch (error) {
    console.error("获取视频任务失败:", error);
    ElMessage.error("获取视频任务信息失败");
  }
};

// 添加获取 MJ 任务的方法
const fetchMJTasks = async (messageIds: string[]) => {
  try {
    const response = await getMessageMJTasks(messageIds.join(","));
    if (response.data) {
      // 遍历消息列表，将 MJ 任务信息添加到对应的消息中
      messages.value = messages.value.map((message) => {
        if (message.type === "assistant" && response.data[message.id]) {
          const mjTasks = response.data[message.id];
          return {
            ...message,
            mjTasks,
          };
        }
        return message;
      });
    }
  } catch (error) {
    console.error("获取 MJ 任务失败:", error);
    ElMessage.error("获取 MJ 任务信息失败");
  }
};

// 加载会话消息
const loadMessages = async (isLoadMore = false) => {
  if (!sessionId.value) return;

  try {
    if (isLoadMore) {
      loadingMore.value = true;
    } else {
      loading.value = true;
    }

    const response = await getSessionMessages(sessionId.value, {
      page: page.value,
      size: size.value,
      include_context: 1,
    });

    if (response?.data) {
      const newMessages = response.data.messages || [];

      // 更新消息列表
      if (isLoadMore) {
        messages.value = [...newMessages, ...messages.value];
      } else {
        messages.value = newMessages;
      }

      // 获取消息相关的任务
      const assistantMessageIds = newMessages
        .filter((msg) => msg.type === "assistant")
        .map((msg) => msg.id);

      if (assistantMessageIds.length > 0) {
        // 如果是视频助手角色，获取视频任务
        if (session.value?.role_id === 3) {
          await fetchVideoTasks(assistantMessageIds);
        }
        // 如果是创意总监角色，获取 MJ 任务
        if (session.value?.role_id === 28) {
          await fetchMJTasks(assistantMessageIds);
        }
        // 如果是全能创意助手/小红书策略专家角色,获取 HTML 任务
        if (session.value?.role_id === 27 || session.value?.role_id === 25) {
          await initMessageHtml(assistantMessageIds, 0);
        }
        //用户调研洞察策略专家角色，获取 HTML 任务
        if (session.value?.role_id === 32 || session.value?.role_id === 34 || session.value?.role_id === 39) {
          await initMessageHtml([], session.value?.id);
        }
      }

      // 更新会话信息
      if (response.data.session) {
        session.value = response.data.session;
      }
      await nextTick();
      scrollToBottom();
    }
  } catch (error) {
    console.error("获取消息历史失败:", error);
    ElMessage.error("获取消息历史失败");
  } finally {
    if (isLoadMore) {
      loadingMore.value = false;
    } else {
      loading.value = false;
    }
  }
};

// 加载更多消息（加载较早的消息）
const loadMore = async () => {
  if (page.value > 1) {
    page.value--;
    await loadMessages(true);
  }
};

// 格式化时间
const formatTime = (timestamp: number) => {
  // 如果时间戳是秒级的，转换为毫秒级
  const milliseconds = timestamp * 1000;
  return dayjs(milliseconds).format("YYYY-MM-DD HH:mm:ss");
};

// 添加对 props.session 的监听
watch(
  () => props.session,
  (newSession, oldSession) => {
    if (!newSession || newSession === oldSession) return;

    console.log("props.session 变化:", newSession);
    session.value = newSession;

    if (newSession.active_branch_id !== undefined) {
      activeBranchId.value = newSession.active_branch_id;
    }
  }
);

// 将fetchSessionDetail函数移到这里，在watch之前定义
// 获取会话详情
const fetchSessionDetail = async (forceRefresh = false) => {
  if (!sessionId.value) return;

  try {
    if (!loading.value) {
      loading.value = true;
    }

    // 添加随机参数确保绕过缓存
    const params = forceRefresh
      ? { cache_bust: Date.now() + Math.random() }
      : { timestamp: Date.now() };

    console.log(`获取会话详情 (sessionId=${sessionId.value})`, params);
    const response = await getSessionMessages(sessionId.value, {
      page: 1,
      size: 1,
      ...params,
    });

    if (response && response.data) {
      if (response.data.session) {
        console.log("成功获取会话详情:", response.data.session);
        // 重要：确保完全替换会话对象而不是修改属性
        session.value = JSON.parse(JSON.stringify(response.data.session));

        // 更新活跃分支ID
        if (session.value.active_branch_id !== undefined) {
          activeBranchId.value = session.value.active_branch_id;
          console.log(`更新活跃分支ID: ${activeBranchId.value}`);
        }
      } else {
        console.warn("API 返回数据中未包含会话详情");
      }
    }
  } catch (error) {
    console.error("获取会话详情异常:", error);
    ElMessage.error("获取会话信息失败，请稍后重试");
  } finally {
    // 确保loading状态正确更新
    if (!messages.value.length) {
      loading.value = false;
    }
  }
};

// 恢复 onMounted 钩子
onMounted(async () => {
  console.log("组件挂载 - 初始会话状态:", {
    sessionId: sessionId.value,
    hasSession: !!session.value,
  });

  // 统一使用 refreshSession 来处理初始化
  if (sessionId.value) {
    await refreshSession();
  }

  // 滚动到底部
  scrollToBottom();

  // 初始化文本框高度
  nextTick(() => {
    adjustTextareaHeight();
  });

  // 监听窗口大小变化，重新调整高度
  window.addEventListener("resize", adjustTextareaHeight);
});

// 增强路由参数监听，确保每次路由变化都强制刷新
watch(
  () => route.params.sessionId,
  async (newId, oldId) => {
    if (!newId || newId === oldId) return;

    sessionId.value = newId as string;
    console.log("路由变化触发刷新");
    session.value = null;
    await fetchSessionDetail();
    page.value = 1;
    messages.value = [];
    loadMessages();
  }
);

// 修改刷新函数，确保彻底刷新
const refreshSession = async () => {
  console.log("手动刷新会话");

  // 清除缓存的会话数据
  session.value = null;

  // 重新获取会话详情，使用随机参数确保绕过缓存
  await fetchSessionDetail(true);

  // 重新加载消息
  page.value = 1;
  messages.value = [];
  loadMessages();
};

// 检查是否可以发送消息
const canSendMessage = computed(() => {
  const hasMessage = messageInput.value.trim().length > 0;
  const hasFiles = uploadedFiles.value.length > 0;
  const allFilesProcessed = uploadedFiles.value.every(
    (file) => file.status === "completed" || file.status === "error"
  );
  return (hasMessage || hasFiles) && allFilesProcessed;
});

// 添加相同的推理状态逻辑和样式
const inferring = ref(false);
const uploadedFiles = ref<
  Array<{
    id: string;
    name: string;
    size: number;
    type: string;
    status: "uploading" | "parsing" | "completed" | "error";
    dify_file_id?: string;
    obs_preview_url?: string;
    url?: string;
    raw?: File;
  }>
>([]);
// 恢复完整的错误处理
const handleSend = async (eventPayload: {
  content: string;
  files: File[];
  isEdit: boolean;
  parentMessageId: string;
  model: "gpt" | "deepseek";
}) => {
  console.log("handleSend", eventPayload);
  if (!canSendMessage.value) return;

  // 如果是发送普通消息 (原有的发送消息逻辑)
  try {
    sending.value = true;
    const message = eventPayload.content || messageInput.value.trim();
    if (!message && !uploadedFiles.value.length) {
      ElMessage.warning("请输入消息内容或上传文件");
      return;
    }

    // 只获取上传成功的文件
    const successfulFiles = uploadedFiles.value.filter(
      (file) => file.status === "completed"
    );
    
    // 调试信息（生产环境可移除）
    if (process.env.NODE_ENV === 'development') {
      console.log("ChatDetail - 文件上传状态:");
      console.log("- 所有上传的文件:", uploadedFiles.value);
      console.log("- 成功上传的文件:", successfulFiles);
      console.log("- 文件ID列表:", successfulFiles.map(f => f.dify_file_id));
    }
    
    // 创建用户消息
    const userMessage = {
      id: `user_${Date.now()}`,
      content: message,
      type: "user" as const,
      timestamp: Date.now() / 1000,
      branch_id: activeBranchId.value, // 添加当前分支ID
      files: successfulFiles.map((file) => ({
        id: file.dify_file_id,
        name: file.name,
        type: file.type,
        size: file.size,
        dify_file_id: file.dify_file_id,
        obs_preview_url: file.obs_preview_url,
      })),
      model: eventPayload.model,
    };

    // 立即清空输入框和已上传文件
    messageInput.value = "";
    uploadedFiles.value = [];

    // 重置文本框高度
    resetTextareaHeight();

    // 添加用户消息到列表
    messages.value.push(userMessage);

    // 滚动到底部
    scrollToBottom();

    // 创建AI回复的临时消息
    const aiMessage = {
      id: `assistant_${Date.now()}`,
      content: "",
      inferring: true,
      type: "assistant" as const,
      timestamp: Date.now() / 1000,
      branch_id: activeBranchId.value, // 添加当前分支ID
    };
    messages.value.push(aiMessage);
    inferring.value = true;

    // 发送请求
    const requestParams = {
      session_id: sessionId.value,
      role_id: props.role?.id,
      content: userMessage.content,
      file_ids: successfulFiles.map((file) => file.dify_file_id),
      session_type: "continue",
      branch_id: activeBranchId.value,
      parent_message_id: eventPayload.parentMessageId,
      model: userMessage.model,
    };
    
    // 调试信息（生产环境可移除）
    if (process.env.NODE_ENV === 'development') {
      console.log("ChatDetail - 发送请求参数:", requestParams);
    }
    
    const response = await sendMessage(requestParams);

    if (!response.ok) {
      if (response.status === 401) {
        ElMessage.error("登录已过期，请重新登录");
        router.push("/login");
        return;
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    try {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let accumulatedContent = "";

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (!line.trim() || !line.startsWith("data: ")) continue;

            try {
              const event = JSON.parse(line.slice(5));

              switch (event.event) {
                case "session_created":
                  if (event.data?.id) {
                    sessionId.value = event.data.id;
                  }
                  break;

                case "message":
                  if (event.answer) {
                    accumulatedContent += event.answer;
                    const lastMessage =
                      messages.value[messages.value.length - 1];
                    if (lastMessage.type === "assistant") {
                      lastMessage.content = accumulatedContent;
                    }
                    await nextTick();
                    scrollToBottom();
                  }
                  break;
                case "workflow_started":
                  console.log("工作流开始:", event);
                  if (event.message_id) {
                    const userIdx = messages.value.findIndex(
                      (m) => m.id === userMessage.id
                    );
                    const aiIdx = messages.value.findIndex(
                      (m) => m.id === aiMessage.id
                    );

                    if (userIdx !== -1) {
                      messages.value[userIdx].id = `user_${event.message_id}`;
                      messages.value[userIdx].message_id = event.message_id;
                      console.log("保存用户消息ID:", event.message_id);
                    }
                    if (aiIdx !== -1) {
                      messages.value[
                        aiIdx
                      ].id = `assistant_${event.message_id}`;
                      messages.value[aiIdx].message_id = event.message_id;
                      // 设置消息状态为成功
                      console.log("保存AI消息ID:", event.message_id);
                    }
                  }
                  break;
                case "branch_created": // <-- Re-adding this case
                  if (event.data?.branch_id) {
                    console.log("分支已创建:", event.data);
                    // 通知父组件分支创建 (Emit re-added)
                    emit("branch-created", event.data);

                    // 调用 handleBranchCreated 处理后续逻辑, 传递源消息
                    handleBranchCreated(event.data, editingSourceMessage.value);
                  }
                  break;
                case "message_end":
                  if (event.message_id) {
                    // 更新消息ID
                    const userIdx = messages.value.findIndex(
                      (m) => m.id === userMessage.id
                    );
                    const aiIdx = messages.value.findIndex(
                      (m) => m.id === aiMessage.id
                    );

                    if (userIdx !== -1) {
                      messages.value[userIdx].id = `user_${event.message_id}`;
                      messages.value[userIdx].message_id = event.message_id;
                    }
                    if (aiIdx !== -1) {
                      messages.value[
                        aiIdx
                      ].id = `assistant_${event.message_id}`;
                      messages.value[aiIdx].message_id = event.message_id;
                      messages.value[aiIdx].inferring = false;
                      // 设置消息状态为成功
                      messages.value[aiIdx].api_status = "success";
                    }
                  }
                  break;
                case "error":
                  // 处理错误事件
                  console.error("AI 响应错误:", event.message);

                  // 找到最后一条AI消息
                  const lastAiMessage =
                    messages.value[messages.value.length - 1];
                  if (lastAiMessage && lastAiMessage.type === "assistant") {
                    // 将"正在推理中"改为错误状态
                    lastAiMessage.inferring = false;
                    lastAiMessage.api_status = "error";

                    // 存储更友好的错误消息
                    if (event.message && event.message.includes("busy")) {
                      lastAiMessage.errorMessage = "当前系统繁忙，请稍后再试";
                    } else if (
                      event.message &&
                      event.message.includes("timeout")
                    ) {
                      lastAiMessage.errorMessage = "响应超时，请尝试重新发送";
                    } else if (!lastAiMessage.content) {
                      lastAiMessage.errorMessage =
                        "无法生成回复，请尝试修改提问内容";
                    }
                  }

                  // 显示错误提示
                  ElMessage.error(event.message || "生成回复失败，请稍后再试");
                  break;
              }
            } catch (e) {
              console.warn("解析消息失败:", e);
            }
          }
        }
      } finally {
        reader.releaseLock();
        inferring.value = false;
      }
    } catch (error) {
      console.error("处理响应流失败:", error);
      ElMessage.error("处理响应失败，请重试");

      // 确保在错误情况下也重置状态
      inferring.value = false;

      // 更新最后一条AI消息的状态
      const lastMessage = messages.value[messages.value.length - 1];
      if (lastMessage && lastMessage.type === "assistant") {
        lastMessage.inferring = false;
        lastMessage.api_status = "error";
        lastMessage.errorMessage = "网络异常，请检查连接后重试";
        if (!lastMessage.content) {
          lastMessage.content = "";
        }
      }
    }
  } catch (error) {
    console.error("发送消息失败:", error);
    ElMessage.error("发送消息失败");

    // 如果AI消息已经添加但出错，移除它
    if (messages.value[messages.value.length - 1]?.type === "assistant") {
      messages.value.pop();
    }
  } finally {
    sending.value = false;
    inferring.value = false;
    // 添加刷新逻辑，确保界面与后端数据一致
    // if (editingMessageId.value) {
    //   setTimeout(() => {
    //     // 刷新消息列表
    //     refreshMessages();
    //   }, 1000);
    // }
  }

  // 重置文本框高度
  resetTextareaHeight();
};

// 刷新消息
const refreshMessages = async () => {
  messages.value = [];
  page.value = 1;
  await loadMessages();

  // 刷新完成后，更新UI显示
  console.log(`当前活跃分支ID: ${activeBranchId.value}`);
};

// 获取文件图标
const getFileIcon = (type: any) => {
  const iconMap = {
    // 文档类型
    txt: "📄",
    md: "📝",
    markdown: "📝",
    pdf: "📑",
    html: "🌐",
    xlsx: "📊",
    xls: "📊",
    docx: "📃",
    doc: "📃",
    csv: "📋",
    eml: "📧",
    msg: "📧",
    pptx: "📽️",
    ppt: "📽️",
    xml: "📋",
    epub: "📚",

    // 图片类型
    jpg: "🖼️",
    jpeg: "🖼️",
    png: "🖼️",
    gif: "🖼️",
    webp: "🖼️",
    svg: "🖼️",

    // 默认
    default: "📎",
  };

  return iconMap[type] || iconMap["default"];
};

// 下载文件
const downloadFile = async (file) => {
  try {
    if (!file.obs_preview_url) {
      throw new Error("文件链接不存在");
    }

    const response = await fetch(file.obs_preview_url);
    if (!response.ok) {
      throw new Error("下载失败");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = file.name;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    ElMessage.success("下载成功");
  } catch (error) {
    console.error("下载文件失败:", error);
    ElMessage.error("下载文件失败");
  }
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    const messagesContainer = messagesRef.value;
    if (!messagesContainer) return;

    // 等待一小段时间确保 DOM 更新完成
    setTimeout(() => {
      // 检查是否有图片正在加载
      const images = messagesContainer.querySelectorAll("img");
      let loadingImages = 0;

      images.forEach((img) => {
        if (!img.complete) {
          loadingImages++;
          img.onload = () => {
            loadingImages--;
            if (loadingImages === 0) {
              // 所有图片加载完成后滚动
              messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
          };
        }
      });

      // 如果没有图片在加载，直接滚动
      if (loadingImages === 0) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }, 100);
  });
};

// 修改复制文本函数
const copyText = async (text) => {
  try {
    const success = await copyTextToClipboard(text);
    if (success) {
      showSuccessMessage("复制成功");
    } else {
      showErrorMessage("复制失败，请手动复制");
    }
  } catch (err) {
    console.error("复制失败:", err);
    showErrorMessage("复制失败，请手动复制");
  }
};

// Configure marked with highlight.js
marked.setOptions({
  renderer: new marked.Renderer(),
  breaks: true,
  gfm: true,
});

// Format message content
const formatMessageContent = (content: string) => {
  try {
    // Try to parse as JSON first
    const jsonData = JSON.parse(content);
    return `<pre class="json-content">${JSON.stringify(
      jsonData,
      null,
      2
    )}</pre>`;
  } catch {
    // If not JSON, treat as markdown
    return marked(content);
  }
};

// 监听消息列表变化，当有新消息时滚动到底部
watch(
  () => messages.value.length,
  () => {
    if (!loadingMore.value) {
      // 只在非加载更多时滚动到底部
      scrollToBottom();
    }
  }
);

// 添加文本框自适应相关变量
const textareaRef = ref<any>(null);
const textareaRows = ref(3); // 默认行数
const maxRows = 10; // 最大行数限制

// 调整文本框高度的函数
const adjustTextareaHeight = () => {
  const textarea = textareaRef.value?.$el.querySelector("textarea");
  if (!textarea) return;

  // 保存当前滚动位置
  const scrollTop = textarea.scrollTop;

  // 重置高度以获取正确的scrollHeight
  textarea.style.height = "auto";

  // 计算内容的行数
  const lineHeight = parseInt(getComputedStyle(textarea).lineHeight) || 24;
  const paddingTop = parseInt(getComputedStyle(textarea).paddingTop) || 12;
  const paddingBottom =
    parseInt(getComputedStyle(textarea).paddingBottom) || 12;

  // 计算基础高度（空文本框的高度）
  const baseHeight = 3 * lineHeight + paddingTop + paddingBottom;

  // 获取内容高度
  const contentHeight = textarea.scrollHeight;

  // 设置新高度 - 使用Math.max确保至少有基础高度
  const newHeight = Math.min(
    Math.max(baseHeight, contentHeight),
    maxRows * lineHeight + paddingTop + paddingBottom
  );

  // 应用新高度
  textarea.style.height = `${newHeight}px`;

  // 恢复滚动位置
  textarea.scrollTop = scrollTop;

  // 如果内容超过最大行数，启用滚动
  if (contentHeight > maxRows * lineHeight + paddingTop + paddingBottom) {
    textarea.style.overflowY = "auto";
  } else {
    textarea.style.overflowY = "hidden";
  }
};

// 重置文本框高度
const resetTextareaHeight = () => {
  const textarea = textareaRef.value?.$el.querySelector("textarea");
  if (textarea) {
    textarea.style.height = "auto";
    textareaRows.value = 3;
  }
};

// 监听输入消息变化
watch(messageInput, () => {
  nextTick(() => {
    adjustTextareaHeight();
  });
});

// 在组件卸载前移除事件监听
onUnmounted(() => {
  window.removeEventListener("resize", adjustTextareaHeight);
});

// 在 methods 部分添加编辑相关函数
const startEditing = (message: Message) => {
  if (sending.value) return;

  editingMessageId.value = message.message_id; // 保留message.id用于创建分支
  editingSourceMessage.value = message; // 保存源消息对象
  messageInput.value = message.content;
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.focus();
    }
  });

  // 显示提示
  ElMessage.info("您正在编辑历史消息");
};

const cancelEditing = () => {
  editingMessageId.value = null; // 清除编辑ID
  editingSourceMessage.value = null; // 清除源消息
  messageInput.value = "";
};

// 处理分支创建事件
const handleBranchCreated = (
  data: { branch_id: number },
  sourceMessage?: Message
) => {
  console.log("收到分支创建事件", data);

  if (data && data.branch_id) {
    // 更新活跃分支ID
    activeBranchId.value = data.branch_id;

    // 直接使用消息的next_branches属性刷新界面
    // 不需要调用loadBranchTree

    // 手动刷新消息列表
    loadBranchMessages(data.branch_id, sourceMessage, true);

    // 通知用户
    ElMessage.success("创建分支成功，已切换到新分支");
  }
};

// 修改版本切换函数，避免完全重载所有消息
async function switchToAdjacentBranch(message: Message, delta: number) {
  console.log("切换到相邻版本", message, delta);
  try {
    if (!message?.next_branches?.branches?.length) {
      console.error("无可切换的版本或版本数据结构错误");
      return;
    }

    const branches = message.next_branches.branches;
    const currentIndex = message.next_branches.current_branch_index;
    const targetIndex = currentIndex + delta;
    message.next_branches.current_branch_index = targetIndex;

    // 索引范围检查
    if (targetIndex < 0 || targetIndex >= branches.length) {
      console.error("目标版本索引超出范围:", targetIndex);
      return;
    }

    const targetBranchId = branches[targetIndex].branch_id;
    console.log(
      `切换版本: 当前索引=${currentIndex}, 步长=${delta}, 目标索引=${targetIndex}, 目标版本ID=${targetBranchId}`
    );

    // 显示切换加载状态
    loading.value = true;

    try {
      // 调用分支切换API
      console.log(
        "执行分支切换 API 调用 - 会话ID:",
        sessionId.value,
        "目标分支ID:",
        targetBranchId
      );
      const response = await switchBranch(sessionId.value, targetBranchId);
      console.log("分支切换API响应:", response);

      if (response && response.success) {
        // 更新激活的分支ID
        activeBranchId.value = targetBranchId;
        console.log("已更新激活的分支ID:", activeBranchId.value);

        // 切换分支时调用加载函数，加载包含上下文的消息
        await loadBranchMessages(targetBranchId, message);
        console.log(
          "包含上下文的分支消息已加载，当前消息数:",
          messages.value.length
        );

        ElMessage.success("切换版本成功");
      } else {
        ElMessage.error("切换版本失败: " + (response?.message || "未知错误"));
      }
    } finally {
      loading.value = false;
    }
  } catch (error) {
    console.error("版本切换处理失败", error);
    ElMessage.error("版本切换失败，请重试");
    loading.value = false;
  }
}

// 加载特定分支的消息，包含上下文
const loadBranchMessages = async (
  branchId: number,
  sourceMessage?: Message,
  isEditedMessage: boolean = false
) => {
  if (!sessionId.value) return;

  try {
    loading.value = true;
    console.log(
      `开始加载分支消息 - 分支ID: ${branchId}, 消息ID: ${sourceMessage?.id}`
    );

    const targetMessageId =
      sourceMessage?.next_branches?.branches[
        sourceMessage?.next_branches.current_branch_index
      ]?.id;
    // 获取新分支的消息
    const response = await getSessionMessages(sessionId.value, {
      page: 1,
      size: 100,
      branch_id: branchId,
      include_context: 0,
      message_id: targetMessageId, // 添加message_id参数
    });

    if (response.data) {
      const newMessages = response.data.messages;
      // 对 newMessages 做个排序。按id 从小到大排序
      newMessages.sort((a, b) => a.id - b.id);
      console.log(`获取到${newMessages.length}条新消息`);

      if (sourceMessage && newMessages.length > 0) {
        // 将源消息的分支信息复制到新消息列表的第一条消息
        if (sourceMessage.next_branches) {
          newMessages[0].next_branches = JSON.parse(
            JSON.stringify(sourceMessage.next_branches)
          );
          if (isEditedMessage) {
            // 新返回的第一条消息 加到分支里
            const newBranch = {
              id: newMessages[0].message_id,
              title: newMessages[0].content,
              branch_id: newMessages[0].branch_id,
            };
            newMessages[0].next_branches.branches.push(newBranch);
            newMessages[0].next_branches.count =
              newMessages[0].next_branches.branches.length;
            newMessages[0].next_branches.current_branch_index =
              newMessages[0].next_branches.branches.length - 1;
          }
        }

        // 在现有消息列表中找到源消息的位置
        const sourceIndex = messages.value.findIndex(
          (m) => m.id === sourceMessage.id
        );
        if (sourceIndex !== -1) {
          console.log("找到源消息位置", sourceIndex);
          // 删除源消息及之后的所有消息
          messages.value.splice(sourceIndex);
          // 添加新的消息列表
          messages.value.push(...newMessages);
          // 对 messages.value 做个排序。按id 从小到大排序
          messages.value.sort((a, b) => a.id - b.id);
        }
      } else {
        messages.value = newMessages;
      }
      // 更新活跃分支ID
      if (response.data.active_branch_id !== undefined) {
        activeBranchId.value = response.data.active_branch_id;
      } else {
        activeBranchId.value = branchId;
      }

      // 更新会话信息
      if (response.data.session) {
        session.value = response.data.session;
      }
    }
  } catch (error) {
    console.error("加载分支消息失败:", error);
  } finally {
    loading.value = false;
  }
};

// 切换路由时更新会话ID并刷新
watch(
  () => route.params.sessionId,
  (newSessionId) => {
    if (newSessionId && newSessionId !== sessionId.value) {
      sessionId.value = newSessionId as string;
      refreshSession();
    }
  }
);

// 更新props传入的session
watch(
  () => props.session,
  (newSession) => {
    if (newSession) {
      session.value = newSession;

      // 初始化活跃分支ID
      if (newSession.active_branch_id !== undefined) {
        activeBranchId.value = newSession.active_branch_id;
        console.log("通过props初始化activeBranchId:", activeBranchId.value);
      }
    }
  }
);

// 组件卸载时清理轮询
onUnmounted(() => {
  // 清除所有可能存在的轮询定时器
  const intervals = window.setInterval(() => {}, 0);
  for (let i = 0; i < intervals; i++) {
    window.clearInterval(i);
  }
});

// 更新消息的视频任务
const updateMessageTasks = (messageId: string, newTasks: any[]) => {
  messages.value = messages.value.map((msg) => {
    if (msg.message_id === messageId) {
      // 根据session角色判断是视频任务还是MJ任务
      if (session.value?.role_id === 3) {
        // 视频任务
        return {
          ...msg,
          videoTasks: newTasks,
        };
      } else if (session.value?.role_id === 28) {
        // MJ图片任务
        return {
          ...msg,
          mjTasks: newTasks,
        };
      }
      // 默认处理为视频任务
      return {
        ...msg,
        videoTasks: newTasks,
      };
    }
    return msg;
  });
};

// 在 methods 部分添加 openEQMJ 方法
function openEQMJ() {
  window.open(config.EQMJ_HOME, "_blank");
}

// 在 script setup 部分添加
const messageHtmlMap = ref<Record<string, any>>({});

// 初始化消息 HTML 内容
const initMessageHtml = async (messageIds: string[], sessionId: number) => {
  try {
    const response = await getMessageHtmlApi(messageIds, sessionId);
    if (response.success) {
      messageHtmlMap.value = response.data;
    }
  } catch (error) {
    console.error("Init message HTML error:", error);
  }
};

const selectedModel = ref<"gpt" | "deepseek">("gpt");
</script>

<style scoped>
.chat-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f7f8fa; /* 更好的背景色 */
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 10;
}

.role-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.role-info :deep(.el-avatar) {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-wrapper h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
  background: #f7f8fa; /* 确保消息区域背景一致 */
  /* 添加自定义滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
}

/* 自定义滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.3);
}

.message-item {
  display: flex;
  gap: 16px;
  margin-bottom: 24px; /* 增加消息间距 */
  opacity: 0;
  animation: fadeIn 0.3s ease forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-header {
  display: flex;
  flex-direction: column; /* 垂直排列头像和信息 */
  align-items: center;
  gap: 8px;
  min-width: 60px; /* 确保头像区域有足够宽度 */
}

.user .message-header {
  align-items: flex-end; /* 用户消息右对齐 */
}

.assistant .message-header {
  align-items: flex-start; /* 助手消息左对齐 */
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
  flex-shrink: 0; /* 防止头像被压缩 */
  position: relative; /* 为图片错误处理添加相对定位 */
  overflow: hidden; /* 隐藏无法加载的图片 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* 添加头像阴影 */
}

.user-avatar {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.assistant-avatar {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.avatar img {
  width: 100%;
  height: 100%;
  border-radius: 12px;
  object-fit: cover;
}

.message-info {
  text-align: center; /* 信息居中对齐 */
  min-height: 32px; /* 确保信息区域有足够高度 */
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.message-sender {
  font-size: 12px; /* 减小字体 */
  font-weight: 500;
  color: #6b7280; /* 调整颜色 */
  margin-bottom: 2px;
  white-space: nowrap; /* 防止换行 */
}

.message-time {
  font-size: 11px; /* 减小字体 */
  color: #9ca3af;
  white-space: nowrap; /* 防止换行 */
}

.message-content-wrapper {
  max-width: 70%; /* 调整最大宽度 */
  min-width: 200px; /* 调整最小宽度 */
  display: flex; /* 使用 flex 布局 */
  flex-direction: column; /* 垂直排列内容和操作 */
}

.message-content {
  padding: 16px 20px; /* 增加内边距 */
  border-radius: 18px; /* 增加圆角 */
  font-size: 15px;
  line-height: 1.6; /* 调整行高 */
  position: relative;
  transition: all 0.2s ease;
  word-wrap: break-word; /* 允许长单词换行 */
  overflow-wrap: break-word; /* 确保兼容性 */
  white-space: pre-wrap; /* 保留换行符和空格 */
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08); /* 增强阴影效果 */
}

.user .message-content {
  background: linear-gradient(135deg, #4f46e5, #6366f1); /* 渐变背景 */
  color: white;
  border-top-right-radius: 6px; /* 调整用户消息的右上角 */
}

.assistant .message-content {
  background: white;
  color: #1a1a1a;
  border-top-left-radius: 6px; /* 调整助手消息的左上角 */
  border: 1px solid #f0f0f0; /* 添加边框 */
}

.user .message-content :deep(pre) {
  background: rgba(255, 255, 255, 0.15); /* 用户消息中的代码块背景 */
}

.user .message-content :deep(code) {
  background-color: rgba(255, 255, 255, 0.2); /* 用户消息中的内联代码背景 */
}

.message-content :deep(pre) {
  background: rgba(0, 0, 0, 0.05); /* 调整代码块背景 */
  padding: 12px 16px; /* 调整代码块内边距 */
  border-radius: 8px;
  overflow-x: auto;
  margin: 10px 0; /* 调整代码块外边距 */
  font-size: 14px; /* 统一代码字体大小 */
}

.message-content :deep(code) {
  font-family: "Fira Code", Consolas, Monaco, "Andale Mono", "Ubuntu Mono",
    monospace; /* 使用更通用的等宽字体栈 */
  font-size: 0.9em; /* 相对父元素调整大小 */
  background-color: rgba(0, 0, 0, 0.04); /* 为内联代码添加背景 */
  padding: 2px 5px; /* 内联代码内边距 */
  border-radius: 4px; /* 内联代码圆角 */
}

.message-content :deep(ul),
.message-content :deep(ol) {
  padding-left: 24px; /* 调整列表缩进 */
  margin-top: 0.8em; /* 列表上方间距 */
  margin-bottom: 0.8em; /* 列表下方间距 */
}

.message-content :deep(li) {
  margin-bottom: 0.5em; /* 列表项之间的间距 */
  line-height: 1.7; /* 调整行高以提高可读性 */
}

.message-content :deep(ul li::marker) {
  color: #666; /* 无序列表标记颜色 */
  font-size: 0.9em; /* 可以微调标记大小 */
}

.message-content :deep(ol li::marker) {
  color: #666; /* 有序列表标记颜色 */
  font-weight: 500; /* 标记字重 */
  font-size: 0.9em;
}

.message-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-content :deep(th),
.message-content :deep(td) {
  border: 1px solid #dfe2e5;
  padding: 8px 12px;
  text-align: left;
}

.message-content :deep(th) {
  background: #f6f8fa;
  font-weight: 600;
}

.message-content :deep(blockquote) {
  margin: 8px 0;
  padding: 0 16px;
  color: #6a737d;
  border-left: 4px solid #dfe2e5;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 0 4px 4px 0;
}

.message-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 8px 0;
}

.message-content :deep(*) {
  margin: 0 !important;
  padding: 0 !important;
}

.message-content :deep(h1),
.message-content :deep(h2),
.message-content :deep(h3),
.message-content :deep(h4),
.message-content :deep(h5),
.message-content :deep(h6) {
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1 !important;
  font-weight: 600;
}

.message-content :deep(p) {
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1.2 !important;
}

.message-actions {
  display: flex;
  gap: 6px; /* 调整按钮间距 */
  margin-top: 12px; /* 调整与内容的间距 */
  opacity: 1; /* 一直显示 */
  transition: opacity 0.2s ease;
  align-items: center;
  justify-content: flex-end; /* 按钮默认右对齐 */
}

.user .message-actions {
  justify-content: flex-start; /* 用户消息的操作按钮在左侧 */
}

.message-actions .el-button {
  padding: 6px 12px; /* 调整按钮内边距 */
  border-radius: 8px;
  font-size: 12px; /* 减小字体大小 */
  transition: all 0.2s ease;
  color: #6b7280; /* 默认按钮颜色 */
  background-color: rgba(255, 255, 255, 0.9); /* 半透明背景 */
  border: 1px solid #e5e7eb; /* 添加边框 */
  backdrop-filter: blur(4px); /* 添加模糊效果 */
}

.message-actions .el-button:hover {
  background-color: #f9fafb; /* 悬停背景色 */
  color: #374151; /* 悬停文字颜色 */
  transform: translateY(-1px); /* 轻微上移效果 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* 悬停阴影 */
}

.message-actions .el-button .el-icon {
  font-size: 14px; /* 图标大小 */
  margin-right: 4px; /* 图标和文字间距 */
}

/* 添加推理状态样式 */
.inferring-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-style: italic;
  padding: 12px 16px;
  background: rgba(107, 114, 128, 0.1);
  border-radius: 8px;
  margin: 8px 0;
}

.inferring-indicator::before {
  content: "";
  width: 16px;
  height: 16px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #6b7280;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.empty-response {
  color: #9ca3af;
  font-style: italic;
  padding: 12px 16px;
  background: rgba(156, 163, 175, 0.1);
  border-radius: 8px;
  text-align: center;
}

.error-message {
  color: #ef4444;
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  padding: 16px 20px;
  border-radius: 12px;
  border: 1px solid #fecaca;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.1);
  font-weight: 500;
}

/* 加载更多按钮样式 */
.load-more {
  text-align: center;
  padding: 16px 0;
  margin-bottom: 16px;
}

.load-more .el-button {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e5e7eb;
  color: #6b7280;
  border-radius: 12px;
  padding: 10px 24px;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);
}

.load-more .el-button:hover {
  background: white;
  color: #4f46e5;
  border-color: #4f46e5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
}

/* 空状态样式 */
:deep(.el-empty) {
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  margin: 40px 20px;
  backdrop-filter: blur(4px);
}

:deep(.el-empty__description) {
  color: #9ca3af;
  font-size: 14px;
}

.video-tasks-section {
  margin-top: 16px;
  border-top: 1px solid #eee;
  padding-top: 16px;
}

.mj-tasks-section {
  margin-top: 16px;
  border-top: 1px solid #eee;
  padding-top: 16px;
}

.html-preview-section {
  padding-top: 16px;
}
</style>
