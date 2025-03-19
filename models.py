from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import base64

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='user', lazy=True)

    def get_id(self):
        return str(self.id)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    initial_delay_months = db.Column(db.Integer, nullable=False)
    next_warning_date = db.Column(db.DateTime, nullable=False)
    warning_level = db.Column(db.Integer, default=0)  # 0-5: 0=未开始, 1-4=预警级别, 5=最终预警
    is_active = db.Column(db.Boolean, default=True)
    revocation_key = db.Column(db.String(255), unique=True)
    recipients = db.relationship('Recipient', backref='message', lazy=True)
    status_logs = db.relationship('StatusLog', backref='message', lazy=True)

    def generate_revocation_key(self):
        key = Fernet.generate_key()
        self.revocation_key = base64.urlsafe_b64encode(key).decode('utf-8')
        return self.revocation_key

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
            self.next_warning_date = datetime.utcnow() + timedelta(days=30)
        elif self.warning_level == 2:  # 第二次预警后等待1个月
            self.next_warning_date = datetime.utcnow() + timedelta(days=30)
        elif self.warning_level == 3:  # 第三次预警后等待1周
            self.next_warning_date = datetime.utcnow() + timedelta(days=7)
        elif self.warning_level == 4:  # 第四次预警后等待1天
            self.next_warning_date = datetime.utcnow() + timedelta(days=1)
        elif self.warning_level == 5:  # 最终预警，准备发送
            self.next_warning_date = datetime.utcnow() + timedelta(hours=24)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)
    response = db.Column(db.String(20), nullable=True)  # RESET, CONTINUE, null