import json

def clean_and_parse_json(json_str: str) -> dict:
    """
    清理并解析JSON字符串
    
    Args:
        json_str: 包含转义字符的JSON字符串
    
    Returns:
        dict: 解析后的JSON对象
    """
    # 移除开头的 ```json\n 和结尾的 ```
    if json_str.startswith('```json\n'):
        json_str = json_str[8:]
    if json_str.endswith('```'):
        json_str = json_str[:-3]
    
    # 解析JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")