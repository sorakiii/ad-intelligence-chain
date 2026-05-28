from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.models.role import Role
from sqlalchemy import func, text, cast, String, extract
from sqlalchemy.sql import literal_column
from datetime import datetime, timedelta
import json

analytics_bp = Blueprint('analytics', __name__)

def admin_required(fn):
    """装饰器：要求用户为管理员"""
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role_id != 1:
            return jsonify({"message": "需要管理员权限", "status": "error"}), 403
        
        return fn(*args, **kwargs)
    
    wrapper.__name__ = fn.__name__
    return wrapper

@analytics_bp.route('/total-usage', methods=['GET'])
@admin_required
def total_token_usage():
    """获取总体Token使用量"""
    
    # 获取开始日期和结束日期参数
    start_date_str = request.args.get('start_date', None)
    end_date_str = request.args.get('end_date', None)
    
    if not start_date_str or not end_date_str:
        return jsonify({"message": "请提供开始日期和结束日期", "success": False}), 400
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # 修复时区问题：确保正确包含开始和结束日期
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    except ValueError:
        return jsonify({"message": "日期格式无效，请使用YYYY-MM-DD格式", "success": False}), 400
    
    # 使用SQLAlchemy ORM查询，避免直接使用特定数据库功能
    try:
        # 计算使用的token总量
        total_used = db.session.query(
            func.sum(
                func.json_extract(ChatMessage.api_usage, '$.total_tokens').cast(db.Integer)
            )
        ).filter(
            ChatMessage.timestamp >= start_date,
            ChatMessage.timestamp <= end_date  # 修改为包含结束日期
        ).scalar() or 0
        
        total_token = 24000000
        used_token = int(total_used)
        remaining_token = total_token - used_token
        
        data = {
            "total_token": total_token,
            "used_token": used_token,
            "remaining_token": remaining_token
        }
        
        return jsonify({"data": data, "success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"查询失败: {str(e)}", "success": False}), 500

@analytics_bp.route('/user-usage', methods=['GET'])
@admin_required
def user_token_usage():
    """获取每个用户的Token使用量，支持分页"""
    start_date_str = request.args.get('start_date', None)
    end_date_str = request.args.get('end_date', None)
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    offset = (page - 1) * page_size

    if not start_date_str or not end_date_str:
        return jsonify({"message": "请提供开始日期和结束日期", "success": False}), 400

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # 修复时区问题：确保正确包含开始和结束日期
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    except ValueError:
        return jsonify({"message": "日期格式无效，请使用YYYY-MM-DD格式", "success": False}), 400

    try:
        # 总用户数
        total = db.session.query(User).count()

        # 分页查询
        result = db.session.query(
            User.id,
            User.phone,
            User.user_name,
            func.sum(
                func.json_extract(ChatMessage.api_usage, '$.total_tokens').cast(db.Integer)
            ).label('tokens')
        ).outerjoin(
            ChatSession, User.id == ChatSession.user_id
        ).outerjoin(
            ChatMessage, 
            db.and_(
                ChatSession.id == ChatMessage.session_id,
                ChatMessage.timestamp >= start_date,
                ChatMessage.timestamp <= end_date
            )
        ).group_by(
            User.id, User.phone, User.user_name
        ).order_by(
            func.sum(
                func.json_extract(ChatMessage.api_usage, '$.total_tokens').cast(db.Integer)
            ).desc()
        ).offset(offset).limit(page_size).all()

        data = []
        for row in result:
            data.append({
                "user_id": row[0],
                "phone": row[1],
                "user_name": row[2],
                "token_usage": row[3] or 0
            })

        return jsonify({"data": data, "total": total, "success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"查询失败: {str(e)}", "success": False}), 500

@analytics_bp.route('/role-usage', methods=['GET'])
@admin_required
def role_usage():
    """获取每个角色场景的使用量和使用人数"""
    
    # 获取开始日期和结束日期参数
    start_date_str = request.args.get('start_date', None)
    end_date_str = request.args.get('end_date', None)
    
    if not start_date_str or not end_date_str:
        return jsonify({"message": "请提供开始日期和结束日期", "success": False}), 400
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # 修复时区问题：确保正确包含开始和结束日期
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    except ValueError:
        return jsonify({"message": "日期格式无效，请使用YYYY-MM-DD格式", "success": False}), 400
    
    try:
        # 使用ORM查询
        result = db.session.query(
            Role.id,
            Role.title,
            Role.icon,
            func.count(func.distinct(ChatSession.user_id)).label('unique_users'),
            func.count(ChatMessage.id).label('message_count'),
            func.sum(
                func.json_extract(ChatMessage.api_usage, '$.total_tokens').cast(db.Integer)
            ).label('tokens')
        ).outerjoin(
            ChatSession, Role.id == ChatSession.role_id
        ).outerjoin(
            ChatMessage, 
            db.and_(
                ChatSession.id == ChatMessage.session_id,
                ChatMessage.timestamp >= start_date,
                ChatMessage.timestamp <= end_date
            )
        ).group_by(
            Role.id, Role.title, Role.icon
        ).order_by(
            func.count(func.distinct(ChatSession.user_id)).desc(),
            func.sum(
                func.json_extract(ChatMessage.api_usage, '$.total_tokens').cast(db.Integer)
            ).desc()
        ).all()
        
        data = []
        for row in result:
            data.append({
                "role_id": row[0],
                "title": row[1],
                "icon": row[2],
                "unique_users": row[3] or 0,
                "message_count": row[4] or 0,
                "token_usage": row[5] or 0
            })
        
        return jsonify({"data": data, "success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"查询失败: {str(e)}", "success": False}), 500

@analytics_bp.route('/user-role-usage', methods=['GET'])
@admin_required
def user_role_usage():
    """获取每个用户使用的角色场景统计"""
    
    # 获取开始日期和结束日期参数
    start_date_str = request.args.get('start_date', None)
    end_date_str = request.args.get('end_date', None)
    user_id = request.args.get('user_id', None)
    
    # 添加调试信息
    print(f"DEBUG: 接收到的日期参数 - start_date: {start_date_str}, end_date: {end_date_str}")
    
    if not start_date_str or not end_date_str:
        return jsonify({"message": "请提供开始日期和结束日期", "success": False}), 400
    
    try:
        # 修复时区问题：确保正确包含开始和结束日期
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # 设置开始时间为当天的00:00:00
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        # 设置结束时间为当天的23:59:59
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        print(f"DEBUG: 解析后的日期 - start_date: {start_date}, end_date: {end_date}")
    except ValueError:
        return jsonify({"message": "日期格式无效，请使用YYYY-MM-DD格式", "success": False}), 400
    
    try:
        # 构建查询
        query = db.session.query(
            User.id.label('user_id'),
            User.phone,
            User.user_name,
            Role.id.label('role_id'),
            Role.title,
            Role.icon,
            func.count(ChatMessage.id).label('message_count'),
            func.sum(
                func.json_extract(ChatMessage.api_usage, '$.total_tokens').cast(db.Integer)
            ).label('tokens')
        ).join(
            ChatSession, User.id == ChatSession.user_id
        ).join(
            Role, ChatSession.role_id == Role.id
        ).outerjoin(
            ChatMessage, 
            db.and_(
                ChatSession.id == ChatMessage.session_id,
                ChatMessage.timestamp >= start_date,
                ChatMessage.timestamp <= end_date
            )
        )
        
        # 如果提供了特定用户ID，则只查询该用户的数据
        if user_id:
            query = query.filter(User.id == user_id)
        
        result = query.group_by(
            User.id, User.phone, User.user_name, Role.id, Role.title, Role.icon
        ).order_by(
            User.id,
            func.sum(
                func.json_extract(ChatMessage.api_usage, '$.total_tokens').cast(db.Integer)
            ).desc()
        ).all()
        
        # 添加调试信息
        print(f"DEBUG: 查询结果数量: {len(result)}")
        for row in result:
            print(f"DEBUG: 用户 {row[1]} ({row[2]}) - Token: {row[7]}")
        
        # 组织数据结构
        user_data = {}
        for row in result:
            user_id = row[0]
            
            if user_id not in user_data:
                user_data[user_id] = {
                    "user_id": user_id,
                    "phone": row[1],
                    "user_name": row[2],
                    "roles": []
                }
            
            user_data[user_id]["roles"].append({
                "role_id": row[3],
                "title": row[4],
                "icon": row[5],
                "message_count": row[6] or 0,
                "token_usage": row[7] or 0
            })
        
        return jsonify({"data": list(user_data.values()), "success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"查询失败: {str(e)}", "success": False}), 500

@analytics_bp.route('/daily-stats', methods=['GET'])
@admin_required
def daily_stats():
    """获取每日Token使用量统计"""
    
    # 获取开始日期和结束日期参数
    start_date_str = request.args.get('start_date', None)
    end_date_str = request.args.get('end_date', None)
    
    if not start_date_str or not end_date_str:
        return jsonify({"message": "请提供开始日期和结束日期", "success": False}), 400
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # 修复时区问题：确保正确包含开始和结束日期
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    except ValueError:
        return jsonify({"message": "日期格式无效，请使用YYYY-MM-DD格式", "success": False}), 400
    
    try:
        # 使用ORM查询
        result = db.session.query(
            func.date(ChatMessage.timestamp).label('date'),
            func.sum(
                func.json_extract(ChatMessage.api_usage, '$.total_tokens').cast(db.Integer)
            ).label('tokens')
        ).filter(
            ChatMessage.timestamp >= start_date,
            ChatMessage.timestamp <= end_date
        ).group_by(
            func.date(ChatMessage.timestamp)
        ).order_by(
            func.date(ChatMessage.timestamp)
        ).all()
        
        data = []
        for row in result:
            data.append({
                "date": row[0].strftime('%Y-%m-%d'),
                "token_usage": row[1] or 0
            })
        
        return jsonify({"data": data, "success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"查询失败: {str(e)}", "success": False}), 500 