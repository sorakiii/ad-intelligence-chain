import os
import sys
import json
import pytest
from flask import Flask

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # backend directory
sys.path.append(project_root)

from app.services.dify_service import DifyService

pytestmark = pytest.mark.skipif(
    not os.getenv('DIFY_API_KEY'),
    reason='Set DIFY_API_KEY and DIFY_API_URL env vars to run integration tests',
)

# 创建测试用的 Flask 应用
app = Flask(__name__)

app.config.update({
    'DIFY_API_URL': os.getenv('DIFY_API_URL', 'http://mock-dify-api.com'),
    'DIFY_API_KEY': os.getenv('DIFY_API_KEY'),
})

# 测试脚本
test_script = """
    ### **创意短视频脚本 | Y700 平板 —— 黄金尺寸，性能 NO.1**  

---

#### **1. 开场（3-5秒）**  
- **镜头语言：** 城市天际线延时 → 推进至人物中景（人物在咖啡馆/公园/地铁等场景中）  
- **文案：**  
  「这里是____（城市名称），人潮流动，节奏疾驰。手中这台 Y700，黄金尺寸，刚刚好。」  

---

#### **2. 过渡（2秒）**  
- **镜头语言：** 第一视角，手指轻触屏幕，画面切换至游戏/视频界面  
- **音效：** 环境音渐弱，电子音效渐入（如屏幕点按声）  

---
"""

if __name__ == '__main__':
    with app.app_context():
        try:
            dify_service = DifyService()
            print("开始测试 Dify 服务...")
            result = dify_service.convert_script_to_json(test_script, 'test-user')
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("\n测试完成!")
        except Exception as e:
            print(f"测试失败: {str(e)}")
