from flask import Blueprint, request, current_app, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import NotFound
from app.models.chat import ChatSession, ChatMessage, ChatFile, ChatMessageFile
from app.utils.response import success_response, error_response
from app import db
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.services.dify_service import DifyService
from app.services.branch_service import BranchService
import logging
from app.models.role import Role
import mimetypes
from app.utils.file import allowed_file, get_file_extension, get_mime_type
from obs import ObsClient
import json
from app.utils.time import get_china_time
import urllib.parse
import re
import uuid
from app.utils.logger import get_logger


chat_bp = Blueprint('chat', __name__)
logger = get_logger(__name__)


# 会话列表管理接口
@chat_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    user_id = get_jwt_identity()
    type = request.args.get('type')
    filter = request.args.get('filter', 'all')
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 20))
    
    query = ChatSession.query.filter_by(user_id=user_id)
    
    if type:
        query = query.filter_by(type=type)
    
    if filter == 'starred':
        query = query.filter_by(is_starred=True)
    elif filter == 'archived':
        query = query.filter_by(is_archived=True)
    
    pagination = query.order_by(ChatSession.last_time.desc()).paginate(page=page, per_page=size)
    
    sessions = [{
        'id': session.id,
        'title': session.title,
        'role_id': session.role_id,
        'role_name': session.role.title,
        'role_icon': session.role.icon,
        'last_message': session.last_message,
        'last_time': int(session.last_time.timestamp()) if session.last_time else None,
        'message_count': session.message_count,
        'is_starred': session.is_starred,
        'is_archived': session.is_archived
    } for session in pagination.items]
    
    return success_response('获取成功', {
        'sessions': sessions,
        'total': pagination.total
    })

