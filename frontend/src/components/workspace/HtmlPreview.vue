<template>
  <div class="html-preview">
    <!-- 输出模式开关和生成按钮 -->
    <div
      v-if="!localHtmlCode && !inferring && !generating"
      class="generate-controls-simple"
    >
      <el-button
        type="primary"
        @click="generateHtml"
        :loading="generating"
        class="generate-report-btn"
      >
        <el-icon><Document /></el-icon>
        生成可视化报告
      </el-button>
    </div>

    <!-- 实时预览区 -->
    <div v-if="generating" class="realtime-preview">
      <div class="preview-title">
        生成中（已生成：{{ localHtmlCode.length }} 字符）
      </div>
    </div>

    <!-- HTML 预览和下载按钮 -->
    <div v-else-if="localHtmlCode" class="preview-actions">
      <template v-if="localStatus === 'success'">
        <el-button type="primary" @click="showPreview">
          <el-icon><View /></el-icon>
          立即查看
        </el-button>
        <el-button @click="downloadHtml">
          <el-icon><Download /></el-icon>
          下载
        </el-button>
        <el-button :loading="pdfLoading" @click="downloadPdf">
          <el-icon><Download /></el-icon>
          下载为 PDF
        </el-button>
      </template>
      <el-button
        v-if="localStatus === 'success' || localStatus === 'failed'"
        :loading="regenerating"
        @click="regenerateHtml"
      >
        <el-icon><Document /></el-icon>
        重新生成
      </el-button>
    </div>

    <!-- 预览浮层 -->
    <el-dialog
      v-model="previewVisible"
      title="HTML 预览"
      width="80%"
      :close-on-click-modal="true"
      :close-on-press-escape="true"
      :append-to-body="true"
      class="preview-dialog"
    >
      <iframe
        ref="previewFrame"
        class="preview-frame"
        sandbox="allow-scripts allow-same-origin"
      ></iframe>
    </el-dialog>

    <el-dialog
      v-model="selectDialogVisible"
      width="80%"
      :close-on-click-modal="false"
      :close-on-press-escape="true"
      :append-to-body="true"
      title="历史消息列表"
      class="edit-dialog message-select-dialog"
    >
      <el-input
        v-model="searchText"
        placeholder="搜索消息内容"
        clearable
        style="margin-bottom: 8px; width: 100%"
      />
      <div class="msg-list-scroll">
        <el-checkbox-group v-model="selectedMessageIds">
          <div
            v-for="msg in filteredMessages"
            :key="msg.id"
            class="msg-item-flex"
          >
            <el-checkbox :label="msg.id" class="msg-checkbox"
              >&nbsp;</el-checkbox
            >
            <div class="msg-content">
              <div v-if="!expandedIds.includes(msg.id)">
                {{ getShortContent(msg) }}
                <el-link type="primary" @click="toggleExpand(msg.id)"
                  >展开</el-link
                >
              </div>
              <div v-else>
                {{ msg.content }}
                <el-link type="primary" @click="toggleExpand(msg.id)"
                  >收起</el-link
                >
              </div>
            </div>
          </div>
        </el-checkbox-group>
      </div>
      <template #footer>
        <el-button @click="selectDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="goToEdit">下一步</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="editDialogVisible"
      title="编辑内容"
      width="80%"
      :close-on-click-modal="false"
      :close-on-press-escape="true"
      :append-to-body="true"
      class="edit-dialog"
    >
      <el-input
        v-model="editedContent"
        type="textarea"
        :rows="15"
        placeholder="请输入内容"
        style="width: 100%"
      />
      <div class="word-count-display">
        <span :class="{ 'over-limit': editedContent.length > 5000 }">
          {{ editedContent.length }} / 5000 字
        </span>
        <span v-if="editedContent.length > 5000" class="warning-text">
          （超出字数限制，无法提交）
        </span>
      </div>
      <template #footer>
        <div class="edit-dialog-footer">
          <div class="footer-left">
            <el-button @click="editDialogVisible = false">取消</el-button>
            <el-button
              @click="
                editDialogVisible = false;
                selectDialogVisible = true;
              "
              >重新选择</el-button
            >
          </div>
          <div class="footer-right">
            <div class="output-mode-switch-inline">
              <span class="switch-label">输出模式：</span>
              <el-switch
                v-model="isRawOutput"
                class="mode-switch"
                active-text="原文"
                inactive-text="提炼"
                :active-value="true"
                :inactive-value="false"
                inline-prompt
                size="small"
                active-color="#4facfe"
                inactive-color="#00d2ff"
              />
            </div>
            <el-button type="primary" @click="saveEdit">确认生成</el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted, computed } from "vue";
