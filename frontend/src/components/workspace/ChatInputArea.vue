<template>
  <div class="chat-input">
    <div class="input-wrapper">
      <!-- Editing Indicator -->
      <div v-if="editingMessageId" class="editing-indicator">
        <span class="editing-text">请输入修改内容</span>
        <div class="editing-actions">
          <el-button type="text" size="small" @click="$emit('cancel-editing')"
            >取消</el-button
          >
        </div>
      </div>
      <div class="input-tips">按 Enter 发送，Ctrl + Enter 换行</div>

      <!-- 模型选择器和风格选择器按钮区域（role_id = 1 时显示,27是全能创意助手，25是小红书热门内容策划专家） -->
      <div class="controls-row">
        <!-- 模型选择器 -->
        <div class="model-selector">
          <div class="model-selector-label">模型:</div>
          <div class="model-switch-container">
            <div class="model-switch">
              <div
                class="model-switch-slider"
                :class="{ 'slide-right': selectedModel === 'deepseek' }"
              ></div>
              <button
                class="model-switch-option"
                :class="{ active: selectedModel === 'gpt' }"
                @click="$emit('update:selectedModel', 'gpt')"
              >
                <span class="model-icon">🤖</span>
                <span class="model-name">智链AI</span>
              </button>
              <button
                class="model-switch-option"
                :class="{ active: selectedModel === 'deepseek' }"
                @click="$emit('update:selectedModel', 'deepseek')"
              >
                <span class="model-icon">🧠</span>
                <span class="model-name">国产通用AI</span>
              </button>
            </div>
          </div>
        </div>

        <!-- 风格选择器切换按钮 -->
        <div v-if="props.roleId === 1" class="style-toggle">
          <div class="style-selector-label">预设:</div>
          <button
            class="style-toggle-button"
            :class="{ active: showStyleSelector }"
            @click="showStyleSelector = !showStyleSelector"
          >
            <span class="style-icon">🎨</span>
            <span class="preset-label">风格</span>
            <span v-if="selectedStyles.length" class="style-count">{{
              selectedStyles.length
            }}</span>
            <span
              class="toggle-arrow"
              :class="{ 'arrow-up': showStyleSelector }"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </span>
          </button>
        </div>
      </div>

      <!-- 风格选择器面板 -->
      <transition name="fade">
        <div
          class="style-selector"
          v-if="showStyleSelector && props.roleId === 1"
        >
          <div class="style-options">
            <div
              v-for="(style, index) in styleOptions"
              :key="index"
              :class="[
                'style-option',
                { active: selectedStyles.includes(style.id) },
              ]"
              @click="toggleStyle(style.id)"
            >
              <div class="style-content">
                <div class="style-icon">{{ getStyleIcon(style.id) }}</div>
                <div class="style-title">{{ style.title }}</div>
                <div class="style-desc">{{ style.description }}</div>
              </div>
              <div
                class="style-checkbox"
                v-if="selectedStyles.includes(style.id)"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <!-- New row container for input and send button -->
      <div class="input-row">
        <!-- Textarea container now only holds the input -->
        <div class="textarea-container">
          <el-input
            :modelValue="messageInput"
            @update:modelValue="$emit('update:messageInput', $event)"
            type="textarea"
            :rows="textareaRows"
            :placeholder="
              editingMessageId ? '请输入修改内容...' : '输入消息内容...'
            "
            resize="none"
            @keydown.enter.exact.prevent="handleEnterKey"
            @keydown.enter.ctrl.exact.prevent="handleNewLine"
            @input="adjustTextareaHeight"
            ref="textareaRef"
            class="chat-textarea"
          />
        </div>
        <!-- Send Button Container moved outside textarea-container -->
        <div class="input-actions">
          <el-upload
            :action="uploadAction"
            :headers="uploadHeaders"
            :data="uploadData"
            :show-file-list="false"
            :on-success="handleFileSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeFileUpload"
            :on-progress="handleUploadProgress"
            :on-change="handleFileChange"
            multiple
            class="chat-uploader"
          >
            <el-button :icon="Upload" :loading="isUploading"
              >上传文件</el-button
            >
          </el-upload>
          <el-button
            :type="editingMessageId ? 'success' : 'primary'"
            :loading="sending"
            @click="onSend"
            :disabled="!canSendMessage"
          >
            发送
          </el-button>
        </div>
      </div>

      <!-- Uploaded Files List -->
      <div v-if="uniqueUploadedFiles.length" class="uploaded-files">
        <div
          v-for="file in uniqueUploadedFiles"
          :key="file.id"
          class="uploaded-file-item"
        >
          <span class="file-icon">{{ getFileIcon(file.type) }}</span>
          <span class="file-name" @click="downloadFile(file)">{{
            file.name
          }}</span>
          <span class="file-size" v-if="file.size">{{
            formatFileSize(file.size)
          }}</span>
          <span class="file-status" :class="file.status">{{
            getStatusText(file.status)
          }}</span>
          <el-button
            type="text"
            :icon="Delete"
            @click="handleRemoveFile(file)"
            :disabled="file.status === 'uploading'"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onUnmounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Upload, Delete, Brush, Close } from "@element-plus/icons-vue";
