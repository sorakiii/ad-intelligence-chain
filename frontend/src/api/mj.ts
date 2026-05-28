import request from "@/utils/request";

// MJ任务状态类型
export type MJTaskStatus =
  | "WAITING"
  | "IN_PROCESSING"
  | "SUCCESS"
  | "FAIL"
  | "CANCEL";

// MJ任务数据接口
export interface MJTask {
  id: number;
  user_imagine_id: number;
  status: MJTaskStatus;
  prompt: string;
  prompt_cn?: string;
  oss_image_url?: string;
  image_id?: string;
  actions_json?: any[];
  error_show?: string;
  created_at: string;
  updated_at: string;
}

// 接口返回类型
export interface MessageMJTasksResponse {
  [messageId: string]: MJTask[];
}

/**
 * 获取消息关联的图片任务列表
 * @param messageIds 消息ID列表（逗号分隔的字符串）
 */
export function getMessageMJTasks(messageIds: string) {
  return request<MessageMJTasksResponse>({
    url: "/api/mj/messages/tasks",
    method: "GET",
    params: { message_ids: messageIds },
  });
}

// 生成新图片
export function generateImage(data: { prompt: string; opt_uuid?: string }) {
  return request({
    url: "/api/mj/generate",
    method: "post",
    data,
  });
}

// 编辑图片
export function editImage(data: {
  action: string;
  image_id?: string;
  opt_uuid?: string;
}) {
  return request({
    url: "/api/mj/edit",
    method: "post",
    data,
  });
}

// 查询进度
export function queryProgress(user_imagine_id: number) {
  return request({
    url: "/api/mj/progress",
    method: "post",
    data: { user_imagine_id },
  });
}

// 取消任务
export function cancelTask(data: { user_imagine_id: number }) {
  return request({
    url: "/api/mj/cancel",
    method: "post",
    data,
  });
}

// 解析脚本生成图片
export function parseScriptToTasks(data: {
  script: string;
  message_id: string;
}) {
  return request({
    url: "/api/mj/parse-script",
    method: "post",
    data,
  });
}
