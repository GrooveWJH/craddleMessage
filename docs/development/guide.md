# 摇篮留言服务系统 - 开发指南

本文档提供摇篮留言服务系统的开发指南，帮助开发者理解系统架构并参与项目开发。

## 1. 开发环境设置

### 1.1 环境要求

- **操作系统**: Linux, macOS 或 Windows
- **Python**: 3.8+
- **数据库**: MySQL 5.7+
- **开发工具**: 任意代码编辑器或IDE (推荐 Visual Studio Code, PyCharm)
- **版本控制**: Git

### 1.2 环境设置

#### 基础环境设置

1. 克隆代码库:
```bash
git clone https://github.com/your-repo/cradle-message.git
cd cradle-message
```

2. 创建虚拟环境:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或者
# .\.venv\Scripts\activate  # Windows
```

3. 安装依赖:
```bash
pip install -r requirements.txt
```

4. 安装开发依赖:
```bash
pip install pytest pytest-cov black flake8
```

#### 数据库设置

1. 安装和启动MySQL:
   - Linux: `sudo apt install mysql-server && sudo systemctl start mysql`
   - macOS: `brew install mysql && brew services start mysql`
   - Windows: 下载并安装MySQL安装包

2. 创建开发数据库:
```sql
CREATE DATABASE cradle_message_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'cradle_dev'@'localhost' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON cradle_message_dev.* TO 'cradle_dev'@'localhost';
FLUSH PRIVILEGES;
```

#### 环境变量设置

创建`.env`文件在项目根目录:
```
SECRET_KEY=dev-secret-key
DATABASE_URL=mysql+pymysql://cradle_dev:dev_password@localhost/cradle_message_dev
JWT_SECRET_KEY=dev-jwt-secret-key
ENCRYPTION_KEY=dev-encryption-key-32-bytes-long
FLASK_ENV=development
FLASK_DEBUG=1
```

## 2. 项目结构

```
cradle-message/
├── app.py                # 主应用文件
├── models.py             # 数据模型定义
├── config/               # 配置文件
│   └── config.py         # 配置类
├── static/               # 静态资源
│   ├── css/              # CSS样式表
│   ├── js/               # JavaScript文件
│   └── images/           # 图片资源
├── templates/            # HTML模板
│   ├── index.html        # 首页模板
│   ├── login.html        # 登录页模板
│   └── admin.html        # 管理页模板
├── logs/                 # 日志文件夹
├── scripts/              # 实用脚本
├── docs/                 # 文档
├── tests/                # 测试文件
│   ├── test_models.py    # 模型测试
│   ├── test_api.py       # API测试
│   └── test_views.py     # 视图测试
├── .env                  # 环境变量
├── .gitignore            # Git忽略文件
├── requirements.txt      # 项目依赖
└── README.md             # 项目说明
```

## 3. 代码规范

### 3.1 Python代码规范

- 遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)代码风格指南
- 使用[Black](https://github.com/psf/black)格式化代码
- 使用[Flake8](https://flake8.pycqa.org/)进行代码检查
- 添加类型注解
- 编写文档字符串(docstrings)

示例:
```python
def calculate_next_warning_date(initial_date: datetime, warning_level: int) -> datetime:
    """
    计算下一个预警日期
    
    参数:
        initial_date: 初始日期
        warning_level: 当前预警级别(0-5)
        
    返回:
        下一个预警的日期时间
    """
    if warning_level == 0:
        return initial_date + timedelta(days=30)
    elif warning_level == 1:
        return initial_date + timedelta(days=30)
    elif warning_level == 2:
        return initial_date + timedelta(days=7)
    elif warning_level == 3:
        return initial_date + timedelta(days=1)
    else:
        return initial_date + timedelta(hours=24)
```

### 3.2 HTML/CSS/JavaScript规范

- HTML: 使用语义化标签，保持结构清晰
- CSS: 使用统一的命名规范，避免行内样式
- JavaScript: 遵循ES6语法规范，避免全局变量

### 3.3 Git提交规范

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
feat(message): 添加留言预警重置功能

- 添加预警重置API接口
- 实现预警级别重置逻辑
- 更新用户界面显示

Closes #123
```

