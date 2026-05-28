"""视频生成相关的 API"""
import time
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.video_task import VideoTask, TaskStatus
from app.models.chat import ChatMessage
from app.utils.response import success_response, error_response
from app.utils.video_generator import AlibabaVideoGenerator
from app.utils.video_convert import convert_script_to_prompts, json_to_video_prompt
from app.utils.logger import get_logger
from app.tasks.video_tasks import check_video_task_statuses
from app import db

video_bp = Blueprint('video', __name__)
logger = get_logger(__name__)


@video_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_video_task(task_id):
    """获取视频生成任务状态"""
    try:
        user_id = get_jwt_identity()
        
        # 获取任务记录
        task = VideoTask.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return error_response('任务不存在')
            
        # 构建响应数据
        response_data = {
            'id': task.id,
            'status': task.status,
            'script_data': task.script_data,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat(),
            'video_url': task.video_url,
            'error_code': task.error_code,
            'error_message': task.error_message
        }
        
        if task.finished_at:
            response_data['finished_at'] = task.finished_at.isoformat()
            
        return success_response('获取成功', response_data)
        
    except Exception as e:
        logger.error(f"Error in get_video_task: {e}")
        return error_response('服务器内部错误')  # 刷新视频URL的签名
@video_bp.route('/tasks/<int:task_id>/refresh-url', methods=['POST'])
@jwt_required()
def refresh_video_url(task_id):
    """刷新视频URL的签名"""
    try:
        user_id = get_jwt_identity()
        
        # 获取任务记录
        task = VideoTask.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return error_response('任务不存在')
            
        if not task.obs_object_key:
            return error_response('视频文件未找到')
            
        # 重新生成签名URL
        from ..utils.obs_uploader import initialize_obs_client, generate_signed_url
        obs_client = initialize_obs_client()
        new_signed_url = generate_signed_url(
            obs_client=obs_client,
            bucket_name=current_app.config['OBS_BUCKET'],
            object_key=task.obs_object_key
        )
        
        # 更新任务记录
        task.video_url = new_signed_url
        db.session.commit()
        
        return success_response('URL刷新成功', {
            'video_url': new_signed_url
        })
        
    except Exception as e:
        logger.error(f"Failed to refresh video URL: {e}")
        return error_response('刷新URL失败')

@video_bp.route('/refresh-all-expired-urls', methods=['POST'])
@jwt_required()
def refresh_all_expired_urls():
    """手动刷新所有过期的视频URL"""
    try:
        user_id = get_jwt_identity()
        
        # 触发刷新任务
        from app.tasks.video_tasks import refresh_video_urls
        result = refresh_video_urls.delay()
        
        return success_response('刷新任务已启动', {
            'task_id': result.id
        })
        
    except Exception as e:
        logger.error(f"Failed to start refresh task: {e}")
        return error_response('启动刷新任务失败')

