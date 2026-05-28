<!--
  @file 传播策略框架表单组件
  @description 用于收集传播策略相关信息的表单组件
-->
<template>
  <div class="strategy-form-container">
    <div class="strategy-form">
      <h2 class="form-title">传播策略框架信息收集</h2>
      <p class="form-description">
        请填写以下信息，帮助我们更好地为您制定传播策略
      </p>

      <div class="form-section">
        <h3 class="section-title">一、品牌信息</h3>
        <div class="form-item">
          <label>品牌名称/背景<span class="required">*</span></label>
          <textarea
            v-model="formData.brandInfo.background"
            placeholder="简述品牌起源、发展历程或核心理念等"
            rows="3"
            required
            @input="adjustFormTextareaHeight"
            @keydown.enter.ctrl.exact.prevent="
              handleFormNewLine($event, 'brandInfo.background')
            "
            ref="formTextareaRefs"
          ></textarea>
        </div>
        <div class="form-item">
          <label>品牌定位/调性<span class="required">*</span></label>
          <textarea
            v-model="formData.brandInfo.positioning"
            placeholder="明确品牌在市场中的定位，如高端奢华、亲民实惠、科技前沿等，以及品牌所传达的整体风格和气质"
            rows="3"
            required
            @input="adjustFormTextareaHeight"
            @keydown.enter.ctrl.exact.prevent="
              handleFormNewLine($event, 'brandInfo.positioning')
            "
            ref="formTextareaRefs"
          ></textarea>
        </div>
        <div class="form-item">
          <label>目标受众人群画像<span class="required">*</span></label>
          <textarea
            v-model="formData.brandInfo.targetAudience"
            placeholder="详细描述目标受众的年龄、性别、地域、消费习惯、兴趣爱好等特征，以便精准定位"
            rows="3"
            required
            @input="adjustFormTextareaHeight"
            @keydown.enter.ctrl.exact.prevent="
              handleFormNewLine($event, 'brandInfo.targetAudience')
            "
            ref="formTextareaRefs"
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">二、产品信息</h3>
        <div class="form-item">
          <label>产品名称：<span class="required">*</span></label>
          <textarea
            v-model="formData.productInfo.name"
            placeholder="填写产品的具体名称"
            rows="1"
            required
            @input="adjustFormTextareaHeight"
            @keydown.enter.ctrl.exact.prevent="
              handleFormNewLine($event, 'productInfo.name')
            "
            ref="formTextareaRefs"
          ></textarea>
        </div>
        <div class="form-item">
          <label>产品核心卖点（3~5条）：<span class="required">*</span></label>
          <textarea
            v-model="formData.productInfo.sellingPoints"
            placeholder="提炼产品最具竞争力的3到5个特点，如独特的功能、卓越的品质、创新的设计等"
            rows="3"
            required
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
        <div class="form-item">
          <label>主要竞品概览：<span class="required">*</span></label>
          <textarea
            v-model="formData.productInfo.competitors"
            placeholder="列举与本产品直接竞争的主要品牌或型号，分析其优势与不足"
            rows="3"
            required
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
        <div class="form-item">
          <label>定价区间：<span class="required">*</span></label>
          <textarea
            v-model="formData.productInfo.priceRange"
            placeholder="若已明确产品定价范围，请提供，以便更好地制定传播策略"
            rows="1"
            required
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">三、营销目标</h3>
        <div class="form-item">
          <label
            >本次新品上市最想达成的目标：<span class="required">*</span></label
          >
          <textarea
            v-model="formData.marketingGoals"
            placeholder="明确本次新品上市的核心目标，如提高品牌曝光度、打造行业领先形象、实现首月销量KPI等"
            rows="3"
            required
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">四、传播渠道偏好</h3>
        <div class="form-item">
          <label>想要侧重的媒介或渠道：<span class="required">*</span></label>
          <textarea
            v-model="formData.channelPreferences"
            placeholder="选择本次传播中优先考虑的媒介或渠道，如微博、抖音、B站、微信公众号、户外LED、大型线下路演等"
            rows="3"
            required
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">五、传播周期</h3>
        <div class="form-item">
          <label>总体时长：<span class="required">*</span></label>
          <textarea
            v-model="formData.communicationCycle"
            placeholder="规划本次传播的整体时间安排，如预热1个月、发布期1周、后续长尾3个月，或其他时长设定"
            rows="3"
            required
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">六、必须包含的素材维度</h3>
        <div class="form-item">
          <label
            >列举在本次传播中必须出现的创意/物料类型：<span class="required"
              >*</span
            ></label
          >
          <textarea
            v-model="formData.requiredMaterials"
            placeholder="指定必须包含的素材类型，如短视频、海报、文案、KOL合作等"
            rows="3"
            required
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">七、预算或限制条件（若有）</h3>
        <div class="form-item">
          <label>预算限制：</label>
          <textarea
            v-model="formData.budgetLimitations.budget"
            placeholder="如有明确的预算范围，请提供，以便更精准地规划资源分配"
            rows="3"
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
        <div class="form-item">
          <label>合规要求：</label>
          <textarea
            v-model="formData.budgetLimitations.compliance"
            placeholder="如有特殊的行业合规要求或禁忌，请说明，以确保传播策略符合相关规定"
            rows="3"
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">八、其他补充信息</h3>
        <div class="form-item">
          <label>其他重要信息：<span class="required">*</span></label>
          <textarea
            v-model="formData.additionalInfo"
            placeholder="如有其他重要信息，如行业特殊背景、竞品最新动态、可利用的节日热点或IP合作需求等，请在此处补充说明，以便更全面地制定传播策略"
            rows="4"
            required
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
      </div>

      <div class="form-actions">
        <button
          class="submit-btn"
          @click="handleSubmit"
          :disabled="!isFormValid"
        >
          提交表单
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { ElMessage } from "element-plus";

