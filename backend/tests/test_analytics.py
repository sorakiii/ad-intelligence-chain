import unittest
import sys
import os
import json
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from app.models.role import Role
from app.models.chat import ChatSession, ChatMessage
from flask_jwt_extended import create_access_token

class AnalyticsTestCase(unittest.TestCase):
    def setUp(self):
        """测试前设置"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 确保所有表都被创建
        db.create_all()
        
        self.client = self.app.test_client()
        
        # 创建测试角色
        role1 = Role(
            id=1,
            title="测试角色1",
            icon="http://example.com/icon1.png",
            description="用于测试的角色1"
        )
        
        role2 = Role(
            id=2,
            title="测试角色2",
            icon="http://example.com/icon2.png",
            description="用于测试的角色2"
        )
        
        db.session.add_all([role1, role2])
        db.session.flush()
        
        # 创建管理员用户
        admin = User(id=1, phone='13800000001', role_id=1)
        admin.set_password('password')
        
        # 创建普通用户
        user = User(id=2, phone='13800000002', role_id=0)
        user.set_password('password')
        
        db.session.add_all([admin, user])
        db.session.flush()
        
        # 获取当前时间
        now = datetime.now()
        
        # 创建聊天会话
        chat_session1 = ChatSession(
            id=1,
            user_id=1,
            role_id=1,
            title="管理员的测试会话1",
            type="single_role",
            created_at=now - timedelta(days=1)
        )
        
        chat_session2 = ChatSession(
            id=2,
            user_id=2,
            role_id=1,
            title="普通用户的测试会话1",
            type="single_role",
            created_at=now - timedelta(days=1)
        )
        
        chat_session3 = ChatSession(
            id=3,
            user_id=1,
            role_id=2,
            title="管理员的测试会话2",
            type="single_role",
            created_at=now
        )
        
        db.session.add_all([chat_session1, chat_session2, chat_session3])
        db.session.flush()
        
        # 创建聊天消息 - 注意api_usage应该是Python字典，SQLAlchemy会自动处理JSON转换
        chat_message1 = ChatMessage(
            id=1,
            session_id=1,
            content="你好，这是测试消息1",
            type="user",
            timestamp=now - timedelta(hours=5),
            api_usage={"total_tokens": 10}
        )
        
        chat_message2 = ChatMessage(
            id=2,
            session_id=1,
            content="你好，这是测试回复1",
            type="assistant",
            timestamp=now - timedelta(hours=5),
            api_usage={"total_tokens": 15}
        )
        
        chat_message3 = ChatMessage(
            id=3,
            session_id=2,
            content="你好，这是测试消息2",
            type="user",
            timestamp=now - timedelta(hours=3),
            api_usage={"total_tokens": 8}
        )
        
        chat_message4 = ChatMessage(
            id=4,
            session_id=2,
            content="你好，这是测试回复2",
            type="assistant",
            timestamp=now - timedelta(hours=3),
            api_usage={"total_tokens": 12}
        )
        
        chat_message5 = ChatMessage(
            id=5,
            session_id=3,
            content="你好，这是测试消息3",
            type="user",
            timestamp=now - timedelta(hours=1),
            api_usage={"total_tokens": 9}
        )
        
        chat_message6 = ChatMessage(
            id=6,
            session_id=3,
            content="你好，这是测试回复3",
            type="assistant",
            timestamp=now - timedelta(hours=1),
            api_usage={"total_tokens": 14}
        )
        
        db.session.add_all([
            chat_message1, chat_message2, chat_message3, 
            chat_message4, chat_message5, chat_message6
        ])
        
        db.session.commit()
        
        # 获取管理员Token
        with self.app.test_request_context():
            self.admin_token = create_access_token(identity=str(admin.id))
            self.user_token = create_access_token(identity=str(user.id))
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_admin_required(self):
        """测试管理员权限检查"""
        # 获取当前日期
        today = datetime.now()
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        # 使用普通用户令牌访问
        response = self.client.get(
            f'/api/analytics/total-usage?start_date={start_date}&end_date={end_date}',
            headers={'Authorization': f'Bearer {self.user_token}'}
        )
        self.assertEqual(response.status_code, 403)
        
        # 使用管理员令牌访问
        response = self.client.get(
            f'/api/analytics/total-usage?start_date={start_date}&end_date={end_date}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
    
    def test_total_usage(self):
        """测试总Token使用量API"""
        # 获取当前日期
        today = datetime.now()
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        response = self.client.get(
            f'/api/analytics/total-usage?start_date={start_date}&end_date={end_date}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('total_token', data['data'])
        self.assertIn('used_token', data['data'])
        self.assertIn('remaining_token', data['data'])
        
        # 测试缺少日期参数
        response = self.client.get(
            '/api/analytics/total-usage',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_user_usage(self):
        """测试用户Token使用量API"""
        # 获取当前日期
        today = datetime.now()
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        response = self.client.get(
            f'/api/analytics/user-usage?start_date={start_date}&end_date={end_date}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        
        # 测试缺少日期参数
        response = self.client.get(
            '/api/analytics/user-usage',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_role_usage(self):
        """测试角色使用量API"""
        # 获取当前日期
        today = datetime.now()
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        response = self.client.get(
            f'/api/analytics/role-usage?start_date={start_date}&end_date={end_date}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        
        # 测试缺少日期参数
        response = self.client.get(
            '/api/analytics/role-usage',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_user_role_usage(self):
        """测试用户使用角色API"""
        # 获取当前日期
        today = datetime.now()
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        response = self.client.get(
            f'/api/analytics/user-role-usage?start_date={start_date}&end_date={end_date}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        
        # 测试缺少日期参数
        response = self.client.get(
            '/api/analytics/user-role-usage',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 400)
        
        # 测试指定用户ID
        response = self.client.get(
            f'/api/analytics/user-role-usage?start_date={start_date}&end_date={end_date}&user_id=1',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
    
    def test_daily_stats(self):
        """测试每日统计API"""
        # 获取当前日期
        today = datetime.now()
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        # 测试指定日期范围
        response = self.client.get(
            f'/api/analytics/daily-stats?start_date={start_date}&end_date={end_date}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        
        # 测试缺少日期参数
        response = self.client.get(
            '/api/analytics/daily-stats',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 400)
    
    def test_set_admin(self):
        """测试设置管理员API"""
        # 使用管理员令牌设置其他用户为管理员
        response = self.client.post(
            '/auth/set-admin',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={'phone': '13800000002', 'is_admin': True}
        )
        self.assertEqual(response.status_code, 200)
        
        # 验证设置成功
        user = User.query.filter_by(phone='13800000002').first()
        self.assertEqual(user.role_id, 1)
        
        # 取消管理员权限
        response = self.client.post(
            '/auth/set-admin',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={'phone': '13800000002', 'is_admin': False}
        )
        self.assertEqual(response.status_code, 200)
        
        # 验证取消成功
        user = User.query.filter_by(phone='13800000002').first()
        self.assertEqual(user.role_id, 0)

if __name__ == '__main__':
    unittest.main() 