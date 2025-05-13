from flask import Blueprint, render_template, redirect, url_for, jsonify, flash, request, current_app
from flask_login import current_user, login_required
import logging
from datetime import datetime
import os
import shutil
import time

from models import db, User, Message, Recipient, StatusLog

# 创建主要路由蓝图
main_bp = Blueprint('main', __name__)

# 获取logger
logger = logging.getLogger('app')

@main_bp.route('/')
def index():
    """首页路由"""
    # 如果开启了调试模式且用户未登录，则重定向到调试登录页面
    if current_app.debug and not current_user.is_authenticated:
        return redirect(url_for('auth.debug_page'))
    return render_template('index.html')

@main_bp.route('/admin')
@login_required
def admin():
    """管理后台路由，需要登录"""
    # 验证是否为管理员账户
    if current_user.username != "admin":
        flash("您没有权限访问管理后台", "danger")
        return redirect(url_for('main.index'))
    
    # 获取所有用户
    users = User.query.all()
    
    # 获取所有留言并解密内容
    messages = Message.query.all()
    
    # 为管理员解密所有留言内容
    decrypted_messages = []
    for message in messages:
        try:
            # 解密留言内容
            content = message.decrypt_content()
            user = User.query.get(message.user_id)
            
            # 获取留言的接收人和状态记录
            recipients = Recipient.query.filter_by(message_id=message.id).all()
            status_logs = StatusLog.query.filter_by(message_id=message.id).order_by(StatusLog.created_at.desc()).all()
            
            decrypted_messages.append({
                'id': message.id,
                'user': user.username if user else "未知用户",
                'content': content,
                'created_at': message.created_at,
                'initial_delay_months': message.initial_delay_months,
                'next_warning_date': message.next_warning_date,
                'warning_level': message.warning_level,
                'is_active': message.is_active,
                'revocation_key': message.revocation_key,
                'recipients': recipients,
                'status_logs': status_logs
            })
        except Exception as e:
            # 如果解密失败，记录错误但继续处理其他留言
            logger.error(f"解密留言 {message.id} 失败: {str(e)}")
    
    # 计算统计数据
    stats = {
        'user_count': User.query.count(),
        'message_count': Message.query.count(),
        'active_message_count': Message.query.filter_by(is_active=True).count(),
        'warning_levels': {
            'level_0': Message.query.filter_by(warning_level=0, is_active=True).count(),
            'level_1': Message.query.filter_by(warning_level=1, is_active=True).count(),
            'level_2': Message.query.filter_by(warning_level=2, is_active=True).count(),
            'level_3': Message.query.filter_by(warning_level=3, is_active=True).count(),
            'level_4': Message.query.filter_by(warning_level=4, is_active=True).count(),
            'level_5': Message.query.filter_by(warning_level=5, is_active=True).count(),
        }
    }
    
    return render_template('admin.html', users=users, messages=decrypted_messages, stats=stats)

@main_bp.route('/api/admin/messages')
@login_required
def admin_messages_api():
    """管理后台API：获取所有留言数据"""
    if current_user.username != "admin":
        return jsonify({"error": "权限不足"}), 403
    
    # 获取所有留言
    messages = Message.query.all()
    message_list = []
    
    for message in messages:
        try:
            # 解密留言内容
            content = message.decrypt_content()
            user = User.query.get(message.user_id)
            
            # 获取接收人信息
            recipients = []
            for recipient in message.recipients:
                recipients.append({
                    'name': recipient.name,
                    'contact': recipient.contact,
                    'contact_type': recipient.contact_type
                })
            
            message_list.append({
                'id': message.id,
                'user': user.username if user else "未知用户",
                'content': content,
                'created_at': message.created_at.isoformat(),
                'initial_delay_months': message.initial_delay_months,
                'next_warning_date': message.next_warning_date.isoformat() if message.next_warning_date else None,
                'warning_level': message.warning_level,
                'is_active': message.is_active,
                'revocation_key': message.revocation_key,
                'recipients': recipients
            })
        except Exception as e:
            # 错误处理
            logger.error(f"处理留言 {message.id} 时出错: {str(e)}")
    
    return jsonify(message_list)

@main_bp.route('/api/admin/backup-db', methods=['POST'])
@login_required
def backup_database():
    """管理后台API：备份数据库"""
    if current_user.username != "admin":
        return jsonify({"error": "权限不足"}), 403
    
    try:
        # 创建备份目录
        backup_dir = os.path.join(current_app.config['_base_dir'], 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # 生成备份文件名，格式为：backup_YYYY-MM-DD_HH-MM-SS.sql
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"backup_{timestamp}.sql"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # 获取数据库URL
        db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
        # 解析URL获取用户名、密码和数据库名
        # mysql+pymysql://root:302811055wjhhz@localhost/cradle_message
        parts = db_url.replace('mysql+pymysql://', '').split('@')
        auth = parts[0].split(':')
        db_user = auth[0]
        db_pass = auth[1]
        host_db = parts[1].split('/')
        db_host = host_db[0]
        db_name = host_db[1]
        
        # 构建mysqldump命令
        command = f"mysqldump -u {db_user} -p{db_pass} -h {db_host} {db_name} > {backup_path}"
        
        # 执行备份
        exit_code = os.system(command)
        
        if exit_code != 0:
            logger.error(f"数据库备份失败，退出码: {exit_code}")
            return jsonify({
                "success": False,
                "error": f"数据库备份失败，命令返回错误码: {exit_code}"
            }), 500
        
        # 获取文件大小
        file_size = os.path.getsize(backup_path)
        human_size = f"{file_size / 1024 / 1024:.2f} MB" if file_size > 1024 * 1024 else f"{file_size / 1024:.2f} KB"
        
        logger.info(f"数据库备份成功，文件: {backup_path}，大小: {human_size}")
        
        return jsonify({
            "success": True,
            "filename": backup_filename,
            "path": backup_path,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "size": human_size
        })
        
    except Exception as e:
        logger.error(f"数据库备份失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"数据库备份失败: {str(e)}"
        }), 500

@main_bp.route('/api/admin/user/<int:user_id>')
@login_required
def get_user_details(user_id):
    """管理后台API：获取用户详情"""
    if current_user.username != "admin":
        return jsonify({"error": "权限不足"}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        
        # 获取用户留言
        messages = []
        for message in user.messages:
            try:
                # 解密留言内容
                content = message.decrypt_content()
                messages.append({
                    'id': message.id,
                    'content': content,
                    'created_at': message.created_at.strftime("%Y-%m-%d %H:%M"),
                    'is_active': message.is_active,
                    'warning_level': message.warning_level
                })
            except Exception as e:
                logger.error(f"解密用户 {user_id} 的留言 {message.id} 失败: {str(e)}")
                # 添加未解密的留言信息
                messages.append({
                    'id': message.id,
                    'content': "[无法解密]",
                    'created_at': message.created_at.strftime("%Y-%m-%d %H:%M"),
                    'is_active': message.is_active,
                    'warning_level': message.warning_level
                })
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.strftime("%Y-%m-%d %H:%M"),
            'messages': messages
        })
        
    except Exception as e:
        logger.error(f"获取用户详情失败: {str(e)}")
        return jsonify({
            "error": f"获取用户详情失败: {str(e)}"
        }), 500
