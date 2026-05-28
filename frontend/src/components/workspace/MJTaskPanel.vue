<template>
  <div class="mj-task-panel">
    <!-- 只在没有任务且不在推理状态时显示生成图片按钮 -->
    <div v-if="!tasks.length && !inferring" class="no-tasks">
      <el-button
        type="primary"
        :loading="isGenerating"
        @click="handleGenerateImage"
      >
        {{ isGenerating ? "图片任务生成中..." : "生成图片" }}
      </el-button>
    </div>
    <!-- 增加推理中的提示 -->
    <div v-else-if="!tasks.length && inferring" class="inferring-message">
      <el-icon><Loading /></el-icon>
      <span>AI 正在思考中，等待回复完成后可生成图片...</span>
    </div>
    <div v-else class="tasks-container">
      <div v-for="task in tasks" :key="task.id" class="task-item">
        <!-- 任务状态和进度 -->
        <div class="task-header">
          <div class="task-status" :class="task.status.toLowerCase()">
            {{ getStatusText(task.status) }}
            <template
              v-if="
                task.status === 'WAITING' || task.status === 'IN_PROCESSING'
              "
            >
              <div class="loading-spinner">
                <div class="spinner"></div>
              </div>
            </template>
          </div>
          <div class="task-actions" v-if="task.status === 'WAITING'">
            <el-button type="text" size="small" @click="handleCancel(task)">
              取消
            </el-button>
          </div>
        </div>

        <!-- 提示词 -->
        <div class="task-prompt">
          {{ task.prompt }}
        </div>

        <!-- 图片展示区域 -->
        <div v-if="task.oss_image_url" class="task-image">
          <viewer :images="singleImage(task.oss_image_url)">
            <img
              :src="task.oss_image_url"
              style="
                width: 100%;
                max-height: 300px;
                border-radius: 4px;
                cursor: pointer;
                object-fit: contain;
                background: #f5f7fa;
                display: block;
              "
              :alt="task.prompt"
            />
          </viewer>
        </div>

        <!-- 操作按钮 -->
        <div
          v-if="task.status === 'SUCCESS' && task.actions_json?.length"
          class="task-operations"
        >
          <div class="operation-title">可用操作</div>

          <!-- 按钮分组显示 -->
          <div class="action-groups">
            <!-- 放大按钮组 -->
            <div
              v-if="getActionsByType(task.actions_json, 'zoom').length"
              class="action-group zoom-group"
            >
              <div class="group-buttons">
                <button
                  v-for="(action, index) in getActionsByType(
                    task.actions_json,
                    'zoom'
                  )"
                  :key="'zoom-' + index"
                  class="tech-button zoom-button"
                  @click="handleEdit(task, action)"
                >
                  <span class="button-text">{{ getActionText(action) }}</span>
                </button>
              </div>
            </div>

            <!-- 变体按钮组 -->
            <div
              v-if="getActionsByType(task.actions_json, 'variant').length"
              class="action-group variant-group"
            >
              <div class="group-buttons">
                <button
                  v-for="(action, index) in getActionsByType(
                    task.actions_json,
                    'variant'
                  )"
                  :key="'variant-' + index"
                  class="tech-button variant-button"
                  @click="handleEdit(task, action)"
                >
                  <span class="button-text">{{ getActionText(action) }}</span>
                </button>
              </div>
            </div>

            <!-- 重新生成按钮组 -->
            <div
              v-if="getActionsByType(task.actions_json, 'refresh').length"
              class="action-group refresh-group"
            >
              <div class="group-buttons">
                <button
                  v-for="(action, index) in getActionsByType(
                    task.actions_json,
                    'refresh'
                  )"
                  :key="'refresh-' + index"
                  class="tech-button refresh-button"
                  @click="handleEdit(task, action)"
                >
                  <span class="button-text">{{ getActionText(action) }}</span>
                </button>
              </div>
            </div>

            <!-- 其他按钮组 -->
            <div
              v-if="getActionsByType(task.actions_json, 'other').length"
              class="action-group default-group"
            >
              <div class="group-buttons">
                <button
                  v-for="(action, index) in getActionsByType(
                    task.actions_json,
                    'other'
                  )"
                  :key="'other-' + index"
                  class="tech-button default-button"
                  @click="handleEdit(task, action)"
                >
                  <span class="button-text">{{ getActionText(action) }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 错误信息 -->
        <div
          v-if="task.status === 'FAIL' && task.error_show"
          class="task-error"
        >
          {{ task.error_show }}
        </div>
      </div>
    </div>

    <!-- 全屏图片预览弹窗 -->
    <el-dialog
      v-model="showPreview"
      fullscreen
      :show-close="true"
      :close-on-click-modal="true"
      :close-on-press-escape="true"
      :append-to-body="true"
      class="image-preview-dialog"
    >
      <img
        v-if="currentPreviewTask"
        :src="currentPreviewTask.oss_image_url"
        alt="预览大图"
        class="preview-img"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from "vue";
import { ElMessage } from "element-plus";
import {
  MJTask,
  MJTaskStatus,
  editImage,
  cancelTask,
  queryProgress,
  parseScriptToTasks,
  generateImage,
} from "@/api/mj";
import {
  Picture,
  Loading,
  ZoomIn,
  CopyDocument,
  RefreshRight,
  More,
} from "@element-plus/icons-vue";

const props = defineProps<{
  roleId: number;
  tasks: MJTask[];
  messageId: string;
  messageContent: string;
  inferring: boolean;
}>();

const emit = defineEmits(["update:tasks"]);

// 添加生成状态
const isGenerating = ref(false);

// 添加生成图片方法
const handleGenerateImage = async () => {
  if (!props.messageContent || !props.messageId) {
    ElMessage.error("消息内容或ID不存在");
    return;
  }

  isGenerating.value = true;
  try {
    const response = await parseScriptToTasks({
      script: props.messageContent,
      message_id: props.messageId,
    });

    if (response.data) {
      ElMessage.success("图片任务已创建");

      // 构造标准任务对象
      const newTask = {
        id: response.data.id,
        user_imagine_id: response.data.user_imagine_id,
        status: response.data.status,
        prompt: response.data.prompt || props.messageContent,
        oss_image_url: response.data.oss_image_url,
        image_id: response.data.image_id,
        actions_json: response.data.actions_json,
        error_show: response.data.error_show || "",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      // 输出日志检查任务对象
      console.log("创建的新任务:", newTask);

      // 更新任务列表
      const updatedTasks = [newTask];
      emit("update:tasks", updatedTasks);

      // 立即开始轮询任务状态
      if (newTask.status === "WAITING" || newTask.status === "IN_PROCESSING") {
        console.log("立即开始轮询新创建的任务:", newTask.id);
        setTimeout(() => pollTaskStatus(newTask), 1000);
      }
    }
  } catch (error) {
    console.error("图片任务创建失败:", error);
    ElMessage.error("图片任务创建失败，请重试");
  } finally {
    isGenerating.value = false;
  }
};

// 状态文本映射
const statusTextMap: Record<MJTaskStatus, string> = {
  WAITING: "等待中",
  IN_PROCESSING: "生成中",
  SUCCESS: "已完成",
  FAIL: "失败",
  CANCEL: "已取消",
};

// 获取状态显示文本
const getStatusText = (status: MJTaskStatus) => {
  return statusTextMap[status] || status;
};

// 获取操作按钮文本
const getActionText = (action: any) => {
  // 检查 action 是否为对象
  if (typeof action === "object" && action !== null) {
    // 优先使用 popText 属性
    if (action.popText) {
      return action.popText;
    }
    // 如果没有 popText，则使用 name 属性
    if (action.name) {
      return action.name;
    }
    // 如果有 value 属性，分析 value
    if (action.value && typeof action.value === "string") {
      if (action.value.includes("upsample")) {
        return "放大";
      } else if (action.value.includes("variation")) {
        return "变体";
      } else if (
        action.value.includes("regenerate") ||
        action.value.includes("reset")
      ) {
        return "重新生成";
      }
    }
  }
  // 如果 action 是字符串，保留原先的逻辑
  else if (typeof action === "string") {
    if (action.includes("upsample")) {
      return "放大";
    } else if (action.includes("variation")) {
      return "变体";
    } else if (action.includes("regenerate") || action.includes("reset")) {
      return "重新生成";
    }
  }

  return "操作";
};

// 获取操作按钮图标
const getActionIcon = (action: any) => {
  // 检查 action 是否为对象
  if (typeof action === "object" && action !== null) {
    // 根据 value 或 name 确定图标
    if (
      (action.value && action.value.includes("upsample")) ||
      (action.name && action.name.includes("U"))
    ) {
      return "ZoomIn";
    } else if (
      (action.value && action.value.includes("variation")) ||
      (action.name && action.name.includes("V"))
    ) {
      return "CopyDocument";
    } else if (
      (action.value &&
        (action.value.includes("regenerate") ||
          action.value.includes("reset"))) ||
      (action.name && action.name === "REGENERATE")
    ) {
      return "RefreshRight";
    }
  } else if (typeof action === "string") {
    if (action.includes("upsample")) {
      return "ZoomIn";
    } else if (action.includes("variation")) {
      return "CopyDocument";
    } else if (action.includes("regenerate") || action.includes("reset")) {
      return "RefreshRight";
    }
  }
  return "More";
};

// 处理编辑操作
const handleEdit = async (task: MJTask, action: any) => {
  try {
    // 确定要发送给API的action值
    const actionValue =
      typeof action === "object" && action !== null ? action.value : action;

    if (!actionValue) {
      ElMessage.error("无效的操作");
      return;
    }

    const response = await editImage({
      action: actionValue,
      image_id: task.image_id,
    });

    if (response.data) {
      // 假设 response.data 包含新任务的完整信息
      // 例如： { id: new_id, user_imagine_id: new_imagine_id, status: 'WAITING', prompt: new_prompt, ... }
      const newTaskData = response.data;

      // 构造新的任务对象
      const newTask: MJTask = {
        id: newTaskData.id,
        user_imagine_id: newTaskData.user_imagine_id,
        status: newTaskData.status || "WAITING", // 确保有初始状态
        prompt: newTaskData.prompt || `操作: ${getActionText(action)}`, // 构造一个默认提示或使用返回的
        oss_image_url: newTaskData.oss_image_url || "",
        image_id: newTaskData.image_id || "", // 新任务可能有新的 image_id
        actions_json: newTaskData.actions_json || [],
        error_show: newTaskData.error_show || "",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      console.log("编辑操作创建的新任务:", newTask); // 日志记录新任务

      ElMessage.success("新的图片任务已创建");

      // 将新任务添加到任务列表
      // 创建一个包含所有旧任务和新任务的新数组
      const updatedTasks = [...props.tasks, newTask];
      emit("update:tasks", updatedTasks);

      // 如果新任务需要轮询，立即开始
      if (newTask.status === "WAITING" || newTask.status === "IN_PROCESSING") {
        console.log("立即开始轮询新创建的编辑任务:", newTask.id);
        // 稍微延迟启动轮询，确保状态更新已传播
        setTimeout(() => pollTaskStatus(newTask), 500);
      }

      // 注意：不再修改原任务 task 的状态
      // emit(
      //   "update:tasks",
      //   props.tasks.map((t) =>
      //     t.id === task.id ? { ...t, status: "WAITING" as MJTaskStatus } : t
      //   )
      // );
    } else {
      // 处理 API 调用成功但没有返回有效 data 的情况
      console.error("编辑操作 API 调用成功，但未返回新任务数据:", response);
      ElMessage.error("操作已提交，但获取新任务信息失败");
    }
  } catch (error) {
    console.error("编辑操作失败:", error);
    ElMessage.error("操作失败，请重试");
  }
};

// 处理取消操作
const handleCancel = async (task: MJTask) => {
  try {
    const response = await cancelTask({
      user_imagine_id: task.user_imagine_id,
    });

    if (response.data) {
      ElMessage.success("任务已取消");
      // 触发任务列表更新
      emit(
        "update:tasks",
        props.tasks.map((t) =>
          t.id === task.id ? { ...t, status: "CANCEL" as MJTaskStatus } : t
        )
      );
    }
  } catch (error) {
    console.error("取消任务失败:", error);
    ElMessage.error("取消失败，请重试");
  }
};

// 在 script setup 中添加:
const pollTimers = ref<Map<number, NodeJS.Timeout>>(new Map());

// 修改 pollTaskStatus 函数
const pollTaskStatus = async (task: MJTask) => {
  const maxRetries = 3;
  let retryCount = 0;

  // 清除已存在的轮询 (如果因为某些原因重复调用)
  if (pollTimers.value.has(task.id)) {
    clearTimeout(pollTimers.value.get(task.id));
    pollTimers.value.delete(task.id);
    console.log(`清理了任务 ${task.id} 的旧轮询定时器`);
  }

  const poll = async () => {
    // 检查任务是否还存在于当前列表中，避免对已移除的任务进行轮询
    // 注意：这里直接访问 props.tasks 可能不是最新的，因为 emit 是异步的。
    // 更健壮的方式可能是在父组件处理轮询启动，或者确保 pollTaskStatus 拿到的是最新的 task 引用。
    // 但基于当前结构，我们暂时这样处理。
    const currentTaskInList = props.tasks.find((t) => t.id === task.id);
    if (
      !currentTaskInList ||
      (currentTaskInList.status !== "WAITING" &&
        currentTaskInList.status !== "IN_PROCESSING")
    ) {
      console.log(`任务 ${task.id} 不再需要轮询或已从列表中移除，停止轮询。`);
      if (pollTimers.value.has(task.id)) {
        clearTimeout(pollTimers.value.get(task.id));
        pollTimers.value.delete(task.id);
      }
      return; // 停止轮询
    }

    try {
      console.log(
        `轮询任务 ${task.id} 状态 (Imagine ID: ${task.user_imagine_id})...`
      ); // 添加日志
      // 确保使用正确的 ID 进行查询
      const response = await queryProgress(task.user_imagine_id);

      if (response.data?.result) {
        const updatedTaskData = response.data.result;
        console.log(`任务 ${task.id} API 返回状态:`, updatedTaskData.status); // 添加日志

        // 获取当前任务列表的最新状态
        const latestTasks = props.tasks;
        const taskIndex = latestTasks.findIndex((t) => t.id === task.id);

        // 只在任务仍存在于列表中时更新
        if (taskIndex > -1) {
          const updatedTask = { ...latestTasks[taskIndex], ...updatedTaskData };
          const newTaskList = [...latestTasks];
          newTaskList[taskIndex] = updatedTask;

          // 更新任务状态
          emit("update:tasks", newTaskList);

          // 如果任务还在进行中，继续轮询
          if (
            updatedTask.status === "WAITING" ||
            updatedTask.status === "IN_PROCESSING"
          ) {
            // 根据状态调整轮询间隔
            const interval = updatedTask.status === "WAITING" ? 5000 : 3000;
            const timer = setTimeout(() => poll(), interval);
            pollTimers.value.set(task.id, timer);
          } else {
            // 任务完成或失败，从 timers 中移除
            pollTimers.value.delete(task.id);
            console.log(
              `任务 ${task.id} 轮询结束，状态: ${updatedTask.status}`
            );
          }
        } else {
          console.log(`任务 ${task.id} 在轮询期间已从列表中消失，停止轮询。`);
          pollTimers.value.delete(task.id); // 清理定时器
        }
      } else {
        // API 调用成功但没有 result 数据，可以认为任务状态未变化或查询出错了
        console.warn(
          `轮询任务 ${task.id} 未获取到 result 数据。Response:`,
          response
        );
        // 可以选择重试或停止
        if (retryCount < maxRetries) {
          retryCount++;
          const timer = setTimeout(() => poll(), 3000 * retryCount); // 增加重试间隔
          pollTimers.value.set(task.id, timer);
        } else {
          console.error(
            `任务 ${task.id} 轮询多次未获取到 result 数据，停止轮询。`
          );
          pollTimers.value.delete(task.id);
          // 可以选择将任务标记为失败
          const latestTasks = props.tasks;
          const taskIndex = latestTasks.findIndex((t) => t.id === task.id);
          if (taskIndex > -1) {
            const updatedTask = {
              ...latestTasks[taskIndex],
              status: "FAIL" as MJTaskStatus,
              error_show: "轮询数据异常",
            };
            const newTaskList = [...latestTasks];
            newTaskList[taskIndex] = updatedTask;
            emit("update:tasks", newTaskList);
          }
        }
      }
    } catch (error) {
      console.error(`轮询任务 ${task.id} 失败:`, error); // 添加日志
      retryCount++;
      if (retryCount <= maxRetries) {
        const timer = setTimeout(() => poll(), 3000 * retryCount); // 重试间隔
        pollTimers.value.set(task.id, timer);
      } else {
        console.error(`任务 ${task.id} 轮询达到最大重试次数，标记为失败。`);
        pollTimers.value.delete(task.id);
        // 更新任务为失败状态
        const latestTasks = props.tasks;
        const taskIndex = latestTasks.findIndex((t) => t.id === task.id);
        if (taskIndex > -1) {
          const updatedTask = {
            ...latestTasks[taskIndex],
            status: "FAIL" as MJTaskStatus,
            error_show: "轮询失败",
          };
          const newTaskList = [...latestTasks];
          newTaskList[taskIndex] = updatedTask;
          emit("update:tasks", newTaskList);
        }
      }
    }
  };

  // 开始轮询
  console.log(`为任务 ${task.id} 启动轮询流程`);
  poll();
};

// 监听 tasks 变化的 watch 可能需要调整，以避免重复启动轮询
watch(
  () => props.tasks,
  (newTasks, oldTasks) => {
    // 找出新增的任务
    const addedTasks = newTasks.filter(
      (newTask) =>
        !oldTasks || !oldTasks.some((oldTask) => oldTask.id === newTask.id)
    );

    addedTasks.forEach((task) => {
      if (
        (task.status === "WAITING" || task.status === "IN_PROCESSING") &&
        !pollTimers.value.has(task.id) // 确保没有正在进行的轮询
      ) {
        console.log(`检测到新任务 ${task.id} 需要轮询，状态: ${task.status}`);
        pollTaskStatus(task);
      }
    });

    // (可选) 清理不再存在或不再需要轮询的任务的定时器
    if (oldTasks) {
      oldTasks.forEach((oldTask) => {
        const stillExists = newTasks.some(
          (newTask) => newTask.id === oldTask.id
        );
        const needsPolling =
          (stillExists &&
            newTasks.find((t) => t.id === oldTask.id)?.status === "WAITING") ||
          newTasks.find((t) => t.id === oldTask.id)?.status === "IN_PROCESSING";
        if (
          (!stillExists || !needsPolling) &&
          pollTimers.value.has(oldTask.id)
        ) {
          console.log(
            `清理任务 ${oldTask.id} 的轮询定时器，原因：任务移除或状态不再需要轮询。`
          );
          clearTimeout(pollTimers.value.get(oldTask.id));
          pollTimers.value.delete(oldTask.id);
        }
      });
    }
  },
  { deep: true } // deep 仍然需要，因为任务内部状态会改变
  // immediate: true // 移除 immediate，避免初始加载时对所有任务启动轮询，改为在 pollTaskStatus 中判断或由父组件在挂载后触发
);

// 组件挂载时，检查现有任务是否需要启动轮询
onMounted(() => {
  props.tasks.forEach((task) => {
    if (
      (task.status === "WAITING" || task.status === "IN_PROCESSING") &&
      !pollTimers.value.has(task.id)
    ) {
      console.log(`组件挂载时，任务 ${task.id} 需要轮询`);
      pollTaskStatus(task);
    }
  });
});

// 添加组件卸载时的清理
onUnmounted(() => {
  console.log("MJTaskPanel 组件卸载，清除所有轮询定时器");
  // 清除所有轮询定时器
  pollTimers.value.forEach((timer, taskId) => {
    clearTimeout(timer);
    console.log(`Cleared timer for task ${taskId}`);
  });
  pollTimers.value.clear();
});

const showPreview = ref(false);
const currentPreviewTask = ref<any>(null);

function openPreview(task: any) {
  currentPreviewTask.value = task;
  showPreview.value = true;
}

const singleImage = (url: string) => [url];

// 获取按钮样式类
const getButtonClass = (action: any) => {
  const icon = getActionIcon(action);
  if (icon === "ZoomIn") return "zoom-button";
  if (icon === "CopyDocument") return "variant-button";
  if (icon === "RefreshRight") return "refresh-button";
  return "default-button";
};
const actionBlacklist = [
  "Upscale (2x)",
  "Upscale (4x)",
  "局部重绘",
  "往后移动2倍",
  "往后移动1.5倍",
  "往后移动自定义倍数",
];
// 按类型获取操作按钮
const getActionsByType = (actions: any[], type: string) => {
  return actions.filter((action) => {
    if (actionBlacklist.includes(action.popText)) return false;
    const icon = getActionIcon(action);
    if (type === "zoom" && icon === "ZoomIn") return true;
    if (type === "variant" && icon === "CopyDocument") return true;
    if (type === "refresh" && icon === "RefreshRight") return true;
    if (
      type === "other" &&
      !["ZoomIn", "CopyDocument", "RefreshRight"].includes(icon)
    )
      return true;
    return false;
  });
};
</script>

<style scoped>
.mj-task-panel {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.no-tasks {
  text-align: center;
  color: #999;
  padding: 2rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.inferring-message {
  text-align: center;
  color: #999;
  padding: 2rem 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.inferring-message .el-icon {
  animation: spin 1s linear infinite;
  color: #409eff;
}

.tasks-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.task-item {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.task-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.task-status.waiting {
  color: #e6a23c;
}
.task-status.in_processing {
  color: #409eff;
}
.task-status.success {
  color: #67c23a;
}
.task-status.fail {
  color: #f56c6c;
}
.task-status.cancel {
  color: #909399;
}

.task-prompt {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1rem;
  line-height: 1.4;
}

.task-image {
  margin: 1rem 0;

  :deep(.el-image) {
    width: 100%;
    max-height: 300px;
    border-radius: 4px;
    overflow: hidden;
  }
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  background: #f5f7fa;
  color: #909399;
  font-size: 0.9rem;

  .el-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }
}

.task-operations {
  margin-top: 1.5rem;
  border-top: 1px dashed #e0e0e0;
  padding-top: 1rem;
}

.operation-title {
  font-size: 0.9rem;
  color: #606266;
  margin-bottom: 0.8rem;
  font-weight: 500;
}

.action-groups {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-group {
  display: flex;
  flex-direction: column;
}

.group-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 调整按钮样式，使其在组内更加协调 */
.tech-button {
  position: relative;
  min-width: 100px;
  height: 36px;
  padding: 0 16px;
  border-radius: 18px;
  border: none;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.tech-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.tech-button:active {
  transform: translateY(1px);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.button-text {
  text-align: center;
  line-height: 1;
}

/* 放大按钮 */
.zoom-button {
  background: linear-gradient(135deg, #67c23a, #52a930);
  color: white;
}

/* 变体按钮 */
.variant-button {
  background: linear-gradient(135deg, #e6a23c, #d48b1f);
  color: white;
}

/* 重新生成按钮 */
.refresh-button {
  background: linear-gradient(135deg, #909399, #606266);
  color: white;
}

/* 默认按钮 */
.default-button {
  background: linear-gradient(135deg, #409eff, #2b85e4);
  color: white;
}

.task-error {
  margin-top: 1rem;
  padding: 0.5rem;
  background: #fef0f0;
  color: #f56c6c;
  font-size: 0.9rem;
  border-radius: 4px;
}

/* 添加转圈圈样式 */
.loading-spinner {
  display: inline-flex;
  align-items: center;
  margin-left: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.image-preview-dialog .el-dialog__body {
  position: relative;
  padding: 0;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-img {
  position: relative;
  z-index: 2;
  display: block;
  max-width: 100vw;
  max-height: 100vh;
  margin: 0 auto;
}
</style>

<style>
/* 全局覆盖 Element Plus 弹窗遮罩层的透明度 */
.el-overlay {
  background: rgba(0, 0, 0, 0.8) !important; /* 80% 透明度，可根据需要调整 */
}
</style> 