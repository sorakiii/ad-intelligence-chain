<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Logo部分 -->
      <div class="logo-section">
        <div class="logo">AI</div>
        <h1 class="brand">AI广告智链</h1>
      </div>

      <h2 class="page-title">注册账号</h2>
      <!-- <p class="page-subtitle">
        只需一个DeepSeek账号，即可访问DeepSeek的所有服务。
      </p> -->

      <!-- 表单部分 -->
      <div class="form">
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

        <!-- 验证码 -->
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

        <!-- 密码 -->
        <div class="form-item">
          <div class="input-wrapper">
            <i class="input-icon password-icon"></i>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请设置密码"
              show-password
              maxlength="20"
            />
          </div>
          <div class="password-tip">密码长度为8-20个字符</div>
        </div>

        <!-- 确认密码 -->
        <div class="form-item">
          <div class="input-wrapper">
            <i class="input-icon password-icon"></i>
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="请确认密码"
              show-password
              maxlength="20"
            />
          </div>
        </div>

        <!-- 用途选择 -->
        <div class="usage-section">
          <div class="usage-title">使用目的（可多选）</div>
          <div class="usage-options">
            <el-checkbox v-model="form.usage_purposes" label="商业办公"
              >商业办公</el-checkbox
            >
            <el-checkbox v-model="form.usage_purposes" label="科学研究"
              >科学研究</el-checkbox
            >
            <el-checkbox v-model="form.usage_purposes" label="兴趣娱乐"
              >兴趣娱乐</el-checkbox
            >
            <el-checkbox v-model="form.usage_purposes" label="其他"
              >其他</el-checkbox
            >
          </div>
        </div>

        <!-- 同意条款 -->
        <div class="agreement">
          <el-checkbox v-model="form.agreement">
            我已阅读并同意
            <a href="#" class="link">《用户协议》</a>
            与
            <a href="#" class="link">《隐私政策》</a>
          </el-checkbox>
        </div>

        <!-- 注册按钮 -->
        <el-button
          type="primary"
          class="submit-button"
          :loading="loading"
          @click="handleSubmit"
        >
          注册
        </el-button>

        <!-- 返回登录 -->
        <div class="back-to-login">
          <span class="tip">已有账号？</span>
          <a @click="backToLogin" class="text-link">返回登录</a>
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

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import authApi from "@/api/auth";
import SliderCaptcha from "@/components/auth/SliderCaptcha.vue";

const router = useRouter();
const loading = ref(false);
const countdown = ref(0);

const form = reactive({
  phone: "",
  code: "",
  password: "",
  confirmPassword: "",
  usage_purposes: [], // 修改字段名以匹配后端API
  agreement: false,
});

const showCaptcha = ref(false);
const captchaValue = ref("");
const captchaVerified = ref(false);
const sliderCaptchaRef = ref(null);

// 修改处理图形验证码验证结果函数
const handleCaptchaVerified = (verified) => {
  if (verified) {
    // 自动勾选用户协议
    form.agreement = true;

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
  form.agreement = true;

  if (!checkRequiredFields()) {
    captchaVerified.value = false;
    return;
  }

  if (!captchaVerified.value) {
    showCaptcha.value = true;
    return;
  }

  try {
    await authApi.sendCode(form.phone, "register");
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

// 提交注册
const handleSubmit = async () => {
  if (!form.phone || !form.code || !form.password || !form.confirmPassword) {
    ElMessage.warning("请填写完整信息");
    return;
  }

  if (!/^1[3-9]\d{9}$/.test(form.phone)) {
    ElMessage.warning("请输入正确的手机号");
    return;
  }

  if (form.password.length < 8 || form.password.length > 20) {
    ElMessage.warning("密码长度应为8-20个字符");
    return;
  }

  if (form.password !== form.confirmPassword) {
    ElMessage.warning("两次输入的密码不一致");
    return;
  }

  if (form.usage_purposes.length === 0) {
    ElMessage.warning("请选择使用用途");
    return;
  }

  if (!form.agreement) {
    ElMessage.warning("请阅读并同意用户协议和隐私政策");
    return;
  }

  loading.value = true;
  try {
    const res = await authApi.register({
      phone: form.phone,
      code: form.code,
      password: form.password,
      usage_purposes: form.usage_purposes,
    });

    // 保存token
    localStorage.setItem("token", res.data.access_token);
    ElMessage.success("注册成功");
    router.push("/?allowReturn=false");
  } catch (error) {
    console.error("注册失败:", error);
  } finally {
    loading.value = false;
  }
};

// 返回登录页面并显示密码登录
const backToLogin = () => {
  router.push({
    path: "/login",
    query: { tab: "password" }, // 添加查询参数
  });
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

.page-title {
  font-size: 24px;
  font-weight: 500;
  color: #1a1a1a;
  text-align: center;
  margin: 24px 0 12px;
}

.page-subtitle {
  font-size: 14px;
  color: #666;
  text-align: center;
  margin-bottom: 32px;
  line-height: 1.5;
}

.form-item {
  margin-bottom: 24px;
  position: relative;
}

.phone-input-wrapper {
  margin-bottom: 24px;
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

.password-icon {
  background-image: url("@/assets/icons/password.svg");
}

.input-wrapper :deep(.el-input__wrapper) {
  padding-left: 44px;
  height: 48px;
  border-radius: 12px;
}

.usage-section {
  margin: 24px 0;
}

.usage-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 16px;
}

.usage-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.usage-options :deep(.el-checkbox__label) {
  color: #1a1a1a;
}

.agreement {
  margin: 24px 0;
  font-size: 14px;
  color: #666;
}

.link {
  color: #4e6ef2;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.submit-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  border-radius: 12px;
  background: #4e6ef2;
  border: none;
  transition: all 0.3s;
  font-weight: 500;
}

.submit-button:hover {
  background: #4058d9;
}

.back-to-login {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
}

.text-link {
  color: #4e6ef2;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.3s;
  cursor: pointer;
}

.text-link:hover {
  color: #4058d9;
  text-decoration: underline;
}

.tip {
  color: #666;
  margin-right: 4px;
}

/* Element Plus 组件样式覆盖 */
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #4e6ef2;
  border-color: #4e6ef2;
}

:deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #666;
}

:deep(.el-input__wrapper) {
  box-shadow: none !important;
  border: 1px solid #dcdfe6;
  transition: all 0.3s;
}

:deep(.el-input__wrapper:hover) {
  border-color: #4e6ef2;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #4e6ef2;
  box-shadow: 0 0 0 1px rgba(78, 110, 242, 0.1) !important;
}

:deep(.el-input__suffix) {
  right: 12px;
}

:deep(.el-input__password) {
  color: #999;
}

:deep(.el-input__password:hover) {
  color: #4e6ef2;
}

.password-tip {
  position: absolute;
  left: 0;
  bottom: -20px;
  font-size: 12px;
  color: #999;
}

:deep(.el-input__inner::placeholder) {
  color: #999;
  font-size: 14px;
}

:deep(.el-checkbox__inner) {
  border-radius: 4px;
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