"""Midjourney API Service"""
import time
import hashlib
from typing import Optional, Dict, Any
from dataclasses import dataclass
import requests
from flask import current_app
from app.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class MJResponse:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class MJService:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.app_key = current_app.config.get('MJ_APP_KEY', '')
        
    def _generate_signature(self, timestamp: str) -> str:
        """生成签名
        签名算法: md5(app_key + timestamp)
        """
        content = f"{self.app_key}{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        timestamp = str(int(time.time() * 1000))
        return {
            'Authorization': self.api_key,
            'App-Key': self.app_key,
            'Timestamp': timestamp,
            'Signature': self._generate_signature(timestamp),
            'Content-Type': 'application/json'
        }
    
    def generate_image(self, prompt_cn: str, phone_number:str, opt_uuid: Optional[str] = None) -> MJResponse:
        """生成新图片
        
        Args:
            prompt_cn: 中文提示词
            opt_uuid: 可选的操作UUID
        """
        try:
            url = f"{self.base_url}/api/common/open/mj/imagine"
            
            payload = {
                "promptCn": prompt_cn,
                "optUuid": opt_uuid,
                "action": "generate",  # 生成新图片使用 generate
                "phoneNumber": phone_number # 不要动。这是第三方api的定义
            }
            logger.debug(f"generate image payload: {payload}")
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            logger.warning(f"MJ generate image response: {data}")
            if data.get('result',{}).get('taskStatus',{}).get('code',{}) == 'FAIL':
                return MJResponse(success=False, error=data.get('result',{}).get('errorShow',''))
            
            return MJResponse(success=True, data=data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MJ generate image API error: {str(e)}")
            return MJResponse(success=False, error=str(e))

    def edit_image(self, action: str, image_id: str, phone_number:str, opt_uuid: Optional[str] = None) -> MJResponse:
        """编辑图片（放大/变体/重新生成等）
        
        Args:
            action: 操作值，如 "upsample MJ::JOB::upsample::1::31a4e28f-2cf4-4202-bbf1-4024e8cb7f7a"
            imageId: MJ任务ID
            opt_uuid: 可选的操作UUID
        """
        try:
            url = f"{self.base_url}/api/common/open/mj/imagine"
            
            payload = {
                "action": action,
                "imageId": image_id,
                "optUuid": opt_uuid,
                "phoneNumber": phone_number # 不要动。这是第三方api的定义
            }
            logger.debug(f"edit image payload: {payload}")
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            return MJResponse(success=True, data=data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MJ edit image API error: {str(e)}")
            return MJResponse(success=False, error=str(e))

    def cancel(self, user_imagine_id: int) -> MJResponse:
        """取消生图
        
        Args:
            user_imagine_id: 用户生图任务ID
        """
        try:
            url = f"{self.base_url}/api/common/open/mj/cancel"
            
            payload = {
                "userImagineId": user_imagine_id
            }
            
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            return MJResponse(success=True, data={"cancelled": response.json()})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MJ cancel API error: {str(e)}")
            return MJResponse(success=False, error=str(e))

    def query_progress(self, user_imagine_id: int) -> MJResponse:
        """查询生图进度
        
        Args:
            user_imagine_id: 用户生图任务ID
        """
        try:
            url = f"{self.base_url}/api/common/open/mj/progress"
            
            payload = {
                "userImagineId": int(user_imagine_id)  # 确保转换为整数
            }
            
            logger.warning(f"MJ progress API payload: {payload}")
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            logger.warning(f"MJ progress API response: {data}")
            if data.get('result',{}).get('taskStatus',{}).get('code','') == 'FAIL':
                return MJResponse(success=False, error=data.get('result',{}).get('errorShow',{}))
            return MJResponse(success=True, data=data)
            
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.error(f"MJ progress API error: {str(e)}")
            return MJResponse(success=False, error=str(e))
