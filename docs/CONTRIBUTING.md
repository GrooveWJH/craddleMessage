# 贡献指南

感谢您对摇篮留言服务系统的关注！我们欢迎并感谢任何形式的贡献。本文档提供了如何参与项目开发的指南。

## 开发环境设置

### 克隆代码库

```bash
git clone https://github.com/your-repo/cradle-message.git
cd cradle-message
```

### 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Linux/macOS
source .venv/bin/activate
# Windows
.\.venv\Scripts\activate
```

### 安装依赖

```bash
pip install -r requirements.txt

# 如果需要开发环境特定依赖
pip install pytest pytest-cov black flake8
```

### 设置数据库

```bash
# 使用MySQL客户端创建数据库
mysql -u root -p
CREATE DATABASE cradle_message_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'cradle_dev'@'localhost' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON cradle_message_dev.* TO 'cradle_dev'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 配置环境变量
export SECRET_KEY="dev-secret-key"
export DATABASE_URL="mysql+pymysql://cradle_dev:dev_password@localhost/cradle_message_dev"
export JWT_SECRET_KEY="dev-jwt-secret-key"
export ENCRYPTION_KEY="dev-encryption-key-32-bytes-long"

# 初始化数据库
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 创建测试用户

```python
# 使用Python Shell创建用户
python -c "
from app import app, db
from models import User

with app.app_context():
    # 创建普通用户
    user = User(username='testuser', email='test@example.com', password='password')
    db.session.add(user)
    
    # 创建管理员用户
    admin = User(username='admin', email='admin@example.com', password='admin123')
    db.session.add(admin)
    
    db.session.commit()
    print('用户创建成功')
"
```

### 启动开发服务器

```bash
flask run
```

访问 http://localhost:5000 开始使用应用。

## 项目结构

```
cradle-message/
├── app.py                # 主应用文件
├── models.py             # 数据模型定义
├── config/               # 配置文件
│   └── config.py         # 配置类
├── static/               # 静态资源
│   ├── css/              # CSS样式表
│   ├── js/               # JavaScript文件
│   └── img/              # 图片资源
├── templates/            # HTML模板
│   ├── index.html        # 首页模板
│   ├── login.html        # 登录页模板
│   └── admin.html        # 管理页模板
├── docs/                 # 文档
│   ├── api/              # API文档
│   ├── architecture/     # 架构文档
│   ├── deployment/       # 部署文档
│   ├── development/      # 开发文档
│   └── overview/         # 概述文档
├── logs/                 # 日志文件夹
├── scripts/              # 实用脚本
├── .venv/                # 虚拟环境(不提交)
├── .gitignore            # Git忽略配置
├── requirements.txt      # 项目依赖
└── README.md             # 项目说明
```

## 开发流程

### 分支策略

- `main`: 主分支，保持稳定可发布状态
- `develop`: 开发分支，集成最新功能
- `feature/*`: 功能分支，用于开发新功能
- `bugfix/*`: 问题修复分支，用于修复bug
- `hotfix/*`: 紧急修复分支，用于修复生产环境问题

### 开发步骤

1. 从最新的`develop`分支创建功能分支
```bash
git checkout develop
git pull
git checkout -b feature/your-feature-name
```

2. 进行开发，并定期提交
```bash
git add .
git commit -m "feat: implement your feature"
```

3. 完成开发后，合并最新的develop分支内容
```bash
git checkout develop
git pull
git checkout feature/your-feature-name
git merge develop
```

4. 解决冲突(如有)并推送分支
```bash
git add .
git commit -m "merge: resolve conflicts"
git push -u origin feature/your-feature-name
```

5. 创建Pull Request (PR)，等待代码审查

## 代码规范

### Python代码规范

- 遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)代码风格
- 使用4个空格缩进
- 最大行长度为88字符
- 使用描述性的变量名和函数名
- 为函数、类和模块添加文档字符串(docstrings)
- 添加类型注解

示例:
```python
def calculate_warning_date(base_date: datetime, warning_level: int) -> datetime:
    """
    根据基准日期和预警级别计算下一个预警日期
    
    参数:
        base_date: 基准日期时间
        warning_level: 预警级别(0-5)
        
    返回:
        计算得出的下一个预警日期时间
    """
    if warning_level == 0:
        return base_date + timedelta(days=30)
    elif warning_level == 1:
        return base_date + timedelta(days=30)
    elif warning_level == 2:
        return base_date + timedelta(days=7)
    elif warning_level == 3:
        return base_date + timedelta(days=1)
    else:
        return base_date + timedelta(hours=24)
```

### 前端代码规范

- HTML: 使用语义化标签，保持结构清晰
- CSS: 使用一致的命名约定，避免行内样式
- JavaScript: 使用ES6+语法，避免全局变量

### 提交信息规范

使用规范化的提交信息格式:
```
<类型>(<范围>): <描述>

<详细说明>

<相关issue>
```

类型包括:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档变更
- `style`: 代码格式变更
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 其他变更

示例:
```
feat(warning): 添加预警重置功能

- 实现预警级别重置API
- 添加重置按钮到前端界面
- 更新状态日志记录

Closes #42
```

## 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行指定测试
pytest tests/test_models.py

# 带覆盖率报告
pytest --cov=. tests/
```

### 编写测试

- 为每个主要功能编写测试
- 使用描述性的测试函数名
- 确保测试独立且可重复运行
- 模拟外部依赖

示例:
```python
def test_generate_revocation_key():
    """测试撤销密钥生成功能"""
    message = Message(
        user_id=1,
        content="测试留言",
        initial_delay_months=3,
        next_warning_date=datetime.utcnow() + timedelta(days=90)
    )
    
    key = message.generate_revocation_key()
    
    assert key is not None
    assert len(key) > 0
    assert message.revocation_key == key
```

## 文档

### 文档结构

- `/docs/api/`: API参考文档
- `/docs/architecture/`: 系统架构文档
- `/docs/deployment/`: 部署指南
- `/docs/development/`: 开发指南
- `/docs/overview/`: 系统概述

### 更新文档

- 添加新功能时，同步更新相关文档
- 修改API时，更新API参考文档
- 修改架构时，更新架构文档
- 使用Markdown格式编写文档

## 报告问题

如果您发现问题或有功能建议，请通过项目的Issue系统报告:

1. 检查是否已存在相同或类似的Issue
2. 创建新Issue，提供详细描述和复现步骤
3. 如可能，提供screenshots或错误日志

## 联系方式

如果您有任何问题或需要帮助，可以通过以下方式联系我们:

- 项目Issues: https://github.com/your-repo/cradle-message/issues
- 电子邮件: contact@example.com

感谢您的贡献！ 