/**
 * 组件属性定义
 */
const props = defineProps({
  /** 是否显示表单 */
  visible: {
    type: Boolean,
    default: true,
  },
});

/**
 * 组件事件定义
 */
const emit = defineEmits(["submit"]);

/**
 * 表单数据
 */
const formData = ref({
  brandInfo: {
    background: "",
    positioning: "",
    targetAudience: "",
  },
  productInfo: {
    name: "",
    sellingPoints: "",
    competitors: "",
    priceRange: "",
  },
  marketingGoals: "",
  channelPreferences: "",
  communicationCycle: "",
  requiredMaterials: "",
  budgetLimitations: {
    budget: "",
    compliance: "",
  },
  additionalInfo: "",
});

/**
 * 表单引用
 */
const formTextareaRefs = ref([]);

/**
 * 表单验证 - 检查所有必填字段是否已填写
 */
const isFormValid = computed(() => {
  return (
    formData.value.brandInfo.background.trim() !== "" &&
    formData.value.brandInfo.positioning.trim() !== "" &&
    formData.value.brandInfo.targetAudience.trim() !== "" &&
    formData.value.productInfo.name.trim() !== "" &&
    formData.value.productInfo.sellingPoints.trim() !== "" &&
    formData.value.productInfo.competitors.trim() !== "" &&
    formData.value.productInfo.priceRange.trim() !== "" &&
    formData.value.marketingGoals.trim() !== "" &&
    formData.value.channelPreferences.trim() !== "" &&
    formData.value.communicationCycle.trim() !== "" &&
    formData.value.requiredMaterials.trim() !== "" &&
    formData.value.additionalInfo.trim() !== ""
  );
});

/**
 * 格式化表单数据为消息内容
 * @param {Object} form - 表单数据
 * @returns {string} 格式化后的消息内容
 */
