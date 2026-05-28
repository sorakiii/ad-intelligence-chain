from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate 
from app.config import config
import os
from app.utils.logger import get_logger
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate() 
celery = None




def create_app(config_name='default', auto_init=True):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    if auto_init:
        init_app(app)
    return app

def init_app(app):
    # 初始化扩展
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # 注册蓝图 - 统一使用 /api 前缀
    from app.api.auth import auth_bp
    from app.api.roles import roles_bp
    from app.api.chat import chat_bp
    from app.api.video import video_bp
    from app.api.mj import mj_bp
    from app.api.analytics import analytics_bp
    from app.api.html import html_bp
    
    # 修改认证接口前缀，统一使用 /api
    app.register_blueprint(auth_bp, url_prefix='/api/auth')      # 改为 /api/auth
    app.register_blueprint(roles_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(video_bp, url_prefix='/api/video')
    app.register_blueprint(mj_bp, url_prefix='/api/mj')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(html_bp, url_prefix='/api/html')
    
    # 在 Flask 应用初始化时设置最大内容长度
    app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024  # 设置为 15MB
    
    # 设置JSON配置，确保中文等非ASCII字符直接使用UTF-8输出，不转换为Unicode转义序列
    app.config['JSON_AS_ASCII'] = False
    # app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    
    # 其他初始化

def create_celery(app=None):
    """全局唯一 Celery 实例工厂"""
    global celery
    logger = get_logger(__name__) 
    from celery import Celery
    app = app or create_app(os.getenv('FLASK_CONFIG') or 'default')
    celery = Celery(
        app.import_name,
        broker=app.config['REDIS_URL'],
        backend=app.config.get('REDIS_URL'),
        include=[
            'app.tasks.video_tasks',
            'app.tasks.mj_tasks',
            'app.tasks.html_tasks'
        ]
    )
    celery.conf.update(app.config)
    # 绑定 Flask 上下文
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    logger.info(f"Celery broker_url: {celery.conf.broker_url}")
    return celery 
