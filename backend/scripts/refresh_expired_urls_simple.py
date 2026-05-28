#!/usr/bin/env python3
"""
手动刷新所有过期视频URL的脚本（简化版）
使用方法: python refresh_expired_urls_simple.py
"""

import sys
import os
from datetime import datetime, timezone, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def refresh_all_expired_urls():
    """立即刷新所有过期的视频URL"""
    # 使用最小化的初始化，避免循环导入
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from app.config import config
    
    app = Flask(__name__)
    app.config.from_object(config['default'])
    
    # 只初始化数据库
    db = SQLAlchemy()
    db.init_app(app)
    
    with app.app_context():
        try:
            # 直接使用原生SQL查询，避免模型关系问题
            from sqlalchemy import text
            
            current_time = datetime.now(timezone.utc)
            
            # 使用原生SQL查询过期的任务
            query = text("""
                SELECT id, obs_object_key, video_url, url_expires_at
                FROM video_tasks 
                WHERE status = 'SUCCEEDED' 
                AND url_expires_at < :current_time 
                AND obs_object_key IS NOT NULL
            """)
            
            result = db.session.execute(query, {'current_time': current_time})
            expired_tasks = result.fetchall()
            
            if not expired_tasks:
                print("没有找到已过期的视频URL")
                return
                
            print(f"找到 {len(expired_tasks)} 个已过期的视频URL，开始刷新...")
            
            # 初始化OBS客户端 - 传入配置参数
            from app.utils.obs_uploader import initialize_obs_client, generate_signed_url
            
            # 准备OBS配置
            obs_config = {
                'OBS_ACCESS_KEY': app.config['OBS_ACCESS_KEY'],
                'OBS_SECRET_KEY': app.config['OBS_SECRET_KEY'],
                'OBS_ENDPOINT': app.config['OBS_ENDPOINT'],
                'OBS_BUCKET': app.config['OBS_BUCKET'],
            }
            
            obs_client = initialize_obs_client(obs_config)
            bucket_name = app.config['OBS_BUCKET']
            
            # 刷新每个过期的URL
            success_count = 0
            failed_count = 0
            
            for task in expired_tasks:
                task_id = task[0]
                obs_object_key = task[1]
                
                try:
                    # 重新生成签名URL
                    new_signed_url = generate_signed_url(
                        obs_client=obs_client,
                        bucket_name=bucket_name,
                        object_key=obs_object_key
                    )
                    
                    # 使用原生SQL更新任务记录
                    new_expires_at = current_time + timedelta(days=7)
                    update_query = text("""
                        UPDATE video_tasks 
                        SET video_url = :video_url, url_expires_at = :expires_at
                        WHERE id = :task_id
                    """)
                    
                    db.session.execute(update_query, {
                        'video_url': new_signed_url,
                        'expires_at': new_expires_at,
                        'task_id': task_id
                    })
                    
                    success_count += 1
                    print(f"✓ 刷新任务 {task_id} 成功")
                    
                except Exception as e:
                    failed_count += 1
                    print(f"✗ 刷新任务 {task_id} 失败: {e}")
                    continue
            
            # 提交所有更改
            db.session.commit()
            
            print(f"\n刷新完成:")
            print(f"  成功: {success_count}")
            print(f"  失败: {failed_count}")
            print(f"  总计: {len(expired_tasks)}")
            
        except Exception as e:
            print(f"刷新过程出错: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == '__main__':
    refresh_all_expired_urls() 
 