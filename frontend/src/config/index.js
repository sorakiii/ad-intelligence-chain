// 获取当前环境
// const env = import.meta.env.MODE || 'production'
const env = import.meta.env.MODE || "development";

// 环境配置
const envConfig = {
  development: {
    baseURL: import.meta.env.VITE_API_URL || "http://localhost:5002",
    EQMJ_HOME: import.meta.env.VITE_EQMJ_HOME || "http://localhost:5002",
  },
  production: {
    // 使用环境变量或默认值
    baseURL: import.meta.env.VITE_API_URL || "",  // 改为空字符串
    EQMJ_HOME: import.meta.env.VITE_EQMJ_HOME || "",
  },
};

const config = {
  // 环境
  env,

  // API 基础路径配置
  baseURL: envConfig[env].baseURL,
  EQMJ_HOME: envConfig[env].EQMJ_HOME,
  // API 超时时间
  timeout: 300000,

  // API 路径配置
  api: {
    // 认证相关 - 添加 /api 前缀
    auth: {
      login: "/api/auth/login",           // 改为 /api/auth/login
      register: "/api/auth/register",     // 改为 /api/auth/register
      resetPassword: "/api/auth/reset-password",
      sendCode: "/api/auth/send-code",    // 改为 /api/auth/send-code
      updatePurposes: "/api/auth/update-purposes",
    },

    // 聊天相关
    chat: {
      sessions: "/api/chat/sessions",
      messages: "/api/chat/messages",
      parameters: "/api/chat/parameters",
    },

    // 角色相关
    roles: {
      list: "/api/roles",
      detail: "/api/roles/{id}",
    },
  },
};

// 打印当前环境和API地址
console.log(`Current env: ${config.env}`);
console.log(`API baseURL: ${config.baseURL}`);

export default config;
