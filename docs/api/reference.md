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
  - 失败: 显示错误信息并重定向至登录页

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
  - 成功:
  ```json
  {
    "message": "留言撤销成功"
  }
  ```
  - 失败:
    ```json
    {
      "error": "无效的撤销密钥或留言已被撤销"
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
    "response": "RESET"  // 或 "CONTINUE"
  }
  ```
- **响应**:
  - 成功:
  ```json
  {
    "message": "预警响应处理成功"
  }
  ```
  - 失败:
    ```json
    {
      "error": "留言已失效"  // 或其他错误信息
    }
    ```

## 管理接口

### 管理后台

- **URL**: `/admin`
- **方法**: GET
- **描述**: 访问管理后台
- **权限**: 需要登录且用户名为配置的管理员用户名
- **响应**:
  - 成功: 返回管理页面，包含以下统计数据:
    - 用户总数
    - 留言总数
    - 活跃留言数
    - 各级别预警的留言数量
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
   - 用于普通用户登录和页面访问
   - 登录后创建会话，存储在cookie中
   - 适用于浏览器环境

2. **JWT认证**: 用于API接口访问
   - 用于API接口认证
   - 需在请求头中携带JWT令牌
   - 适用于前后端分离或移动应用

API接口调用示例:

```javascript
// 创建留言
fetch('/api/message', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  },
  body: JSON.stringify({
    content: "这是一条测试留言",
    initial_delay_months: 3,
    recipients: [
      {
        name: "张三",
        contact: "zhangsan@example.com",
        contact_type: "email"
      }
    ]
  })
})
.then(response => response.json())
.then(data => console.log(data));

// 撤销留言
fetch('/api/message/revoke/YOUR_REVOCATION_KEY', {
  method: 'POST'
})
.then(response => response.json())
.then(data => console.log(data));

// 处理预警响应
fetch('/api/message/123/warning/response', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  },
  body: JSON.stringify({
    response: "RESET"  // 或 "CONTINUE"
  })
})
.then(response => response.json())
.then(data => console.log(data));
``` 