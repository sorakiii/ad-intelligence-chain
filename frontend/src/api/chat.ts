import request from "@/utils/request";
import type {
  SessionListParams,
  SessionListResponse,
  MessageListParams,
  MessageListResponse,
  Session,
} from "@/types/chat";
import config from "@/config";

/**
 * 获取会话列表
 * @param params 查询参数
 */
export function getSessionList(params: SessionListParams = {}) {
  return request<SessionListResponse>({
    url: "/api/chat/sessions",
    method: "GET",
    params: {
      type: params.type,
      filter: params.filter,
      page: params.page || 1,
      size: params.size || 20,
    },
  });
}

/**
 * 收藏/取消收藏会话
 * @param sessionId 会话ID
 * @param isStarred 是否收藏
 */
export function toggleSessionStar(sessionId: string, isStarred: boolean) {
  return request({
    url: `/api/chat/sessions/${sessionId}/star`,
    method: "PUT",
    data: { is_starred: isStarred },
  });
}

/**
 * 归档/取消归档会话
 * @param sessionId 会话ID
 * @param isArchived 是否归档
 */
export function toggleSessionArchive(sessionId: string, isArchived: boolean) {
  return request({
    url: `/api/chat/sessions/${sessionId}/archive`,
    method: "PUT",
    data: { is_archived: isArchived },
  });
}

/**
 * 获取会话消息历史
 * @param sessionId 会话ID
 * @param params 查询参数
 */
export function getSessionMessages(
  sessionId: string,
  params: MessageListParams = {}
) {
  return request<MessageListResponse>({
    url: `/api/chat/sessions/${sessionId}/messages`,
    method: "GET",
    params: {
      page: params.page || 1,
      size: params.size || 20,
      branch_id: params.branch_id,
      include_context: params.include_context,
      message_id: params.message_id,
    },
  });
}

/**
 * 发送消息
 * @param params 消息参数
 */
export function sendMessage(params: {
  session_id?: string;
  role_id?: string;
  content: string;
  file_ids?: number[];
  session_type: "single_role" | "targeted" | "team";
  branch_id?: number;
  parent_message_id?: string;
  model: "gpt" | "deepseek";
}) {
  // 获取认证token
  const token = localStorage.getItem("token");
  if (!token) {
    throw new Error("未登录");
  }

  // 使用config中的baseURL和API路径
  const url = `${config.baseURL}${config.api.chat.messages}`;
  const body = JSON.stringify({
    session_id: params.session_id,
    role_id: params.role_id,
    content: params.content,
    file_ids: params.file_ids,
    session_type: params.session_type,
    branch_id: params.branch_id,
    parent_message_id: params.parent_message_id,
    model: params.model,
  });

  return fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      "Cache-Control": "no-cache",
      Authorization: `Bearer ${token}`,
    },
    body,
    // credentials: "include",
  });
}

/**
 * 获取角色对话参数
 * @param roleId 角色ID
 */
export function getChatParameters(roleId: string) {
  return request<{
    opening_statement: string;
    suggested_questions: string[];
    suggested_questions_after_answer: { enabled: boolean };
    speech_to_text: { enabled: boolean };
    retriever_resource: { enabled: boolean };
    annotation_reply: { enabled: boolean };
    user_input_form: Array<{
      "text-input"?: {
        label: string;
        variable: string;
        required: boolean;
        default: string;
      };
      select?: {
        label: string;
        variable: string;
        required: boolean;
        default: string;
        options: string[];
      };
    }>;
    file_upload: {
      image: {
        enabled: boolean;
        number_limits: number;
        transfer_methods: string[];
      };
    };
    system_parameters: {
      file_size_limit: number;
      image_file_size_limit: number;
      audio_file_size_limit: number;
      video_file_size_limit: number;
    };
  }>({
    url: "/api/chat/parameters",
    method: "GET",
    params: { role_id: roleId },
  });
}

/**
 * 重命名会话
 * @param sessionId 会话ID
 * @param params 重命名参数
 */
export function renameSession(
  sessionId: string,
  params: {
    title: string;
    autoGenerate?: boolean;
  }
) {
  return request<{
    id: string;
    title: string;
    conversation_id: string;
    updated_at: number;
  }>({
    url: `/api/chat/sessions/${sessionId}/rename`,
    method: "POST",
    data: {
      title: params.title,
      auto_generate: params.autoGenerate ?? false,
    },
  });
}

/**
 * 删除会话
 * @param sessionId 会话ID
 */
export function deleteSession(sessionId: string) {
  return request({
    url: `/api/chat/sessions/${sessionId}`,
    method: "DELETE",
  });
}

/**
 * 获取最近会话
 * @param limit 限制数量，默认10
 */
export function getRecentSessions(limit: number = 10) {
  return request({
    url: "/api/chat/sessions/recent",
    method: "GET",
    params: { limit },
  });
}

/**
 * 获取会话的分支树
 * @param sessionId 会话ID
 */
export function getBranchTree(sessionId: string | number) {
  return request<{
    branch_tree: {
      id: number;
      title: string;
      children: Array<{
        id: number;
        title: string;
        fork_from_id: number;
        fork_content: string;
        parent_id: number;
        children: Array<any>;
      }>;
    };
    active_branch_id: number;
  }>({
    url: `/api/chat/sessions/${sessionId}/branches`,
    method: "GET",
  });
}

/**
 * 切换分支
 * @param sessionId 会话ID
 * @param branchId 分支ID
 */
export function switchBranch(sessionId: string | number, branchId: number) {
  return request<{
    branch_id: number;
  }>({
    url: `/api/chat/sessions/${sessionId}/branches/${branchId}/switch`,
    method: "PUT",
  });
}

/**
 * 刷新会话消息列表
 * @param sessionId 会话ID
 */
export function refreshSessionMessages(sessionId: string) {
  return request<MessageListResponse>({
    url: `/api/chat/sessions/${sessionId}/messages`,
    method: "GET",
    params: {
      page: 1,
      size: 100,
      timestamp: Date.now(),
    },
  });
}
