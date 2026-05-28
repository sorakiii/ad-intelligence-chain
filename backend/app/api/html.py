import json
from flask import Blueprint, request, jsonify, Response, stream_with_context, send_file
from app.models.chat import ChatMessage, ChatSession
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.message_html import MessageHtml
from app.services.dify_service import DifyService
from app.utils.response import success_response, error_response
from app.utils.logger import get_logger
from app import db
import re
import time
import os
import redis
from sqlalchemy.orm import scoped_session, sessionmaker
from io import BytesIO
# from weasyprint import HTML
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import img2pdf
from PIL import Image
from io import BytesIO
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.tasks.html_tasks import generate_html_task

logger = get_logger(__name__)

html_bp = Blueprint('html', __name__)


@html_bp.route('/messages/html', methods=['GET'])
@jwt_required()
def get_message_html():
    """获取指定消息ID列表对应的HTML内容
    
    Query参数:
    - message_ids: 逗号分隔的消息ID列表，例如: ?message_ids=688,689,690
    - session_id: 会话ID，例如: ?session_id=688
    
    返回格式:
    {
        "code": 0,
        "message": "获取成功",
        "data": {
            "688": {  # 按消息ID分组
                "id": 1,
                "html_code": "...",
                "created_at": "2024-01-20T10:00:00Z",
                "updated_at": "2024-01-20T10:00:00Z",
                "status": "success"
            },
            "689": {...},
            ...
        }
    }
    """
    try:
        # 获取并验证消息ID列表
        message_ids_str = request.args.get('message_ids', '')
        session_id = request.args.get('session_id', 0)
        if not message_ids_str and not session_id:
            return error_response('消息ID列表不能为空')
            
        try:
            message_ids = [id.strip() for id in message_ids_str.split(',') if id.strip()]
        except ValueError:
            return error_response('消息ID格式错误')
            
        # 查询HTML内容
        if message_ids:
            html_records = MessageHtml.query.filter(
                MessageHtml.message_id.in_(message_ids)
            ).all()
        else:
            html_records = MessageHtml.query.filter(
                MessageHtml.session_id == session_id
            ).all()
        
        # 按消息ID分组整理结果
        result = {}
        now = datetime.utcnow()
        for record in html_records:
            status = record.status
            if status == "generating" and record.updated_at and (now - record.updated_at).total_seconds() > 5:
                status = "failed"
            key = record.message_id if record.type == 'message' else record.session_id
            result[key] = {
                'id': record.id,
                'html_code': record.html_code,
                'type': record.type,
                'session_id': record.session_id,
                'message_id': record.message_id,
                'prompt': record.prompt,
                'status': status,
                'created_at': record.created_at.isoformat() if record.created_at else None,
                'updated_at': record.updated_at.isoformat() if record.updated_at else None
            }
            
        return success_response('获取成功', result)
        
    except Exception as e:
        logger.error(f"Error in get_message_html: {e}")
        return error_response('服务器内部错误')