@video_bp.route('/messages/tasks', methods=['GET'])
@jwt_required()
def get_message_video_tasks():
    """获取指定消息ID列表对应的视频任务信息
    
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
                    "status": "SUCCEEDED",
                    "video_url": "...",
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
            
        # 查询视频任务
        tasks = VideoTask.query.filter(
            VideoTask.user_id == user_id,
            VideoTask.source_message_id.in_(message_ids)
        ).all()
        
        # 按消息ID分组整理结果
        result = {}
        for task in tasks:
            msg_id = task.source_message_id
            if msg_id not in result:
                result[msg_id] = []
                
            result[msg_id].append({
                'id': task.id,
                'status': task.status,
                'script_data': task.script_data,
                'prompt': task.prompt,
                'video_url': task.video_url,
                'error_code': task.error_code,
                'error_message': task.error_message,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                'finished_at': task.finished_at.isoformat() if task.finished_at else None
            })
            
        return success_response('获取成功', result)
        
    except Exception as e:
        logger.error(f"Error in get_message_video_tasks: {e}")
        return error_response('服务器内部错误')

def create_video_tasks_for_message(user_id: int, message: ChatMessage, data: dict) -> list:
    """
    为消息创建视频任务
    
    Args:
        user_id: 用户ID
        message: ChatMessage实例
        data: 包含title和其他视频生成相关数据的字典
    
    Returns:
        list: 创建的任务列表
    """
    try:
        # 使用 convert_script_to_prompts 转换为多个提示词
        prompts = convert_script_to_prompts(data)
        if not prompts:
            return []
            
        created_tasks = []
        for prompt_data in prompts:
            # 创建视频任务记录
            video_task = VideoTask(
                user_id=user_id,
                source_message_id=message.id,
                prompt=prompt_data['prompt'],
                script_data=prompt_data['script_data'],
                status=TaskStatus.PENDING  # 初始状态为 PENDING
            )
            
            # 保存任务记录
            db.session.add(video_task)
            db.session.flush()  # 获取生成的 task.id
            
            created_tasks.append({
                'id': video_task.id,
                'status': video_task.status,
                'prompt': video_task.prompt,
                'script_data': video_task.script_data,
                'video_url': None
            })
        
        # 提交事务
        db.session.commit()
        
        return created_tasks
        
    except Exception as e:
        logger.error(f"Error creating video tasks: {e}")
        db.session.rollback()
        raise

@video_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_video_task(task_id):
    """更新视频生成任务"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 获取任务记录
        task = VideoTask.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return error_response('任务不存在')
            
        # 验证提示词
        prompt = data.get('prompt')
        if not prompt or not prompt.strip():
            return error_response('提示词不能为空')
            
        # 更新任务状态和清空视频相关字段
        task.prompt = prompt.strip()
        task.video_url = None  # 清空视频URL
        task.obs_object_key = None  # 清空OSS对象键
        task.status = TaskStatus.PROCESSING  # 设置为处理中状态
        
        # 调用视频生成服务创建新任务
        try:
            api_key = current_app.config.get('DASHSCOPE_API_KEY')
            generator = AlibabaVideoGenerator(api_key=api_key)
            result = generator.create_video_task(prompt=prompt)
            
            task.aliyun_task_id = result
            db.session.commit()
            check_video_task_statuses.delay()
            return success_response('视频任务更新成功', {
                'task_id': task.id,
                'aliyun_task_id': task.aliyun_task_id,
                'status': task.status
            })
            
        except Exception as e:
            logger.error(f"Failed to create new video task: {e}")
            return error_response('创建新视频任务失败')
            
    except Exception as e:
        logger.error(f"Error in update_video_task: {e}")
        return error_response('服务器内部错误')  # 刷新视频URL的签名

@video_bp.route('/parse-script', methods=['POST'])
@jwt_required()
def parse_script_to_tasks():
    """解析文本脚本并创建视频任务
    
    请求体格式:
    {
        "script": "要解析的文本内容",
        "message_id": "20240120123456789"  # 必填，关联的消息ID（字符串格式）
    }
    
    返回格式:
    {
        "code": 0,
        "message": "解析成功",
        "data": {
            "tasks": [
                {
                    "id": 1,
                    "status": "PENDING",
                    "prompt": "...",
                    "script_data": {...},
                    ...
                },
                ...
            ]
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
        
        # 调用 DifyService 解析脚本
        from app.services.dify_service import DifyService
        api_key = current_app.config.get('DIFY_API_KEY_VIDEO_SCRIPT') or current_app.config.get('DIFY_API_KEY')
        if not api_key:
            return error_response('视频脚本解析服务未配置 Dify API Key')
        dify_service = DifyService(api_key=api_key)
        script_json = dify_service.convert_script_to_json(script_text, str(user_id))
        
        # 获取消息实例
        from app.models.chat import ChatMessage
        message = ChatMessage.query.filter_by(message_id=message_id, type="assistant").first()
        if not message:
            return error_response('关联的消息不存在')
            
        # 创建关联到消息的视频任务
        video_tasks = create_video_tasks_for_message(
            user_id=user_id,
            message=message,
            data=script_json
        )
        
        return success_response('解析成功', {
            'message_id': message_id,
            'tasks': video_tasks
        })
        
    except Exception as e:
        logger.error(f"Error in parse_script_to_tasks: {e}")
        return error_response('解析脚本失败')

