from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Index, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import db

class MessageHtml(db.Model):
    """
    存储消息生成的 HTML 网页内容
    """
    __tablename__ = 'message_html'
    __table_args__ = (
        Index('ix_message_html_message_id', 'message_id', 'session_id', unique=True),
    )

    # --- Core Identification ---
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('chat_messages.id'), nullable=True)
    message = relationship("ChatMessage", back_populates="message_html")
    # --- Content --- #
    html_code = Column(Text, nullable=False, comment="HTML代码")
    prompt = Column(Text, nullable=False, comment="代码生成提示")
    
    # --- Timestamps --- #
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    status = Column(String(20), default='pending')  # pending/generating/success/failed
    error_message = Column(Text, nullable=True)
    type = Column(Enum('message', 'session', name='message_html_type'), default='message', nullable=False, comment="类型")
    session_id = Column(Integer, nullable=False, default=0, comment="会话ID")

    def __repr__(self):
        return f'<MessageHtml {self.id} Message: {self.message_id}>' 