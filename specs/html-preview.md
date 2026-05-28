# 需求
可视化网页功能：
1、接入deepseek的生成可视化网页功能
2、全能创意助手一个来接入测试 (YOUR_DIFY_API_KEY)
3、流程：生成内容后，内容下方有一个按钮：生成可视化网页
生成后有两个按钮：立即查看、下载
4、点击立即查看后，打开一个新的网页来浏览
5、下载就是下载html文件

## 风格设计

Design a futuristic, high-tech UI with:
- Holographic elements
- Vibrant neon color accents
- Thin, precise lines
- Floating interactive components
- Augmented reality-inspired interfaces
- Dynamic, animated transitions


## 方案

角色id如果是 27， 需要支持模型切换。
如果返回的聊天信息中，带有```html
可以认为包含html代码，需要提取出来，然后生成可视化网页。

前端直接用正则提取```html{代码}```之间的代码，然后生成可视化网页。

自定义一个新的组件，就叫 HtmlPreview.vue

在组件中，需要展示这个html代码，并且需要展示一个按钮：立即查看、下载

点击立即查看后，可以显示一个可关闭的浮层。浮层的内容 用iframe来展示html代码

点击下载后，下载html文件


### 后端

#### 工作流
dify_service.py 再封装一个工作流，功能内容生成html网页。
对应的 key 通过环境变量 `DIFY_API_KEY_HTML_ZIP` 或 `DIFY_API_KEY` 配置。
参考实现：
```python
   def convert_text_to_prompt_json(self, text_data, user=None):
        """将文本转换为绘画提示词 JSON 格式
        
        Args:
            text_data (str): 原始文本内容
            user (str, optional): 用户标识
            
        Returns:
            dict: 结构化的绘画提示词 JSON 对象，包含 ai_mj 字段
        """
        try:
            
            url = f"{self.base_url}/chat-messages"
            
            # 准备请求体
            payload = {
                "inputs": {},
                "query": f"{text_data}",  # 添加明确的指令
                "response_mode": "blocking",
                "user": user or "system"
            }
            
            # 使用特定的 API Key 构建请求头
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.debug(f"Converting text to prompt JSON - URL: {url}")
            logger.debug(f"Text length: {len(text_data)} characters")
            
            # 发送请求
            response = requests.post(url, json=payload, headers=headers)
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"Text conversion error - Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Text conversion failed with status {response.status_code}")
            
            # 解析响应内容
            result = response.json()
            
            # 提取并解析 answer 部分为 JSON
            if 'answer' in result:
                try:
                    # 使用新的清理函数
                    json_content = clean_and_parse_json(result['answer'])
                    logger.info("Text successfully converted to prompt JSON format")
                    
                    # 确保返回的 JSON 包含必要的字段
                    if not isinstance(json_content, dict):
                        raise ValueError("Response is not a valid JSON object")
                        
                    # 设置默认值
                    prompt_json = {
                        "ai_mj": json_content.get("ai_mj", result['answer'])
                    }
                    
                    return prompt_json
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Response is not valid JSON: {str(e)}")
                    return {"ai_mj": result['answer']}
            else:
                logger.warning("No answer field in response")
                return {"ai_mj": str(result)}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Text conversion request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Error response: {e.response.text}")
            raise Exception(f"Failed to convert text: {str(e)}")
        except Exception as e:
            logger.error(f"Text conversion error: {str(e)}")
            raise 

```

参考 @backend/tests/test_dify_service.py 来写一个测试用例。
测试生成的html网页是否能正常显示。

#### models
message_html 
只需要几个字段：
id 自增id
message_id 消息id
html_code html代码
created_at 创建时间
updated_at 更新时间

参考代码：
```python
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    ForeignKey, 
    JSON, 
    Text,
    DateTime,
    Enum as SQLAlchemyEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import db

# --- Enums --- #

