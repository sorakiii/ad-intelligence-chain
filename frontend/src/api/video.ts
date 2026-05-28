import request from "@/utils/request";

// 视频任务状态类型
export type VideoTaskStatus = "PENDING" | "PROCESSING" | "SUCCEEDED" | "FAILED";

// 视频任务数据接口
export interface VideoTask {
  id: number;
  message_id: number;
  status: VideoTaskStatus;
  error_message?: string;
  video_url?: string;
  prompt: string;
  script_data?: string;
  created_at: string;
  updated_at: string;
}

// 接口返回类型
export interface MessageVideoTasksResponse {
  [messageId: string]: VideoTask[];
}

/**
 * 获取消息关联的视频任务列表
 * @param messageIds 消息ID列表（逗号分隔的字符串）
 */
export function getMessageVideoTasks(messageIds: string) {
  return request<Record<string, any[]>>({
    url: "/api/video/messages/tasks",
    method: "GET",
    params: { message_ids: messageIds },
  });
}

// 更新视频任务
export function updateVideoTask(taskId: number, prompt: string) {
  return request({
    url: `/api/video/tasks/${taskId}`,
    method: "put",
    data: {
      prompt,
    },
  });
}

/**
 * 创建视频生成任务
 */
export function createVideoTask(messageId: string, data: Record<string, any>) {
  return request({
    url: `/api/video/messages/${messageId}/tasks`,
    method: "POST",
    data,
  });
}

/**
 * 查询视频任务状态
 */
export interface VideoTaskStatusResponse {
  request_id: string;
  output: {
    task_id: string;
    task_status: string;
    submit_time?: string;
    scheduled_time?: string;
    end_time?: string;
    video_url?: string;
  };
  usage?: {
    video_count: number;
  };
}

export function getVideoTaskStatus(taskId: string) {
  return request<VideoTaskStatusResponse>({
    url: `/api/video/tasks/${taskId}`,
    method: "GET",
  });
}

/**
 * 轮询视频任务状态
 */
export async function pollVideoTaskStatus(
  taskId: string,
  options: {
    interval?: number; // 轮询间隔，默认 5000ms
    timeout?: number; // 超时时间，默认 15分钟
    onProgress?: (status: string) => void; // 进度回调
  } = {}
): Promise<VideoTaskStatusResponse> {
  const { interval = 5000, timeout = 15 * 60 * 1000, onProgress } = options;

  const startTime = Date.now();

  while (true) {
    const response = await getVideoTaskStatus(taskId);
    const status = response.output.task_status;

    // 调用进度回调
    if (onProgress) {
      onProgress(status);
    }

    // 如果任务完成或失败，返回结果
    if (status === "SUCCEEDED" || status === "FAILED") {
      return response;
    }

    // 检查是否超时
    if (Date.now() - startTime > timeout) {
      throw new Error("Task polling timeout");
    }

    // 等待指定时间后继续轮询
    await new Promise((resolve) => setTimeout(resolve, interval));
  }
}

/**
 * 解析文本脚本并创建视频任务
 * @param script 要解析的文本内容
 * @param messageId 可选的消息ID（字符串格式）
 */
export function parseScriptToTasks(script: string, messageId: string) {
  return request<{
    tasks: Array<{
      id: number;
      status: VideoTaskStatus;
      prompt: string;
      script_data: any;
      video_url: string | null;
    }>;
  }>({
    url: "/api/video/parse-script",
    method: "POST",
    data: {
      script,
      message_id: messageId,
    },
  });
}
