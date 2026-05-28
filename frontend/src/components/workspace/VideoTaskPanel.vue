<template>
  <div class="video-task-panel">
    <!-- 只在角色ID为3、没有任务、且消息不在推理中时显示生成按钮 -->
    <div
      v-if="
        props.roleId === 3 && (!tasks || tasks.length === 0) && !props.inferring
      "
      class="generate-tasks"
    >
      <el-button
        type="primary"
        :loading="isGenerating"
        @click="handleGenerateTasks"
      >
        生成分镜脚本
      </el-button>
    </div>

    <!-- 现有的任务卡片列表 -->
    <div v-else v-for="(task, index) in tasks" :key="task.id" class="task-card">
      <div class="task-header">
        <!-- 先显示镜头标题 -->
        <div v-if="task.script_data" class="shot-title">
          {{ index + 1 }}. {{ getShotTitle(task.script_data) }}
        </div>
        <!-- 再显示状态标签 -->
        <!-- <div :class="['status-badge', task.status.toLowerCase()]">
          {{ getTaskStatusText(task.status) }}
        </div> -->
      </div>

      <div class="task-content">
        <!-- 1. 等待编辑提示词状态 -->
        <div v-if="task.status === 'PENDING'" class="task-edit">
          <div class="prompt-preview">{{ task.prompt }}</div>
          <div class="task-buttons">
            <el-button type="primary" @click="handleEdit(task)">
              编辑提示词生成视频
            </el-button>
            <el-button type="success" @click="handleDirectGenerate(task)">
              直接生成视频
            </el-button>
          </div>
        </div>

        <!-- 2. 等待视频生成状态 -->
        <div
          v-else-if="task.status === 'PROCESSING' && !task.video_url"
          class="task-progress"
        >
          <div class="loading-circle">
            <div class="circle"></div>
            <span class="x">×</span>
          </div>
          <span class="progress-text">视频生成中...</span>
        </div>

        <!-- 3. 视频展示状态 -->
        <div v-else-if="task.video_url" class="video-container">
          <!-- 添加提示词显示 -->
          <div class="prompt-preview">{{ task.prompt }}</div>
          <video
            class="video-player"
            :src="task.video_url"
            controls
            preload="metadata"
          ></video>
          <div class="video-actions">
            <el-button type="primary" @click="downloadVideo(task)"
              >下载视频</el-button
            >
            <el-button @click="handleEdit(task)">重新生成</el-button>
          </div>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="task.status === 'FAILED'" class="task-error">
          <el-alert
            :title="task.error_message || '视频生成失败'"
            type="error"
            show-icon
          />
          <el-button class="mt-2" @click="handleEdit(task)">重试</el-button>
        </div>
      </div>
    </div>

    <!-- 编辑提示词对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑提示词"
      width="500px"
      :append-to-body="true"
      :modal="true"
      :close-on-click-modal="false"
      destroy-on-close
      class="edit-dialog"
    >
      <el-form :model="form" label-position="top">
        <el-form-item label="提示词">
          <el-input
            v-model="editingPrompt"
            type="textarea"
            :rows="4"
            placeholder="请输入视频生成提示词"
            resize="none"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleUpdateTask">
            开始生成
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import { ElMessage } from "element-plus";
import {
  updateVideoTask,
  getVideoTaskStatus,
  parseScriptToTasks,
} from "@/api/video";
import type { VideoTask, VideoTaskStatus } from "@/api/video";

const props = defineProps<{
  roleId: number;
  tasks: VideoTask[];
  messageId: string;
  messageContent: string;
  inferring: boolean; // 新增 inferring 属性
}>();

const emit = defineEmits(["update", "update:tasks"]);

const isGenerating = ref(false);

const handleGenerateTasks = async () => {
  if (!props.messageContent || !props.messageId) {
    ElMessage.error("消息内容或ID不存在");
    return;
  }

  isGenerating.value = true;
  try {
    const response = await parseScriptToTasks(
      props.messageContent,
      props.messageId
    );
    // 触发父组件更新任务列表
    emit("update:tasks", response.data.tasks);
    ElMessage.success("分镜脚本生成成功");
  } catch (error) {
    console.error("生成分镜脚本失败:", error);
    ElMessage.error("生成分镜脚本失败");
  } finally {
    isGenerating.value = false;
  }
};