class TaskStatus(str, Enum):
    """Enum for video generation task statuses."""
    PENDING = "PENDING"       # Task received, awaiting processing start
    QUEUED = "QUEUED"         # Task sent to the async worker queue
    PROCESSING = "PROCESSING"   # Task is actively being processed by Alibaba Cloud
    SUCCEEDED = "SUCCEEDED"     # Task completed successfully, video available
    FAILED = "FAILED"         # Task failed during generation or upload
    API_ERROR = "API_ERROR"     # An error occurred trying to query or interact with the Alibaba API itself

# --- Models --- #

class VideoTask(db.Model):
    """
    Represents a video generation task in the database.
    Linked to the ChatMessage that initiated it.
    """
    __tablename__ = 'video_tasks'

    # --- Core Identification ---
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)

    # --- Link to Source Message --- #
    source_message_id = Column(Integer, ForeignKey('chat_messages.id'), nullable=True, index=True)
    source_message = relationship("ChatMessage", back_populates="video_tasks")  # 改为复数形式

    # --- Input Data --- #
    prompt = Column(Text, nullable=False)  # 可编辑的提示词
    script_data = Column(JSON, nullable=True)  # 原始场景数据备份，结构不固定

    # --- Task Status & Results --- #
    status = Column(
        SQLAlchemyEnum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True
    )
    aliyun_task_id = Column(String(128), nullable=True, index=True)
    video_url = Column(String(1024), nullable=True)
    url_expires_at = Column(DateTime(timezone=True), nullable=True)
    obs_object_key = Column(String(512), nullable=True)  # 存储在OBS中的对象键


    # --- Error Information --- #
    error_code = Column(String(128), nullable=True)
    error_message = Column(Text, nullable=True)

    # --- Timestamps --- #
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f'<VideoTask {self.id} [{self.status.value}] User: {self.user_id}>'

    # --- Helper Methods --- #

    def set_status(self, status: str, commit: bool = True):
        """Helper method to update the status and finished_at timestamp."""
        self.status = status
        if status in ['SUCCEEDED', 'FAILED', 'API_ERROR']:
            self.finished_at = datetime.now(timezone.utc)
        db.session.add(self)
        if commit:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e

    def set_success(self, video_url: str, obs_object_key: str, url_expires_at: datetime, commit: bool = True):
        """Marks the task as succeeded and saves the video URL with expiration time."""
        self.video_url = video_url
        self.obs_object_key = obs_object_key
        self.url_expires_at = url_expires_at
        self.error_code = None
        self.error_message = None
        self.set_status('SUCCEEDED', commit=commit)

    def set_failure(self, error_code: Optional[str] = None, error_message: Optional[str] = None, commit: bool = True):
        """Marks the task as failed and saves error details."""
        self.error_code = error_code
        self.error_message = error_message
        self.set_status('FAILED', commit=commit)

    @property
    def needs_url_refresh(self) -> bool:
        """检查URL是否需要刷新（过期时间前24小时）"""
        if not self.url_expires_at:
            return True
        refresh_threshold = datetime.now(timezone.utc) + timedelta(hours=24)
        return self.url_expires_at <= refresh_threshold

# --- Migration Reminder --- #
# Remember to run database migrations after changing models:
# flask db migrate -m "Add VideoTask model linked to ChatMessage"
# flask db upgrade 

