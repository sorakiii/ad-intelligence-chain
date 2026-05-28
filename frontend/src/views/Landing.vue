<template>
  <div class="landing-page">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="nav-logo">AI广告智链</div>
      <div class="nav-menu">
        <a href="#features">产品特性</a>
        <a href="#workflow">工作流程</a>
        <a href="#pricing">价格方案</a>
        <a href="#about">关于我们</a>
      </div>
      <div class="nav-buttons">
        <button class="button button-secondary" @click="handleButtonClick">
          {{ isLoggedIn ? "进入工作台" : "登录" }}
        </button>
        <button
          v-if="isLoggedIn"
          class="button button-secondary"
          @click="logout"
        >
          退出登录
        </button>
      </div>
    </nav>

    <!-- 英雄区域 -->
    <section class="hero">
      <h1 class="hero-title">AI驱动的广告服务新范式</h1>
      <p class="hero-subtitle">
        整合AI超级战队，重塑广告服务流程，让创意更高效，让营销更智能
      </p>
      <button class="button button-primary" @click="handleButtonClick">
        {{ isLoggedIn ? "继续使用" : "立即体验" }}
      </button>
    </section>

    <!-- 特性区域 -->
    <section class="features" id="features">
      <h2 class="section-title">核心优势</h2>
      <p class="section-subtitle">
        通过AI技术重塑广告服务流程，让创意更高效，让营销更智能
      </p>
      <div class="features-grid">
        <feature-card
          v-for="feature in features"
          :key="feature.title"
          v-bind="feature"
          @click="handleButtonClick"
          class="clickable"
        />
      </div>
    </section>

    <!-- 工作流程 -->
    <section class="workflow" id="workflow">
      <h2 class="section-title">工作流程</h2>
      <div class="workflow-steps">
        <workflow-step
          v-for="(step, index) in workflowSteps"
          :key="index"
          :number="index + 1"
          v-bind="step"
        />
      </div>
    </section>

    <!-- 价格方案 -->
    <section class="pricing" id="pricing">
      <h2 class="section-title">价格方案</h2>
      <p class="section-subtitle">灵活的价格方案，满足不同规模企业需求</p>
      <div class="pricing-grid">
        <div class="pricing-card">
          <div class="plan-name">基础版</div>
          <div class="plan-price">
            <span class="currency">¥</span>
            <span class="amount">299</span>
            <span class="period">/月</span>
          </div>
          <div class="plan-features">
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>单角色对话无限制</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>基础AI模型支持</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>基础文件上传(10MB/个)</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>标准客户支持</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>专业版-试用3天</span>
            </div>
          </div>
          <button class="plan-button" @click="handleButtonClick">
            {{ isLoggedIn ? "继续使用" : "开始使用" }}
          </button>
        </div>

        <div class="pricing-card popular">
          <div class="popular-badge">最受欢迎</div>
          <div class="plan-name">专业版</div>
          <div class="plan-price">
            <span class="currency">¥</span>
            <span class="amount">899</span>
            <span class="period">/月</span>
          </div>
          <div class="plan-features">
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>超级战队全角色支持</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>高级AI模型支持</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>高级文件处理(50MB/个)</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>优先客户支持</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>数据分析功能</span>
            </div>
          </div>
          <button class="plan-button primary" @click="handleButtonClick">
            {{ isLoggedIn ? "继续使用" : "免费试用" }}
          </button>
        </div>

        <div class="pricing-card">
          <div class="plan-name">企业版</div>
          <div class="plan-price">
            <div class="enterprise-text">联系我们</div>
            <div class="enterprise-desc">定制化方案</div>
          </div>
          <div class="plan-features">
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>专属定制AI模型</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>无限制文件处理</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>专属客户成功经理</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>API集成支持</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">✓</span>
              <span>SLA保障</span>
            </div>
          </div>
          <button class="plan-button" @click="handleEnterpriseClick">
            联系我们
          </button>
        </div>
      </div>
    </section>

    <!-- 关于我们 -->
    <section class="about" id="about">
      <h2 class="section-title">关于我们</h2>
      <p class="section-subtitle">用AI重新定义广告服务的未来</p>
      <div class="about-grid">
        <div class="about-card">
          <div class="about-icon">🎯</div>
          <h3 class="about-title">使命</h3>
          <p class="about-desc">
            让每个企业都能享受到高质量、高效率的AI驱动广告服务，
            助力企业实现营销目标。
          </p>
        </div>
        <div class="about-card">
          <div class="about-icon">👁️</div>
          <h3 class="about-title">愿景</h3>
          <p class="about-desc">
            成为全球领先的AI广告服务平台，引领行业创新，
            为广告营销领域带来革命性变革。
          </p>
        </div>
        <div class="about-card">
          <div class="about-icon">💎</div>
          <h3 class="about-title">价值观</h3>
          <p class="about-desc">
            创新、专业、高效、共赢。始终以客户需求为中心， 持续创新技术与服务。
          </p>
        </div>
      </div>
      <div class="company-stats">
        <div class="stat-item">
          <div class="stat-number">10000+</div>
          <div class="stat-label">服务客户</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">100万+</div>
          <div class="stat-label">生成创意</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">99%</div>
          <div class="stat-label">客户满意度</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">24/7</div>
          <div class="stat-label">全天候服务</div>
        </div>
      </div>
    </section>

    <!-- CTA区域 -->
    <section class="cta">
      <h2 class="cta-title">开启您的AI广告服务之旅</h2>
      <p class="cta-subtitle">立即体验AI超级战队带来的革新性广告服务体验</p>
    </section>

    <!-- 添加联系表单弹窗 -->
    <el-dialog
      v-model="showContactForm"
      :show-close="false"
      width="560px"
      :close-on-click-modal="true"
      destroy-on-close
      class="contact-dialog"
    >
      <div class="dialog-header">
        <h3>开启企业定制服务</h3>
        <p>
          填写以下信息，我们将安排专属顾问与您联系 (<span class="required"
            >*</span
          >为必填项)
        </p>
      </div>
      <el-form
        ref="contactFormRef"
        :model="contactForm"
        :rules="contactRules"
        label-width="70px"
        @submit.prevent="handleSubmit"
        class="contact-form"
      >
        <el-form-item label="姓名" prop="name" required>
          <el-input v-model="contactForm.name" placeholder="请输入您的姓名">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="手机" prop="phone" required>
          <el-input v-model="contactForm.phone" placeholder="请输入联系电话">
            <template #prefix>
              <el-icon><Phone /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="公司" prop="company">
          <el-input
            v-model="contactForm.company"
            placeholder="请输入公司名称（选填）"
          >
            <template #prefix>
              <el-icon><OfficeBuilding /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <div class="form-grid">
          <el-form-item label="职位" prop="position" label-width="70px">
            <el-input v-model="contactForm.position" placeholder="选填">
              <template #prefix>
                <el-icon><Briefcase /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="邮箱" prop="email" label-width="70px">
            <el-input v-model="contactForm.email" placeholder="选填">
              <template #prefix>
                <el-icon><Message /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </div>

        <el-form-item label="需求" prop="requirements" required>
          <el-input
            v-model="contactForm.requirements"
            type="textarea"
            :rows="4"
            placeholder="请简要描述您的需求"
            resize="none"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button
            plain
            @click="showContactForm = false"
            class="cancel-button"
          >
            取消
          </el-button>
          <el-button
            type="primary"
            @click="handleSubmit"
            :loading="submitting"
            class="submit-button"
          >
            提交需求
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch, computed } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import { ElMessage, ElLoading } from "element-plus";
import { ElButton, ElForm, ElFormItem, ElInput, ElDialog } from "element-plus";
import {
  User,
  Briefcase,
  OfficeBuilding,
  Phone,
  Message,
} from "@element-plus/icons-vue";
import request from "@/utils/request";
import FeatureCard from "@/components/landing/FeatureCard.vue";
import WorkflowStep from "@/components/landing/WorkflowStep.vue";

