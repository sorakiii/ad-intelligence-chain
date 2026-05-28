from app import db
from datetime import datetime

class Role(db.Model):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String(1024))
    icons = db.Column(db.JSON)  # 新的图标数组字段: [{"type": "web", "icon": "🌐"}, {"type": "video", "icon": "🎬"}]
    title = db.Column(db.String(100), nullable=False) # 角色标题
    description = db.Column(db.Text)  # 角色描述
    dify_api_key = db.Column(db.String(255))  # Dify API Key 字段, gpt4o
    dify_api_key_ds = db.Column(db.String(255))  # Dify API Key 字段, deepseek
    tags = db.Column(db.JSON)                        # 角色标签
    rating = db.Column(db.Float, default=5.0)        # 评分
    service_count = db.Column(db.Integer, default=0) # 服务次数
    category = db.Column(db.String(50))             # 角色分类
    sub_category = db.Column(db.String(50))             # 角色子分类
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sort_order = db.Column(db.Integer, default=0)  # 排序字段，默认为0 

    def get_icons(self):
        """获取角色图标列表，支持向后兼容"""
        # 优先返回新的 icons 数组
        if self.icons and len(self.icons) > 0:
            return self.icons
        # 如果没有新图标但有旧图标，不转换为数组格式
        # 让前端直接使用旧的 icon 字段显示
        return []
    
    def add_icon(self, icon_type, icon_content):
        """添加图标到角色"""
        if not self.icons:
            self.icons = []
        
        # 检查是否已存在相同类型的图标
        for existing_icon in self.icons:
            if existing_icon.get('type') == icon_type:
                existing_icon['icon'] = icon_content
                return
        
        # 添加新图标
        self.icons.append({"type": icon_type, "icon": icon_content})
    
    def remove_icon(self, icon_type):
        """移除指定类型的图标"""
        if self.icons:
            self.icons = [icon for icon in self.icons if icon.get('type') != icon_type]