import { View, Download, Document } from "@element-plus/icons-vue";
import { ElDialog, ElMessage } from "element-plus";
import type { Message } from "@/types/chat";
import config from "@/config";
import { QuillEditor } from "@vueup/vue-quill";
import "@vueup/vue-quill/dist/vue-quill.snow.css";
import "@/styles/variables.css";

/**
 * @typedef {Object} Props
 * @property {string} htmlCode - HTML 代码内容
 * @property {string} messageId - 消息 ID
 * @property {any} message - 消息内容
 * @property {string} [model] - 可选的模型
 */
const props = defineProps<{
  html: {
    html_code: string;
    status: string;
    id: number;
    type: "session" | "message";
    session_id: number;
    message_id: number;
    prompt: string;
  };
  messageId: string;
  sessionId: number; // 会话ID
  content: string; // 消息内容
  messages?: Message[];
  model?: string;
  inferring?: boolean;
}>();

const localHtmlCode = ref(props.html.html_code || "");
const localStatus = ref(props.html.status || "");
const generating = computed(() => localStatus.value === "generating");
const regenerating = ref(false);

/**
 * 输出模式状态
 * @type {import('vue').Ref<boolean>} - true: 原文输出(raw), false: 提炼输出(zip)
 */
const isRawOutput = ref(false); // 默认为提炼输出

function startSSE(url: string, token: string, onMessage: (data: any) => void) {
  fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then((response) => {
    const reader = response.body?.getReader();
    if (!reader) return;
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    function read() {
      reader.read().then(({ done, value }) => {
        if (done) return;
        buffer += decoder.decode(value, { stream: true });
        let lines = buffer.split("\n\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              onMessage(data);
            } catch (e) {}
          }
        }
        read();
      });
    }
    read();
  });
}
// 首次生成会触发，后续流式更新会触发
watch(
  () => props.html.status,
  (status) => {
    if (status === "generating") {
      startPreviewStream();
    }
  },
  { immediate: true }
);

onUnmounted(() => {
  // 清理 SSE 连接（如有）
});

const previewVisible = ref(false);
const previewFrame = ref<HTMLIFrameElement | null>(null);

const showPreview = () => {
  previewVisible.value = true;
};

watch(previewVisible, async (newVal) => {
  if (newVal) {
    await nextTick();
    if (previewFrame.value) {
      const frame = previewFrame.value;
      const doc = frame.contentDocument || frame.contentWindow?.document;
      if (doc) {
        doc.open();
        doc.write(stripMarkdownCodeBlock(localHtmlCode.value));
        doc.close();
      }
    }
  }
});

