import os
import yaml
from datetime import timedelta

class Config:
    # 确定配置文件路径
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _config_file = os.path.join(_base_dir, 'config', 'app_config.yaml')
    
    # 加载YAML配置
    try:
        with open(_config_file, 'r') as f:
            _config = yaml.safe_load(f)
    except Exception as e:
        print(f"无法加载配置文件: {e}")
        _config = {}
    
    # 基础配置
    SECRET_KEY = _config.get('app', {}).get('secret_key', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = _config.get('database', {}).get('url', 
        'mysql+pymysql://root:302811055wjhhz@localhost/cradle_message')
    SQLALCHEMY_TRACK_MODIFICATIONS = _config.get('database', {}).get('track_modifications', False)
    
    # 调试模式配置
    DEBUG = _config.get('app', {}).get('debug', False)
    
    # JWT配置
    JWT_SECRET_KEY = _config.get('jwt', {}).get('secret_key', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=_config.get('jwt', {}).get('access_token_expires_hours', 1))
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(_base_dir, 'uploads')
    MAX_CONTENT_LENGTH = _config.get('uploads', {}).get('max_content_length', 16 * 1024 * 1024)  # 16MB
    
    # 日志配置
    LOG_FOLDER = os.path.join(_base_dir, 'logs')
    
    # 预警时间配置（单位：天）
    ALERT_INTERVALS = {
        'first': _config.get('alerts', {}).get('first', 90),    # 3个月
        'second': _config.get('alerts', {}).get('second', 30),  # 1个月
        'third': _config.get('alerts', {}).get('third', 30),    # 1个月
        'fourth': _config.get('alerts', {}).get('fourth', 7),   # 1周
        'final': _config.get('alerts', {}).get('final', 1)      # 1天
    }
    
    # 管理员配置
    ADMIN_USERNAME = _config.get('admin', {}).get('username', 'admin')
    ADMIN_PASSWORD = _config.get('admin', {}).get('password', 'admin123')
    
    # 加密配置
    ENCRYPTION_KEY = _config.get('encryption', {}).get('key', 'encryption-key-32-bytes-long')
    
    @staticmethod
    def init_app(app):
        # 创建必要的目录
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.LOG_FOLDER, exist_ok=True)
    
    @classmethod
    def update_config(cls, new_config):
        """更新YAML配置文件"""
        try:
            # 先读取当前配置
            with open(cls._config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # 更新配置
            for section, values in new_config.items():
                if section not in config:
                    config[section] = {}
                    
                if isinstance(values, dict):
                    for key, value in values.items():
                        config[section][key] = value
                else:
                    config[section] = values
            
            # 写回文件
            with open(cls._config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
            return True
        except Exception as e:
            print(f"更新配置失败: {e}")
            return False