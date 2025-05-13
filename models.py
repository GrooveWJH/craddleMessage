from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta, UTC
from cryptography.fernet import Fernet
import base64
import os

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    messages = db.relationship('Message', backref='user', lazy=True)

    def get_id(self):
        return str(self.id)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    encrypted_content = db.Column(db.Text, nullable=False)  # 加密后的内容
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    initial_delay_months = db.Column(db.Integer, nullable=False)
    next_warning_date = db.Column(db.DateTime, nullable=False)
    warning_level = db.Column(db.Integer, default=0)  # 0-5: 0=未开始, 1-4=预警级别, 5=最终预警
    is_active = db.Column(db.Boolean, default=True)
    revocation_key = db.Column(db.String(255), unique=True)
    encryption_key = db.Column(db.String(255), nullable=True)  # 存储用于加密内容的密钥
    recipients = db.relationship('Recipient', backref='message', lazy=True, cascade="all, delete-orphan")
    status_logs = db.relationship('StatusLog', backref='message', lazy=True, cascade="all, delete-orphan")
    
    def __init__(self, user_id, content, initial_delay_months, next_warning_date):
        self.user_id = user_id
        self.initial_delay_months = initial_delay_months
        self.next_warning_date = next_warning_date
        
        # 生成密钥并加密内容
        self.generate_revocation_key(content)

    def generate_revocation_key(self, content=None):
        """生成撤销密钥并加密内容（如果提供）"""
        # 生成一个加密密钥
        key = Fernet.generate_key()
        self.revocation_key = base64.urlsafe_b64encode(key).decode('utf-8')
        
        # 如果提供了内容，使用密钥加密
        if content:
            self.encrypt_content(content, key)
        
        return self.revocation_key
    
    def encrypt_content(self, content, key=None):
        """加密留言内容"""
        if key is None:
            # 如果没有提供密钥，使用已存储的撤销密钥
            key = base64.urlsafe_b64decode(self.revocation_key.encode('utf-8'))
        
        # 创建Fernet实例并加密
        fernet = Fernet(key)
        encrypted = fernet.encrypt(content.encode('utf-8'))
        
        # 存储加密后的内容
        self.encrypted_content = encrypted.decode('utf-8')
    
    def decrypt_content(self, key=None):
        """解密留言内容"""
        try:
            if key is None:
                # 使用撤销密钥解密
                key = base64.urlsafe_b64decode(self.revocation_key.encode('utf-8'))
            else:
                # 如果提供了外部密钥字符串，转换为二进制密钥
                key = base64.urlsafe_b64decode(key.encode('utf-8'))
            
            # 创建Fernet实例并解密
            fernet = Fernet(key)
            decrypted = fernet.decrypt(self.encrypted_content.encode('utf-8'))
            
            return decrypted.decode('utf-8')
        except Exception as e:
            # 解密失败
            return None
    
    def get_content(self, user=None):
        """获取内容，管理员可以直接查看，其他用户需要密钥"""
        # 如果是管理员账户，总是返回解密内容
        if user and user.username == "admin":
            return self.decrypt_content()
        # 否则需要密钥才能解密
        return None

    def calculate_warning_schedule(self):
        """计算预警时间表"""
        base_date = self.created_at
        schedule = {
            'first_warning': base_date + timedelta(days=self.initial_delay_months * 30),
            'second_warning': base_date + timedelta(days=(self.initial_delay_months * 30) + 30),
            'third_warning': base_date + timedelta(days=(self.initial_delay_months * 30) + 60),
            'fourth_warning': base_date + timedelta(days=(self.initial_delay_months * 30) + 67),
            'final_warning': base_date + timedelta(days=(self.initial_delay_months * 30) + 68),
            'final_delivery': base_date + timedelta(days=(self.initial_delay_months * 30) + 69)
        }
        return schedule

    def reset_warning_cycle(self):
        """重置预警周期"""
        self.warning_level = 0
        self.next_warning_date = self.created_at + timedelta(days=self.initial_delay_months * 30)
        
    def advance_warning_level(self):
        """推进预警等级"""
        self.warning_level += 1
        if self.warning_level == 1:  # 第一次预警后等待1个月
            self.next_warning_date = datetime.now(UTC) + timedelta(days=30)
        elif self.warning_level == 2:  # 第二次预警后等待1个月
            self.next_warning_date = datetime.now(UTC) + timedelta(days=30)
        elif self.warning_level == 3:  # 第三次预警后等待1周
            self.next_warning_date = datetime.now(UTC) + timedelta(days=7)
        elif self.warning_level == 4:  # 第四次预警后等待1天
            self.next_warning_date = datetime.now(UTC) + timedelta(days=1)
        elif self.warning_level == 5:  # 最终预警，准备发送
            self.next_warning_date = datetime.now(UTC) + timedelta(hours=24)

class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    contact_type = db.Column(db.String(20), nullable=False)

class StatusLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # WARNING_1, WARNING_2, WARNING_3, WARNING_4, WARNING_FINAL, DELIVERED
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    details = db.Column(db.Text)
    response = db.Column(db.String(20), nullable=True)  # RESET, CONTINUE, null