<!--
  @file 产品定位验证表单组件
  @description 用于收集产品定位验证相关信息的表单组件
-->
<template>
  <div class="product-validation-form-container">
    <div class="product-validation-form">
      <h2 class="form-title">产品定位验证信息收集</h2>
      <p class="form-description">
        请填写以下信息，帮助我们更好地为您进行产品定位验证
      </p>

      <div class="form-section">
        <h3 class="section-title">①【产品核心传播卖点】</h3>
        <div class="form-item">
          <label>产品核心传播卖点<span class="required">*</span></label>
          <textarea
            v-model="formData.coreSellingPoints"
            placeholder="请详细描述产品的核心传播卖点，包括性能、屏幕、便携性等关键特性"
            rows="4"
            required
            @input="adjustFormTextareaHeight"
            @keydown.enter.ctrl.exact.prevent="
              handleFormNewLine($event, 'coreSellingPoints')
            "
            ref="formTextareaRefs"
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">②【目标人群画像】</h3>
        <div class="form-item">
          <label>年龄段<span class="required">*</span></label>
          <textarea
            v-model="formData.targetAudience.ageRange"
            placeholder="如：18 - 30岁"
            rows="1"
            required
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
        <div class="form-item">
          <label>人群范围<span class="required">*</span></label>
          <textarea
            v-model="formData.targetAudience.demographic"
            placeholder="如：3D/三维设计师"
            rows="1"
            required
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
        <div class="form-item">
          <label>职业<span class="required">*</span></label>
          <textarea
            v-model="formData.targetAudience.occupation"
            placeholder="如：工业设计 / 游戏动画设计 / 建筑设计"
            rows="2"
            required
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
        <div class="form-item">
          <label>场景<span class="required">*</span></label>
          <textarea
            v-model="formData.targetAudience.scenario"
            placeholder="根据人群和事业，由你来提供具体的使用场景描述"
            rows="2"
            required
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">③【首发售价 & 规格档位】</h3>
        <div class="form-item">
          <label>首发价格</label>
          <textarea
            v-model="formData.pricing.launchPrice"
            placeholder="如：8999起"
            rows="1"
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">④【竞品优先名单】</h3>
        <div class="form-item">
          <label>竞品</label>
          <textarea
            v-model="formData.competitors.list"
            placeholder="请列举主要竞品，如：&#10;1、戴尔（DELL）Precision 3591移动图形工作站笔记本电脑；&#10;2、荣耀MagicBook Pro16 2025"
            rows="4"
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">⑤【上市时间窗口】</h3>
        <div class="form-item">
          <label>上市时间</label>
          <textarea
            v-model="formData.launchTimeWindow"
            placeholder="如：2025年618电商节期间上市"
            rows="1"
            @input="adjustFormTextareaHeight"
            ref="formTextareaRefs"
          ></textarea>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">⑥【访谈对象要求】</h3>
        <div class="form-item">
          <label>访谈对象要求</label>
          <textarea
            v-model="formData.interviewRequirements"
            placeholder="结合人群与职业，由你定制具体的访谈对象要求"
            rows="3"
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
  coreSellingPoints: "",
  targetAudience: {
    ageRange: "",
    demographic: "",
    occupation: "",
    scenario: "",
  },
  pricing: {
    launchPrice: "",
  },
  competitors: {
    list: "",
  },
  launchTimeWindow: "",
  interviewRequirements: "",
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
    formData.value.coreSellingPoints.trim() !== "" &&
    formData.value.targetAudience.ageRange.trim() !== "" &&
    formData.value.targetAudience.demographic.trim() !== "" &&
    formData.value.targetAudience.occupation.trim() !== "" &&
    formData.value.targetAudience.scenario.trim() !== ""
  );
});

/**
 * 格式化表单数据为消息内容
 * @param {Object} form - 表单数据
 * @returns {string} 格式化后的消息内容
 */
const formatFormToMessage = (form) => {
  return `# 产品定位验证信息

## ①【产品核心传播卖点】
${form.coreSellingPoints}

## ②【目标人群画像】
- **年龄段**：${form.targetAudience.ageRange}
- **人群范围**：${form.targetAudience.demographic}
- **职业**：${form.targetAudience.occupation}
- **场景**：${form.targetAudience.scenario}

## ③【首发售价 & 规格档位】
${form.pricing.launchPrice || "（可空）"}

## ④【竞品优先名单】
${form.competitors.list || "（可空）"}

## ⑤【上市时间窗口】
${form.launchTimeWindow || "（可空）"}

## ⑥【访谈对象要求】
${form.interviewRequirements || "（可空）"}

请基于以上信息，为我进行产品定位验证分析。`;
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
    coreSellingPoints: "",
    targetAudience: {
      ageRange: "",
      demographic: "",
      occupation: "",
      scenario: "",
    },
    pricing: {
      launchPrice: "",
    },
    competitors: {
      list: "",
    },
    launchTimeWindow: "",
    interviewRequirements: "",
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
/* 产品定位验证表单样式，与StrategyForm保持一致 */
.product-validation-form-container {
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

.product-validation-form {
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
  .product-validation-form {
    padding: 20px;
  }
}
</style> 