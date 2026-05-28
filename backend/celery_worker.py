# backend/celery_worker.py
import os
import logging
from app import create_app, create_celery, celery, init_app

logger = logging.getLogger(__name__)

app = create_app(os.getenv('FLASK_CONFIG') or 'default', auto_init=False)
celery = create_celery(app)  # 这一步让 app.celery 变成全局唯一实例
init_app(app)

# 可选：加载 celery 配置
celery.config_from_object('celery_config')

# 可选：打印调度任务信息
logger.info("Loaded beat schedule:")
if hasattr(celery.conf, 'beat_schedule'):
    for task_name, task_config in celery.conf.beat_schedule.items():
        logger.info(f"- {task_name}: {task_config['task']} (schedule: {task_config['schedule']})")
else:
    logger.warning("No beat schedule configured!")

if __name__ == '__main__':
    # 启动 worker: celery -A celery_worker.celery worker --loglevel=info
    pass  # Celery CLI 会自动用 celery_worker.celery
