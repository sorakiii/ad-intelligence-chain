import os
import mimetypes
from flask import current_app

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_file_extension(filename):
    """获取文件扩展名"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else None

def get_mime_type(filename):
    """获取MIME类型"""
    return mimetypes.guess_type(filename)[0] 