# 摇篮留言服务系统

一个安全、可靠的长期留言存储和发送服务系统。

## 功能特性

- **安全存储**
  - 端到端加密
  - 分布式存储
  - 多重备份

- **智能预警**
  - 五级预警机制
  - 灵活的时间设置
  - 多渠道通知

- **用户友好**
  - 简洁的界面
  - 便捷的操作
  - 完善的文档

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 14+
- PostgreSQL 12+
- Redis 6+
- RabbitMQ 3.8+
- Nginx 1.18+

### 安装步骤

1. 克隆代码
```bash
git clone https://github.com/your-repo/cradle-message.git
cd cradle-message
```

2. 安装后端依赖
```bash
python3.8 -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

3. 安装前端依赖
```bash
cd frontend
npm install
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，设置必要的环境变量
```

5. 初始化数据库
```bash
flask db upgrade
```

6. 启动服务
```bash
# 启动后端服务
flask run

# 启动前端服务
cd frontend
npm run serve
```

## 文档

- [系统概述](docs/overview/introduction.md)
- [功能说明](docs/overview/features.md)
- [技术架构](docs/architecture/technical.md)
- [API参考](docs/api/reference.md)
- [部署指南](docs/deployment/guide.md)
- [开发指南](docs/development/guide.md)
- [贡献指南](docs/CONTRIBUTING.md)
- [更新日志](docs/CHANGELOG.md)

## 开发

### 开发环境设置

1. 安装开发依赖
```bash
pip install -r requirements-dev.txt
```

2. 安装开发工具
```bash
# 安装pre-commit钩子
pre-commit install

# 安装测试工具
pytest
```

### 代码规范

- 遵循PEP 8规范
- 使用类型注解
- 编写单元测试
- 保持代码整洁

### 提交规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

## 测试

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_message.py

# 运行带覆盖率报告的测试
pytest --cov=app tests/
```

### 测试覆盖率
```bash
# 生成覆盖率报告
coverage report

# 生成HTML覆盖率报告
coverage html
```

## 部署

### 生产环境部署

1. 准备服务器
```bash
# 安装系统依赖
sudo apt update
sudo apt install python3.8 python3.8-venv nginx postgresql redis-server rabbitmq-server
```

2. 配置服务
```bash
# 配置Nginx
sudo cp nginx/cradle-message.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/cradle-message.conf /etc/nginx/sites-enabled/

# 配置系统服务
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

3. 启动服务
```bash
# 启动所有服务
sudo systemctl start postgresql redis-server rabbitmq-server
sudo systemctl start cradle-message
sudo systemctl start nginx
```

## 贡献

我们欢迎任何形式的贡献，包括但不限于：

- 提交问题
- 改进文档
- 提交代码
- 提供建议

请查看[贡献指南](docs/CONTRIBUTING.md)了解更多信息。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页：[GitHub](https://github.com/your-repo/cradle-message)
- 问题反馈：[Issues](https://github.com/your-repo/cradle-message/issues)
- 邮件联系：[email@example.com](mailto:email@example.com)

## 致谢

感谢所有为项目做出贡献的开发者！
