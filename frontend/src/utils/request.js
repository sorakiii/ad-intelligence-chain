import axios from "axios";
import config from "@/config";
import { ElMessage } from "element-plus";
import router from "@/router";
import { useUserStore } from "@/stores/user";

// 创建一个标记，防止多次触发重定向
let isRedirecting = false;

// 创建 axios 实例
const request = axios.create({
  baseURL: config.baseURL,
  timeout: config.timeout,
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.log(error);
    return Promise.reject("你的网络有些波动，刷新一下就好了");
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data;
    if (res.success) {
      return res;
    }
    ElMessage.error(res.message || "你的网络有些波动，刷新一下就好了");
    return Promise.reject(
      new Error(res.message || "你的网络有些波动，刷新一下就好了")
    );
  },
  (error) => {
    // 处理 Token 过期情况
    if (error.response && error.response.status === 401) {
      handleTokenExpired();
    } else {
      // 处理其他错误
      const message =
        error.response?.data?.message || "你的网络有些波动，刷新一下就好了";
      ElMessage.error(message);
    }
    console.log(error);
    return Promise.reject("你的网络有些波动，刷新一下就好了");
  }
);

// 处理 Token 过期
const handleTokenExpired = () => {
  // 防止多个请求同时触发多次重定向
  if (isRedirecting) return;
  isRedirecting = true;

  // 获取 store 实例
  const userStore = useUserStore();

  // 清除用户状态
  userStore.logout();

  // 显示友好提示
  ElMessage.warning("登录已过期，请重新登录");

  // 重定向到首页
  router.replace({ path: "/", query: { expired: "true" } });

  // 延迟重置标记，防止短时间内多次触发
  setTimeout(() => {
    isRedirecting = false;
  }, 2000);
};

export default request;
