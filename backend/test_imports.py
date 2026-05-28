# 测试导入是否正确
try:
    from app.tasks.mj_tasks import check_mj_task_statuses
    print("Successfully imported check_mj_task_statuses")
except Exception as e:
    print(f"Import failed: {e}")

# 测试 Celery 任务注册
from celery_worker import celery
print("\nRegistered tasks:")
for task in celery.tasks.keys():
    print(f"- {task}")