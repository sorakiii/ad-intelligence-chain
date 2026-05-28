# Text to Video
对于 房琪爆款短视频脚本 这个角色的聊天，需要新增一个功能。
1. 对于ai返回的内容，需要整理成 脚本，
譬如:
镜头 1：xxx
镜头 2：xxx
镜头 3：xxx
镜头 4：xxx
脚本可能多个。整理过程是否应该调用 dify 的工作流, 让ai解析出 json 规范化的格式。
然后显示给用户可以二次编辑。
每个脚本都要可以编辑。 用户编辑完点击确认 调用 阿里的 文生视频 模型 生成视频。
这个生成过程比较长，可能有 10～15 分钟。
对应有 2 个api:
1. 发起生成视频的task, 会返回task_id
2. 根据task_id 获取生成结果。

前端需要有视频生成中的 loading 状态。当视频生成好，需要显示视频，并可以播放和下载。

需要参考当前代码的实现：
譬如后端用的python flask, 代码在backend目录
前端用的vue。 代码在frontend目录

## json规范化

使用 LLM 来格式化 聊天内容。
譬如：
{
  "prompt": "请将以下文本内容转换为标准JSON格式，确保键名使用英文双引号，字符串值使用英文双引号，整数值无需引号，布尔值使用true/false，数组和对象需用方括号/花括号包裹。若内容含特殊字符需转义，保留原始换行符为\\n。示例模板：\n{\n  \"title\": \"字符串\",\n  \"duration\": 60,\n  \"shots\": [\n    {\"type\": \"延时摄影\", \"description\": \"镜头内容\"}\n  ],\n  \"hasMusic\": true\n}",
  "requirements": [
    "1. 严格遵循JSON语法规范",
    "2. 对AI返回的镜头语言、文案、音效等内容分层级处理",
    "3. 时间单位统一转换为秒数",
    "4. 转场效果等需标注为独立字段",
    "5. 最终输出不带解释性文字"
  ],
  "example_input": "开场（3-5秒）\n镜头：延时摄影未名湖晨曦\n文案：这里是北京大学...\n音效：鸟鸣声",
  "example_output": "{\n  \"opening\": {\n    \"duration\": 4,\n    \"shots\": [{\n      \"type\": \"time-lapse\",\n      \"subject\": \"未名湖晨曦\",\n      \"transition\": \"push-in\"\n    }],\n    \"caption\": \"这里是北京大学...\",\n    \"sound\": \"birds_chirping.mp3\"\n  }\n}"
}

返回的内容可能是：

```json
{
  "title": "在北大，听见理想发芽的声音",
  "description": "中国最高学府",
  "duration": 60,
  "content": [
    {
      "part": "开场",
      "duration": 4,
      "shots": [
        {
          "type": "time-lapse",
          "description": "晨曦中的未名湖泛起涟漪 → 镜头缓缓推进，出现人物背影走向博雅塔"
        }
      ],
      "caption": "这里是北京大学，此刻我在未名湖边，带你看见一座校园如何承载一代人的理想与星光。"
    },
    {
      "part": "过渡镜头",
      "duration": 2,
      "shots": [
        {
          "type": "close-up",
          "description": "手指滑过一页泛黄的课本 → 转场至图书馆内景"
        }
      ],
      "soundEffects": [
        "鸟鸣",
        "翻书声",
        "远处教学楼的钟声隐隐传来"
      ]
    },
    {
      "part": "正文段落",
      "structure": "3+1",
      "duration": 47.5
    }
  ]
}
```

## 视频生成 api

### 创建任务

请求示例

```shell
curl --location 'https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis' \
    -H 'X-DashScope-Async: enable' \
    -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
    -H 'Content-Type: application/json' \
    -d '{
    "model": "wanx2.1-t2v-turbo",
    "input": {
        "prompt": "一只小猫在月光下奔跑"
    },
    "parameters": {
        "size": "1280*720"
    }
}'
```

响应示例：

正常

```json
{
    "output": {
        "task_status": "PENDING",
        "task_id": "0385dc79-5ff8-4d82-bcb6-xxxxxx"
    },
    "request_id": "4909100c-7b5a-9f92-bfe5-xxxxxx"
}
```

异常：

```json
{
    "code":"InvalidApiKey",
    "message":"Invalid API-key provided.",
    "request_id":"fb53c4ec-1c12-4fc4-a580-xxxxxx"
}
```

### 根据任务ID查询结果

```shell
curl -X GET \
--header "Authorization: Bearer $DASHSCOPE_API_KEY" \
https://dashscope.aliyuncs.com/api/v1/tasks/86ecf553-d340-4e21-xxxxxxxxx
```

响应示例：

成功示例：

