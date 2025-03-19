import os
import sys

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

from app import db, create_app
from app import User, Message, Recipient, StatusLog
from datetime import datetime

def create_test_data():
    app = create_app()
    with app.app_context():
        # 创建测试用户
        test_user = User(
            username='test_user',
            email='test@example.com',
            password='test123'
        )
        db.session.add(test_user)
        db.session.commit()  # 先提交用户以获取 ID
        
        # 创建测试留言
        test_message = Message(
            user_id=test_user.id,  # 使用实际的用户 ID
            content='这是一条测试留言',
            media_type='text',
            created_at=datetime.now(),
            trigger_condition='time'
        )
        db.session.add(test_message)
        db.session.commit()  # 先提交消息以获取 ID
        
        # 创建测试接收人
        test_recipient = Recipient(
            message_id=test_message.id,  # 使用实际的消息 ID
            name='测试接收人',
            contact='recipient@example.com',
            contact_type='email'
        )
        db.session.add(test_recipient)
        
        # 创建测试状态记录
        test_status = StatusLog(
            message_id=test_message.id,  # 使用实际的消息 ID
            status='created',
            created_at=datetime.now(),
            details='留言创建成功'
        )
        db.session.add(test_status)
        
        # 提交所有更改
        db.session.commit()
        print("测试数据创建成功！")

if __name__ == '__main__':
    create_test_data()