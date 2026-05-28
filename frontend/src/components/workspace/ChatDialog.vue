<!-- 
  @file 聊天对话组件
  @description AI角色的聊天对话界面
-->
<template>
  <div class="chat-page">
    <!-- 对话头部 -->
    <div class="chat-header">
      <div class="header-left">
        <button class="back-btn" @click="handleClose">
          <span>←</span>
        </button>
        <div class="avatar">
          <img
            v-if="isImageUrl(role?.icon)"
            :src="role?.icon"
            :alt="role?.title"
            @error="handleImageError"
            loading="lazy"
          />
          <span v-else class="fallback-icon">{{
            getFallbackIcon(role?.title)
          }}</span>
        </div>
      </div>
      <div class="role-info">
        <div class="role-title">{{ role?.title }}</div>
        <div class="role-status">在线</div>
      </div>
    </div>

    <!-- 对话内容区 -->
    <div class="chat-content" ref="chatContentRef">
      <!-- 欢迎消息 -->
      <div
        v-if="
          props.openingStatement &&
          ((!showStrategyForm && !showProductValidationForm) ||
            strategyFormSubmitted ||
            productValidationFormSubmitted)
        "
        class="message assistant"
      >
        <div class="message-content">
          <div
            class="opening-statement"
            v-html="formatOpeningStatement(props.openingStatement)"
          ></div>
        </div>
      </div>

      <!-- 传播策略框架表单 - 仅在角色ID为9且没有消息时显示 -->
      <StrategyForm
        v-if="showStrategyForm"
        @submit="handleStrategyFormSubmit"
      />

      <!-- 产品定位验证表单 - 仅在角色ID为34且没有消息时显示 -->
      <ProductValidationForm
        v-if="showProductValidationForm"
        @submit="handleProductValidationFormSubmit"
      />

      <!-- ThinkPad 详情页生成表单 - 仅在角色ID为30且没有消息时显示 -->
      <div v-if="showThinkpadForm" class="thinkpad-form-container">
        <div class="thinkpad-form">
          <h2 class="form-title">ThinkPad 详情页生成 · 用户信息采集</h2>
          <p class="form-description">
            为了生成一份专业、精准的 ThinkPad
            产品详情页文案，请您按以下提示提供必要信息。所有信息提交完毕后，我将自动为您生成结构完整、风格统一、可直接上线使用的详情页内容。
          </p>

          <div class="form-section">
            <h3 class="section-title">① 基础产品信息</h3>
            <p class="section-description">
              请填写以下字段，便于识别产品核心配置：
            </p>
            <div class="form-item">
              <label>品牌名称<span class="required">*</span></label>
              <textarea
                v-model="thinkpadForm.basicInfo.brand"
                placeholder="如：ThinkPad / Lenovo / Yoga / Legion 等"
                rows="1"
                required
                @input="adjustFormTextareaHeight"
                ref="formTextareaRefs"
              ></textarea>
            </div>
            <div class="form-item">
              <label>产品系列<span class="required">*</span></label>
              <textarea
                v-model="thinkpadForm.basicInfo.series"
                placeholder="如：X1、X9、T14s、P1、E15等"
                rows="1"
                required
                @input="adjustFormTextareaHeight"
                ref="formTextareaRefs"
              ></textarea>
            </div>
            <div class="form-item">
              <label>产品定位<span class="required">*</span></label>
              <textarea
                v-model="thinkpadForm.basicInfo.positioning"
                placeholder="可简述，如：'高端AI旗舰'、'性价比轻薄本'、'重载创作工作站'等"
                rows="2"
                required
                @input="adjustFormTextareaHeight"
                ref="formTextareaRefs"
              ></textarea>
            </div>
          </div>

          <div class="form-section">
            <h3 class="section-title">② 目标用户与应用场景</h3>

            <div class="form-item">
              <label>目标人群类型<span class="required">*</span></label>
              <div class="radio-options">
                <div
                  v-for="(option, index) in targetUserOptions"
                  :key="index"
                  class="radio-option"
                >
                  <input
                    type="radio"
                    :id="`target-user-${index}`"
                    :value="option.value"
                    v-model="thinkpadForm.targetUser.type"
                    name="targetUserType"
                  />
                  <label :for="`target-user-${index}`">{{
                    option.label
                  }}</label>
                </div>
                <div class="radio-option custom-option">
                  <input
                    type="radio"
                    id="target-user-custom"
                    value="custom"
                    v-model="thinkpadForm.targetUser.type"
                    name="targetUserType"
                  />
                  <label for="target-user-custom">其他：</label>
                  <textarea
                    v-model="thinkpadForm.targetUser.customType"
                    placeholder="请描述"
                    rows="1"
                    :disabled="thinkpadForm.targetUser.type !== 'custom'"
                    @input="adjustFormTextareaHeight"
                    ref="formTextareaRefs"
                  ></textarea>
                </div>
              </div>
            </div>

            <div class="form-item">
              <label>使用场景示意<span class="required">*</span></label>
              <div class="checkbox-options">
                <div
                  v-for="(option, index) in usageScenarioOptions"
                  :key="index"
                  class="checkbox-option"
                >
                  <input
                    type="checkbox"
                    :id="`usage-scenario-${index}`"
                    :value="option.value"
                    v-model="thinkpadForm.targetUser.scenarios"
                  />
                  <label :for="`usage-scenario-${index}`">{{
                    option.label
                  }}</label>
                </div>
                <div class="checkbox-option custom-option">
                  <input
                    type="checkbox"
                    id="usage-scenario-custom"
                    value="custom"
                    v-model="thinkpadForm.targetUser.scenarios"
                  />
                  <label for="usage-scenario-custom">其他：</label>
                  <textarea
                    v-model="thinkpadForm.targetUser.customScenario"
                    placeholder="请描述"
                    rows="1"
                    :disabled="
                      !thinkpadForm.targetUser.scenarios.includes('custom')
                    "
                    @input="adjustFormTextareaHeight"
                    ref="formTextareaRefs"
                  ></textarea>
                </div>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3 class="section-title">③ 卖点内容上传</h3>
            <p class="section-description">
              请上传包含卖点信息的文档或图片（如 PPT、PDF、Word、脑图等形式）
            </p>
            <div class="form-item">
              <label
                >文件上传<span class="tip"
                  >文件内容建议包含具体配置、产品特色点、差异化优势等</span
                ></label
              >
              <div class="file-upload-container">
                <button
                  class="upload-btn thinkpad-upload-btn"
                  @click="handleThinkpadFileClick"
                >
                  <span class="upload-icon">📎</span>
                  <span class="upload-text">选择文件</span>
                </button>
                <input
                  type="file"
                  ref="thinkpadFileInput"
                  @change="handleThinkpadFileUpload"
                  style="display: none"
                  multiple
                />
              </div>

              <!-- 已上传文件列表 -->
              <div
                v-if="thinkpadForm.files.length"
                class="uploaded-files thinkpad-uploaded-files"
              >
                <div
                  v-for="file in thinkpadForm.files"
                  :key="file.id"
                  class="uploaded-file-item"
                >
                  <span class="file-icon">{{ getFileIcon(file.type) }}</span>
                  <span class="file-name">{{ file.name }}</span>
                  <span class="file-size">{{ formatFileSize(file.size) }}</span>
                  <span class="file-status" :class="file.status">
                    {{ getStatusText(file.status) }}
                  </span>
                  <button
                    class="remove-btn"
                    @click="handleRemoveThinkpadFile(file)"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3 class="section-title">④ 卖点优先级标注</h3>
            <p class="section-description">
              哪些卖点最重要？请简要排序（1为最高优先级）
            </p>
            <div class="form-item">
              <label>优先级排序<span class="required">*</span></label>
              <textarea
                v-model="thinkpadForm.sellingPoints"
                placeholder="例如：
1.轻薄便携
2.AI功能
3.屏幕素质
4.安全防护
5.扩展性"
                rows="6"
                required
                @input="adjustFormTextareaHeight"
                ref="formTextareaRefs"
              ></textarea>
            </div>
          </div>

          <div class="form-section">
            <h3 class="section-title">
              ⑤ 可选项：风格补充建议<span class="optional">(选填)</span>
            </h3>
            <div class="form-item">
              <label>希望营造的口吻/气质关键词</label>
              <textarea
                v-model="thinkpadForm.stylePreferences.tone"
                placeholder="如：专业感、科技感、高端商务、精英气场、创新先锋 等"
                rows="2"
                @input="adjustFormTextareaHeight"
                ref="formTextareaRefs"
              ></textarea>
            </div>
            <div class="form-item">
              <label>品牌口号/态度语</label>
              <textarea
                v-model="thinkpadForm.stylePreferences.slogan"
                placeholder="如：'快，从不等待''为创造，轻装而来''灵感自驱，行动不设限'等"
                rows="2"
                @input="adjustFormTextareaHeight"
                ref="formTextareaRefs"
              ></textarea>
            </div>
          </div>

          <div class="form-actions">
            <button
              class="submit-btn"
              @click="submitThinkpadForm"
              :disabled="!isThinkpadFormValid"
            >
              提交表单
            </button>
          </div>
        </div>
      </div>

      <!-- 消息列表 - 仅在非表单模式或表单已提交时显示 -->
      <div
        v-if="
          (!showStrategyForm &&
            !showThinkpadForm &&
            !showProductValidationForm) ||
          strategyFormSubmitted ||
          thinkpadFormSubmitted ||
          productValidationFormSubmitted
        "
        class="messages"
      >
        <div
          v-for="message in messages"
          :key="message.id"
          class="message"
          :class="[message.type, { edited: message.isEdited }]"
        >
          <!-- 新增 message-content-wrapper 包裹层 -->
          <div class="message-content-wrapper">
            <div class="message-content">
              <div
                v-if="
                  message.type === 'assistant' &&
                  message.inferring &&
                  !message.content
                "
                class="inferring"
              >
                <span class="inferring-dots">
                  <span class="dot"></span>
                  <span class="dot"></span>
                  <span class="dot"></span>
                </span>
                正在推理中...
              </div>
              <div
                v-else-if="
                  message.type === 'assistant' && message.api_status === 'error'
                "
                class="error-message"
              >
                当前系统繁忙，请稍后再试
              </div>
              <div
                v-if="message.content"
                class="message-text"
                v-html="
                  message.type === 'assistant'
                    ? formatMessageContent(message.content)
                    : message.content
                "
              ></div>

              <!-- 文件列表 -->
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
                  <span class="file-size">{{ formatFileSize(file.size) }}</span>
                </div>
              </div>
              <!-- 添加视频任务面板组件 -->

              <!-- ... 其他消息内容 ... -->
              <div>
                <!-- 视频任务面板 -->
                <div
                  v-if="props?.role?.id === 3 && message.type === 'assistant'"
                  class="video-tasks-section"
                >
                  <VideoTaskPanel
                    :role-id="props.role.id"
                    :tasks="message.videoTasks || []"
                    :message-id="message.message_id"
                    :message-content="message.content"
                    :inferring="message.inferring"
                    @update:tasks="
                      updateMessageTasks(message.message_id, $event)
                    "
                  />
                </div>

                <!-- 文生图面板 -->
                <div
                  v-if="props?.role?.id === 28 && message.type === 'assistant'"
                  class="image-generation-section"
                >
                  <MJTaskPanel
                    :role-id="props.role.id"
                    :tasks="message.mjTasks || []"
                    :message-id="message.message_id"
                    :message-content="message.content"
                    :inferring="message.inferring"
                    @update:tasks="
                      updateMessageTasks(message.message_id, $event)
                    "
                  />
                </div>
              </div>
            </div>
            <!-- 添加消息操作区域 -->
            <div class="message-actions">
              <template v-if="message.type === 'user'">
                <el-button
                  class="edit-btn"
                  type="text"
                  size="small"
                  @click="startEditing(message)"
                  :disabled="
                    !!editingMessageId && editingMessageId !== message.id
                  "
                >
                  <el-icon><EditPen /></el-icon>
                  编辑
                </el-button>
                <el-button
                  class="copy-btn"
                  type="text"
                  size="small"
                  @click="copyText(message.content)"
                >
                  <el-icon><DocumentCopy /></el-icon>
                  复制
                </el-button>
              </template>
              <el-button
                v-if="message.type === 'assistant'"
                class="copy-btn"
                type="text"
                size="small"
                @click="copyText(message.content)"
              >
                <el-icon><DocumentCopy /></el-icon>
                复制
              </el-button>
              <!-- 添加 HTML 预览组件 -->
              <HtmlPreview
                v-if="
                  message.type === 'assistant' &&
                  (props?.role?.id === 27 || props?.role?.id === 25)
                "
                :message-id="message.message_id"
                :session-id="0"
                :html="
                  message.html || {
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
                    message.html = html;
                  }
                "
              />
              <el-button
                v-if="props?.role?.id === 28 && message.type === 'assistant'"
                class="eqmj-btn"
                type="text"
                size="small"
                @click="openEQMJ"
              >
                <el-icon><Document /></el-icon>
                跳转EQMJ
              </el-button>

              <!-- Version Navigation -->
              <div
                v-if="
                  message.next_branches &&
                  message.next_branches.branches?.length > 1
                "
                class="version-nav"
              >
                <button
                  class="version-button prev"
                  :disabled="
                    message.next_branches.branches.findIndex(
                      (b) =>
                        b.branch_id === (message.branch_id || activeBranchId)
                    ) === 0
                  "
                  @click="switchToAdjacentBranch(message, -1)"
                  title="Previous Version"
                >
                  <el-icon><ArrowLeft /></el-icon>
                </button>
                <span class="version-counter">
                  {{
                    message.next_branches.branches.findIndex(
                      (b) =>
                        b.branch_id === (message.branch_id || activeBranchId)
                    ) + 1
                  }}
                  / {{ message.next_branches.branches.length }}
                </span>
                <button
                  class="version-button next"
                  :disabled="
                    message.next_branches.branches.findIndex(
                      (b) =>
                        b.branch_id === (message.branch_id || activeBranchId)
                    ) ===
                    message.next_branches.branches.length - 1
                  "
                  @click="switchToAdjacentBranch(message, 1)"
                  title="Next Version"
                >
                  <el-icon><ArrowRight /></el-icon>
                </button>
              </div>
            </div>
          </div>
        </div>
        <!-- 添加 HTML 预览组件 -->
        <HtmlPreview
          v-if="
            messages.length > 1 &&
            (props?.role?.id === 32 || props?.role?.id === 34 || props?.role?.id === 39)
          "
          :session-id="currentSessionId"
          :html="
            messageHtmlMap[currentSessionId] || {
              html_code: '',
              status: '',
              id: 0,
              type: 'session',
              session_id: currentSessionId,
              message_id: 0,
              prompt: '',
            }
          "
          :messages="messages.filter((msg) => msg.type === 'assistant')"
          :model="selectedModel"
          :inferring="messages[messages.length - 1].inferring"
          @update:html="
            (html) => {
              messageHtmlMap[currentSessionId] = html;
            }
          "
        />
      </div>
    </div>

    <!-- 输入区域 - 仅在非表单模式或表单已提交时显示 -->
    <ChatInputArea
      v-if="
        (!showStrategyForm &&
          !showThinkpadForm &&
          !showProductValidationForm) ||
        strategyFormSubmitted ||
        thinkpadFormSubmitted ||
        productValidationFormSubmitted
      "
      v-model:messageInput="inputMessage"
      :uploadedFiles="uploadedFiles"
      @update:uploadedFiles="(files) => {
        console.log('🔥 父组件收到文件更新事件:', files);
        uploadedFiles = files;
      }"
      :sending="sending"
      :editing-message-id="editingMessageId"
      :role-id="props.role?.id"
      :active-branch-id="activeBranchId"
      :base-url="config.baseURL"
      :auth-token="getToken()"
      :selectedModel="selectedModel"
      @update:selectedModel="(val) => (selectedModel = val)"
      @send="handleSend"
      @cancel-editing="cancelEditing"
    />
  </div>
