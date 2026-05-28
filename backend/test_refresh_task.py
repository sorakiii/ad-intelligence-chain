#!/usr/bin/env python3
"""
测试定时刷新任务
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, create_celery

def test_refresh_task():
    """测试刷新任务"""
    try:
        # 初始化应用
        app = create_app(auto_init=False)
        create_celery(app)
        
        # 导入任务
        from app.tasks.video_tasks import refresh_video_urls
        from app import init_app
        
        # 初始化应用
        init_app(app)
        
        with app.app_context():
            print("开始执行刷新任务...")
            result = refresh_video_urls()
            print(f"任务执行完成，结果: {result}")
            
    except Exception as e:
        print(f"任务执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_refresh_task() 