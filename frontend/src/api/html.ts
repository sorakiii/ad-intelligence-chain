import request from "@/utils/request";

/**
 * 生成 HTML 网页内容
 */
export function generateHtmlApi(data: {
  text: string;
  message_id: string;
  model?: string;
}) {
  return request({
    url: "/api/html/generate",
    method: "post",
    data,
  });
}

/**
 * 获取消息 HTML 内容
 */
export function getMessageHtmlApi(messageIds: string[], sessionId: number) {
  return request({
    url: "/api/html/messages/html",
    method: "get",
    params: {
      message_ids: messageIds.join(","),
      session_id: sessionId,
    },
  });
}
