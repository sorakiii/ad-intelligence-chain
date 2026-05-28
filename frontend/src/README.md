# 项目结构

此文档描述了前端代码库的目录结构和内容。

## 目录结构

- **src/**
  - **views/**
    - `Workspace.vue`
    - `Dashboard.vue`
    - `Landing.vue`
    - **workspace/**
    - **auth/**
  - **styles/**
    - `variables.css`
  - **types/**
    - `chat.ts`
  - **utils/**
    - `request.js`
  - **layouts/**
    - `BlankLayout.vue`
    - `MainLayout.vue`
  - **router/**
    - `index.js`
  - **components/**
    - **workspace/**
    - **landing/**
    - **layout/**
  - **api/**
    - `auth.js`
    - `roles.ts`
  - **assets/**
    - **icons/**
      - `password.svg`
      - `phone.svg`
      - `wechat.svg`
      - `email.svg`
  - `main.js`
  - `App.vue`

## 概述

- **views/**: 包含不同视图的 Vue 组件，如工作区、仪表板和着陆页。
- **styles/**: 包含样式的 CSS 文件，如 `variables.css`。
- **types/**: 包含 TypeScript 类型定义，如 `chat.ts`。
- **utils/**: 包含实用函数，如 `request.js`。
- **layouts/**: 包含布局组件，如 `BlankLayout.vue` 和 `MainLayout.vue`。
- **router/**: 包含路由配置，如 `index.js`。
- **components/**: 包含可重用的 Vue 组件，按子目录组织。
- **api/**: 包含与 API 相关的脚本，如 `auth.js` 和 `roles.ts`。
- **assets/**: 包含静态资源，如图标。 