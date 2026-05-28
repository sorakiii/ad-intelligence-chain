<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Logo部分 -->
      <div class="logo-section">
        <div class="logo">AI</div>
        <h1 class="brand">AI广告智链</h1>
      </div>

      <!-- 登录方式切换 -->
      <div class="login-tabs">
        <span
          :class="['tab', activeTab === 'code' ? 'active' : '']"
          @click="activeTab = 'code'"
        >
          验证码登录
        </span>
        <span
          :class="['tab', activeTab === 'password' ? 'active' : '']"
          @click="activeTab = 'password'"
        >
          密码登录
        </span>
      </div>

      <!-- 提示文本 -->
      <div class="login-tip">您所在地区仅支持 手机号 / 微信 登录</div>

      <!-- 登录表单 -->
      <div class="login-form">
        <!-- 验证码登录 -->
        <template v-if="activeTab === 'code'">
          <!-- 手机号输入 -->
          <div class="form-item phone-input-wrapper">
            <div class="phone-input">
              <div class="country-code">+86</div>
              <el-input
                v-model="form.phone"
                placeholder="请输入手机号"
                class="phone-number"
                maxlength="11"
              />
            </div>
          </div>
          <div class="form-item verification-code">
            <el-input
              v-model="form.code"
              placeholder="请输入验证码"
              class="code-input"
              maxlength="6"
            />
            <el-button
              class="send-code-btn"
              :disabled="countdown > 0"
              @click="showCaptcha = true"
            >
              {{ countdown > 0 ? `${countdown}s后重新发送` : "发送验证码" }}
            </el-button>
          </div>
        </template>

        <!-- 密码登录 -->
        <template v-if="activeTab === 'password'">
          <div class="form-item">
            <div class="input-wrapper">
              <i class="input-icon phone-icon"></i>
              <el-input
                v-model="form.phone"
                placeholder="请输入手机号"
                maxlength="11"
              />
            </div>
          </div>
          <div class="form-item">
            <div class="input-wrapper">
              <i class="input-icon password-icon"></i>
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                show-password
                maxlength="20"
              />
            </div>
          </div>
          <div class="form-options">
            <a @click="router.push('/reset-password')" class="text-link"
              >忘记密码</a
            >
            <a @click="router.push('/register')" class="text-link">立即注册</a>
          </div>
        </template>

        <!-- 同意条款 -->
        <div class="agreement">
          <el-checkbox v-model="form.agreement">
            我已阅读并同意
            <a href="#" class="link">用户协议</a>
            与
            <a href="#" class="link">隐私政策</a>
          </el-checkbox>
        </div>

        <!-- 登录按钮 -->
        <el-button
          type="primary"
          class="login-button"
          :loading="loading"
          @click="handleLogin"
        >
          登录
        </el-button>

        <!-- 分割线 -->
        <div class="divider">
          <span>或</span>
        </div>

        <!-- 微信登录 -->
        <div class="wechat-login">
          <button class="wechat-btn">
            <img
              src="@/assets/icons/wechat.svg"
              class="wechat-icon"
              alt="微信图标"
            />
            使用微信登录
          </button>
        </div>
      </div>
    </div>

    <!-- 修改图形验证码弹窗 -->
    <el-dialog
      v-model="showCaptcha"
      title="安全验证"
      width="400px"
      :show-close="false"
      :close-on-click-modal="true"
      @close="handleDialogClose"
      class="captcha-dialog"
      destroy-on-close
    >
      <div class="captcha-content">
        <p class="captcha-tip">请滑动滑块完成验证</p>
        <slider-captcha
          ref="sliderCaptchaRef"
          @verified="handleCaptchaVerified"
        />
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCancel">取消</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #fff;
}

.login-container {
  width: 400px;
  padding: 40px;
  background: white;
}

