
# 文生图功能说明

在广告海报创意总监这块增加生图功能，图也可以转视频。

## 代码说明
需要参考当前代码的实现：
譬如后端用的python flask, 代码在backend目录
前端用的vue。 代码在frontend目录

## 后端接口说明

### 生成新图片

POST /api/mj/generate

请求头：
- Content-Type: application/json
- Authorization: Bearer {access_token}

请求体：
```json
{
    "prompt": "一只可爱的猫咪在阳光下玩耍",
    "optUuid": "optional-uuid-123"  // 可选
}
```

响应：
```json
{
    "success": true,
    "message": "生图任务已创建",
    "data": {
        "userImagineId": 1234,
        // 其他返回字段...
    }
}
```

### 编辑图片

POST /api/mj/edit

用于执行放大、变体、重新生成等操作。

请求头：
- Content-Type: application/json
- Authorization: Bearer {access_token}

请求体：
```json
{
    "action": "upsample MJ::JOB::upsample::1::31a4e28f-2cf4-4202-bbf1-4024e8cb7f7a",
    "imageId": "image-id-123",
    "optUuid": "optional-uuid-123"  // 可选
}
```

响应：
```json
{
    "success": true,
    "message": "图片编辑任务已创建",
    "data": {
        // 任务相关信息
    }
}
```

### 查询生图进度

POST /api/mj/progress

请求头：
- Content-Type: application/json
- Authorization: Bearer {access_token}

请求体：
```json
{
    "userImagineId": 1234
}
```

响应：
```json
{
    "success": true,
    "message": "查询成功",
    "data": {
        "result": {
            "imageId": "image-id-123",
            "status": "COMPLETED",
            "imageUrl": "https://example.com/image.jpg",
            "actionsJson": [
                // 可用的操作列表
            ]
        }
    }
}
```

### 取消生图任务

POST /api/mj/cancel

请求头：
- Content-Type: application/json
- Authorization: Bearer {access_token}

请求体：
```json
{
    "userImagineId": 1234
}
```

响应：
```json
{
    "success": true,
    "message": "任务已取消",
    "data": {
        // 取消结果信息
    }
}
```

## 错误响应
所有接口在发生错误时会返回统一格式：
```json
{
    "success": false,
    "message": "错误信息",
    "code": 500  // 错误码
}
```

常见错误码：
- 400: 请求参数错误
- 401: 未授权
- 500: 服务器内部错误


## 前端交互说明
在广告海报创意总监这块增加生图功能，图也可以转视频。
首先这个特定的角色。
发送消息时：
如果角色id=28
那么就发起一个生成图片的task, imageid 需要存数据库。
此时用户有 1 个操作：
1. 取消，调用取消接口
在未取消的情况下， 轮询调用获取进度接口 直到获取结果 获取用户取消。

获取到了图片后，展示当前图片。
同时暂时当前图片可以允许的操作。 获取进度的接口有返回。参考 test.rest里的接口示例。

用户编辑图片 后 会生成新的图片生成任务。也有imageid, 也是可取消和轮询结果。

对于轮询进度的说明：
重点关注 taskStatus
SUCCESS： 生成成功，此时可获取 ossImageUrl 作为展示。同时遍历actionsJson 展示给用户编辑选项。
WAITING: 继续。轮询，这个状态可取消图片生成
taskStatus: FAIL 失败了。。显示errorShow
taskStatus: CANCEL 已经取消了。
IN_PROCESSING: 需要急需轮询。




## EQMJ项目 接口说明

Base URLs: https://api.example.com


### Authentication
接口鉴权方法为：
在header中传入Timestamp（时间戳）和Signature（签名）
Signature的算法为 md5（秘钥+Timestamp），详见下面Java代码。

