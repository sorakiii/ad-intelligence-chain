import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import current_app
from datetime import datetime

class SMSService:
    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=2, backoff_factor=0.1)
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.timeout = 3

    def _http_post_headers_json(self, url, params):
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = self.session.post(
            url, 
            data=json.dumps(params), 
            headers=headers, 
            timeout=self.timeout
        ).text
        return response

    def send_code(self, phone, code):
        """
        发送验证码
        :param phone: 手机号
        :param code: 验证码
        :return: (success, message)
        """
        config = current_app.config
        msg_content = f"【{config['SMS_SIGN_NAME']}】{code} 是您的验证码。请勿与任何人分享此码。"
        
        params = {
            "account": config['SMS_ACCOUNT'],
            "password": config['SMS_PASSWORD'],
            "msg": msg_content,
            "phone": str(phone),
            "report": True
        }

        try:
            response = self._http_post_headers_json(config['SMS_URL'], params)
            current_app.logger.info(f"SMS send response: {response}")
            
            if response:
                result = json.loads(response)
                if result["code"] == "0":
                    current_app.logger.info(f"SMS send success, msgId: {result['msgId']}")
                    return True, result["msgId"]
                else:
                    current_app.logger.error(f"SMS send fail, error: {result['errorMsg']}")
                    return False, result["errorMsg"]
            
            current_app.logger.error("SMS send fail, response is null")
            return False, "Response is null"
            
        except Exception as e:
            current_app.logger.error(f"SMS send error: {str(e)}")
            return False, str(e) 