## 4. 开发流程

### 4.1 分支管理

- `main`: 主分支，保持稳定可发布状态
- `develop`: 开发分支，集成最新功能
- `feature/*`: 功能分支，用于开发新功能
- `bugfix/*`: 问题修复分支，用于修复非紧急bug
- `hotfix/*`: 紧急修复分支，用于修复生产环境问题

### 4.2 开发步骤

1. 从最新的`develop`分支创建功能分支
```bash
git checkout develop
git pull
git checkout -b feature/new-feature-name
```

2. 进行开发，并定期提交
```bash
git add .
git commit -m "feat: implement new feature"
```

3. 更新开发分支内容
```bash
git checkout develop
git pull
git checkout feature/new-feature-name
git merge develop
```

4. 解决冲突(如有)并提交
```bash
git add .
git commit -m "merge: resolve conflicts"
```

5. 推送分支到远程仓库
```bash
git push -u origin feature/new-feature-name
```

6. 创建Pull Request (PR)
   - 描述新功能或修复的问题
   - 列出主要更改
   - 添加相关的issue引用

### 4.3 代码审查

- 所有PR必须通过代码审查
- 审查者应检查代码质量、功能实现和测试覆盖率
- 审查通过后才能合并到主干分支

## 5. 数据库迁移

使用Flask-Migrate进行数据库迁移:

1. 初始化迁移(仅首次运行):
```bash
flask db init
```

2. 创建迁移脚本:
```bash
flask db migrate -m "描述更改"
```

3. 应用迁移:
```bash
flask db upgrade
```

4. 回滚迁移:
```bash
flask db downgrade
```

## 6. 测试

### 6.1 测试框架