</template>



<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 85vh; /* 使用全屏高度 */
  background: #fff;
  position: relative;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
  background: #fff;
  z-index: 10;
  flex-shrink: 0; /* 防止头部压缩 */
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  padding: 8px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 20px;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.3s;
}

.back-btn:hover {
  background: #f5f7f9;
  color: #4e6ef2;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7f9;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.role-info {
  margin-left: 12px;
}

.role-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.role-status {
  font-size: 12px;
  color: #4caf50;
  margin-top: 2px;
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #f5f7f9;
  position: relative;
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
}

/* 自定义滚动条样式 */
.chat-content::-webkit-scrollbar {
  width: 6px; /* 更细的滚动条 */
}

.chat-content::-webkit-scrollbar-track {
  background: transparent;
}

.chat-content::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.3);
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.message.assistant {
  align-items: flex-start;
}

.message.user {
  align-items: flex-end;
}

.message.assistant .message-content {
  align-self: flex-start;
  background: #fff;
  border-radius: 0 12px 12px 12px;
}

.message.user .message-content {
  align-self: flex-end;
  background: #4e6ef2;
  color: #fff;
  border-radius: 12px 0 12px 12px;
  max-width: 100%;
}

.message-content-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
}

.message-content {
  padding: 12px 16px;
  line-height: 1.6;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  word-break: break-word;
}

.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.message:hover .message-actions {
  opacity: 1;
}

.el-button {
  display: flex;
  align-items: center;
  gap: 4px;
}

.el-button :deep(.el-icon) {
  margin-right: 4px;
}

/* 保持其他样式不变 */
/* 统一按钮样式 */
.action-btn {
  display: none;
}

/* 添加新的按钮样式 */
.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.message:hover .message-actions {
  opacity: 1;
}

.el-button {
  display: flex;
  align-items: center;
  gap: 4px;
}

.el-button :deep(.el-icon) {
  margin-right: 4px;
}

/* 编辑按钮样式 */
.edit-btn.active {
  color: #fa8c16;
  background-color: #fff7e6;
  border-color: #ffe7ba;
}

/* 复制按钮样式 */
.copy-btn:hover {
  color: #409eff;
  background-color: #ecf5ff;
  border-color: #c6e2ff;
}

/* 编辑状态下的消息样式优化 */
.message.edited .message-content {
  padding-left: 13px; /* 补偿边框宽度 */
}

.message.edited::after {
  content: "(已编辑)";
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  align-self: flex-end;
  margin-right: 8px;
}

/* 编辑状态指示器优化 */
.editing-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background-color: #fff7e6;
  border: 1px solid #ffe7ba;
  border-radius: 6px;
  margin-bottom: 12px;
  box-shadow: 0 2px 6px rgba(250, 140, 22, 0.1);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 2px 6px rgba(250, 140, 22, 0.1);
  }
  50% {
    box-shadow: 0 2px 10px rgba(250, 140, 22, 0.3);
  }
  100% {
    box-shadow: 0 2px 6px rgba(250, 140, 22, 0.1);
  }
}

/* 取消编辑按钮优化 */
.cancel-edit-btn {
  padding: 4px 12px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  color: #606266;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 12px;
  height: 28px;
  display: flex;
  align-items: center;
}

.cancel-edit-btn:hover {
  color: #f56c6c;
  border-color: #fbc4c4;
  background-color: #fef0f0;
}

.opening-statement {
  white-space: pre-wrap;
  word-wrap: break-word;
  max-width: 100%; /* 限制最大宽度 */
  overflow-x: hidden; /* 防止水平滚动 */
}

.opening-statement :deep(p) {
  margin: 0;
  padding: 4px 0;
  line-height: 1.8;
  font-size: 15px;
  overflow-wrap: break-word; /* 确保长文本会换行 */
}

.example {
  padding: 12px;
  background: #f5f7f9;
  border-radius: 8px;
  margin: 8px 0;
  font-style: italic;
}

.highlight {
  color: #4e6ef2;
  font-weight: 500;
}

.hint {
  color: #666;
  font-style: italic;
}

/* 添加文件相关样式 */
.message-files {
  margin-top: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 8px;
  background: white;
  border-radius: 6px;
  margin-bottom: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.file-item:hover {
  background: #f0f2f5;
}

.file-icon {
  margin-right: 8px;
  font-size: 16px;
}

.file-name {
  flex: 1;
  color: #4e6ef2;
  font-size: 14px;
  margin-right: 8px;
}

.file-size {
  color: #999;
  font-size: 12px;
  margin-right: 8px;
}

.download-icon {
  color: #4e6ef2;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  background: #f0f2f5;
  cursor: pointer;
}

.download-icon:hover {
  background: #e6e8eb;
}

.uploaded-files {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.uploaded-file-item {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  background: #f5f7f9;
  border-radius: 6px;
  gap: 8px;
}

.message-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

/* Add new styles for markdown and JSON content */
:deep(.message-text) {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}

:deep(.message-text pre) {
  background: #f6f8fa;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
  margin: 8px 0;
}

:deep(.message-text code) {
  background: #f6f8fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier,
    monospace;
  font-size: 0.9em;
}

:deep(.message-text table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
}

:deep(.message-text th),
:deep(.message-text td) {
  border: 1px solid #dfe2e5;
  padding: 8px;
  text-align: left;
}

:deep(.message-text th) {
  background: #f6f8fa;
}

:deep(.message-text blockquote) {
  margin: 8px 0;
  padding: 0 16px;
  color: #6a737d;
  border-left: 4px solid #dfe2e5;
}

:deep(.message-text img) {
  max-width: 100%;
  height: auto;
}

:deep(.message-text h1),
:deep(.message-text h2),
:deep(.message-text h3),
:deep(.message-text h4),
:deep(.message-text h5),
:deep(.message-text h6) {
  margin: 16px 0 8px;
  line-height: 1.25;
}

:deep(.message-text ul),
:deep(.message-text ol) {
  padding-left: 24px;
}

:deep(.message-text li) {
  margin: 4px 0;
}

:deep(.json-content) {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier,
    monospace;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding: 0 4px;
}

.clear-failed-btn {
  padding: 4px 8px;
  font-size: 12px;
  color: #f56c6c;
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.clear-failed-btn:hover {
  background: #fde2e2;
  border-color: #f89898;
}

.input-tips {
  position: absolute;
  top: -20px;
  right: 10px;
  font-size: 12px;
  color: #909399;
}

.input-box {
  position: relative;
  margin: 0 auto;
  /* 保持原有样式 */
}

/* 添加推理中的样式 */
.inferring {
  color: #909399;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
}

.inferring-dots {
  display: flex;
  gap: 4px;
}

.inferring-dots .dot {
  width: 6px;
  height: 6px;
  background-color: #909399;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.inferring-dots .dot:nth-child(1) {
  animation-delay: 0s;
}
.inferring-dots .dot:nth-child(2) {
  animation-delay: 0.2s;
}
.inferring-dots .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.style-toggle {
  position: relative;
  margin-bottom: 12px;
}

.style-select-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s;
  height: 36px;
  min-width: 120px; /* 统一最小宽度 */
}

.style-select-btn:hover {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
  background: #f5f7f9;
}

.style-icon {
  font-size: 16px;
}

.style-text {
  font-size: 14px;
  color: #606266;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
}

.style-count {
  background: var(--el-color-primary);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  min-width: 20px;
  text-align: center;
}

.style-selector {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  margin: 0 16px 12px;
}

.style-options {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  padding: 12px;
}

.style-option {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid #eee;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.3s;
}

.style-option:hover {
  background: #fff;
  border-color: var(--el-color-primary-light-5);
  transform: translateY(-1px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.style-option.active {
  background: #fff;
  border-color: var(--el-color-primary);
}

.style-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.style-icon {
  font-size: 16px;
  margin-bottom: 4px;
}

.style-title {
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

.style-desc {
  font-size: 11px;
  color: #666;
  line-height: 1.4;
}

.remove-btn {
  width: 16px;
  height: 16px;
  border: none;
  background: none;
  color: #999;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
}

.remove-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #666;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.error-message {
  color: #f56c6c;
  font-size: 14px;
  padding: 8px 12px;
  background-color: rgba(245, 108, 108, 0.1);
  border-radius: 8px;
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  width: fit-content;
}

.error-message::before {
  content: "⚠️";
  margin-right: 8px;
  font-size: 16px;
}

/* 更新传播策略框架表单样式，与 ThinkPad 表单保持一致 */
.strategy-form-container {
  width: 100%;
  max-width: 100%;
  margin: 0 auto 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
  animation: fadeIn 0.4s ease-out;
}

.strategy-form {
  padding: 36px;
}

.strategy-form .form-title {
  font-size: 22px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  text-align: center;
  line-height: 1.2;
  position: relative;
  padding-bottom: 12px;
}

.strategy-form .form-title:after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background: #e60012;
  border-radius: 2px;
}

.strategy-form .form-description {
  font-size: 14px;
  color: #666;
  margin-top: 20px;
  margin-bottom: 36px;
  line-height: 1.7;
  text-align: center;
}

.strategy-form .form-section {
  margin-bottom: 40px;
  padding-bottom: 32px;
  border-bottom: 1px solid #f0f0f0;
  position: relative;
}

.strategy-form .form-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.strategy-form .form-section:after {
  content: "";
  position: absolute;
  bottom: -1px;
  left: 0;
  height: 1px;
  width: 40px;
  background: #e60012;
  opacity: 0.2;
}

.strategy-form .form-section:last-child:after {
  display: none;
}

.strategy-form .section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  line-height: 1.3;
}

.strategy-form .form-item {
  margin-bottom: 24px;
}

.strategy-form .form-item:last-child {
  margin-bottom: 0;
}

.strategy-form .form-item label {
  margin-bottom: 12px;
  display: block;
}

.strategy-form .required {
  color: #e60012;
  margin-left: 4px;
  font-weight: bold;
}

.strategy-form textarea {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  transition: all 0.25s ease;
  background: #fafafa;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02);
  min-height: 46px;
}

.strategy-form textarea:focus {
  background: #fff;
  border-color: #4e6ef2;
  box-shadow: 0 0 0 3px rgba(78, 110, 242, 0.1),
    inset 0 1px 2px rgba(0, 0, 0, 0);
  outline: none;
}

.strategy-form textarea:hover:not(:focus) {
  border-color: #c0c4cc;
}

.strategy-form .form-actions {
  margin-top: 48px;
  display: flex;
  justify-content: center;
}

.strategy-form .submit-btn {
  min-width: 160px;
  height: 46px;
  padding: 0 28px;
  background: #e60012;
  color: #fff;
  font-size: 16px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(230, 0, 18, 0.2);
  position: relative;
  overflow: hidden;
}

.strategy-form .submit-btn:before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0.1),
    rgba(255, 255, 255, 0.2)
  );
  transform: translateX(-100%);
  transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

