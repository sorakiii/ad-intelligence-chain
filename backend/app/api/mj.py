from flask import Blueprint, request, current_app
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.response import success_response, error_response
from app.services.mj_service import MJService
from app.models.mj_task import MJTask, MJTaskStatus
from app import db
from app.tasks.mj_tasks import check_mj_task_statuses
from app.utils.logger import get_logger

from app.models.chat import ChatMessage

logger = get_logger(__name__)

mj_bp = Blueprint('mj', __name__)

def get_mj_service():
    """获取 MJ Service 实例"""
    return MJService(
        base_url=current_app.config['MJ_API_URL'],
        api_key=current_app.config['MJ_API_KEY']
    )

def generate_image(user_id: int, phone_number:str, prompt: str, message: ChatMessage) -> tuple[bool, str, dict]:
    """生成新图片
    
    Args:
        user_id: 用户ID
        prompt: 提示词
        opt_uuid: 可选的UUID
        
    Returns:
        tuple: (是否成功, 错误消息, 返回数据)
    """
    try:
        # 创建任务记录
        task = MJTask(
            user_id=user_id,
            prompt=prompt,
            message_id=message.id,
            status=MJTaskStatus.WAITING
        )
        db.session.add(task)
        db.session.flush()
        # 调用 MJ 服务
        mj_service = get_mj_service()
        response = mj_service.generate_image(prompt_cn=prompt, phone_number=phone_number)
        
        if not response.success:
            task.status = MJTaskStatus.FAIL
            task.error_message = response.error
            db.session.commit()
            return False, f'生图请求失败: {response.error}', {}
            
        # 更新任务信息
        result = response.data.get('result',{})
        task.user_imagine_id = result.get('userImagineId')
        task.actions_json = result.get('actionsJson')
        db.session.commit()
            
        return True, '', {
            'id': task.id,
            'prompt': task.prompt,
            'user_imagine_id': task.user_imagine_id,
            'image_id': task.image_id,
            'status': task.status.value,
            'oss_image_url': task.oss_image_url,
            'actions_json': task.actions_json
        }
        
    except Exception as e:
        logger.error(f"Generate image error: {str(e)}")
        return False, '服务器错误', {}

@mj_bp.route('/edit', methods=['POST'])
@jwt_required()
def edit_image():
    """编辑图片接口
    
    请求体:
    {
        "action": "upsample MJ::JOB::upsample::1::xxx",
        "image_id": "xxx",
        "opt_uuid": "optional-uuid-123"  // 可选
    }
    """
    try:
        user_id = get_jwt_identity()
        user_id = int(user_id)
        data = request.get_json()
        
        if not data or 'action' not in data or 'image_id' not in data:
            return error_response('缺少必要参数')
            
        action = data['action']
        image_id = data['image_id']
        opt_uuid = data.get('opt_uuid')
        # query user from db
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return error_response('用户不存在')
        phone_number = user.phone
        
        # 查找原始任务
        original_task = MJTask.query.filter_by(image_id=image_id).first()
        if not original_task:
            return error_response('原始图片任务不存在')
        if original_task.user_id != user_id:
            return error_response('无权操作该图片')
            
        # 创建新的任务记录
        new_task = MJTask(
            user_id=user_id,
            prompt=original_task.prompt,
            message_id=original_task.message_id,
            status=MJTaskStatus.WAITING,
            parent_task_id=original_task.id,
            action_type=action.split()[0]  # 提取操作类型（upsample/variation/reset）
        )
        
        # 调用 MJ 服务
        mj_service = get_mj_service()
        response = mj_service.edit_image(
            action=action, 
            image_id=image_id,
            phone_number=phone_number,
            opt_uuid=opt_uuid
        )
        
        if not response.success:
            return error_response(f'图片编辑请求失败: {response.error}')
            
        # 更新任务信息
        result = response.data.get('result',{})
        logger.debug(f"result: {response.data}")
        new_task.user_imagine_id = result.get('userImagineId')
        new_task.image_id = result.get('imageId')
        new_task.actions_json = result.get('actionsJson')
        db.session.add(new_task)
        db.session.commit()
        try:
            check_mj_task_statuses.delay() 
        except Exception as e:
            logger.error(f"Failed to queue task check_mj_task_statuses: {e}")
        return success_response('图片编辑任务已创建', {
            'task_id': new_task.id,
            'user_imagine_id': new_task.user_imagine_id,
            'image_id': new_task.image_id,
            'status': new_task.status.value,
            'oss_image_url': new_task.oss_image_url,
            'actions_json': new_task.actions_json
        })
        
    except Exception as e:
        logger.error(f"Edit image error: {str(e)}")
        return error_response('服务器错误', code=500)

@mj_bp.route('/progress', methods=['POST'])
@jwt_required()
def query_progress():
    """查询生图进度 - 直接从数据库获取状态
    
    请求体:
    {
        "user_imagine_id": 123
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_imagine_id' not in data:
            return error_response('缺少必要参数')
            
        try:
            user_imagine_id = int(data['user_imagine_id'])
        except (TypeError, ValueError):
            return error_response('user_imagine_id 必须是整数')
            
        # 从数据库查询任务
        task = MJTask.query.filter_by(user_imagine_id=user_imagine_id).first()
        
        if not task:
            return error_response('任务不存在')
            
        # 构造响应数据
        result = {
            "id": task.id,
            "user_imagine_id": task.user_imagine_id,
            "image_id": task.image_id,
            "status": task.status.value,
            "error_show": task.error_show,
            "oss_image_url": task.oss_image_url,
            "actions_json": task.actions_json
        }
            
        return success_response('查询成功', {
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Query progress error: {str(e)}")
        return error_response('服务器错误', code=500)

@mj_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_task():
    """取消生图任务
    
    请求体:
    {
        "user_imagine_id": 123
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_imagine_id' not in data:
            return error_response('缺少必要参数')
            
        user_imagine_id = data['user_imagine_id']
        
        mj_service = get_mj_service()
        response = mj_service.cancel(user_imagine_id=user_imagine_id)
        
        if not response.success:
            return error_response(f'取消任务失败: {response.error}')
            
        return success_response('任务已取消', response.data)
        
    except Exception as e:
        logger.error(f"Cancel task error: {str(e)}")
        return error_response('服务器错误', code=500)

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

def extract_image_prompt(text: str, user_id: int) -> str:
    """从文本中提取 AI 绘画提示词"""
    prompt = ""
    try:
        # 调用 DifyService 解析脚本
        from app.services.dify_service import DifyService
        api_key = current_app.config.get('DIFY_API_KEY_MJ_PROMPT') or current_app.config.get('DIFY_API_KEY')
        if not api_key:
            logger.warning("DIFY_API_KEY_MJ_PROMPT not configured, skipping prompt extraction")
            return prompt
        dify_service = DifyService(api_key=api_key)
        script_json = dify_service.convert_script_to_json(text, str(user_id))
        prompt = script_json.get('ai_mj', '')
    except Exception as e:
        logger.error(f"Error extracting prompt from text: {e}")
        
    return prompt
