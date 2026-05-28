import time
from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    expired_at = db.Column(db.DateTime) # 过期时间
    role_id = db.Column(db.Integer, default=-1)  # 2表示普通用户，1表示管理员, -1表示临时用户
    user_name = db.Column(db.String(255))


    # 关联用户使用目的
    purposes = db.relationship('UserPurpose', backref='user', lazy=True)
    # 关联最近项目
    recent_projects = db.relationship('RecentProject', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def set_expired_days(self, expired_days):
        """
        设置用户的过期时间为当前时间加指定天数

        Args:
            expired_days (int): 过期天数，必须为正整数

        Raises:
            ValueError: 如果 expired_days 不是正整数
        """
        if not isinstance(expired_days, int) or expired_days <= 0:
            raise ValueError("expired_days 必须为正整数")
        self.expired_at = datetime.utcnow() + timedelta(days=expired_days)
        
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

class UserPurpose(db.Model):
    __tablename__ = 'user_purposes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    purpose_type = db.Column(db.Enum('商业办公', '科学研究', '兴趣娱乐', '其他'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RecentProject(db.Model):
    __tablename__ = 'recent_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    project_type = db.Column(db.Enum('超级战队服务', '单角色服务', '定向需求服务'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 