.strategy-form .submit-btn:hover {
  background: #d40010;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(230, 0, 18, 0.3);
}

.strategy-form .submit-btn:hover:before {
  transform: translateX(100%);
}

.strategy-form .submit-btn:disabled {
  background: #ffb3b3;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.strategy-form .submit-btn:disabled:before {
  display: none;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .strategy-form {
    padding: 20px;
  }
}

/* 添加必填标识样式 */
.required {
  color: #f56c6c;
  margin-left: 4px;
}

/* 修改单行文本框样式，使其更大 */
.form-item textarea[rows="1"] {
  min-height: 50px; /* 增加最小高度 */
  max-height: 100px; /* 增加最大高度 */
  padding: 12px 16px; /* 增加内边距 */
  line-height: 26px; /* 增加行高 */
  font-size: 15px; /* 增加字体大小 */
  resize: none;
  overflow-y: hidden;
}

/* 为产品名称和定价区间添加特殊样式 */
.form-section:nth-child(2) .form-item:first-child textarea,
.form-section:nth-child(2) .form-item:last-child textarea {
  font-weight: 500; /* 加粗字体 */
  color: #333; /* 更深的文字颜色 */
}

.editing-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: #fff7e6;
  border: 1px solid #ffe7ba;
  border-radius: 8px;
  margin-bottom: 12px;
}

.editing-text {
  color: #d48806;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.editing-actions {
  display: flex;
  gap: 8px;
}

.cancel-edit-btn {
  padding: 4px 12px;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  color: #595959;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-edit-btn:hover {
  color: #ff4d4f;
  border-color: #ff4d4f;
}

.action-btn {
  background: none;
  border: none;
  padding: 4px 8px;
  font-size: 13px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
  color: #8c8c8c;
  transition: all 0.3s;
}

.edit-btn:hover {
  color: #fa8c16;
  background: rgba(250, 140, 22, 0.1);
}

.copy-btn:hover {
  color: #1890ff;
  background: rgba(24, 144, 255, 0.1);
}

.message.edited .message-content {
  border-left: 3px solid #fa8c16;
  padding-left: 13px; /* 补偿边框宽度 */
}

.message.edited::after {
  content: "(已编辑)";
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
  align-self: flex-end;
}

.send-btn.edit-mode {
  background: #fa8c16;
}

.send-btn.edit-mode:hover {
  background: #d46b08;
}

/* 确保消息操作区域在消息内容下方 */
.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  justify-content: flex-end; /* 右对齐按钮 */
  opacity: 1;
  transition: opacity 0.2s ease;
}

/* 用户消息和AI消息的操作区域可能需要不同的对齐方式 */
.message.user .message-actions {
  justify-content: flex-end; /* 用户消息右对齐 */
}

.message.assistant .message-actions {
  justify-content: flex-start; /* AI消息左对齐 */
}

.action-btn .icon {
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 编辑状态指示器 */
.editing-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background-color: #fff7e6;
  border: 1px solid #ffe7ba;
  border-radius: 6px;
  margin-bottom: 12px;
  box-shadow: 0 2px 6px rgba(250, 140, 22, 0.1);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 2px 6px rgba(250, 140, 22, 0.1);
  }
  50% {
    box-shadow: 0 2px 10px rgba(250, 140, 22, 0.3);
  }
  100% {
    box-shadow: 0 2px 6px rgba(250, 140, 22, 0.1);
  }
}

.editing-text {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #d48806;
  font-weight: 500;
}

.cancel-edit-btn {
  height: 28px;
  padding: 0 12px;
  border-radius: 4px;
  background: white;
  border: 1px solid #dcdfe6;
  color: #606266;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 12px;
  display: flex;
  align-items: center;
}

.cancel-edit-btn:hover {
  color: #f56c6c;
  border-color: #fbc4c4;
  background-color: #fef0f0;
}

/* 添加高亮动画样式 */
@keyframes highlight {
  0% {
    background-color: rgba(250, 140, 22, 0.1);
  }
  100% {
    background-color: transparent;
  }
}

.highlight-new {
  animation: highlight 2s ease-out;
}

.edit-btn.active {
  color: #fa8c16;
  background-color: #fff7e6;
  border-color: #ffe7ba;
}

/* ThinkPad 表单样式 */
.thinkpad-form-container {
  width: 100%;
  max-width: 100%;
  margin: 0 auto 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.thinkpad-form {
  padding: 36px;
}

/* 优化表单标题 */
.thinkpad-form .form-title {
  font-size: 22px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  text-align: center;
  line-height: 1.2;
  position: relative;
  padding-bottom: 12px;
}

.thinkpad-form .form-title:after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background: #e60012;
  border-radius: 2px;
}

/* 改进表单章节样式 */
.thinkpad-form .form-section {
  margin-bottom: 40px;
  padding-bottom: 32px;
  border-bottom: 1px solid #f0f0f0;
  position: relative;
}

.thinkpad-form .form-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.thinkpad-form .form-section:after {
  content: "";
  position: absolute;
  bottom: -1px;
  left: 0;
  height: 1px;
  width: 40px;
  background: #e60012;
  opacity: 0.2;
}

.thinkpad-form .form-section:last-child:after {
  display: none;
}

/* 改进表单章节标题 */
.thinkpad-form .section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  line-height: 1.3;
}

/* 样式优化单选框和复选框 */
.radio-options,
.checkbox-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
  padding: 6px 2px;
}

.radio-option,
.checkbox-option {
  display: flex;
  align-items: center;
  padding: 14px 18px;
  background: #fafafa;
  border-radius: 8px;
  transition: all 0.2s ease;
  border: 1px solid #f0f0f0;
}

.radio-option:hover,
.checkbox-option:hover {
  background: #f5f7f9;
  border-color: #e1e4e8;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.radio-option input[type="radio"],
.checkbox-option input[type="checkbox"] {
  width: 20px;
  height: 20px;
  margin-right: 12px;
  cursor: pointer;
  accent-color: #e60012;
}

/* 自定义选项样式 */
.custom-option {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  background: #f5f7f9;
  border-color: #e5e7eb;
}

.custom-option textarea {
  margin-left: 8px;
  flex: 1;
  min-width: 250px;
  min-height: 36px;
  padding: 8px 12px;
  font-size: 14px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: #fff;
  transition: all 0.25s ease;
}

.custom-option textarea:focus {
  border-color: #4e6ef2;
  box-shadow: 0 0 0 3px rgba(78, 110, 242, 0.1);
}

/* 优化文本输入区域 */
.thinkpad-form textarea {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  transition: all 0.25s ease;
  background: #fafafa;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.02);
  min-height: 46px;
}

.thinkpad-form textarea:focus {
  background: #fff;
  border-color: #4e6ef2;
  box-shadow: 0 0 0 3px rgba(78, 110, 242, 0.1),
    inset 0 1px 2px rgba(0, 0, 0, 0);
  outline: none;
}

/* 优化文件上传按钮 */
.thinkpad-upload-btn {
  padding: 14px 20px;
  background: #f9f9f9;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 10px;
  width: fit-content;
}

.thinkpad-upload-btn:hover {
  background: #f0f7ff;
  border-color: #4e6ef2;
  color: #4e6ef2;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(78, 110, 242, 0.1);
}

.thinkpad-upload-btn .upload-icon {
  font-size: 20px;
}

.thinkpad-upload-btn .upload-text {
  font-weight: 500;
}

/* 优化已上传文件列表 */
.thinkpad-uploaded-files {
  margin-top: 14px;
  background: #fafafa;
  border-radius: 8px;
  padding: 10px;
  border: 1px solid #eee;
}

.thinkpad-form .uploaded-file-item {
  padding: 12px 16px;
  margin-bottom: 8px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #eaeaea;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s;
}

.thinkpad-form .uploaded-file-item:hover {
  background: #fcfcfc;
  border-color: #d9d9d9;
}

.thinkpad-form .uploaded-file-item .file-icon {
  font-size: 18px;
  margin-right: 8px;
}

.thinkpad-form .uploaded-file-item .file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 8px;
}

.thinkpad-form .uploaded-file-item .remove-btn {
  opacity: 0.7;
  transition: all 0.2s;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #f5f5f5;
  cursor: pointer;
  font-size: 14px;
}

.thinkpad-form .uploaded-file-item .remove-btn:hover {
  opacity: 1;
  background: #ffebeb;
  color: #e60012;
}

/* 优化提交按钮 */
.thinkpad-form .form-actions {
  margin-top: 48px;
  display: flex;
  justify-content: center;
}

.thinkpad-form .submit-btn {
  min-width: 160px;
  height: 46px;
  padding: 0 28px;
  background: #e60012;
  color: #fff;
  font-size: 16px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(230, 0, 18, 0.2);
  position: relative;
  overflow: hidden;
}

.thinkpad-form .submit-btn:before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0.1),
    rgba(255, 255, 255, 0.2)
  );
  transform: translateX(-100%);
  transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

.thinkpad-form .submit-btn:hover {
  background: #d40010;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(230, 0, 18, 0.3);
}

.thinkpad-form .submit-btn:hover:before {
  transform: translateX(100%);
}

.thinkpad-form .submit-btn:disabled {
  background: #ffb3b3;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.thinkpad-form .submit-btn:disabled:before {
  display: none;
}

/* 优化必填标记和提示 */
.thinkpad-form .required {
  color: #e60012;
  margin-left: 4px;
  font-weight: bold;
}

.thinkpad-form .optional {
  color: #909399;
  font-size: 13px;
  font-weight: normal;
  margin-left: 6px;
  opacity: 0.8;
}

.thinkpad-form .tip {
  font-size: 13px;
  color: #666;
  font-style: italic;
  margin-left: 4px;
  font-weight: normal;
  opacity: 0.9;
}

/* 添加选中状态样式 */
.radio-option.selected,
.checkbox-option.selected {
  background-color: #fff7f7;
  border-color: #ffd0d0;
}

/* 动画效果 */
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

.thinkpad-form-container {
  animation: fadeIn 0.4s ease-out;
}

