import os
from celery.schedules import crontab

# Broker 配置 - 直接使用环境变量中的 REDIS_URL
# 环境变量已经由 config.py 通过 load_dotenv 加载
broker_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# 时区配置
timezone = 'Asia/Shanghai'
enable_utc = True

# 并发配置 - 根据使用场景调整
worker_concurrency = 4  # 设置4个并发worker进程
worker_prefetch_multiplier = 1  # 每个worker预取1个任务，避免长任务阻塞
task_acks_late = True  # 任务完成后才确认，确保可靠性
worker_max_tasks_per_child = 1000  # 每个子进程最多处理1000个任务后重启，防止内存泄漏

# HTML生成专用配置 - 可根据实际需求调整
HTML_WORKER_CONCURRENCY = int(os.getenv('HTML_WORKER_CONCURRENCY', '4'))  # 默认4并发，可通过环境变量调整

# 任务路由配置 - 将不同类型的任务分配到不同队列
task_routes = {
    'app.tasks.html_tasks.generate_html_task': {'queue': 'html_generation'},
    'app.tasks.video_tasks.check_video_task_statuses': {'queue': 'video_processing'},
    'app.tasks.mj_tasks.*': {'queue': 'image_processing'},
    # refresh_video_urls 作为定时任务，使用默认队列
}

# 队列配置
task_default_queue = 'default'
task_queues = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'html_generation': {
        'exchange': 'html_generation',
        'routing_key': 'html_generation',
    },
    'video_processing': {
        'exchange': 'video_processing', 
        'routing_key': 'video_processing',
    },
    'image_processing': {
        'exchange': 'image_processing',
        'routing_key': 'image_processing',
    },
}

# 定时任务配置
beat_schedule = {
    'check-video-tasks-every-minute': {
        'task': 'app.tasks.video_tasks.check_video_task_statuses',
        'schedule': crontab(minute='*/1'),
    },
    'refresh-video-urls-every-4-hours': {
        'task': 'app.tasks.video_tasks.refresh_video_urls',
        'schedule': crontab(minute=0, hour='*/4'),  # 每4小时执行一次
    },
    'check-mj-tasks-every-10-seconds': {
        'task': 'app.tasks.mj_tasks.check_mj_task_statuses',
        'schedule': 10.0,  # 每10秒检查一次
    }
}