- 使用[pytest](https://docs.pytest.org/)编写和运行测试
- 使用[coverage](https://coverage.readthedocs.io/)计算测试覆盖率

### 6.2 测试分类

- **单元测试**: 测试单个函数或类
- **集成测试**: 测试多个组件协同工作
- **API测试**: 测试API接口
- **端到端测试**: 测试整个应用流程

### 6.3 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_models.py

# 运行带测试覆盖率的测试
pytest --cov=app tests/

# 生成HTML覆盖率报告
pytest --cov=app --cov-report=html tests/
```

### 6.4 测试示例

```python
def test_message_revocation():
    """测试留言撤销功能"""
    # 创建测试用户
    user = User(username="testuser", email="test@example.com", password="password")
    db.session.add(user)
    db.session.commit()
    
    # 创建测试留言
    message = Message(user_id=user.id, content="测试留言", initial_delay_months=3)
    message.generate_revocation_key()
    db.session.add(message)
    db.session.commit()
    
    # 保存撤销密钥
    revocation_key = message.revocation_key
    
    # 测试撤销功能
    message = Message.query.filter_by(revocation_key=revocation_key).first()
    assert message is not None
    assert message.is_active is True
    
    # 撤销留言
    message.is_active = False
    db.session.commit()
    
    # 验证撤销结果
    message = Message.query.get(message.id)
    assert message.is_active is False
```

## 7. API开发

### 7.1 API规范

- 使用RESTful风格设计API
- 使用JSON格式进行数据交换
- 使用JWT进行API认证
- 使用适当的HTTP状态码

### 7.2 API路由设计

- `/api/message`: 留言管理
  - `POST`: 创建新留言
  - `GET`: 获取留言列表
  - `GET /<id>`: 获取特定留言
  - `PUT /<id>`: 更新留言
  - `DELETE /<id>`: 删除留言

- `/api/message/revoke/<revocation_key>`: 撤销留言
  - `POST`: 使用撤销密钥撤销留言

- `/api/message/<message_id>/warning/response`: 预警响应处理
  - `POST`: 处理用户对预警的响应

### 7.3 API示例

创建新留言:
```python
@app.route('/api/message', methods=['POST'])
@jwt_required()
def create_message():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        message = Message(
            user_id=user_id,
            content=data['content'],
            initial_delay_months=data['initial_delay_months']
        )
        
        # 处理其他逻辑...
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'message': '留言创建成功',
            'id': message.id,
            'revocation_key': message.revocation_key
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## 8. 前端开发

### 8.1 模板结构

使用Jinja2模板引擎构建前端页面:

```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}摇篮留言系统{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block head %}{% endblock %}
</head>
<body>
    <header>
        <nav>
            <a href="{{ url_for('index') }}">首页</a>
            {% if current_user.is_authenticated %}
                <a href="{{ url_for('logout') }}">登出</a>
            {% else %}
                <a href="{{ url_for('login') }}">登录</a>
            {% endif %}
        </nav>
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>&copy; 2024 摇篮留言系统</p>
    </footer>
    
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

### 8.2 表单处理

使用Flask的表单处理方式:

```html
<!-- login.html -->
{% extends 'base.html' %}

{% block title %}登录 - 摇篮留言系统{% endblock %}

{% block content %}
<section class="login-form">
    <h1>用户登录</h1>
    
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <div class="flash-messages">
                {% for message in messages %}
                    <div class="flash-message">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}
    
    <form method="post" action="{{ url_for('login') }}">
        <div class="form-group">
            <label for="username">用户名</label>
            <input type="text" id="username" name="username" required>
        </div>
        
        <div class="form-group">
            <label for="password">密码</label>
            <input type="password" id="password" name="password" required>
        </div>
        
        <button type="submit">登录</button>
    </form>
</section>
{% endblock %}
```

### 8.3 JavaScript交互

使用原生JavaScript进行前端交互:

```javascript
// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // 处理表单提交
    const messageForm = document.getElementById('message-form');
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const content = document.getElementById('content').value;
            const initial_delay_months = document.getElementById('initial_delay_months').value;
            
            // 获取接收人信息
            const recipients = [];
            const recipientElements = document.querySelectorAll('.recipient');
            recipientElements.forEach(element => {
                const name = element.querySelector('.name').value;
                const contact = element.querySelector('.contact').value;
                const contact_type = element.querySelector('.contact-type').value;
                
                recipients.push({
                    name,
                    contact,
                    contact_type
                });
            });
            
            // 发送API请求
            fetch('/api/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('token')
                },
                body: JSON.stringify({
                    content,
                    initial_delay_months,
                    recipients
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.revocation_key) {
                    // 显示撤销密钥
                    document.getElementById('revocation-key').textContent = data.revocation_key;
                    document.getElementById('success-message').style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('error-message').style.display = 'block';
            });
        });
    }
});
```

## 9. 安全开发

### 9.1 认证与授权

系统使用Flask-Login和JWT进行身份认证:

```python
# 设置Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 设置JWT
jwt = JWTManager(app)
```

### 9.2 数据加密

敏感数据应该加密存储:

```python
def encrypt_data(data):
    """加密敏感数据"""
    key = base64.urlsafe_b64decode(os.environ.get('ENCRYPTION_KEY'))
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    """解密敏感数据"""
    key = base64.urlsafe_b64decode(os.environ.get('ENCRYPTION_KEY'))
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()
```

### 9.3 输入验证

所有用户输入都应该进行验证:

```python
def validate_message_data(data):
    """验证留言数据"""
    errors = {}
    
    if 'content' not in data or not data['content']:
        errors['content'] = '留言内容不能为空'
    
    if 'initial_delay_months' not in data:
        errors['initial_delay_months'] = '初始延迟时间不能为空'
    elif not isinstance(data['initial_delay_months'], int) or data['initial_delay_months'] < 1:
        errors['initial_delay_months'] = '初始延迟时间必须是大于0的整数'
    
    if 'recipients' not in data or not data['recipients']:
        errors['recipients'] = '接收人不能为空'
    else:
        for i, recipient in enumerate(data['recipients']):
            if 'name' not in recipient or not recipient['name']:
                errors[f'recipients[{i}].name'] = '接收人姓名不能为空'
            
            if 'contact' not in recipient or not recipient['contact']:
                errors[f'recipients[{i}].contact'] = '联系方式不能为空'
            
            if 'contact_type' not in recipient or recipient['contact_type'] not in ['email', 'phone', 'wechat']:
                errors[f'recipients[{i}].contact_type'] = '联系方式类型无效'
    
    return errors
