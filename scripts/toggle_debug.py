#!/usr/bin/env python3
import os
import sys
import yaml

# 获取项目根目录
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(ROOT_DIR, 'config', 'app_config.yaml')

def toggle_debug():
    """切换调试模式"""
    # 读取配置文件
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"错误：无法读取配置文件: {e}")
        return
    
    # 获取当前设置
    current_value = config.get('app', {}).get('debug', False)
    
    # 切换值
    new_value = not current_value
    
    # 确保app部分存在
    if 'app' not in config:
        config['app'] = {}
    
    # 更新配置
    config['app']['debug'] = new_value
    
    # 写回文件
    try:
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"调试模式已切换: {current_value} -> {new_value}")
        print(f"重启应用后生效")
    except Exception as e:
        print(f"错误：无法写入配置文件: {e}")

def check_debug():
    """查看当前调试模式状态"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)
        
        current_value = config.get('app', {}).get('debug', False)
        status = "开启" if current_value else "关闭"
        print(f"当前调试模式: {status} ({current_value})")
    except Exception as e:
        print(f"错误：无法读取配置文件: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        check_debug()
    else:
        toggle_debug() 