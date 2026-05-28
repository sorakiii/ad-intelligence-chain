<template>
  <div class="settings-page">
    <div class="settings-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">系统设置</h1>
        <p class="page-description">管理你的账号设置和偏好</p>
      </div>

      <!-- 设置内容区 -->
      <div class="settings-content">
        <!-- 个人信息设置 -->
        <div class="settings-section">
          <h2 class="section-title">个人信息</h2>
          <div class="section-content">
            <div class="form-item">
              <label>头像</label>
              <div class="avatar-upload">
                <el-avatar :size="64" :src="userInfo.avatar" />
                <el-button class="upload-btn">更换头像</el-button>
              </div>
            </div>
            <div class="form-item">
              <label>昵称</label>
              <el-input v-model="userInfo.nickname" placeholder="请输入昵称" />
            </div>
            <div class="form-item">
              <label>个人简介</label>
              <el-input
                v-model="userInfo.bio"
                type="textarea"
                :rows="3"
                placeholder="请输入个人简介"
                maxlength="200"
                show-word-limit
              />
            </div>
          </div>
        </div>

        <!-- 账号安全设置 -->
        <div class="settings-section">
          <h2 class="section-title">账号安全</h2>
          <div class="section-content">
            <div class="security-item">
              <div class="item-info">
                <div class="item-title">登录密码</div>
                <div class="item-desc">用于保护账号安全</div>
              </div>
              <el-button link type="primary" @click="handleChangePassword">修改</el-button>
            </div>
            <div class="security-item">
              <div class="item-info">
                <div class="item-title">手机号码</div>
                <div class="item-desc">已绑定：{{ userInfo.phone }}</div>
              </div>
              <el-button link type="primary" @click="handleChangePhone">更换</el-button>
            </div>
            <div class="security-item">
              <div class="item-info">
                <div class="item-title">邮箱地址</div>
                <div class="item-desc">{{ userInfo.email ? `已绑定：${userInfo.email}` : '未绑定' }}</div>
              </div>
              <el-button link type="primary" @click="handleChangeEmail">
                {{ userInfo.email ? '更换' : '绑定' }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- 通知设置 -->
        <div class="settings-section">
          <h2 class="section-title">通知设置</h2>
          <div class="section-content">
            <div class="notification-item">
              <div class="item-info">
                <div class="item-title">系统通知</div>
                <div class="item-desc">接收系统更新、维护等重要通知</div>
              </div>
              <el-switch v-model="notifications.system" />
            </div>
            <div class="notification-item">
              <div class="item-info">
                <div class="item-title">任务通知</div>
                <div class="item-desc">接收任务进度、完成等相关通知</div>
              </div>
              <el-switch v-model="notifications.task" />
            </div>
            <div class="notification-item">
              <div class="item-info">
                <div class="item-title">营销通知</div>
                <div class="item-desc">接收新功能、优惠活动等营销信息</div>
              </div>
              <el-switch v-model="notifications.marketing" />
            </div>
          </div>
        </div>

        <!-- 主题外观 -->
        <div class="settings-section">
          <h2 class="section-title">主题外观</h2>
          <div class="section-content">
            <div class="theme-item">
              <label>主题模式</label>
              <el-radio-group v-model="appearance.theme">
                <el-radio-button label="light">浅色</el-radio-button>
                <el-radio-button label="dark">深色</el-radio-button>
                <el-radio-button label="system">跟随系统</el-radio-button>
              </el-radio-group>
            </div>
            <div class="theme-item">
              <label>主题色</label>
              <el-color-picker v-model="appearance.primaryColor" />
            </div>
          </div>
        </div>

        <!-- 语言设置 -->
        <div class="settings-section">
          <h2 class="section-title">语言设置</h2>
          <div class="section-content">
            <div class="language-item">
              <label>显示语言</label>
              <el-select v-model="language" class="language-select">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
                <el-option label="日本語" value="ja-JP" />
              </el-select>
            </div>
          </div>
        </div>

        <!-- 保存按钮 -->
        <div class="settings-footer">
          <el-button type="primary" :loading="saving" @click="handleSave">保存更改</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

// 用户信息
const userInfo = reactive({
  avatar: '',
  nickname: '',
  bio: '',
  phone: '138****8888',
  email: 'example@email.com'
})

// 通知设置
const notifications = reactive({
  system: true,
  task: true,
  marketing: false
})

// 主题外观
const appearance = reactive({
  theme: 'light',
  primaryColor: '#4e6ef2'
})

// 语言设置
const language = ref('zh-CN')

// 保存状态
const saving = ref(false)

// 修改密码
const handleChangePassword = () => {
  // TODO: 实现修改密码逻辑
}

// 更换手机号
const handleChangePhone = () => {
  // TODO: 实现更换手机号逻辑
}

// 更换邮箱
const handleChangeEmail = () => {
  // TODO: 实现更换邮箱逻辑
}

// 保存设置
const handleSave = async () => {
  saving.value = true
  try {
    // TODO: 实现保存设置逻辑
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('设置已保存')
  } catch (error) {
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: var(--bg-color);
  padding: 40px;
}

.settings-container {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 40px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 8px;
}

.page-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.settings-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.section-title {
  font-size: 18px;
  font-weight: 500;
  color: var(--text-color);
  margin: 0 0 20px;
}

.form-item {
  margin-bottom: 24px;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-item label {
  display: block;
  font-size: 14px;
  color: var(--text-color);
  margin-bottom: 8px;
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.upload-btn {
  height: 32px;
}

.security-item,
.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
}

.security-item:last-child,
.notification-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.security-item:first-child,
.notification-item:first-child {
  padding-top: 0;
}

.item-info {
  flex: 1;
}

.item-title {
  font-size: 14px;
  color: var(--text-color);
  margin-bottom: 4px;
}

.item-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.theme-item {
  margin-bottom: 20px;
}

.theme-item:last-child {
  margin-bottom: 0;
}

.theme-item label {
  display: block;
  font-size: 14px;
  color: var(--text-color);
  margin-bottom: 8px;
}

.language-item {
  display: flex;
  align-items: center;
}

.language-item label {
  font-size: 14px;
  color: var(--text-color);
  margin-right: 16px;
  white-space: nowrap;
}

.language-select {
  width: 200px;
}

.settings-footer {
  margin-top: 40px;
  text-align: center;
}

:deep(.el-input__wrapper),
:deep(.el-textarea__wrapper) {
  border-radius: 8px;
}

:deep(.el-radio-button__inner) {
  padding: 8px 20px;
}

:deep(.el-switch) {
  --el-switch-on-color: #4e6ef2;
}
</style> 