.logo-section {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  width: 40px;
  height: 40px;
  background: #4e6ef2;
  border-radius: 8px;
  color: white;
  font-size: 20px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.brand {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin-top: 12px;
}

.login-tabs {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 24px;
  position: relative;
}

.tab {
  font-size: 16px;
  color: #666;
  cursor: pointer;
  padding: 4px 0;
  position: relative;
}

.tab.active {
  color: #1a1a1a;
  font-weight: 500;
}

.tab.active::after {
  content: "";
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #4e6ef2;
  border-radius: 1px;
}

.login-tip {
  text-align: center;
  color: #666;
  font-size: 14px;
  margin-bottom: 24px;
}

.form-item {
  margin-bottom: 16px;
}

.phone-input-wrapper {
  margin-bottom: 16px;
}

.phone-input {
  display: flex;
  align-items: center;
  border: 1px solid #dcdfe6;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  background: #fff;
  height: 48px;
}

.phone-input:hover {
  border-color: #4e6ef2;
}

.phone-input:focus-within {
  border-color: #4e6ef2;
  box-shadow: 0 0 0 1px rgba(78, 110, 242, 0.1);
}

.country-code {
  padding: 0 16px;
  color: #1a1a1a;
  font-size: 15px;
  border-right: 1px solid #ebeef5;
  height: 100%;
  line-height: 48px;
  background: #fff;
  font-weight: 500;
}

.phone-number {
  flex: 1;
}

.phone-number :deep(.el-input__wrapper) {
  box-shadow: none !important;
  padding: 0 16px;
  border: none;
  height: 48px;
  background: transparent;
}

.verification-code {
  display: flex;
  gap: 12px;
}

.code-input :deep(.el-input__wrapper) {
  height: 48px;
  border-radius: 12px;
  border: 1px solid #dcdfe6;
}

.send-code-btn {
  width: 120px;
  height: 48px;
  border: 1px solid #4e6ef2;
  color: #4e6ef2;
  background: transparent;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
}

.send-code-btn:hover {
  background: rgba(78, 110, 242, 0.05);
}

.send-code-btn:disabled {
  border-color: #dcdfe6;
  color: #999;
  cursor: not-allowed;
}

.agreement {
  margin: 24px 0;
  font-size: 14px;
}

.link {
  color: #4e6ef2;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  border-radius: 12px;
  background: #4e6ef2;
  border: none;
  transition: all 0.3s;
  font-weight: 500;
}

.login-button:hover {
  background: #4058d9;
}

.divider {
  display: flex;
  align-items: center;
  color: #999;
  margin: 24px 0;
}

.divider::before,
.divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: #eee;
}

.divider span {
  padding: 0 16px;
}

.wechat-login {
  text-align: center;
}

.wechat-btn {
  width: 100%;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 12px;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.wechat-btn:hover {
  border-color: #07c160;
  color: #07c160;
  background: rgba(7, 193, 96, 0.05);
}

.wechat-icon {
  width: 20px;
  height: 20px;
}

/* 输入框样式优化 */
:deep(.el-input__wrapper) {
  box-shadow: none !important;
  border: 1px solid #dcdfe6;
  border-radius: 12px;
  height: 48px;
  transition: all 0.3s;
  padding: 0 16px;
}

:deep(.el-input__wrapper:hover) {
  border-color: #4e6ef2;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #4e6ef2;
  box-shadow: 0 0 0 1px rgba(78, 110, 242, 0.1) !important;
}

/* 按钮样式优化 */
:deep(.el-button) {
  border-radius: 8px;
  transition: all 0.3s;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #4e6ef2;
  border-color: #4e6ef2;
}

:deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #666;
}

.input-wrapper {
  position: relative;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  z-index: 1;
  background-size: contain;
  background-repeat: no-repeat;
}

.phone-icon {
  background-image: url("@/assets/icons/phone.svg");
}

.password-icon {
  background-image: url("@/assets/icons/password.svg");
}

.input-wrapper :deep(.el-input__wrapper) {
  padding-left: 44px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  margin: -8px 0 16px;
  padding: 0 4px;
}

.text-link {
  color: #4e6ef2;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.3s;
}

.text-link:hover {
  color: #4058d9;
  text-decoration: underline;
}

/* 修改密码框的眼睛图标位置 */
:deep(.el-input__suffix) {
  right: 12px;
}

:deep(.el-input__password) {
  color: #999;
}

:deep(.el-input__password:hover) {
  color: #4e6ef2;
}

/* 图形验证码弹窗样式 */
.captcha-dialog {
  --el-dialog-padding-primary: 20px;
}

:deep(.el-dialog__header) {
  margin-right: 0;
  padding: 20px 20px 10px;
  text-align: center;
}

.captcha-content {
  padding: 0 20px;
}

.captcha-tip {
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
  text-align: center;
}

:deep(.el-dialog__footer) {
  padding: 10px 20px 20px;
  text-align: center;
}

