<!-- 
  @file 工作区页面头部组件
  @description 包含页面标题和搜索/筛选功能的公共头部
-->
<template>
  <div class="page-header">
    <div class="header-left">
      <h1 class="page-title">{{ title }}</h1>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <span class="search-icon">🔍</span>
      <el-input
        type="textarea"
        :placeholder="searchPlaceholder"
        v-model="searchValue"
        :autosize="{ minRows: 2, maxRows: 6 }"
        @input="$emit('update:search', searchValue)"
      ></el-input>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const props = defineProps({
  title: String,
  searchPlaceholder: String,
  categoryTags: {
    type: Array,
    default: () => [],
  },
  modelValue: String,
});

const searchValue = ref("");

// 添加返回首页功能
const router = useRouter();
const goToHome = () => {
  console.log("返回首页按钮点击");

  // 添加 allowReturn 标记
  router.replace({ path: "/", query: { allowReturn: "true" } });
};

defineEmits(["update:modelValue", "update:search"]);
</script>

<style scoped>
.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: var(--text-primary);
}

/* 搜索栏 */
.search-bar {
  position: relative;
  margin-bottom: 24px;
}

.search-bar input {
  width: 100%;
  height: 40px;
  padding: 8px 16px 8px 40px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: white;
  transition: all 0.2s ease;
}

.search-bar input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1);
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 16px;
}

/* 分类标签 */
.category-tags {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.category-tag {
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 14px;
  color: var(--text-secondary);
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-tag:hover {
  color: var(--primary-color);
}

.category-tag.active {
  color: white;
  background: var(--primary-color);
}

@media (max-width: 768px) {
  .category-tags {
    overflow-x: auto;
    padding-bottom: 8px;
  }

  .category-tag {
    flex-shrink: 0;
  }
}
</style> 