const router = useRouter();
const userStore = useUserStore();

const isLoggedIn = ref(false);

onMounted(() => {
  // 使用 store 中的登录状态
  isLoggedIn.value = userStore.isLoggedIn;
});

// 监听用户登录状态变化
watch(
  () => userStore.isLoggedIn,
  (newValue) => {
    isLoggedIn.value = newValue;
  }
);
const logout = () => {
  userStore.logout();
  router.push("/login");
};
// 统一处理所有按钮的点击事件
const handleButtonClick = async () => {
  console.log("按钮被点击");

  // 添加加载效果
  const loading = ElLoading.service({
    lock: true,
    text: "处理中...",
    background: "rgba(255, 255, 255, 0.7)",
  });

  try {
    // 从 localStorage 直接检查 token
    const token = localStorage.getItem("token");
    console.log("token 检查结果:", token ? "存在" : "不存在");

    if (token) {
      console.log("用户已登录，正在跳转到工作台...");
      router.push("/workspace/single-role");
    } else {
      console.log("用户未登录，正在跳转到登录页...");
      router.push("/login");
    }
  } catch (error) {
    console.error("处理按钮点击时出错:", error);
  } finally {
    // 关闭加载效果
    loading.close();
  }
};

// 功能特性数据
const features = ref([
  {
    icon: "🤖",
    title: "AI超级战队",
    description: "10个专业角色，覆盖广告服务全流程，智能协同作业",
    stats: [
      { icon: "👥", text: "10位专家" },
      { icon: "⚡️", text: "协同作业" },
    ],
  },
  {
    icon: "⚡️",
    title: "极速响应",
    description: "7×24小时实时响应，智能分配任务，快速交付",
    stats: [
      { icon: "⏱️", text: "24h响应" },
      { icon: "📈", text: "高效率" },
    ],
  },
  {
    icon: "🎯",
    title: "精准服务",
    description: "深度理解需求，个性化定制方案，确保精准需求",
    stats: [
      { icon: "🎯", text: "定制化" },
      { icon: "⭐️", text: "高满意" },
    ],
  },
  {
    icon: "🎨",
    title: "多维创意",
    description: "覆盖文案、视觉、视频等多维度创意输出",
    stats: [
      { icon: "🎨", text: "全方位" },
      { icon: "✨", text: "高品质" },
    ],
  },
  {
    icon: "📊",
    title: "数据驱动",
    description: "基于大数据分析，提供市场洞察和策略建议",
    stats: [
      { icon: "📈", text: "实时分析" },
      { icon: "🎯", text: "精准洞察" },
    ],
  },
  {
    icon: "🔄",
    title: "持续优化",
    description: "智能监测效果，持续迭代优化营销方案",
    stats: [
      { icon: "📊", text: "效果监测" },
      { icon: "⚡️", text: "快速迭代" },
    ],
  },
]);

