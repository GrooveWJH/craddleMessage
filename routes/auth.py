from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt_identity
import hashlib
import logging
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

# 获取logger
logger = logging.getLogger('app')

# 登录路由
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 调试模式下GET请求直接重定向到调试登录页面
    if current_app.debug and request.method == 'GET':
        return redirect(url_for('auth.debug_page'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        # 使用werkzeug的check_password_hash验证密码
        if user and check_password_hash(user.password, password):
            login_user(user)
            # 生成JWT令牌并返回给客户端 - 确保用户ID是字符串
            access_token = create_access_token(identity=str(user.id))
            logger.info(f'用户 {username} 登录成功，生成JWT令牌')
            
            response = redirect(url_for('main.index'))
            response.set_cookie('jwt_token', access_token, httponly=False)  # 设置为非httponly以便JS读取
            return response
        else:
            flash('用户名或密码错误', 'danger')
            logger.warning(f'用户 {username} 登录失败')
    
    return render_template('login.html')

# 注册路由
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 检查两次密码是否一致
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return render_template('register.html')
        
        # 检查用户名格式
        if len(username) < 3 or len(username) > 20:
            flash('用户名长度必须在3-20个字符之间', 'danger')
            return render_template('register.html')
            
        if not username.isalnum():
            flash('用户名只能包含字母和数字', 'danger')
            return render_template('register.html')
        
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('用户名已存在，请选择其他用户名', 'danger')
            return render_template('register.html')
        
        # 检查邮箱是否已存在
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('该邮箱已被注册', 'danger')
            return render_template('register.html')
        
        # 验证邮箱格式
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(email):
            flash('请输入有效的电子邮箱', 'danger')
            return render_template('register.html')
        
        # 密码强度验证
        if len(password) < 6:
            flash('密码长度不能少于6个字符', 'danger')
            return render_template('register.html')
        
        # 使用werkzeug生成密码哈希
        hashed_password = generate_password_hash(password)
        
        # 创建新用户
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        logger.info(f'新用户注册成功: {username}')
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

# 登出路由
@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    logger.info(f'用户 {username} 登出成功')
    
    # 创建响应并清除debug_login cookie
    response = redirect(url_for('main.index'))
    response.set_cookie('debug_login', '', expires=0)  # 清除cookie
    response.set_cookie('jwt_token', '', expires=0)  # 清除jwt cookie
    return response

# 调试模式路由
@auth_bp.route('/debug')
def debug_page():
    if not current_app.debug:
        return redirect(url_for('main.index'))
    
    return render_template('debug_login.html')

# 调试快速登录路由
@auth_bp.route('/debug_login/<mode>')
def debug_login(mode):
    if not current_app.debug:
        return redirect(url_for('main.index'))
    
    # 清除当前用户会话
    if current_user.is_authenticated:
        logout_user()
    
    response = None
    
    if mode == 'admin':
        # 检查admin用户是否存在，如不存在则创建
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            hashed_password = generate_password_hash('admin123')
            admin = User(username='admin', email='admin@example.com', password=hashed_password)
            db.session.add(admin)
            db.session.commit()
            logger.info(f"创建管理员用户: ID={admin.id}")
        else:
            logger.info(f"使用现有管理员用户: ID={admin.id}")
        
        login_user(admin)
        # 生成JWT令牌 - 确保用户ID是字符串
        access_token = create_access_token(identity=str(admin.id))
        logger.info(f'调试模式: 使用管理员账户登录(ID={admin.id})，生成JWT令牌')
        response = redirect(url_for('main.admin'))  # 直接进入管理后台
        response.set_cookie('debug_login', 'admin')
        response.set_cookie('jwt_token', access_token, httponly=False)  # 设置为非httponly以便JS读取
        
    elif mode == 'test':
        # 先检查是否有testuser用户
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            # 再检查是否有testAccount1用户
            test_user = User.query.filter_by(username='testAccount1').first()
            
            # 再检查是否有相同邮箱的用户
            if not test_user:
                email_user = User.query.filter_by(email='test@example.com').first()
                if email_user:
                    # 如果有相同邮箱的用户，使用该用户
                    test_user = email_user
                    logger.info(f"使用现有邮箱用户: ID={test_user.id}, 用户名={test_user.username}")
        
        # 如果没有找到任何用户，创建新的测试用户
        if not test_user:
            hashed_password = generate_password_hash('test123123')
            test_user = User(username='testuser', email='testuser@example.com', password=hashed_password)
            db.session.add(test_user)
            db.session.commit()
            logger.info(f"创建测试用户: ID={test_user.id}")
        else:
            logger.info(f"使用现有测试用户: ID={test_user.id}, 用户名={test_user.username}")
        
        login_user(test_user)
        # 生成JWT令牌 - 确保用户ID是字符串
        access_token = create_access_token(identity=str(test_user.id))
        logger.info(f'调试模式: 使用测试账户登录(ID={test_user.id})，生成JWT令牌: {access_token[:10]}...')
        response = redirect(url_for('main.index'))
        response.set_cookie('debug_login', 'test')
        response.set_cookie('jwt_token', access_token, httponly=False)  # 设置为非httponly以便JS读取
    
    return response

# JWT测试端点
@auth_bp.route('/api/test_jwt')
def test_jwt():
    """测试JWT令牌解析的辅助端点"""
    auth_header = request.headers.get('Authorization', '')
    if current_app.debug:
        logger.info(f"测试JWT端点收到请求，Authorization头: {auth_header}")
    
    if not auth_header.startswith('Bearer '):
        return jsonify({"error": "缺少Bearer令牌"}), 401
    
    token = auth_header.split('Bearer ')[1]
    try:
        # 手动验证令牌
        verify_jwt_in_request()
        # 获取身份
        user_id = get_jwt_identity()
        logger.info(f"JWT解析成功，用户身份(字符串): {user_id}, 类型: {type(user_id)}")
        
        # 转换为整数用于数据库查询
        try:
            user_db_id = int(user_id)
            user = User.query.get(user_db_id)
            if user:
                return jsonify({
                    "success": True,
                    "user_id": user_id,
                    "username": user.username
                })
            else:
                return jsonify({"error": f"找不到ID为{user_id}的用户"}), 404
        except ValueError:
            logger.error(f"无法将用户ID转换为整数: {user_id}")
            return jsonify({"error": "用户ID格式无效"}), 400
            
    except Exception as e:
        logger.error(f"JWT解析错误: {str(e)}")
        return jsonify({"error": str(e)}), 401
