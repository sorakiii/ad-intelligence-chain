import requests
from flask import current_app
import os
import mimetypes
import time
import json
import tempfile
from app.utils.json_helper import clean_and_parse_json  # 修改为绝对导入
from app.utils.logger import get_logger

logger = get_logger(__name__)

class DifyService:
    """Dify API 服务类"""
    
    def __init__(self, api_key=None):
        """初始化 Dify 服务
        
        Args:
            api_key: 可选的 API key，如果不提供则使用默认配置
        """
        # 确保base_url末尾没有斜杠，并且包含 /v1
        base_url = current_app.config['DIFY_API_URL']
        base_url = base_url.rstrip('/')
        if not base_url.endswith('/v1'):
            base_url = f"{base_url}/v1"
        self.base_url = base_url
        
        # 使用传入的 API key 或配置中的默认值
        self.api_key = api_key or current_app.config['DIFY_API_KEY']
        
        if not self.api_key or not self.api_key.startswith('app-'):
            raise ValueError("Invalid Dify API Key format")
        
        logger.info(f"DifyService initialized with URL: {self.base_url}")
        logger.debug(f"Using API Key starting with: {self.api_key[:8]}...")
        
    def _get_headers(self):
        """获取请求头"""
        # 这里使用 Dify 的 API Key，而不是我们系统的 JWT token
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # Dify的API Key
            "Content-Type": "application/json"
        }
        # 不要在日志中暴露完整的API Key
        logger.debug("Request headers prepared with Dify API Key")
        return headers
    
    def chat_messages(self, query, inputs=None, response_mode="blocking", user=None, conversation_id=None, files=None, parent_message_id=None):
        """
        发送聊天消息到 Dify
        
        Args:
            query (str): 用户查询内容
            inputs (dict, optional): 输入参数
            response_mode (str, optional): 响应模式，可选 "blocking" 或 "streaming"
            user (str, optional): 用户标识
            conversation_id (str, optional): 会话ID
            files (list, optional): 文件列表
            parent_message_id (str, optional): 父消息ID，用于编辑消息
            
        Returns:
            Response: 请求响应
        """
        url = f"{self.base_url}/chat-messages"
        
        payload = {
            "inputs": inputs or {},
            "query": query,
            "response_mode": response_mode,
            "user": user
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
            
        if files:
            payload["files"] = files
            
        if parent_message_id:
            payload["parent_message_id"] = parent_message_id
            logger.info(f"Adding parent_message_id to request: {parent_message_id}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 调试输出完整请求
        logger.debug(f"Dify API request - URL: {url}, Payload: {payload}")
        
        response = requests.post(url, json=payload, headers=headers, stream=response_mode == "streaming")
        return response

    def chat_messages_stream(self, query, inputs={}, user=None, conversation_id=None, files=None):
        """流式发送对话消息"""
        try:
            url = f"{self.base_url}/chat-messages"
            
            # 构造请求体，确保所有参数都有效
            payload = {
                "inputs": inputs or {},
                "query": query,
                "response_mode": "streaming",
                "user": str(user) if user else "default"
            }
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
                
            # 处理文件
            if files and isinstance(files, list) and len(files) > 0:
                # 直接使用传入的文件列表，因为格式已经在上层处理好了
                payload["files"] = files
                logger.debug(f"Adding files to payload: {files}")
                
            logger.debug(f"Sending streaming request to Dify API: {url}")
            logger.debug(f"Request payload: {payload}")
            
            response = requests.post(
                url, 
                json=payload, 
                headers=self._get_headers(),
                stream=True
            )
            
            if response.status_code != 200:
                logger.error(f"Dify API error - Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                error_data = response.json() if response.text else {}
                error_message = error_data.get('message', f"Dify API returned status {response.status_code}")
                raise Exception(error_message)
                
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Dify API request failed: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Error response: {e.response.text}")
            raise

    def get_conversation_messages(self, conversation_id, user, first_id=None, limit=20):
        """获取会话历史消息"""
        url = f"{self.base_url}/messages"
        params = {
            "conversation_id": conversation_id,
            "user": user,
            "first_id": first_id,
            "limit": limit
        }
        
        try:
            response = requests.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get conversation messages error: {str(e)}")
            raise

    def get_conversations(self, user, last_id=None, limit=20, sort_by="-updated_at"):
        """获取会话列表"""
        url = f"{self.base_url}/conversations"
        params = {
            "user": user,
            "last_id": last_id,
            "limit": limit,
            "sort_by": sort_by
        }
        
        try:
            response = requests.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get conversations error: {str(e)}")
            raise

    def delete_conversation(self, conversation_id, user):
        """删除会话"""
        url = f"{self.base_url}/conversations/{conversation_id}"
        params = {"user": user}
        
        try:
            response = requests.delete(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Delete conversation error: {str(e)}")
            raise

    def rename_conversation(self, conversation_id, name, user, auto_generate=False):
        """重命名会话"""
        url = f"{self.base_url}/conversations/{conversation_id}/name"
        payload = {
            "name": name,
            "auto_generate": auto_generate,
            "user": user
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Rename conversation error: {str(e)}")
            raise

    def upload_file(self, file_path, user=None):
        """上传文件到 Dify"""
        try:
            logger.debug(f"Uploading file to Dify: {os.path.basename(file_path)}")
            
            # 如果是 URL，直接下载文件内容
            if file_path.startswith('http'):
                response = requests.get(file_path, stream=True)
                response.raise_for_status()
                file_content = response.content
                file_name = os.path.basename(file_path)
                content_type = response.headers.get('Content-Type', 'application/octet-stream')
            else:
                # 本地文件
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                file_name = os.path.basename(file_path)
                content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            
            logger.debug(f"Content type: {content_type}")
            
            # 从 MIME 类型获取正确的扩展名
            mime_to_ext = {
                'application/pdf': 'pdf',
                'application/msword': 'doc',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
                'text/plain': 'txt',
                'text/markdown': 'md',
                'text/html': 'html',
                'text/csv': 'csv',
                'message/rfc822': 'eml',
                'application/xml': 'xml',
                'application/epub+zip': 'epub',
                'image/jpeg': 'jpg',
                'image/png': 'png',
                'image/gif': 'gif',
                'image/webp': 'webp',
                'image/svg+xml': 'svg'
            }
            
            # 获取正确的扩展名
            extension = mime_to_ext.get(content_type.lower())
            if not extension and '.' in file_name:
                extension = file_name.rsplit('.', 1)[1].lower()
            
            # 如果仍然无法获取扩展名，使用默认值
            if not extension:
                extension = 'bin'
            
            # 创建一个带有正确扩展名的临时文件
            with tempfile.NamedTemporaryFile(suffix=f'.{extension}', delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # 准备上传请求
                url = f"{self.base_url}/files/upload"
                headers = {
                    'Authorization': f"Bearer {self.api_key}"
                }
                
                # 使用临时文件上传，确保文件名只包含扩展名，不包含点号
                with open(temp_file_path, 'rb') as f:
                    # 使用一个简单的文件名，确保扩展名正确
                    simple_filename = f"file.{extension}"
                    files = {'file': (simple_filename, f, content_type)}
                    
                    if user:
                        data = {'user': user}
                        response = requests.post(url, headers=headers, files=files, data=data)
                    else:
                        response = requests.post(url, headers=headers, files=files)
                    
                    response.raise_for_status()
                    
                    logger.info("File uploaded successfully to Dify")
                    logger.debug(f"Dify response: {response.text}")
                    
                    return response.json()
            finally:
                # 删除临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        
        except Exception as e:
            logger.error(f"Error uploading file to Dify: {str(e)}")
            raise

    def stop_chat_message(self, task_id, user):
        """停止消息响应"""
        try:
            url = f"{self.base_url}/chat-messages/{task_id}/stop"
            
            payload = {
                "user": user
            }
            
            logger.debug(f"Sending stop request to Dify API: {url}")
            logger.debug(f"Request payload: {payload}")
            
            # 添加更多错误处理和重试逻辑
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(url, json=payload, headers=self._get_headers())
                    
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 404:
                        logger.error(f"Task {task_id} not found")
                        raise Exception("Task not found")
                    else:
                        logger.error(f"Dify API error - Status: {response.status_code}")
                        logger.error(f"Response: {response.text}")
                        
                    if attempt < max_retries - 1:
                        time.sleep(1)  # 重试前等待
                        continue
                        
                    raise Exception(f"Dify API returned status {response.status_code}")
                    
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        continue
                    raise
                
        except Exception as e:
            logger.error(f"Dify API request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Error response: {e.response.text}")
            raise

    def message_feedback(self, message_id, rating, user, content=None):
        """消息反馈"""
        try:
            # 检查消息 ID 格式
            if not message_id:
                raise ValueError("Message ID is required")
            
            # 构造完整的 URL
            url = f"{self.base_url}/messages/{message_id}/feedbacks"
            logger.debug(f"Dify feedback API URL: {url}")
            
            # 构造请求体 - 修改 rating 处理
            payload = {
                "user": user,
                "rating": "null" if rating is None else rating  # 使用字符串 "null" 来取消反馈
            }
            
            if content:
                payload["content"] = content
            
            # 获取请求头
            headers = self._get_headers()
            
            # 详细的请求日志
            logger.debug("Dify feedback request details:")
            logger.debug(f"- URL: {url}")
            logger.debug(f"- Method: POST")
            logger.debug(f"- Headers: {headers}")
            logger.debug(f"- Payload: {payload}")
            
            # 发送请求
            response = requests.post(url, json=payload, headers=headers)
            
            # 响应日志
            logger.debug(f"Dify response status: {response.status_code}")
            logger.debug(f"Dify response headers: {dict(response.headers)}")
            logger.debug(f"Dify response body: {response.text}")
            
            if response.status_code == 404:
                error_msg = response.json().get('message', '')
                logger.warning(f"Message {message_id} not found in Dify: {error_msg}")
                raise Exception(f"Message Not Exists: {error_msg}")
            elif response.status_code != 200:
                logger.error(f"Dify API error - Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Dify API returned status {response.status_code}")
                
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Dify API request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Error response: {e.response.text}")
            raise

    def get_suggested_questions(self, message_id, user):
        """获取下一轮建议问题列表"""
        try:
            # 修正 URL 路径
            url = f"{self.base_url}/messages/{message_id}/suggested"
            
            params = {
                "user": user
            }
            
            logger.debug("Dify suggested questions request details:")
            logger.debug(f"- URL: {url}")
            logger.debug(f"- Method: GET")
            logger.debug(f"- Params: {params}")
            
            response = requests.get(
                url,
                params=params,
                headers=self._get_headers()
            )
            
            # 响应日志
            logger.debug(f"Dify response status: {response.status_code}")
            
            # 只有在状态码为 200 时才尝试解析 JSON
            if response.status_code == 200:
                logger.debug(f"Dify response body: {response.text}")
                return response.json()
            
            # 处理错误情况
            if response.status_code == 404:
                try:
                    error_msg = response.json().get('message', 'Message not found')
                except:
                    error_msg = 'Message not found'
                logger.warning(f"Message {message_id} not found in Dify: {error_msg}")
                raise Exception(f"Message Not Exists: {error_msg}")
            else:
                logger.error(f"Dify API error - Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Dify API returned status {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Dify API request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Error response: {e.response.text}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Raw response: {response.text}")
            raise Exception("Invalid response format from Dify API")

    def generate_conversation_name(self, conversation_id, user, auto_generate=True, name=None):
        """生成或更新会话标题"""
        try:
            url = f"{self.base_url}/conversations/{conversation_id}/name"
            
            data = {
                "user": user,
                "auto_generate": auto_generate
            }
            if name:
                data["name"] = name
            
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=data
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to generate conversation name: {str(e)}")
            raise

    def get_parameters(self):
        """获取应用参数配置"""
        try:
            url = f"{self.base_url}/parameters"
            
            response = requests.get(
                url,
                headers=self._get_headers()
            )
            
            if response.status_code != 200:
                logger.error(f"Dify API error - Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Dify API returned status {response.status_code}")
                
            data = response.json()
            
            # 转换为标准格式
            parameters = {
                'opening_statement': data.get('opening_statement', ''),
                'suggested_questions': data.get('suggested_questions', []),
                'suggested_questions_after_answer': {
                    'enabled': data.get('suggested_questions_after_answer', {}).get('enabled', False)
                },
                'speech_to_text': {
                    'enabled': data.get('speech_to_text', {}).get('enabled', False)
                },
                'retriever_resource': {
                    'enabled': data.get('retriever_resource', {}).get('enabled', False)
                },
                'annotation_reply': {
                    'enabled': data.get('annotation_reply', {}).get('enabled', False)
                },
                'user_input_form': [],
                'file_upload': {
                    'image': {
                        'enabled': data.get('file_upload', {}).get('image', {}).get('enabled', False),
                        'number_limits': data.get('file_upload', {}).get('image', {}).get('number_limits', 3),
                        'transfer_methods': data.get('file_upload', {}).get('image', {}).get('transfer_methods', [])
                    }
                },
                'system_parameters': {
                    'file_size_limit': data.get('system_parameters', {}).get('file_size_limit', 15),
                    'image_file_size_limit': data.get('system_parameters', {}).get('image_file_size_limit', 10),
                    'audio_file_size_limit': data.get('system_parameters', {}).get('audio_file_size_limit', 10),
                    'video_file_size_limit': data.get('system_parameters', {}).get('video_file_size_limit', 100)
                }
            }
            
            # 处理用户输入表单
            for form_item in data.get('user_input_form', []):
                if 'type' not in form_item:
                    continue
                    
                input_config = {
                    'label': form_item.get('label', ''),
                    'variable': form_item.get('variable', ''),
                    'required': form_item.get('required', False),
                    'default': form_item.get('default', '')
                }
                
                if form_item['type'] == 'select':
                    input_config['options'] = form_item.get('options', [])
                    
                parameters['user_input_form'].append({
                    form_item['type']: input_config
                })
                
            return parameters
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Dify API request failed: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Error response: {e.response.text}")
            raise

    def fix_file_extension(self, file_id, correct_extension):
        """修复 Dify 文件的扩展名"""
        try:
            # 这里我们需要使用 Dify 的管理 API 来修改文件扩展名
            # 由于 Dify 可能没有直接提供修改文件扩展名的 API，我们可以尝试以下方法：
            
            # 1. 获取文件信息
            url = f"{self.base_url}/files/{file_id}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            file_info = response.json()
            
            # 2. 如果文件扩展名不正确，我们可以尝试重新上传文件
            if file_info.get('extension', '').lstrip('.').lower() != correct_extension.lower():
                logger.info(f"Fixing file extension for {file_id}: changing to {correct_extension}")
                
                # 下载文件内容
                download_url = f"{self.base_url}/files/{file_id}/download"
                download_response = requests.get(download_url, headers=headers)
                download_response.raise_for_status()
                
                # 创建临时文件
                with tempfile.NamedTemporaryFile(suffix=f'.{correct_extension}', delete=False) as temp_file:
                    temp_file.write(download_response.content)
                    temp_file_path = temp_file.name
                
                try:
                    # 上传新文件
                    new_file_info = self.upload_file(temp_file_path, file_info.get('user_id'))
                    
                    # 返回新文件 ID
                    return new_file_info.get('id')
                finally:
                    # 删除临时文件
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
            
            return file_id
        except Exception as e:
            logger.error(f"Error fixing file extension: {str(e)}")
            # 如果修复失败，返回原始文件 ID
            return file_id

    def convert_script_to_json(self, script_data, user=None):
        """将脚本数据转换为JSON格式并发送到Dify处理
        
        Args:
            script_data (str): 脚本的原始数据内容
            user (str, optional): 用户标识
            
        Returns:
            dict: Dify API的JSON响应结果
        """
        try:
            # 使用特定的API Key发送请求
            
            url = f"{self.base_url}/chat-messages"
            
            # 准备请求体
            payload = {
                "inputs": {},
                "query": script_data,  # 将脚本数据作为查询内容
                "response_mode": "blocking",  # 使用阻塞模式等待完整响应
                "user": user or "system"  # 如果未提供用户标识，则使用"system"
            }
            logger.warning(f"Dify script payload: {payload}")
            
            # 使用特定的API Key构建请求头
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.debug(f"Converting script to JSON - URL: {url}")
            logger.debug(f"Script length: {len(script_data)} characters")
            
            # 发送请求
            response = requests.post(url, json=payload, headers=headers)
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"Script conversion error - Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Script conversion failed with status {response.status_code}")
            
            # 解析响应内容
            result = response.json()
            logger.warning(f"Dify script result: {result}")
            # 提取并解析answer部分为JSON
            if 'answer' in result:
                try:
                    # 使用新的清理函数
                    json_content = clean_and_parse_json(result['answer'])
                    logger.info("Script successfully converted to JSON format")
                    return json_content
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Response is not valid JSON: {str(e)}")
                    return result['answer']
            else:
                logger.warning("No answer field in response")
                return result
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Script conversion request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Error response: {e.response.text}")
            raise Exception(f"Failed to convert script: {str(e)}")
        except Exception as e:
            logger.error(f"Script conversion error: {str(e)}")
            raise

    def convert_text_to_prompt_json(self, text_data, user=None):
        """将文本转换为绘画提示词 JSON 格式
        
        Args:
            text_data (str): 原始文本内容
            user (str, optional): 用户标识
            
        Returns:
            dict: 结构化的绘画提示词 JSON 对象，包含 ai_mj 字段
        """
        try:
            
            url = f"{self.base_url}/chat-messages"
            
            # 准备请求体
            payload = {
                "inputs": {},
                "query": f"{text_data}",  # 添加明确的指令
                "response_mode": "blocking",
                "user": user or "system"
            }
            
            # 使用特定的 API Key 构建请求头
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.debug(f"Converting text to prompt JSON - URL: {url}")
            logger.debug(f"Text length: {len(text_data)} characters")
            
            # 发送请求
            response = requests.post(url, json=payload, headers=headers)
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"Text conversion error - Status: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Text conversion failed with status {response.status_code}")
            
            # 解析响应内容
            result = response.json()
            
            # 提取并解析 answer 部分为 JSON
            if 'answer' in result:
                try:
                    # 使用新的清理函数
                    json_content = clean_and_parse_json(result['answer'])
                    logger.info("Text successfully converted to prompt JSON format")
                    
                    # 确保返回的 JSON 包含必要的字段
                    if not isinstance(json_content, dict):
                        raise ValueError("Response is not a valid JSON object")
                        
                    # 设置默认值
                    prompt_json = {
                        "ai_mj": json_content.get("ai_mj", result['answer'])
                    }
                    
                    return prompt_json
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Response is not valid JSON: {str(e)}")
                    return {"ai_mj": result['answer']}
            else:
                logger.warning("No answer field in response")
                return {"ai_mj": str(result)}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Text conversion request failed: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Error response: {e.response.text}")
            raise Exception(f"Failed to convert text: {str(e)}")
        except Exception as e:
            logger.error(f"Text conversion error: {str(e)}")
            raise 

    def generate_html_by_workflow(self, text_data, model=None, user=None):
        """
        调用 deepseek/dify 服务生成 HTML 网页内容
        Args:
            text_data (str): 用户输入内容
            model (str, optional): 模型名称
            user (str, optional): 用户标识
        Returns:
            str: 生成的 HTML 字符串
        """
        url = f"{self.base_url}/chat-messages"
        payload = {
            "inputs":  {"model_name": model} if model else {},
            "query": f"{text_data}",
            "response_mode": "blocking",
            "user": user or "system"
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"HTML生成失败: {response.status_code} {response.text}")
        result = response.json()
        # 假设 answer 字段直接为 HTML 字符串
        html_code = result.get("answer", "")
        # 如果html_code 以```html开始 和 ``` 结束， 则去掉 前面的 ```html 和 后面的 ```
        if html_code.startswith("```html"):
            html_code = html_code[len("```html"):]
        if html_code.endswith("```"):
            html_code = html_code[:-len("```")]
        return html_code
