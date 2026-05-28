from app import db
from app.models.user import User
from app.models.verification import VerificationCode
from app.utils.redis_client import RedisClient
from app.services.sms import SMSService
import random
import string
from datetime import datetime, timedelta

class AuthService:
    @staticmethod
    def generate_code():
        return ''.join(random.choices('0123456789', k=6))
    
    @staticmethod
    def send_code(phone, type='login'):
        redis_client = RedisClient()
        
        # 检查发送频率限制
        if not redis_client.can_send_code(phone):
            return False, "请等待60秒后再试"
        
        # 移除用户存在性检查,允许新用户直接发送验证码
        # 仅在重置密码时检查用户是否存在
        if type == 'reset_password':
            user_exists = User.query.filter_by(phone=phone).first() is not None
            if not user_exists:
                return False, "用户不存在"
        
        code = AuthService.generate_code()
        sms_service = SMSService()
        success, msg = sms_service.send_code(phone, code)
        
        if success:
            # 保存验证码到Redis
            redis_client.set_verification_code(phone, code)
            # 设置发送限制
            redis_client.set_send_limit(phone)
            
            # 同时保存到MySQL（用于记录历史）
            verification = VerificationCode(
                phone=phone,
                code=code,
                type=type
            )
            try:
                db.session.add(verification)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f"Save verification code to MySQL error: {str(e)}")
                # 即使MySQL保存失败，只要Redis成功就继续
                pass
                
            return True, "验证码已发送"
        return False, msg
    
    @staticmethod
    def verify_code(phone, code, type='login'):
        redis_client = RedisClient()
        stored_code = redis_client.get_verification_code(phone)
        
        if not stored_code:
            return False, "验证码已过期"
        
        if stored_code.decode() != code:
            return False, "验证码错误"
        
        # 更新MySQL中的验证码状态
        try:
            verification = VerificationCode.query.filter_by(
                phone=phone,
                code=code,
                type=type,
                used=False
            ).order_by(VerificationCode.created_at.desc()).first()
            
            if verification:
                verification.used = True
                db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Update verification code status error: {str(e)}")
        
        # 验证成功后删除Redis中的验证码
        redis_client.delete_verification_code(phone)
        return True, "验证成功"
    
    @staticmethod
    def register_user(phone, password, usage_purposes):
        user = User(phone=phone, usage_purposes=','.join(usage_purposes))
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def login_with_password(phone, password):
        user = User.query.filter_by(phone=phone).first()
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            return user
        return None 