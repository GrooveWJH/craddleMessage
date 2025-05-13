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

## 10. Windows 开发/部署指南

本章节将指导您在一台未安装服务器软件的 Windows 系统上配置和运行摇篮留言系统。

### 10.1 安装必要软件

#### 10.1.1 安装 Python

1. 从 [Python 官网](https://www.python.org/downloads/windows/) 下载 Python 3.8 或更高版本的安装程序
2. 运行安装程序，确保勾选 "Add Python to PATH" 选项
3. 完成安装后，打开命令提示符（CMD）或 PowerShell，输入以下命令验证安装：

```cmd
python --version
pip --version
```

#### 10.1.2 安装 MySQL

1. 从 [MySQL 官网](https://dev.mysql.com/downloads/installer/) 下载 MySQL 安装程序
2. 运行安装程序，选择 "Custom" 安装类型
3. 在组件选择页面，确保选择了 MySQL Server 和 MySQL Workbench
4. 按照安装向导完成安装，设置 root 用户密码
5. 完成安装后，启动 MySQL Workbench 进行配置

### 10.2 项目配置

#### 10.2.1 创建数据库

1. 打开 MySQL Workbench，连接到本地 MySQL 服务器
2. 创建新的数据库和用户，执行以下 SQL 命令：

```sql
CREATE DATABASE cradle_message CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'cradle_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON cradle_message.* TO 'cradle_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 10.2.2 克隆项目

方法一：使用Git（推荐）

1. 安装 Git for Windows（如果尚未安装）：
   - 从 [Git 官网](https://git-scm.com/download/win) 下载安装程序
   - 按照默认选项完成安装

2. 克隆项目代码：
   - 打开命令提示符或 PowerShell
   - 切换到您想要存放项目的目录
   - 执行以下命令：

```cmd
git clone https://github.com/your-repo/cradle-message.git
cd cradle-message
```

方法二：不使用Git直接下载

1. 在浏览器中访问项目的GitHub仓库页面
2. 点击绿色的"Code"按钮，然后选择"Download ZIP"
3. 下载完成后，解压ZIP文件到您想要的目录
4. 打开命令提示符或PowerShell，切换到解压后的目录：

```cmd
cd path\to\cradle-message
```

#### 10.2.3 设置 Python 虚拟环境

```cmd
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

#### 10.2.4 配置环境变量

方法一：创建.env文件（推荐）

创建 `.env` 文件，填入必要的环境变量：

```
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://cradle_user:your_password@localhost/cradle_message
JWT_SECRET_KEY=your-jwt-secret-key
ENCRYPTION_KEY=your-encryption-key-32-bytes-long
```

方法二：使用Windows系统环境变量

1. 右键点击"此电脑"或"我的电脑"，选择"属性"
2. 点击"高级系统设置"
3. 在"高级"选项卡中，点击"环境变量"按钮
4. 在"系统变量"区域，点击"新建"按钮
5. 依次添加以下变量：
   - 变量名: SECRET_KEY, 变量值: your-secret-key
   - 变量名: DATABASE_URL, 变量值: mysql+pymysql://cradle_user:your_password@localhost/cradle_message
   - 变量名: JWT_SECRET_KEY, 变量值: your-jwt-secret-key
   - 变量名: ENCRYPTION_KEY, 变量值: your-encryption-key-32-bytes-long
6. 点击"确定"保存所有变量

#### 10.2.5 数据库配置替代方法

如果您不熟悉SQL命令，也可以通过MySQL Workbench图形界面完成数据库配置：

1. 打开MySQL Workbench并连接到您的MySQL服务器
2. 创建数据库：
   - 在导航栏中右键点击"Schemas"，选择"Create Schema..."
   - 输入名称"cradle_message"，字符集选择"utf8mb4"，排序规则选择"utf8mb4_unicode_ci"
   - 点击"Apply"，然后在确认对话框中再次点击"Apply"
3. 创建用户：
   - 点击左侧导航栏中的"Administration"
   - 点击"Users and Privileges"
   - 点击"Add Account"按钮
   - 在"Login"选项卡中设置用户名为"cradle_user"，主机为"localhost"，密码为您自定义的密码
   - 切换到"Schema Privileges"选项卡，点击"Add Entry..."
   - 选择"cradle_message"数据库，然后勾选"All"权限
   - 点击"Apply"保存设置

### 10.3 初始化数据库

```cmd
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 10.4 运行应用

#### 10.4.1 开发模式

```cmd
flask run --host=0.0.0.0 --port=5000
```

#### 10.4.2 生产模式（无需外部服务器）

在 Windows 上，可以使用 Waitress 作为 WSGI 服务器，无需 Nginx：

1. 安装 Waitress：

```cmd
pip install waitress
```

2. 创建 `run.py` 文件：

```python
from waitress import serve
from app import app

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
```

3. 运行应用：

```cmd
python run.py
```

### 10.5 设置为 Windows 服务（可选）

如果需要将应用作为 Windows 服务运行，可以使用 NSSM（Non-Sucking Service Manager）：

1. 从 [NSSM官网](https://nssm.cc/download) 下载 NSSM
2. 解压文件，将 nssm.exe 放在系统路径下或者项目目录中
3. 打开命令提示符（以管理员身份运行）
4. 执行以下命令：

```cmd
nssm install CradleMessage
```

5. 在弹出的配置窗口中：
   - Path: 输入 python.exe 的完整路径（例如：C:\path\to\.venv\Scripts\python.exe）
   - Startup directory: 输入项目目录路径
   - Arguments: 输入 run.py 的路径
   - 在 "Details" 选项卡中填写服务的显示名称和描述
   - 点击 "Install service"

6. 启动服务：

```cmd
nssm start CradleMessage
```

### 10.6 访问应用

完成上述步骤后，您可以通过以下网址访问应用：

- http://localhost:5000

如果需要从网络上的其他计算机访问，请确保 Windows 防火墙允许 5000 端口的传入连接。

### 10.7 常见问题排查

#### 10.7.1 端口占用问题

如果 5000 端口已被占用，可以选择其他端口，修改相应的命令：

```cmd
flask run --host=0.0.0.0 --port=8080
```

或在 `run.py` 中修改：

```python
serve(app, host='0.0.0.0', port=8080)
```

#### 10.7.2 数据库连接问题

- 检查 MySQL 服务是否正在运行（在服务管理器中查看）
- 确认数据库连接字符串中的用户名和密码是否正确
- 检查防火墙设置，确保应用可以连接到数据库（通常 MySQL 使用 3306 端口）

#### 10.7.3 文件权限问题

如果应用无法写入日志文件或其他文件，请确保运行应用的用户对相应的文件夹有写入权限。

#### 10.7.4 使用图形化界面运行项目（适合不熟悉命令行的用户）

对于不熟悉命令行操作的用户，可以采用以下图形化方式：

1. 安装PyCharm社区版：
   - 从[PyCharm官网](https://www.jetbrains.com/pycharm/download/)下载社区版（Community Edition，免费版本）
   - 按照安装向导完成安装

2. 使用PyCharm打开项目：
   - 启动PyCharm
   - 选择"Open"（打开），然后浏览到您的项目目录
   - 等待PyCharm加载和索引项目文件

3. 配置Python解释器：
   - 在PyCharm中，点击"File"→"Settings"（在Mac上是"PyCharm"→"Preferences"）
   - 在左侧导航栏选择"Project: cradle-message"→"Python Interpreter"
   - 点击齿轮图标，选择"Add..."
   - 选择"New Environment"，设置位置为项目目录下的".venv"文件夹
   - 点击"OK"确认

4. 安装依赖：
   - PyCharm会检测到requirements.txt文件
   - 在弹出的通知中，点击"Install requirements"
   - 或者在requirements.txt文件上右击，选择"Install All Packages"

5. 设置环境变量：
   - 点击右上角的运行配置下拉菜单
   - 选择"Edit Configurations..."
   - 点击"+"号，选择"Python"
   - 名称设为"Flask Run"
   - 脚本路径选择项目中的app.py
   - 在"Environment variables"字段中添加：
     ```
     SECRET_KEY=your-secret-key;DATABASE_URL=mysql+pymysql://cradle_user:your_password@localhost/cradle_message;JWT_SECRET_KEY=your-jwt-secret-key;ENCRYPTION_KEY=your-encryption-key-32-bytes-long
     ```
   - 点击"OK"保存配置

6. 运行项目：
   - 点击右上角的绿色三角形运行按钮
   - 应用将启动，您可以在PyCharm的控制台中看到输出
   - 在浏览器中访问http://localhost:5000

7. 调试项目：
   - 在代码中点击行号左侧设置断点
   - 点击右上角的绿色虫子图标（Debug）而不是运行按钮
   - PyCharm将在断点处暂停执行，您可以检查变量值和程序状态

### 10.8 常见错误及解决方案

#### 10.8.1 找不到模块错误

错误消息：`ModuleNotFoundError: No module named 'xxx'`

解决方案：
- 确保您的虚拟环境已激活
- 运行 `pip install -r requirements.txt` 安装所有依赖
- 如果使用PyCharm，确保配置了正确的Python解释器

#### 10.8.2 数据库连接错误

错误消息：`OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server on 'localhost'")`

解决方案：
- 检查MySQL服务是否正在运行（在服务管理器中查看）
- 确认用户名和密码是否正确
- 检查数据库名称是否正确创建

#### 10.8.3 权限错误

错误消息：`PermissionError: [Errno 13] Permission denied: 'xxx'`

解决方案：
- 以管理员身份运行命令提示符或PyCharm
- 检查文件或目录的权限设置
- 确保应用对日志目录有写入权限

## 11. 联系与支持

如需技术支持，请联系:

- **项目主页**: [GitHub](https://github.com/your-repo/cradle-message)
- **问题报告**: [GitHub Issues](https://github.com/your-repo/cradle-message/issues)

---

本部署指南最后更新于 2024-07-10