@html_bp.route('/generate/streaming', methods=['POST'])
@jwt_required()
def generate_html_streaming():
    """
    提交 HTML 生成任务（非流式响应）

    请求体格式:
    {
        "text": "要生成HTML的内容",
        "message_id": "20240120123456789",  # 必填，关联的消息ID
        "type": "message",  # 必填，关联的消息类型
        "session_id": "20240120123456789",  # 必填，关联的会话ID
        "model": "model_name",  # 可选，模型名称
        "key_type": "zip"  # 可选，生成类型，zip 或 raw
    }

    返回格式:
    {
        "code": 0,
        "message": "生成成功",
        "data": {
            "id": 1,
            "message_id": "20240120123456789",
            "type": "message",
            "session_id": "20240120123456789",
            "html_code": "...",
            "status": "generating",
            "created_at": "2024-01-20T10:00:00Z"
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data or 'text' not in data:
            return error_response('缺少必要的内容')
        if 'message_id' not in data and 'session_id' not in data:
            return error_response('缺少必要的消息ID')
        text = data['text']
        type = data['type']
        key_type = data.get('key_type', 'zip')
        if type == 'message':
            message_id = data['message_id']
            session_id = 0
        else:
            session_id = data['session_id']
            message_id = ""
        model = data.get('model')
        session = None
        message = None
        # 查询 message_id 是否存在
        if type == 'message':
            message = ChatMessage.query.filter_by(message_id=message_id, type='assistant').first()
        else:
            session = ChatSession.query.filter_by(id=session_id).first()
        if not message and not session:
            return error_response('消息ID不存在')
        # 更新数据就好
        if type == 'message':
            record = MessageHtml.query.filter_by(message_id=message.id).first()
        else:
            record = MessageHtml.query.filter_by(session_id=session.id).first()
        if record:
            record.html_code = ''
            record.prompt = text
            record.status = 'generating'
            db.session.commit()
        else:
            # 插入新记录
            if type == 'message':
                record = MessageHtml(message_id=message.id, html_code='', status='generating', prompt=text, type=type)
            else:
                record = MessageHtml(session_id=session.id, html_code='', status='generating', prompt=text,type=type)
        db.session.add(record)
        db.session.commit()
        # 启动 Celery 任务
        generate_html_task.delay(record.id, text, model, user_id, key_type)
        return success_response('生成成功',{
            'id': record.id,
            'message_id': record.message_id,
            'type': type,
            'prompt': record.prompt,
            'session_id': record.session_id,
            'html_code': record.html_code,
            'status': record.status,
            'created_at': record.created_at.isoformat()
        })
    except Exception as e:
        logger.error(f"Error in generate_html_streaming: {e}")
        return error_response('生成HTML失败')

@html_bp.route('/stream/html/preview', methods=['GET'])
@jwt_required()
def stream_html_preview():
    """
    根据 id 轮询数据库，实时推送 HTML 生成进度（SSE，无插入/任务触发）

    Query参数:
    - id: 消息ID

    返回格式（SSE流式事件）:
    data: {"html_code": "...", "status": "generating"}
    data: {"html_code": "...", "status": "success"}
    data: {"html_code": "...", "status": "failed"}
    """
    try:
        id = request.args.get('id')
        if not id:
            return error_response('缺少必要的消息ID')
        def stream():
            last_html_len = int(request.args.get('last_html_len', 0))
            Session = scoped_session(sessionmaker(bind=db.engine))
            last_status = None
            while True:
                session = Session()
                try:
                    rec = session.query(MessageHtml).filter_by(id=id).first()
                    if rec:
                        html_code = rec.html_code or ''
                        status = rec.status or 'generating'
                        if len(html_code) > last_html_len or status != last_status:
                            html_piece = html_code[last_html_len:]
                            yield f"data: {json.dumps({'html_piece': html_piece, 'status': status})}\n\n"
                            last_html_len = len(html_code)
                            last_status = status
                        if status in ['success', 'failed']:
                            break
                finally:
                    session.close()
                time.sleep(1)
        return Response(
            stream_with_context(stream()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
    except Exception as e:
        logger.error(f"Error in stream_html_preview: {e}")
        return error_response('轮询HTML失败')

@html_bp.route('/generate/pdf', methods=['GET'])
@jwt_required()
def generate_pdf():
    """
    根据 id 查询 html_code，转为 PDF 并下载

    Query参数:
    - id: 消息ID

    返回: PDF 文件流，Content-Type: application/pdf，Content-Disposition: attachment; filename="message_id.pdf"
    """
    try:
        id = request.args.get('id')
        if not id:
            return error_response('缺少必要的消息ID')
        
        # 查找 id 对应的 MessageHtml 记录
        record = MessageHtml.query.filter_by(id=id).first()
        if not record or not record.html_code:
            return error_response('未找到对应的HTML内容')
        
        html_code = record.html_code
        # 去除 markdown 代码块包裹
        html_code = re.sub(r'^```html\s*', '', html_code)
        html_code = re.sub(r'```\s*$', '', html_code)
        html_code = html_code.strip()
        
        if not html_code:
            return error_response('HTML内容为空')
        
        # 检查 HTML 内容是否已生成完成
        if record.status != 'success':
            return error_response('HTML内容尚未生成完成，请稍后再试')
        
        # 用浏览器生成 PDF
        pdf_io = BytesIO()
        try:
            generate_html_pdf(html_code, pdf_io)
        except Exception as e:
            logger.error(f"生成 PDF 失败: {e}")
            return error_response('PDF生成失败，请稍后重试')
        
        pdf_io.seek(0)
        filename = f"{id}.pdf"
        
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error in generate_pdf: {e}")
        return error_response('导出PDF失败，请稍后重试') 
    
def generate_html_pdf(html_code: str, io):
    """
    用浏览器高保真渲染 HTML，并分页截图生成多页 PDF，写入 BytesIO。

    Args:
        html_code (str): HTML 源码字符串，支持动态 JS 渲染。
        io (BytesIO): 目标 BytesIO 对象，PDF 内容将写入其中。

    Raises:
        Exception: 渲染、截图或 PDF 生成过程中出现的任何异常。
    """
    import tempfile
    import os
    import subprocess
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    import img2pdf
    from PIL import Image
    from io import BytesIO
    
    # 启动虚拟显示
    xvfb_process = None
    try:
        # 启动 Xvfb 虚拟显示
        xvfb_process = subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x24'])
        import time
        time.sleep(2)  # 等待虚拟显示启动
        
        # 页面宽度 1920px，高度仍为 A4 1123px
        PAGE_WIDTH_PX = 1920
        PAGE_HEIGHT_PX = 1123

        # 1. 写入临时 HTML 文件
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_code)
            html_path = f.name
        file_url = f'file://{html_path}'

        # 2. 启动 headless Chromium
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument(f'--window-size={PAGE_WIDTH_PX},{PAGE_HEIGHT_PX}')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # 禁用图片加载，提高速度
        options.binary_location = '/usr/bin/chromium'  # 使用 Chromium

        service = Service('/usr/bin/chromedriver')  # 使用 Chromium 的 chromedriver

        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get(file_url)
            # 等待页面加载和 JS 渲染
            time.sleep(3)
            
            # 1. 先获取 scrollHeight
            scroll_height = driver.execute_script("return document.body.scrollHeight")

            # 2. 计算所有 sticky/fixed 元素的 bottom 边界
            sticky_height = driver.execute_script("""
                var height = 0;
                var nodes = document.querySelectorAll('*');
                for (var i=0; i<nodes.length; i++) {
                    var style = window.getComputedStyle(nodes[i]);
                    if (style.position === 'sticky') {
                        var rect = nodes[i].getBoundingClientRect();
                        height += rect.height;
                    }
                }
                return height;
            """)
            
            # 3. 计算总高度
            total_height = scroll_height + sticky_height + 50
            driver.set_window_size(1920, int(total_height))

            # 截图
            png_bytes = driver.get_screenshot_as_png()

            # 转 PDF
            img = Image.open(BytesIO(png_bytes))
            img_byte_io = BytesIO()
            img.save(img_byte_io, format='PNG')
            img_byte_io.seek(0)
            io.write(img2pdf.convert(img_byte_io.getvalue()))
            io.seek(0)
            
        finally:
            driver.quit()
            os.remove(html_path)
            
    except Exception as e:
        logger.error(f"Chromium PDF 生成失败: {e}")
        # 如果 Chromium 方案失败，尝试使用简单的 PDF 生成
        try:
            generate_simple_pdf(html_code, io)
        except Exception as e2:
            logger.error(f"简单 PDF 生成也失败: {e2}")
            raise e2
            
    finally:
        # 清理虚拟显示
        if xvfb_process:
            xvfb_process.terminate()
            xvfb_process.wait()

def generate_simple_pdf(html_code: str, io):
    """
    简单的 PDF 生成方案，不依赖浏览器
    """
    try:
        # 使用 reportlab 生成简单的 PDF
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        
        # 创建 PDF 文档
        doc = SimpleDocTemplate(io, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # 将 HTML 转换为纯文本
        import re
        text_content = re.sub(r'<[^>]+>', '', html_code)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # 创建段落
        story = [Paragraph(text_content, styles['Normal'])]
        
        # 构建 PDF
        doc.build(story)
        
    except ImportError:
        # 如果没有 reportlab，创建一个包含 HTML 内容的简单 PDF
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(io, pagesize=letter)
        c.drawString(100, 750, "HTML Content:")
        
        # 分行显示 HTML 内容
        lines = html_code.split('\n')
        y_position = 700
        for i, line in enumerate(lines[:20]):  # 最多显示20行
            if y_position < 50:  # 如果页面空间不足，停止
                break
            c.drawString(100, y_position, line[:80] + "..." if len(line) > 80 else line)
            y_position -= 20
        
        c.save()
    """
    用浏览器高保真渲染 HTML，并分页截图生成多页 PDF，写入 BytesIO。

    Args:
        html_code (str): HTML 源码字符串，支持动态 JS 渲染。
        io (BytesIO): 目标 BytesIO 对象，PDF 内容将写入其中。

    Raises:
        Exception: 渲染、截图或 PDF 生成过程中出现的任何异常。
    """
    import tempfile
    import os
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    import img2pdf
    from PIL import Image
    from io import BytesIO
    
    # 页面宽度 1920px，高度仍为 A4 1123px
    PAGE_WIDTH_PX = 1920
    PAGE_HEIGHT_PX = 1123

    # 1. 写入临时 HTML 文件
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_code)
        html_path = f.name
    file_url = f'file://{html_path}'

    # 2. 启动 headless Chrome
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--window-size={PAGE_WIDTH_PX},{PAGE_HEIGHT_PX}')
    options.binary_location = '/usr/bin/chromium'

    service = Service('/usr/bin/chromedriver')

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(file_url)
        # 等待页面加载和 JS 渲染（可根据实际情况调整时间或用 WebDriverWait）
        import time
        time.sleep(2)
        # 1. 先获取 scrollHeight
        scroll_height = driver.execute_script("return document.body.scrollHeight")

        # 2. 计算所有 sticky/fixed 元素的 bottom 边界
        sticky_height = driver.execute_script("""
            var height = 0;
            var nodes = document.querySelectorAll('*');
            for (var i=0; i<nodes.length; i++) {
                var style = window.getComputedStyle(nodes[i]);
                if (style.position === 'sticky') {
                    var rect = nodes[i].getBoundingClientRect();
                    height += rect.height;
                }
            }
            return height;
        """)
        # 3. 计算总高度
        total_height = scroll_height+sticky_height+50
        driver.set_window_size(1920, int(total_height))


        # 截图
        png_bytes = driver.get_screenshot_as_png()

        # 转 PDF
        img = Image.open(BytesIO(png_bytes))
        img_byte_io = BytesIO()
        img.save(img_byte_io, format='PNG')
        img_byte_io.seek(0)
        io.write(img2pdf.convert(img_byte_io.getvalue()))
        io.seek(0)
    finally:
        driver.quit()
        os.remove(html_path)