```json
{
    "request_id": "851985d0-fbba-9d8d-a17a-xxxxxx",
    "output": {
        "task_id": "208e2fd1-fcb4-4adf-9fcc-xxxxxx",
        "task_status": "SUCCEEDED",
        "submit_time": "2025-01-08 16:43:27.877",
        "scheduled_time": "2025-01-08 16:43:27.908",
        "end_time": "2025-01-08 16:46:35.304",
        "video_url": "https://dashscope-result-wlcb.oss-cn-wulanchabu.aliyuncs.comc/aa.mp4"
    },
    "usage": {
        "video_count": 1
    }
}
```

失败示例：

```json
{
    "request_id": "e5d70b02-ebd3-98ce-9fe8-759d7d7b107d",
    "output": {
        "task_id": "86ecf553-d340-4e21-af6e-a0c6a421c010",
        "task_status": "FAILED",
        "code": "InvalidParameter",
        "message": "The size is not match xxxxxx"
    }
}
```

### 限制

任务下发接口QPS限制2次/秒

### 视频生成模型

模型名称：wanx2.1-t2v-turbo

## 视频存储

试用华为云的obs,可参考现有代码。

```python
    # 初始化 OBS 客户端
            obs_client = ObsClient(
                access_key_id=current_app.config['OBS_ACCESS_KEY'],
                secret_access_key=current_app.config['OBS_SECRET_KEY'],
                server=current_app.config['OBS_ENDPOINT']
            )
            
            # 生成 OBS 对象键，使用安全的文件名
            obs_object_key = f"advertisting_intelligence_chain/{user_id}/{safe_filename}"
            
            # 直接将文件内容上传到 OBS
            obs_response = obs_client.putObject(
                bucketName=current_app.config['OBS_BUCKET'],
                objectKey=obs_object_key,
                content=file.stream.read()  # 直接读取文件内容
            )
            
            if obs_response.status >= 300:
                logger.error(f"OBS upload failed: {obs_response.errorMessage}")
                return error_response('OBS 上传失败')
            
            # 生成可下载的 OBS 文件的预览地址
            signed_url = obs_client.createSignedUrl(
                'GET',
                current_app.config['OBS_BUCKET'],
                obs_object_key,
                expires=3600
            )
            obs_preview_url = signed_url['signedUrl']
```

## 异步任务

使用 APScheduler 等库在 Flask 应用内或单独进程中运行定时任务来轮询状态。
流程: Flask 直接调用“创建任务”API -> 存储 task_id -> 后台调度器定时查询数据库中“处理中”的任务 -> 调用“查询结果”API -> 更新数据库。

前端轮询接口 就是调用api 查询结果。
api 查询接口 先查 数据库。
数据库如果是处理中再查 阿里的api 查询结果。

## api

### 创建视频生成任务
# @name createVideoTask
# 注意：message_id 必须是 type='assistant' 的消息ID
POST {{baseUrl}}/api/video/messages/{{messageId}}/tasks/0

### 获取视频任务状态
GET {{baseUrl}}/api/video/tasks/{{taskId}}
Authorization: Bearer {{access_token}}

### 获取视频任务列表
GET {{baseUrl}}/api/video/tasks
?page=1
&size=10
Authorization: Bearer {{access_token}}

### 获取消息关联的视频任务列表
# @name messageVideoTasks
GET {{baseUrl}}/api/video/messages/tasks
?message_ids=688,689,690
Authorization: Bearer {{access_token}}


## frontend
### 需要解析 video_parsed 事件
video_parsed 事件会把视频脚本 转成 json.
格式如下：
```json
{
  "title": "在北大，听见理想发芽的声音",
  "description": "中国最高学府",
  "duration": 60,
  "content": [
    {
      "part": "开场",
      "duration": 4,
      "shots": [
        {
          "type": "time-lapse",
          "description": "晨曦中的未名湖泛起涟漪 → 镜头缓缓推进，出现人物背影走向博雅塔"
        }
      ],
      "caption": "这里是北京大学，此刻我在未名湖边，带你看见一座校园如何承载一代人的理想与星光。"
    },
    {
      "part": "过渡镜头",
      "duration": 2,
      "shots": [
        {
          "type": "close-up",
          "description": "手指滑过一页泛黄的课本 → 转场至图书馆内景"
        }
      ],
      "soundEffects": [
        "鸟鸣",
        "翻书声",
        "远处教学楼的钟声隐隐传来"
      ]
    },
    {
      "part": "正文段落",
      "structure": "3+1",
      "duration": 47.5
    }
  ]
}
```

 允许用户编辑 description。

 确认后 调用创建视频生成任务 接口。
 然后轮询 调用 获取视频任务状态 接口。 直到获取到视频链接。
 展示给用户。可以播放视频。用户可以下载视频。可以二次编辑脚本，重新生成视频。

 重新生成视频也是调用 创建视频生成任务, taskId 就不是 0 了。而是当前视频的taskId

 
 