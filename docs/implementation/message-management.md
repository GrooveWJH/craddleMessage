# 留言管理实现详情

## 概述

留言管理是摇篮留言系统的核心功能，包括留言创建、查看、撤销和预警响应等操作。本文档详细介绍留言管理功能的实现细节。

## 留言创建

### 功能描述

用户可以创建包含以下信息的留言：
- 留言内容（文本）
- 初始等待时间（月）
- 接收人信息（姓名、联系方式、联系类型）

### 实现细节

1. **前端实现**
   - 使用表单收集留言信息
   - 支持动态添加多个接收人
   - 提供预警机制说明

2. **后端实现**
   - 使用JWT验证用户身份
   - 使用Fernet对称加密存储留言内容
   - 自动生成撤销密钥
   - 计算预警时间表

3. **数据流**
   - 前端表单验证 → API请求 → 身份验证 → 数据处理 → 加密存储 → 返回密钥

4. **安全考虑**
   - 留言内容使用密钥加密，即使管理员也无法查看原文（除非在管理后台）
   - 撤销密钥仅显示一次，用户需自行保存

## 留言列表

### 功能描述

用户可以查看自己创建的所有留言列表，包含以下信息：
- 创建时间
- 内容预览（需要密钥才能查看完整内容）
- 预警级别（0-5）
- 下次预警时间
- 状态（活跃/已撤销）
- 操作按钮

### 实现细节

1. **前端实现**
   - 页面加载时自动请求用户留言列表
   - 使用表格展示留言基本信息
   - 使用不同颜色的徽章显示预警级别和状态
   - 提供查看按钮（需要输入密钥）

2. **后端实现**
   - 创建`/api/user/messages`端点获取当前用户留言
   - 仅返回基本信息，不包含完整内容
   - 按创建时间倒序排列

3. **用户体验**
   - 使用异步加载减少页面等待时间
   - 提供加载状态和错误提示
   - 支持响应式布局适配不同设备

## 留言查看

### 功能描述

用户可以通过正确的撤销密钥查看留言完整内容，包括：
- 留言文本内容
- 创建时间
- 初始延迟时间
- 当前状态
- 预警级别
- 下次预警时间
- 接收人列表

### 实现细节

1. **前端实现**
   - 提供密钥输入模态窗口
   - 验证密钥与留言ID匹配
   - 展示完整留言内容和相关信息
   - 提供撤销选项

2. **后端实现**
   - `/api/message/<message_id>/verify`端点验证密钥是否与留言ID匹配
   - `/api/message/view/<revocation_key>`端点使用密钥解密并返回留言内容
   - `/api/message/find-by-key/<revocation_key>`端点根据密钥查找留言ID

3. **安全机制**
   - 验证密钥与留言ID的匹配关系，防止使用A留言的密钥查看B留言
   - 使用密钥解密留言内容，确保只有持有密钥的人能查看
   - 错误提示不泄露敏感信息

## 留言撤销

### 功能描述

用户可以使用撤销密钥永久删除留言及其相关数据，此操作不可逆。

### 实现细节

1. **前端实现**
   - 提供撤销密钥输入表单
   - 显示撤销警告确认对话框
   - 撤销成功后提供反馈

2. **后端实现**
   - 验证撤销密钥有效性
   - 删除留言及其关联数据（接收人、状态日志）
   - 记录撤销操作日志

3. **数据安全**
   - 完全删除数据库记录而非标记为已删除
   - 撤销后数据无法恢复

## 预警响应

### 功能描述

用户可以对系统发出的预警进行响应，选择：
- 继续等待（进入下一级预警）
- 重置等待期（重置为初始设定的月数）

### 实现细节

1. **预警级别**
   - 第一次预警：初始等待期结束时
   - 第二次预警：第一次预警后1个月
   - 第三次预警：第二次预警后1个月
   - 第四次预警：第三次预警后1周
   - 最终预警：第四次预警后1天

2. **预警处理流程**
   - 系统定时任务检查达到预警时间的留言
   - 系统发送预警通知
   - 用户进行响应
   - 系统根据响应更新留言状态和下次预警时间

3. **自动发送机制**
   - 最终预警后24小时内未响应，系统自动发送留言
   - 自动发送后留言状态变为"已发送"

## 技术实现

### 前端技术

- JavaScript原生DOM操作
- 异步请求(fetch API)
- 模态窗口
- 表单验证
- 状态管理

### 后端技术

- Flask蓝图(Blueprint)架构
- JWT认证
- Fernet对称加密
- SQLAlchemy ORM
- 错误处理与日志记录

### 数据库模型

- Message模型：存储留言基本信息和加密内容
- Recipient模型：存储接收人信息
- StatusLog模型：记录留言状态变更

## 未来优化方向

1. **用户体验**
   - 添加留言分类功能
   - 提供留言搜索和筛选
   - 实现留言模板功能

2. **安全性**
   - 添加密钥恢复机制
   - 实现双因素验证
   - 增强密钥管理

3. **功能扩展**
   - 支持多种留言内容格式（图片、文件等）
   - 提供留言定时发送选项
   - 添加条件触发规则 