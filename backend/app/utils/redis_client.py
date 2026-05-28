from flask import current_app
import redis
from datetime import timedelta

class RedisClient:
    def __init__(self):
        try:
            self.client = redis.from_url(current_app.config['REDIS_URL'])
            self.client.ping()  # 测试连接
        except redis.ConnectionError:
            current_app.logger.error("Redis connection failed. Make sure Redis is running.")
            # 如果Redis连接失败，使用内存字典作为临时存储
            self.client = {}
            self._use_memory_store = True
        else:
            self._use_memory_store = False

    def set_verification_code(self, phone, code, expires=300):  # 5分钟过期
        try:
            if self._use_memory_store:
                self.client[f"verification_code:{phone}"] = code
                return
            key = f"verification_code:{phone}"
            self.client.setex(key, timedelta(seconds=expires), code)
        except Exception as e:
            current_app.logger.error(f"Redis error in set_verification_code: {str(e)}")

    def get_verification_code(self, phone):
        try:
            if self._use_memory_store:
                return self.client.get(f"verification_code:{phone}")
            key = f"verification_code:{phone}"
            return self.client.get(key)
        except Exception as e:
            current_app.logger.error(f"Redis error in get_verification_code: {str(e)}")
            return None

    def delete_verification_code(self, phone):
        try:
            if self._use_memory_store:
                self.client.pop(f"verification_code:{phone}", None)
                return
            key = f"verification_code:{phone}"
            self.client.delete(key)
        except Exception as e:
            current_app.logger.error(f"Redis error in delete_verification_code: {str(e)}")

    def set_send_limit(self, phone, expires=60):  # 1分钟内不能重复发送
        try:
            if self._use_memory_store:
                self.client[f"send_limit:{phone}"] = 1
                return
            key = f"send_limit:{phone}"
            self.client.setex(key, timedelta(seconds=expires), 1)
        except Exception as e:
            current_app.logger.error(f"Redis error in set_send_limit: {str(e)}")

    def can_send_code(self, phone):
        try:
            if self._use_memory_store:
                return f"send_limit:{phone}" not in self.client
            key = f"send_limit:{phone}"
            return not bool(self.client.exists(key))
        except Exception as e:
            current_app.logger.error(f"Redis error in can_send_code: {str(e)}")
            return True  # 如果Redis出错，默认允许发送 