// 状态变量
const dialogVisible = ref(false);
const editingPrompt = ref("");
const currentTask = ref<VideoTask | null>(null);
const saving = ref(false);
let pollInterval: number | null = null;

// 表单数据
const form = ref({
  prompt: "",
});

// 监听 editingPrompt 变化同步到表单
watch(editingPrompt, (newVal) => {
  form.value.prompt = newVal;
});

// 更新本地任务状态
const updateLocalTaskStatus = (
  taskId: number,
  status: VideoTaskStatus,
  videoUrl?: string,
  newPrompt?: string
) => {
  const taskIndex = props.tasks.findIndex((t) => t.id === taskId);
  if (taskIndex !== -1) {
    const updatedTask = {
      ...props.tasks[taskIndex],
      status,
      video_url: videoUrl || undefined,
      prompt:
        newPrompt !== undefined ? newPrompt : props.tasks[taskIndex].prompt,
    };
    props.tasks.splice(taskIndex, 1, updatedTask);
  }
};

// 轮询单个任务状态
const pollSingleTaskStatus = async (taskId: number) => {
  try {
    const response = await getVideoTaskStatus(taskId.toString());

    // 检查后端返回的状态
    if (!response.success) {
      console.error(`获取任务 ${taskId} 状态失败:`, response.message);
      return false; // 继续轮询
    }

    const taskData = response.data;
    const status = taskData.status;

    // 更新本地任务状态
    updateLocalTaskStatus(
      taskId,
      status as VideoTaskStatus,
      taskData.video_url
    );

    // 只有在明确完成或失败时才停止轮询
    return ["SUCCEEDED", "FAILED"].includes(status);
  } catch (error) {
    console.error(`轮询任务 ${taskId} 状态失败:`, error);
    return false; // 发生错误时继续轮询
  }
};

// 开始轮询
const startPolling = () => {
  if (pollInterval) return;

  pollInterval = setInterval(async () => {
    const processingTasks = props.tasks.filter(
      (task) => task.status === "PROCESSING"
    );

    if (processingTasks.length === 0) {
      stopPolling();
      return;
    }

    // 并行轮询所有处理中的任务
    const pollResults = await Promise.all(
      processingTasks.map((task) => pollSingleTaskStatus(task.id))
    );

    // 只有当所有任务都明确完成或失败时才停止轮询
    if (
      pollResults.length > 0 &&
      pollResults.every((result) => result === true)
    ) {
      stopPolling();
    }
  }, 5000); // 每5秒轮询一次
};

// 停止轮询
const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
};

// 生命周期钩子
onMounted(() => {
  // 检查是否有正在处理中的任务，如果有则开始轮询
  const hasProcessingTasks = props.tasks.some(
    (task) => task.status === "PROCESSING"
  );
  if (hasProcessingTasks) {
    startPolling();
  }
});

onUnmounted(() => {
  stopPolling();
});

// 编辑相关方法
const handleEdit = (task: VideoTask) => {
  console.log("handleEdit", task);
  currentTask.value = task;
  editingPrompt.value = task.prompt || "";
  dialogVisible.value = true;
};

/**
 * 直接生成视频（不编辑提示词）
 * @param task 视频任务对象
 */
const handleDirectGenerate = async (task: VideoTask) => {
  if (!task.prompt?.trim()) {
    ElMessage.warning("提示词不能为空");
    return;
  }

  try {
    // 直接使用当前提示词更新任务
    await updateVideoTask(task.id, task.prompt.trim());
    ElMessage.success("视频生成任务已开始");

    // 更新本地任务状态为处理中
    updateLocalTaskStatus(
      task.id,
      "PROCESSING" as VideoTaskStatus,
      undefined,
      task.prompt.trim()
    );

    // 开始轮询
    startPolling();
  } catch (error: any) {
    console.error("直接生成视频失败:", error);
    ElMessage.error(error.response?.data?.message || "视频生成失败");
  }
};

const handleCancel = () => {
  dialogVisible.value = false;
  editingPrompt.value = "";
  currentTask.value = null;
  saving.value = false;
};

