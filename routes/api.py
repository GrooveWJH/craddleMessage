from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime, timedelta, UTC
import logging
import json
import traceback

from models import db, User, Message, Recipient, StatusLog

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 获取logger
logger = logging.getLogger('app')

@api_bp.route('/message', methods=['POST'])
@jwt_required()
def create_message():
    try:
        # 详细日志记录
        auth_header = request.headers.get('Authorization', '')
        if current_app.debug:
            logger.info(f"收到留言创建请求，Authorization头: {auth_header}")
            logger.info(f"请求内容: {request.data.decode('utf-8')}")
        
        # 尝试解析用户ID
        try:
            user_id_str = get_jwt_identity()
            logger.info(f"JWT解析获取的用户ID(字符串): {user_id_str}")
            
            # 将字符串ID转换为整数以便数据库查询
            try:
                user_id = int(user_id_str)
                user = User.query.get(user_id)
                if user:
                    logger.info(f"JWT解析成功，用户ID: {user_id}, 用户名: {user.username}")
                else:
                    logger.error(f"找不到ID为{user_id}的用户")
                    return jsonify({"error": "用户不存在"}), 404
            except ValueError:
                logger.error(f"无法将用户ID转换为整数: {user_id_str}")
                return jsonify({"error": "用户ID格式无效"}), 400
                
        except Exception as e:
            logger.error(f"JWT解析错误: {str(e)}")
            return jsonify({"error": "身份验证失败: " + str(e)}), 401
        
        # 解析JSON数据
        try:
            data = request.get_json()
            if data is None:
                logger.error('创建留言失败: 无效的JSON数据')
                return jsonify({'error': '无效的请求数据格式'}), 400
            
            if current_app.debug:
                logger.info(f"解析的JSON数据: {json.dumps(data)}")
        except Exception as e:
            logger.error(f"JSON解析错误: {str(e)}")
            return jsonify({"error": "无法解析请求数据: " + str(e)}), 400
        
        # 验证必要字段
        required_fields = ['content', 'initial_delay_months', 'recipients']
        for field in required_fields:
            if field not in data:
                logger.error(f'创建留言失败: 缺少必要字段 {field}')
                return jsonify({'error': f'缺少必要字段: {field}'}), 400
                
        if not data['recipients']:
            logger.error('创建留言失败: 未提供接收人')
            return jsonify({'error': '至少需要一个接收人'}), 400
        
        # 创建留言记录
        try:
            # 创建新的留言对象，传入内容和其他基本信息
            message = Message(
                user_id=user_id,
                content=data['content'],
                initial_delay_months=data['initial_delay_months'],
                next_warning_date=datetime.now(UTC) + timedelta(days=data['initial_delay_months'] * 30)
            )
            
            # 获取生成的撤销密钥
            revocation_key = message.revocation_key
            
            # 添加接收人
            for recipient_data in data['recipients']:
                if 'name' not in recipient_data or 'contact' not in recipient_data or 'contact_type' not in recipient_data:
                    logger.error('创建留言失败: 接收人信息不完整')
                    return jsonify({'error': '接收人信息不完整'}), 400
                    
                recipient = Recipient(
                    name=recipient_data['name'],
                    contact=recipient_data['contact'],
                    contact_type=recipient_data['contact_type']
                )
                message.recipients.append(recipient)
                
            logger.info(f"准备保存留言，用户ID: {user_id}, 内容长度: {len(data['content'])}, 接收人数: {len(data['recipients'])}")
            
            # 保存到数据库
            db.session.add(message)
            db.session.commit()
            
            # 计算预警时间表
            warning_schedule = message.calculate_warning_schedule()
            
            logger.info(f'用户 {user_id} 创建了新留言 {message.id}')
            return jsonify({
                'message': '留言创建成功',
                'message_id': message.id,
                'revocation_key': revocation_key,
                'warning_schedule': warning_schedule
            }), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"数据库操作错误: {str(e)}")
            return jsonify({"error": "数据库操作失败: " + str(e)}), 500
        
    except Exception as e:
        logger.error(f'创建留言失败: {str(e)}')
        # 在调试模式下记录更详细的错误信息
        if current_app.debug:
            error_trace = traceback.format_exc()
            logger.error(f'错误详情: {error_trace}')
        return jsonify({'error': '创建留言失败，请重试: ' + str(e)}), 500

@api_bp.route('/message/revoke/<revocation_key>', methods=['POST'])
def revoke_message(revocation_key):
    try:
        message = Message.query.filter_by(revocation_key=revocation_key, is_active=True).first()
        if not message:
            return jsonify({'error': '无效的撤销密钥或留言已被撤销'}), 404
        
        # 记录被删除消息的ID用于日志
        message_id = message.id
        user_id = message.user_id
        
        try:
            # 直接删除留言及其关联数据
            db.session.delete(message)
            db.session.commit()
            
            logger.info(f'留言 {message_id} 被彻底删除，用户ID: {user_id}')
            return jsonify({'message': '留言撤销成功并已删除所有相关数据'}), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'删除留言记录失败: {str(e)}')
            
            # 如果删除失败，则退回到仅标记为非活跃
            message = Message.query.get(message_id)
            if message:
                message.is_active = False
                status_log = StatusLog(
                    message_id=message.id,
                    status='REVOKED',
                    details='用户撤销留言（删除失败）'
                )
                db.session.add(status_log)
                db.session.commit()
                logger.info(f'留言 {message_id} 已标记为非活跃（删除失败）')
                return jsonify({'message': '留言已撤销，但无法完全删除数据'}), 200
            else:
                return jsonify({'error': '撤销留言失败：' + str(e)}), 500
    
    except Exception as e:
        logger.error(f'撤销留言失败: {str(e)}')
        return jsonify({'error': '撤销留言失败'}), 500