// 工作流程数据
const workflowSteps = ref([
  {
    title: "提交需求",
    description: "描述您的广告需求，选择合适的服务类型",
  },
  {
    title: "组建战队",
    description: "AI智能匹配最佳角色组合，形成专属服务团队",
  },
  {
    title: "协同创作",
    description: "多角色协同工作，持续优化方案",
  },
  {
    title: "交付成果",
    description: "输出完整解决方案，提供持续优化服务",
  },
]);

// 联系表单相关
const showContactForm = ref(false);
const submitting = ref(false);
const contactFormRef = ref(null);

const contactForm = reactive({
  name: "",
  company: "",
  position: "",
  phone: "",
  email: "",
  requirements: "",
});

const contactRules = {
  name: [
    { required: true, message: "请输入姓名", trigger: "blur" },
    { min: 2, max: 20, message: "长度在 2 到 20 个字符", trigger: "blur" },
  ],
  phone: [
    { required: true, message: "请输入手机号码", trigger: "blur" },
    {
      pattern: /^1[3-9]\d{9}$/,
      message: "请输入正确的手机号码",
      trigger: "blur",
    },
  ],
  requirements: [
    { required: true, message: "请输入需求描述", trigger: "blur" },
    { min: 10, max: 500, message: "长度在 10 到 500 个字符", trigger: "blur" },
  ],
  company: [],
  position: [],
  email: [{ type: "email", message: "请输入正确的邮箱地址", trigger: "blur" }],
};

// 处理表单提交
const handleSubmit = async () => {
  if (!contactFormRef.value) return;

  try {
    await contactFormRef.value.validate();
    submitting.value = true;

    // 这里添加实际的表单提交逻辑
    // 模拟API调用
    await new Promise((resolve) => setTimeout(resolve, 1000));

    ElMessage.success("提交成功！我们的客户经理将尽快与您联系");
    showContactForm.value = false;

    // 重置表单
    contactFormRef.value.resetFields();
  } catch (error) {
    console.error("表单验证失败:", error);
    ElMessage.error("请检查表单填写是否正确");
  } finally {
    submitting.value = false;
  }
};

// 修改企业版按钮点击事件
const handleEnterpriseClick = () => {
  showContactForm.value = true;
};

