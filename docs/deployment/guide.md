# 摇篮留言服务系统 - 部署指南

本文档提供摇篮留言服务系统的部署步骤和最佳实践。

## 1. 系统要求

### 1.1 硬件要求

- **最低配置**:
  - CPU: 双核处理器
  - 内存: 4GB RAM
  - 硬盘: 20GB 可用空间

- **推荐配置**:
  - CPU: 四核处理器
  - 内存: 8GB RAM
  - 硬盘: 50GB SSD

### 1.2 软件要求

- **操作系统**:
  - Linux (推荐 Ubuntu 20.04 LTS 或更高版本)
  - macOS 10.15 或更高版本
  - Windows 10/11 (仅用于开发环境)

- **运行环境**:
  - Python 3.8 或更高版本
  - MySQL 5.7 或更高版本
  - Nginx 1.18 或更高版本 (生产环境)
  - Gunicorn 20.0 或更高版本 (生产环境)

## 2. 安装步骤

### 2.1 准备环境

#### Linux (Ubuntu)

```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装依赖
sudo apt install -y python3 python3-pip python3-venv mysql-server nginx

# 安装 MySQL
sudo apt install -y mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql

# 设置 MySQL 安全配置
sudo mysql_secure_installation
```

#### macOS

```bash
# 使用 Homebrew 安装
brew update
brew install python@3.8 mysql nginx

# 启动 MySQL
brew services start mysql
```

### 2.2 创建数据库

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库和用户
CREATE DATABASE cradle_message CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'cradle_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON cradle_message.* TO 'cradle_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2.3 设置应用

```bash
# 克隆代码库
git clone https://github.com/your-repo/cradle-message.git
cd cradle-message

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或者
# .\.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 创建一个.env文件或者直接export
export SECRET_KEY="your-secret-key"
export DATABASE_URL="mysql+pymysql://cradle_user:your_password@localhost/cradle_message"
export JWT_SECRET_KEY="your-jwt-secret-key"
export ENCRYPTION_KEY="your-encryption-key-32-bytes-long"
```

### 2.4 初始化数据库

```bash
# 初始化数据库
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 2.5 测试运行

```bash
# 测试运行
flask run --host=0.0.0.0 --port=5000
```

访问 http://localhost:5000 测试应用是否正常运行。

## 3. 生产环境配置

### 3.1 设置 Gunicorn

为生产环境创建 Gunicorn 配置文件:

```bash
# 创建 gunicorn.conf.py
touch gunicorn.conf.py
```

编辑 `gunicorn.conf.py`:

```python
# gunicorn.conf.py
workers = 4
bind = "127.0.0.1:8000"
timeout = 120
```

### 3.2 设置 Nginx

创建 Nginx 配置文件:

```bash
# 创建 Nginx 配置
sudo nano /etc/nginx/sites-available/cradle-message
```

编辑配置文件:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/cradle-message/static;
        expires 30d;
    }
}
```

启用网站配置:

```bash
sudo ln -s /etc/nginx/sites-available/cradle-message /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3.3 设置 Systemd 服务

创建 Systemd 服务文件:

```bash
sudo nano /etc/systemd/system/cradle-message.service
```

编辑服务文件:

```ini
[Unit]
Description=Cradle Message Service
After=network.target mysql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/cradle-message
Environment="PATH=/path/to/cradle-message/.venv/bin"
Environment="SECRET_KEY=your-secret-key"
Environment="DATABASE_URL=mysql+pymysql://cradle_user:your_password@localhost/cradle_message"
Environment="JWT_SECRET_KEY=your-jwt-secret-key"
Environment="ENCRYPTION_KEY=your-encryption-key-32-bytes-long"
ExecStart=/path/to/cradle-message/.venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启用并启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl enable cradle-message
sudo systemctl start cradle-message
sudo systemctl status cradle-message
```

## 4. 安全配置

### 4.1 设置 HTTPS

安装 Certbot:

```bash
sudo apt install -y certbot python3-certbot-nginx
```

获取 SSL 证书:

```bash
sudo certbot --nginx -d your-domain.com
```

### 4.2 防火墙设置

```bash
# 配置防火墙
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

### 4.3 系统安全性

