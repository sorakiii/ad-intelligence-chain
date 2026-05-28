import dayjs from "dayjs";
export const formatTime = (timestamp) => {
  // 格式化时间
  // 如果时间戳是秒级的，转换为毫秒级
  const milliseconds = timestamp * 1000;
  const now = Date.now();
  const diff = now - milliseconds;

  if (diff < 60 * 1000) return "刚刚";
  if (diff < 60 * 60 * 1000) return `${Math.floor(diff / (60 * 1000))}分钟前`;
  if (diff < 24 * 60 * 60 * 1000)
    return `${Math.floor(diff / (60 * 60 * 1000))}小时前`;
  if (diff < 30 * 24 * 60 * 60 * 1000)
    return `${Math.floor(diff / (24 * 60 * 60 * 1000))}天前`;

  return dayjs(milliseconds).format("YYYY-MM-DD HH:mm");
};