const formatFormToMessage = (form) => {
  return `# 传播策略框架信息

## 一、品牌信息
- **品牌名称/背景**：${form.brandInfo.background}
- **品牌定位/调性**：${form.brandInfo.positioning}
- **目标受众人群画像**：${form.brandInfo.targetAudience}

## 二、产品信息
- **产品名称**：${form.productInfo.name}
- **产品核心卖点**：${form.productInfo.sellingPoints}
- **主要竞品概览**：${form.productInfo.competitors}
- **定价区间**：${form.productInfo.priceRange}

## 三、营销目标
${form.marketingGoals}

## 四、传播渠道偏好
${form.channelPreferences}

## 五、传播周期
${form.communicationCycle}

## 六、必须包含的素材维度
${form.requiredMaterials}

## 七、预算或限制条件
- **预算限制**：${form.budgetLimitations.budget}
- **合规要求**：${form.budgetLimitations.compliance}

## 八、其他补充信息
${form.additionalInfo}

请基于以上信息，为我制定一套完整的传播策略框架。`;
};

/**
 * 提交表单
 */
const handleSubmit = () => {
  if (!isFormValid.value) {
    ElMessage.warning("请填写所有必填项");
    return;
  }

  // 格式化表单数据
  const formattedContent = formatFormToMessage(formData.value);

  // 发送提交事件
  emit("submit", {
    formData: formData.value,
    formattedContent,
  });

  // 重置表单
  resetForm();
};

/**
 * 重置表单
 */
const resetForm = () => {
  formData.value = {
    brandInfo: {
      background: "",
      positioning: "",
      targetAudience: "",
    },
    productInfo: {
      name: "",
      sellingPoints: "",
      competitors: "",
      priceRange: "",
    },
    marketingGoals: "",
    channelPreferences: "",
    communicationCycle: "",
    requiredMaterials: "",
    budgetLimitations: {
      budget: "",
      compliance: "",
    },
    additionalInfo: "",
  };
};

/**
 * 调整表单文本框高度
 */
const adjustFormTextareaHeight = () => {
  // 这里可以添加文本框高度调整逻辑
  // 暂时保留空实现，与原组件保持一致
};

/**
 * 处理表单换行
 * @param {Event} event - 键盘事件
 * @param {string} field - 字段路径
 */
const handleFormNewLine = (event, field) => {
  // 这里可以添加换行处理逻辑
  // 暂时保留空实现，与原组件保持一致
};
</script>

<style scoped>
/* 更新传播策略框架表单样式，与原版保持一致 */
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

.form-title {
  font-size: 22px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  text-align: center;
  line-height: 1.2;
  position: relative;
  padding-bottom: 12px;
}

.form-title:after {
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

.form-description {
  font-size: 14px;
  color: #666;
  margin-top: 20px;
  margin-bottom: 36px;
  line-height: 1.7;
  text-align: center;
}

.form-section {
  margin-bottom: 40px;
  padding-bottom: 32px;
  border-bottom: 1px solid #f0f0f0;
  position: relative;
}

.form-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.form-section:after {
  content: "";
  position: absolute;
  bottom: -1px;
  left: 0;
  height: 1px;
  width: 40px;
  background: #e60012;
  opacity: 0.2;
}

.form-section:last-child:after {
  display: none;
}

.section-title {
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

.section-title:after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 2px;
  background: rgba(230, 0, 18, 0.6);
  border-radius: 1px;
}

.form-item {
  margin-bottom: 24px;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-item label {
  margin-bottom: 12px;
  display: block;
}

.required {
  color: #e60012;
  margin-left: 4px;
  font-weight: bold;
}

.form-item textarea {
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

.form-item textarea:focus {
  background: #fff;
  border-color: #4e6ef2;
  box-shadow: 0 0 0 3px rgba(78, 110, 242, 0.1),
    inset 0 1px 2px rgba(0, 0, 0, 0);
  outline: none;
}

.form-item textarea:hover:not(:focus) {
  border-color: #c0c4cc;
}

.form-actions {
  margin-top: 48px;
  display: flex;
  justify-content: center;
}

.submit-btn {
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

.submit-btn:before {
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

.submit-btn:hover {
  background: #d40010;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(230, 0, 18, 0.3);
}

.submit-btn:hover:before {
  transform: translateX(100%);
}

.submit-btn:disabled {
  background: #ffb3b3;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.submit-btn:disabled:before {
  display: none;
}

/* 添加淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .strategy-form {
    padding: 20px;
  }
}
</style> 