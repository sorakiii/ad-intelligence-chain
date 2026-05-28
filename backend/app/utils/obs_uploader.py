
import logging
import requests
from obs import ObsClient
from flask import current_app
import os
from urllib.parse import urlparse
from typing import Optional, Tuple, Dict, Any, Union, BinaryIO

logger = logging.getLogger(__name__)
MAX_EXPIRES = 604800  # 7 days in seconds (maximum allowed by Huawei Cloud OBS)
class ObsUploadError(Exception):
    """Custom exception for OBS upload errors."""
    pass

def get_obs_config(obs_config: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    获取OBS配置信息，优先使用传入的配置，否则尝试从Flask应用配置中获取。
    
    Args:
        obs_config: 可选的OBS配置字典
        
    Returns:
        包含OBS配置信息的字典
        
    Raises:
        ValueError: 如果缺少必要的配置信息
    """
    if obs_config is None:
        if not current_app:
            raise ValueError("OBS configuration must be provided or run within Flask app context.")
        config = current_app.config
    else:
        config = obs_config

    # 验证配置完整性
    required_keys = ['OBS_ACCESS_KEY', 'OBS_SECRET_KEY', 'OBS_ENDPOINT', 'OBS_BUCKET']
    if not all(key in config for key in required_keys):
        missing_keys = [key for key in required_keys if key not in config]
        raise ValueError(f"Missing OBS configuration keys: {missing_keys}")
    
    return config

def initialize_obs_client(config: Dict[str, str]) -> ObsClient:
    """
    初始化OBS客户端。
    
    Args:
        config: 包含OBS配置的字典
        
    Returns:
        初始化好的ObsClient实例
        
    Raises:
        ObsUploadError: 初始化客户端失败时
    """
    try:
        # 处理OBS_ENDPOINT，移除可能的http/https前缀
        endpoint = config['OBS_ENDPOINT']
        if endpoint.startswith('http://') or endpoint.startswith('https://'):
            parsed = urlparse(endpoint)
            endpoint = parsed.netloc or endpoint
            
        obs_client = ObsClient(
            access_key_id=config['OBS_ACCESS_KEY'],
            secret_access_key=config['OBS_SECRET_KEY'],
            server=endpoint
        )
        return obs_client
    except Exception as e:
        logger.error(f"Failed to initialize OBS client: {e}", exc_info=True)
        raise ObsUploadError(f"OBS client initialization failed: {e}")

def generate_obs_object_key(user_id: str, task_id: str, file_url: str = "") -> str:
    """
    生成OBS对象存储的键值。
    
    Args:
        user_id: 用户ID
        task_id: 任务ID
        file_url: 可选的文件URL，用于提取文件扩展名
        
    Returns:
        生成的OBS对象键
    """
    # 从URL路径中尝试获取扩展名，默认为.mp4
    ext = '.mp4'
    if file_url:
        parsed_url = urlparse(file_url)
        _, parsed_ext = os.path.splitext(parsed_url.path)
        if parsed_ext:
            ext = parsed_ext
    
    # 确保task_id是字符串
    safe_task_id = str(task_id)
    
    # 定义结构化的对象键
    return f"video_tasks/{user_id}/{safe_task_id}{ext}"

def upload_to_obs(
    obs_client: ObsClient, 
    bucket_name: str, 
    object_key: str, 
    content: Union[bytes, BinaryIO],
) -> Dict[str, Any]:
    """
    上传内容到OBS存储。
    
    Args:
        obs_client: OBS客户端实例
        bucket_name: 存储桶名称
        object_key: 对象键
        content: 要上传的内容，可以是字节数据或文件对象
        content_type: 内容类型，默认为video/mp4
        
    Returns:
        OBS上传响应
        
    Raises:
        ObsUploadError: 上传失败时
    """
    logger.info(f"Uploading content to OBS bucket '{bucket_name}' with key '{object_key}'...")
    
    try:
        obs_response = obs_client.putObject(
            bucketName=bucket_name,
            objectKey=object_key,
            content=content,
        )
        
        if obs_response.status >= 300:
            error_msg = f"OBS upload failed with status {obs_response.status}. Reason: {obs_response.reason}, Error: {getattr(obs_response, 'errorMessage', 'Unknown error')}"
            logger.error(error_msg)
            raise ObsUploadError(error_msg)
            
        logger.info(f"Successfully uploaded content to OBS. Status: {obs_response.status}")
        return obs_response
    except ObsUploadError:
        raise
    except Exception as e:
        logger.error(f"Failed to upload content to OBS: {e}", exc_info=True)
        raise ObsUploadError(f"Content upload to OBS failed: {e}")

def generate_signed_url(
    obs_client: ObsClient, 
    bucket_name: str, 
    object_key: str, 
    expires: int = MAX_EXPIRES  # 默认使用最大有效期
) -> str:
    """
    为OBS对象生成签名URL。
    
    Args:
        obs_client: OBS客户端实例
        bucket_name: 存储桶名称
        object_key: 对象键
        expires: URL有效期（秒），最大值为7天（604800秒）
        
    Returns:
        生成的签名URL
        
    Raises:
        ObsUploadError: 生成签名URL失败时
    """
    try:
        # 确保不超过最大有效期
        expires = min(expires, MAX_EXPIRES)
        
        signed_url_response = obs_client.createSignedUrl(
            'GET',
            bucket_name,
            object_key,
            expires=expires
        )
        preview_url = signed_url_response.get('signedUrl')
        if not preview_url:
            raise ObsUploadError("Failed to generate signed URL: 'signedUrl' key missing in response.")
            
        logger.info(f"Generated signed URL (valid for {expires} seconds): {preview_url}")
        return preview_url
    except Exception as e:
        logger.error(f"Failed to generate signed URL for {object_key}: {e}", exc_info=True)
        raise ObsUploadError(f"Failed to generate signed URL: {e}")

def upload_video_from_url_to_obs(
    video_url: str,
    user_id: str,
    task_id: str,
    obs_config: Dict[str, str] = None
) -> Tuple[str, str]:
    """
    从URL下载视频并上传到华为云OBS。
    
    Args:
        video_url: 视频文件的公共URL
        user_id: 用户ID，用于构建OBS对象键
        task_id: 视频任务ID，用于构建OBS对象键
        obs_config: 可选的包含OBS配置的字典
        
    Returns:
        包含obs_object_key和signed_preview_url的元组
        
    Raises:
        ObsUploadError: 如果下载、上传或生成签名URL的任何步骤失败
        ValueError: 如果缺少OBS配置
    """
    # 获取OBS配置
    config = get_obs_config(obs_config)
    
    logger.info(f"Attempting to download video for task {task_id} from: {video_url}")

    try:
        # 使用流式下载处理可能的大文件
        with requests.get(video_url, stream=True, timeout=60) as response:
            response.raise_for_status()  # 对错误响应（4xx或5xx）抛出HTTPError
            
            # 如果可用，获取内容长度用于记录/进度（可选）
            content_length = response.headers.get('content-length')
            if content_length:
                logger.info(f"Video size: {int(content_length) / (1024 * 1024):.2f} MB")
                
            # 初始化OBS客户端
            obs_client = initialize_obs_client(config)
            
            # 生成OBS对象键
            obs_object_key = generate_obs_object_key(user_id, task_id, video_url)
            
            # 上传到OBS
            upload_to_obs(
                obs_client=obs_client,
                bucket_name=config['OBS_BUCKET'],
                object_key=obs_object_key,
                content=response.raw.read(),
            )
            
            # 生成签名URL
            preview_url = generate_signed_url(
                obs_client=obs_client,
                bucket_name=config['OBS_BUCKET'],
                object_key=obs_object_key
            )
            
            return obs_object_key, preview_url
            
    except requests.exceptions.RequestException as download_err:
        logger.error(f"Failed to download video from {video_url}: {download_err}", exc_info=True)
        raise ObsUploadError(f"Video download failed: {download_err}")
    except Exception as e:
        # 捕获处理过程中的任何其他意外错误
        logger.error(f"An unexpected error occurred during OBS upload process for task {task_id}: {e}", exc_info=True)
        # 重新引发为ObsUploadError以便一致处理
        raise ObsUploadError(f"Unexpected error during OBS upload: {e}")

# 上传特定类型的文件到OBS
def upload_file_to_obs(
    file_content: Union[bytes, BinaryIO],
    file_path: str,
    user_id: str,
    bucket_prefix: str = "uploads",
    content_type: str = None,
    obs_config: Dict[str, str] = None,
    expires: int = MAX_EXPIRES  # 默认使用最大有效期
) -> Tuple[str, str]:
    """
    上传文件内容到华为云OBS。
    
    Args:
        file_content: 文件内容，可以是字节或文件对象
        file_path: 文件路径，用于提取文件名和扩展名
        user_id: 用户ID，用于构建OBS对象键
        bucket_prefix: 存储桶中的前缀，默认为"uploads"
        content_type: 内容类型，如果为None则尝试自动检测
        obs_config: 可选的包含OBS配置的字典
        expires: 签名URL的有效期（秒）
        
    Returns:
        包含obs_object_key和signed_url的元组
        
    Raises:
        ObsUploadError: 上传失败时
        ValueError: 如果缺少OBS配置
    """
    # 获取OBS配置
    config = get_obs_config(obs_config)
    
    try:
        # 初始化OBS客户端
        obs_client = initialize_obs_client(config)
        
        # 从文件路径提取文件名
        filename = os.path.basename(file_path)
        
        # 生成OBS对象键
        object_key = f"{bucket_prefix}/{user_id}/{filename}"
        logger.info(f"Generated OBS object key for file: {object_key}")
        
        # 如果未提供content_type，尝试根据文件扩展名猜测
        if content_type is None:
            _, ext = os.path.splitext(file_path)
            if ext.lower() in ['.jpg', '.jpeg']:
                content_type = 'image/jpeg'
            elif ext.lower() == '.png':
                content_type = 'image/png'
            elif ext.lower() == '.pdf':
                content_type = 'application/pdf'
            elif ext.lower() in ['.mp4', '.mov']:
                content_type = 'video/mp4'
            else:
                content_type = 'application/octet-stream'
        
        # 上传到OBS
        upload_to_obs(
            obs_client=obs_client,
            bucket_name=config['OBS_BUCKET'],
            object_key=object_key,
            content=file_content,
            content_type=content_type
        )
        
        # 生成签名URL
        signed_url = generate_signed_url(
            obs_client=obs_client,
            bucket_name=config['OBS_BUCKET'],
            object_key=object_key,
            expires=expires
        )
        
        return object_key, signed_url
        
    except Exception as e:
        logger.error(f"Failed to upload file {file_path} to OBS: {e}", exc_info=True)
        raise ObsUploadError(f"File upload to OBS failed: {e}")
