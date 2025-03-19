# 部署指南

## 1. 环境要求

### 1.1 系统要求
- **操作系统**
  - Linux (推荐 Ubuntu 20.04 LTS)
  - macOS (10.15+)
  - Windows Server 2019+

- **硬件要求**
  - CPU: 2核+
  - 内存: 4GB+
  - 磁盘: 50GB+
  - 网络: 100Mbps+

### 1.2 软件要求
- **基础软件**
  - Python 3.8+
  - Node.js 14+
  - PostgreSQL 12+
  - Redis 6+
  - RabbitMQ 3.8+
  - Nginx 1.18+

- **Python包**
  ```
  Flask==2.0.1
  SQLAlchemy==1.4.23
  psycopg2-binary==2.9.1
  redis==3.5.3
  celery==5.1.2
  gunicorn==20.1.0
  python-jose==3.3.0
  passlib==1.7.4
  python-multipart==0.0.5
  ```

- **Node.js包**
  ```
  vue@3.0.0
  element-plus@2.0.0
  axios@0.21.1
  ```

## 2. 安装步骤

### 2.1 基础环境安装
```bash
# 更新系统包
sudo apt update
sudo apt upgrade

# 安装Python
sudo apt install python3.8 python3.8-venv python3.8-dev

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt install nodejs

# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 安装Redis
sudo apt install redis-server

# 安装RabbitMQ
sudo apt install rabbitmq-server

# 安装Nginx
sudo apt install nginx
```

### 2.2 数据库配置
```sql
-- 创建数据库
CREATE DATABASE cradle_message;

-- 创建用户
CREATE USER cradle_user WITH PASSWORD 'your_password';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE cradle_message TO cradle_user;
```

### 2.3 应用部署
```bash
# 克隆代码
git clone https://github.com/your-repo/cradle-message.git
cd cradle-message

# 创建虚拟环境
python3.8 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
npm run build
```

## 3. 配置说明

### 3.1 环境变量配置
```bash
# .env文件
FLASK_APP=app
FLASK_ENV=production
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://cradle_user:your_password@localhost/cradle_message
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

### 3.2 数据库配置
```python
# config/database.py
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### 3.3 Redis配置
```python
# config/redis.py
REDIS_URL = os.getenv('REDIS_URL')
```

### 3.4 RabbitMQ配置
```python
# config/rabbitmq.py
RABBITMQ_URL = os.getenv('RABBITMQ_URL')
```

## 4. 服务配置

### 4.1 Gunicorn配置
```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
threads = 2
timeout = 120
```

### 4.2 Nginx配置
```nginx
# /etc/nginx/sites-available/cradle-message
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/static/files;
    }

    location /media {
        alias /path/to/your/media/files;
    }
}
```

### 4.3 Celery配置
```python
# config/celery.py
broker_url = os.getenv('RABBITMQ_URL')
result_backend = os.getenv('REDIS_URL')
```

## 5. 服务启动

### 5.1 启动顺序
1. 启动PostgreSQL
```bash
sudo systemctl start postgresql
```

2. 启动Redis
```bash
sudo systemctl start redis-server
```

3. 启动RabbitMQ
```bash
sudo systemctl start rabbitmq-server
```

4. 启动Celery
```bash
celery -A app.celery worker --loglevel=info
celery -A app.celery beat --loglevel=info
```

5. 启动Gunicorn
```bash
gunicorn -c gunicorn.conf.py app:app
```

6. 启动Nginx
```bash
sudo systemctl start nginx
```

### 5.2 服务管理
```bash
# 查看服务状态
sudo systemctl status postgresql
sudo systemctl status redis-server
sudo systemctl status rabbitmq-server
sudo systemctl status nginx

# 重启服务
sudo systemctl restart postgresql
sudo systemctl restart redis-server
sudo systemctl restart rabbitmq-server
sudo systemctl restart nginx
```

## 6. 监控和维护

### 6.1 日志管理
```bash
# 应用日志
tail -f /var/log/cradle-message/app.log

# Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 系统日志
journalctl -u cradle-message
```

### 6.2 备份策略
```bash
# 数据库备份
pg_dump -U cradle_user cradle_message > backup.sql

# 文件备份
tar -czf media_backup.tar.gz /path/to/media
```

### 6.3 性能监控
```bash
# 系统监控
top
htop
iotop

# 应用监控
ps aux | grep python
ps aux | grep celery
```

## 7. 故障排除

### 7.1 常见问题
1. **数据库连接失败**
   - 检查PostgreSQL服务状态
   - 验证数据库用户权限
   - 检查防火墙设置

2. **Redis连接失败**
   - 检查Redis服务状态
   - 验证Redis配置
   - 检查内存使用情况

3. **RabbitMQ连接失败**
   - 检查RabbitMQ服务状态
   - 验证用户权限
   - 检查端口占用

4. **应用启动失败**
   - 检查日志文件
   - 验证环境变量
   - 检查依赖安装

### 7.2 性能优化
1. **数据库优化**
   - 创建索引
   - 优化查询
   - 定期维护

2. **缓存优化**
   - 调整缓存策略
   - 优化缓存键
   - 监控缓存命中率

3. **应用优化**
   - 调整工作进程数
   - 优化静态文件
   - 启用压缩 