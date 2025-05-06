# API 接口参考

本文档提供摇篮留言服务系统的所有API接口详细说明。

## 认证接口

### 登录

- **URL**: `/login`
- **方法**: POST
- **描述**: 用户登录系统
- **参数**:
  - `username`: 用户名
  - `password`: 密码
- **响应**:
  - 成功: 重定向至主页
  - 失败: 显示错误信息

### 登出

- **URL**: `/logout`
- **方法**: GET
- **描述**: 用户登出系统
- **权限**: 需要登录
- **响应**:
  - 成功: 重定向至主页

## 留言管理接口

### 创建留言

- **URL**: `/api/message`
- **方法**: POST
- **描述**: 创建新的留言
- **权限**: 需要JWT认证
- **请求体**:
  ```json
  {
    "content": "留言内容",
    "initial_delay_months": 6,
    "recipients": [
      {
        "name": "接收人姓名",
        "contact": "联系方式",
        "contact_type": "email/phone/wechat"
      }
    ]
  }
  ```
- **响应**:
  ```json
  {
    "message": "留言创建成功",
    "revocation_key": "撤销密钥",
    "warning_schedule": {
      "first_warning": "2024-12-20T00:00:00Z",
      "second_warning": "2025-01-20T00:00:00Z",
      "third_warning": "2025-02-20T00:00:00Z",
      "fourth_warning": "2025-02-27T00:00:00Z",
      "final_warning": "2025-02-28T00:00:00Z",
      "final_delivery": "2025-03-01T00:00:00Z"
    }
  }
  ```

### 撤销留言

- **URL**: `/api/message/revoke/<revocation_key>`
- **方法**: POST
- **描述**: 使用撤销密钥撤销留言
- **权限**: 无需认证，任何拥有撤销密钥的人都可以撤销
- **参数**:
  - `revocation_key`: 撤销密钥（URL参数）
- **响应**:
  ```json
  {
    "message": "留言撤销成功"
  }
  ```

### 处理预警响应

- **URL**: `/api/message/<int:message_id>/warning/response`
- **方法**: POST
- **描述**: 处理用户对预警的响应
- **权限**: 需要JWT认证
- **参数**:
  - `message_id`: 留言ID（URL参数）
- **请求体**:
  ```json
  {
    "response": "RESET或CONTINUE"
  }
  ```
- **响应**:
  ```json
  {
    "message": "预警响应处理成功"
  }
  ```

## 管理接口

### 管理后台

- **URL**: `/admin`
- **方法**: GET
- **描述**: 访问管理后台
- **权限**: 需要登录且用户名为配置的管理员用户名
- **响应**:
  - 成功: 返回管理页面，包含系统统计数据
  - 失败: 重定向至主页

## 状态码说明

- **200**: 请求成功
- **201**: 资源创建成功
- **400**: 请求参数错误
- **401**: 未授权访问
- **404**: 资源不存在
- **500**: 服务器内部错误

## 错误响应格式

```json
{
  "error": "错误描述"
}
```

## 认证说明

系统使用两种认证方式:

1. **会话认证**: 基于Flask-Login实现，用于Web界面访问
2. **JWT认证**: 用于API接口访问，需在请求头中携带JWT令牌

获取JWT令牌的方式可通过标准的OAuth2流程或直接调用登录API。 