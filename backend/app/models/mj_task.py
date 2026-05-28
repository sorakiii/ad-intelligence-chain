from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, JSON, Text, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import db

class MJTaskStatus(str, Enum):
    """MJ 任务状态"""
    WAITING = "WAITING"           # 等待中，可取消
    IN_PROCESSING = "IN_PROCESSING"   # 处理中，需要加快轮询
    SUCCESS = "SUCCESS"           # 生成成功
    FAIL = "FAIL"                # 生成失败
    CANCEL = "CANCEL"            # 已取消

class MJTask(db.Model):
    """MJ 图片生成任务"""
    __tablename__ = 'mj_tasks'

    id = Column(Integer, primary_key=True)
    
    # --- 关联用户 --- #
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship("User")

    # --- 关联消息 --- #
    message_id = Column(Integer, ForeignKey('chat_messages.id'), nullable=True, index=True)
    message = relationship("ChatMessage", back_populates="mj_task")

    # --- 任务信息 --- #
    image_id= Column(String(128), nullable=True, index=True)  # MJ返回的图片ID
    user_imagine_id = Column(Integer, nullable=True, index=True)  # MJ返回的任务ID
    prompt = Column(Text, nullable=False)  # 原始提示词
    opt_uuid = Column(String(128), nullable=True)  # 操作UUID

    # --- 任务状态 --- #
    status = Column(
        SQLAlchemyEnum(MJTaskStatus),
        nullable=False,
        default=MJTaskStatus.WAITING,
        index=True
    )
    
    # --- 结果信息 --- #
    oss_image_url = Column(String(1024), nullable=True)  # OSS存储的图片URL
    actions_json = Column(JSON, nullable=True)  # 可用的操作列表
    
    error_show = Column(Text, nullable=True)

    # --- 父子任务关系 --- #
    parent_task_id = Column(Integer, ForeignKey('mj_tasks.id'), nullable=True)
    parent_task = relationship("MJTask", remote_side=[id], backref="child_tasks")
    action_type = Column(String(64), nullable=True)  # 编辑操作类型：放大/变体/重新生成

    
    # --- 时间戳 --- #
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    api_call_at = Column(DateTime(timezone=True), nullable=True)  # API调用时间
    api_end_at = Column(DateTime(timezone=True), nullable=True)  # API结束时间

    def __repr__(self):
        return f'<MJTask {self.id} [{self.status}] Prompt: {self.prompt[:20]}...>'

    @property
    def is_completed(self) -> bool:
        """任务是否已完成（成功/失败/取消）"""
        return self.status in [MJTaskStatus.SUCCESS, MJTaskStatus.FAIL, MJTaskStatus.CANCEL]

    @property
    def is_cancelable(self) -> bool:
        """任务是否可以取消"""
        return self.status in [MJTaskStatus.WAITING]

    @property
    def should_fast_polling(self) -> bool:
        """是否需要加快轮询"""
        return self.status == MJTaskStatus.IN_PROCESSING
