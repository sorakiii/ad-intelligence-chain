// 会话类型
export type SessionType = "single_role" | "targeted" | "team";

// 过滤条件
export type SessionFilter = "all" | "starred" | "archived";

// 会话列表请求参数
export interface SessionListParams {
  type?: SessionType;
  filter?: SessionFilter;
  page?: number;
  size?: number;
}

// 会话信息
export interface Session {
  id: string;
  title: string;
  role_id: number;
  role_name: string;
  role_icon: string;
  last_message: string;
  last_time: number;
  message_count: number;
  is_starred: boolean;
  is_archived: boolean;
  active_branch_id?: number; // 当前活跃的分支ID
}

// 会话列表响应
export interface SessionListResponse {
  sessions: Session[];
  total: number;
}

export interface ChatSession {
  id: string;
  title: string;
  role_id: string;
  role_name: string;
  role_icon: string;
  last_message: string;
  last_time: number;
  message_count: number;
  is_starred: boolean;
  is_archived: boolean;
  active_branch_id?: number; // 当前活跃的分支ID
}

export interface ChatMessage {
  id: string;
  content: string;
  type: "user" | "assistant";
  timestamp: number;
  file_ids?: string[];
  branch_id?: number; // 分支ID
  position?: number; // 在分支中的位置
}

export interface ChatRole {
  id: string;
  title: string;
  icon: string;
  description?: string;
  capabilities?: string[];
  examples?: string[];
}

// 消息类型
export type MessageType = "user" | "assistant";

// 消息接口
export interface Message {
  id: number;
  message_id?: string;
  content: string;
  type: MessageType;
  timestamp: number;
  file_ids?: string[];
  files?: any[];
  api_status?: string;
  api_usage?: any;
  inferring?: boolean;
  retriever_resources?: any;
  feedback_rating?: string;
  feedback?: {
    rating: string;
    content?: string;
  };
  branch_id?: number; // 分支ID
  position?: number; // 在分支中的位置
  fork_from_id?: number; // 分支来源ID
  next_branches?: {
    // 新增：后续分支信息
    count: number;
    branches: { id: string; title: string; branch_id: number }[];
    current_branch_index: number;
  } | null;
  errorMessage?: string;
  html?: {
    html_code: string;
    status: string;
    id: number;
    type: "session" | "message";
    session_id: number;
    message_id: number;
  };
}

// 消息列表响应
export interface MessageListResponse {
  messages: Message[];
  total: number;
  active_branch_id?: number; // 当前活跃的分支ID
  has_more?: boolean;
  session?: Session;
}

// 消息列表请求参数
export interface MessageListParams {
  page?: number;
  size?: number;
  branch_id?: number; // 分支ID
  include_context?: number; // 是否包含父辈上下文,1:包含,0:不包含
  message_id?: string; // 消息ID
}

// 分支节点
export interface BranchNode {
  id: number;
  title: string;
  parent_id?: number;
  fork_from_id?: number;
  fork_content?: string;
  path?: string;
  children?: BranchNode[];
}

// 分支树
export interface BranchTree {
  id: number; // 根节点ID为0
  title: string;
  path: string;
  children: BranchNode[];
}

// 分支树响应
export interface BranchTreeResponse {
  branch_tree: BranchTree;
  active_branch_id: number;
}

// 视频任务状态
export type VideoTaskStatus =
  | "PENDING"
  | "QUEUED"
  | "PROCESSING"
  | "SUCCEEDED"
  | "FAILED"
  | "API_ERROR";

// 视频任务接口
export interface VideoTask {
  id: number;
  status: VideoTaskStatus;
  prompt: string;
  script_data: string;
  video_url?: string;
  error_code?: string | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
  finished_at?: string | null;
}
