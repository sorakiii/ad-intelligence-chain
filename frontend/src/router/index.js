import { createRouter, createWebHistory } from "vue-router";
import Landing from "@/views/Landing.vue";
import MainLayout from "@/layouts/MainLayout.vue";

const routes = [
  {
    path: "/",
    name: "landing",
    component: () => import("@/views/Landing.vue"),
    meta: {
      title: "AI广告智链 - 首页",
      layout: "blank",
    },
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/auth/Login.vue"),
  },
  {
    path: "/register",
    name: "register",
    component: () => import("@/views/auth/Register.vue"),
  },
  {
    path: "/reset-password",
    name: "resetPassword",
    component: () => import("@/views/auth/ResetPassword.vue"),
  },
  {
    path: "/settings",
    name: "settings",
    component: () => import("@/views/settings/SystemSettings.vue"),
  },
  {
    path: "/workspace",
    component: MainLayout,
    children: [
      {
        path: "",
        redirect: "/workspace/single-role",
      },
      {
        path: "single-role",
        name: "singleRole",
        component: () => import("@/views/workspace/SingleRole.vue"),
      },
      {
        path: "targeted-service",
        name: "targetedService",
        component: () => import("@/views/workspace/TargetedService.vue"),
      },
      {
        path: "history",
        name: "history",
        component: () => import("@/views/workspace/History.vue"),
        children: [
          {
            path: "recent",
            name: "recentHistory",
            component: () =>
              import("@/views/workspace/history/RecentHistory.vue"),
          },
          {
            path: "single-role",
            name: "singleRoleHistory",
            component: () =>
              import("@/views/workspace/history/SingleRoleHistory.vue"),
            children: [
              {
                path: ":sessionId",
                name: "chatDetail",
                component: () => import("@/views/workspace/ChatDetail.vue"),
                props: true,
              },
            ],
          },
        ],
      },
      {
        path: "statistics",
        name: "statistics",
        component: () => import("@/views/workspace/Statistics.vue"),
        meta: {
          title: "数据分析",
          requiresAuth: true,
        },
      },
    ],
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: () => import("@/views/Dashboard.vue"),
  },
  // 暂时注释掉不存在的路由
  /*
  {
    path: '/workspace/targeted-service',
    name: 'targetedService',
    component: () => import('@/views/workspace/TargetedService.vue')
  },
  {
    path: '/workspace/history',
    name: 'history',
    component: () => import('@/views/workspace/History.vue')
  }
  */
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");

  // 处理 Token 过期后重定向到首页的情况
  if (to.path === "/" && to.query.expired === "true") {
    // 已经处理过了，继续导航
    next();
    return;
  }

  // 如果需要登录但没有token，重定向到登录页
  if ((to.path.startsWith("/workspace") || to.path === "/settings") && !token) {
    next("/login");
    return;
  }

  // 检查是否有主动返回首页的标记，如果有则允许访问
  if (to.path === "/" && token && !to.query.allowReturn) {
    // 如果 allowReturn 显式设置为 false，说明是退出登录，不重定向
    if (to.query.allowReturn === "false") {
      next();
      return;
    }

    // 否则重定向到工作台
    next("/workspace/single-role");
    return;
  }

  // 如果已登录且尝试访问登录/注册页面，重定向到工作台
  if ((to.path === "/login" || to.path === "/register") && token) {
    next("/workspace/single-role");
    return;
  }

  next();
});

export default router;
