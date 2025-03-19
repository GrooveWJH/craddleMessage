# 摇篮留言服务系统技术文档

## 技术栈

- 后端框架：Flask
- 数据库：MariaDB
- 前端：HTML + CSS + JavaScript
- 加密：AES-256
- 认证：JWT
- 部署：腾讯云

## 系统架构

### 目录结构

```
code/
├── app.py              # 主应用入口
├── config/             # 配置文件目录
│   └── config.py       # 系统配置
├── static/             # 静态文件
│   ├── css/           # 样式文件
│   ├── js/            # JavaScript文件
│   └── img/           # 图片资源
├── templates/          # HTML模板
│   ├── index.html     # 主页
│   ├── admin.html     # 管理后台
│   └── login.html     # 登录页面
├── logs/              # 日志文件
├── scripts/           # 脚本文件
│   ├── init_db.py     # 数据库初始化
│   └── create_test_data.py  # 测试数据生成
└── requirements.txt   # 项目依赖
```

## 核心功能实现

### 1. 留言存储

- 使用 MariaDB 存储用户信息和留言内容
- 采用 AES-256 加密存储敏感信息
- 支持多种媒体格式的存储

### 2. 状态确认机制

- 基于时间间隔的状态检查
- 多级预警通知系统
- 状态重置机制

### 3. 发送机制

- 基于触发条件的自动发送
- 多渠道发送支持（邮件、短信等）
- 发送状态追踪

### 4. 安全机制

- JWT 用户认证
- 唯一长密码生成
- 数据加密存储

### 5. 日志系统

- 操作日志记录
- 系统状态监控
- 错误追踪

## 数据库设计

### 用户表 (users)

- id: 主键
- username: 用户名
- password: 密码（加密存储）
- email: 邮箱
- created_at: 创建时间

### 留言表 (messages)

- id: 主键
- user_id: 用户ID
- content: 留言内容
- media_type: 媒体类型
- created_at: 创建时间
- trigger_condition: 触发条件

### 接收人表 (recipients)

- id: 主键
- message_id: 留言ID
- name: 接收人姓名
- contact: 联系方式
- contact_type: 联系类型

### 状态记录表 (status_logs)

- id: 主键
- message_id: 留言ID
- status: 状态
- created_at: 记录时间
- details: 详细信息

## 配置说明

### 系统配置

- 数据库连接信息
- 加密密钥
- JWT 密钥
- 日志配置

### 发送配置

- 预警时间间隔
- 发送渠道配置
- 重试机制

## 部署说明

1. 环境要求

   - Python 3.8+
   - MariaDB 10.5+
   - 腾讯云服务器
2. 部署步骤

   - 安装依赖
   - 配置数据库
   - 初始化系统
   - 启动服务

## 维护说明

1. 日志管理

   - 定期检查日志文件
   - 清理过期日志
2. 数据库维护

   - 定期备份
   - 性能优化
3. 系统监控

   - 服务状态检查
   - 性能监控
   - 错误告警
