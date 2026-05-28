from app import db
from app.models.chat import ChatSession, ChatMessage, ChatMessageFile, ChatFile
from app.services.dify_service import DifyService
from datetime import datetime
import logging
from app.utils.time import get_china_time
import json

logger = logging.getLogger(__name__)

class BranchService:
    """聊天分支管理服务"""
    
    @staticmethod
    def get_branch_messages(session_id, branch_id=0):
        """获取指定分支的所有消息，包括所有祖先分支的上下文消息
        
        Args:
            session_id: 会话ID
            branch_id: 分支ID，默认为主分支(0)
            
        Returns:
            list: 包含该分支及其所有祖先分支上下文的消息
        """
        return BranchService._get_branch_messages_with_context(session_id, branch_id)

    @staticmethod
    def get_branch_messages_only(session_id, branch_id=0):
        """只获取指定分支的消息，不包含父辈分支的上下文
        
        Args:
            session_id: 会话ID
            branch_id: 分支ID，默认为主分支(0)
            
        Returns:
            list: 仅包含指定分支的消息
        """
        return ChatMessage.query.filter_by(
            session_id=session_id,
            branch_id=branch_id,
            is_deleted=False
        ).order_by(ChatMessage.id.asc()).all()

    @staticmethod
    def _get_branch_messages_with_context(session_id, branch_id=0):
        """获取指定分支的所有消息，包括所有祖先分支的上下文消息
        
        Args:
            session_id: 会话ID
            branch_id: 分支ID，默认为主分支(0)
            
        Returns:
            list: 包含该分支及其所有祖先分支上下文的消息
        """
        # 递归收集所有分支的消息
        def collect_branch_context(current_branch_id, fork_id=None):
            # 如果已到达主分支，获取主分支消息
            if current_branch_id == 0:
                query = ChatMessage.query.filter_by(
                    session_id=session_id,
                    branch_id=0,
                    is_deleted=False
                )
                # 如果有fork_id限制，只获取id严格小于fork_id的消息
                if fork_id is not None:
                    query = query.filter(ChatMessage.id < fork_id)
                return query.order_by(ChatMessage.id.asc()).all()
            
            # 获取当前分支的所有消息
            current_branch_messages = ChatMessage.query.filter_by(
                session_id=session_id,
                branch_id=current_branch_id,
                is_deleted=False
            ).order_by(ChatMessage.id.asc()).all()
            
            # 如果没有消息，表示分支不存在或所有消息已被删除
            if not current_branch_messages:
                return []
            
            # 使用第一条消息获取分支信息
            branch_info = current_branch_messages[0]
            
            # 获取分叉点位置和父分支ID
            parent_branch_id = branch_info.parent_branch_id
            fork_position = branch_info.fork_from_id

            # 直接递归获取父分支的上下文，无需检查分叉点消息是否存在
            if parent_branch_id is not None and fork_position is not None:
                # 递归获取父分支的上下文
                parent_messages = collect_branch_context(parent_branch_id, fork_position)
                
                # 合并消息
                result = parent_messages + current_branch_messages
                return result
            else:
                # 如果没有父分支信息，只返回当前分支的消息
                logger.warning(f"分支 {current_branch_id} 没有有效的父分支信息")
                return current_branch_messages
        
        # 开始递归收集
        return collect_branch_context(branch_id)
    

    @staticmethod
    def switch_branch(session_id, branch_id):
        """切换当前活跃分支（仅用于手动切换已有分支）
        
        Args:
            session_id: 会话ID
            branch_id: 目标分支ID
        
        Returns:
            bool: 是否切换成功
        """
        try:
            # 1. 验证分支是否存在
            branch_exists = False
            if branch_id == 0:  # 主分支总是存在
                branch_exists = True
            else:
                branch_exists = ChatMessage.query.filter_by(
                    session_id=session_id,
                    branch_id=branch_id,
                    is_deleted=False  # 只考虑未删除的消息
                ).first() is not None
            
            if not branch_exists:
                raise ValueError(f"分支 {branch_id} 不存在或所有消息已被删除")
            
            # 2. 更新会话的活跃分支
            session = ChatSession.query.get(session_id)
            if not session:
                raise ValueError("无效的会话ID")
            
            session.active_branch_id = branch_id
            session.updated_at = get_china_time()
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"切换分支失败: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def get_active_branch(session_id):
        """获取会话当前活跃的分支ID
        
        Args:
            session_id: 会话ID
        
        Returns:
            int: 活跃分支ID
        """
        session = ChatSession.query.get(session_id)
        if not session:
            return 0
        return session.active_branch_id

    @staticmethod
    def get_next_branches_info(session_id: int, message_id: int, branch_id: int):
        """获取指定消息的后续分支信息
        
        Args:
            session_id: 会话ID
            message_id: 当前消息的数据库ID
            branch_id: 当前活跃分支ID
        Returns:
            dict or None: 包含分支数量、分支信息列表及当前分支索引，如果无分支则返回 None
            e.g., { 
                'count': 2, 
                'branches': [
                    {'id': 0, 'title': '主分支', 'branch_id': 0},
                    {'id': 5, 'title': '分支 5', 'branch_id': 5}
                ], 
                'current_branch_index': 0 
            }
        """
        # 获取当前消息
        current_message = ChatMessage.query.get(message_id)
        if not current_message:
            return None
        if current_message.fork_from_id is None and branch_id != 0:
            return None
        if branch_id == 0:
            fork_from_message = current_message
        else:
            fork_from_message = ChatMessage.query.get(current_message.fork_from_id)
        if not fork_from_message:
            return None

        # 获取当前会话的活跃分支ID
        active_branch_id = BranchService.get_active_branch(session_id)
        logger.debug(f"获取分支信息 - 会话ID: {session_id}, 消息ID: {message_id}, 活跃分支ID: {active_branch_id}")
        
        # 简化实现：直接查询以此消息为 fork_from_id 的分支
        next_branch_ids = []
        next_branches = []
        
        # 总是包含原始分支
        original_branch_id = current_message.branch_id
        next_branch_ids.append(original_branch_id)
        
        # 原始分支信息
        original_branch_info = {
            'id': fork_from_message.message_id,
            'branch_id': fork_from_message.branch_id,
            'title': fork_from_message.content
        }
        next_branches.append(original_branch_info)
        
        # 查找所有以此消息为 fork_from_id 的新分支
        forked_messages = ChatMessage.query.filter_by(
            session_id=session_id,
            fork_from_id=fork_from_message.id,
            is_deleted=False
        ).distinct(ChatMessage.branch_id).all()
        
        # 将查询结果添加到分支列表
        for message in forked_messages:
            branch_info = {
                'id': message.message_id,
                'branch_id': message.branch_id,
                'title': message.content
            }
            next_branches.append(branch_info)
        if len(next_branches) == 1:
            return None
        # 确定当前活跃分支在列表中的索引
        current_branch_index = len(next_branches) - 1
        for index, branch in enumerate(next_branches):
            if branch['branch_id'] == active_branch_id:
                current_branch_index = index
                break
        
        # 记录调试信息
        logger.debug(f"分支切换信息 - 分支列表: {[b['branch_id'] for b in next_branches]}, 当前索引: {current_branch_index}")
            
        return {
            'count': len(next_branches),
            'branches': next_branches,
            'current_branch_index': current_branch_index
        } 