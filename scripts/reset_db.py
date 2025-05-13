import sys
import os
import hashlib
from datetime import datetime, UTC

# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from app import app, create_app
from models import db, User
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash

def reset_database():
    print("========= 数据库重置工具 =========")
    print("警告：此操作将删除所有现有数据并重新创建数据库！")
    confirm = input("输入 'YES' 确认操作: ")
    
    if confirm != "YES":
        print("操作已取消！")
        return
    
    # 创建数据库连接（不指定数据库名）
    engine = create_engine('mysql+pymysql://root:302811055wjhhz@localhost/')
    
    # 删除现有数据库（如果存在）
    with engine.connect() as conn:
        conn.execute(text("DROP DATABASE IF EXISTS cradle_message"))
        conn.commit()
        print("已删除现有数据库")
        
        # 创建新数据库
        conn.execute(text("CREATE DATABASE cradle_message CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        conn.commit()
        print("已创建新数据库")
    
    # 使用应用上下文创建表
    app = create_app()
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("已创建所有数据库表")
        
        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password=generate_password_hash("123123"),
            created_at=datetime.now(UTC)
        )
        db.session.add(admin_user)
        
        # 创建测试用户
        test_user = User(
            username="testuser",
            email="test@example.com",
            password=generate_password_hash("123123"),
            created_at=datetime.now(UTC)
        )
        db.session.add(test_user)
        
        db.session.commit()
        print("已创建管理员用户 (admin/123123) 和测试用户 (testuser/123123)")
        
    print("数据库重置成功！")
    print("=================================")

if __name__ == '__main__':
    reset_database() 