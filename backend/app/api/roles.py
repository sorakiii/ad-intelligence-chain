from flask import Blueprint, request
from app.models.role import Role
from app.utils.response import success_response, error_response
from sqlalchemy import or_
from sqlalchemy.exc import OperationalError, SQLAlchemyError
import logging

roles_bp = Blueprint('roles', __name__)

logger = logging.getLogger(__name__)

@roles_bp.route('/roles', methods=['GET'])
def get_roles():
    """获取角色列表"""
    try:
        # 获取查询参数
        category = request.args.get('category')
        keyword = request.args.get('keyword')
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        sort = request.args.get('sort', 'sort_order')  # 默认按sort_order排序
        
        # 构建查询
        query = Role.query
        
        # 按分类筛选
        if category:
            query = query.filter(Role.category == category)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    Role.title.ilike(f'%{keyword}%'),
                    Role.description.ilike(f'%{keyword}%')
                )
            )
        
        # 添加排序
        if sort == 'sort_order':
            query = query.order_by(Role.sort_order.asc())
        elif sort == 'rating':
            query = query.order_by(Role.rating.desc())
        elif sort == 'service_count':
            query = query.order_by(Role.service_count.desc())
        elif sort == 'title':
            query = query.order_by(Role.title.asc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=size)
        
        roles = [{
            'id': role.id,
            'icon': role.icon,  # 保留向后兼容
            'icons': role.get_icons(),  # 新的多图标字段
            'title': role.title,
            'description': role.description,
            'tags': role.tags,
            'rating': role.rating,
            'serviceCount': role.service_count,
            'category': role.category,
            'sub_category': role.sub_category,
        } for role in pagination.items]
        
        return success_response('获取成功', {
            'roles': roles,
            'total': pagination.total
        })
        
    except OperationalError as e:
        logger.error(f"Database operational error: {str(e)}")
        return error_response('数据库连接错误，请稍后重试')
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return error_response('数据库错误，请稍后重试')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return error_response('服务器错误，请稍后重试')

@roles_bp.route('/roles/<int:role_id>', methods=['GET'])
def get_role(role_id):
    """获取角色详情"""
    role = Role.query.get_or_404(role_id)
    
    return success_response('获取成功', {
        'role': {
            'id': role.id,
            'icon': role.icon,  # 保留向后兼容
            'icons': role.get_icons(),  # 新的多图标字段
            'title': role.title,
            'description': role.description,
            'tags': role.tags,
            'rating': role.rating,
            'serviceCount': role.service_count,
            'category': role.category,
        }
    }) 