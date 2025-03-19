# API接口文档

## API概述

### 基础信息

- 基础URL: `https://api.example.com/v1`
- 认证方式: Bearer Token
- 响应格式: JSON
- 编码方式: UTF-8

### 通用响应格式

```json
{
    "code": 200,
    "message": "success",
    "data": {
        // 响应数据
    }
}
```

### 错误码说明

| 错误码 | 说明           |
| ------ | -------------- |
| 200    | 成功           |
| 400    | 请求参数错误   |
| 401    | 未授权         |
| 403    | 禁止访问       |
| 404    | 资源不存在     |
| 500    | 服务器内部错误 |

## 认证相关接口

### 1. 用户注册

- **请求路径**: `/auth/register`
- **请求方法**: POST
- **请求参数**:

```json
{
    "username": "string",
    "password": "string",
    "email": "string",
    "phone": "string"
}
```

- **响应示例**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "user_id": 1,
        "username": "string",
        "email": "string"
    }
}
```

### 2. 用户登录

- **请求路径**: `/auth/login`
- **请求方法**: POST
- **请求参数**:

```json
{
    "username": "string",
    "password": "string"
}
```

- **响应示例**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "token": "string",
        "user": {
            "id": 1,
            "username": "string",
            "email": "string"
        }
    }
}
```

## 留言相关接口

### 1. 创建留言

- **请求路径**: `/messages`
- **请求方法**: POST
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**:

```json
{
    "title": "string",
    "content": "string",
    "priority": "low|medium|high",
    "scheduled_at": "datetime",
    "recipients": [
        {
            "name": "string",
            "contact_type": "email|phone|wechat",
            "contact_value": "string"
        }
    ],
    "media_files": [
        {
            "file_name": "string",
            "file_type": "string",
            "file_size": "number"
        }
    ]
}
```

- **响应示例**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "message_id": 1,
        "status": "draft"
    }
}
```

### 2. 获取留言列表

- **请求路径**: `/messages`
- **请求方法**: GET
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**:
  - page: 页码
  - size: 每页数量
  - status: 状态筛选
  - start_date: 开始日期
  - end_date: 结束日期
- **响应示例**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 100,
        "items": [
            {
                "id": 1,
                "title": "string",
                "content": "string",
                "status": "string",
                "created_at": "datetime"
            }
        ]
    }
}
```

### 3. 获取留言详情

- **请求路径**: `/messages/{id}`
- **请求方法**: GET
- **请求头**:
  - Authorization: Bearer {token}
- **响应示例**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "title": "string",
        "content": "string",
        "status": "string",
        "recipients": [
            {
                "id": 1,
                "name": "string",
                "contact_type": "string",
                "status": "string"
            }
        ],
        "media_files": [
            {
                "id": 1,
                "file_name": "string",
                "file_type": "string"
            }
        ]
    }
}
```

## 接收人相关接口

### 1. 添加接收人

- **请求路径**: `/messages/{message_id}/recipients`
- **请求方法**: POST
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**:

```json
{
    "recipients": [
        {
            "name": "string",
            "contact_type": "email|phone|wechat",
            "contact_value": "string"
        }
    ]
}
```

- **响应示例**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "recipient_ids": [1, 2]
    }
}
```

### 2. 获取接收人列表

- **请求路径**: `/messages/{message_id}/recipients`
- **请求方法**: GET
- **请求头**:
  - Authorization: Bearer {token}
- **响应示例**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "recipients": [
            {
                "id": 1,
                "name": "string",
                "contact_type": "string",
                "status": "string"
            }
        ]
    }
}
```

## 状态确认相关接口

### 1. 确认状态

- **请求路径**: `/status/confirm`
- **请求方法**: POST
- **请求参数**:

```json
{
    "message_id": "number",
    "recipient_id": "number",
    "status": "confirmed|failed"
}
```

- **响应示例**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "check_id": 1,
        "status": "confirmed"
    }
}
```

### 2. 获取状态历史

- **请求路径**: `/status/history`
- **请求方法**: GET
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**:
  - message_id: 留言ID
  - recipient_id: 接收人ID
  - start_date: 开始日期
  - end_date: 结束日期
- **响应示例**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "history": [
            {
                "id": 1,
                "check_time": "datetime",
                "status": "string",
                "response_time": "datetime"
            }
        ]
    }
}
```

## 文件上传接口

### 1. 获取上传URL

- **请求路径**: `/upload/url`
- **请求方法**: POST
- **请求头**:
  - Authorization: Bearer {token}
- **请求参数**:

```json
{
    "file_name": "string",
    "file_type": "string"
}
```

- **响应示例**:

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "upload_url": "string",
        "f
```
