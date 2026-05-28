<!-- 
  @file 单角色服务页面
  @description 展示所有可用的AI角色列表
-->
<template>
  <div class="single-role">
    <template v-if="!currentRole">
      <h1 class="page-title">单角色服务</h1>

      <!-- 搜索栏（Tabs上方） -->
      <el-input
        type="textarea"
        v-model="searchInput"
        placeholder="搜索角色或技能..."
        :autosize="{ minRows: 2, maxRows: 6 }"
        clearable
        class="role-search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <!-- 一级Tab -->
      <el-tabs
        v-model="currentFirstLevel"
        @tab-click="onFirstLevelChange"
        class="role-btn-tabs"
        tab-position="top"
      >
        <el-tab-pane
          v-for="item in filterTags"
          :key="item.value"
          :label="item.label"
          :name="item.value"
        />
      </el-tabs>

      <!-- 二级Tab只有在有多个子类时才显示 -->
      <el-tabs
        v-if="secondLevelTabs.length"
        v-model="currentSecondLevel"
        @tab-click="onSecondLevelChange"
        style="margin-top: 16px"
      >
        <el-tab-pane
          v-for="item in secondLevelTabs"
          :key="item.value"
          :label="item.label"
          :name="item.value"
        />
      </el-tabs>

      <!-- 角色列表 -->
      <div class="roles-grid">
        <role-card
          v-for="role in filteredRoles"
          :key="role.id"
          v-bind="role"
          @start-chat="startChat(role)"
          :loading="loading"
        />
      </div>
    </template>

    <!-- 聊天对话界面 -->
    <chat-dialog
      v-else
      :role="currentRole"
      :opening-statement="openingStatement"
      @close="handleDialogClose"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import RoleCard from "@/components/workspace/RoleCard.vue";
import PageHeader from "@/components/workspace/PageHeader.vue";
import ChatDialog from "@/components/workspace/ChatDialog.vue";
import {
  getRoles,
  getRoleDetail,
  type Role,
  type RoleDetail,
} from "@/api/roles";
import { sendMessage, getChatParameters } from "@/api/chat";
import { ElMessage } from "element-plus";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const router = useRouter();

/** @type {import('vue').Ref<string>} 用户输入的搜索内容 */
const searchInput = ref("");
/** @type {import('vue').Ref<string>} 实际用于过滤的搜索内容（防抖后赋值） */
const searchQuery = ref("");

// 搜索和筛选状态
const currentFilter = ref("全部");
const loading = ref(false);

// 1. 定义分类结构
const filterTags = [
  {
    label: "全部",
    value: "全部",
    children: [{ label: "全部", value: "全部" }],
  },
  {
    label: "策略洞察",
    value: "策略洞察",
    children: [{ label: "全部", value: "全部" }],
  },
  {
    label: "创意内容",
    value: "创意内容",
    children: [
      { label: "全部", value: "全部" },
      { label: "文案类", value: "文案类" },
      { label: "平面类", value: "平面类" },
      { label: "视频类", value: "视频类" },
      { label: "活动类", value: "活动类" },
      { label: "综合类", value: "综合类" },
    ],
  },
  {
    label: "自由沟通",
    value: "自由沟通",
    children: [{ label: "全部", value: "全部" }],
  },
];

// 2. Tab状态
const currentFirstLevel = ref("全部");
const currentSecondLevel = ref("全部");

// 3. 动态生成二级Tab
/**
 * @description 根据一级分类动态生成二级Tab，只有子类多于1时才显示
 */
const secondLevelTabs = computed(() => {
  const first = filterTags.find(
    (item) => item.value === currentFirstLevel.value
  );
  // 过滤掉只有"全部"一个选项的情况
  if (!first || first.children.length <= 1) return [];
  return first.children;
});

// 4. Tab切换逻辑
function onFirstLevelChange() {
  const first = filterTags.find(
    (item) => item.value === currentFirstLevel.value
  );
  if (!first || first.children.length <= 1) {
    currentSecondLevel.value = "全部";
  } else {
    currentSecondLevel.value = first.children[0].value;
  }
}

// 5. 角色筛选
const roles = ref<Role[]>([]);
const currentRole = ref<RoleDetail | null>(null);
const openingStatement = ref("");

/**
 * @description 先按Tab筛选，再按searchQuery过滤
 */
const filteredRoles = computed(() => {
  return roles.value
    .filter((role) => {
      // 一级Tab为"全部"
      if (currentFirstLevel.value === "全部") return true;
      // 二级Tab为"全部"
      if (currentSecondLevel.value === "全部") {
        return role.category === currentFirstLevel.value;
      }
      // 一级、二级都不是"全部"
      return (
        role.category === currentFirstLevel.value &&
        role.sub_category === currentSecondLevel.value
      );
    })
    .filter((role) => {
      // 搜索过滤
      if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase();
        return (
          role.title.toLowerCase().includes(q) ||
          role.description.toLowerCase().includes(q) ||
          (role.tags && role.tags.some((tag) => tag.toLowerCase().includes(q)))
        );
      }
      return true;
    });
});

// 开始对话
const startChat = async (role: Role) => {
  try {
    loading.value = true;
    // 获取角色详情
    const { data: roleData } = await getRoleDetail(role.id);
    if (!roleData.role) {
      throw new Error("获取角色详情失败");
    }

    // 获取角色参数
    const { data: parameters } = await getChatParameters(role.id);
    if (!parameters) {
      throw new Error("获取角色参数失败");
    }

    // 设置当前角色和开场白
    currentRole.value = roleData.role;
    openingStatement.value = parameters.opening_statement || "";
  } catch (error: any) {
    console.error("开始对话失败:", error);
    ElMessage.error(error.message || "开始对话失败");
  } finally {
    loading.value = false;
  }
};

