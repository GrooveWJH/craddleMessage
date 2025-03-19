import sys
import os

# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from app import app
from models import db, User
from config.config import Config
from sqlalchemy import create_engine, text
from datetime import datetime

def init_database():
    # 创建数据库连接（不指定数据库名）
    engine = create_engine('mysql+pymysql://root:302811055wjhhz@localhost/')
    
    # 创建数据库（如果不存在）
    with engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS cradle_message"))
        conn.commit()
    
    # 使用应用上下文创建表
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建管理员用户（如果不存在）
        admin_user = User.query.filter_by(username=Config.ADMIN_USERNAME).first()
        if not admin_user:
            admin_user = User(
                username=Config.ADMIN_USERNAME,
                email='admin@example.com',
                password=Config.ADMIN_PASSWORD,
                created_at=datetime.utcnow()
            )
            db.session.add(admin_user)
            db.session.commit()
            print("管理员用户创建成功！")
        
        print("数据库表创建成功！")

if __name__ == '__main__':
    init_database()