from app import db
from datetime import datetime
from sqlalchemy import ForeignKey, Integer, Text, Boolean, JSON, Index, Column, String, Enum
from sqlalchemy.orm import relationship
from .role import Role
from .video_task import VideoTask
from app.utils.time import get_china_time

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(Enum('single_role', 'targeted', 'team'), nullable=False)
    last_message = db.Column(db.Text)
    last_time = db.Column(db.DateTime)
    message_count = db.Column(db.Integer, nullable=False, default=0)
    is_starred = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    conversation_id = db.Column(db.String(100))
    api_status = db.Column(Enum('active', 'archived', 'error'), default='active')
    created_at = db.Column(db.DateTime, default=get_china_time)
    updated_at = db.Column(db.DateTime, default=get_china_time, onupdate=get_china_time)
    active_branch_id = db.Column(db.Integer, default=0)
    
    # 关联
    user = db.relationship('User', backref='chat_sessions')
    role = db.relationship('Role', backref='chat_sessions')
    messages = db.relationship('ChatMessage', backref='chat_session', lazy=True, cascade='all, delete-orphan')

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False)
    message_id = db.Column(db.String(64))
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    api_status = db.Column(db.String(20), default='success')
    api_usage = db.Column(db.JSON)
    retriever_resources = db.Column(db.JSON)
    feedback_rating = db.Column(db.String(20))
    feedback_content = db.Column(db.Text)
    feedback_time = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # 分支相关字段
    branch_id = db.Column(db.Integer, default=0, nullable=False, index=True)
    parent_branch_id = db.Column(db.Integer)
    fork_from_id = db.Column(db.Integer)
    branch_path = db.Column(db.String(255), default='0', nullable=False)
    position = db.Column(db.Integer, default=0, nullable=False)
    
    # 视频任务关联 - 修改为一对多关系
    video_tasks = db.relationship('VideoTask', back_populates='source_message')  # 改为复数形式

    # 消息HTML关联
    message_html = db.relationship("MessageHtml", back_populates="message", uselist=False)
    
    # 文件关联
    files = db.relationship('ChatFile', secondary='chat_message_files', backref='messages')
    
    # 添加与 MJTask 的关联
    mj_task = relationship("MJTask", back_populates="message", uselist=False)
    
    __table_args__ = (
        Index('idx_branch_id_position', 'branch_id', 'position'),
        Index('idx_branch_path', 'branch_path'),
    )

class ChatFile(db.Model):
    __tablename__ = 'chat_files'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(1024), nullable=False)
    created_at = db.Column(db.DateTime, default=get_china_time)
    dify_file_id = db.Column(db.String(100))
    obs_object_key = db.Column(db.String(255))
    obs_preview_url = db.Column(db.String(1024))
    
    # 关联
    user = db.relationship('User', backref='chat_files')

class ChatMessageFile(db.Model):
    __tablename__ = 'chat_message_files'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id', ondelete='CASCADE'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('chat_files.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_china_time) 