```

### 9.4 日志记录

记录关键操作日志:

```python
import logging

logger = logging.getLogger(__name__)

@app.route('/api/message/revoke/<revocation_key>', methods=['POST'])
def revoke_message(revocation_key):
    try:
        message = Message.query.filter_by(revocation_key=revocation_key, is_active=True).first()
        if not message:
            logger.warning(f'尝试使用无效的撤销密钥: {revocation_key}')
            return jsonify({'error': '无效的撤销密钥或留言已被撤销'}), 404
        
        message.is_active = False
        db.session.commit()
        
        logger.info(f'留言 {message.id} 被撤销')
        return jsonify({'message': '留言撤销成功'}), 200
    except Exception as e:
        logger.error(f'撤销留言失败: {str(e)}')
        return jsonify({'error': '撤销留言失败'}), 500
```

## 10. 性能优化

### 10.1 数据库优化

- 为常用查询添加索引
- 使用合适的数据类型
- 优化SQL查询

```python
# 添加索引示例
class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    revocation_key = db.Column(db.String(255), unique=True, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    next_warning_date = db.Column(db.DateTime, nullable=False, index=True)
```

### 10.2 代码优化

- 避免不必要的数据库查询
- 使用批量操作
- 避免重复计算

```python
# 优化前
for user_id in user_ids:
    user = User.query.get(user_id)
    # 处理用户...

# 优化后
users = User.query.filter(User.id.in_(user_ids)).all()
for user in users:
    # 处理用户...
```

### 10.3 缓存策略

- 使用缓存减少数据库访问
- 缓存不经常变化的数据
- 设置合理的缓存过期时间

## 11. 故障排除

### 11.1 调试技巧

- 使用Flask的调试模式:
```bash
FLASK_DEBUG=1 flask run
```

- 使用日志记录关键信息:
```python
app.logger.debug('调试信息')
app.logger.info('信息日志')
app.logger.warning('警告信息')
app.logger.error('错误信息')
```

- 使用交互式调试器(如需要):
```python
import pdb; pdb.set_trace()
```

### 11.2 常见问题

- **数据库连接问题**
  - 检查数据库连接字符串
  - 确保数据库服务运行中
  - 验证用户权限

- **模板渲染问题**
  - 检查变量名拼写
  - 查看模板路径是否正确
  - 确认上下文数据存在

- **API 响应问题**
  - 验证请求格式是否正确
  - 检查认证状态
  - 查看服务器日志

## 12. 文档规范

### 12.1 代码文档

- 为模块、类、方法添加文档字符串
- 遵循[Google风格的文档字符串](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings)

```python
def handle_warning_response(message_id, response):
    """
    处理用户对预警的响应
    
    处理用户收到预警通知后的响应，包括重置预警周期或继续预警流程
    
    Args:
        message_id: 留言ID
        response: 用户响应，可能值为'RESET'或'CONTINUE'
        
    Returns:
        dict: 包含处理结果的字典
        
    Raises:
        ValueError: 当响应值无效时
        NotFoundError: 当留言不存在时
    """
    # 实现代码...
```

### 12.2 项目文档

- 使用Markdown编写文档
- 保持文档的及时更新
- 文档应包括以下部分:
  - 系统架构
  - API参考
  - 开发指南
  - 部署指南
  - 用户手册

## 13. 协作工具

### 13.1 版本控制

- Git: 代码版本控制
- GitHub/GitLab: 代码托管和协作

### 13.2 项目管理

- Issues: 跟踪任务和bug
- Projects: 项目进度跟踪
- Milestones: 版本规划

### 13.3 持续集成

- GitHub Actions: 自动化测试和部署
- Jenkins: 自定义CI/CD流程

## 14. 联系方式

如有开发相关问题，请联系:

- GitHub Issues: https://github.com/your-repo/cradle-message/issues
- 开发者邮件: dev@example.com

---

本开发指南最后更新于2024-06-25 