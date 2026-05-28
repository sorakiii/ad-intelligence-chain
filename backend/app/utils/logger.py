import logging
import sys
from typing import Optional
from flask import has_request_context, request
from logging.handlers import RotatingFileHandler
import os

# 获取当前文件所在目录的父目录父目录 (backend/app)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class RequestFormatter(logging.Formatter):
    """自定义日志格式器，添加请求相关信息"""
    
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.request_id = request.headers.get('X-Request-ID', '-')
        else:
            record.url = None
            record.remote_addr = None
            record.request_id = None
            
        return super().format(record)

def setup_logger(name: str, 
                log_file: Optional[str] = None,
                level: int = logging.DEBUG,
                max_bytes: int = 10 * 1024 * 1024,  # 10MB
                backup_count: int = 5) -> logging.Logger:
    """
    设置并返回一个配置好的logger实例
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径，如果为None则只输出到控制台
        level: 日志级别
        max_bytes: 单个日志文件最大大小
        backup_count: 保留的日志文件数量
    
    Returns:
        配置好的logger实例
    """
    
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
        
    # 设置格式
    formatter = RequestFormatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] '
        '[%(request_id)s] %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    
    return logger

# 创建默认logger
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取一个预配置的logger实例
    
    Args:
        name: 日志记录器名称，默认使用调用模块的名称
        
    Returns:
        配置好的logger实例
    """
    if name is None:
        # 获取调用者的模块名
        import inspect
        frame = inspect.currentframe()
        if frame is None:
            name = __name__
        else:
            try:
                name = frame.f_back.f_globals['__name__']
            finally:
                del frame
    
    # 使用绝对路径构建日志文件路径
    log_file = os.path.join(BASE_DIR, 'logs', f'{name}.log')
    return setup_logger(name, log_file)

# 示例用法
if __name__ == '__main__':
    # 获取logger
    logger = get_logger()
    
    # 测试各种日志级别
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
