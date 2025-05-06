# 摇篮留言服务系统

这是一个安全、可靠的长期留言存储和发送服务系统，提供定时留言传递功能和多级预警机制。

## 功能特性

- **安全存储**
  - 端到端加密保护敏感信息
  - 使用密钥管理和撤销机制
  - 对用户信息和留言内容进行加密处理

- **智能预警机制**
  - 五级预警系统，逐步递增预警频率
  - 用户可配置初始延迟时间
  - 灵活的预警响应选择（重置或继续）

- **用户友好**
  - 简洁直观的界面设计
  - 便捷的留言创建和管理
  - 详细的状态记录和跟踪

## 系统架构

- **后端框架**：Flask
- **数据库**：MySQL (使用SQLAlchemy ORM)
- **身份验证**：Flask-Login + JWT
- **加密**：Cryptography库
- **任务调度**：APScheduler

## 核心模块

1. **用户管理**
   - 注册、登录和认证
   - 用户权限控制

2. **留言管理**
   - 创建、存储和加密留言
   - 生成撤销密钥
   - 管理接收人信息

3. **预警系统**
   - 多级预警时间表计算
   - 预警响应处理（重置/继续）
   - 状态记录和跟踪

4. **管理后台**
   - 系统状态监控
   - 留言统计和管理
   - 用户管理功能

## 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+
- 其他依赖见requirements.txt

### 安装步骤

1. 克隆代码
```bash
git clone https://github.com/your-repo/cradle-message.git
cd cradle-message
```

2. 安装依赖
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

3. 配置环境变量
```bash
# 设置必要的环境变量
export SECRET_KEY="your-secret-key"
export DATABASE_URL="mysql+pymysql://username:password@localhost/cradle_message"
export ENCRYPTION_KEY="your-encryption-key-32-bytes-long"
```

4. 初始化数据库
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. 启动服务
```bash
flask run
```

## 使用说明

### 创建留言

1. 注册并登录系统
2. 填写留言内容
3. 设置初始延迟时间
4. 添加接收人信息
5. 保存留言并记录撤销密钥

### 管理留言

1. 通过撤销密钥可以随时撤销留言
2. 收到预警通知后可以选择重置预警周期或继续

### 预警响应

当系统发送预警通知时，用户有两种选择：
- **重置预警**：将预警级别重置为0，重新开始预警周期
- **继续预警**：预警级别提升，进入下一级预警

## 技术文档

更多技术细节请参考[技术文档](tech.md)

## 开发指南

### 目录结构

```
cradle-message/
├── app.py            # 主应用入口
├── models.py         # 数据模型定义
├── config/           # 配置文件
├── templates/        # HTML模板
├── static/           # 静态资源
├── logs/             # 日志文件
└── scripts/          # 辅助脚本
```

### 开发环境设置

参考快速开始部分设置开发环境。

### 代码规范

- 遵循PEP 8规范
- 添加适当的类型注解
- 编写单元测试
- 保持代码整洁

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页：[GitHub](https://github.com/your-repo/cradle-message)
- 问题反馈：[Issues](https://github.com/your-repo/cradle-message/issues)

## 致谢

感谢所有为项目做出贡献的开发者！
