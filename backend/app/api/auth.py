from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from app.services.auth import AuthService
from app.utils.response import success_response, error_response
from app import db
from app.models.user import User, UserPurpose
from datetime import datetime
from flask import current_app
from flask_jwt_extended import jwt_required
from app.utils.logger import get_logger

logger = get_logger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/send-code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone = data.get('phone')
    type = data.get('type', 'login')  # 获取验证码类型，默认为登录
    
    # 验证类型是否合法
    if type not in ['register', 'login', 'reset_password']:
        return error_response('无效的验证码类型')
    
    if not phone:
        return error_response('手机号不能为空')
    
    # 移除用户存在性检查,允许新用户直接发送验证码登录
    success, msg = AuthService.send_code(phone, type)
    if success:
        return success_response(msg)
    return error_response(msg)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')
    code = data.get('code')
    
    if not phone:
        return error_response('手机号不能为空')
    
    user = User.query.filter_by(phone=phone).first()
    
    if code:  # 验证码登录
        success, msg = AuthService.verify_code(phone, code, 'login')
        if not success:
            return error_response(msg)
            
        if not user:  # 如果用户不存在，自动创建
            user = User(phone=phone)
            db.session.add(user)
            db.session.commit()
            
    elif password:  # 密码登录
        if not user or not user.check_password(password):
            return error_response('手机号或密码错误')
    else:
        return error_response('请提供验证码或密码')
    
    # 更新登录时间
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # 生成token
    access_token = create_access_token(identity=str(user.id))
    return success_response('登录成功', {
        'access_token': access_token,
        'user': {
            'phone': user.phone,
            'role_id': user.role_id,  # 返回用户角色ID
            'expired_at': int(user.expired_at.timestamp()) if user.expired_at else 0,
            'purposes': [p.purpose_type for p in user.purposes],
            'recent_projects': [{
                'id': p.id,
                'name': p.project_name,
                'type': p.project_type,
                'created_at': p.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': p.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            } for p in user.recent_projects]
        }
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')
    code = data.get('code')
    usage_purposes = data.get('usage_purposes', [])  # 修改这里，匹配请求参数名
    
    logger.info(f"Register request - phone: {phone}, purposes: {usage_purposes}")
    
    if not all([phone, password, code]):
        return error_response('请填写完整信息')
    
    if not usage_purposes:  # 修改验证
        return error_response('请选择使用目的')
    
    # 验证每个目的是否合法
    valid_purposes = ['商业办公', '科学研究', '兴趣娱乐', '其他']
    if not all(purpose in valid_purposes for purpose in usage_purposes):
        return error_response('无效的使用目的')
    
    # 验证手机号是否已注册
    if User.query.filter_by(phone=phone).first():
        return error_response('该手机号已注册')
    
    # 验证码验证
    success, msg = AuthService.verify_code(phone, code, 'register')
    if not success:
        return error_response(msg)
    
    try:
        # 创建新用户
        user = User(phone=phone,role_id=-1)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # 获取user.id
        
        logger.info(f"Created user with ID: {user.id}")
        
        # 保存用户使用目的
        for purpose in usage_purposes:
            user_purpose = UserPurpose(
                user_id=user.id,
                purpose_type=purpose
            )
            db.session.add(user_purpose)
            logger.info(f"Added purpose {purpose} for user {user.id}")
        
        db.session.commit()
        logger.info(f"Successfully registered user {user.id} with purposes {usage_purposes}")
        
        # 生成token
        access_token = create_access_token(identity=str(user.id))
        return success_response('注册成功', {
            'access_token': access_token,
            'user': {
                'phone': user.phone,
                'purposes': [p.purpose_type for p in user.purposes]
            }
        })
    except Exception as e:
        logger.error(f"Register error: {str(e)}")
        db.session.rollback()
        return error_response('注册失败，请稍后重试')

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    phone = data.get('phone')
    new_password = data.get('password')
    code = data.get('code')
    
    if not all([phone, new_password, code]):
        return error_response('请填写完整信息')
    
    # 验证码验证
    success, msg = AuthService.verify_code(phone, code, 'reset_password')
    if not success:
        return error_response(msg)
    
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return error_response('用户不存在')
    
    try:
        user.set_password(new_password)
        db.session.commit()
        return success_response('密码重置成功')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Reset password error: {str(e)}")
        return error_response('密码重置失败，请稍后重试')

@auth_bp.route('/update-purposes', methods=['POST'])
@jwt_required()  # 需要登录才能调用
def update_purposes():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    data = request.get_json()
    purposes = data.get('purposes', [])
    
    try:
        # 删除旧的使用目的
        UserPurpose.query.filter_by(user_id=user.id).delete()
        
        # 添加新的使用目的
        for purpose in purposes:
            user_purpose = UserPurpose(
                user=user,
                purpose_type=purpose
            )
            db.session.add(user_purpose)
        
        db.session.commit()
        return success_response('更新成功', {
            'purposes': [p.purpose_type for p in user.purposes]
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update purposes error: {str(e)}")
        return error_response('更新失败，请稍后重试')

@auth_bp.route('/set-admin', methods=['POST'])
@jwt_required()
def set_admin():
    """设置或取消管理员权限"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    # 验证当前用户是否为管理员
    if user.role_id != 1:
        return error_response('您没有管理员权限', code=403)
    
    data = request.get_json()
    target_phone = data.get('phone')
    is_admin = data.get('is_admin', False)
    
    if not target_phone:
        return error_response('请提供目标用户手机号')
    
    # 查找目标用户
    target_user = User.query.filter_by(phone=target_phone).first()
    if not target_user:
        return error_response('目标用户不存在')
    
    try:
        target_user.role_id = 1 if is_admin else 0
        db.session.commit()
        return success_response(f"用户 {target_phone} {'设为管理员' if is_admin else '取消管理员权限'}成功")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Set admin error: {str(e)}")
        return error_response('操作失败，请稍后重试')

@auth_bp.route('/check-admin', methods=['GET'])
@jwt_required()
def check_admin():
    """检查当前用户是否为管理员"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    is_admin = user.role_id == 1
    
    return success_response('获取成功', {
        'is_admin': is_admin
    })

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_info():
    """获取当前用户信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        
        return success_response('获取成功', {
            'id': user.id,
            'phone': user.phone,
            'role_id': user.role_id,
            'expired_at': int(user.expired_at.timestamp()) if user.expired_at else 0,
            'purposes': [p.purpose_type for p in user.purposes],
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        return error_response('获取用户信息失败，请稍后重试')

# 暂时注释掉注册和重置密码接口
"""
@auth_bp.route('/register', methods=['POST'])
def register():
    pass

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    pass
""" 

@auth_bp.route('/add-user', methods=['POST'])
@jwt_required()
def add_user():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')
    expired_days = data.get('expired_days')
    usage_purposes = data.get('usage_purposes', [])  # 修改这里，匹配请求参数名
    
    logger.info(f"Register request - phone: {phone}, purposes: {usage_purposes}")
    
    if not all([phone, password, expired_days]):
        return error_response('请填写完整信息')
    
    if not usage_purposes:  # 修改验证
        return error_response('请选择使用目的')
    
    # 验证每个目的是否合法
    valid_purposes = ['商业办公', '科学研究', '兴趣娱乐', '其他']
    if not all(purpose in valid_purposes for purpose in usage_purposes):
        return error_response('无效的使用目的')
    
    # 验证手机号是否已注册
    if User.query.filter_by(phone=phone).first():
        return error_response('该手机号已注册')
    

    
    try:
        # 创建新用户
        user = User(phone=phone,role_id=-1)
        user.set_password(password)
        user.set_expired_days(expired_days)
        db.session.add(user)
        db.session.flush()  # 获取user.id
        
        logger.info(f"Created user with ID: {user.id}")
        
        # 保存用户使用目的
        for purpose in usage_purposes:
            user_purpose = UserPurpose(
                user_id=user.id,
                purpose_type=purpose
            )
            db.session.add(user_purpose)
            logger.info(f"Added purpose {purpose} for user {user.id}")
        
        db.session.commit()
        logger.info(f"Successfully registered user {user.id} with purposes {usage_purposes}")
        
        # 生成token
        access_token = create_access_token(identity=str(user.id))
        return success_response('注册成功', {
            'access_token': access_token,
            'user': {
                'phone': user.phone,
                'purposes': [p.purpose_type for p in user.purposes]
            }
        })
    except Exception as e:
        logger.error(f"Register error: {str(e)}")
        db.session.rollback()
        return error_response('注册失败，请稍后重试')