```bash
# 更新系统安全补丁
sudo apt update
sudo apt upgrade -y

# 安装安全工具
sudo apt install -y fail2ban
```

## 5. 备份策略

### 5.1 数据库备份

创建数据库备份脚本:

```bash
nano backup.sh
```

添加以下内容:

```bash
#!/bin/bash
DATE=$(date +"%Y%m%d")
BACKUP_DIR="/path/to/backups"

# 确保备份目录存在
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u cradle_user -p'your_password' cradle_message > $BACKUP_DIR/cradle_message_$DATE.sql

# 压缩备份
gzip $BACKUP_DIR/cradle_message_$DATE.sql

# 保留最近30天的备份
find $BACKUP_DIR -name "cradle_message_*.sql.gz" -mtime +30 -delete
```

设置执行权限和定时任务:

```bash
chmod +x backup.sh
crontab -e

# 添加以下行
0 2 * * * /path/to/cradle-message/backup.sh
```

### 5.2 文件备份

```bash
# 创建一个简单的文件备份脚本
nano file_backup.sh
```

添加以下内容:

```bash
#!/bin/bash
DATE=$(date +"%Y%m%d")
BACKUP_DIR="/path/to/file_backups"
APP_DIR="/path/to/cradle-message"

# 确保备份目录存在
mkdir -p $BACKUP_DIR

# 备份应用文件
tar -czf $BACKUP_DIR/cradle_files_$DATE.tar.gz -C $APP_DIR --exclude=".venv" --exclude="__pycache__" .

# 保留最近10天的备份
find $BACKUP_DIR -name "cradle_files_*.tar.gz" -mtime +10 -delete
```

设置执行权限和定时任务:

```bash
chmod +x file_backup.sh
crontab -e

# 添加以下行
0 3 * * * /path/to/cradle-message/file_backup.sh
```

## 6. 监控与维护

### 6.1 日志管理

配置日志轮转:

```bash
sudo nano /etc/logrotate.d/cradle-message
```

添加以下内容:

```
/path/to/cradle-message/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data www-data
}
```

### 6.2 系统监控

安装监控工具:

```bash
# 安装监控工具
sudo apt install -y htop netdata
```

Netdata 提供 Web 界面，默认可通过 http://your-server-ip:19999 访问。

## 7. 扩展与高可用

### 7.1 负载均衡

对于高流量网站，可以考虑使用如下架构:

```
用户请求 → CDN → 负载均衡器 → 多个应用服务器 → 主从复制的数据库集群
```

### 7.2 水平扩展

1. 配置多个应用服务器
2. 使用共享配置和会话存储
3. 配置负载均衡器分发流量

## 8. 故障排除

### 8.1 常见问题

- **应用启动失败**
  - 检查日志文件 `/path/to/cradle-message/logs/app.log`
  - 确认所有环境变量正确设置
  - 验证数据库连接是否正常

- **数据库连接问题**
  - 验证数据库服务是否运行 `sudo systemctl status mysql`
  - 检查数据库连接字符串是否正确
  - 确认数据库用户权限

- **Nginx 配置问题**
  - 检查 Nginx 错误日志 `sudo tail -f /var/log/nginx/error.log`
  - 验证 Nginx 配置语法 `sudo nginx -t`

### 8.2 日志检查

```bash
# 查看应用日志
tail -f /path/to/cradle-message/logs/app.log

# 查看 Nginx 访问日志
sudo tail -f /var/log/nginx/access.log

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log

# 查看系统日志
sudo journalctl -fu cradle-message.service
```

## 9. 更新与升级

### 9.1 应用更新

```bash
# 进入应用目录
cd /path/to/cradle-message

# 拉取最新代码
git pull

# 激活虚拟环境
source .venv/bin/activate

# 安装最新依赖
pip install -r requirements.txt

# 更新数据库
flask db upgrade

# 重启服务
sudo systemctl restart cradle-message
```

### 9.2 系统更新

定期更新系统软件包:

```bash
sudo apt update
sudo apt upgrade -y
```

## 10. 联系与支持

如需技术支持，请联系:

- **项目主页**: [GitHub](https://github.com/your-repo/cradle-message)
- **问题报告**: [GitHub Issues](https://github.com/your-repo/cradle-message/issues)

---

本部署指南最后更新于 2024-06-25 