@api_bp.route('/message/view/<revocation_key>', methods=['GET'])
def view_message(revocation_key):
    try:
        message = Message.query.filter_by(revocation_key=revocation_key).first()
        if not message:
            return jsonify({'error': '无效的密钥或留言不存在'}), 404
        
        # 使用撤销密钥解密留言内容
        content = message.decrypt_content(revocation_key)
        if content is None:
            return jsonify({'error': '无法解密留言内容，密钥可能不正确'}), 400
        
        # 获取接收人信息
        recipients = []
        for recipient in message.recipients:
            recipients.append({
                'name': recipient.name,
                'contact': recipient.contact,
                'contact_type': recipient.contact_type
            })
        
        # 查询留言状态
        status = "活跃" if message.is_active else "已撤销"
        warning_level = message.warning_level
        next_warning = message.next_warning_date.isoformat() if message.next_warning_date else None
        
        # 构建响应数据
        response_data = {
            'message_id': message.id,
            'content': content,
            'created_at': message.created_at.isoformat(),
            'initial_delay_months': message.initial_delay_months,
            'status': status,
            'warning_level': warning_level,
            'next_warning_date': next_warning,
            'recipients': recipients
        }
        
        logger.info(f'留言 {message.id} 被查看，使用密钥: {revocation_key[:10]}...')
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f'查看留言失败: {str(e)}')
        return jsonify({'error': '查看留言失败：' + str(e)}), 500

@api_bp.route('/message/<int:message_id>/warning/response', methods=['POST'])
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

@api_bp.route('/test_jwt')
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

@api_bp.route('/user/messages', methods=['GET'])
@jwt_required()
def get_user_messages():
    """获取当前用户的留言列表"""
    try:
        # 获取当前用户ID
        user_id_str = get_jwt_identity()
        
        try:
            user_id = int(user_id_str)
            user = User.query.get(user_id)
            if not user:
                logger.error(f"找不到ID为{user_id}的用户")
                return jsonify({"error": "用户不存在"}), 404
        except ValueError:
            logger.error(f"无法将用户ID转换为整数: {user_id_str}")
            return jsonify({"error": "用户ID格式无效"}), 400
        
        # 获取用户的留言列表
        messages = Message.query.filter_by(user_id=user_id).all()
        messages_list = []
        
        for message in messages:
            # 不返回完整内容，只返回基本信息和预览
            # 查看完整内容需要使用撤销密钥
            content_preview = "需要密钥才能查看完整内容"
            
            try:
                # 获取接收人信息
                recipients = []
                for recipient in message.recipients:
                    recipients.append({
                        'name': recipient.name,
                        'contact': recipient.contact,
                        'contact_type': recipient.contact_type
                    })
                
                # 状态日志
                status_logs = []
                for log in message.status_logs:
                    status_logs.append({
                        'status': log.status,
                        'details': log.details,
                        'created_at': log.created_at.isoformat()
                    })
                
                messages_list.append({
                    'id': message.id,
                    'content_preview': content_preview,
                    'created_at': message.created_at.isoformat(),
                    'initial_delay_months': message.initial_delay_months,
                    'next_warning_date': message.next_warning_date.isoformat() if message.next_warning_date else None,
                    'warning_level': message.warning_level,
                    'is_active': message.is_active,
                    'recipients_count': len(recipients),
                    'status': "活跃" if message.is_active else "已撤销"
                })
            except Exception as e:
                logger.error(f"处理留言 {message.id} 时出错: {str(e)}")
        
        return jsonify(messages_list)
        
    except Exception as e:
        logger.error(f'获取用户留言列表失败: {str(e)}')
        return jsonify({'error': '获取留言列表失败：' + str(e)}), 500

@api_bp.route('/message/<int:message_id>/verify', methods=['POST'])
def verify_message_key(message_id):
    """验证特定消息ID的密钥是否匹配"""
    try:
        data = request.get_json()
        if not data or 'key' not in data:
            return jsonify({'error': '缺少密钥参数'}), 400
        
        revocation_key = data['key']
        
        # 查找对应的消息
        message = Message.query.get_or_404(message_id)
        
        # 验证密钥是否匹配
        if message.revocation_key != revocation_key:
            return jsonify({'verified': False, 'error': '密钥不匹配'}), 200
            
        # 密钥匹配
        return jsonify({'verified': True}), 200
        
    except Exception as e:
        logger.error(f'验证消息密钥失败: {str(e)}')
        return jsonify({'error': '验证密钥失败'}), 500

@api_bp.route('/message/find-by-key/<revocation_key>', methods=['GET'])
def find_message_by_key(revocation_key):
    """根据撤销密钥查找消息ID"""
    try:
        # 查找密钥对应的消息
        message = Message.query.filter_by(revocation_key=revocation_key).first()
        
        if not message:
            return jsonify({'error': '无效的密钥或留言不存在'}), 404
            
        # 返回消息ID
        return jsonify({
            'message_id': message.id,
            'exists': True
        }), 200
        
    except Exception as e:
        logger.error(f'根据密钥查找消息失败: {str(e)}')
        return jsonify({'error': '查找留言失败'}), 500