// 优化滚动动画
onMounted(() => {
  const animateOnScroll = () => {
    const elements = document.querySelectorAll(".feature-card, .step");
    const workflowSteps = document.querySelector(".workflow-steps");

    elements.forEach((element) => {
      const elementTop = element.getBoundingClientRect().top;
      const elementBottom = element.getBoundingClientRect().bottom;

      if (elementTop < window.innerHeight * 0.8 && elementBottom > 0) {
        element.classList.add("visible");
      }
    });

    // 工作流程连接线动画
    if (workflowSteps) {
      const workflowTop = workflowSteps.getBoundingClientRect().top;
      if (workflowTop < window.innerHeight * 0.8) {
        workflowSteps.classList.add("visible");
      }
    }
  };

  window.addEventListener("scroll", animateOnScroll);
  // 初始化时执行一次
  setTimeout(animateOnScroll, 100);

  // 清理事件监听
  return () => window.removeEventListener("scroll", animateOnScroll);
});
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
}

/* 导航栏样式优化 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  padding: 0 40px;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.nav-logo {
  font-size: 22px;
  font-weight: 600;
  color: var(--primary-color);
  letter-spacing: -0.5px;
}

.nav-menu {
  margin-left: 40px;
  display: flex;
  gap: 32px;
}

.nav-menu a {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 15px;
  transition: color 0.2s ease;
  padding: 6px 12px;
  border-radius: 6px;
  position: relative;
}

.nav-buttons {
  margin-left: auto;
  display: flex;
  gap: 16px;
}

/* 按钮样式 */
.button {
  padding: 12px 28px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.button-primary {
  background: var(--gradient-primary);
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 102, 255, 0.2);
}

.button-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 102, 255, 0.3);
}

.button-secondary {
  background: white;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.button-secondary:hover {
  background: rgba(0, 102, 255, 0.05);
  transform: translateY(-1px);
}

.button-light {
  background: white;
  color: var(--primary-color);
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.button-light:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

/* 英雄区域动画 */
.hero {
  padding: 140px 40px 100px;
  background: var(--gradient-light);
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 20px;
  line-height: 1.2;
  letter-spacing: -0.5px;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  position: relative;
  z-index: 1;
}

.hero-subtitle {
  font-size: 18px;
  color: var(--text-secondary);
  max-width: 600px;
  margin: 0 auto 32px;
  position: relative;
  z-index: 1;
}

/* 工作流程连接线 */
.workflow-steps::before {
  content: "";
  position: absolute;
  top: 40px;
  left: 60px;
  right: 60px;
  height: 2px;
  background: linear-gradient(
    90deg,
    rgba(0, 102, 255, 0.1) 0%,
    rgba(0, 102, 255, 0.3) 50%,
    rgba(0, 102, 255, 0.1) 100%
  );
  z-index: 0;
}

/* CTA区域背景图案 */
.cta {
  background: var(--gradient-primary);
  padding: 80px 40px;
  text-align: center;
  color: white;
  position: relative;
  overflow: hidden;
}

.cta::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><circle cx="2" cy="2" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
  opacity: 0.3;
  animation: backgroundMove 20s linear infinite;
}

@keyframes backgroundMove {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 100px 100px;
  }
}

.cta-title {
  font-size: 36px;
  font-weight: 600;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.cta-subtitle {
  font-size: 18px;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto 40px;
  position: relative;
  z-index: 1;
}

/* 工作流程动画 */
.workflow {
  background: var(--bg-color);
  padding: 80px 40px;
  overflow: hidden;
}

.workflow-steps {
  display: flex;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  padding: 0 40px;
}

.workflow-steps::before {
  content: "";
  position: absolute;
  top: 40px;
  left: 60px;
  right: 60px;
  height: 2px;
  background: linear-gradient(
    90deg,
    rgba(0, 102, 255, 0.1) 0%,
    rgba(0, 102, 255, 0.3) 50%,
    rgba(0, 102, 255, 0.1) 100%
  );
  z-index: 0;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 1s cubic-bezier(0.4, 0, 0.2, 1);
}

.workflow-steps.visible::before {
  transform: scaleX(1);
}

/* 滚动动画 */
.feature-card,
.step {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.feature-card.visible,
.step.visible {
  opacity: 1;
  transform: translateY(0);
}

/* 添加延迟动画 */
.step:nth-child(2) {
  transition-delay: 0.2s;
}

.step:nth-child(3) {
  transition-delay: 0.4s;
}

.step:nth-child(4) {
  transition-delay: 0.6s;
}

/* 特性区域样式 */
.features {
  background: linear-gradient(180deg, #fff 0%, var(--bg-color) 100%);
  padding: 80px 0;
}

.section-title {
  font-size: 32px;
  text-align: center;
  margin-bottom: 12px;
}

.section-subtitle {
  text-align: center;
  color: var(--text-secondary);
  margin-bottom: 40px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
}

.feature-card {
  background: white;
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.feature-card.active,
.feature-card:focus {
  border: 1px solid var(--primary-color);
  outline: none;
}

@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 36px;
  }

  .workflow-steps {
    flex-direction: column;
    gap: 32px;
  }

  .nav-menu {
    display: none;
  }
}

/* 价格方案样式 */
.pricing {
  padding: 80px 40px;
  background: linear-gradient(180deg, var(--bg-color) 0%, #fff 100%);
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: 40px auto 0;
  padding: 0 20px;
}

.pricing-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  position: relative;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}

.pricing-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.pricing-card.popular {
  border: 2px solid var(--primary-color);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.popular-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--gradient-primary);
  color: white;
  padding: 4px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.plan-name {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
}

.plan-price {
  margin-bottom: 24px;
}

.currency {
  font-size: 24px;
  font-weight: 500;
  vertical-align: top;
}

.amount {
  font-size: 48px;
  font-weight: 700;
  line-height: 1;
}

.period {
  font-size: 16px;
  color: var(--text-secondary);
}

.enterprise-text {
  font-size: 24px;
  font-weight: 600;
  color: var(--primary-color);
}

.enterprise-desc {
  font-size: 16px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.plan-features {
  text-align: left;
  margin-bottom: 32px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  font-size: 15px;
}

.feature-icon {
  color: var(--primary-color);
  font-weight: bold;
}

.plan-button {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid var(--primary-color);
  background: white;
  color: var(--primary-color);
}

.plan-button:hover {
  background: rgba(0, 102, 255, 0.05);
}

.plan-button.primary {
  background: var(--gradient-primary);
  color: white;
  border: none;
}

.plan-button.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 102, 255, 0.2);
}

/* 关于我们样式 */
.about {
  padding: 80px 40px;
  background: white;
}

.about-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
}

