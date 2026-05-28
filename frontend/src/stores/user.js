import { defineStore } from "pinia";
import { ref } from "vue";
import authApi from "@/api/auth";

export const useUserStore = defineStore("user", () => {
  const userInfo = ref(null);
  const isAdmin = ref(false);
  const isLoggedIn = ref(false);
  const canUseWorkspace = ref(false);
  const loading = ref(false);

  /**
   * 用户登录
   * @param {string} token - 访问令牌
   * @param {Object} user - 用户信息
   */
  const login = (token, user) => {
    userInfo.value = user;
    isAdmin.value = user.role_id === 1; // 假设 role_id 1 是管理员
    isLoggedIn.value = true;
    localStorage.setItem("token", token);
    localStorage.setItem("userInfo", JSON.stringify(user));
  };

  /**
   * 检查登录状态
   * @returns {Promise<boolean>} 是否已登录
   */
  const checkLoginStatus = async () => {
    // 优先使用本地存储的用户信息
    const storedUserInfo = localStorage.getItem("userInfo");
    if (storedUserInfo) {
      const user = JSON.parse(storedUserInfo);
      userInfo.value = user;
      isAdmin.value = user.role_id === 1;
      return true;
    }

    // 如果没有本地存储的信息，再尝试从服务器获取
    try {
      const response = await authApi.getCurrentUser();
      userInfo.value = response.data;
      isAdmin.value = response.data.role_id === 1;
      localStorage.setItem("userInfo", JSON.stringify(response.data));
      return true;
    } catch (error) {
      userInfo.value = null;
      isAdmin.value = false;
      return false;
    }
  };

  /**
   * 检查管理员权限
   * @returns {Promise<boolean>} 是否为管理员
   */
  const checkAdminPermission = async () => {
    if (isAdmin.value) return true;

    // 如果 store 中没有用户信息，尝试从本地存储获取
    if (!userInfo.value) {
      const storedUserInfo = localStorage.getItem("userInfo");
      if (storedUserInfo) {
        const user = JSON.parse(storedUserInfo);
        userInfo.value = user;
      }
    }
    isAdmin.value = userInfo.value.role_id === 1;
    return isAdmin.value;
  };

  /**
   * 检查使用权限
   * @returns {Promise<boolean>} 是否可以使用工作台
   */
  const checkUserPermission = async () => {
    if (canUseWorkspace.value) return true;
    // 如果 store 中没有用户信息，尝试从本地存储获取
    if (!userInfo.value) {
      const storedUserInfo = localStorage.getItem("userInfo");
      if (storedUserInfo) {
        const user = JSON.parse(storedUserInfo);
        userInfo.value = user;
      }
    }
    const timestampInSeconds = Math.floor(Date.now() / 1000);
    if (userInfo.value.role_id === -1) {
      canUseWorkspace.value = userInfo.value.expired_at > timestampInSeconds;
    } else {
      canUseWorkspace.value = true;
    }
    return canUseWorkspace.value;

    return false;
  };

  /**
   * 用户登出
   * @returns {Promise<void>}
   */
  const logout = async () => {
    try {
      // await authApi.logout();
      clearUserInfo();
    } catch (error) {
      console.error("登出失败:", error);
      throw error;
    }
  };

  /**
   * 清除用户信息
   */
  const clearUserInfo = () => {
    userInfo.value = null;
    isAdmin.value = false;
    isLoggedIn.value = false;
    localStorage.removeItem("token");
    localStorage.removeItem("userInfo");
  };

  return {
    userInfo,
    isAdmin,
    loading,
    isLoggedIn,
    login,
    checkLoginStatus,
    checkAdminPermission,
    checkUserPermission,
    logout,
    clearUserInfo,
  };
});
