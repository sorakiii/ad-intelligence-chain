import json

def json_to_video_prompt(json_data):
    """将完整脚本转换为单个提示词"""
    prompt_parts = []
    
    # 添加标题和描述
    title = json_data.get("title", "")
    description = json_data.get("description", "")
    if title:
        prompt_parts.append(f"视频标题：{title}")
    if description:
        prompt_parts.append(f"视频主题：{description}")
    
    # 处理内容部分
    prompt_parts.append("视频结构：")
    for content in json_data.get("content", []):
        part_desc = f"{content.get('part', '')}："
        
        # 处理镜头描述
        shots_desc = []
        for shot in content.get("shots", []):
            shot_type = shot.get("type", "")
            shot_desc = shot.get("description", "")
            shots_desc.append(f"{shot_type}：{shot_desc}")
        
        if shots_desc:
            part_desc += "；".join(shots_desc)
            
        prompt_parts.append(part_desc)
    
    return "。".join(prompt_parts) + "。"

def convert_script_to_prompts(script_json):
    """将视频脚本转换为多个独立的镜头提示词"""
    prompts = []
    
    title = script_json.get("title", "")
    description = script_json.get("description", "")
    
    if "content" in script_json:
        for section in script_json["content"]:
            if "shots" in section:
                for shot in section["shots"]:
                    # 构建完整的提示词
                    prompt = f"{shot['description']}"
                    
                    prompt_data = {
                        "prompt": prompt,  # 确保包含提示词
                        "script_data": json.dumps({
                            "type": shot["type"],
                            "description": shot["description"],
                            "part": section["part"]
                        }, ensure_ascii=False)
                    }
                    prompts.append(prompt_data)
    
    return prompts

# 示例使用
if __name__ == "__main__":
    # 这里应该是你的JSON数据
    example_json = {
  "title": "Y700 平板 —— 黄金尺寸，性能 NO.1",
  "description": "一台刚刚好的平板，既轻便又强劲，Y700 用黄金尺寸演绎生活、游戏、影音的完美平衡。快节奏镜头切换带你走进它的精彩世界，探索属于你的「刚刚好」。",
  "content": [
    {
      "part": "画面1",
      "shots": [
        {
          "type": "延时+中景镜头",
          "description": "城市天际线延时拍摄，光影交替、车流穿梭，镜头推进至一名在咖啡馆/地铁/公园场景中的人物中景，人群流动中主角安静使用平板，突出都市节奏与个人空间反差。"
        },
        {
          "type": "画外音+字幕",
          "description": "文案叠加：「这里是____（城市名称），人潮流动，节奏疾驰。手中这台 Y700，黄金尺寸，刚刚好。」"
        }
      ]
    },
    {
      "part": "画面2",
      "shots": [
        {
          "type": "第一人称视角",
          "description": "手指触碰平板屏幕，画面瞬间切换，进入游戏或视频界面。"
        },
        {
          "type": "音效过渡",
          "description": "环境声逐渐减弱，电子点击音叠加，气氛转为专注沉浸。"
        }
      ]
    },
    {
      "part": "画面3",
      "shots": [
        {
          "type": "生活场景大片段镜头组",
          "description": "地铁内单手握持 Y700 翻阅电子书；切换到咖啡馆，连接蓝牙键盘，角色在轻松办公；再切换到用户从包中取出 Y700，展示便捷性。"
        },
        {
          "type": "文案叠加",
          "description": "文案：「它比一本书更轻，比一台笔电更自由。7 寸黄金尺寸，刚刚好装进你的节奏。」"
        }
      ]
    },
    {
      "part": "画面4",
      "shots": [
        {
          "type": "游戏镜头组",
          "description": "展示高帧率手游实况：角色快速切换、释放技能；细节镜头中拍摄手指与触控区域，强调操控感。"
        },
        {
          "type": "画面对比",
          "description": "左右对比：同尺寸其它平板 vs Y700，Y700 明显更流畅，强调高性能。"
        },
        {
          "type": "文案叠加",
          "description": "文案：「小尺寸？但性能，全开！高刷、低延迟，Y700 让指尖快过子弹。」"
        },
        {
          "type": "互动提示",
          "description": "画面右下弹出问题：「手机太小，笔电太大，你的黄金尺寸是什么？」引导用户评论互动。"
        }
      ]
    },
    {
      "part": "画面5",
      "shots": [
        {
          "type": "影音体验镜头组",
          "description": "播放高清视频，色彩丰富，人物眼神细节可见；随后切换为多任务分屏，一侧运行游戏，一侧浏览攻略或聊天；最后是人物凝视屏幕，深度沉浸。"
        },
        {
          "type": "文案叠加",
          "description": "文案：「2.5K 屏幕，120Hz 高刷，色彩与细节，都该有它的位置。」"
        }
      ]
    },
    {
      "part": "画面6",
      "shots": [
        {
          "type": "桌面俯拍镜头",
          "description": "桌面放置三个设备：手机、笔电、Y700，Y700 位于中央，尺寸居中，象征平衡。"
        },
        {
          "type": "人物操作镜头",
          "description": "人物轻松拿起 Y700，转换场景进入办公/观影状态，面带微笑表现适配性强。"
        },
        {
          "type": "文案叠加",
          "description": "文案：「手机太小，笔电太大。黄金尺寸，刚刚好。」"
        }
      ]
    },
    {
      "part": "画面7",
      "shots": [
        {
          "type": "尾镜头+情感收束",
          "description": "城市夜色中，人物背影走向街道尽头灯火辉映，手中的 Y700 屏幕亮起，画面慢慢淡出。"
        },
        {
          "type": "结尾旁白+字幕",
          "description": "文案：「在快与慢之间，它刚刚好。这里是 __（博主名称），我们下次见。」"
        },
        {
          "type": "卡点特写",
          "description": "人物回头轻眨眼，构成 58 秒处记忆点。"
        }
      ]
    }
  ]
}
    
    prompt = json_to_video_prompt(example_json)
    print("生成的视频生成prompt:")
    print(prompt)
    
    prompts = convert_script_to_prompts(example_json)
    print("\n生成的独立镜头提示词:")
    for i, prompt_data in enumerate(prompts, 1):
        print(f"Prompt {i}:")
        print(f"  Description: {prompt_data['prompt']}")
        print(f"  Script Data: {prompt_data['script_data']}")
        print()
