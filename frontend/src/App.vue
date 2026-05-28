<template>
  <router-view></router-view>
  <VersionCheck />
</template>

<script setup>
import { onMounted, onUnmounted } from "vue";
import { useUserStore } from "@/stores/user";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import VersionCheck from "@/components/common/VersionCheck.vue";

const userStore = useUserStore();
const router = useRouter();

onMounted(async () => {
  // 获取 token
  const token = localStorage.getItem("token");

  if (token) {
    try {
      // 可以添加一个简单的 API 调用来验证 token 有效性
      // 例如：await fetch('/api/validate-token')

      // 如果成功，更新 store
      userStore.token = token;
    } catch (error) {
      // 如果 token 无效，清除状态并提示
      if (error.response && error.response.status === 401) {
        userStore.logout();
        ElMessage.warning("登录已过期，请重新登录");

        // 如果当前不在首页，重定向到首页
        if (router.currentRoute.value.path !== "/") {
          router.replace("/");
        }
      }
    }
  }

  // 设置定期检查 token 有效性（例如每 30 分钟）
  const tokenCheckInterval = setInterval(async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      clearInterval(tokenCheckInterval);
      return;
    }

    try {
      // 简单的 API 调用验证 token
      // await fetch('/api/validate-token')
    } catch (error) {
      if (error.response && error.response.status === 401) {
        clearInterval(tokenCheckInterval);
        userStore.logout();
        ElMessage.warning("登录已过期，请重新登录");

        if (router.currentRoute.value.path !== "/") {
          router.replace("/");
        }
      }
    }
  }, 30 * 60 * 1000); // 30分钟

  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(tokenCheckInterval);
  });
});
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
    "Helvetica Neue", Arial, sans-serif;
  color: var(--text-primary);
  background-color: var(--bg-color);
}

/* 在工作区页面隐藏导航栏 */
.workspace .nav-header {
  display: none;
}
</style> 