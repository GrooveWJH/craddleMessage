# 摇篮留言服务系统文档

## 文档目录

### 1. 系统概述
- [系统简介](overview/introduction.md)
- [系统特性](overview/features.md)

### 2. 架构设计
- [系统架构](architecture/system.md)
- [蓝图架构](architecture/blueprint.md)
- [数据库设计](architecture/database.md)
- [API架构](architecture/api.md)
- [技术架构](architecture/technical.md)

### 3. 功能实现
- [留言管理](implementation/message-management.md)
- [用户认证](implementation/authentication.md)
- [安全机制](implementation/security.md)
- [前端实现](implementation/frontend.md)

### 4. API参考
- [API文档](api/reference.md)

### 5. 部署与运维
- [部署指南](deployment/guide.md)

### 6. 开发指南
- [开发指南](development/guide.md)
- [贡献指南](CONTRIBUTING.md)

### 7. 变更记录
- [更新日志](CHANGELOG.md)

## 最新功能

### 留言管理功能
- **我的留言列表**：用户可以查看自己创建的所有留言，包括状态、预警级别等信息
- **留言内容查看**：通过密钥验证可以查看完整留言内容
- **留言撤销**：用户可以使用撤销密钥彻底删除留言数据

### 安全特性
- **内容加密**：使用Fernet对称加密保护留言内容
- **密钥验证**：实现留言ID与密钥匹配验证，防止密钥滥用
- **数据保护**：撤销留言时完全删除数据库记录

### 用户界面
- **响应式设计**：适配不同设备屏幕大小
- **交互反馈**：添加操作成功/失败的提示信息
- **状态显示**：使用颜色和图标直观显示留言状态和预警级别

## 文档说明

本文档采用 Markdown 格式编写，使用 Mermaid 图表来展示系统流程和架构。文档结构清晰，便于查阅和维护。

### 文档更新

- 最后更新：2024-05-30
- 版本：1.1.0
- 状态：开发中

### 文档维护

本文档由开发团队维护，如有问题或建议，请提交 Issue 或 Pull Request。

## 快速开始

1. 克隆项目

```bash
git clone https://github.com/your-username/cradle-message.git
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 初始化数据库

```bash
python scripts/init_db.py
```

4. 启动服务

```bash
python app.py
```

## 系统要求

- Python 3.8+
- MySQL 5.7+
- 所需Python包（详见requirements.txt）

## 许可证

MIT License