import { v4 as uuidv4 } from "uuid";
import dayjs from "dayjs"; // Import dayjs if needed for file timestamps, otherwise remove

// 生成稳定的文件唯一标识
const generateFileId = (file: { name: string; size: number }): string => {
  // 将文件名和大小组合生成相对唯一的标识
  return `${file.name}-${file.size}-${Date.now()}`;
};

// --- Props ---
const props = defineProps<{
  messageInput: string;
  uploadedFiles: Array<{
    id: string;
    name: string;
    size: number;
    type: string;
    status: "uploading" | "parsing" | "completed" | "error";
    dify_file_id?: string;
    obs_preview_url?: string;
    url?: string;
    raw?: File;
  }>;
  sending: boolean;
  editingMessageId: string | null;
  roleId?: number | string;
  activeBranchId?: number;
  baseUrl: string;
  authToken: string;
  selectedModel: "gpt" | "deepseek";
}>();

// --- Emits ---
const emit = defineEmits([
  "update:messageInput",
  "update:uploadedFiles",
  "send",
  "cancel-editing",
  "update:selectedModel",
]);

// --- Refs and State ---
const textareaRef = ref<any>(null);
const textareaRows = ref(3); // Changed initial rows from 1 to 3
const maxRows = 6;
const isUploading = ref(false);
const showStyleSelector = ref(false);
const selectedStyles = ref<number[]>([]); // 预设风格选择状态

// 风格选项定义
const styleOptions = [
  {
    id: 1,
    title: "品牌洞察 × 诗意想象",
    description: "奥美的品牌洞察力结合李欣频的诗意表达",
    combination: "奥美 + 李欣频",
  },
  {
    id: 2,
    title: "叙事 × 冲突",
    description: "W+K的叙事技巧结合天与空的冲突美学",
    combination: "Wieden+Kennedy + 天与空",
  },
  {
    id: 3,
    title: "极简 × 赛博朋克",
    description: "MUJI的日式极简美学遇见未来赛博朋克",
    combination: "MUJI + 赛博朋克",
  },
  {
    id: 4,
    title: "经典 × 哲思",
    description: "Apple的经典品牌调性结合许舜英的哲思主义",
    combination: "Apple + 许舜英",
  },
  {
    id: 5,
    title: "戏剧 × 情感",
    description: "Droga5的戏剧化叙事结合BBDO的情感共鸣",
    combination: "Droga5 + BBDO",
  },
  {
    id: 6,
    title: "极简 × 未来",
    description: "Yohji Yamamoto的极简哲学与银翼杀手的未来感",
    combination: "Yohji Yamamoto + Blade Runner",
  },
];

// 切换风格选择
const toggleStyle = (styleId: number) => {
  const index = selectedStyles.value.indexOf(styleId);
  if (index === -1) {
    selectedStyles.value.push(styleId);
  } else {
    selectedStyles.value.splice(index, 1);
  }
};

// 获取风格图标
const getStyleIcon = (styleId: number) => {
  const iconMap: Record<number, string> = {
    1: "🎯", // 品牌洞察
    2: "📖", // 叙事
    3: "✨", // 极简
    4: "🍎", // Apple
    5: "🎭", // 戏剧化
    6: "🌌", // 未来感
  };
  return iconMap[styleId] || "🎨";
};