const downloadHtml = () => {
  try {
    // 兜底去除 markdown 代码块包裹
    const pureHtml = stripMarkdownCodeBlock(localHtmlCode.value);
    const blob = new Blob([pureHtml], { type: "text/html" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "preview.html";
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    ElMessage.success("下载成功");
  } catch (error) {
    ElMessage.error("下载失败");
  }
};

const pdfLoading = ref(false);

const downloadPdf = async () => {
  pdfLoading.value = true;
  try {
    const token = localStorage.getItem("token") || "";
    const url = `${config.baseURL}/api/html/generate/pdf?id=${props.html.id}`;
    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!response.ok) throw new Error("下载失败");
    const blob = await response.blob();
    const a = document.createElement("a");
    a.href = window.URL.createObjectURL(blob);
    a.download = `${props.html.id}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(a.href);
    document.body.removeChild(a);
    ElMessage.success("PDF 下载成功");
  } catch (error) {
    ElMessage.error("PDF 下载失败");
  } finally {
    pdfLoading.value = false;
  }
};
const doGenerateHtml = ref(false);
const generateHtml = async () => {
  if (props.messages && (!editedContent.value || !doGenerateHtml.value)) {
    // 传的是一批消息。就应该把消息内容拼接起来, 然后让用户编辑。
    selectDialogVisible.value = true;
    return;
  }
  if (!props.content && !editedContent.value) {
    ElMessage.error("消息内容不存在，无法生成HTML");
    return;
  }
  doGenerateHtml.value = false;
  const content = props.content || editedContent.value;
  localHtmlCode.value = "";
  localStatus.value = "generating";
  try {
    const url = config.baseURL + "/api/html/generate/streaming";
    const token = localStorage.getItem("token") || "";
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({
        text: content,
        message_id: props.messageId,
        session_id: props.sessionId,
        type: props.html.type,
        model: "deepseek",
        key_type: isRawOutput.value ? "raw" : "zip", // 添加输出模式参数
      }),
    });
    const res = await response.json();
    if (res.success) {
      // 任务提交成功，进入生成中状态, 有watch, 会自动启动流式查询
      localStatus.value = "generating";
      emit("update:html", {
        html_code: "",
        status: "generating",
        id: res.data.id,
        message_id: props.messageId,
        type: props.html.type,
        session_id: props.sessionId,
        prompt: content,
      });
    } else {
      ElMessage.error(res.message || "生成任务提交失败");
      localStatus.value = "failed";
    }
  } catch (error) {
    ElMessage.error("生成失败");
    localStatus.value = "failed";
  }
};

function startPreviewStream() {
  const token = localStorage.getItem("token") || "";
  const url = `${config.baseURL}/api/html/stream/html/preview?id=${props.html.id}&last_html_len=${localHtmlCode.value.length}`;
  startSSE(url, token, (data) => {
    if (data.html_piece) {
      localHtmlCode.value += data.html_piece;
    }
    localStatus.value = data.status;
    if (data.status === "success" || data.status === "failed") {
      emit("update:html", {
        html_code: localHtmlCode.value,
        status: data.status,
        id: props.html.id,
        message_id: props.messageId,
        type: props.html.type,
        session_id: props.sessionId,
        prompt: editedContent.value,
      });
    }
  });
}

/**
 * 监听 model 变化，若已生成 htmlCode，则自动重新生成
 */
watch(
  () => props.model,
  async (newModel, oldModel) => {
    console.log("model 变化:", newModel, oldModel);
  }
);

// watch(localHtmlCode, async () => {
//   await nextTick();
//   const pre = previewPreRef.value;
//   if (pre) {
//     pre.scrollTop = pre.scrollHeight;
//   }
// });

const emit = defineEmits(["update:html"]);

function stripMarkdownCodeBlock(html) {
  // 去除首部 ```html（可有可无空格），以及尾部 ```
  return html
    .replace(/^```html\s*/i, "")
    .replace(/```\s*$/i, "")
    .trim();
}

/**
 * 重新生成 HTML
 */
const regenerateHtml = async () => {
  if (props.html.type === "session") {
    // 重新编辑消息。
    editedContent.value = props.html.prompt;
    editDialogVisible.value = true;
    return;
  }
  regenerating.value = true;
  try {
    const url = config.baseURL + "/api/html/generate/streaming";
    const token = localStorage.getItem("token") || "";
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({
        text: props.content,
        message_id: props.messageId,
        type: props.html.type,
        session_id: props.sessionId,
        model: "deepseek",
        force: true, // 关键参数
        key_type: isRawOutput.value ? "raw" : "zip", // 添加输出模式参数
      }),
    });
    const res = await response.json();
    if (res.success) {
      localHtmlCode.value = "";
      localStatus.value = "generating";
      emit("update:html", {
        html_code: "",
        status: "generating",
        id: res.data.id,
        message_id: props.messageId,
        type: props.html.type,
        session_id: props.sessionId,
        prompt: editedContent.value,
      });
      ElMessage.success("已重新提交生成任务");
    } else {
      ElMessage.error(res.message || "重新生成失败");
    }
  } catch (error) {
    ElMessage.error("重新生成失败");
  } finally {
    regenerating.value = false;
  }
};

const selectDialogVisible = ref(false);
const selectedMessageIds = ref<number[]>([]);
const editDialogVisible = ref(false);
const editedContent = ref("");
const searchText = ref("");
const expandedIds = ref<number[]>([]);

const goToEdit = () => {
  const selectedMsgs = props.messages?.filter((msg) =>
    selectedMessageIds.value.includes(msg.id)
  );
  const content = selectedMsgs?.map((msg) => msg.content).join("\n") || "";
  editedContent.value = content;
  selectDialogVisible.value = false;
  editDialogVisible.value = true;
};

const saveEdit = () => {
  if (editedContent.value.length > 5000) {
    ElMessage.error("内容不能超过5000个字！");
    return;
  }
  editDialogVisible.value = false;
  // update html.prompt
  props.html.prompt = editedContent.value;
  doGenerateHtml.value = true;
  emit("update:html", props.html);
  generateHtml();
};

const filteredMessages = computed(() => {
  if (!props.messages) return [];
  const search = searchText.value.toLowerCase();
  return props.messages.filter((msg) =>
    msg.content.toLowerCase().includes(search)
  );
});

const getShortContent = (msg: Message) => {
  const content = msg.content
    .replace(/<[^>]+>/g, "")
    .replace(/\s+/g, " ")
    .trim();
  return content.length > 50 ? content.slice(0, 50) + "..." : content;
};

const toggleExpand = (id: number) => {
  if (expandedIds.value.includes(id)) {
    expandedIds.value = expandedIds.value.filter((i) => i !== id);
  } else {
    expandedIds.value.push(id);
  }
};
</script>

<style scoped>
/* 生成报告按钮区域优化 */
.html-preview {
  display: inline-block;
  border-radius: 12px;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

/* 添加科技风装饰元素 */
.html-preview::before {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  width: 150px;
  height: 150px;
  background: radial-gradient(
    circle,
    rgba(79, 172, 254, 0.1) 0%,
    rgba(0, 242, 254, 0.05) 30%,
    transparent 70%
  );
  border-radius: 50%;
  pointer-events: none;
}

.html-preview::after {
  content: "";
  position: absolute;
  bottom: -30px;
  left: -30px;
  width: 120px;
  height: 120px;
  background: radial-gradient(
    circle,
    rgba(99, 125, 255, 0.08) 0%,
    transparent 70%
  );
  border-radius: 50%;
  pointer-events: none;
}

/* 生成按钮增强样式 */
.html-preview .el-button {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  border-radius: 10px;
  padding: 12px 24px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 150, 0.1);
  position: relative;
  overflow: hidden;
}

.html-preview .el-button--primary {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-color: transparent;
}

.html-preview .el-button--primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(79, 172, 254, 0.25);
}

.html-preview .el-button--primary::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  transition: all 0.8s;
}

.html-preview .el-button--primary:hover::before {
  left: 100%;
}

/* 生成可视化报告按钮样式优化 */
.generate-report-btn {
  min-width: 180px !important;
  height: 44px !important;
  border-radius: 10px !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 10px !important;
  margin: 0 !important;
  background: linear-gradient(135deg, #4776e6 0%, #00d2ff 100%) !important;
  border: none !important;
  color: white !important;
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
  position: relative !important;
  overflow: hidden !important;
  box-shadow: 0 8px 16px rgba(0, 0, 150, 0.12) !important;
}

.generate-report-btn:hover {
  transform: translateY(-3px) !important;
  box-shadow: 0 12px 20px rgba(0, 0, 150, 0.15) !important;
  filter: brightness(1.05) !important;
}

.generate-report-btn:active {
  transform: translateY(0) scale(0.98) !important;
  box-shadow: 0 6px 12px rgba(0, 0, 150, 0.1) !important;
}

.generate-report-btn .el-icon {
  font-size: 18px !important;
  transition: all 0.3s !important;
}

.generate-report-btn:hover .el-icon {
  transform: scale(1.2) rotate(5deg) !important;
}

/* 添加光效 */
.generate-report-btn::before {
  content: "" !important;
  position: absolute !important;
  top: 0 !important;
  left: -100% !important;
  width: 100% !important;
  height: 100% !important;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.3) 50%,
    rgba(255, 255, 255, 0) 100%
  ) !important;
  transition: all 0.8s !important;
  transform: skewX(-25deg) !important;
}

.generate-report-btn:hover::before {
  left: 100% !important;
}

/* 报告生成状态展示优化 */
.realtime-preview {
  margin: 16px 0;
  border: 1px solid rgba(99, 125, 255, 0.2);
  border-radius: 12px;
  background: rgba(240, 246, 255, 0.5);
  padding: 20px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 5px 15px rgba(0, 0, 150, 0.05);
}

.realtime-preview::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  opacity: 0.8;
  animation: progressBar 2s linear infinite;
  background-size: 200% 100%;
}

@keyframes progressBar {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}

/* 缩减按钮区域尺寸 */
.preview-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px; /* 减小按钮间距 */
  margin: 20px auto; /* 缩小上下边距 */
  max-width: 700px; /* 限制最大宽度 */
  padding: 15px; /* 减小内边距 */
  border-radius: 12px;
  flex-wrap: wrap;
}

/* 底部装饰线 - 保留科技感但不添加额外空间 */
.preview-actions::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 10%;
  right: 10%;
  height: 2px;
  opacity: 0.7;
}

/* 优化按钮尺寸 */
.preview-actions .el-button {
  min-width: 110px;
  height: 40px;
  padding: 0 18px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
}

/* 主按钮样式（蓝色按钮） */
.preview-actions .el-button--primary {
  background: linear-gradient(135deg, #4776e6 0%, #00d2ff 100%);
  border: none;
  color: white;
  box-shadow: 0 6px 12px rgba(0, 0, 150, 0.1);
}

.preview-actions .el-button--primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 18px rgba(0, 0, 150, 0.15);
  filter: brightness(1.05);
}

/* 次要按钮样式（白色按钮） */
.preview-actions .el-button--default {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(99, 125, 255, 0.3);
  color: #4c5d7c;
  box-shadow: 0 6px 12px rgba(0, 0, 150, 0.06);
}

.preview-actions .el-button--default:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(79, 172, 254, 0.5);
  color: #4776e6;
  transform: translateY(-3px);
  box-shadow: 0 10px 18px rgba(0, 0, 150, 0.1);
}

/* 按钮图标共享样式 */
.preview-actions .el-button .el-icon {
  font-size: 16px;
  transition: all 0.4s;
}

.preview-actions .el-button:hover .el-icon {
  transform: scale(1.2);
}

/* 按钮光效共享样式 */
.preview-actions .el-button::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.3) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  transition: all 0.8s;
  transform: skewX(-25deg);
}

.preview-actions .el-button:hover::before {
  left: 100%;
}

/* 点击效果共享样式 */
.preview-actions .el-button:active {
  transform: translateY(0) scale(0.98);
  transition: all 0.15s;
}

.preview-dialog :deep(.el-dialog__body) {
  padding: 0;
  height: 80vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  max-height: 80vh;
  overflow-y: auto;
}

.preview-dialog :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.preview-dialog :deep(.el-dialog__header) {
  background: linear-gradient(90deg, #3a7bd5, #3a6073);
  padding: 16px 20px;
}

.preview-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 500;
}

.preview-dialog :deep(.el-dialog__headerbtn) {
  top: 16px;
}

.preview-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: rgba(255, 255, 255, 0.9);
}

.preview-frame {
  width: 100%;
  height: 100%;
  min-height: 80vh;
  border: none;
  background: white;
  display: block;
}

.preview-title {
  font-size: 14px;
  color: #5a6a85;
  font-weight: 500;
  display: flex;
  align-items: center;
}

.preview-title::before {
  content: "";
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #4facfe;
  margin-right: 8px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.4;
  }
}

.preview-pre {
  min-height: 120px;
  max-height: 200px;
  overflow-y: auto;
  background: rgba(10, 20, 40, 0.02);
  border-radius: 8px;
  padding: 16px;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier,
    monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  border: 1px solid rgba(99, 125, 255, 0.1);
}

.msg-item-flex {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  transition: all 0.2s;
  padding: 12px;
  border-radius: 10px;
  border: 2px solid #e0e4e8;
  background: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  position: relative;
}

.msg-item-flex::before {
  content: "";
  position: absolute;
  left: 4px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 30px;
  background: #e5e7eb;
  border-radius: 2px;
  transition: all 0.2s ease;
}

.msg-item-flex:hover {
  transform: translateX(4px);
  border-color: #9ca3af;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.msg-item-flex:hover::before {
  background: #9ca3af;
  height: 35px;
}

.msg-checkbox {
  margin-top: 6px;
  margin-left: 8px;
  flex-shrink: 0;
}

.msg-content {
  word-break: break-all;
  white-space: pre-wrap;
  background: linear-gradient(145deg, #f8faff, #f0f4fc);
  border-radius: 10px;
  padding: 16px 20px;
  font-size: 15px;
  line-height: 1.8;
  margin-left: 12px;
  width: 100%;
  box-sizing: border-box;
  border: 1px solid rgba(99, 125, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 150, 0.04);
  transition: all 0.2s;
}

.msg-content:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 150, 0.08);
}

.msg-list-scroll {
  max-height: 50vh;
  overflow-y: auto;
  padding-right: 12px;
  margin: 12px 0;
  scrollbar-width: thin;
  scrollbar-color: rgba(99, 125, 255, 0.3) transparent;
}

.msg-list-scroll::-webkit-scrollbar {
  width: 6px;
}

.msg-list-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.msg-list-scroll::-webkit-scrollbar-thumb {
  background-color: rgba(99, 125, 255, 0.3);
  border-radius: 6px;
}

:deep(.el-button) {
  border-radius: 8px;
  transition: all 0.3s;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-color: transparent;
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  opacity: 0.9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(79, 172, 254, 0.3);
}

:deep(.el-button--default) {
  border: 1px solid rgba(99, 125, 255, 0.3);
}

:deep(.el-button--default:hover) {
  border-color: rgba(79, 172, 254, 0.7);
  color: #4facfe;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 150, 0.05);
}

:deep(.el-input__inner) {
  border-radius: 8px;
}

:deep(.el-input__inner:focus) {
}

:deep(.el-dialog__footer) {
  border-top: 1px solid rgba(99, 125, 255, 0.1);
  padding: 16px 20px;
}

/* 编辑对话框的样式优化 */
.el-dialog.edit-dialog :deep(.el-dialog__header) {
  background: linear-gradient(90deg, #3a7bd5, #3a6073);
  padding: 16px 20px;
  margin-right: 0;
}

.el-dialog.edit-dialog :deep(.el-dialog__title) {
  color: white;

  font-weight: 500;
  font-size: 18px;
}

.el-dialog.edit-dialog :deep(.el-dialog__body) {
  padding: 24px;
  background: linear-gradient(145deg, #f8faff, #f0f4fc);
  overflow-y: auto;
}

:deep(.el-textarea__inner) {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 150, 0.04);
  border: 1px solid rgba(99, 125, 255, 0.2);
  padding: 12px;
  font-size: 15px;
  line-height: 1.8;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
}

:deep(.el-textarea__inner:focus) {
  border-color: #4facfe;
  box-shadow: 0 0 0 2px rgba(79, 172, 254, 0.2),
    0 4px 16px rgba(0, 0, 150, 0.06);
}

:deep(.el-textarea__inner::placeholder) {
  color: #8c9db5;
}

/* 调整确认按钮样式 */
.el-dialog.edit-dialog :deep(.el-dialog__footer .el-button--primary) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-color: transparent;
  padding: 10px 24px;
  font-weight: 500;
}

.el-dialog.edit-dialog :deep(.el-dialog__footer .el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(79, 172, 254, 0.3);
}

/* 取消按钮微调 */
.el-dialog.edit-dialog :deep(.el-dialog__footer .el-button--default) {
  border: 1px solid rgba(99, 125, 255, 0.3);
  padding: 10px 20px;
}

.el-dialog.edit-dialog :deep(.el-dialog__footer .el-button--default:hover) {
  border-color: rgba(79, 172, 254, 0.7);
  color: #4facfe;
  background: rgba(240, 246, 255, 0.5);
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #e60012;
  border-color: #e60012;
}

:deep(.el-checkbox__inner) {
  width: 18px;
  height: 18px;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  transition: all 0.2s ease;
}

:deep(.el-checkbox__inner:hover) {
  border-color: #9ca3af;
}

/* 为选中的消息项添加特殊样式 */
.msg-item-flex:has(.el-checkbox__input.is-checked)::before {
  background: #e60012;
  height: 40px;
}

.msg-item-flex:has(.el-checkbox__input.is-checked) {
  border-color: #e60012;
  background: #fff7f7;
  box-shadow: 0 3px 8px rgba(230, 0, 18, 0.12);
}

:deep(.el-link--primary) {
  color: #4facfe;
}

:deep(.el-link--primary:hover) {
  color: #00f2fe;
}

/* 消息选择对话框特定样式 */
.message-select-dialog :deep(.el-input) {
  margin-bottom: 16px;
}

.message-select-dialog :deep(.el-input__inner) {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(99, 125, 255, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 150, 0.03);
  padding: 12px 15px;
  font-size: 15px;
  transition: all 0.3s;
}

.message-select-dialog :deep(.el-input__inner:focus) {
  background: rgba(255, 255, 255, 0.95);
  border-color: #4facfe;
  box-shadow: 0 0 0 2px rgba(79, 172, 254, 0.15),
    0 4px 10px rgba(0, 0, 150, 0.05);
}

.message-select-dialog :deep(.el-input__suffix) {
  color: rgba(99, 125, 255, 0.6);
}

.message-select-dialog .msg-item-flex {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 14px;
  border: 1px solid rgba(99, 125, 255, 0.08);
  transition: all 0.25s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 150, 0.02);
  display: flex;
  align-items: center;
}

.message-select-dialog .msg-checkbox {
  margin-top: 0;
  margin-right: 12px;
  display: flex;
  align-items: center;
}

.message-select-dialog :deep(.el-dialog__footer .el-button) {
  border-radius: 10px;
  padding: 10px 24px;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  font-weight: 500;
  position: relative;
  overflow: hidden;
}

.message-select-dialog :deep(.el-dialog__footer .el-button--default) {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(99, 125, 255, 0.2);
  color: #5a6a85;
}

.message-select-dialog :deep(.el-dialog__footer .el-button--default:hover) {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(99, 125, 255, 0.4);
  color: #4facfe;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 150, 0.05);
}

.message-select-dialog :deep(.el-dialog__footer .el-button--primary) {
  background: linear-gradient(135deg, #3a7bd5, #00d2ff);
  border: none;
  box-shadow: 0 5px 15px rgba(0, 0, 150, 0.1);
}

.message-select-dialog :deep(.el-dialog__footer .el-button--primary:hover) {
  background: linear-gradient(135deg, #3a7bd5, #00d2ff);
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 20px rgba(0, 0, 150, 0.15);
}

.message-select-dialog :deep(.el-dialog__footer .el-button--primary::before) {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  transition: all 0.8s;
}

.message-select-dialog
  :deep(.el-dialog__footer .el-button--primary:hover::before) {
  left: 100%;
}

.message-select-dialog .msg-id {
  font-size: 15px;
  font-weight: 500;
  color: #4facfe;
  min-width: 50px;
  display: inline-block;
  margin-right: 10px;
}

.message-select-dialog :deep(.el-dialog__body) {
  background: linear-gradient(145deg, #f6f9ff, #eef2fc);
  padding: 20px;
}

.message-select-dialog :deep(.el-input__inner) {
  height: 45px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(99, 125, 255, 0.2);
  box-shadow: 0 4px 10px rgba(0, 0, 150, 0.03);
}

.message-select-dialog :deep(.el-input__inner::placeholder) {
  color: #8c9db5;
  font-size: 14px;
}

/* 增加动画效果，让消息列表项有序出现 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-select-dialog .msg-item-flex {
  animation: fadeInUp 0.3s ease forwards;
  opacity: 0;
}

.message-select-dialog .msg-item-flex:nth-child(1) {
  animation-delay: 0.05s;
}
.message-select-dialog .msg-item-flex:nth-child(2) {
  animation-delay: 0.1s;
}
.message-select-dialog .msg-item-flex:nth-child(3) {
  animation-delay: 0.15s;
}
.message-select-dialog .msg-item-flex:nth-child(4) {
  animation-delay: 0.2s;
}
.message-select-dialog .msg-item-flex:nth-child(5) {
  animation-delay: 0.25s;
}
.message-select-dialog .msg-item-flex:nth-child(6) {
  animation-delay: 0.3s;
}
.message-select-dialog .msg-item-flex:nth-child(7) {
  animation-delay: 0.35s;
}
.message-select-dialog .msg-item-flex:nth-child(8) {
  animation-delay: 0.4s;
}
.message-select-dialog .msg-item-flex:nth-child(9) {
  animation-delay: 0.45s;
}
.message-select-dialog .msg-item-flex:nth-child(10) {
  animation-delay: 0.5s;
}

/* 消息内容区样式修复 */
.message-select-dialog .msg-content {
  border: none;
  box-shadow: none;
  background: transparent;
  padding: 8px 12px;
  margin-left: 0;
  flex: 1;
  font-size: 14.5px;
  line-height: 1.6;
  color: #333;
  border-radius: 6px;
}

/* 高亮当前选中的消息 */
.message-select-dialog .msg-item-flex:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(99, 125, 255, 0.2);
  box-shadow: 0 6px 15px rgba(0, 0, 150, 0.07);
  transform: translateY(-2px);
}

/* 调整消息ID样式使其更加突出 */
.message-select-dialog .msg-id {
  font-size: 14px;
  font-weight: 600;
  color: #4facfe;
  background: rgba(79, 172, 254, 0.1);
  padding: 3px 8px;
  border-radius: 6px;
  min-width: 40px;
  text-align: center;
  margin-right: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 150, 0.04);
}

/* 优化链接样式 */
.message-select-dialog :deep(.el-link) {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 13px;
  margin-left: 8px;
  transition: all 0.2s;
  background: rgba(79, 172, 254, 0.1);
}

.message-select-dialog :deep(.el-link:hover) {
  background: rgba(79, 172, 254, 0.2);
  transform: translateY(-1px);
}

/* 优化滚动区域 */
.message-select-dialog .msg-list-scroll {
  max-height: 60vh;
  overflow-y: auto;
  padding: 16px;
  margin: 0 0 12px 0;
  border-radius: 12px;
  background: linear-gradient(
    145deg,
    rgba(248, 250, 255, 0.5),
    rgba(240, 244, 252, 0.5)
  );
  box-shadow: inset 0 2px 8px rgba(0, 0, 150, 0.03);
  border: 1px solid rgba(99, 125, 255, 0.1);
}

/* 对话框整体优化 */
.message-select-dialog :deep(.el-dialog) {
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.18);
  border-radius: 16px;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

/* 添加技术线条装饰 */
.message-select-dialog :deep(.el-dialog__header)::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(79, 172, 254, 0.5) 20%,
    rgba(0, 242, 254, 0.5) 50%,
    rgba(79, 172, 254, 0.5) 80%,
    transparent 100%
  );
}

/* 设置取消按钮和下一步按钮的间距 */
.message-select-dialog :deep(.el-dialog__footer) {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 18px 24px;
  background: rgba(248, 250, 255, 0.8);
  border-top: 1px solid rgba(99, 125, 255, 0.1);
}

/* 添加复选框的选中动画 */
.message-select-dialog :deep(.el-checkbox__inner::after) {
  transition: all 0.3s cubic-bezier(0.18, 0.89, 0.32, 1.28);
}

.message-select-dialog
  :deep(.el-checkbox__input.is-checked .el-checkbox__inner::after) {
  transform: rotate(45deg) scaleY(1.2);
}

/* 简化版生成控制区域 */
.generate-controls-simple {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px auto;
  padding: 16px;
  max-width: 400px;
}

/* 输出模式开关样式 */
.output-mode-switch {
  display: flex;
  align-items: center;
  gap: 12px;
}

.switch-label {
  font-size: 14px;
  font-weight: 500;
  color: #4c5d7c;
  white-space: nowrap;
}

.mode-switch {
  --el-switch-on-color: #4facfe;
  --el-switch-off-color: #00d2ff;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

:deep(.el-switch__core) {
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 150, 0.1);
  transition: all 0.3s ease;
}

:deep(.el-switch.is-checked .el-switch__core) {
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.2);
}

:deep(.el-switch:not(.is-checked) .el-switch__core) {
  box-shadow: 0 4px 12px rgba(0, 210, 254, 0.2);
}

:deep(.el-switch__action) {
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

:deep(.el-switch__inner) {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 自定义字数统计样式 */
.word-count-display {
  text-align: right;
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
}

.word-count-display .over-limit {
  color: #f56c6c;
  font-weight: 600;
}

.word-count-display .warning-text {
  color: #f56c6c;
  font-size: 12px;
  margin-left: 8px;
}

/* 编辑对话框底部布局 */
.edit-dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 20px;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 内联输出模式开关样式 */
.output-mode-switch-inline {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(248, 250, 255, 0.8);
  border-radius: 8px;
  border: 1px solid rgba(99, 125, 255, 0.15);
  transition: all 0.3s ease;
}

.output-mode-switch-inline:hover {
  background: rgba(248, 250, 255, 0.95);
  border-color: rgba(99, 125, 255, 0.25);
  box-shadow: 0 2px 8px rgba(0, 0, 150, 0.06);
}

.output-mode-switch-inline .switch-label {
  font-size: 13px;
  font-weight: 500;
  color: #4c5d7c;
  white-space: nowrap;
}

.output-mode-switch-inline .mode-switch {
  --el-switch-on-color: #4facfe;
  --el-switch-off-color: #00d2ff;
}

.output-mode-switch-inline :deep(.el-switch__core) {
  border-radius: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 150, 0.08);
  transition: all 0.3s ease;
}

.output-mode-switch-inline :deep(.el-switch.is-checked .el-switch__core) {
  box-shadow: 0 2px 6px rgba(79, 172, 254, 0.15);
}

.output-mode-switch-inline :deep(.el-switch:not(.is-checked) .el-switch__core) {
  box-shadow: 0 2px 6px rgba(0, 210, 254, 0.15);
}

.output-mode-switch-inline :deep(.el-switch__inner) {
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .generate-controls-simple {
    max-width: 90%;
    padding: 16px;
  }

  .generate-report-btn {
    min-width: 200px !important;
  }

  .edit-dialog-footer {
    flex-direction: column;
    gap: 16px;
  }

  .footer-left,
  .footer-right {
    width: 100%;
    justify-content: center;
  }

  .footer-right {
    flex-direction: column;
    gap: 12px;
  }
}
</style> 