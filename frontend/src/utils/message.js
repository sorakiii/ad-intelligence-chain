import { ElMessage } from "element-plus";

/**
 * 显示普通消息
 * @param {string | import('vue').VNode | (() => import('vue').VNode)} message 消息内容
 * @param {object} options ElMessage 的其他选项，可覆盖默认值
 * @returns {import('element-plus').MessageHandle}
 */
export function showMessage(message, options = {}) {
  return ElMessage({
    message,
    duration: 1000, // 默认 1 秒
    ...options, // 允许覆盖
  });
}

/**
 * 显示成功消息
 * @param {string | import('vue').VNode | (() => import('vue').VNode)} message 消息内容
 * @param {object} options ElMessage 的其他选项，可覆盖默认值
 * @returns {import('element-plus').MessageHandle}
 */
export function showSuccessMessage(message, options = {}) {
  return ElMessage.success({
    message,
    duration: 1000, // 默认 1 秒
    ...options,
  });
}

/**
 * 显示错误消息
 * @param {string | import('vue').VNode | (() => import('vue').VNode)} message 消息内容
 * @param {object} options ElMessage 的其他选项，可覆盖默认值
 * @returns {import('element-plus').MessageHandle}
 */
export function showErrorMessage(message, options = {}) {
  return ElMessage.error({
    message,
    duration: 1000, // 默认 1 秒
    ...options,
  });
}

/**
 * 显示警告消息
 * @param {string | import('vue').VNode | (() => import('vue').VNode)} message 消息内容
 * @param {object} options ElMessage 的其他选项，可覆盖默认值
 * @returns {import('element-plus').MessageHandle}
 */
export function showWarningMessage(message, options = {}) {
  return ElMessage.warning({
    message,
    duration: 1000, // 默认 1 秒
    ...options,
  });
}

/**
 * 显示普通信息消息
 * @param {string | import('vue').VNode | (() => import('vue').VNode)} message 消息内容
 * @param {object} options ElMessage 的其他选项，可覆盖默认值
 * @returns {import('element-plus').MessageHandle}
 */
export function showInfoMessage(message, options = {}) {
  return ElMessage.info({
    message,
    duration: 1000, // 默认 1 秒
    ...options,
  });
}

// ... 可以添加 showError, showWarning 等
