import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

def load_env():
    """根据环境加载对应的.env文件"""
    env = os.getenv('FLASK_ENV', 'development')
    
    # 获取app目录的路径
    app_dir = Path(__file__).parent
    
    # 构建环境配置文件的路径
    env_file = app_dir / f'.env.{env}'
    default_env = app_dir / '.env'
    
    # 如果存在对应环境的配置文件则加载，否则加载默认的.env
    if env_file.exists():
        load_dotenv(env_file)
    elif default_env.exists():
        load_dotenv(default_env)
    else:
        print(f"Warning: No .env file found in {app_dir}")

# 加载环境配置
load_env()

class BaseConfig:
    """基础配置"""
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 添加数据库连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'max_overflow': 2
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=365)
    JWT_HEADER_TYPE = 'Bearer'
    
    # Redis配置
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # 短信配置（253 平台）
    SMS_URL = "https://smssh1.253.com/msg/v1/send/json"
    SMS_ACCOUNT = os.getenv('SMS_ACCOUNT')
    SMS_PASSWORD = os.getenv('SMS_PASSWORD')
    SMS_SIGN_NAME = os.getenv('SMS_SIGN_NAME')
    
    # Dify API
    DIFY_API_URL = os.getenv('DIFY_API_URL')
    DIFY_API_KEY = os.getenv('DIFY_API_KEY')
    DIFY_API_KEY_HTML_ZIP = os.getenv('DIFY_API_KEY_HTML_ZIP')
    DIFY_API_KEY_HTML_RAW = os.getenv('DIFY_API_KEY_HTML_RAW')
    DIFY_API_KEY_VIDEO_SCRIPT = os.getenv('DIFY_API_KEY_VIDEO_SCRIPT')
    DIFY_API_KEY_MJ_PROMPT = os.getenv('DIFY_API_KEY_MJ_PROMPT')
    
    # 通义千问 / DashScope 文生视频
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
    
    # Midjourney API配置
    MJ_API_URL = os.getenv('MJ_API_URL', 'https://api.example.com')
    MJ_API_KEY = os.getenv('MJ_API_KEY')
    MJ_APP_KEY = os.getenv('MJ_APP_KEY')
    
    # 移除本地文件上传配置，只保留文件类型限制
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'doc', 'docx',  # 文档
        'png', 'jpg', 'jpeg',         # 图片
        'md', 'markdown'              # Markdown
    }
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # OBS配置
    OBS_ACCESS_KEY = os.getenv('OBS_ACCESS_KEY')
    OBS_SECRET_KEY = os.getenv('OBS_SECRET_KEY')
    OBS_ENDPOINT = os.getenv('OBS_ENDPOINT')
    OBS_BUCKET = os.getenv('OBS_BUCKET')
    
    # 视频URL相关配置
    VIDEO_URL_VALIDITY_PERIOD = 6 * 24 * 3600  # URL有效期：6天
    VIDEO_URL_REFRESH_MAX_AGE = 30  # 自动刷新的最大任务年龄（天）
    
    @classmethod
    def init_app(cls, app):
        if not cls.DIFY_API_URL:
            raise ValueError("DIFY_API_URL not found in environment variables")

class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    DEBUG = True
    HOST = 'localhost'
    PORT = 5002
    DOMAIN = os.getenv('DOMAIN', 'http://localhost:5002')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')

class TestingConfig(BaseConfig):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    # 使用SQLite内存数据库进行测试
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # 禁用CSRF保护
    WTF_CSRF_ENABLED = False
    # 禁用连接池，适合SQLite内存数据库
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'check_same_thread': False}
    }
    # 测试环境JWT配置
    JWT_SECRET_KEY = 'testing-secret-key'
    # 测试环境其他服务的模拟URL
    DIFY_API_URL = 'http://mock-dify-api.com'

class ProductionConfig(BaseConfig):
    """生产环境配置"""
    DEBUG = False
    HOST = '0.0.0.0'  # 允许外部访问
    PORT = 5002
    DOMAIN = os.getenv('DOMAIN', 'http://localhost:5002')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/uploads')

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,  # 添加测试环境配置
    'default': DevelopmentConfig
}
