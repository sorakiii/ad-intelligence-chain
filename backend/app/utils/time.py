from datetime import datetime, timedelta

def get_china_time():
    """获取中国时间（UTC+8）"""
    return datetime.utcnow() + timedelta(hours=8) 