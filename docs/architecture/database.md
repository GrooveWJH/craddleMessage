# 数据库设计文档

## 数据库架构

本文档详细说明摇篮留言服务系统的数据库设计。系统使用关系型数据库MySQL作为数据存储，并通过SQLAlchemy ORM框架进行数据访问和管理。

## 数据模型概述

系统包含四个主要数据模型，它们通过外键关系相互关联：

1. **User**: 用户信息模型
2. **Message**: 留言信息模型
3. **Recipient**: 接收人信息模型
4. **StatusLog**: 状态日志模型

## 数据表结构

### User (用户表)

存储系统用户信息。

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 用户ID | 主键 |
| username | String(80) | 用户名 | 非空，唯一 |
| email | String(120) | 电子邮件 | 非空，唯一 |
| password | String(120) | 密码 | 非空 |
| created_at | DateTime | 创建时间 | 默认当前时间 |

**索引**:
- 主键索引: `id`
- 唯一索引: `username`, `email`

**关系**:
- 一对多关系到 `Message`: 一个用户可以创建多条留言

### Message (留言表)

存储留言内容和状态信息。

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 留言ID | 主键 |
| user_id | Integer | 关联的用户ID | 外键，非空 |
| content | Text | 留言内容 | 非空 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| initial_delay_months | Integer | 初始延迟月数 | 非空 |
| next_warning_date | DateTime | 下次预警日期 | 非空 |
| warning_level | Integer | 预警级别 | 默认0 |
| is_active | Boolean | 是否活跃 | 默认True |
| revocation_key | String(255) | 撤销密钥 | 唯一 |

**索引**:
- 主键索引: `id`
- 外键索引: `user_id` -> `User.id`
- 唯一索引: `revocation_key`

**关系**:
- 多对一关系到 `User`: 多条留言可以关联到一个用户
- 一对多关系到 `Recipient`: 一条留言可以有多个接收人
- 一对多关系到 `StatusLog`: 一条留言可以有多个状态日志

### Recipient (接收人表)

存储留言接收人信息。

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 接收人ID | 主键 |
| message_id | Integer | 关联的留言ID | 外键，非空 |
| name | String(100) | 接收人姓名 | 非空 |
| contact | String(100) | 联系方式 | 非空 |
| contact_type | String(20) | 联系类型 | 非空 |

**索引**:
- 主键索引: `id`
- 外键索引: `message_id` -> `Message.id`

**关系**:
- 多对一关系到 `Message`: 多个接收人可以关联到一条留言

### StatusLog (状态日志表)

记录留言状态变更历史。

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 日志ID | 主键 |
| message_id | Integer | 关联的留言ID | 外键，非空 |
| status | String(50) | 状态标识 | 非空 |
| created_at | DateTime | 创建时间 | 默认当前时间 |
| details | Text | 详细信息 | 可空 |
| response | String(20) | 用户响应 | 可空 |

**索引**:
- 主键索引: `id`
- 外键索引: `message_id` -> `Message.id`

**关系**:
- 多对一关系到 `Message`: 多个状态日志可以关联到一条留言

## 数据模型关系图

```
+-------+       +---------+       +------------+
| User  |1     *| Message |1     *| Recipient  |
+-------+       +---------+       +------------+
|       |------>|         |------>|            |
+-------+       +---------+       +------------+
                     |1
                     |
                     v*
               +------------+
               | StatusLog  |
               +------------+
               |            |
               +------------+
```

## 数据模型定义

以下是使用SQLAlchemy ORM定义的数据模型代码：

