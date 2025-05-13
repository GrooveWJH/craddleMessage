from flask import Flask
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
import logging
import os
from config.config import Config
from models import db

# 全局定义DEBUG_MODE，便于外部文件引用，不应当修改此处状态，因为只是默认初始化，将被覆盖
DEBUG_MODE = False

# 初始化应用
def create_app(config=None):
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(Config)
    if config:
        app.config.update(config)
    
    # 读取配置中的DEBUG设置
    global DEBUG_MODE
    DEBUG_MODE = app.config.get('DEBUG', False)
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化登录管理器
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # 初始化JWT
    jwt = JWTManager(app)
    
    # 配置日志
    if not os.path.exists(Config.LOG_FOLDER):
        os.makedirs(Config.LOG_FOLDER)
    
    logging.basicConfig(
        filename=os.path.join(Config.LOG_FOLDER, 'app.log'),
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('app')
    
    # 创建一个开发环境的控制台日志处理器
    if DEBUG_MODE:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
        logger.info("调试模式已启用，日志将同时输出到控制台")
    
    # 注册JWT错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.error(f"JWT令牌已过期: {jwt_payload}")
        return {'error': "令牌已过期，请重新登录"}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        logger.error(f"无效的JWT令牌: {error_string}")
        return {'error': "无效的身份验证令牌"}, 422
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        logger.error(f"缺少JWT令牌: {error_string}")
        return {'error': "请求缺少身份验证令牌"}, 401
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # 导入蓝图
    from routes.auth import auth_bp
    from routes.api import api_bp
    from routes.main import main_bp
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(main_bp, url_prefix='')
    
    # 设置应用的调试标志
    app.debug = DEBUG_MODE
    logger.info(f"应用调试模式已设置为: {DEBUG_MODE}")
    
    return app

# 创建默认应用实例
app = create_app()

if __name__ == '__main__':
    # 使用应用的DEBUG配置
    app.run(port=3001, debug=DEBUG_MODE)