/* 调整 ThinkPad 表单描述文本样式 */
.thinkpad-form .form-description {
  font-size: 14px;
  color: #666;
  margin-top: 20px;
  margin-bottom: 36px;
  line-height: 1.7;
  text-align: center;
}

/* 进一步优化表单输入框样式 */
.thinkpad-form textarea,
.strategy-form textarea {
  width: 100%;
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.6;
  transition: all 0.25s ease;
  background: #ffffff;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
  min-height: 50px;
  color: #333;
}

.thinkpad-form textarea:focus,
.strategy-form textarea:focus {
  background: #fff;
  border-color: #4e6ef2;
  box-shadow: 0 0 0 3px rgba(78, 110, 242, 0.15),
    inset 0 1px 2px rgba(0, 0, 0, 0);
  outline: none;
}

.thinkpad-form textarea:hover:not(:focus),
.strategy-form textarea:hover:not(:focus) {
  border-color: #b0b7c3;
  background: #fafbfc;
}

/* 优化表单项标签样式 */
.thinkpad-form .form-item label,
.strategy-form .form-item label {
  display: block;
  font-size: 15px;
  color: #333;
  margin-bottom: 12px;
  font-weight: 500;
  position: relative;
}

/* 优化必填标记 */
.thinkpad-form .required,
.strategy-form .required {
  color: #e60012;
  margin-left: 4px;
  font-weight: bold;
  font-size: 16px;
}

/* 优化表单项容器 */
.thinkpad-form .form-item,
.strategy-form .form-item {
  margin-bottom: 28px;
  position: relative;
}

/* 优化单选和复选框容器 */
.radio-options,
.checkbox-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
  padding: 8px 2px;
}

/* 优化单选和复选框选项 */
.radio-option,
.checkbox-option {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: #ffffff;
  border-radius: 10px;
  transition: all 0.2s ease;
  border: 1px solid #e8e8e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.radio-option:hover,
.checkbox-option:hover {
  background: #f9fafc;
  border-color: #d0d7de;
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.05);
}

/* 增强选中状态样式 */
.radio-option.selected,
.checkbox-option.selected {
  background-color: #fff7f7;
  border-color: #ffcaca;
  box-shadow: 0 2px 6px rgba(230, 0, 18, 0.08);
}

/* 优化自定义选项样式 */
.custom-option {
  background: #f9fafc;
  border-color: #e5e7eb;
}

.custom-option textarea {
  margin-left: 10px;
  flex: 1;
  min-width: 250px;
  min-height: 40px;
  padding: 10px 14px;
  font-size: 14px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: #fff;
  transition: all 0.25s ease;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.03);
}

/* 优化表单章节标题 */
.thinkpad-form .section-title,
.strategy-form .section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 22px;
  display: flex;
  align-items: center;
  line-height: 1.3;
  color: #222;
  position: relative;
  padding-bottom: 10px;
}

.thinkpad-form .section-title:after,
.strategy-form .section-title:after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 2px;
  background: rgba(230, 0, 18, 0.6);
  border-radius: 1px;
}

/* 优化表单描述文本 */
.thinkpad-form .section-description,
.strategy-form .section-description {
  font-size: 14px;
  color: #666;
  margin-bottom: 24px;
  line-height: 1.6;
  background: #f9f9f9;
  padding: 12px 16px;
  border-radius: 8px;
  border-left: 3px solid #e0e0e0;
}