```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import base64

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='user', lazy=True)

    def get_id(self):
        return str(self.id)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    initial_delay_months = db.Column(db.Integer, nullable=False)
    next_warning_date = db.Column(db.DateTime, nullable=False)
    warning_level = db.Column(db.Integer, default=0)  # 0-5: 0=未开始, 1-4=预警级别, 5=最终预警
    is_active = db.Column(db.Boolean, default=True)
    revocation_key = db.Column(db.String(255), unique=True)
    recipients = db.relationship('Recipient', backref='message', lazy=True)
    status_logs = db.relationship('StatusLog', backref='message', lazy=True)

    def generate_revocation_key(self):
        key = Fernet.generate_key()
        self.revocation_key = base64.urlsafe_b64encode(key).decode('utf-8')
        return self.revocation_key

    def calculate_warning_schedule(self):
        """计算预警时间表"""
        base_date = self.created_at
        schedule = {
            'first_warning': base_date + timedelta(days=self.initial_delay_months * 30),
            'second_warning': base_date + timedelta(days=(self.initial_delay_months * 30) + 30),
            'third_warning': base_date + timedelta(days=(self.initial_delay_months * 30) + 60),
            'fourth_warning': base_date + timedelta(days=(self.initial_delay_months * 30) + 67),
            'final_warning': base_date + timedelta(days=(self.initial_delay_months * 30) + 68),
            'final_delivery': base_date + timedelta(days=(self.initial_delay_months * 30) + 69)
        }
        return schedule

    def reset_warning_cycle(self):
        """重置预警周期"""
        self.warning_level = 0
        self.next_warning_date = datetime.utcnow() + timedelta(days=self.initial_delay_months * 30)
        
    def advance_warning_level(self):
        """推进预警等级"""
        self.warning_level += 1
        if self.warning_level == 1:  # 第一次预警后等待1个月
            self.next_warning_date = datetime.utcnow() + timedelta(days=30)
        elif self.warning_level == 2:  # 第二次预警后等待1个月
            self.next_warning_date = datetime.utcnow() + timedelta(days=30)
        elif self.warning_level == 3:  # 第三次预警后等待1周
            self.next_warning_date = datetime.utcnow() + timedelta(days=7)
        elif self.warning_level == 4:  # 第四次预警后等待1天
            self.next_warning_date = datetime.utcnow() + timedelta(days=1)
        elif self.warning_level == 5:  # 最终预警，准备发送
            self.next_warning_date = datetime.utcnow() + timedelta(hours=24)

class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    contact_type = db.Column(db.String(20), nullable=False)

class StatusLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # WARNING_1, WARNING_2, WARNING_3, WARNING_4, WARNING_FINAL, DELIVERED, REVOKED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)
    response = db.Column(db.String(20), nullable=True)  # RESET, CONTINUE, null
```

## 数据库迁移

系统使用Flask-Migrate扩展来管理数据库模式变更：

1. 初始化迁移仓库:
```bash
flask db init
```

2. 生成迁移脚本:
```bash
flask db migrate -m "Initial migration"
```

3. 应用迁移:
```bash
flask db upgrade
```

## 预警状态说明

留言预警级别(warning_level)定义:
- 0: 初始状态，等待第一次预警
- 1: 第一级预警，初始延迟期结束后
- 2: 第二级预警，第一级预警30天后
- 3: 第三级预警，第二级预警30天后
- 4: 第四级预警，第三级预警7天后
- 5: 最终预警，第四级预警1天后，准备发送留言

状态日志(StatusLog)中的状态(status)定义:
- WARNING_1: 第一级预警
- WARNING_2: 第二级预警
- WARNING_3: 第三级预警
- WARNING_4: 第四级预警
- WARNING_5: 最终预警
- WARNING_RESET: 用户重置了预警
- REVOKED: 留言被撤销
- DELIVERED: 留言已发送到接收人

## 数据库初始化

数据库初始化通过 `scripts/init_db.py` 完成，主要步骤：

1. 创建数据库（如果不存在）
2. 创建所有表
3. 设置必要的索引
4. 初始化基础数据（如果需要）

初始化命令：

```bash
python scripts/init_db.py
```

## 数据安全

### 1. 密码安全

- 用户密码使用安全算法加密存储
- 禁止明文存储敏感信息

### 2. 数据备份

- 定期全量备份
- 实时增量备份
- 备份文件加密存储

### 3. 访问控制

- 严格的用户权限管理
- 操作日志记录
- SQL注入防护
