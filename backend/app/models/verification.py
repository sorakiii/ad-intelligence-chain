from app import db
from datetime import datetime, timedelta

class VerificationCode(db.Model):
    __tablename__ = 'verification_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(11), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    type = db.Column(db.Enum('register', 'login', 'reset_password'), nullable=False, default='login')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    def __init__(self, phone, code, type='login', expires_at=None):
        self.phone = phone
        self.code = code
        self.type = type
        self.expires_at = expires_at or datetime.utcnow() + timedelta(minutes=5)
    
    def is_valid(self):
        return not self.used and datetime.utcnow() <= self.expires_at 