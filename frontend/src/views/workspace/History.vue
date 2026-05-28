<!-- 
  @file 历史记录布局组件
  @description 历史记录页面的布局容器，用于显示子路由内容
-->
<template>
  <div class="history-container">
    <router-view></router-view>
  </div>
</template>

<script setup>
</script>

<style scoped>
.history-container {
  height: 100%;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}
</style> 