.about-card {
  text-align: center;
  padding: 32px;
  background: var(--bg-color);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.about-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.about-icon {
  font-size: 40px;
  margin-bottom: 20px;
}

.about-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
}

.about-desc {
  color: var(--text-secondary);
  line-height: 1.6;
}

.company-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: 60px auto 0;
  padding: 0 20px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .pricing-grid,
  .about-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .company-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .pricing-grid,
  .about-grid,
  .company-stats {
    grid-template-columns: 1fr;
  }

  .pricing,
  .about {
    padding: 60px 20px;
  }
}

/* 联系表单弹窗样式优化 */
.contact-dialog {
  --dialog-margin-top: 8vh;
}

:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.dialog-header {
  background: linear-gradient(
    135deg,
    var(--el-color-primary-light-5) 0%,
    var(--el-color-primary) 100%
  );
  padding: 32px 40px;
  color: white;
  margin-bottom: 24px;
}

.dialog-header h3 {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.dialog-header p {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
}

.required {
  color: #ff4949;
  margin: 0 2px;
}

.contact-form {
  padding: 0 40px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  box-shadow: none !important;
  border: 1px solid var(--el-border-color);
  transition: all 0.3s ease;
  background: #f8fafc;
}

:deep(.el-input__wrapper:hover),
:deep(.el-textarea__inner:hover) {
  border-color: var(--el-color-primary-light-3);
  background: white;
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-textarea__inner:focus) {
  border-color: var(--el-color-primary);
  background: white;
}

:deep(.el-input__inner) {
  height: 40px;
  line-height: 40px;
}

:deep(.el-input__prefix-inner) {
  font-size: 16px;
  color: var(--el-text-color-secondary);
}

:deep(.el-dialog__footer) {
  padding: 20px 40px 10px;
  border-top: 1px solid var(--el-border-color-light);
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.cancel-button {
  min-width: 100px;
}

.submit-button {
  min-width: 120px;
  background: var(--gradient-primary);
  border: none;
  font-weight: 500;
}

.submit-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 102, 255, 0.2);
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
    gap: 0;
  }

  :deep(.el-dialog) {
    width: 90% !important;
    margin: 5vh auto !important;
  }

  .dialog-header {
    padding: 24px 20px;
  }

  .contact-form {
    padding: 0 20px;
  }

  :deep(.el-dialog__footer) {
    padding: 20px;
  }
}

/* 移除所有元素的触摸高亮效果 */
* {
  -webkit-tap-highlight-color: transparent;
  outline: none;
}

/* 确保可点击元素在触摸时没有蓝边 */
button,
a {
  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
  outline: none;
}

/* 如果需要保持可访问性，可以添加自定义的焦点样式 */
button:focus-visible,
a:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}

/* 添加鼠标指针样式和过渡效果 */
.clickable {
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.clickable:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}
</style> 