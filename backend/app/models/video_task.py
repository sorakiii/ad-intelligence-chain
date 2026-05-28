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
    # 使用字符串形式的关系定义，延迟加载
    source_message = relationship("ChatMessage", back_populates="video_tasks", lazy='select')

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