@chat_bp.route('/sessions/<string:session_id>/rename', methods=['POST'])
@jwt_required()
def rename_session(session_id):
    """重命名会话接口
    
    请求参数:
    {
        "title": "新标题",  // 当 auto_generate 为 false 时必需
        "auto_generate": false  // 是否自动生成标题，默认 false
    }
    
    响应:
    {
        "code": 0,
        "message": "重命名成功",
        "data": {
            "id": "会话ID",
            "title": "新标题",
            "conversation_id": "dify会话ID",
            "updated_at": 1577836800  // 更新时间戳
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        logger.debug(f"Rename request - session_id: {session_id}, data: {data}")
        
        # 验证请求数据
        if not isinstance(data, dict):
            return error_response('无效的请求数据格式')
            
        # 获取参数
        auto_generate = data.get('auto_generate', False)
        title = data.get('title', '').strip() if not auto_generate else None
        
        # 参数验证
        if not auto_generate and not title:
            return error_response('手动重命名时标题不能为空')
            
        # 查找会话
        session = ChatSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first()
        
        if not session:
            logger.error(f"Session not found - session_id: {session_id}")
            return error_response('会话不存在', code=404)
            
        # 确保会话有 conversation_id
        if not session.conversation_id:
            logger.error(f"Session has no conversation_id - session_id: {session_id}")
            return error_response('会话未初始化', code=400)
            
        try:
            # 创建 DifyService 实例
            dify_service = DifyService(api_key=session.role.dify_api_key)
            
            # 调用 Dify API 重命名会话
            response = dify_service.generate_conversation_name(
                conversation_id=session.conversation_id,
                user=str(user_id),
                auto_generate=auto_generate,
                name=title  # 这里传给 Dify 的参数仍然是 name
            )
            
            logger.debug(f"Dify rename response: {response}")
            
            if response and 'name' in response:
                # 更新会话标题
                session.title = response['name']
                session.updated_at = get_china_time()
                db.session.commit()
                
                return success_response('重命名成功', {
                    'id': session.id,
                    'title': session.title,
                    'conversation_id': session.conversation_id,
                    'updated_at': int(session.updated_at.timestamp())
                })
            else:
                return error_response('获取新标题失败', code=500)
                
        except Exception as e:
            logger.error(f"Failed to rename session: {str(e)}", exc_info=True)
            db.session.rollback()
            return error_response('重命名失败，请稍后重试', code=500)
            
    except Exception as e:
        logger.error(f"Unexpected error in rename_session: {str(e)}", exc_info=True)
        return error_response('服务器错误', code=500)

@chat_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    """删除会话"""
    try:
        user_id = get_jwt_identity()
        
        # 验证会话存在且属于当前用户
        session = ChatSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first_or_404()
        
        try:
            # 开启事务
            with db.session.begin_nested():
                # 1. 删除会话关联的消息文件关系
                message_ids = [msg.id for msg in session.messages]
                if message_ids:
                    ChatMessageFile.query.filter(
                        ChatMessageFile.message_id.in_(message_ids)
                    ).delete(synchronize_session=False)
                
                # 2. 删除会话的所有消息
                ChatMessage.query.filter_by(session_id=session_id).delete()
                
                # 3. 删除会话本身
                db.session.delete(session)
            
            # 提交事务
            db.session.commit()
            
            return success_response('删除成功')
            
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            db.session.rollback()
            return error_response('删除失败，请重试', code=500)
            
    except NotFound:
        return error_response('会话不存在', code=404)
    except Exception as e:
        logger.error(f"Unexpected error in delete_session: {str(e)}")
        return error_response('服务器错误', code=500)

@chat_bp.route('/sessions/<int:session_id>/star', methods=['PUT'])
@jwt_required()
def star_session(session_id):
    user_id = get_jwt_identity()
    session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first_or_404()
    
    data = request.get_json()
    is_starred = data.get('is_starred', False)
    
    session.is_starred = is_starred
    db.session.commit()
    
    return success_response('操作成功', {
        'id': session.id,
        'is_starred': session.is_starred
    })

@chat_bp.route('/sessions/<int:session_id>/archive', methods=['PUT'])
@jwt_required()
def archive_session(session_id):
    user_id = get_jwt_identity()
    session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first_or_404()
    
    data = request.get_json()
    is_archived = data.get('is_archived', False)
    
    session.is_archived = is_archived
    db.session.commit()
    
    return success_response('操作成功', {
        'id': session.id,
        'is_archived': session.is_archived
    })

# 会话消息管理接口
@chat_bp.route('/sessions/<int:session_id>/messages', methods=['GET'])
@jwt_required()
def get_session_messages(session_id):
    """获取会话消息历史
    
    GET 参数:
    - page: 页码，默认1
    - size: 每页大小，默认1000
    - branch_id: 分支ID，默认为当前活跃分支
    - include_context: 是否包含父辈分支上下文，1/0，默认1
    
    返回:
    {
        "code": 0,
        "message": "获取成功",
        "data": {
            "messages": [
                {
                    "id": 123,
                    "content": "消息内容",
                    "type": "user/assistant",
                    "timestamp": 1577836800,
                    "files": [
                        {
                            "id": 1,
                            "name": "文件名",
                            "url": "文件地址",
                            "type": "文件类型",
                            "size": 1024
                        }
                    ],
                    "branchId": 0,
                    "position": 1,
                    "nextBranches": {
                        "count": 2,
                        "branches": [
                            {"id": 0, "title": "主分支", "branch_id": 0},
                            {"id": 5, "title": "分支 5", "branch_id": 5}
                        ],
                        "current_branch_index": 0
                    }
                }
            ],
            "total": 100,
            "activeBranchId": 0
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 1000, type=int)
        include_context = request.args.get('include_context', 1, type=int) == 1
        message_id = request.args.get('message_id', type=str)  # 新增 message_id 参数
        # 查消息
        message = ChatMessage.query.filter_by(message_id=message_id).first()
        if not message:
            return error_response('消息不存在', code=404)
        message_id = message.id
        
        # 获取会话
        session = ChatSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first_or_404()
        
        # 获取分支ID参数，默认使用会话当前活跃分支
        branch_id = int(request.args.get('branch_id', session.active_branch_id))
        
        # 根据include_context参数决定使用哪个方法获取消息
        if include_context:
            # 获取包含父辈上下文的所有消息
            all_messages = BranchService.get_branch_messages(session_id, branch_id)
        else:
            # 只获取当前分支的消息，不包含父辈上下文
            all_messages = BranchService.get_branch_messages_only(session_id, branch_id)
            
        # 如果指定了message_id，只返回id >= message_id的消息
        if message_id:
            all_messages = [msg for msg in all_messages if msg.id >= message_id]
        
        # 计算总消息数
        total_messages = len(all_messages)
        
        # 手动分页
        start_idx = (page - 1) * size
        end_idx = min(start_idx + size, total_messages)
        
        # 获取当前页的消息
        paginated_messages = all_messages[start_idx:end_idx]
        
        # 检查是否存在任何分支
        has_any_branches = db.session.query(ChatMessage.branch_id)\
            .filter(ChatMessage.session_id == session_id,
                   ChatMessage.branch_id > 0)\
            .first() is not None

        # 格式化消息
        messages = []
        for message in paginated_messages:
            # 获取文件列表
            files = []
            message_files = ChatMessageFile.query.filter_by(message_id=message.id).all()
            for message_file in message_files:
                chat_file = ChatFile.query.get(message_file.file_id)
                if chat_file:
                    files.append({
                        'id': chat_file.id,
                        'name': chat_file.name,
                        'size': chat_file.size,
                        'type': chat_file.type,
                        'url': chat_file.url,
                        'obs_preview_url': chat_file.obs_preview_url
                    })
            
            # 获取后续分支信息
            next_branches_info = None
            if message.type == 'user' and has_any_branches:  # 只在存在分支且是用户消息时获取分支信息
                next_branches_info = BranchService.get_next_branches_info(session_id, message.id,branch_id)
                
                # 重要:始终确保current_branch_index与实际分支匹配
                if next_branches_info and 'branches' in next_branches_info:
                    active_branch_id = branch_id  # 使用请求中指定的分支ID
                    
                    # 查找活跃分支在分支列表中的索引
                    current_branch_index = 0
                    for index, branch in enumerate(next_branches_info['branches']):
                        if branch['branch_id'] == active_branch_id:
                            current_branch_index = index
                            break
                    
                    # 更新current_branch_index
                    next_branches_info['current_branch_index'] = current_branch_index
                    logger.debug(f"更新分支索引 - 活跃分支ID: {active_branch_id}, 索引: {current_branch_index}")
            
            messages.append({
                'id': message.id,
                'message_id': message.message_id,
                'content': message.content,
                'type': message.type,
                'timestamp': int(message.timestamp.timestamp()),
                'files': files,
                'api_status': message.api_status,
                'api_usage': message.api_usage,
                'retriever_resources': message.retriever_resources,
                'feedback_rating': message.feedback_rating,
                'branch_id': message.branch_id,
                'position': message.position,
                'next_branches': next_branches_info,
                'parent_branch_id': message.parent_branch_id,  # 添加父分支ID
                'fork_from_id': message.fork_from_id,  # 添加分叉来源ID
                'branch_path': message.branch_path  # 添加分支路径
            })
        
        return success_response('获取成功', {
            'messages': messages,
            'total': total_messages,
            'active_branch_id': session.active_branch_id,
            'has_more': page < (total_messages // size) + (total_messages % size > 0),
            'session': {
                'id': session.id,
                'title': session.title,
                'role_id': session.role_id,
                'role_name': session.role.title,
                'role_icon': session.role.icon,
                'active_branch_id': session.active_branch_id,
                'type': session.type,
                'message_count': session.message_count,
                'is_starred': session.is_starred,
                'is_archived': session.is_archived,
                'created_at': int(session.created_at.timestamp()),
                'last_message': session.last_message,
                'last_time': int(session.last_time.timestamp()) if session.last_time else None
            }
        })
        
    except NotFound:
        return error_response('会话不存在', code=404)
    except Exception as e:
        logger.error(f"Error getting session messages: {str(e)}")
        return error_response('获取消息失败', code=500)

def _send_message_to_dify(user_id, content, conversation_id=None, files=None, role=None):
    """发送消息到 Dify 的通用方法"""
    try:
        # 使用角色的 API Key 创建 DifyService 实例
        if not role or not role.dify_api_key:
            logger.error(f"Role {role.id if role else 'None'} does not have a valid Dify API Key")
            raise ValueError("Invalid role configuration")
            
        dify_service = DifyService(api_key=role.dify_api_key)
        logger.debug(f"Using Dify API Key from role {role.id}")
        
        logger.debug(f"Sending message with fileIds: {files}")
        
        response = dify_service.chat_messages_stream(
            query=content,
            inputs={},
            user=str(user_id),
            conversation_id=conversation_id,
            files=files
        )
        return response
    except Exception as e:
        logger.error(f"Failed to send message to Dify: {str(e)}")
        raise

def _save_files_to_db( user_message_id,  files=None):
    """保存消息到数据库的通用方法"""
    try:
        logger.info(f"Starting _save_files_to_db - session_id: {user_message_id}")
        # 添加文件关联
        if files:
            for file in files:
                chat_message_file = ChatMessageFile(
                    message_id=user_message_id,
                    file_id=file.id,
                    created_at=get_china_time()
                )
                db.session.add(chat_message_file)
                logger.debug(f"Added file association - message_id: {user_message_id}, file_id: {file.id}")
        
            db.session.commit()
    except Exception as e:
        logger.error(f"Error _save_files_to_db: {str(e)}")
        db.session.rollback()
        raise

def _generate_session_title(conversation_id, user_id):
    """使用 Dify API 生成会话标题"""
    try:
        dify_service = DifyService()
        response = dify_service.generate_conversation_name(
            conversation_id=conversation_id,
            user=str(user_id),
            auto_generate=True
        )
        if response and 'name' in response:
            return response['name']
    except Exception as e:
        logger.error(f"Failed to generate session title: {str(e)}")
    return None

@chat_bp.route('/messages', methods=['POST'])
@jwt_required()
def send_message():
    """统一的消息发送接口（支持创建会话和编辑消息）"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        session_id = data.get('session_id')
        role_id = data.get('role_id')
        content = data.get('content')
        file_ids = data.get('file_ids', [])
        session_type = data.get('session_type')
        parent_message_id = data.get('parent_message_id')  # 父消息ID
        branch_id = data.get('branch_id')  # 添加分支ID参数
        model = data.get('model','gpt') # 模型类型,
        
        # 记录消息请求（生产环境保留）
        logger.info(f"收到消息请求 - 用户ID: {user_id}, 文件数量: {len(file_ids)}, 内容长度: {len(content) if content else 0}")
        
        # 初始化变量
        is_new_session = False
        is_new_branch = False
        new_branch_id = None
        branch_path = None
        parent_branch_id = None
        
        if not session_type:
            return error_response('session_type 不能为空，会话类型：single_role/targeted/team')
        
        if not content and not file_ids:
            return error_response('消息内容和文件不能同时为空')
        
        # 处理会话
        if session_id:
            session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
            if not session:
                return error_response('会话不存在')
            role = session.role  # 获取会话关联的角色
            
            # 如果指定了父消息ID，创建新分支而不是删除消息
            if parent_message_id:
                # 查找父消息
                parent_message = ChatMessage.query.filter_by(
                    message_id=parent_message_id,
                    session_id=session_id
                ).first()
                
                if not parent_message:
                    logger.error(f"Parent message not found - parent_message_id: {parent_message_id}, session_id: {session_id}")
                    return error_response('指定的父消息不存在')
                
                logger.info(f"Processing branch creation - parent_message_id: {parent_message_id}, session_id: {session_id}")
                
                # 获取当前最大分支ID
                max_branch_query = db.session.query(db.func.max(ChatMessage.branch_id)).filter_by(
                    session_id=session_id
                )
                max_branch_id = max_branch_query.scalar() or 0
                
                # 创建新分支ID
                new_branch_id = max_branch_id + 1
                session.active_branch_id = new_branch_id
                db.session.commit()
                
                # 设置新分支的父分支和路径
                parent_branch_id = parent_message.branch_id or 0
                if parent_message.branch_path:
                    branch_path = f"{parent_message.branch_path}/{new_branch_id}"
                else:
                    branch_path = f"0/{new_branch_id}"
                
                # 标记为新分支
                is_new_branch = True
                branch_id = new_branch_id
                
                logger.info(f"Created new branch - branch_id: {new_branch_id}, parent_branch_id: {parent_branch_id}, branch_path: {branch_path}")
        else:
            if not role_id:
                return error_response('roleId 不能为空')
                
            role = Role.query.get(role_id)
            if not role:
                return error_response('角色不存在')
            # 创建新会话，使用临时标题
            session = ChatSession(
                user_id=user_id,
                role_id=role_id,
                type=session_type,
                title="新会话",  # 临时标题，稍后会更新
                message_count=0,
                last_time=get_china_time(),
                active_branch_id=0  # 初始使用主分支
            )
            db.session.add(session)
            db.session.flush()
            logger.debug(f"Created new session with id {session.id}")
            is_new_session = True
            branch_id = 0  # 新会话默认使用主分支
            
        # 检查角色的 API Key
        if not role.dify_api_key:
            logger.error(f"Role {role.id} does not have a Dify API Key configured")
            return error_response('该角色未正确配置，请联系管理员', code=500)
            
        # 创建 DifyService 实例
        dify_service = DifyService(api_key=role.dify_api_key)
        
        def generate():
            nonlocal session, is_new_session, is_new_branch, new_branch_id, branch_path, parent_branch_id,parent_message_id
            full_response = ""
            message_id = None
            assistant_message_id = None
            first_message = True
            
            try:
                # 获取当前分支中最大的position值
                max_position = db.session.query(db.func.max(ChatMessage.position)).filter_by(
                    session_id=session.id,
                    branch_id=branch_id
                ).scalar() or 0
                
                # 创建用户消息记录，添加分支相关字段
                user_message = ChatMessage(
                    session_id=session.id,
                    content=content,
                    type='user',
                    timestamp=get_china_time(),
                    api_status='success',
                    branch_id=branch_id,
                    position=max_position + 1
                )
                
                # 处理分支路径
                if is_new_branch:
                    # 如果是新创建的分支，设置分支相关信息
                    user_message.parent_branch_id = parent_branch_id
                    user_message.fork_from_id = parent_message.id if 'parent_message' in locals() else None
                    user_message.branch_path = branch_path
                elif branch_id != 0:
                    # 非主分支且不是新创建的分支，获取当前分支的路径
                    branch_message = ChatMessage.query.filter_by(
                        session_id=session.id,
                        branch_id=branch_id
                    ).first()
                    
                    if branch_message and branch_message.branch_path:
                        user_message.branch_path = branch_message.branch_path
                    else:
                        # 如果找不到分支信息，默认设置为"0/{branch_id}"
                        user_message.branch_path = f"0/{branch_id}"
                else:
                    user_message.branch_path = "0"  # 主分支路径
                
                db.session.add(user_message)
                db.session.flush()
                if file_ids:
                    files = ChatFile.query.filter(ChatFile.dify_file_id.in_(file_ids)).all()
                    _save_files_to_db(user_message.id, files)
                
                # 修改构造文件参数的部分
                files_for_message = []
                
                for dify_file_id in file_ids:
                    # 根据 dify_file_id 查找对应的 chat_file
                    chat_file = ChatFile.query.filter_by(
                        dify_file_id=dify_file_id,
                        user_id=user_id
                    ).first()
                    
                    if chat_file:
                        # 根据文件扩展名判断类型，去掉可能存在的点号
                        file_extension = chat_file.type.lower().lstrip('.')
                        file_type = "image" if file_extension in ALLOWED_IMAGE_TYPES else "document"
                        
                        # 直接在发送消息时指定正确的扩展名
                        files_for_message.append({
                            "type": file_type,
                            "transfer_method": "local_file",
                            "upload_file_id": dify_file_id,
                            "extension": file_extension  # 使用 Dify API 需要的字段名
                        })
                        
                        logger.debug(f"添加文件到消息 - 类型: {file_type}, 扩展名: {file_extension}, ID: {dify_file_id}")
                    else:
                        logger.warning(f"未找到文件，dify_file_id: {dify_file_id}")
                
                if files_for_message:
                    logger.info(f"成功处理 {len(files_for_message)} 个文件")
                # 创建助手消息记录，同样添加分支相关字段
                assistant_message = ChatMessage(
                    session_id=session.id,
                    content="",  # 初始为空，后续会更新
                    type='assistant',
                    timestamp=get_china_time(),
                    api_status='streaming',
                    branch_id=branch_id,
                    position=max_position + 2,
                    branch_path=user_message.branch_path
                )
                db.session.add(assistant_message)
                db.session.flush()
                
                # 发送消息到 Dify，添加 parent_message_id 参数
                inputs = {
                    "model_name": model
                }
               
                response = dify_service.chat_messages(
                    query=content,
                    inputs=inputs,
                    response_mode="streaming",
                    user=str(user_id),
                    conversation_id=session.conversation_id,
                    files=files_for_message,
                    parent_message_id=parent_message_id  # 添加父消息ID
                )

                # 调试输出
                logger.info(f"Sending message to Dify - parent_message_id: {parent_message_id}, inputs: {inputs}")
                
                # 如果是新会话，先发送会话信息
                if is_new_session:
                    session_data = {
                        'id': session.id,
                        'title': session.title,
                        'role_id': session.role_id,
                        'role_name': session.role.title,
                        'role_icon': session.role.icon,
                        'type': session.type,
                        'message_count': 0,
                        'is_starred': session.is_starred,
                        'is_archived': session.is_archived,
                        'created_at': int(session.created_at.timestamp()),
                        'last_message': None,
                        'last_time': int(session.last_time.timestamp())
                    }
                    yield f"data: {json.dumps({'event': 'session_created', 'data': session_data})}\n\n"
                
              
                # 处理流式响应
                for line in response.iter_lines():
                    if line:
                        try:
                            line_text = line.decode('utf-8')
                            if not line_text.startswith('data: '):
                                continue
                            
                            json_str = line_text.replace('data: ', '', 1)
                            data = json.loads(json_str)
                            # logger.debug(f"Received data from Dify: {data}")
                            
                            if data['event'] == 'message':
                                # 更新会话ID（如果是新会话）
                                if is_new_session and not session.conversation_id:
                                    conversation_id = data.get('conversation_id')
                                    session.conversation_id = conversation_id
                                    db.session.commit()
                                
                                # 第一条消息时设置用户消息ID和助手消息ID
                                if first_message:
                                    # 设置用户消息ID
                                    message_id = data.get('message_id')
                                    if message_id:
                                        user_message.message_id = message_id
                                        logger.debug(f"Set user message_id: {message_id}")
                                    
                                    # 设置助手消息ID（使用当前消息的ID）
                                    assistant_message.message_id = data.get('id')
                                    logger.debug(f"Set assistant message_id: {data.get('id')}")
                                    
                                    first_message = False
                                
                                # 累积助手回复内容
                                answer = data.get('answer', '')
                                full_response += answer
                                assistant_message.content = full_response
                                
                                # 立即提交更改
                                db.session.commit()
                                
                            elif data['event'] == 'message_end':
                                # 更新消息状态和使用统计
                                assistant_message.api_status = 'success'
                                assistant_message.api_usage = data.get('metadata', {}).get('usage')
                                assistant_message.retriever_resources = data.get('metadata', {}).get('retriever_resources')
                                
                                # 更新会话信息
                                session.message_count += 2
                                session.last_message = full_response
                                session.last_time = get_china_time()
                                
                                # 如果是新会话，自动生成标题
                                if is_new_session and session.conversation_id:
                                    try:
                                        # 调用 Dify API 生成标题
                                        title_response = dify_service.generate_conversation_name(
                                            conversation_id=session.conversation_id,
                                            user=str(user_id),
                                            auto_generate=True
                                        )
                                        
                                        if title_response and 'name' in title_response:
                                            session.title = title_response['name']
                                            # 使用 repr() 来安全地记录可能包含特殊字符的标题
                                            logger.debug(f"Updated session title to: {repr(session.title)}")
                                            # 立即提交标题更新
                                            db.session.commit()
                                            
                                            # 返回更新后的会话信息给前端
                                            session_update_data = {
                                                'event': 'session_updated',
                                                'data': {
                                                    'id': session.id,
                                                    'title': session.title,
                                                    'conversation_id': session.conversation_id
                                                }
                                            }
                                            yield f"data: {json.dumps(session_update_data)}\n\n"
                                        else:
                                            logger.warning("Failed to get title from Dify API")
                                            
                                    except Exception as e:
                                        logger.error(f"Failed to generate session title: {str(e)}")
                                        # 如果获取标题失败，使用默认标题
                                        session.title = f"新会话 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                        db.session.commit()
                                
                                db.session.commit()
                                
                                # 验证 assistant_message_id 是否正确设置
                                if not assistant_message.message_id:
                                    logger.error("Failed to set assistant message_id")
                                else:
                                    logger.debug(f"Final assistant message_id: {assistant_message.message_id}")
                            
                            yield line_text + '\n\n'
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error: {str(e)}")
                            continue
                        except Exception as e:
                            logger.error(f"Error processing message: {str(e)}")
                            continue
                  # 如果是新分支，发送分支创建信息
                if is_new_branch:
                    branch_data = {
                        'branch_id': new_branch_id,
                        'parent_branch_id': parent_branch_id,
                        'parent_message_id': parent_message_id if 'parent_message_id' in locals() else None
                    }
                    yield f"data: {json.dumps({'event': 'branch_created', 'data': branch_data})}\n\n"
               
                            
            except Exception as e:
                logger.error(f"Stream error: {str(e)}")
                error_data = {
                    'event': 'error',
                    'message': str(e)
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                raise

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"Session handling error: {str(e)}")
        db.session.rollback()
        raise
        
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        return error_response('消息发送失败，请稍后重试')

@chat_bp.route('/sessions/<int:session_id>/messages/<string:task_id>/stop', methods=['POST'])
@jwt_required()
def stop_message(session_id, task_id):
    """停止消息响应"""
    try:
        user_id = get_jwt_identity()
        
        # 验证会话存在且属于当前用户
        session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first_or_404()
        
        # 验证消息存在 - 修改查询条件
        message = ChatMessage.query.filter_by(
            session_id=session_id,
            message_id=task_id  # 只用 session_id 和 task_id 查询
        ).first()
        
        if not message:
            logger.error(f"No message found with task_id: {task_id}")
            return error_response('找不到对应的消息', code=404)
            
        # 检查消息状态
        if message.api_status not in ['streaming', 'success']:  # 允许停止 streaming 和 success 状态的消息
            logger.error(f"Message {task_id} is in {message.api_status} state, cannot be stopped")
            return error_response('消息已经停止或出错', code=400)
        
        try:
            # 调用 Dify API 停止响应
            dify_service = DifyService()
            response = dify_service.stop_chat_message(task_id, str(user_id))
            
            # 更新消息状态
            message.api_status = 'stopped'
            db.session.commit()
            
            logger.info(f"Successfully stopped message {task_id} for session {session_id}")
            return success_response('停止成功')
            
        except Exception as e:
            logger.error(f"Failed to stop message via Dify API: {str(e)}")
            # 如果是 404 错误，说明消息已经结束
            if "Task not found" in str(e):
                message.api_status = 'success'  # 更新状态为成功
                db.session.commit()
                return error_response('消息已经结束', code=400)
            return error_response('停止失败：与AI服务通信失败', code=502)
        
    except Exception as e:
        logger.error(f"Stop message error: {str(e)}")
        return error_response('停止失败，请稍后重试', code=500)

# 在文件上传函数之前添加允许的文件类型常量
ALLOWED_DOCUMENT_TYPES = {
    'txt', 'md', 'markdown', 'pdf', 'html', 'xlsx', 
    'xls', 'docx', 'csv', 'eml', 'msg', 'pptx', 
    'ppt', 'xml', 'epub'
}

ALLOWED_IMAGE_TYPES = {
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'
}

# 更新文件类型验证函数
def allowed_file(filename):
    """检查文件类型是否允许"""
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_DOCUMENT_TYPES or extension in ALLOWED_IMAGE_TYPES

# 更新文件类型判断函数
def get_file_type(filename):
    """获取文件类型（document/image）"""
    if '.' not in filename:
        return None
    extension = filename.rsplit('.', 1)[1].lower()
    if extension in ALLOWED_IMAGE_TYPES:
        return 'image'
    elif extension in ALLOWED_DOCUMENT_TYPES:
        return 'document'
    return None

def get_extension_from_mime_type(mime_type):
    """从 MIME 类型获取文件扩展名"""
    mime_to_ext = {
        'application/pdf': 'pdf',
        'application/msword': 'doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
        'text/plain': 'txt',
        'text/markdown': 'md',
        'text/html': 'html',
        'text/csv': 'csv',
        'message/rfc822': 'eml',
        'application/xml': 'xml',
        'application/epub+zip': 'epub',
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif',
        'image/webp': 'webp',
        'image/svg+xml': 'svg'
    }
    return mime_to_ext.get(mime_type.lower())

@chat_bp.route('/files/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """上传文件"""
    try:
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            logger.error("No file part in request.files")
            return error_response('没有文件')
        
        file = request.files['file']
        if file.filename == '':
            logger.error("No selected file")
            return error_response('没有选择文件')
        
        # 获取原始文件名和 MIME 类型
        original_filename = file.filename
        mime_type = file.content_type
        logger.debug(f"Original filename: {original_filename}, MIME type: {mime_type}")
        
        # 优先从 MIME 类型获取扩展名
        file_extension = get_extension_from_mime_type(mime_type)
        
        # 如果从 MIME 类型无法获取扩展名，尝试从文件名获取
        if not file_extension and '.' in original_filename:
            file_extension = original_filename.rsplit('.', 1)[1].lower().lstrip('.')  # 确保去掉点号
            # 验证扩展名是否在允许列表中
            if file_extension not in ALLOWED_DOCUMENT_TYPES and file_extension not in ALLOWED_IMAGE_TYPES:
                file_extension = None
        
        if not file_extension:
            logger.error(f"Unsupported file type: {mime_type}")
            return error_response('不支持的文件类型')
        
        # 生成安全的文件名
        safe_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}.{file_extension}"
        logger.debug(f"Generated safe filename: {safe_filename}")
        
        # 确定文件类型（document/image）
        file_type = "image" if file_extension in ALLOWED_IMAGE_TYPES else "document"
        
        # 获取文件大小
        file_size = file.content_length
        
        try:
            # 初始化 OBS 客户端
            obs_client = ObsClient(
                access_key_id=current_app.config['OBS_ACCESS_KEY'],
                secret_access_key=current_app.config['OBS_SECRET_KEY'],
                server=current_app.config['OBS_ENDPOINT']
            )
            
            # 生成 OBS 对象键，使用安全的文件名
            obs_object_key = f"advertisting_intelligence_chain/{user_id}/{safe_filename}"
            
            # 直接将文件内容上传到 OBS
            obs_response = obs_client.putObject(
                bucketName=current_app.config['OBS_BUCKET'],
                objectKey=obs_object_key,
                content=file.stream.read()  # 直接读取文件内容
            )
            
            if obs_response.status >= 300:
                logger.error(f"OBS upload failed: {obs_response.errorMessage}")
                return error_response('OBS 上传失败')
            
            # 生成可下载的 OBS 文件的预览地址
            signed_url = obs_client.createSignedUrl(
                'GET',
                current_app.config['OBS_BUCKET'],
                obs_object_key,
                expires=3600
            )
            obs_preview_url = signed_url['signedUrl']
            
            # 获取一个可用的角色来上传文件到 Dify
            role = Role.query.filter(Role.dify_api_key.isnot(None)).first()
            if not role:
                logger.error("No role with valid Dify API key found")
                return error_response('系统配置错误：未找到有效的 Dify API 配置')
            
            # 使用角色的 API Key 创建 DifyService 实例
            dify_service = DifyService(api_key=role.dify_api_key)
            
            # 将文件上传到 Dify
            dify_response = dify_service.upload_file(
                file_path=obs_preview_url,  # 使用 OBS URL 而不是本地文件路径
                user=str(user_id)
            )
            
            # 创建文件记录，使用原始文件名但安全的扩展名
            chat_file = ChatFile(
                user_id=user_id,
                name=original_filename,
                type=file_extension.lstrip('.'),  # 确保去掉点号
                size=file_size,
                url=obs_preview_url,  # 使用 OBS URL
                dify_file_id=dify_response.get('id'),
                obs_object_key=obs_object_key,
                obs_preview_url=obs_preview_url
            )
            
            db.session.add(chat_file)
            db.session.commit()
            
            logger.info(f"File uploaded successfully: {original_filename}, type: {file_extension}")
            
            return success_response('上传成功', {
                'id': chat_file.id,
                'name': chat_file.name,
                'size': chat_file.size,
                'type': chat_file.type,
                'url': chat_file.url,
                'dify_file_id': chat_file.dify_file_id,
                'obs_object_key': chat_file.obs_object_key,
                'obs_preview_url': chat_file.obs_preview_url
            })
            
        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            return error_response('文件上传失败：与服务通信失败')
            
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return error_response('文件上传失败')

@chat_bp.route('/files/<string:dify_file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(dify_file_id):
    """删除文件接口"""
    try:
        user_id = get_jwt_identity()
        logger.info(f"User {user_id} is attempting to delete file with dify_file_id: {dify_file_id}")
        
        # 查找文件
        chat_file = ChatFile.query.filter_by(
            dify_file_id=dify_file_id,
            user_id=user_id
        ).first()
        
        if not chat_file:
            logger.error(f"File not found - dify_file_id: {dify_file_id}")
            return error_response('文件不存在', code=404)
        
        # 删除文件记录
        db.session.delete(chat_file)
        db.session.commit()
        
        logger.info(f"File deleted successfully - dify_file_id: {dify_file_id}")
        return success_response('文件删除成功')
        
    except Exception as e:
        logger.error(f"Failed to delete file: {str(e)}", exc_info=True)
        return error_response('文件删除失败，请稍后重试', code=500)

# 最近会话接口
@chat_bp.route('/sessions/recent', methods=['GET'])
@jwt_required()
def get_recent_sessions():
    user_id = get_jwt_identity()
    limit = int(request.args.get('limit', 10))
    
    sessions = ChatSession.query.filter_by(user_id=user_id)\
        .order_by(ChatSession.last_time.desc())\
        .limit(limit)\
        .all()
    
    return success_response('获取成功', {
        'sessions': [{
            'id': session.id,
            'title': session.title,
            'type': session.type,
            'path': f"/chat/{session.id}",
            'last_message': session.last_message,
            'last_time': int(session.last_time.timestamp()) if session.last_time else None,
            'role_icon': session.role.icon
        } for session in sessions]
    })

@chat_bp.route('/messages/<string:message_id>/feedback', methods=['POST'])
@jwt_required()
def message_feedback(message_id):
    """消息反馈接口"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        logger.debug(f"Feedback request - message_id: {message_id}, data: {data}")
        
        # 验证请求数据
        if not isinstance(data, dict):
            return error_response('无效的请求数据格式')
            
        # 获取参数
        rating = data.get('rating')  # like/dislike/null
        content = data.get('content', '')  # 可选的反馈内容，默认为空字符串
        
        # 验证并转换 rating 参数
        if rating not in ['like', 'dislike', None]:
            return error_response('无效的反馈类型')
        
        # 将 rating 转换为 Dify API 需要的格式
        dify_rating = str(rating) if rating else 'null'
        
        # 查找消息
        message = ChatMessage.query.filter_by(
            message_id=message_id
        ).first()
        
        if not message:
            logger.error(f"Message not found - message_id: {message_id}")
            return error_response('消息不存在', code=404)
            
        # 验证消息所属的会话是否属于当前用户
        if message.chat_session.user_id != user_id:
            logger.error(f"Unauthorized access - user_id: {user_id}, message_id: {message_id}")
            return error_response('无权操作此消息', code=403)
            
        try:
            # 创建 DifyService 实例
            dify_service = DifyService(api_key=message.chat_session.role.dify_api_key)
            
            # 准备发送到 Dify 的数据
            feedback_data = {
                'rating': dify_rating,
                'user': str(user_id)
            }
            if content:
                feedback_data['content'] = content
                
            logger.debug(f"Sending feedback to Dify - data: {feedback_data}")
            
            # 调用 Dify API 发送反馈
            response = dify_service.message_feedback(
                message_id=message_id,
                rating=dify_rating,
                user=str(user_id),
                content=content if content else None
            )
            
            logger.debug(f"Dify feedback response: {response}")
            
            # 更新本地数据库
            message.feedback_rating = rating  # 使用原始 rating
            message.feedback_content = content
            message.feedback_time = get_china_time() if rating is not None else None
            
            db.session.commit()
            logger.info(f"Feedback saved - message_id: {message_id}, rating: {rating}")
            
            return success_response('反馈成功')
            
        except Exception as e:
            logger.error(f"Failed to send feedback: {str(e)}", exc_info=True)
            db.session.rollback()
            return error_response('反馈失败，请稍后重试', code=500)
            
    except Exception as e:
        logger.error(f"Unexpected error in message_feedback: {str(e)}", exc_info=True)
        return error_response('服务器错误', code=500)

@chat_bp.route('/messages/<string:message_id>/suggested', methods=['GET'])
@jwt_required()
def get_suggested_questions(message_id):
    """获取建议问题接口"""
    try:
        user_id = get_jwt_identity()
        
        # 查找消息
        message = ChatMessage.query.filter_by(
            message_id=message_id
        ).first()
        
        if not message:
            return error_response('消息不存在', code=404)
            
        # 验证消息所属的会话是否属于当前用户
        if message.chat_session.user_id != user_id:
            return error_response('无权访问此消息', code=403)
            
        try:
            # 创建 DifyService 实例
            dify_service = DifyService(api_key=message.chat_session.role.dify_api_key)
            
            # 调用 Dify API 获取建议问题
            response = dify_service.get_suggested_questions(
                message_id=message_id,
                user=str(user_id)
            )
            
            # 返回建议问题列表
            return success_response('获取成功', {
                'questions': response.get('data', [])
            })
            
        except Exception as e:
            logger.error(f"Failed to get suggested questions: {str(e)}", exc_info=True)
            return error_response('获取建议问题失败，请稍后重试', code=500)
            
    except Exception as e:
        logger.error(f"Unexpected error in get_suggested_questions: {str(e)}", exc_info=True)
        return error_response('服务器错误', code=500)

@chat_bp.route('/parameters', methods=['GET'])
@jwt_required()
def get_parameters():
    """获取应用参数配置"""
    try:
        user_id = get_jwt_identity()
        role_id = request.args.get('role_id')
        
        # 验证角色
        if not role_id:
            return error_response('role_id 不能为空')
            
        role = Role.query.get(role_id)
        if not role:
            return error_response('角色不存在')
            
        # 检查角色的 API Key
        if not role.dify_api_key:
            logger.error(f"Role {role.id} does not have a Dify API Key configured")
            return error_response('该角色未正确配置，请联系管理员', code=500)
            
        try:
            # 使用角色的 API Key 创建 DifyService 实例
            dify_service = DifyService(api_key=role.dify_api_key)
            # 获取应用参数
            parameters = dify_service.get_parameters()
            
            return success_response('获取成功', parameters)
            
        except Exception as e:
            logger.error(f"Failed to get parameters from Dify: {str(e)}")
            return error_response('获取参数失败', code=500)
            
    except Exception as e:
        logger.error(f"Error getting parameters: {str(e)}")
        return error_response('服务器错误', code=500)

@chat_bp.route('/files/cleanup', methods=['POST'])
@jwt_required()
def cleanup_file():
    """清理上传失败的文件"""
    try:
        data = request.get_json()
        obs_object_key = data.get('obs_object_key')
        
        if not obs_object_key:
            return error_response('缺少必要参数')
            
        # 初始化 OBS 客户端
        obs_client = ObsClient(
            access_key_id=current_app.config['OBS_ACCESS_KEY'],
            secret_access_key=current_app.config['OBS_SECRET_KEY'],
            server=current_app.config['OBS_ENDPOINT']
        )
        
        # 删除 OBS 对象
        try:
            obs_client.deleteObject(
                bucketName=current_app.config['OBS_BUCKET'],
                objectKey=obs_object_key
            )
        except Exception as e:
            logger.error(f"Failed to delete object from OBS: {str(e)}")
            # 即使删除失败也继续处理
            
        return success_response('清理成功')
        
    except Exception as e:
        logger.error(f"File cleanup error: {str(e)}")
        return error_response('清理失败')

# 添加分支相关的API端点



@chat_bp.route('/sessions/<int:session_id>/branches/<int:branch_id>/switch', methods=['PUT'])
@jwt_required()
def switch_branch(session_id, branch_id):
    """切换活跃分支
    
    返回:
    {
        "code": 0,
        "message": "切换成功",
        "data": {
            "branch_id": 1
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        
        # 验证会话归属
        session = ChatSession.query.filter_by(
            id=session_id,
            user_id=user_id
        ).first_or_404()
        
        # 切换分支
        success = BranchService.switch_branch(session_id, branch_id)
        
        if success:
            return success_response('切换成功', {
                'branch_id': branch_id
            })
        else:
            return error_response('切换分支失败', code=400)
        
    except Exception as e:
        logger.error(f"Error switching branch: {str(e)}")
        return error_response('切换分支失败', code=500) 
