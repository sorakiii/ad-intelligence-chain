import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "./styles/variables.css";

// 导入Element Plus
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
// 如果需要中文界面，添加以下导入
import zhCn from "element-plus/dist/locale/zh-cn.mjs";

import "viewerjs/dist/viewer.css";
import VueViewer from "v-viewer";

// 注册Service Worker来处理缓存
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('SW registered: ', registration);
      })
      .catch(registrationError => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

const app = createApp(App);

// 使用Element Plus
app.use(ElementPlus, {
  locale: zhCn, // 使用中文
});
app.use(createPinia());
app.use(router);
app.use(VueViewer);

app.mount("#app");
