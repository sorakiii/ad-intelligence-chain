from app import create_app,init_app, db, create_celery, celery
from app.utils.logger import get_logger
import os
import sys
logger = get_logger(__name__)
app = create_app(auto_init=False)
create_celery(app)  # 这一步让 celery 变成全局唯一实例
init_app(app)
# 创建数据库表
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # 打印所有注册的路由
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
    
    app.run(host='0.0.0.0', port=5002) 