// 格式化风格消息
const formatStyleMessage = (userMessage: string, selectedStyles: number[]) => {
  if (!selectedStyles.length) {
    return userMessage;
  }

  const styleDescriptions = selectedStyles
    .map((styleId) => {
      switch (styleId) {
        case 1:
          return "「奥美（品牌洞察）+ 李欣频（诗意想象）」";
        case 2:
          return "「Wieden+Kennedy（叙事）+ 天与空（冲突）」";
        case 3:
          return "「MUJI（日式极简）+ 未来赛博朋克」";
        case 4:
          return "「Apple 经典品牌调性 + 许舜英（哲思主义）」";
        case 5:
          return "「Droga5（戏剧化叙事）+ BBDO（强情感共鸣）」";
        case 6:
          return "「Yohji Yamamoto（极简哲学）+ Blade Runner（未来赛博）」";
        default:
          return "";
      }
    })
    .filter((desc) => desc !== "");

  if (styleDescriptions.length === 0) {
    return userMessage;
  }

  return `${userMessage}\n请用以下${
    styleDescriptions.length
  }种风格来完成我的上述需求：\n${styleDescriptions
    .map((desc, index) => `${index + 1}、${desc}`)
    .join("\n")}`;
};

// --- Computed Properties ---
const canSendMessage = computed(() => {
  const hasInput = props.messageInput.trim().length > 0;
  const currentFiles = props.uploadedFiles || [];
  const hasFiles = currentFiles.some((file) => file.status === "completed");
  const isNotUploading = !currentFiles.some(
    (file) => file.status === "uploading" || file.status === "parsing"
  );

  return (hasInput || hasFiles) && isNotUploading && !props.sending;
});

// 确保文件列表中没有重复项
const uniqueUploadedFiles = computed(() => {
  const uniqueFiles = [];
  const fileMap = new Map();

  for (const file of props.uploadedFiles) {
    // 使用文件名+大小作为唯一键
    const key = `${file.name}-${file.size}`;

    // 如果这是第一次见到这个文件，或者这个文件状态更新了（从uploading到completed）
    if (!fileMap.has(key) || fileMap.get(key).status !== "completed") {
      fileMap.set(key, file);
    }
  }

  return Array.from(fileMap.values());
});