/* 优化文件上传按钮 */
.thinkpad-upload-btn {
  padding: 16px 22px;
  background: #f5f7fa;
  border: 1px dashed #c0c6d0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 12px;
  width: fit-content;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.thinkpad-upload-btn:hover {
  background: #eef4ff;
  border-color: #4e6ef2;
  color: #4e6ef2;
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(78, 110, 242, 0.12);
}

.thinkpad-upload-btn .upload-icon {
  font-size: 22px;
}

.thinkpad-upload-btn .upload-text {
  font-weight: 500;
  font-size: 15px;
}

/* 优化已上传文件列表 */
.thinkpad-uploaded-files {
  margin-top: 18px;
  background: #f9fafc;
  border-radius: 10px;
  padding: 12px;
  border: 1px solid #e8e8e8;
}

.thinkpad-form .uploaded-file-item {
  padding: 14px 18px;
  margin-bottom: 10px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #eaeaea;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

/* 增加表单容器的阴影和边框效果 */
.thinkpad-form-container,
.strategy-form-container {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
  border: 1px solid #e0e0e0;
}

/* 优化表单内部间距 */
.thinkpad-form,
.strategy-form {
  padding: 40px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .thinkpad-form,
  .strategy-form {
    padding: 24px;
  }

  .thinkpad-form textarea,
  .strategy-form textarea {
    padding: 14px;
    font-size: 14px;
  }
}

/* Add version navigation styles */
.version-nav {
  display: flex;
  align-items: center;
  background-color: #f0f2f5; /* Light background */
  border-radius: 4px;
  padding: 2px 4px;
  margin-left: auto; /* Push it to the right */
}

.version-counter {
  font-size: 12px;
  color: #595959; /* Darker gray */
  padding: 0 6px;
  font-weight: 500;
  min-width: 30px; /* Ensure space */
  text-align: center;
}

.version-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #595959;
  border-radius: 4px;
  transition: background-color 0.2s, color 0.2s;
}

.version-button:hover:not(:disabled) {
  background-color: #e6e8eb; /* Slightly darker hover */
  color: #262626;
}

.version-button:disabled {
  color: #bfbfbf; /* Lighter gray for disabled */
  cursor: not-allowed;
}

.version-button .el-icon {
  font-size: 14px;
}

/* Adjust message actions alignment if necessary */
.message-actions {
  /* Ensure enough space for version nav */
  justify-content: flex-end; /* Keep actions to the right */
}

/* 响应式调整 */
@media (max-width: 768px) {
  .thinkpad-form,
  .strategy-form {
    padding: 24px;
  }

  .thinkpad-form textarea,
  .strategy-form textarea {
    padding: 14px;
    font-size: 14px;
  }
}

.chat-dialog-content {
  display: flex;
  flex-direction: column;
  height: 70vh; /* 或根据需要设置 */
  max-height: 800px;
  background-color: #f7f8fa; /* 匹配 ChatDetail 背景色 */
  border-radius: 12px;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  background: #fff; /* 匹配 ChatDetail Header 背景色 */
  border-bottom: 1px solid #ebeef5;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); /* 匹配 ChatDetail Header 阴影 */
}

.role-info {
  display: flex;
  align-items: center;
  gap: 12px; /* 调整间距 */
}

.role-avatar {
  position: relative;
  width: 40px; /* 匹配 ChatDetail 头像大小 */
  height: 40px;
  border-radius: 12px; /* 匹配 ChatDetail 头像圆角 */
  overflow: hidden;
  background: linear-gradient(
    135deg,
    #10b981,
    #059669
  ); /* 匹配 Assistant 头像背景 */
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 16px;
}

.role-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.fallback-icon {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #10b981, #059669); /* 确保背景一致 */
  color: white;
  font-weight: 600;
  font-size: 16px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.show-fallback .fallback-icon {
  opacity: 1;
}

.role-details h3 {
  margin: 0 0 4px 0;
  font-size: 16px; /* 调整字体大小 */
  font-weight: 600; /* 匹配 ChatDetail 标题粗细 */
  color: #1a1a1a; /* 匹配 ChatDetail 标题颜色 */
}

.role-details p {
  margin: 0;
  font-size: 13px; /* 调整字体大小 */
  color: #6b7280; /* 匹配 ChatDetail 描述颜色 */
}

.chat-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.main-chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 防止内容溢出 */
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px; /* 匹配 ChatDetail 消息区域 padding */
  scroll-behavior: smooth;
}

/* --- Message Item Styles (Copied & Adapted from ChatDetail) --- */
.message {
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

.message.user {
  flex-direction: row-reverse;
}

.message-header {
  /* display: flex; */ /* 移除 flex，让头像和信息垂直排列 */
  align-items: center; /* 保持头像和信息水平居中 */
  gap: 12px;
  margin-bottom: 8px;
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
}

.avatar .fallback-icon-msg {
  /* 重用 .fallback-icon 的样式，或创建新的 */
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 16px;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.avatar.show-fallback .fallback-icon-msg {
  opacity: 1;
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
  /* 移除 flex 相关样式，让 sender 和 time 堆叠 */
  text-align: left; /* 助手消息信息左对齐 */
}

.user .message-info {
  text-align: right; /* 用户消息信息右对齐 */
}

.message-sender {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 2px;
}

.message-time {
  font-size: 12px;
  color: #9ca3af;
  /* margin-top: 4px; */ /* 调整间距 */
}

.message-content-wrapper {
  max-width: 75%; /* 稍微增加最大宽度 */
  min-width: 150px; /* 调整最小宽度 */
  display: flex; /* 使用 flex 布局 */
  flex-direction: column; /* 垂直排列内容和操作 */
}

.message-content {
  padding: 14px 18px; /* 调整内边距 */
  border-radius: 16px;
  font-size: 15px;
  line-height: 1.65; /* 增加行高 */
  position: relative;
  transition: all 0.2s ease;
  word-wrap: break-word; /* 允许长单词换行 */
  overflow-wrap: break-word; /* 确保兼容性 */
  white-space: pre-wrap; /* 保留换行符和空格 */
}

.user .message-content {
  background: #4f46e5;
  color: white;
  border-top-right-radius: 4px;
}

.assistant .message-content {
  background: white;
  color: #1a1a1a;
  border-top-left-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06); /* 调整阴影 */
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

.user .message-content :deep(pre) {
  background: rgba(255, 255, 255, 0.1);
}

/* 优化列表样式 */
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

.message-actions {
  display: flex;
  gap: 6px; /* 调整按钮间距 */
  margin-top: 10px; /* 调整与内容的间距 */
  opacity: 1;
  transition: opacity 0.2s ease;
  align-items: center;
  justify-content: flex-end; /* 按钮默认右对齐 */
}

.user .message-actions {
  /* 用户消息的操作按钮在左侧，如果需要的话 */
  /* justify-content: flex-start; */
}

.message-actions .el-button {
  padding: 5px 10px; /* 调整按钮内边距 */
  border-radius: 8px;
  font-size: 12px; /* 减小字体大小 */
  transition: all 0.2s ease;
  color: #6b7280; /* 默认按钮颜色 */
  background-color: transparent; /* 默认透明背景 */
}

.message-actions .el-button:hover {
  background-color: #f3f4f6; /* 悬停背景色 */
  color: #374151; /* 悬停文字颜色 */
}

.message-actions .el-button .el-icon {
  font-size: 14px; /* 图标大小 */
  margin-right: 4px; /* 图标和文字间距 */
}

/* --- End of Message Item Styles --- */

.chat-input {
  background: white;
  padding: 16px 24px 24px 24px; /* 调整 padding */
  border-top: 1px solid #ebeef5;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05); /* 匹配 ChatDetail 输入框阴影 */
}

.input-wrapper {
  position: relative; /* 添加相对定位 */
  /* 移除 margin: 0 auto; 如果不需要居中 */
}

.input-tips {
  font-size: 12px; /* 减小提示字体大小 */
  color: #b0b0b0; /* 调整提示颜色 */
  position: absolute; /* 绝对定位 */
  top: -18px; /* 调整位置 */
  right: 0; /* 靠右 */
}

.textarea-container {
  display: flex;
  align-items: flex-end; /* 底部对齐 */
  border: 1px solid #dcdfe6; /* 添加边框 */
  border-radius: 12px; /* 匹配 ChatDetail 圆角 */
  padding: 8px 0px 8px 12px; /* 内边距，右侧为0给按钮留空间 */
  background: #f7f8fa; /* 匹配 ChatDetail 输入框背景 */
  transition: border-color 0.2s, box-shadow 0.2s; /* 添加过渡效果 */
}

.textarea-container:focus-within {
  border-color: #4f46e5; /* 聚焦时边框颜色 */
  box-shadow: 0 0 0 1px #4f46e5; /* 聚焦时阴影 */
}

.chat-input :deep(.el-textarea) {
  flex-grow: 1; /* 占据剩余空间 */
  border: none !important; /* 移除 el-textarea 的边框 */
  background: transparent !important; /* 背景透明 */
}

.chat-input :deep(.el-textarea__inner) {
  min-height: 40px !important; /* 调整最小高度 */
  max-height: 200px !important; /* 设置最大高度，超过会滚动 */
  resize: none;
  font-size: 15px;
  line-height: 1.6;
  padding: 0 10px 0 0; /* 移除默认 padding，特别是右侧 */
  box-shadow: none !important; /* 移除默认阴影 */
  border: none !important; /* 再次确认移除边框 */
  background-color: transparent !important; /* 确保背景透明 */
  overflow-y: auto; /* 内容超出时显示滚动条 */
}

/* 移除 Element Plus 默认的 wrapper padding 和 border */
.chat-input :deep(.el-textarea .el-input__wrapper) {
  padding: 0 !important;
  box-shadow: none !important;
  border: none !important;
  background: transparent !important;
}

.send-btn-container {
  display: flex;
  align-items: flex-end; /* 确保按钮底部对齐 */
  padding-left: 8px; /* 与文本框的间距 */
  padding-right: 8px; /* 按钮右侧内边距 */
}

.send-btn {
  padding: 0;
  height: 40px; /* 初始高度与文本框最小高度匹配 */
  min-width: 60px; /* 最小宽度 */
  border-radius: 8px; /* 按钮圆角 */
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease, color 0.2s ease, height 0.1s ease-out; /* 添加高度过渡 */
  display: flex;
  align-items: center;
  justify-content: center;
  align-self: flex-end; /* 按钮自身在 flex 容器中底部对齐 */
}

.send-btn.el-button--primary {
  background: #4f46e5;
  border-color: #4f46e5;
}

.send-btn.el-button--primary:hover {
  background: #4338ca;
  border-color: #4338ca;
  /* transform: translateY(-1px); */ /* 移除悬浮效果 */
}

.send-btn.el-button--success {
  background: #10b981; /* 编辑时的发送按钮颜色 */
  border-color: #10b981;
}
.send-btn.el-button--success:hover {
  background: #059669;
  border-color: #059669;
}

.input-actions {
  display: flex;
  /* justify-content: space-between; */ /* 改为 flex-start */
  justify-content: flex-start;
  align-items: center;
  margin-top: 12px; /* 调整与输入框的间距 */
  gap: 10px; /* 操作按钮之间的间距 */
}

.input-actions .el-button {
  padding: 6px 12px; /* 调整按钮大小 */
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
  background-color: #f3f4f6; /* 默认背景 */
  color: #374151; /* 默认文字颜色 */
  border: 1px solid #e5e7eb; /* 默认边框 */
}
.input-actions .el-button:hover {
  background-color: #e5e7eb;
  border-color: #d1d5db;
}

.input-actions .el-button .el-icon {
  margin-right: 4px;
  font-size: 15px;
}

.uploaded-files {
  margin-top: 16px;
  padding: 0; /* 移除外层 padding */
  /* background: #f9fafb; */ /* 移除背景色 */
  /* border-radius: 12px; */ /* 移除圆角 */
  max-height: 150px; /* 限制最大高度 */
  overflow-y: auto; /* 超出滚动 */
}

.uploaded-file-item {
  display: flex;
  align-items: center;
  gap: 10px; /* 调整间距 */
  padding: 8px 12px;
  background: #f0f2f5; /* 更浅的背景色 */
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.2s ease;
  border: 1px solid #e5e7eb; /* 添加细边框 */
}

.uploaded-file-item:hover {
  background-color: #e8ebf0; /* 悬浮背景色 */
  /* transform: translateX(4px); */ /* 移除悬浮效果 */
}

.file-icon {
  font-size: 18px; /* 调整图标大小 */
  color: #6b7280; /* 图标颜色 */
}

.file-name {
  flex: 1;
  font-size: 14px;
  color: #4f46e5;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis; /* 超长文件名显示省略号 */
}

.file-name:hover {
  text-decoration: underline;
}

.file-size {
  font-size: 12px;
  color: #9ca3af;
  margin-left: auto; /* 文件大小推到右边 */
  padding-left: 10px; /* 和状态保持距离 */
}

.file-status {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
}

.file-status.uploading {
  color: #fbbf24; /* Amber 500 */
  background-color: #fffbeb; /* Amber 50 */
}
.file-status.parsing {
  color: #3b82f6; /* Blue 500 */
  background-color: #eff6ff; /* Blue 50 */
}
.file-status.completed {
  color: #10b981; /* Emerald 500 */
  background-color: #ecfdf5; /* Emerald 50 */
}
.file-status.error {
  color: #ef4444; /* Red 500 */
  background-color: #fef2f2; /* Red 50 */
}

.uploaded-file-item .el-button--text {
  padding: 0;
  margin-left: 8px;
  color: #9ca3af;
  font-size: 16px;
}
.uploaded-file-item .el-button--text:hover {
  color: #ef4444; /* 悬浮变红 */
}

.inferring-indicator {
  display: inline-block; /* 改为 inline-block */
  /* align-items: center; */
  /* gap: 8px; */
  color: #9ca3af;
  font-style: italic;
  padding: 5px 0; /* 增加上下内边距 */
}

.inferring-indicator::after {
  /* 用伪元素模拟光标闪烁 */
  content: "";
  display: inline-block;
  width: 8px;
  height: 1.2em; /* 光标高度 */
  background: #9ca3af;
  margin-left: 4px;
  animation: blink 1s infinite step-end;
  vertical-align: text-bottom; /* 与文字底部对齐 */
}

@keyframes blink {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

.editing-indicator {
  background: #eff6ff; /* Blue 50 */
  border: 1px solid #bfdbfe; /* Blue 200 */
  padding: 8px 12px; /* 调整内边距 */
  border-radius: 8px; /* 调整圆角 */
  margin-bottom: 12px; /* 调整与输入框的间距 */
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px; /* 调整字体大小 */
}

.editing-text {
  color: #3b82f6; /* Blue 500 */
  font-weight: 500;
}

.editing-actions .el-button--text {
  padding: 0;
  font-size: 13px;
  color: #6b7280;
}
.editing-actions .el-button--text:hover {
  color: #ef4444; /* 取消按钮悬浮变红 */
}

.form-section {
  padding: 20px;
  border-bottom: 1px solid #eee;
  background-color: #fff;
}
.form-section:last-child {
  border-bottom: none;
}

h4 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.form-item {
  margin-bottom: 15px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.form-item :deep(.el-input .el-input__inner),
.form-item :deep(.el-textarea .el-textarea__inner) {
  border-radius: 8px;
  background-color: #f7f8fa;
  border-color: #e0e0e0;
}
.form-item :deep(.el-input .el-input__inner:focus),
.form-item :deep(.el-textarea .el-textarea__inner:focus) {
  border-color: #4f46e5;
  box-shadow: 0 0 0 1px #4f46e5;
}

.form-item :deep(.el-radio-group),
.form-item :deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.form-item :deep(.el-radio.el-radio--large),
.form-item :deep(.el-checkbox.el-checkbox--large) {
  height: auto; /* 自适应高度 */
  padding: 8px 15px; /* 调整内边距 */
  border-radius: 20px; /* 胶囊形状 */
  background-color: #f0f2f5;
  border: 1px solid #e0e0e0;
  transition: all 0.2s ease;
  margin-right: 0 !important; /* 覆盖默认 margin */
}

.form-item :deep(.el-radio.el-radio--large .el-radio__label),
.form-item :deep(.el-checkbox.el-checkbox--large .el-checkbox__label) {
  font-size: 14px;
  padding-left: 6px;
}

/* 移除原生的 radio 和 checkbox */
.form-item :deep(.el-radio__inner),
.form-item :deep(.el-checkbox__inner) {
  display: none;
}

.form-item :deep(.el-radio.is-checked),
.form-item :deep(.el-checkbox.is-checked) {
  background-color: #e0e7ff; /* 选中背景色 (Indigo 100) */
  border-color: #a5b4fc; /* 选中边框色 (Indigo 300) */
  color: #4338ca; /* 选中文字颜色 (Indigo 700) */
}

.form-item :deep(.el-radio.is-checked .el-radio__label),
.form-item :deep(.el-checkbox.is-checked .el-checkbox__label) {
  color: #4338ca; /* 确保选中时文字颜色也改变 */
}

.style-options {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.style-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 100px;
  text-align: center;
  position: relative;
  background-color: #fff;
}

.style-option:hover {
  border-color: #a5b4fc;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.style-option.active {
  border-color: #4f46e5;
  background-color: #eef2ff; /* Indigo 50 */
}

.style-icon {
  font-size: 28px;
  margin-bottom: 10px;
}

.style-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.style-desc {
  font-size: 12px;
  color: #777;
  margin-top: 5px;
}

.style-option .remove-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background: rgba(255, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 12px;
  line-height: 18px;
  text-align: center;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.style-option.active:hover .remove-btn {
  opacity: 1;
}
.style-option .remove-btn:hover {
  background: red;
}

.chat-footer {
  padding: 16px 24px;
  background: #fff;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar,
.uploaded-files::-webkit-scrollbar,
.form-container::-webkit-scrollbar {
  width: 6px; /* 减小滚动条宽度 */
}

.chat-messages::-webkit-scrollbar-track,
.uploaded-files::-webkit-scrollbar-track,
.form-container::-webkit-scrollbar-track {
  background: transparent; /* 轨道透明 */
}

.chat-messages::-webkit-scrollbar-thumb,
.uploaded-files::-webkit-scrollbar-thumb,
.form-container::-webkit-scrollbar-thumb {
  background: #d1d5db; /* 滑块颜色 */
  border-radius: 3px; /* 滑块圆角 */
}

.chat-messages::-webkit-scrollbar-thumb:hover,
.uploaded-files::-webkit-scrollbar-thumb:hover,
.form-container::-webkit-scrollbar-thumb:hover {
  background: #9ca3af; /* 悬停时滑块颜色 */
}

/* Thinkpad 特有的上传按钮样式 */
.thinkpad-upload-btn {
  display: inline-flex; /* 改为 inline-flex */
  align-items: center;
  padding: 8px 15px;
  border: 1px solid #dcdfe6;
  border-radius: 20px; /* 胶囊形状 */
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  color: #606266;
  background-color: #fff;
}
.thinkpad-upload-btn:hover {
  border-color: #c0c4cc;
  color: #409eff;
}
.thinkpad-upload-btn .el-icon {
  margin-right: 6px;
  font-size: 16px;
}

/* Thinkpad 已上传文件列表 */
.thinkpad-uploaded-files {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.thinkpad-uploaded-files .uploaded-file-item {
  /* 复用之前的样式，或根据需要微调 */
  background: #f0f2f5;
  border-radius: 8px;
  padding: 6px 10px;
  margin-bottom: 0; /* 移除底部 margin */
}

.image-generation-section {
  margin-top: 16px;
  border-top: 1px solid #eee;
  padding-top: 16px;
}

/* 添加加载动画相关样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  display: flex;
  gap: 6px;
}

.loading-spinner .dot {
  width: 8px;
  height: 8px;
  background: #4e6ef2;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-spinner .dot:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-spinner .dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.loading-text {
  font-size: 14px;
  color: #666;
}

.cancel-btn {
  margin-top: 8px;
  padding: 6px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn:hover {
  background: #f5f5f5;
  border-color: #ccc;
}
</style>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, computed, onUnmounted } from "vue";
import type { RoleDetail } from "@/api/roles";
import type { Message } from "@/types/chat";
import { ElMessage } from "element-plus";
import { sendMessage } from "@/api/chat";
import VideoTaskPanel from "@/components/workspace/VideoTaskPanel.vue";
import MJTaskPanel from "@/components/workspace/MJTaskPanel.vue";
import StrategyForm from "@/components/workspace/StrategyForm.vue";
import ProductValidationForm from "@/components/workspace/ProductValidationForm.vue";
import { v4 as uuidv4 } from "uuid";
import { EditPen, DocumentCopy } from "@element-plus/icons-vue";
import { Document, Check } from "@element-plus/icons-vue";
import { marked, type MarkedOptions } from "marked"; // 导入 MarkedOptions 类型
import hljs from "highlight.js";
import "highlight.js/styles/github.css";
import { copyTextToClipboard } from "@/utils/clipboard";
import { getToken } from "@/utils/auth";
import { ArrowLeft, ArrowRight } from "@element-plus/icons-vue"; // 导入箭头图标
import { switchBranch } from "@/api/chat"; // 导入切换分支API
import { getSessionMessages } from "@/api/chat"; // 导入获取消息API
import config from "@/config";
import HtmlPreview from "./HtmlPreview.vue";

const props = defineProps<{
  role: RoleDetail | null;
  openingStatement?: string;
  sessionId?: string;
}>();
const messageHtmlMap = ref<Record<string, any>>({});
const emit = defineEmits<{
  (e: "close"): void;
  (e: "session-created", sessionId: string): void;
  (e: "session-error"): void;
  (e: "branch-created", data: any): void;
}>();

// 状态管理
const messages = ref<Message[]>([]);
const inputMessage = ref("");
const sending = ref(false);
const chatContentRef = ref<HTMLElement | null>(null);
const currentSessionId = ref<string | undefined>(props.sessionId);
const inferring = ref(false);
const showStyleSelector = ref(false);
const selectedStyles = ref([]);
const activeBranchId = ref<number>(0); // 重新添加 activeBranchId
const loadingMessages = ref(false); // 重新添加 loadingMessages

// Configure marked with highlight.js
marked.setOptions({
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
  breaks: true,
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

// 文件相关工具函数
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

const getFileIcon = (type: string) => {
  const icons: Record<string, string> = {
    pdf: "📄",
    doc: "📝",
    docx: "📝",
    xlsx: "📊",
    xls: "📊",
    ppt: "📊",
    pptx: "📊",
    txt: "��",
    csv: "📊",
  };
  return icons[type] || "📄";
};

const getStatusText = (status: string) => {
  switch (status) {
    case "uploading":
      return "上传中...";
    case "parsing":
      return "解析中...";
    case "completed":
      return "已完成";
    case "error":
      return "上传失败";
    default:
      return "";
  }
};

// 修改 deleteFile 函数
const deleteFile = async (fileId: string) => {
  if (!fileId) {
    ElMessage.warning("文件ID不存在");
    return;
  }

  const token = localStorage.getItem("token");
  if (!token) {
    ElMessage.error("请先登录");
    return;
  }

  const response = await fetch(`${config.baseURL}/api/chat/files/${fileId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("删除文件失败");
  }

  // 不需要更新 uploadedFiles，因为会在 handleRemoveFile 中统一处理
  ElMessage.success("文件删除成功");
};

// 处理关闭
const handleClose = () => {
  emit("close");
};

const formatStyleMessage = (userMessage: string, selectedStyles: number[]) => {
  if (!userMessage.trim() || selectedStyles.length === 0) {
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
let messageAutoId = 1;
// 修复发送消息函数
const handleSend = async (eventPayload: {
  content: string;
  files: File[];
  isEdit: boolean;
  parentMessageId: string;
  model: "gpt" | "deepseek";
}) => {
  // 检查是否有正在进行的请求
  if (sending.value) return;

  // 获取输入的消息内容
  const message = inputMessage.value.trim();

  // 检查消息是否为空
  if (!message && !uploadedFiles.value.length) {
    ElMessage.warning("请输入消息内容或上传文件");
    return;
  }

  // 设置发送状态
  sending.value = true;

  // 保存编辑状态，用于后续处理
  const isEditMode = !!editingMessageId.value;
  const editedMessageId = editingMessageId.value;

  // 应用风格提示（如果有选择风格）
  const formattedMessage = formatStyleMessage(message, selectedStyles.value);

  // 获取成功上传的文件
  const successfulFiles = uploadedFiles.value.filter(
    (file) => file.status === "completed"
  );

  // 调试信息（生产环境可移除）
  if (process.env.NODE_ENV === 'development') {
    console.log("ChatDialog - 文件上传状态:");
    console.log("- 所有上传的文件:", uploadedFiles.value);
    console.log("- 成功上传的文件:", successfulFiles);
    console.log("- 文件ID列表:", successfulFiles.map(f => f.dify_file_id));
  }

  // 构建请求参数
  const params = {
    session_id: currentSessionId.value,
    role_id: props.role?.id,
    file_ids: successfulFiles.map((file) => file.dify_file_id),
    session_type: currentSessionId.value ? "continue" : "single_role",
    content: eventPayload ? eventPayload.content : message,
    parent_message_id: "",
    branch_id: activeBranchId.value,
    model: eventPayload?.model || "gpt", // 使用 eventPayload 中传递的模型参数
  };

  // 调试信息（生产环境可移除）
  if (process.env.NODE_ENV === 'development') {
    console.log("ChatDialog - 发送消息参数:", params);
  }
  // 如果角色id 是 30 或者 31
  if (props.role?.id === 30 || props.role?.id === 31) {
    // thinkpadForm.value.files 也要加入files_ids
    params.file_ids = [
      ...params.file_ids,
      ...thinkpadForm.value.files.map((file) => file.dify_file_id),
    ];
  }

  try {
    // 创建用户消息
    const userMessage = {
      id: messageAutoId++,
      content: formattedMessage,
      type: "user" as const,
      timestamp: Date.now() / 1000,
      files: successfulFiles.map((file) => ({
        id: file.dify_file_id,
        name: file.name,
        type: file.type,
        size: file.size,
        dify_file_id: file.dify_file_id,
        obs_preview_url: file.obs_preview_url,
      })),
    };
    // 如果角色id 是 30 或者 31
    if (props.role?.id === 30 || props.role?.id === 31) {
      userMessage.files = thinkpadForm.value.files.map((file) => ({
        id: file.dify_file_id,
        name: file.name,
        type: file.type,
        size: file.size,
        dify_file_id: file.dify_file_id,
        obs_preview_url: file.obs_preview_url,
      }));
    }

    // 清空输入和文件列表
    inputMessage.value = "";
    uploadedFiles.value = [];
    selectedStyles.value = [];
    showStyleSelector.value = false;

    // 如果是编辑模式，添加 parentMessageId 参数
    if (isEditMode) {
      // 查找被编辑的消息
      const editedMessage = messages.value.find(
        (m) => m.message_id === editedMessageId
      );
      // 检查消息对象
      console.log("找到要编辑的消息:", editedMessage);

      // 从消息ID中提取Dify消息ID (格式可能是 "user_message_id" 或 "user_{timestamp}")
      if (editedMessage) {
        let messageId = null;

        // 如果消息对象有 message_id 属性，直接使用
        if (editedMessage.message_id) {
          messageId = editedMessage.message_id;
        }

        if (messageId) {
          // 使用消息的 message_id 作为 parent_message_id
          params.parent_message_id = messageId;
          console.log("发送编辑请求 - 参数:", params);
        } else {
          console.log("编辑消息 - 无法提取有效的消息ID:", editedMessageId);
          console.warn("无法找到被编辑消息的 message_id");
        }
      }
    }

    // 添加用户消息到列表
    messages.value.push(userMessage);

    // 重置文本框高度
    resetTextareaHeight();

    scrollToBottom();

    // 创建AI回复的临时消息
    const aiMessage = {
      id: messageAutoId++,
      content: "",
      inferring: true,
      type: "assistant" as const,
      timestamp: Date.now() / 1000,
    };
    messages.value.push(aiMessage);
    inferring.value = true;

    // 发送请求
    const response = await sendMessage(params);

    // 处理流式响应
    let accumulatedContent = "";

    if (response.ok) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          inferring.value = false; // Reset inferring state on clean stream end
          break;
        }

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
                  currentSessionId.value = event.data.id;
                  emit("session-created", event.data.id);
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

              case "message":
                if (event.answer) {
                  // 更新AI消息内容
                  accumulatedContent += event.answer;

                  // 更新最后一条消息
                  const lastMessage = messages.value[messages.value.length - 1];
                  if (lastMessage && lastMessage.type === "assistant") {
                    lastMessage.content = accumulatedContent;
                    // 保存消息ID
                    if (event.message_id && !lastMessage.message_id) {
                      lastMessage.message_id = event.message_id;
                      console.log("收到AI消息ID:", event.message_id);
                    }
                  }

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
                    messages.value[userIdx].message_id = event.message_id;
                    console.log("保存用户消息ID:", event.message_id);
                  }
                  if (aiIdx !== -1) {
                    messages.value[aiIdx].message_id = event.message_id;
                    // 设置消息状态为成功
                    console.log("保存AI消息ID:", event.message_id);
                  }
                }
                break;
              case "message_end":
                inferring.value = false; // Reset inferring state
                if (event.message_id) {
                  const userIdx = messages.value.findIndex(
                    (m) => m.id === userMessage.id
                  );
                  const aiIdx = messages.value.findIndex(
                    (m) => m.id === aiMessage.id
                  );

                  if (userIdx !== -1) {
                    messages.value[userIdx].message_id = event.message_id;
                    console.log("保存用户消息ID:", event.message_id);
                  }
                  if (aiIdx !== -1) {
                    messages.value[aiIdx].message_id = event.message_id;
                    messages.value[aiIdx].inferring = false;
                    // 设置消息状态为成功
                    messages.value[aiIdx].api_status = "success";
                    console.log("保存AI消息ID:", event.message_id);
                  }
                }
                break;

              case "error":
                inferring.value = false; // Reset inferring state
                // 处理错误事件
                console.error("AI 响应错误:", event.message);

                // 找到最后一条AI消息
                const lastAiMessage = messages.value.find(
                  (m) => m.id === aiMessage.id
                );
                if (lastAiMessage) {
                  // 将"正在推理中"改为"当前系统繁忙，请稍后再试或联系管理员"
                  lastAiMessage.inferring = false;
                  lastAiMessage.api_status = "error";
                }

                // 如果是首次对话（没有有效的会话ID），清除当前会话ID
                if (!props.sessionId && currentSessionId.value) {
                  console.warn(
                    "首次对话失败，清除临时会话ID:",
                    currentSessionId.value
                  );
                  currentSessionId.value = "";
                  // 通知父组件会话创建失败
                  emit("session-error");
                }

                // 显示错误提示
                ElMessage.error(event.message || "生成回复失败，请稍后再试");
                break;
            }
          } catch (e) {
            console.error("解析响应失败:", e);
            console.error("line:", line);
            inferring.value = false; // Reset inferring state on parsing error
          }
        }
      }
    } else {
      ElMessage.error("发送消息失败");
      inferring.value = false; // Reset inferring state if response not ok
    }
  } catch (error) {
    console.error("发送消息失败:", error);
    ElMessage.error("发送失败，请重试");
    sending.value = false;
    inferring.value = false;
  } finally {
    sending.value = false;
    // 在响应处理完成后再清除编辑状态
    if (isEditMode) {
      editingMessageId.value = null;
      originalMessageContent.value = "";
    }
  }

  // 如果是编辑模式，可以考虑在处理完成后刷新消息列表
  if (isEditMode) {
    // 可以在这里添加一些视觉反馈，表明编辑成功
    ElMessage.success("消息已更新");

    // 高亮显示新添加的消息
    const lastMessageElement = document.querySelector(
      ".messages .message:last-child"
    );
    if (lastMessageElement) {
      lastMessageElement.classList.add("highlight-new");
      setTimeout(() => {
        lastMessageElement.classList.remove("highlight-new");
      }, 2000);
    }
  }
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    const chatContent = chatContentRef.value;
    if (chatContent) {
      chatContent.scrollTop = chatContent.scrollHeight;
    }
  });
};

// 检查是否是图片URL
const isImageUrl = (url?: string) => {
  if (!url) return false;
  const obsPattern = /^https?:\/\/[^/]+\.obs\.[^/]+\.(huaweicloud\.com|myhuaweicloud\.com)/;
  const imagePattern = /\.(jpg|jpeg|png|webp|avif|gif|svg|bmp|tiff)(\?.*)?$/i;
  const dataUrlPattern = /^data:image\//;
  return obsPattern.test(url) || imagePattern.test(url) || dataUrlPattern.test(url);
};

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

// 处理图片加载错误
const handleImageError = (e: Event) => {
  const target = e.target as HTMLImageElement;
  console.error("Avatar load failed:", target.src);
  target.style.display = "none";
  target.parentElement?.classList.add("show-fallback");
};

// 格式化开场白
const formatOpeningStatement = (text: string) => {
  try {
    // Try to parse as JSON first
    const jsonData = JSON.parse(text);
    return `<pre class="json-content">${JSON.stringify(
      jsonData,
      null,
      2
    )}</pre>`;
  } catch {
    // If not JSON, treat as markdown
    return marked(text);
  }
};

// 组件挂载时初始化
onMounted(() => {
  // 不再在这里添加欢迎消息，因为模板中已经处理了
  scrollToBottom();

  // 初始化文本框高度
  nextTick(() => {
    adjustTextareaHeight();
  });

  // 监听窗口大小变化，重新调整高度
  window.addEventListener("resize", adjustTextareaHeight);
});

// 监听 props.openingStatement 的变化
watch(
  () => props.openingStatement,
  (newVal) => {
    if (newVal && messages.value.length === 0) {
      messages.value = [];
    }
  },
  { immediate: true }
);

// 复制文本
const copyText = (text) => {
  if (!text) return;

  copyTextToClipboard(text)
    .then(() => {
      ElMessage.success("已复制到剪贴板");
    })
    .catch(() => {
      ElMessage.error("复制失败，请手动复制");
    });
};

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

// 监听props.sessionId的变化
watch(
  () => props.sessionId,
  (newId) => {
    currentSessionId.value = newId;
  }
);

// 判断是否显示传播策略框架表单
const showStrategyForm = computed(() => {
  return (
    props.role &&
    props.role.id === 9 &&
    messages.value.length === 0 &&
    !strategyFormSubmitted.value
  );
});

// 添加表单提交状态
const strategyFormSubmitted = ref(false);

// 处理传播策略表单提交
const handleStrategyFormSubmit = async (payload: {
  formData: any;
  formattedContent: string;
}) => {
  // 设置输入消息为格式化后的表单内容
  inputMessage.value = payload.formattedContent;

  // 设置表单已提交状态
  strategyFormSubmitted.value = true;

  // 调用发送消息函数
  await handleSend();
};

// 文本框引用和行数控制
const textareaRef = ref(null);
const textareaRows = ref(3); // 默认行数
const maxRows = 10; // 最大行数限制

// 调整文本框高度的函数
const adjustTextareaHeight = () => {
  const textarea = textareaRef.value;
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

  // 同时调整发送按钮高度
  const sendButton = textarea.parentElement?.querySelector(".send-btn");
  if (sendButton) {
    sendButton.style.height = `${newHeight}px`;
  }

  // 恢复滚动位置
  textarea.scrollTop = scrollTop;

  // 如果内容超过最大行数，启用滚动
  if (contentHeight > maxRows * lineHeight + paddingTop + paddingBottom) {
    textarea.style.overflowY = "auto";
  } else {
    textarea.style.overflowY = "hidden";
  }
};

// 修改重置文本框高度函数，同时重置发送按钮高度
const resetTextareaHeight = () => {
  if (textareaRef.value) {
    // 设置为基础高度
    textareaRef.value.style.height = "80px";
    textareaRows.value = 3;

    // 同时重置发送按钮高度
    const sendButton =
      textareaRef.value.parentElement?.querySelector(".send-btn");
    if (sendButton) {
      sendButton.style.height = "80px";
    }
  }
};

// 监听输入消息变化
watch(inputMessage, () => {
  nextTick(() => {
    adjustTextareaHeight();
  });
});

// 在组件卸载前移除事件监听
onUnmounted(() => {
  window.removeEventListener("resize", adjustTextareaHeight);
});

// 在 data 部分添加编辑状态相关变量
const editingMessageId = ref<string | null>(null); // 当前正在编辑的消息ID
const originalMessageContent = ref(""); // 保存原始消息内容，用于取消编辑时恢复
const editingSourceMessage = ref<Message | null>(null); // 保存被编辑的消息对象

// 在 methods 部分添加编辑相关函数
const startEditing = (message: Message) => {
  // 只允许编辑用户消息
  if (message.type !== "user") return;

  // 如果已经在编辑其他消息，先取消之前的编辑
  if (editingMessageId.value && editingMessageId.value !== message.message_id) {
    cancelEditing();
  }

  // 保存原始输入框内容（如果需要恢复的话）
  // originalMessageContent.value = inputMessage.value;

  // 设置编辑状态
  editingMessageId.value = message.message_id || null; // 使用 message_id
  editingSourceMessage.value = message; // 保存源消息对象

  // 将消息内容填充到输入框
  inputMessage.value = message.content;

  // 调整文本框高度
  nextTick(() => {
    adjustTextareaHeight();
    // 聚焦输入框
    textareaRef.value?.focus();
    // 滚动到输入区域
    const inputArea = document.querySelector(".chat-input");
    inputArea?.scrollIntoView({ behavior: "smooth" });
  });
};

const cancelEditing = () => {
  // 恢复原始消息内容 (可选，看是否需要恢复输入框之前的状态)
  // inputMessage.value = originalMessageContent.value;
  inputMessage.value = ""; // 直接清空输入框

  // 清除编辑状态
  editingMessageId.value = null;
  editingSourceMessage.value = null; // 清除源消息

  // 调整文本框高度
  nextTick(() => {
    adjustTextareaHeight();
  });
};

// ThinkPad 表单选项定义
const targetUserOptions = [
  { value: "business", label: "商务白领 / 企业高管" },
  { value: "creative", label: "设计师 / 创意工作者" },
  { value: "developer", label: "程序员 / 开发者" },
  { value: "student", label: "学生 / 教育用户" },
];

const usageScenarioOptions = [
  { value: "mobile_office", label: "移动办公 / 远程会议" },
  { value: "video_design", label: "视频剪辑 / 图形设计" },
  { value: "coding", label: "代码开发 / 多任务处理" },
  { value: "data_analysis", label: "数据分析 / 模拟仿真" },
];

// ThinkPad 表单数据
const thinkpadForm = ref({
  basicInfo: {
    brand: "",
    series: "",
    positioning: "",
  },
  targetUser: {
    type: "",
    customType: "",
    scenarios: [],
    customScenario: "",
  },
  files: [],
  sellingPoints: "",
  stylePreferences: {
    tone: "",
    slogan: "",
  },
});

// 修复 ThinkPad 表单显示逻辑
const showThinkpadForm = computed(() => {
  return (
    props.role &&
    (props.role.id === 30 || props.role.id === 31) &&
    messages.value.length === 0 &&
    !thinkpadFormSubmitted.value
  );
});

// ThinkPad 表单是否已提交
const thinkpadFormSubmitted = ref(false);

// ThinkPad 表单是否有效
const isThinkpadFormValid = computed(() => {
  // 检查基础信息
  const basicInfoValid =
    thinkpadForm.value.basicInfo.brand.trim() !== "" &&
    thinkpadForm.value.basicInfo.series.trim() !== "" &&
    thinkpadForm.value.basicInfo.positioning.trim() !== "";

  // 检查目标用户类型
  let targetUserValid = thinkpadForm.value.targetUser.type !== "";
  if (thinkpadForm.value.targetUser.type === "custom") {
    targetUserValid =
      targetUserValid && thinkpadForm.value.targetUser.customType.trim() !== "";
  }

  // 检查使用场景
  let scenariosValid = thinkpadForm.value.targetUser.scenarios.length > 0;
  if (thinkpadForm.value.targetUser.scenarios.includes("custom")) {
    scenariosValid =
      scenariosValid &&
      thinkpadForm.value.targetUser.customScenario.trim() !== "";
  }

  // 检查卖点优先级
  const sellingPointsValid = thinkpadForm.value.sellingPoints.trim() !== "";

  return (
    basicInfoValid && targetUserValid && scenariosValid && sellingPointsValid
  );
});

// ThinkPad 文件上传相关
const thinkpadFileInput = ref(null);

const handleThinkpadFileClick = () => {
  thinkpadFileInput.value?.click();
};

const handleThinkpadFileUpload = async (event) => {
  const files = Array.from((event.target as HTMLInputElement).files || []);
  const token = localStorage.getItem("token");
  if (!token) {
    ElMessage.error("请先登录");
    return;
  }

  // 定义允许的文件类型
  const allowedDocumentTypes = [
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

  const allowedImageTypes = ["jpg", "jpeg", "png", "gif", "webp", "svg"];

  for (const file of files) {
    // 获取文件扩展名
    const fileExtension = file.name.split(".").pop()?.toLowerCase() || "";

    // 检查文件类型是否允许
    if (
      !allowedDocumentTypes.includes(fileExtension) &&
      !allowedImageTypes.includes(fileExtension)
    ) {
      ElMessage.error(`不支持的文件类型: ${file.name}`);
      continue;
    }

    // 检查文件大小
    if (file.size > 10 * 1024 * 1024) {
      ElMessage.error(`文件大小不能超过10MB: ${file.name}`);
      continue;
    }

    // 初始化文件对象
    const fileObj = {
      id: uuidv4(),
      name: file.name,
      size: file.size,
      type: fileExtension,
      status: "uploading" as const,
    };
    thinkpadForm.value.files.push(fileObj);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("roleId", props.role?.id || "");

      // 上传文件
      const response = await fetch(`${config.baseURL}/api/chat/files/upload`, {
        method: "POST",
        body: formData,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("上传失败");
      }

      const result = await response.json();
      if (result.success) {
        // 上传成功
        const index = thinkpadForm.value.files.findIndex(
          (f) => f.id === fileObj.id
        );
        if (index !== -1) {
          thinkpadForm.value.files[index] = {
            ...fileObj,
            status: "completed",
            url: result.data.url,
            dify_file_id: result.data.dify_file_id,
            obs_object_key: result.data.obs_object_key,
            obs_preview_url: result.data.obs_preview_url,
          };
        }
        ElMessage.success("上传成功");
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      console.error("文件上传失败:", error);

      // 更新文件状态为失败
      const index = thinkpadForm.value.files.findIndex(
        (f) => f.id === fileObj.id
      );
      if (index !== -1) {
        thinkpadForm.value.files[index].status = "error";
      }

      ElMessage.error("上传失败");
    }
  }

  // 清空文件输入框
  if (event.target) {
    (event.target as HTMLInputElement).value = "";
  }
};

const handleRemoveThinkpadFile = async (file) => {
  try {
    // 如果文件已经上传完成并有 dify_file_id，需要调用后端接口删除
    if (file.status === "completed" && file.dify_file_id) {
      await deleteFile(file.dify_file_id);
    }

    // 无论是否调用后端，都从前端列表中移除
    thinkpadForm.value.files = thinkpadForm.value.files.filter(
      (f) => f.id !== file.id
    );
  } catch (error) {
    console.error("移除文件失败:", error);
    ElMessage.error("移除文件失败");
  }
};

// 提交 ThinkPad 表单
const submitThinkpadForm = async () => {
  if (!isThinkpadFormValid.value) {
    ElMessage.warning("请填写所有必填项");
    return;
  }

  // 将表单数据格式化为消息内容
  const formattedContent = formatThinkpadFormToMessage(thinkpadForm.value);

  // 设置输入消息为格式化后的表单内容
  inputMessage.value = formattedContent;

  // 设置表单已提交状态
  thinkpadFormSubmitted.value = true;

  // 调用发送消息函数
  await handleSend();

  // 重置表单
  resetThinkpadForm();
};

// 格式化 ThinkPad 表单数据为消息内容
const formatThinkpadFormToMessage = (form) => {
  // 处理目标用户类型
  let targetUserType = "";
  if (form.targetUser.type === "custom") {
    targetUserType = form.targetUser.customType;
  } else {
    const selectedOption = targetUserOptions.find(
      (opt) => opt.value === form.targetUser.type
    );
    targetUserType = selectedOption
      ? selectedOption.label
      : form.targetUser.type;
  }

  // 处理使用场景
  const scenarios = form.targetUser.scenarios
    .map((scenario) => {
      if (scenario === "custom") {
        return form.targetUser.customScenario;
      } else {
        const scenarioOption = usageScenarioOptions.find(
          (opt) => opt.value === scenario
        );
        return scenarioOption ? scenarioOption.label : scenario;
      }
    })
    .join("、");

  // 构建文件列表文本
  const filesText =
    form.files.length > 0
      ? form.files
          .filter((file) => file.status === "completed")
          .map((file) => `- ${file.name}`)
          .join("\n")
      : "无文件上传";

  return `# ThinkPad 产品详情页信息

## 基础产品信息
- **品牌名称**：${form.basicInfo.brand}
- **产品系列**：${form.basicInfo.series}
- **产品定位**：${form.basicInfo.positioning}

## 目标用户与应用场景
- **目标人群**：${targetUserType}
- **使用场景**：${scenarios}

## 卖点内容
已上传文件：
${filesText}

## 卖点优先级
${form.sellingPoints}

## 风格补充建议
- **口吻/气质关键词**：${form.stylePreferences.tone || "无特殊要求"}
- **品牌口号/态度语**：${form.stylePreferences.slogan || "无特殊要求"}

请根据以上信息，生成一份结构完整、风格统一的 ThinkPad 详情页内容。`;
};

// 重置 ThinkPad 表单
const resetThinkpadForm = () => {
  thinkpadForm.value = {
    basicInfo: {
      brand: "",
      series: "",
      positioning: "",
    },
    targetUser: {
      type: "",
      customType: "",
      scenarios: [],
      customScenario: "",
    },
    files: [],
    sellingPoints: "",
    stylePreferences: {
      tone: "",
      slogan: "",
    },
  };
};

// 在 ThinkPad 表单相关的 script 部分添加以下交互增强逻辑

// 添加选中样式的处理函数
const updateSelectedStyles = () => {
  nextTick(() => {
    // 为单选项添加选中样式
    const radioOptions = document.querySelectorAll(".radio-option");
    radioOptions.forEach((option) => {
      const radio = option.querySelector('input[type="radio"]');
      if (radio && radio.checked) {
        option.classList.add("selected");
      } else {
        option.classList.remove("selected");
      }
    });

    // 为复选项添加选中样式
    const checkboxOptions = document.querySelectorAll(".checkbox-option");
    checkboxOptions.forEach((option) => {
      const checkbox = option.querySelector('input[type="checkbox"]');
      if (checkbox && checkbox.checked) {
        option.classList.add("selected");
      } else {
        option.classList.remove("selected");
      }
    });
  });
};

// 监听表单值变化，更新选中样式
watch(() => thinkpadForm.value.targetUser.type, updateSelectedStyles);
watch(() => thinkpadForm.value.targetUser.scenarios, updateSelectedStyles, {
  deep: true,
});

// 监听表单显示，初始化样式
watch(showThinkpadForm, (newVal) => {
  if (newVal) {
    nextTick(() => {
      updateSelectedStyles();
    });
  }
});

/**
 * @function switchToAdjacentBranch
 * @description 切换到相邻的分支（版本）
 * @param {Message} message - 包含分支信息的消息对象
 * @param {number} delta - 切换方向 (-1 表示上一个, +1 表示下一个)
 */
const switchToAdjacentBranch = async (message: Message, delta: number) => {
  if (!currentSessionId.value) {
    ElMessage.warning("缺少会话信息，无法切换版本");
    return;
  }

  if (!message.next_branches || !message.next_branches.branches?.length) {
    console.warn("消息对象缺少有效的分支信息:", message);
    return;
  }

  const branches = message.next_branches.branches;
  // 在切换分支时，current_branch_index 应该反映当前显示的分支
  let currentIndex = message.next_branches.current_branch_index;

  if (currentIndex === -1) {
    console.warn(
      `无法确定当前分支索引，message branch_id: ${message.branch_id}, activeBranchId: ${activeBranchId.value}`,
      branches
    );
    // Fallback: try finding the active branch ID in the list if message.branch_id isn't reliable
    const fallbackIndex = branches.findIndex(
      (b) => b.branch_id === activeBranchId.value
    );
    if (fallbackIndex === -1) {
      console.error("无法在分支列表中找到活跃分支ID，无法切换。");
      return;
    }
    // If fallback works, use it (though this indicates potential data inconsistency)
    currentIndex = fallbackIndex;
  }

  // 计算目标分支的索引
  const targetIndex = currentIndex + delta;

  // 检查目标索引是否有效
  if (targetIndex < 0 || targetIndex >= branches.length) {
    return;
  }

  const targetBranchId = branches[targetIndex].branch_id;

  console.log(
    `ChatDialog: 准备切换分支 - 从索引 ${currentIndex} 到 ${targetIndex} (目标分支ID: ${targetBranchId})`
  );

  try {
    // 调用后端 API 切换分支
    await switchBranch(currentSessionId.value, targetBranchId);

    console.log(`ChatDialog: 后端切换分支成功，目标: ${targetBranchId}`);

    // 切换成功后，更新 activeBranchId 并重新加载消息（使用拼接方式）
    activeBranchId.value = targetBranchId;
    message.next_branches.current_branch_index = targetIndex;
    // 传递源消息 message 和 isEdited=false
    await loadBranchMessages(targetBranchId, message, false);

    ElMessage.success("版本切换成功");
  } catch (error) {
    console.error("ChatDialog: 切换分支失败:", error);
    ElMessage.error("切换版本失败，请重试");
  }
};

/**
 * @computed processedMessages
 */
const processedMessages = computed(() => {
  // Implement your logic to process messages here
  return messages.value.map((message) => ({
    ...message,
    processed: true,
  }));
});

/**
 * @function loadBranchMessages
 * @description 加载指定分支的消息，并根据需要进行拼接或替换
 * @param {number} branchId - 要加载的分支ID
 * @param {Message | null} [sourceMessage] - (可选) 触发加载的源消息，用于拼接
 * @param {boolean} [isEditedMessage=false] - (可选) 是否由编辑消息触发
 */
const loadBranchMessages = async (
  branchId: number,
  sourceMessage?: Message | null,
  isEditedMessage: boolean = false
) => {
  if (!currentSessionId.value) {
    console.warn("loadBranchMessages: 缺少会话ID");
    return;
  }

  try {
    loadingMessages.value = true;
    console.log(
      `ChatDialog: 开始加载分支消息 - 分支ID: ${branchId}, 源消息ID: ${
        sourceMessage?.message_id || "无"
      }, 是否编辑: ${isEditedMessage}`
    );

    const response = await getSessionMessages(currentSessionId.value, {
      page: 1,
      size: 100, // 加载足够多确保上下文完整
      branch_id: branchId,
      include_context: 0, // 请求包含上下文
      message_id:
        sourceMessage?.next_branches?.branches[
          sourceMessage?.next_branches.current_branch_index
        ]?.id,
    });

    if (response.data) {
      // 1. 直接映射 API 响应数据，确保包含 next_branches
      const fetchedMessages = (response.data.messages as any[]).map(
        (item: any) => ({
          id: item.id, // 使用后端数据库ID
          message_id: item.message_id,
          content: item.content,
          type: item.type,
          timestamp: item.timestamp,
          files: item.files || [],
          api_status: item.api_status || "success",
          inferring: false,
          branch_id: item.branch_id,
          next_branches: item.next_branches, // 直接映射
          fork_from_id: item.fork_from_id,
        })
      );
      fetchedMessages.sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0));

      console.log(
        `获取到${fetchedMessages.length}条分支 ${branchId} 的消息 (含上下文)`
      );

      // 2. Splicing Logic
      if (sourceMessage) {
        // 使用 message_id 或 id 查找源消息在当前显示列表中的索引
        const sourceKey = sourceMessage.message_id;
        const sourceIndex = messages.value.findIndex(
          (m) => m.message_id === sourceKey
        );

        if (sourceIndex !== -1) {
          console.log(`源消息 (key: ${sourceKey}) 找到位置: ${sourceIndex}`);
          // 拼接：保留 sourceIndex 之前的消息，追加获取到的完整上下文消息列表
          const preservedMessages = messages.value.slice(0, sourceIndex);

          if (isEditedMessage) {
            const firstMessage = fetchedMessages[0];
            // 为新创建的分支构造信息
            const newBranchInfo = {
              id: firstMessage.message_id, // 使用message_id
              title: firstMessage.content, // 内容摘要
              branch_id: firstMessage.branch_id,
            };
            if (sourceMessage?.next_branches) {
              firstMessage.next_branches = sourceMessage.next_branches;
            } else {
              firstMessage.next_branches = {
                branches: [
                  {
                    id: sourceMessage.message_id,
                    title: sourceMessage.content,
                    branch_id: sourceMessage.branch_id || 0,
                  },
                ],
                count: 1,
                current_branch_index: 0,
              };
            }
            firstMessage.next_branches.branches.push(newBranchInfo);
            firstMessage.next_branches.count =
              firstMessage.next_branches.branches.length;
            firstMessage.next_branches.current_branch_index =
              firstMessage.next_branches.branches.length - 1;
            console.log(
              "firstMessage.next_branches",
              firstMessage.next_branches
            );
          } else {
            // 非编辑的，需要复制
            const firstMessage = fetchedMessages[0];
            if (sourceMessage?.next_branches) {
              firstMessage.next_branches = sourceMessage.next_branches;
            }
          }
          messages.value = [...preservedMessages, ...fetchedMessages];
          console.log(`拼接完成, 当前总数: ${messages.value.length}`);
          // 注意：普通切换分支时，不需要手动更新 next_branches，因为 include_context=1 返回的数据应该已经是正确的
        } else {
          console.warn(
            `源消息 (key: ${sourceKey}) 未在列表中找到，将直接替换列表。`
          );
          messages.value = fetchedMessages;
        }
      } else {
        // 如果没有源消息（例如，首次加载或完全刷新），直接替换
        console.log("无源消息，直接替换列表。");
        messages.value = fetchedMessages;
      }

      // 4. 更新活跃分支 ID
      activeBranchId.value = response.data.active_branch_id ?? branchId;
      console.log(`ChatDialog: 活跃分支ID更新为: ${activeBranchId.value}`);
      scrollToBottom();
    } else {
      console.warn("ChatDialog: 加载分支消息失败，未收到有效数据。", response);
      ElMessage.warning("加载版本消息失败，请稍后再试。");
    }
  } catch (error) {
    console.error("ChatDialog: 获取分支消息（含上下文）失败:", error);
    ElMessage.error("加载版本消息时出错，请重试。");
  } finally {
    loadingMessages.value = false;
  }
};

/**
 * @function handleBranchCreated
 * @description 处理分支创建事件，更新状态并加载新分支消息
 * @param {object} data - 包含新分支ID的数据
 * @param {Message | null} sourceMessage - 触发编辑的原始消息
 */
const handleBranchCreated = (
  data: { branch_id: number },
  sourceMessage: Message | null
) => {
  console.log("ChatDialog: 收到分支创建事件", data, "源消息:", sourceMessage);
  if (data?.branch_id) {
    const newBranchId = data.branch_id;
    activeBranchId.value = newBranchId;
    console.log(`ChatDialog: 活跃分支ID更新为: ${newBranchId}`);

    // 创建分支后，加载包含上下文的新分支消息
    // 注意：传递 triggerMessage 和 isEdited=true
    loadBranchMessages(newBranchId, sourceMessage, true);
  }
};
const updateMessageTasks = (messageId: string, newTasks: any[]) => {
  messages.value = messages.value.map((msg) => {
    if (msg.message_id === messageId) {
      // 根据session角色判断是视频任务还是MJ任务
      if (props?.role?.id === 3) {
        // 视频任务
        return {
          ...msg,
          videoTasks: newTasks,
        };
      } else if (props?.role?.id === 28) {
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

const openEQMJ = () => {
  window.open(config.EQMJ_HOME, "_blank");
};

/**
 * @description 当前对话弹窗内统一的模型选择（gpt/deepseek），初始值为 gpt
 * @type {import('vue').Ref<'gpt' | 'deepseek'>}
 */
const selectedModel = ref<"gpt" | "deepseek">("gpt");

// 判断是否显示产品定位验证表单
const showProductValidationForm = computed(() => {
  return (
    props.role &&
    props.role.id === 34 &&
    messages.value.length === 0 &&
    !productValidationFormSubmitted.value
  );
});

// 添加产品定位验证表单提交状态
const productValidationFormSubmitted = ref(false);

// 处理产品定位验证表单提交
const handleProductValidationFormSubmit = async (payload: {
  formData: any;
  formattedContent: string;
}) => {
  // 设置输入消息为格式化后的表单内容
  inputMessage.value = payload.formattedContent;

  // 设置表单已提交状态
  productValidationFormSubmitted.value = true;

  // 调用发送消息函数
  await handleSend();
};
</script>
