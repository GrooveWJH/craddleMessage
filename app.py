from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import logging
import os
from config.config import Config
from models import db, User, Message, Recipient, StatusLog

# 初始化应用
app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库
db.init_app(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 初始化JWT
jwt = JWTManager(app)

# 配置日志
logging.basicConfig(
    filename=os.path.join(Config.LOG_FOLDER, 'app.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 路由定义
@app.route('/')
def index():
    logger.info('访问主页')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:  # 实际应用中应该使用密码哈希
            login_user(user)
            logger.info(f'用户 {username} 登录成功')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
            logger.warning(f'用户 {username} 登录失败')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    logger.info(f'用户 {username} 登出成功')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    if current_user.username != Config.ADMIN_USERNAME:
        logger.warning(f'用户 {current_user.username} 尝试访问管理后台')
        return redirect(url_for('index'))
    
    # 获取统计数据
    stats = {
        'userCount': User.query.count(),
        'messageCount': Message.query.count(),
        'activeMessages': Message.query.filter_by(is_active=True).count(),
        'warningLevels': {
            'level1': Message.query.filter_by(warning_level=1, is_active=True).count(),
            'level2': Message.query.filter_by(warning_level=2, is_active=True).count(),
            'level3': Message.query.filter_by(warning_level=3, is_active=True).count(),
            'level4': Message.query.filter_by(warning_level=4, is_active=True).count(),
            'level5': Message.query.filter_by(warning_level=5, is_active=True).count()
        }
    }
    
    logger.info(f'管理员 {current_user.username} 访问管理后台')
    return render_template('admin.html', stats=stats)

@app.route('/api/message', methods=['POST'])
@jwt_required()
def create_message():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        message = Message(
            user_id=user_id,
            content=data['content'],
            initial_delay_months=data['initial_delay_months'],
            next_warning_date=datetime.utcnow() + timedelta(days=data['initial_delay_months'] * 30)
        )
        
        # 生成撤销密钥
        revocation_key = message.generate_revocation_key()
        
        # 添加接收人
        for recipient_data in data['recipients']:
            recipient = Recipient(
                name=recipient_data['name'],
                contact=recipient_data['contact'],
                contact_type=recipient_data['contact_type']
            )
            message.recipients.append(recipient)
        
        db.session.add(message)
        db.session.commit()
        
        # 计算预警时间表
        warning_schedule = message.calculate_warning_schedule()
        
        logger.info(f'用户 {user_id} 创建了新留言 {message.id}')
        return jsonify({
            'message': '留言创建成功',
            'revocation_key': revocation_key,
            'warning_schedule': warning_schedule
        }), 201
        
    except Exception as e:
        logger.error(f'创建留言失败: {str(e)}')
        return jsonify({'error': '创建留言失败'}), 500

@app.route('/api/message/revoke/<revocation_key>', methods=['POST'])
def revoke_message(revocation_key):
    try:
        message = Message.query.filter_by(revocation_key=revocation_key, is_active=True).first()
        if not message:
            return jsonify({'error': '无效的撤销密钥或留言已被撤销'}), 404
        
        message.is_active = False
        status_log = StatusLog(
            message_id=message.id,
            status='REVOKED',
            details='用户撤销留言'
        )
        db.session.add(status_log)
        db.session.commit()
        
        logger.info(f'留言 {message.id} 被撤销')
        return jsonify({'message': '留言撤销成功'}), 200
        
    except Exception as e:
        logger.error(f'撤销留言失败: {str(e)}')
        return jsonify({'error': '撤销留言失败'}), 500

@app.route('/api/message/<int:message_id>/warning/response', methods=['POST'])
@jwt_required()
def handle_warning_response(message_id):
    try:
        data = request.get_json()
        response = data.get('response')  # RESET 或 CONTINUE
        
        message = Message.query.get_or_404(message_id)
        if not message.is_active:
            return jsonify({'error': '留言已失效'}), 400
            
        if response == 'RESET':
            message.reset_warning_cycle()
            status = 'WARNING_RESET'
            details = '用户选择重置预警周期'
        else:  # CONTINUE
            message.advance_warning_level()
            status = f'WARNING_{message.warning_level}'
            details = f'用户选择继续第{message.warning_level}级预警'
            
        status_log = StatusLog(
            message_id=message.id,
            status=status,
            details=details,
            response=response
        )
        db.session.add(status_log)
        db.session.commit()
        
        logger.info(f'留言 {message_id} 的预警响应已处理: {response}')
        return jsonify({'message': '预警响应处理成功'}), 200
        
    except Exception as e:
        logger.error(f'处理预警响应失败: {str(e)}')
        return jsonify({'error': '处理预警响应失败'}), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)