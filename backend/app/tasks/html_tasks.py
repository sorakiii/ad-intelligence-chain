import re
import json
from flask import current_app
from app import  db,celery
from app.models.message_html import MessageHtml
from app.services.dify_service import DifyService
import time
import logging
from sqlalchemy.orm.exc import StaleDataError, ObjectDeletedError

logger = logging.getLogger(__name__)


def _resolve_html_dify_api_key(html_type: str):
    key_name = 'DIFY_API_KEY_HTML_ZIP' if html_type == 'zip' else 'DIFY_API_KEY_HTML_RAW'
    return current_app.config.get(key_name) or current_app.config.get('DIFY_API_KEY')


@celery.task(bind=True, queue='html_generation', soft_time_limit=600, time_limit=600)
def generate_html_task(self, id, text, model, user_id, type='zip'):
    """
    Celery 异步任务：流式生成 HTML，分段写入数据库
    支持自动检测HTML完整性并续写，最多重试2轮
    任务超时限制：软限制5分钟，硬限制6分钟
    """
    record = db.session.query(MessageHtml).filter_by(id=id).first()
    if not record:
        logger.warning(f"MessageHtml record for id={id} not found, task exit.")
        return
    else:
        record.status = 'generating'
        record.html_code = ''
        record.error_message = None
        db.session.commit()

    api_key = _resolve_html_dify_api_key(type)
    if not api_key:
        logger.error("Dify API key not configured for HTML generation (type=%s)", type)
        record.status = 'failed'
        record.error_message = 'Dify API key not configured'
        db.session.commit()
        return

    try:
        dify_service = DifyService(api_key=api_key)
        inputs = {"model_name": model} if model else {}
        
        # 初始化变量
        conversation_id = None
        full_html = record.html_code or ""
        max_continue_rounds = 3  # 最多续写2轮
        current_round = 0
        start_time = time.time()  # 记录开始时间
        
        while current_round <= max_continue_rounds:
            # 检查是否超时 (软限制前30秒停止)
            if time.time() - start_time > 540:  # 9分钟
                logger.warning(f"HTML生成任务接近超时限制，停止续写。当前轮次: {current_round}")
                break
                
            # 确定本轮的查询内容
            if current_round == 0:
                query = text  # 第一轮使用原始文本
            else:
                #query = "基于上述未完成的HTML代码，继续编写衔接代码，在衔接已有代码时，确保新代码与已有代码之间没有重复的部分，避免不必要的冗余，不需要回复其他内容，仅输出代码即可"  # 续写轮使用"继续"
                query = "继续"  # 续写轮使用"继续"
                logger.info(f"HTML生成第{current_round}轮续写开始，conversation_id={conversation_id}")
            
            # 发送请求
            response = dify_service.chat_messages(
                query=query,
                inputs=inputs,
                user=str(user_id),
                conversation_id=conversation_id,
                response_mode="streaming"
            )
            
            # 处理流式响应
            buffer = []
            last_commit_time = time.time()
            round_html = ""  # 本轮生成的HTML内容
            round_start_time = time.time()  # 单轮开始时间
            
            for line in response.iter_lines():
                # 单轮超时检查 (最多2分钟/轮)
                if time.time() - round_start_time > 300:
                    logger.warning(f"第{current_round}轮生成超时，跳出本轮")
                    break
                    
                if isinstance(line, bytes):
                    line = line.decode('utf-8')
                if not line.strip():
                    continue
                if not line.startswith('data: '):
                    continue
                json_str = line.replace('data: ', '', 1)
                try:
                    data = json.loads(json_str)
                    
                    # 获取conversation_id（第一轮的第一次响应）
                    if current_round == 0 and conversation_id is None:
                        conversation_id = data.get('conversation_id')
                        if conversation_id:
                            logger.info(f"获取到conversation_id: {conversation_id}")
                    
                    if data.get('event') == 'message':
                        html_piece = data.get('answer', '')
                        buffer.append(html_piece)
                        round_html += html_piece
                        
                        # 定期提交到数据库 (减少提交频率，提高性能)
                        if len(buffer) >= 20 or (time.time() - last_commit_time) > 2:
                            full_html += "".join(buffer)
                            record.html_code = full_html
                            db.session.commit()
                            buffer = []
                            last_commit_time = time.time()
                            
                except (StaleDataError, ObjectDeletedError) as e:
                    logger.warning(f"MessageHtml record for id={id} deleted during task, exit. {e}")
                    return
                except Exception as e:
                    logger.debug(f"解析响应数据失败: {e}")
                    continue
            
            # 本轮结束，处理缓冲区剩余内容
            if buffer:
                full_html += "".join(buffer)
                record.html_code = full_html
                db.session.commit()
            
            logger.info(f"第{current_round}轮完成，本轮生成内容长度: {len(round_html)}, 耗时: {time.time() - round_start_time:.2f}秒")
            
            # 检查HTML完整性
            if _is_html_complete(full_html):
                logger.info(f"HTML生成完整，共{current_round + 1}轮，最终长度: {len(full_html)}, 总耗时: {time.time() - start_time:.2f}秒")
                break
            elif current_round < max_continue_rounds:
                logger.info(f"HTML不完整，准备第{current_round + 1}轮续写")
                current_round += 1
            else:
                logger.warning(f"已达到最大续写轮数({max_continue_rounds})，停止续写")
                break
        
        # 标记生成成功
        record.status = 'success'
        db.session.commit()
        logger.info(f"HTML生成任务完成，总耗时: {time.time() - start_time:.2f}秒")
        
    except (StaleDataError, ObjectDeletedError) as e:
        logger.warning(f"MessageHtml record for id={id} deleted during task, exit. {e}")
        return
    except Exception as e:
        logger.error(f"HTML生成任务失败: {e}")
        record.status = 'failed'
        record.error_message = str(e)
        db.session.commit()
        raise 

def _is_html_complete(html_content):
    """
    检查HTML内容是否完整
    
    Args:
        html_content (str): HTML内容
        
    Returns:
        bool: True表示完整，False表示不完整
    """
    if not html_content:
        return False
    
    # 去除末尾的空白字符
    content = html_content.strip()
    
    # 检查是否以 </html> 或 </html>``` 结尾
    html_end_patterns = [
        r'</html>\s*$',           # 以 </html> 结尾
        r'</html>\s*```\s*$',     # 以 </html>``` 结尾
    ]
    
    for pattern in html_end_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            logger.debug("检测到HTML完整结束标志")
            return True
    
    logger.debug("HTML未检测到完整结束标志")
    return False 