const uploadAction = computed(() => `${props.baseUrl}/api/chat/files/upload`);

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${props.authToken}`,
}));

const uploadData = computed(() => ({
  role_id: props.roleId || "",
  branch_id: props.activeBranchId || undefined,
}));

// --- Methods ---

// Input Handling
const handleEnterKey = (event: KeyboardEvent) => {
  if (event.isComposing || event.keyCode === 229) return;
  event.preventDefault();
  onSend();
};

const handleNewLine = () => {
  const textarea = textareaRef.value?.$refs.textarea as HTMLTextAreaElement;
  if (textarea) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const newValue =
      props.messageInput.substring(0, start) +
      "\n" +
      props.messageInput.substring(end);
    emit("update:messageInput", newValue);
    // Move cursor after newline
    nextTick(() => {
      textarea.selectionStart = textarea.selectionEnd = start + 1;
      adjustTextareaHeight();
    });
  }
};

// Send/Edit Handling
const onSend = () => {
  if (!canSendMessage.value) return;

  // 获取原始内容
  const rawContent = props.messageInput.trim();

  // 应用风格提示如果有选择风格
  const contentToSend = formatStyleMessage(rawContent, selectedStyles.value);

  const successfulFiles = props.uploadedFiles
    .filter((f) => f.status === "completed")
    .map((f) => ({
      id: f.id,
      name: f.name,
      size: f.size,
      type: f.type,
      dify_file_id: f.dify_file_id,
      obs_preview_url: f.obs_preview_url,
      url: f.url,
    }));

  console.log("🔥🔥🔥 最新版本发送消息调试 - 2025年1月23日 🔥🔥🔥");
  console.log("🚀 发送消息时的文件信息:");
  console.log("📁 所有上传的文件:", props.uploadedFiles);
  console.log("✅ 成功上传的文件:", successfulFiles);
  console.log("🆔 文件ID列表:", successfulFiles.map(f => f.dify_file_id));
  console.log("📊 文件状态统计:", props.uploadedFiles.map(f => ({ name: f.name, status: f.status, id: f.id })));

  emit("send", {
    content: contentToSend,
    files: successfulFiles,
    isEdit: !!props.editingMessageId, // Indicate if it's an edit
    parentMessageId: props.editingMessageId, // Pass the ID being edited
    model: props.selectedModel, // Include the selected model
  });

  // Clear input after emitting (parent handles message list update)
  emit("update:messageInput", "");
  emit("update:uploadedFiles", []); // 清空文件列表
  resetTextareaHeight();

  // 发送后清空已选风格
  selectedStyles.value = [];
  showStyleSelector.value = false;
};

const onCancelEditing = () => {
  emit("cancel-editing");
  // Parent component should handle clearing editingMessageId and potentially restoring input
};

// File Upload Handling
const ALLOWED_DOCUMENT_TYPES = [
  "txt",
  "md",
  "markdown",
  "pdf",
  "html",
  "xlsx",
  "xls",
  "docx",
  "csv",
  "eml",
  "msg",
  "pptx",
  "ppt",
  "xml",
  "epub",
];
const ALLOWED_IMAGE_TYPES = ["jpg", "jpeg", "png", "gif", "webp", "svg"];

const beforeFileUpload = (rawFile: File): boolean => {
  const fileExtension = rawFile.name.split(".").pop()?.toLowerCase() || "";
  const isAllowedType =
    ALLOWED_DOCUMENT_TYPES.includes(fileExtension) ||
    ALLOWED_IMAGE_TYPES.includes(fileExtension);
  const isLt10M = rawFile.size / 1024 / 1024 < 10;

  if (!isAllowedType) {
    ElMessage.error(`不支持的文件类型: ${rawFile.name}`);
  }
  if (!isLt10M) {
    ElMessage.error(`文件大小不能超过 10MB: ${rawFile.name}`);
  }
  return isAllowedType && isLt10M;
};

const handleFileChange = (uploadFile: any, uploadFiles: any) => {
  console.log("=== 文件变化调试 ===");
  console.log("上传文件对象:", uploadFile);
  console.log("当前文件列表:", props.uploadedFiles);
  console.log("文件状态:", uploadFile.status);
  
  // 只在文件开始上传时添加到列表
  if (uploadFile.status === 'ready' || uploadFile.status === 'uploading') {
    // 检查文件是否已存在于上传列表中（使用uid而不是name+size）
    const fileExists = props.uploadedFiles.some(
      (file) => file.id === uploadFile.uid
    );

    // 如果文件已存在，则不再添加
    if (fileExists) {
      console.log("文件已存在，跳过添加:", uploadFile.uid);
      return;
    }

    const fileObj = {
      id: uploadFile.uid || uuidv4(),
      name: uploadFile.name,
      size: uploadFile.size || 0,
      type: uploadFile.name.split(".").pop()?.toLowerCase() || "unknown",
      status: "uploading" as const,
      raw: uploadFile.raw,
    };

    console.log("添加新文件到列表:", fileObj);
    emit("update:uploadedFiles", [...props.uploadedFiles, fileObj]);
    isUploading.value = true;
  }
};

const handleUploadProgress = (
  event: any,
  uploadFile: any,
  uploadFiles: any
) => {
  console.log("=== 文件上传进度调试 ===");
  console.log("上传文件对象:", uploadFile);
  console.log("当前文件列表:", props.uploadedFiles);
  
  // 检查文件是否已存在于上传列表中（使用uid而不是name+size）
  const fileExists = props.uploadedFiles.some(
    (file) => file.id === uploadFile.uid
  );

  // 如果文件已存在，则不再添加
  if (fileExists) {
    console.log("文件已存在，跳过添加:", uploadFile.uid);
    return;
  }

  const fileObj = {
    id: uploadFile.uid || uuidv4(),
    name: uploadFile.name,
    size: uploadFile.size || 0,
    type: uploadFile.name.split(".").pop()?.toLowerCase() || "unknown",
    status: "uploading" as const,
    raw: uploadFile.raw,
  };

  console.log("添加新文件到列表:", fileObj);
  emit("update:uploadedFiles", [...props.uploadedFiles, fileObj]);
  isUploading.value = true;
};

const handleFileSuccess = (response: any, uploadFile: any) => {
  console.log("🔥🔥🔥 最新版本文件上传成功处理 - 2025年1月23日 🔥🔥🔥");
  console.log("🎯 文件上传成功 - 开始处理");
  console.log("响应数据:", response);
  console.log("上传文件:", uploadFile);
  console.log("当前文件列表长度:", props.uploadedFiles.length);
  
  // 检查响应格式
  if (!response || !response.success) {
    console.error("文件上传失败，响应格式错误:", response);
    ElMessage.error("文件上传失败");
    return;
  }

  // 直接创建文件对象并添加到列表（不依赖之前的文件列表）
  const fileId = uploadFile.uid || Date.now().toString();
  const fileData = response.data;
  
  const newFile = {
    id: fileId,
    name: uploadFile.name,
    size: uploadFile.size || 0,
    type: uploadFile.name.split(".").pop()?.toLowerCase() || "unknown",
    status: "completed" as const,
    url: fileData.url,
    dify_file_id: fileData.dify_file_id,
    obs_preview_url: fileData.obs_preview_url,
    raw: uploadFile.raw,
  };

  console.log("✅ 创建的新文件对象:", newFile);

  // 检查文件是否已存在
  const existingFileIndex = props.uploadedFiles.findIndex(file => file.id === fileId);
  console.log("文件索引:", existingFileIndex);
  
  let updatedFiles;
  if (existingFileIndex >= 0) {
    // 更新现有文件
    updatedFiles = [...props.uploadedFiles];
    updatedFiles[existingFileIndex] = newFile;
    console.log("🔄 更新现有文件");
  } else {
    // 添加新文件
    updatedFiles = [...props.uploadedFiles, newFile];
    console.log("➕ 添加新文件");
  }

  console.log("📋 更新后的文件列表:", updatedFiles);
  console.log("📋 文件列表长度:", updatedFiles.length);

  // 立即更新文件列表
  emit("update:uploadedFiles", updatedFiles);

  // 强制立即更新上传状态
  isUploading.value = false;

  // 用 nextTick 确保视图更新
  nextTick(() => {
    checkUploadCompletion();
    console.log("🎉 文件上传完成，最终文件列表长度:", props.uploadedFiles.length);
    console.log("🎉 最终文件列表:", props.uploadedFiles);
  });
};

const handleUploadError = (error: Error, uploadFile: any) => {
  console.error("上传错误:", error);
  // 正确获取 fileId
  const fileId = uploadFile.uid;
  if (!fileId) return;

  const updatedFiles = [...props.uploadedFiles];
  const fileIndex = updatedFiles.findIndex((f) => f.id === fileId);
  if (fileIndex !== -1) {
    updatedFiles[fileIndex] = {
      ...updatedFiles[fileIndex],
      status: "error",
    };
    emit("update:uploadedFiles", updatedFiles);
    ElMessage.error(`${uploadFile.name} 上传失败`);
  }
  checkUploadCompletion();
};

const checkUploadCompletion = () => {
  const uploading = props.uploadedFiles.some(
    (f) => f.status === "uploading" || f.status === "parsing"
  );
  if (isUploading.value !== uploading) {
    isUploading.value = uploading;
  }
};

// File List Item Handling
const handleRemoveFile = (fileToRemove: any) => {
  const updatedFiles = props.uploadedFiles.filter(
    (f) => f.id !== fileToRemove.id
  );
  emit("update:uploadedFiles", updatedFiles);
  checkUploadCompletion();
};

const downloadFile = async (file: any) => {
  try {
    const downloadUrl = file.obs_preview_url || file.url;
    if (!downloadUrl) {
      throw new Error("文件链接不存在");
    }
    // Use simplest method: direct link open
    window.open(downloadUrl, "_blank");
  } catch (error: any) {
    console.error("下载文件失败:", error);
    ElMessage.error("下载文件失败: " + error.message);
  }
};

// --- Utils ---
const getFileIcon = (type: string) => {
  const iconMap: Record<string, string> = {
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
    jpg: "🖼️",
    jpeg: "🖼️",
    png: "🖼️",
    gif: "🖼️",
    webp: "🖼️",
    svg: "🖼️",
    default: "📎",
  };
  return iconMap[type] || iconMap["default"];
};

const formatFileSize = (size: number): string => {
  if (!size && size !== 0) return "";
  if (size < 1024) return size + " B";
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + " KB";
  return (size / (1024 * 1024)).toFixed(1) + " MB";
};

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    uploading: "上传中",
    parsing: "解析中",
    completed: "已完成",
    error: "失败",
  };
  return statusMap[status] || "未知";
};

// Textarea Height Adjustment
const adjustTextareaHeight = () => {
  nextTick(() => {
    const textarea = textareaRef.value?.$refs.textarea;
    if (textarea) {
      const computedStyle = getComputedStyle(textarea);
      const lineHeight = parseFloat(computedStyle.lineHeight) || 20;
      const paddingTop = parseFloat(computedStyle.paddingTop) || 0;
      const paddingBottom = parseFloat(computedStyle.paddingBottom) || 0;
      const minHeight = lineHeight + paddingTop + paddingBottom;
      const maxHeight = maxRows * lineHeight + paddingTop + paddingBottom;

      textarea.style.height = "auto";
      const scrollHeight = textarea.scrollHeight;
      let newHeight = Math.max(minHeight, scrollHeight);
      newHeight = Math.min(newHeight, maxHeight);
      textarea.style.height = `${newHeight}px`;
      textarea.style.overflowY = scrollHeight > maxHeight ? "auto" : "hidden";
    }
  });
};

const resetTextareaHeight = () => {
  nextTick(() => {
    const textarea = textareaRef.value?.$refs.textarea;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.overflowY = "hidden";
    }
    textareaRows.value = 3;
  });
};

// Watch for external changes to messageInput (e.g., when editing starts)
watch(
  () => props.messageInput,
  () => {
    nextTick(adjustTextareaHeight);
  }
);
// Watch for editing state change to potentially clear files or restore input
watch(
  () => props.editingMessageId,
  (newId, oldId) => {
    if (newId !== oldId && newId === null) {
      // Exited editing mode, parent should handle clearing input/files if needed
    }
    if (newId && newId !== oldId) {
      // Entered editing mode, focus and adjust height
      nextTick(() => {
        textareaRef.value?.focus();
        adjustTextareaHeight();
      });
    }
  }
);

// Lifecycle
onUnmounted(() => {
  // Cleanup if necessary
});
</script>

<style scoped>
/* Restore original styles, adapted for this component */
.chat-input {
  background: white;
  padding: 12px 20px 16px 20px;
  border-top: 1px solid #ebeef5;
  box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.04);
  flex-shrink: 0;
}

.input-wrapper {
  position: relative;
}

.editing-indicator {
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  padding: 6px 10px;
  border-radius: 6px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
}

.editing-text {
  color: #4338ca;
  font-weight: 500;
}

.editing-actions .el-button--text {
  padding: 0;
  font-size: 13px;
  color: #6b7280;
  height: auto;
  line-height: 1;
}
.editing-actions .el-button--text:hover {
  color: #ef4444;
  background-color: transparent !important;
}

.input-tips {
  font-size: 12px;
  color: #909399;
  position: absolute;
  top: -18px;
  right: 0;
  background-color: #f8f9fa;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
  letter-spacing: 0.2px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  border: 1px solid #ebeef5;
}

/* 模型选择器和风格切换器所在行 */
.controls-row {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 20px;
  margin-bottom: 12px;
  padding: 0 2px;
}

/* 模型选择器样式 - 高级版 */
.model-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.model-selector-label {
  font-size: 13px;
  color: #505968;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.model-switch-container {
  position: relative;
}

.model-switch {
  display: flex;
  position: relative;
  background-color: #f5f7fa;
  border-radius: 10px;
  padding: 3px;
  width: fit-content;
  min-width: 190px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.model-switch:hover {
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.06);
}

.model-switch-slider {
  position: absolute;
  top: 3px;
  left: 3px;
  height: calc(100% - 6px);
  width: calc(50% - 3px);
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f0ff 100%);
  border-radius: 8px;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
  z-index: 1;
  border: 1px solid rgba(160, 207, 255, 0.4);
}

.model-switch-slider.slide-right {
  transform: translateX(100%);
}

.model-switch-option {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  border: none;
  background-color: transparent;
  color: #606266;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
  outline: none;
  font-weight: 500;
  flex: 1;
  white-space: nowrap;
  height: 30px;
  letter-spacing: 0.2px;
}

.model-switch-option.active {
  color: #3a8ee6;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.model-icon {
  font-size: 15px;
  transition: transform 0.2s ease;
  margin-right: 1px;
}

.model-switch-option:hover .model-icon {
  transform: scale(1.1);
}

.model-name {
  font-weight: inherit;
  font-family: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI",
    Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
}

/* 风格切换按钮样式 */
.style-toggle {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
}

.style-selector-label {
  font-size: 13px;
  color: #505968;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.style-toggle-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 10px;
  border: 1px solid #e4e7ed;
  background-color: #f5f7fa;
  color: #606266;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  outline: none;
  height: 30px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
  letter-spacing: 0.2px;
  width: 115px; /* 固定宽度与模型选择器一致 */
  justify-content: flex-start;
}

.style-toggle-button span {
  white-space: nowrap;
}

.preset-label {
  color: #3a8ee6;
  font-weight: 500;
}

.style-toggle-button:hover {
  background-color: #f0f2f5;
  border-color: #dcdfe6;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.06);
}

.style-toggle-button.active {
  background-color: #ecf5ff;
  border-color: #a0cfff;
  color: #3a8ee6;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.style-icon {
  font-size: 15px;
  transition: transform 0.2s ease;
  margin-right: 1px;
}

.style-toggle-button:hover .style-icon {
  transform: scale(1.1);
}

.toggle-arrow {
  display: flex;
  align-items: center;
  transition: transform 0.3s ease;
  margin-left: 2px;
}

.toggle-arrow.arrow-up {
  transform: rotate(180deg);
}

.style-count {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background-color: #3a8ee6;
  color: white;
  border-radius: 9px;
  font-size: 12px;
  font-weight: 500;
  margin-left: 2px;
}

/* 风格选择器面板样式 */
.style-selector {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  z-index: 10;
}

.style-options {
  display: flex;
  flex-wrap: nowrap;
  gap: 8px;
  padding: 12px;
  justify-content: space-between;
}

.style-option {
  display: flex;
  flex-direction: column;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.25s ease;
  position: relative;
  overflow: hidden;
  flex: 1;
  min-width: 0;
}

.style-option:hover {
  background: #f0f2f5;
  border-color: #c0c4cc;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.style-option.active {
  background: #ecf5ff;
  border-color: #a0cfff;
}

.style-option.active:hover {
  background: #dbedff;
}

.style-content {
  display: flex;
  flex-direction: column;
  gap: 3px;
  width: 100%;
}

.style-icon {
  font-size: 16px;
  margin-bottom: 2px;
}

.style-title {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}

.style-desc {
  font-size: 11px;
  color: #606266;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  max-height: 2.6em;
}

.style-checkbox {
  position: absolute;
  top: 5px;
  right: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3a8ee6;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  width: 18px;
  height: 18px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 淡入淡出过渡效果 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Style for el-input (textarea wrapper) */
.chat-input :deep(.el-textarea) {
  /* Target the root element if needed */
}
.chat-input :deep(.el-textarea .el-textarea__inner) {
  min-height: calc(3 * 24px) !important; /* Match initial 3 rows */
  max-height: calc(6 * 24px) !important; /* 6 rows * ~24px line-height */
  resize: none;
  font-size: 14px;
  line-height: 24px;
  padding: 8px 12px; /* Original padding */
  box-shadow: none !important;
  border: 1px solid #dcdfe6 !important; /* Original border */
  border-radius: 10px; /* Original border-radius */
  background-color: #fff !important; /* Original background */
  overflow-y: auto;
  color: #303133;
  margin-bottom: 10px; /* Space below input */
}
.chat-input :deep(.el-textarea .el-textarea__inner::placeholder) {
  color: #a8abb2;
}
.chat-input :deep(.el-textarea.is-focus .el-textarea__inner) {
  border-color: #a5b4fc !important;
  box-shadow: 0 0 0 1px #e0e7ff !important; /* Mimic focus ring */
}

/* Remove default wrapper styles if they interfere */
.chat-input :deep(.el-input__wrapper) {
  padding: 0 !important;
  box-shadow: none !important;
  border: none !important;
  background: transparent !important;
}

/* Styles for the actions container below input */
.input-actions {
  display: flex;
  justify-content: space-between; /* Align items to ends */
  align-items: center;
  margin-top: 0; /* Reset top margin, textarea margin-bottom handles it */
  gap: 10px;
}

/* Styles specifically for buttons within input-actions */
.input-actions .el-button {
  /* General button style - adjust as needed */
  padding: 0 16px;
  height: 32px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  line-height: 32px;
  border: 1px solid transparent;
}

/* Style the upload button trigger specifically */
.input-actions .chat-uploader > .el-button {
  /* Original light gray style */
  padding: 6px 12px; /* Adjust padding if needed */
  height: 32px; /* Match send button height */
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  background-color: #f4f4f5;
  color: #606266;
  border: 1px solid #e9e9eb;
  line-height: normal;
  display: inline-flex;
  align-items: center;
  transition: all 0.2s ease;
}
.input-actions .chat-uploader > .el-button:hover {
  background-color: #ebeef5;
  border-color: #dcdfe6;
  color: #303133;
}
.input-actions .chat-uploader > .el-button .el-icon {
  margin-right: 4px;
  font-size: 15px;
}
.input-actions .chat-uploader > .el-button.is-loading {
  background-color: #f4f4f5;
}

/* Style the Send/Save button specifically */
.input-actions > .el-button {
  /* This targets the send button directly */
  padding: 0 16px;
  height: 32px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  line-height: 32px;
  border: none; /* Override general button border */
}
.input-actions > .el-button.el-button--primary {
  background-color: #4f46e5;
  color: white;
}
.input-actions > .el-button.el-button--primary:hover {
  background-color: #4338ca;
}
.input-actions > .el-button.el-button--primary:disabled {
  background-color: #a5b4fc;
  color: #e0e7ff;
  cursor: not-allowed;
}
.input-actions > .el-button.el-button--success {
  background-color: #10b981;
  color: white;
}
.input-actions > .el-button.el-button--success:hover {
  background-color: #059669;
}
.input-actions > .el-button.el-button--success:disabled {
  background-color: #6ee7b7;
  color: #d1fae5;
  cursor: not-allowed;
}

/* Uploaded Files List */
.uploaded-files {
  margin-top: 10px;
  padding: 0;
  max-height: 120px;
  overflow-y: auto;
}

/* ... rest of the uploaded file item styles remain the same ... */
.uploaded-file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: #f0f2f5;
  border-radius: 6px;
  margin-bottom: 6px;
  transition: background-color 0.2s ease;
  border: 1px solid #e5e7eb;
  font-size: 13px;
}

.uploaded-file-item:hover {
  background-color: #e8ebf0;
}

.file-icon {
  font-size: 16px;
  color: #6b7280;
  flex-shrink: 0;
}

.file-name {
  flex: 1;
  color: #4f46e5;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 8px;
}

.file-name:hover {
  text-decoration: underline;
}

.file-size {
  font-size: 12px;
  color: #9ca3af;
  padding-left: 8px;
  flex-shrink: 0;
}

.file-status {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 5px;
  border-radius: 4px;
  margin-left: auto;
  flex-shrink: 0;
}

.file-status.uploading {
  color: #d97706;
  background-color: #fef3c7;
}
.file-status.parsing {
  color: #2563eb;
  background-color: #dbeafe;
}
.file-status.completed {
  color: #059669;
  background-color: #d1fae5;
}
.file-status.error {
  color: #dc2626;
  background-color: #fee2e2;
}

.uploaded-file-item .el-button--text {
  padding: 0;
  margin-left: 6px;
  color: #9ca3af;
  font-size: 16px;
  flex-shrink: 0;
  height: auto;
  line-height: 1;
}
.uploaded-file-item .el-button--text:hover {
  color: #ef4444;
  background-color: transparent !important;
}
.uploaded-file-item .el-button--text.is-disabled {
  color: #d1d5db;
  cursor: not-allowed;
}

/* Scrollbar Styles */
.uploaded-files::-webkit-scrollbar {
  width: 5px;
}
.uploaded-files::-webkit-scrollbar-track {
  background: transparent;
}
.uploaded-files::-webkit-scrollbar-thumb {
  background: #e0e6f0;
  border-radius: 3px;
}
.uploaded-files::-webkit-scrollbar-thumb:hover {
  background: #d1d5db;
}
</style> 