const handleUpdateTask = async () => {
  if (!editingPrompt.value.trim()) {
    ElMessage.warning("提示词不能为空");
    return;
  }

  if (!currentTask.value) {
    ElMessage.error("当前任务不存在");
    return;
  }

  try {
    saving.value = true;
    await updateVideoTask(currentTask.value.id, editingPrompt.value.trim());
    ElMessage.success("新视频生成任务已创建");

    // 更新本地任务状态为处理中，同时更新提示词
    updateLocalTaskStatus(
      currentTask.value.id,
      "PROCESSING" as VideoTaskStatus,
      undefined,
      editingPrompt.value.trim()
    );

    // 关闭对话框
    dialogVisible.value = false;

    // 开始轮询
    startPolling();
  } catch (error: any) {
    console.error("更新视频任务失败:", error);
    ElMessage.error(error.response?.data?.message || "更新视频任务失败");
  } finally {
    saving.value = false;
  }
};

// 获取任务状态文本
const getTaskStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    PENDING: "等待中",
    QUEUED: "排队中",
    PROCESSING: "生成中",
    SUCCEEDED: "已完成",
    FAILED: "失败",
  };
  return statusMap[status] || status;
};

// 下载视频
const downloadVideo = async (task: VideoTask) => {
  if (!task.video_url) {
    ElMessage.warning("视频链接不存在");
    return;
  }

  try {
    const response = await fetch(task.video_url);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `video_${task.id}.mp4`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (error) {
    console.error("下载视频失败:", error);
    ElMessage.error("下载视频失败");
  }
};

// 添加获取镜头标题的方法
const getShotTitle = (scriptData: string) => {
  try {
    const data = JSON.parse(scriptData);
    if (data.part && data.type) {
      return `${data.part} - ${data.type}`;
    }
    return data.part || data.type || "";
  } catch (e) {
    return "";
  }
};
</script>

<style scoped>
.generate-tasks {
  display: flex;
  justify-content: center;
  padding: 20px;
}

/* 添加对话框相关样式 */
:deep(.edit-dialog) {
  .el-dialog {
    border-radius: 8px;
    overflow: hidden;
  }

  .el-dialog__header {
    margin: 0;
    padding: 20px;
    border-bottom: 1px solid #dcdfe6;
  }

  .el-dialog__body {
    padding: 20px;
  }

  .el-dialog__footer {
    padding: 20px;
    border-top: 1px solid #dcdfe6;
  }
}

.dialog-content {
  padding: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 确保对话框在最顶层显示 */
:deep(.el-dialog__wrapper) {
  z-index: 2000;
}

:deep(.v-modal) {
  z-index: 1999;
}

/* 其他现有的样式保持不变 */
.video-task-panel {
  display: grid;
  gap: 20px;
  padding: 16px;
}

.task-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #edf2f7;
}

.video-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 12px;
  margin-bottom: 12px;
}

.task-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.shot-title {
  font-size: 14px;
  color: #606266;
  margin-right: 12px; /* 改为右边距 */
  flex: 1;
  text-align: left; /* 改为左对齐 */
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
}

.status-badge.succeeded {
  background: #c6f6d5;
  color: #2f855a;
}

.status-badge.failed {
  background: #fed7d7;
  color: #c53030;
}

.status-badge.processing {
  background: #bee3f8;
  color: #2b6cb0;
  animation: pulse 2s infinite;
}

.status-badge.pending,
.status-badge.queued {
  background: #edf2f7;
  color: #4a5568;
}

.task-content {
  padding: 20px;
}

.task-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 12px;
}

.task-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
}

.loading-circle {
  position: relative;
  width: 60px;
  height: 60px;
}

.circle {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top-color: #ff4d4f;
  border-right-color: #ff4d4f;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.x {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #666;
  font-size: 16px;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.progress-text {
  color: #666;
  font-size: 14px;
}

.video-container {
  border-radius: 8px;
  overflow: hidden;
}

.video-container .video-player {
  background: #000;
  width: 100%;
  display: block;
  aspect-ratio: 16/9;
}

.prompt-preview {
  background: #f9f9f9;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
  color: #333;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.mb-3 {
  margin-bottom: 12px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fff5f5;
  border-radius: 8px;
  color: #c53030;
  font-size: 14px;
}

.task-actions {
  padding: 16px 20px;
  border-top: 1px solid #edf2f7;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  background: #f8fafc;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
  100% {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .video-task-panel {
    padding: 12px;
    gap: 16px;
  }

  .task-actions {
    flex-direction: column;
  }

  .task-actions .el-button {
    width: 100%;
  }

  .task-buttons {
    flex-direction: column;
    gap: 8px;
  }

  .task-buttons .el-button {
    width: 100%;
  }
}
</style>