```
#### api
需要增加几个api:
1. text, model 为入参，生成html代码
参考代码：
```python
@mj_bp.route('/parse-script', methods=['POST'])
@jwt_required()
def parse_script_to_tasks():
    """解析文本脚本并直接创建图片生成任务
    
    请求体格式:
    {
        "script": "要解析的文本内容",
        "message_id": "20240120123456789"  # 必填，关联的消息ID
    }
    
    返回格式:
    {
        "code": 0,
        "message": "解析成功",
        "data": {
            "id": 1,
            "user_imagine_id": 123,
            "status": "WAITING",
            "prompt": "...",
            "oss_image_url": null,
            "actions_json": null
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'script' not in data:
            return error_response('缺少必要的脚本内容')
            
        if 'message_id' not in data:
            return error_response('缺少必要的消息ID')
            
        script_text = data['script']
        message_id = data['message_id']
        # query user from db
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return error_response('用户不存在')
        phone_number = user.phone
        
        # 获取消息实例
        message = ChatMessage.query.filter_by(message_id=message_id, type="assistant").first()
        if not message:
            return error_response('关联的消息不存在')
            
        # 提取提示词
        prompt = extract_image_prompt(script_text, user_id)
        if not prompt:
            return error_response('未找到有效的图片生成提示词')
            
        # 直接调用生成图片函数
        success, error_msg, result = generate_image(
            user_id=user_id,
            phone_number=phone_number,
            prompt=prompt,
            message=message
        )
        
        if not success:
            return error_response(error_msg)
        try:
            check_mj_task_statuses.delay()
        except Exception as e:
            logger.error(f"Failed to queue task check_mj_task_statuses: {e}")
        return success_response('生图任务已创建', result)
        
    except Exception as e:
        logger.error(f"Error in parse_script_to_tasks: {e}")
        return error_response('解析脚本失败')

```
2. 根据message_id 列表， 获取对应消息的html代码
参考代码：
```python
@mj_bp.route('/messages/tasks', methods=['GET'])
@jwt_required()
def get_message_mj_tasks():
    """获取指定消息ID列表对应的图片任务信息
    
    Query参数:
    - message_ids: 逗号分隔的消息ID列表，例如: ?message_ids=688,689,690
    
    返回格式:
    {
        "code": 0,
        "message": "获取成功",
        "data": {
            "688": [  # 按消息ID分组
                {
                    "id": 1,
                    "status": "WAITING",
                    "prompt": "...",
                    "oss_image_url": "...",
                    "created_at": "2024-01-20T10:00:00Z",
                    ...
                },
                ...
            ],
            "689": [...],
            ...
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        
        # 获取并验证消息ID列表
        message_ids_str = request.args.get('message_ids', '')
        if not message_ids_str:
            return error_response('消息ID列表不能为空')
            
        try:
            message_ids = [int(id.strip()) for id in message_ids_str.split(',') if id.strip()]
        except ValueError:
            return error_response('消息ID格式错误')
            
        # 查询图片任务
        tasks = MJTask.query.filter(
            MJTask.user_id == user_id,
            MJTask.message_id.in_(message_ids)
        ).all()
        
        # 按消息ID分组整理结果
        result = {}
        for task in tasks:
            msg_id = task.message_id
            if msg_id not in result:
                result[msg_id] = []
                
            result[msg_id].append({
                'id': task.id,
                'status': task.status.value,
                'prompt': task.prompt,
                'user_imagine_id': task.user_imagine_id,
                'image_id': task.image_id,
                'oss_image_url': task.oss_image_url,  # 改用 oss_image_url
                'actions_json': task.actions_json,
                'error_show': task.error_show,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None
            })
            
        return success_response('获取成功', result)
        
    except Exception as e:
        logger.error(f"Error in get_message_mj_tasks: {e}")
        return error_response('服务器内部错误')

```

### 前端

自定义一个新的组件，就叫 HtmlPreview.vue
有3个参数。
一个是message_id，
一个是html_code
一个是message 
如果没有html_code, 就有 生成html的按钮，点击就调用 html/generate 生成html.

如果html_code 存在， 就展示 立即查看 和 下载 按钮。
点击立即查看后，可以显示一个可关闭的浮层。浮层的内容 用iframe来展示html代码

点击下载后，下载html文件

HtmlPreview.vue 需要在 ChatDetail.vue 和 ChatDialog.vue 中使用。

有个差别是：
ChatDetail.vue 中， 需要调用 `api/html/messages/html?message_ids=688,689,690` 接口初始化历史消息。
而 ChatDialog.vue 展示的是实时消息，不需要调用。