实例请求：
```sh
curl --location --request POST 'http://127.0.0.1:9010/api/common/open/mj/imagine' \
--header 'Timestamp: 1737036080059' \
--header 'Signature: YOUR_SIGNATURE' \
--header 'Authorization: YOUR_MJ_API_KEY' \
--header 'Front-Version: 0.0.0' \
--header 'App-Key: YOUR_MJ_APP_KEY' \
--header 'User-Agent: Apifox/1.0.0 (https://apifox.com)' \
--header 'Content-Type: application/json' \
--header 'Accept: */*' \
--header 'Host: 127.0.0.1:9010' \
--header 'Connection: keep-alive' \
--data-raw '{
    "action": "generate",
    "promptCn": "一个美丽的小女孩"
}'

```
### 通用接口/MJ生图

<a id="opIdcancelUsingPOST_1"></a>

#### POST 取消生图

POST /api/common/open/mj/cancel

> Body 请求参数

```json
{
  "userImagineId": 0
}
```

#### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|Authorization|header|string| 否 ||none|
|Front-Version|header|string| 否 ||none|
|App-Key|header|string| 否 ||none|
|body|body|[CancelImagineQo](#schemacancelimagineqo)| 否 | CancelImagineQo|none|

> 返回示例

> 200 Response

```json
true
```

#### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|boolean|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|none|Inline|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|none|Inline|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|none|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|none|Inline|

#### 返回数据结构

<a id="opIdimagineUsingPOST"></a>

### POST 开始生图（调用MJ生图）

POST /api/common/open/mj/imagine

> Body 请求参数

```json
{
  "action": "string",
  "imageId": "string",
  "optUuid": "string",
  "promptCn": "string"
}
```

#### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|Authorization|header|string| 否 ||none|
|Front-Version|header|string| 否 ||none|
|App-Key|header|string| 否 ||none|
|body|body|[CreateImagineQo](#schemacreateimagineqo)| 否 | CreateImagineQo|none|

> 返回示例

> 200 Response

```json
{
  "action": "string",
  "actionsJson": [
    {}
  ],
  "apiCallAt": "2019-08-24T14:15:22Z",
  "apiEndAt": "2019-08-24T14:15:22Z",
  "apiOpt": "string",
  "apiRequestJson": {
    "property1": {},
    "property2": {}
  },
  "apiResponseJson": {
    "property1": {},
    "property2": {}
  },
  "apiResult": "SUCCESS",
  "apiSource": "DISCORD_LOGIC",
  "createdAt": "2019-08-24T14:15:22Z",
  "createdBy": 0,
  "errorOverview": "string",
  "errorShow": "string",
  "imageId": "string",
  "imageUrl": "string",
  "isSingleImage": false,
  "mjAccount": "string",
  "mjChannelId": 0,
  "note": "string",
  "optUuid": "string",
  "ossImageUrl": "string",
  "progress": 0,
  "prompt": "string",
  "promptCn": "string",
  "promptMd5": "string",
  "realCostTime": 0,
  "sort": 0,
  "speed": "RELAX",
  "status": "string",
  "taskCode": 0,
  "taskId": "string",
  "taskStatus": "WAITING",
  "traceId": "string",
  "user": {
    "address": "string",
    "area": "string",
    "avatar": "string",
    "birthday": "2019-08-24",
    "city": "string",
    "country": "string",
    "createdAt": "2019-08-24T14:15:22Z",
    "createdBy": 0,
    "email": "string",
    "gender": "FEMALE",
    "invitationCode": "string",
    "invitationUserId": 0,
    "language": "string",
    "maxSioptNum": 0,
    "nickName": "string",
    "note": "string",
    "phoneNumber": "string",
    "point": 0,
    "province": "string",
    "realName": "string",
    "showUserId": "string",
    "sign": "string",
    "sort": 0,
    "status": "string",
    "type": "PLATFORM",
    "useSecs": 0,
    "userId": 0,
    "userLevel": "TURBO_LEVEL",
    "uuid": "string",
    "version": 0
  },
  "userId": 0,
  "userImagineId": 0,
  "version": 0,
  "waitCount": 0
}
```

#### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|[BmsUserImagineVo](#schemabmsuserimaginevo)|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|none|Inline|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|none|Inline|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|none|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|none|Inline|

#### 返回数据结构

状态码 **200**

*BmsUserImagineVo*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» action|string|false|none||本次请求的action|
|» actionsJson|[object]|false|none||可以跟进的actions|
|» apiCallAt|string(date-time)|false|none||API请求的时间|
|» apiEndAt|string(date-time)|false|none||记录回调时间，这样可以统计一次请求的完整时间|
|» apiOpt|string|false|none||api的接口操作|
|» apiRequestJson|object|false|none||本次请求的request body，用于回溯请求|
|»» **additionalProperties**|object|false|none||none|
|» apiResponseJson|object|false|none||本次请求的response body，用于回溯请求|
|»» **additionalProperties**|object|false|none||none|
|» apiResult|string|false|none||api的调用结果，SUCCESS：成功；FAILED：失败|
|» apiSource|string|false|none||三方API的源，ZHI_SHU_YUN：知数云；API_CLOUDS：源通智云|
|» createdAt|string(date-time)|false|none||创建时间戳|
|» createdBy|integer(int32)|false|none||创建用户|
|» errorOverview|string|false|none||错误概述|
|» errorShow|string|false|none||错误展示，来自于字典值配置|
|» imageId|string|false|none||三方图片的id|
|» imageUrl|string|false|none||三方生成图片的URL，临时有效|
|» isSingleImage|boolean|false|none||是否为单张图|
|» mjAccount|string|false|none||MJ账号|
|» mjChannelId|integer(int32)|false|none||mjChannelId|
|» note|string|false|none||备注|
|» optUuid|string|false|none||一次操作的全局ID，例如一次生图操作会执行多次命令，那么共用一个全局ID|
|» ossImageUrl|string|false|none||当progress=100时，会将临时的image_url上传到对象存储上，形成oss_image_url|
|» progress|number|false|none||进度百分比|
|» prompt|string|false|none||本次请求的prompt文本|
|» promptCn|string|false|none||中文prompt|
|» promptMd5|string|false|none||prompt的md5加密值|
|» realCostTime|integer(int32)|false|none||真实花费时间|
|» sort|integer(int32)|false|none||排序|
|» speed|string|false|none||生图速度|
|» status|string|false|none||状态，是否生效，0：未生效；1：生效|
|» taskCode|integer(int32)|false|none||Discord的taskCode|
|» taskId|string|false|none||三方任务id|
|» taskStatus|string|false|none||任务状态|
|» traceId|string|false|none||跟踪id|
|» user|[SysUserBaseVo](#schemasysuserbasevo)|false|none|SysUserBaseVo|none|
|»» address|string|false|none||地址|
|»» area|string|false|none||区|
|»» avatar|string|false|none||头像图片|
|»» birthday|string(date)|false|none||生日|
|»» city|string|false|none||城市|
|»» country|string|false|none||国家|
|»» createdAt|string(date-time)|false|none||创建时间戳|
|»» createdBy|integer(int32)|false|none||创建用户|
|»» email|string|false|none||邮箱|
|»» gender|string|false|none||用户性别；UNKNOWN：保密；MALE：男性；FEMALE：女性；|
|»» invitationCode|string|false|none||邀请码|
|»» invitationUserId|integer(int32)|false|none||邀请人id|
|»» language|string|false|none||语言|
|»» maxSioptNum|integer(int32)|false|none||最大同时执行操作次数|
|»» nickName|string|false|none||昵称|
|»» note|string|false|none||备注|
|»» phoneNumber|string|false|none||手机号|
|»» point|integer(int32)|false|none||总分数|
|»» province|string|false|none||省份|
|»» realName|string|false|none||真实名称|
|»» showUserId|string|false|none||展示用用户ID，如果用户昵称不存在，则使用该ID|
|»» sign|string|false|none||用户签名|
|»» sort|integer(int32)|false|none||排序|
|»» status|string|false|none||状态，是否生效，0：未生效；1：生效|
|»» type|string|false|none||人员类别，平台方：PLATFORM，需求方：DEMANDER；供货方：SUPPLIER|
|»» useSecs|integer(int32)|false|none||使用时长（秒）|
|»» userId|integer(int32)|false|none||PK|
|»» userLevel|string|false|none||用户级别|
|»» uuid|string|false|none||预留id，一般为hash值|
|»» version|integer(int32)|false|none||版本号|
|» userId|integer(int32)|false|none||用户id|
|» userImagineId|integer(int32)|false|none||PK|
|» version|integer(int32)|false|none||版本号|
|» waitCount|integer(int32)|false|none||当前排队数，2024-05-19新增需求，当排队中时会有这个参数，如果为排队中状态，则该参数如果为0，则也展示为1|

##### 枚举值

|属性|值|
|---|---|
|apiResult|SUCCESS|
|apiResult|FAILED|
|apiSource|DISCORD_LOGIC|
|apiSource|ZHI_SHU_YUN|
|apiSource|API_CLOUDS|
|speed|RELAX|
|speed|FAST|
|speed|TURBO|
|taskStatus|WAITING|
|taskStatus|IN_PROCESSING|
|taskStatus|SUCCESS|
|taskStatus|FAIL|
|taskStatus|CANCEL|
|gender|FEMALE|
|gender|MALE|
|gender|UNKNOWN|
|type|PLATFORM|
|type|USER|
|userLevel|TURBO_LEVEL|
|userLevel|NORMAL_LEVEL|

<a id="opIdprogressUsingPOST"></a>

### POST 查询生图进度

POST /api/common/open/mj/progress

> Body 请求参数

```json
{
  "userImagineId": 0
}
```

#### 请求参数

|名称|位置|类型|必选|中文名|说明|
|---|---|---|---|---|---|
|Authorization|header|string| 否 ||none|
|Front-Version|header|string| 否 ||none|
|App-Key|header|string| 否 ||none|
|body|body|[ImagineProgressQo](#schemaimagineprogressqo)| 否 | ImagineProgressQo|none|

> 返回示例

> 200 Response

```json
{
  "action": "string",
  "actionsJson": [
    {}
  ],
  "apiCallAt": "2019-08-24T14:15:22Z",
  "apiEndAt": "2019-08-24T14:15:22Z",
  "apiOpt": "string",
  "apiRequestJson": {
    "property1": {},
    "property2": {}
  },
  "apiResponseJson": {
    "property1": {},
    "property2": {}
  },
  "apiResult": "SUCCESS",
  "apiSource": "DISCORD_LOGIC",
  "createdAt": "2019-08-24T14:15:22Z",
  "createdBy": 0,
  "errorOverview": "string",
  "errorShow": "string",
  "imageId": "string",
  "imageUrl": "string",
  "isSingleImage": false,
  "mjAccount": "string",
  "mjChannelId": 0,
  "note": "string",
  "optUuid": "string",
  "ossImageUrl": "string",
  "progress": 0,
  "prompt": "string",
  "promptCn": "string",
  "promptMd5": "string",
  "realCostTime": 0,
  "sort": 0,
  "speed": "RELAX",
  "status": "string",
  "taskCode": 0,
  "taskId": "string",
  "taskStatus": "WAITING",
  "traceId": "string",
  "user": {
    "address": "string",
    "area": "string",
    "avatar": "string",
    "birthday": "2019-08-24",
    "city": "string",
    "country": "string",
    "createdAt": "2019-08-24T14:15:22Z",
    "createdBy": 0,
    "email": "string",
    "gender": "FEMALE",
    "invitationCode": "string",
    "invitationUserId": 0,
    "language": "string",
    "maxSioptNum": 0,
    "nickName": "string",
    "note": "string",
    "phoneNumber": "string",
    "point": 0,
    "province": "string",
    "realName": "string",
    "showUserId": "string",
    "sign": "string",
    "sort": 0,
    "status": "string",
    "type": "PLATFORM",
    "useSecs": 0,
    "userId": 0,
    "userLevel": "TURBO_LEVEL",
    "uuid": "string",
    "version": 0
  },
  "userId": 0,
  "userImagineId": 0,
  "version": 0,
  "waitCount": 0
}
```

#### 返回结果

|状态码|状态码含义|说明|数据模型|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|none|[BmsUserImagineVo](#schemabmsuserimaginevo)|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|none|Inline|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|none|Inline|
|403|[Forbidden](https://tools.ietf.org/html/rfc7231#section-6.5.3)|none|Inline|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|none|Inline|

#### 返回数据结构

状态码 **200**

*BmsUserImagineVo*

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|» action|string|false|none||本次请求的action|
|» actionsJson|[object]|false|none||可以跟进的actions|
|» apiCallAt|string(date-time)|false|none||API请求的时间|
|» apiEndAt|string(date-time)|false|none||记录回调时间，这样可以统计一次请求的完整时间|
|» apiOpt|string|false|none||api的接口操作|
|» apiRequestJson|object|false|none||本次请求的request body，用于回溯请求|
|»» **additionalProperties**|object|false|none||none|
|» apiResponseJson|object|false|none||本次请求的response body，用于回溯请求|
|»» **additionalProperties**|object|false|none||none|
|» apiResult|string|false|none||api的调用结果，SUCCESS：成功；FAILED：失败|
|» apiSource|string|false|none||三方API的源，ZHI_SHU_YUN：知数云；API_CLOUDS：源通智云|
|» createdAt|string(date-time)|false|none||创建时间戳|
|» createdBy|integer(int32)|false|none||创建用户|
|» errorOverview|string|false|none||错误概述|
|» errorShow|string|false|none||错误展示，来自于字典值配置|
|» imageId|string|false|none||三方图片的id|
|» imageUrl|string|false|none||三方生成图片的URL，临时有效|
|» isSingleImage|boolean|false|none||是否为单张图|
|» mjAccount|string|false|none||MJ账号|
|» mjChannelId|integer(int32)|false|none||mjChannelId|
|» note|string|false|none||备注|
|» optUuid|string|false|none||一次操作的全局ID，例如一次生图操作会执行多次命令，那么共用一个全局ID|
|» ossImageUrl|string|false|none||当progress=100时，会将临时的image_url上传到对象存储上，形成oss_image_url|
|» progress|number|false|none||进度百分比|
|» prompt|string|false|none||本次请求的prompt文本|
|» promptCn|string|false|none||中文prompt|
|» promptMd5|string|false|none||prompt的md5加密值|
|» realCostTime|integer(int32)|false|none||真实花费时间|
|» sort|integer(int32)|false|none||排序|
|» speed|string|false|none||生图速度|
|» status|string|false|none||状态，是否生效，0：未生效；1：生效|
|» taskCode|integer(int32)|false|none||Discord的taskCode|
|» taskId|string|false|none||三方任务id|
|» taskStatus|string|false|none||任务状态|
|» traceId|string|false|none||跟踪id|
|» user|[SysUserBaseVo](#schemasysuserbasevo)|false|none|SysUserBaseVo|none|
|»» address|string|false|none||地址|
|»» area|string|false|none||区|
|»» avatar|string|false|none||头像图片|
|»» birthday|string(date)|false|none||生日|
|»» city|string|false|none||城市|
|»» country|string|false|none||国家|
|»» createdAt|string(date-time)|false|none||创建时间戳|
|»» createdBy|integer(int32)|false|none||创建用户|
|»» email|string|false|none||邮箱|
|»» gender|string|false|none||用户性别；UNKNOWN：保密；MALE：男性；FEMALE：女性；|
|»» invitationCode|string|false|none||邀请码|
|»» invitationUserId|integer(int32)|false|none||邀请人id|
|»» language|string|false|none||语言|
|»» maxSioptNum|integer(int32)|false|none||最大同时执行操作次数|
|»» nickName|string|false|none||昵称|
|»» note|string|false|none||备注|
|»» phoneNumber|string|false|none||手机号|
|»» point|integer(int32)|false|none||总分数|
|»» province|string|false|none||省份|
|»» realName|string|false|none||真实名称|
|»» showUserId|string|false|none||展示用用户ID，如果用户昵称不存在，则使用该ID|
|»» sign|string|false|none||用户签名|
|»» sort|integer(int32)|false|none||排序|
|»» status|string|false|none||状态，是否生效，0：未生效；1：生效|
|»» type|string|false|none||人员类别，平台方：PLATFORM，需求方：DEMANDER；供货方：SUPPLIER|
|»» useSecs|integer(int32)|false|none||使用时长（秒）|
|»» userId|integer(int32)|false|none||PK|
|»» userLevel|string|false|none||用户级别|
|»» uuid|string|false|none||预留id，一般为hash值|
|»» version|integer(int32)|false|none||版本号|
|» userId|integer(int32)|false|none||用户id|
|» userImagineId|integer(int32)|false|none||PK|
|» version|integer(int32)|false|none||版本号|
|» waitCount|integer(int32)|false|none||当前排队数，2024-05-19新增需求，当排队中时会有这个参数，如果为排队中状态，则该参数如果为0，则也展示为1|

##### 枚举值

|属性|值|
|---|---|
|apiResult|SUCCESS|
|apiResult|FAILED|
|apiSource|DISCORD_LOGIC|
|apiSource|ZHI_SHU_YUN|
|apiSource|API_CLOUDS|
|speed|RELAX|
|speed|FAST|
|speed|TURBO|
|taskStatus|WAITING|
|taskStatus|IN_PROCESSING|
|taskStatus|SUCCESS|
|taskStatus|FAIL|
|taskStatus|CANCEL|
|gender|FEMALE|
|gender|MALE|
|gender|UNKNOWN|
|type|PLATFORM|
|type|USER|
|userLevel|TURBO_LEVEL|
|userLevel|NORMAL_LEVEL|

## 数据模型

<h2 id="tocS_BmsUserImagineVo">BmsUserImagineVo</h2>

<a id="schemabmsuserimaginevo"></a>
<a id="schema_BmsUserImagineVo"></a>
<a id="tocSbmsuserimaginevo"></a>
<a id="tocsbmsuserimaginevo"></a>

```json
{
  "action": "string",
  "actionsJson": [
    {}
  ],
  "apiCallAt": "2019-08-24T14:15:22Z",
  "apiEndAt": "2019-08-24T14:15:22Z",
  "apiOpt": "string",
  "apiRequestJson": {
    "property1": {},
    "property2": {}
  },
  "apiResponseJson": {
    "property1": {},
    "property2": {}
  },
  "apiResult": "SUCCESS",
  "apiSource": "DISCORD_LOGIC",
  "createdAt": "2019-08-24T14:15:22Z",
  "createdBy": 0,
  "errorOverview": "string",
  "errorShow": "string",
  "imageId": "string",
  "imageUrl": "string",
  "isSingleImage": false,
  "mjAccount": "string",
  "mjChannelId": 0,
  "note": "string",
  "optUuid": "string",
  "ossImageUrl": "string",
  "progress": 0,
  "prompt": "string",
  "promptCn": "string",
  "promptMd5": "string",
  "realCostTime": 0,
  "sort": 0,
  "speed": "RELAX",
  "status": "string",
  "taskCode": 0,
  "taskId": "string",
  "taskStatus": "WAITING",
  "traceId": "string",
  "user": {
    "address": "string",
    "area": "string",
    "avatar": "string",
    "birthday": "2019-08-24",
    "city": "string",
    "country": "string",
    "createdAt": "2019-08-24T14:15:22Z",
    "createdBy": 0,
    "email": "string",
    "gender": "FEMALE",
    "invitationCode": "string",
    "invitationUserId": 0,
    "language": "string",
    "maxSioptNum": 0,
    "nickName": "string",
    "note": "string",
    "phoneNumber": "string",
    "point": 0,
    "province": "string",
    "realName": "string",
    "showUserId": "string",
    "sign": "string",
    "sort": 0,
    "status": "string",
    "type": "PLATFORM",
    "useSecs": 0,
    "userId": 0,
    "userLevel": "TURBO_LEVEL",
    "uuid": "string",
    "version": 0
  },
  "userId": 0,
  "userImagineId": 0,
  "version": 0,
  "waitCount": 0
}

```

BmsUserImagineVo

#### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|action|string|false|none||本次请求的action|
|actionsJson|[object]|false|none||可以跟进的actions|
|apiCallAt|string(date-time)|false|none||API请求的时间|
|apiEndAt|string(date-time)|false|none||记录回调时间，这样可以统计一次请求的完整时间|
|apiOpt|string|false|none||api的接口操作|
|apiRequestJson|object|false|none||本次请求的request body，用于回溯请求|
|» **additionalProperties**|object|false|none||none|
|apiResponseJson|object|false|none||本次请求的response body，用于回溯请求|
|» **additionalProperties**|object|false|none||none|
|apiResult|string|false|none||api的调用结果，SUCCESS：成功；FAILED：失败|
|apiSource|string|false|none||三方API的源，ZHI_SHU_YUN：知数云；API_CLOUDS：源通智云|
|createdAt|string(date-time)|false|none||创建时间戳|
|createdBy|integer(int32)|false|none||创建用户|
|errorOverview|string|false|none||错误概述|
|errorShow|string|false|none||错误展示，来自于字典值配置|
|imageId|string|false|none||三方图片的id|
|imageUrl|string|false|none||三方生成图片的URL，临时有效|
|isSingleImage|boolean|false|none||是否为单张图|
|mjAccount|string|false|none||MJ账号|
|mjChannelId|integer(int32)|false|none||mjChannelId|
|note|string|false|none||备注|
|optUuid|string|false|none||一次操作的全局ID，例如一次生图操作会执行多次命令，那么共用一个全局ID|
|ossImageUrl|string|false|none||当progress=100时，会将临时的image_url上传到对象存储上，形成oss_image_url|
|progress|number|false|none||进度百分比|
|prompt|string|false|none||本次请求的prompt文本|
|promptCn|string|false|none||中文prompt|
|promptMd5|string|false|none||prompt的md5加密值|
|realCostTime|integer(int32)|false|none||真实花费时间|
|sort|integer(int32)|false|none||排序|
|speed|string|false|none||生图速度|
|status|string|false|none||状态，是否生效，0：未生效；1：生效|
|taskCode|integer(int32)|false|none||Discord的taskCode|
|taskId|string|false|none||三方任务id|
|taskStatus|string|false|none||任务状态|
|traceId|string|false|none||跟踪id|
|user|[SysUserBaseVo](#schemasysuserbasevo)|false|none||none|
|userId|integer(int32)|false|none||用户id|
|userImagineId|integer(int32)|false|none||PK|
|version|integer(int32)|false|none||版本号|
|waitCount|integer(int32)|false|none||当前排队数，2024-05-19新增需求，当排队中时会有这个参数，如果为排队中状态，则该参数如果为0，则也展示为1|

##### 枚举值

|属性|值|
|---|---|
|apiResult|SUCCESS|
|apiResult|FAILED|
|apiSource|DISCORD_LOGIC|
|apiSource|ZHI_SHU_YUN|
|apiSource|API_CLOUDS|
|speed|RELAX|
|speed|FAST|
|speed|TURBO|
|taskStatus|WAITING|
|taskStatus|IN_PROCESSING|
|taskStatus|SUCCESS|
|taskStatus|FAIL|
|taskStatus|CANCEL|

<h2 id="tocS_SysUserBaseVo">SysUserBaseVo</h2>

<a id="schemasysuserbasevo"></a>
<a id="schema_SysUserBaseVo"></a>
<a id="tocSsysuserbasevo"></a>
<a id="tocssysuserbasevo"></a>

```json
{
  "address": "string",
  "area": "string",
  "avatar": "string",
  "birthday": "2019-08-24",
  "city": "string",
  "country": "string",
  "createdAt": "2019-08-24T14:15:22Z",
  "createdBy": 0,
  "email": "string",
  "gender": "FEMALE",
  "invitationCode": "string",
  "invitationUserId": 0,
  "language": "string",
  "maxSioptNum": 0,
  "nickName": "string",
  "note": "string",
  "phoneNumber": "string",
  "point": 0,
  "province": "string",
  "realName": "string",
  "showUserId": "string",
  "sign": "string",
  "sort": 0,
  "status": "string",
  "type": "PLATFORM",
  "useSecs": 0,
  "userId": 0,
  "userLevel": "TURBO_LEVEL",
  "uuid": "string",
  "version": 0
}

```

SysUserBaseVo

#### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|address|string|false|none||地址|
|area|string|false|none||区|
|avatar|string|false|none||头像图片|
|birthday|string(date)|false|none||生日|
|city|string|false|none||城市|
|country|string|false|none||国家|
|createdAt|string(date-time)|false|none||创建时间戳|
|createdBy|integer(int32)|false|none||创建用户|
|email|string|false|none||邮箱|
|gender|string|false|none||用户性别；UNKNOWN：保密；MALE：男性；FEMALE：女性；|
|invitationCode|string|false|none||邀请码|
|invitationUserId|integer(int32)|false|none||邀请人id|
|language|string|false|none||语言|
|maxSioptNum|integer(int32)|false|none||最大同时执行操作次数|
|nickName|string|false|none||昵称|
|note|string|false|none||备注|
|phoneNumber|string|false|none||手机号|
|point|integer(int32)|false|none||总分数|
|province|string|false|none||省份|
|realName|string|false|none||真实名称|
|showUserId|string|false|none||展示用用户ID，如果用户昵称不存在，则使用该ID|
|sign|string|false|none||用户签名|
|sort|integer(int32)|false|none||排序|
|status|string|false|none||状态，是否生效，0：未生效；1：生效|
|type|string|false|none||人员类别，平台方：PLATFORM，需求方：DEMANDER；供货方：SUPPLIER|
|useSecs|integer(int32)|false|none||使用时长（秒）|
|userId|integer(int32)|false|none||PK|
|userLevel|string|false|none||用户级别|
|uuid|string|false|none||预留id，一般为hash值|
|version|integer(int32)|false|none||版本号|

##### 枚举值

|属性|值|
|---|---|
|gender|FEMALE|
|gender|MALE|
|gender|UNKNOWN|
|type|PLATFORM|
|type|USER|
|userLevel|TURBO_LEVEL|
|userLevel|NORMAL_LEVEL|

<h2 id="tocS_CancelImagineQo">CancelImagineQo</h2>

<a id="schemacancelimagineqo"></a>
<a id="schema_CancelImagineQo"></a>
<a id="tocScancelimagineqo"></a>
<a id="tocscancelimagineqo"></a>

```json
{
  "userImagineId": 0
}

```

CancelImagineQo

#### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|userImagineId|integer(int32)|true|none||用户生图id|

<h2 id="tocS_CreateImagineQo">CreateImagineQo</h2>

<a id="schemacreateimagineqo"></a>
<a id="schema_CreateImagineQo"></a>
<a id="tocScreateimagineqo"></a>
<a id="tocscreateimagineqo"></a>

```json
{
  "action": "string",
  "imageId": "string",
  "optUuid": "string",
  "promptCn": "string"
}

```

CreateImagineQo

#### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|action|string|true|none||首次生图，为generate。在后续需要对图像进行处理时，可以设置为第一次生成结果的返回值中的 actions 的任一值，代表待处理图像的操作类型。该值默认为 generate|
|imageId|string|false|none||图像 ID。在第一次生成预览图时，不需要指定该字段。在后续需要对图像进行处理时，需要指定该字段，代表待处理图像的 ID。该 ID 即为第一次生成预览图时返回的 image_id 字段|
|optUuid|string|false|none||操作的uuid，统一全局的uuid，如果传入的uuid是一个，代表是对某个图片的一次性操作|
|promptCn|string|false|none||图像描述。在第一次生成预览图时，需要指定该字段，代表待生成图像的描述。系统会自动将中文翻译为英文|

<h2 id="tocS_ImagineProgressQo">ImagineProgressQo</h2>

<a id="schemaimagineprogressqo"></a>
<a id="schema_ImagineProgressQo"></a>
<a id="tocSimagineprogressqo"></a>
<a id="tocsimagineprogressqo"></a>

```json
{
  "userImagineId": 0
}

```

ImagineProgressQo

#### 属性

|名称|类型|必选|约束|中文名|说明|
|---|---|---|---|---|---|
|userImagineId|integer(int32)|true|none||用户生图id|