// 处理对话框关闭
const handleDialogClose = () => {
  currentRole.value = null;
  openingStatement.value = "";
};

// 加载角色列表
const loadRoles = async () => {
  loading.value = true;
  try {
    const { data } = await getRoles({
      page: 1,
      size: 20,
    });
    roles.value = data.roles;
  } catch (error) {
    console.error("获取角色列表失败:", error);
    ElMessage.error("获取角色列表失败");
  } finally {
    loading.value = false;
  }
};

// 监听搜索和筛选变化
watch([searchQuery, currentFilter], async ([newQuery, newFilter]) => {
  await loadRoles();
});

// 在页头添加返回首页的链接按钮
const goToHome = () => {
  router.push("/");
};

// 修改 onMounted
onMounted(async () => {
  console.log("工作台页面加载...");

  // 先加载角色列表，不阻塞用户操作
  loadRoles();

  // 并行检查登录状态
  const isValid = await userStore.checkLoginStatus();
  console.log("登录状态检查结果:", isValid);

  if (!isValid) {
    console.log("用户未登录，重定向到登录页");
    ElMessage.warning("请先登录");
    router.push("/login");
  }
});

let debounceTimer = null;
/**
 * @description 监听 searchInput，200ms 防抖后赋值给 searchQuery
 */
watch(searchInput, (val) => {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    searchQuery.value = val;
  }, 200);
});

function onSecondLevelChange(tab) {
  currentSecondLevel.value = tab.name;
}
</script>

<style scoped>
.single-role {
  padding: 0 32px;
  background: #fff;
}

.roles-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  padding: 24px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .roles-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .single-role {
    padding: 16px;
  }

  .roles-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .role-search-input {
    font-size: 15px;
  }
  .role-search-input .el-input__inner {
    font-size: 15px;
    height: 40px;
  }
}

.role-search-input {
  margin-top: 32px;
  margin-bottom: 32px;
  width: 100%;
  font-size: 16px;
  border-radius: 10px;
  background: #fff;
  border: 1.5px solid #e5e6eb;
  box-shadow: 0 2px 8px 0 #f3f6fa;
  transition: border-color 0.2s, box-shadow 0.2s;
  display: block;
}

.role-search-input .el-input__wrapper {
  border-radius: 10px !important;
  box-shadow: none !important;
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
}

.role-search-input .el-input__inner {
  border-radius: 10px !important;
  border: none !important;
  background: transparent !important;
  font-size: 16px;
  color: #222;
  font-family: inherit;
  padding-left: 40px;
  height: 48px;
  box-shadow: none !important;
  outline: none !important;
  transition: box-shadow 0.2s, border-color 0.2s;
}

.role-search-input .el-input__inner:focus {
  outline: none !important;
  border: none !important;
  box-shadow: 0 0 0 2px #3575f6 !important;
}

.role-search-input .el-input__inner::placeholder {
  color: #bfc2cc;
  font-size: 15px;
  opacity: 1;
  font-family: inherit;
}

.role-search-input .el-input__prefix {
  left: 12px;
  color: #3575f6;
}

.role-btn-tabs {
  --tab-height: 40px;
  --tab-radius: 10px;
  --tab-padding: 0 28px;
  --tab-font-size: 17px;
  --tab-bg: transparent;
  --tab-active-bg: #3575f6;
  --tab-active-color: #fff;
  --tab-inactive-color: #666;
  --tab-gap: 16px;
  --tab-border: none;
  --tab-shadow: none;
  background: #fff;
  border-bottom: none;
  box-shadow: none;
  padding: 0 0 8px 0;
}
.role-btn-tabs .el-tabs__header {
  border-bottom: none !important;
  margin-bottom: 0;
  box-shadow: none;
}
.role-btn-tabs .el-tabs__nav {
  border: none;
  box-shadow: none;
  display: flex;
  gap: var(--tab-gap);
  background: transparent;
}
.role-btn-tabs .el-tabs__item {
  height: var(--tab-height);
  line-height: var(--tab-height);
  border-radius: var(--tab-radius);
  padding: var(--tab-padding);
  font-size: var(--tab-font-size);
  font-weight: 500;
  color: var(--tab-inactive-color);
  background: var(--tab-bg);
  border: var(--tab-border);
  box-shadow: var(--tab-shadow);
  margin-right: 0;
  transition: background 0.2s, color 0.2s;
  position: relative;
  z-index: 1;
}
.role-btn-tabs .el-tabs__item.is-active {
  background: var(--tab-active-bg);
  color: var(--tab-active-color);
  font-weight: 700;
  box-shadow: 0 2px 8px 0 #3575f61a;
}
.role-btn-tabs .el-tabs__item:not(.is-active):hover {
  background: #f5f7fa;
  color: #3575f6;
}
.role-btn-tabs .el-tabs__active-bar,
.role-btn-tabs .el-tabs__nav-wrap::after {
  display: none !important;
}
.role-sub-tabs {
  margin-top: 8px;
  margin-bottom: 8px;
  background: #fff;
  border-radius: 0 0 10px 10px;
  border-bottom: 1.5px solid #e5e6eb;
  box-shadow: none;
}
.role-sub-tabs .el-tabs__item {
  font-size: 15px;
  font-weight: 500;
  color: #222;
  padding: 0 20px;
  font-family: inherit;
  transition: color 0.2s;
}
.role-sub-tabs .el-tabs__item.is-active {
  color: #3575f6;
  font-weight: 600;
  background: none;
}
.role-sub-tabs .el-tabs__item:not(.is-active):hover {
  color: #3575f6;
  background: none;
}
.role-sub-tabs .el-tabs__active-bar {
  height: 2px;
  background: #3575f6;
  border-radius: 2px 2px 0 0;
  box-shadow: none;
}
</style> 