.dialog-footer {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.dialog-footer .el-button {
  min-width: 100px;
}
</style>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import request from "@/utils/request";
import authApi from "@/api/auth";
import { ChatDotRound } from "@element-plus/icons-vue";
import SliderCaptcha from "@/components/auth/SliderCaptcha.vue";
import { useUserStore } from "@/stores/user";

const router = useRouter();
const route = useRoute();
const loading = ref(false);
const countdown = ref(0);
const activeTab = ref(route.query.tab || "code");

const showCaptcha = ref(false);
const captchaValue = ref("");
const captchaVerified = ref(false);

const userStore = useUserStore();

const sliderCaptchaRef = ref(null);

// 监听路由变化
onMounted(() => {
  if (route.query.tab) {
    activeTab.value = route.query.tab;
  }
});

const form = reactive({
  phone: "",
  code: "",
  password: "",
  agreement: false,
});

// 修改处理图形验证码验证结果函数
const handleCaptchaVerified = (verified) => {
  if (verified) {
    // 自动勾选用户协议
    if (form.agreement !== undefined) {
      form.agreement = true;
    }

    captchaVerified.value = true;
    showCaptcha.value = false;
    sendCode();
  } else {
    ElMessage.error("验证失败，请重试");
  }
};

// 检查发送验证码前的必填项
const checkRequiredFields = () => {
  if (!form.phone) {
    ElMessage.warning("请输入手机号");
    return false;
  }

  if (!/^1[3-9]\d{9}$/.test(form.phone)) {
    ElMessage.warning("请输入正确的手机号");
    return false;
  }

  if (!form.agreement) {
    ElMessage.warning("请先阅读并同意用户协议和隐私政策");
    return false;
  }

  return true;
};

// 修改发送验证码函数
const sendCode = async () => {
  // 自动勾选用户协议
  if (form.agreement !== undefined) {
    form.agreement = true;
  }

  if (!checkRequiredFields()) {
    captchaVerified.value = false;
    return;
  }

  if (!captchaVerified.value) {
    showCaptcha.value = true;
    return;
  }

  try {
    await authApi.sendCode(form.phone, "login");
    ElMessage.success("验证码已发送");
    countdown.value = 60;
    const timer = setInterval(() => {
      countdown.value--;
      if (countdown.value <= 0) {
        clearInterval(timer);
        captchaVerified.value = false; // 倒计时结束后重置验证状态
      }
    }, 1000);
  } catch (error) {
    console.error("发送验证码失败:", error);
    captchaVerified.value = false; // 发送失败时重置验证状态
  }
};

// 处理登录
const handleLogin = async () => {
  if (!form.agreement) {
    ElMessage.warning("请先同意用户协议和隐私政策");
    return;
  }

  if (!form.phone) {
    ElMessage.warning("请输入手机号");
    return;
  }

  if (!/^1[3-9]\d{9}$/.test(form.phone)) {
    ElMessage.warning("请输入正确的手机号");
    return;
  }

  const loginData = {
    phone: form.phone,
  };

  // 根据登录方式添加不同参数
  if (activeTab.value === "code") {
    if (!form.code) {
      ElMessage.warning("请输入验证码");
      return;
    }
    loginData.code = form.code;
  } else {
    if (!form.password) {
      ElMessage.warning("请输入密码");
      return;
    }
    loginData.password = form.password;
  }

  loading.value = true;
  try {
    const res = await authApi.login(loginData);
    handleLoginSuccess(res);
  } catch (error) {
    console.error("登录失败:", error);
  } finally {
    loading.value = false;
  }
};

// 处理登录成功
const handleLoginSuccess = (res) => {
  const token = res.data.access_token;
  const { role_id, expired_at } = res.data.user;
  localStorage.setItem("token", token);
  // 使用 store 登录方法
  userStore.login(token, res.data.user || {});
  ElMessage.success("登录成功");
  let defaultUrl = "/workspace/single-role";
  const timestampInSeconds = Math.floor(Date.now() / 1000);
  if (role_id === -1 && expired_at < timestampInSeconds) {
    defaultUrl = "/?allowReturn=false";
  }
  // 检查是否有重定向URL
  const redirectUrl = route.query.redirect || defaultUrl;
  router.push(redirectUrl);
};

// 处理弹窗关闭
const handleDialogClose = () => {
  captchaValue.value = "";
  captchaVerified.value = false;
};

// 处理取消按钮点击
const handleCancel = () => {
  showCaptcha.value = false;
  handleDialogClose();
};
</script> 