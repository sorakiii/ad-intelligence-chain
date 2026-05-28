/**
 * 通用复制文本工具函数
 * 支持多种复制方法，确保在不同环境下都能正常工作
 */
export const copyTextToClipboard = async (text) => {
  // 方法1: 使用现代 Clipboard API (如果可用)
  if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      console.warn('Clipboard API 失败，尝试备选方法', err);
      // 失败时继续尝试其他方法
    }
  }

  // 方法2: 使用传统的 document.execCommand 方法
  try {
    // 创建临时文本区域
    const textArea = document.createElement('textarea');
    textArea.value = text;
    
    // 设置样式使其不可见
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.width = '2em';
    textArea.style.height = '2em';
    textArea.style.padding = '0';
    textArea.style.border = 'none';
    textArea.style.outline = 'none';
    textArea.style.boxShadow = 'none';
    textArea.style.background = 'transparent';
    
    // 添加到文档并选中文本
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    // 执行复制命令
    const successful = document.execCommand('copy');
    
    // 清理
    document.body.removeChild(textArea);
    
    if (successful) {
      return true;
    }
  } catch (err) {
    console.error('execCommand 复制方法失败', err);
  }

  // 如果所有方法都失败，返回失败
  return false;
}; 