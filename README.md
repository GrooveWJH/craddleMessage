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

- **后端框架**：Flask（使用蓝图模块化）
- **数据库**：MySQL (使用SQLAlchemy ORM)
- **身份验证**：Flask-Login + JWT
- **加密**：Cryptography库
- **任务调度**：APScheduler

### 蓝图架构

项目使用Flask的蓝图(Blueprint)特性进行模块化组织，提高代码的可维护性和可扩展性：

- **认证蓝图(`auth_bp`)**：处理用户认证相关功能
  - 登录/注册
  - 登出
  - 调试快速登录
  
- **API蓝图(`api_bp`)**：处理所有API请求
  - 留言创建
  - 留言撤销
  - 预警响应处理
  
- **主页蓝图(`main_bp`)**：处理主要页面路由
  - 首页
  - 管理后台

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
export JWT_SECRET_KEY="your-jwt-secret-key"
export ENCRYPTION_KEY="your-encryption-key-32-bytes-long"
```

4. 初始化数据库

```bash
# 先创建数据库
mysql -u root -p
CREATE DATABASE cradle_message CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'cradle_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON cradle_message.* TO 'cradle_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 初始化数据库结构
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. 启动服务

```bash
flask run
```

## 使用说明

### 用户注册

系统支持通过前端注册新用户：

1. 访问首页点击"注册"按钮
2. 填写用户名、电子邮箱和密码
3. 提交注册表单

### 创建留言

1. 登录系统
   - 访问首页并点击"登录"按钮
   - 输入用户名和密码
   - 提交登录表单

2. 填写留言信息
   - 在主页的"创建新留言"卡片中填写信息
   - 输入留言内容
   - 选择初始延迟时间（1-60个月）
   - 添加接收人信息（姓名、联系方式和联系类型）
   - 点击"添加接收人"按钮可添加多个接收人

3. 提交留言
   - 点击"创建留言"按钮提交
   - 系统将返回撤销密钥和预警时间表
   - **重要**: 请妥善保存撤销密钥，这是撤销留言的唯一凭证

### 管理留言

1. 查看留言
   - 登录后在首页可查看"我的留言"列表
   - 列表显示创建时间、内容预览、预警级别、下次预警时间和状态

2. 撤销留言
   - 使用创建留言时获得的撤销密钥可随时撤销留言
   - 撤销后留言状态将变为非活跃，且不可恢复

### 预警响应

当系统发送预警通知时，用户有两种响应选择：

1. **重置预警**
   - 预警级别将重置为0
   - 下次预警时间将设置为当前时间加上初始延迟时间
   - 预警周期重新开始

2. **继续预警**
   - 预警级别提升至下一级
   - 系统根据当前预警级别更新下次预警时间：
     - 第1级到第2级：30天后
     - 第2级到第3级：30天后
     - 第3级到第4级：7天后
     - 第4级到第5级：1天后
     - 第5级：24小时后自动发送留言

### 管理后台

1. 访问管理后台
   - 以管理员身份登录系统
   - 点击导航栏中的"管理后台"链接

2. 查看统计信息
   - 用户总数
   - 留言总数
   - 活跃留言数量
   - 各级别预警的留言数量

### 调试模式

系统提供调试模式，方便开发和测试：

1. 在app.py中设置`DEBUG_MODE = True`
2. 访问首页时将出现调试登录选项
3. 可快速以管理员或测试用户身份登录

## 技术文档

更多技术细节请参考[技术文档](docs/tech.md)

## 开发指南

### 目录结构

```
cradle-message/
├── app.py            # 主应用入口
├── models.py         # 数据模型定义
├── routes/           # 路由蓝图模块
│   ├── __init__.py   # 初始化文件
│   ├── auth.py       # 认证相关路由
│   ├── api.py        # API接口路由
│   └── main.py       # 主要页面路由
├── config/           # 配置文件
├── templates/        # HTML模板
├── static/           # 静态资源
│   ├── css/          # 样式文件
│   ├── js/           # JavaScript文件
│   └── img/          # 图片资源
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
