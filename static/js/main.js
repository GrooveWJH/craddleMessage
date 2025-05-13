// 添加接收人
function addRecipient() {
    const recipientsDiv = document.getElementById('recipients');
    const newRecipient = document.createElement('div');
    newRecipient.className = 'recipient-entry';
    newRecipient.style.marginBottom = '1rem';
    newRecipient.innerHTML = `
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <input type="text" class="form-control" name="recipient_name[]" placeholder="姓名" style="flex: 1; margin-right: 0.5rem;">
            <button type="button" class="btn btn-sm btn-danger remove-recipient" style="flex-shrink: 0;">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <input type="text" class="form-control" name="recipient_contact[]" placeholder="联系方式" style="margin-bottom: 0.5rem;">
        <select class="form-control" name="recipient_type[]">
            <option value="email">邮箱</option>
            <option value="phone">手机</option>
            <option value="wechat">微信</option>
        </select>
    `;
    
    recipientsDiv.appendChild(newRecipient);
    
    // 添加删除事件
    newRecipient.querySelector('.remove-recipient').addEventListener('click', function() {
        recipientsDiv.removeChild(newRecipient);
    });
}

// 获取Cookie值的辅助函数
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// 复制撤销密钥
function copyRevocationKey() {
    const keyElement = document.getElementById('revocationKey');
    const key = keyElement.textContent;
    navigator.clipboard.writeText(key).then(() => {
        alert('密钥已复制到剪贴板！');
    }).catch(err => {
        console.error('复制失败:', err);
        alert('复制失败，请手动复制。');
    });
}

// 显示撤销密钥弹窗
function showKeyModal(key) {
    document.getElementById('revocationKey').textContent = key;
    document.getElementById('keyModal').style.display = 'block';
}

// 关闭弹窗
function closeModal() {
    document.getElementById('keyModal').style.display = 'none';
}

// 使用撤销密钥查看留言内容
async function viewMessageWithKey(key) {
    try {
        const response = await fetch(`/api/message/view/${key}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // 创建查看留言内容的模态窗口
            const viewModal = document.createElement('div');
            viewModal.className = 'modal';
            viewModal.id = 'viewMessageModal';
            viewModal.innerHTML = `
                <div class="modal-content">
                    <span class="close-modal">&times;</span>
                    <h3><i class="fas fa-envelope-open-text"></i> 留言内容</h3>
                    
                    <div class="message-details">
                        <div class="detail-item">
                            <label>创建时间：</label>
                            <span>${new Date(result.created_at).toLocaleString()}</span>
                        </div>
                        <div class="detail-item">
                            <label>留言内容：</label>
                            <div class="message-content">${result.content}</div>
                        </div>
                        <div class="detail-item">
                            <label>初始延迟：</label>
                            <span>${result.initial_delay_months} 个月</span>
                        </div>
                        <div class="detail-item">
                            <label>当前状态：</label>
                            <span>${result.status}</span>
                        </div>
                        <div class="detail-item">
                            <label>预警级别：</label>
                            <span>${result.warning_level}</span>
                        </div>
                        <div class="detail-item">
                            <label>下次预警：</label>
                            <span>${result.next_warning_date ? new Date(result.next_warning_date).toLocaleString() : '无'}</span>
                        </div>
                        
                        <h4>接收人信息：</h4>
                        <ul class="recipients-list">
                            ${result.recipients.map(recipient => `
                                <li>
                                    <strong>${recipient.name}</strong>
                                    (${recipient.contact_type}): ${recipient.contact}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                    
                    <div class="modal-actions">
                        <button class="btn btn-danger" onclick="viewModalConfirmRevoke('${key}')">
                            <i class="fas fa-trash-alt"></i> 撤销此留言
                        </button>
                        <button class="btn btn-secondary" onclick="closeViewModal()">
                            <i class="fas fa-times"></i> 关闭
                        </button>
                    </div>
                </div>
            `;
            
            // 添加到页面并显示
            document.body.appendChild(viewModal);
            viewModal.style.display = 'block';
            
            // 添加关闭事件
            const closeBtn = viewModal.querySelector('.close-modal');
            closeBtn.onclick = closeViewModal;
            
            // 点击窗口外部关闭
            window.onclick = function(event) {
                if (event.target == viewModal) {
                    closeViewModal();
                }
            };
        } else {
            // 显示错误消息
            alert(result.error || '无法查看留言内容');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('查看失败：' + (error.message || '未知错误'));
    }
}

// 关闭查看留言模态窗口
function closeViewModal() {
    const viewModal = document.getElementById('viewMessageModal');
    if (viewModal) {
        viewModal.style.display = 'none';
        document.body.removeChild(viewModal);
    }
}

// 从查看窗口中确认撤销留言
function viewModalConfirmRevoke(key) {
    if (confirm('确定要撤销此留言吗？此操作不可恢复，留言将被永久删除。')) {
        // 关闭查看窗口
        closeViewModal();
        // 执行撤销操作
        revokeMessage(key);
    }
}

// 撤销留言
async function revokeMessage(key) {
    try {
        const response = await fetch(`/api/message/revoke/${key}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // 显示成功消息
            alert('留言撤销成功！所有数据已被删除。');
            
            // 如果在撤销表单中执行的操作，则重置表单
            const revokeForm = document.getElementById('revokeForm');
            if (revokeForm) {
                revokeForm.reset();
            }
        } else {
            // 显示错误消息
            alert(result.error || '撤销失败，请检查密钥是否正确');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('撤销失败：' + (error.message || '未知错误'));
    }
}

// 测试JWT令牌
async function testJwtToken() {
    try {
        const jwtToken = getCookie('jwt_token');
        console.log('测试JWT令牌:', jwtToken ? jwtToken.substring(0, 10) + '...' : '无效');
        
        if (!jwtToken) {
            console.error('JWT令牌不存在');
            return false;
        }
        
        const response = await fetch('/api/test_jwt', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${jwtToken}`
            }
        });
        
        const result = await response.json();
        console.log('JWT测试结果:', result);
        
        if (response.ok) {
            console.log('JWT验证成功, 用户ID:', result.user_id);
            return true;
        } else {
            console.error('JWT验证失败:', result.error);
            return false;
        }
    } catch (error) {
        console.error('JWT测试错误:', error);
        return false;
    }
}

// 加载当前用户的留言列表
async function loadUserMessages() {
    const messagesList = document.getElementById('messagesList');
    if (!messagesList) return; // 如果不存在消息列表元素则返回
    
    try {
        // 先测试JWT令牌
        const jwtValid = await testJwtToken();
        if (!jwtValid) {
            messagesList.innerHTML = '<tr><td colspan="6">身份验证已失效，请刷新页面重试</td></tr>';
            return;
        }
        
        // 从cookie获取JWT令牌
        const jwtToken = getCookie('jwt_token');
        if (!jwtToken) {
            messagesList.innerHTML = '<tr><td colspan="6">身份验证令牌缺失，请重新登录</td></tr>';
            return;
        }
        
        // 显示加载状态
        messagesList.innerHTML = '<tr><td colspan="6"><i class="fas fa-spinner fa-spin"></i> 正在加载留言列表...</td></tr>';
        
        const response = await fetch('/api/user/messages', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${jwtToken}`
            }
        });
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('非JSON响应:', text);
            messagesList.innerHTML = '<tr><td colspan="6">加载失败：服务器返回了非JSON响应</td></tr>';
            return;
        }
        
        const messages = await response.json();
        
        if (response.ok) {
            if (messages.length === 0) {
                messagesList.innerHTML = '<tr><td colspan="6">您还没有创建任何留言</td></tr>';
                return;
            }
            
            // 清空表格内容
            messagesList.innerHTML = '';
            
            // 填充留言列表
            messages.forEach(message => {
                const row = document.createElement('tr');
                
                // 创建时间
                const timeCell = document.createElement('td');
                timeCell.textContent = new Date(message.created_at).toLocaleString();
                row.appendChild(timeCell);
                
                // 内容预览
                const contentCell = document.createElement('td');
                contentCell.textContent = message.content_preview;
                row.appendChild(contentCell);
                
                // 预警级别
                const levelCell = document.createElement('td');
                const levelBadge = document.createElement('span');
                levelBadge.className = 'badge';
                
                // 根据预警级别设置不同的颜色
                switch (message.warning_level) {
                    case 0:
                        levelBadge.className += ' badge-info';
                        levelBadge.textContent = '未激活';
                        break;
                    case 1:
                        levelBadge.className += ' badge-primary';
                        levelBadge.textContent = '一级预警';
                        break;
                    case 2:
                        levelBadge.className += ' badge-warning';
                        levelBadge.textContent = '二级预警';
                        break;
                    case 3:
                        levelBadge.className += ' badge-warning';
                        levelBadge.textContent = '三级预警';
                        break;
                    case 4:
                        levelBadge.className += ' badge-danger';
                        levelBadge.textContent = '四级预警';
                        break;
                    case 5:
                        levelBadge.className += ' badge-danger';
                        levelBadge.textContent = '最终预警';
                        break;
                    default:
                        levelBadge.className += ' badge-secondary';
                        levelBadge.textContent = '未知状态';
                }
                
                levelCell.appendChild(levelBadge);
                row.appendChild(levelCell);
                
                // 下次预警时间
                const nextWarningCell = document.createElement('td');
                if (message.next_warning_date) {
                    nextWarningCell.textContent = new Date(message.next_warning_date).toLocaleString();
                } else {
                    nextWarningCell.textContent = '无';
                }
                row.appendChild(nextWarningCell);
                
                // 状态
                const statusCell = document.createElement('td');
                const statusBadge = document.createElement('span');
                statusBadge.className = 'badge ' + (message.is_active ? 'badge-success' : 'badge-danger');
                statusBadge.textContent = message.status;
                statusCell.appendChild(statusBadge);
                row.appendChild(statusCell);
                
                // 操作按钮
                const actionCell = document.createElement('td');
                const viewBtn = document.createElement('button');
                viewBtn.className = 'btn btn-sm btn-secondary';
                viewBtn.innerHTML = '<i class="fas fa-eye"></i> 查看';
                viewBtn.onclick = function() {
                    showMessageViewPrompt(message.id);
                };
                actionCell.appendChild(viewBtn);
                row.appendChild(actionCell);
                
                messagesList.appendChild(row);
            });
        } else {
            // 显示错误消息
            const errorMessage = messages.error || '加载留言列表失败';
            messagesList.innerHTML = `<tr><td colspan="6">${errorMessage}</td></tr>`;
        }
    } catch (error) {
        console.error('Error:', error);
        messagesList.innerHTML = `<tr><td colspan="6">加载留言列表失败: ${error.message || '未知错误'}</td></tr>`;
    }
}

// 显示查看留言的密钥输入提示
function showMessageViewPrompt(messageId) {
    // 创建密钥输入模态窗口
    const keyModal = document.createElement('div');
    keyModal.className = 'modal';
    keyModal.id = 'keyInputModal';
    keyModal.innerHTML = `
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h3><i class="fas fa-key"></i> 输入密钥查看留言</h3>
            <p>请输入留言的撤销密钥以查看完整内容：</p>
            <div class="form-group">
                <input type="text" id="viewKeyInput" class="form-control" placeholder="输入撤销密钥">
            </div>
            <div class="modal-actions">
                <button id="submitViewKey" class="btn btn-primary">
                    <i class="fas fa-eye"></i> 查看留言
                </button>
                <button id="cancelViewKey" class="btn btn-secondary">
                    <i class="fas fa-times"></i> 取消
                </button>
            </div>
        </div>
    `;
    
    // 添加到页面并显示
    document.body.appendChild(keyModal);
    keyModal.style.display = 'block';
    
    // 添加关闭事件
    const closeBtn = keyModal.querySelector('.close-modal');
    closeBtn.onclick = closeKeyInputModal;
    
    // 取消按钮事件
    const cancelBtn = document.getElementById('cancelViewKey');
    cancelBtn.onclick = closeKeyInputModal;
    
    // 提交按钮事件
    const submitBtn = document.getElementById('submitViewKey');
    submitBtn.onclick = function() {
        const key = document.getElementById('viewKeyInput').value.trim();
        if (!key) {
            alert('请输入撤销密钥');
            return;
        }
        
        // 先验证密钥是否与消息ID匹配
        verifyMessageKey(messageId, key);
    };
    
    // 点击窗口外部关闭
    window.onclick = function(event) {
        if (event.target == keyModal) {
            closeKeyInputModal();
        }
    };
    
    // 添加键盘事件：按Enter键提交
    const keyInput = document.getElementById('viewKeyInput');
    keyInput.focus();
    keyInput.addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            submitBtn.click();
        }
    });
}

// 验证消息ID和密钥是否匹配
async function verifyMessageKey(messageId, key) {
    try {
        // 显示验证中状态
        const submitBtn = document.getElementById('submitViewKey');
        if (submitBtn) {
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 验证中...';
            submitBtn.disabled = true;
        }
        
        // 调用API验证密钥
        const response = await fetch(`/api/message/${messageId}/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ key: key })
        });
        
        const result = await response.json();
        
        // 恢复按钮状态
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-eye"></i> 查看留言';
            submitBtn.disabled = false;
        }
        
        if (response.ok) {
            if (result.verified) {
                // 密钥验证成功，关闭输入窗口并查看留言
                closeKeyInputModal();
                viewMessageWithKey(key);
            } else {
                // 密钥与消息ID不匹配
                alert('密钥与留言不匹配，请检查后重试');
            }
        } else {
            // API调用失败
            alert(result.error || '验证密钥失败，请重试');
        }
    } catch (error) {
        console.error('Error:', error);
        
        // 恢复按钮状态
        const submitBtn = document.getElementById('submitViewKey');
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-eye"></i> 查看留言';
            submitBtn.disabled = false;
        }
        
        alert('验证失败：' + (error.message || '未知错误'));
    }
}

// 关闭密钥输入模态窗口
function closeKeyInputModal() {
    const keyModal = document.getElementById('keyInputModal');
    if (keyModal) {
        keyModal.style.display = 'none';
        document.body.removeChild(keyModal);
    }
}

// 处理表单提交
document.addEventListener('DOMContentLoaded', function() {
    // 测试JWT令牌
    testJwtToken();
    
    // 初始化模态窗口关闭事件
    const modal = document.getElementById('keyModal');
    const closeBtn = document.querySelector('.close-modal');
    
    if (closeBtn) {
        closeBtn.onclick = closeModal;
    }
    
    // 点击模态窗口外部关闭
    window.onclick = function(event) {
        if (event.target == modal) {
            closeModal();
        }
    };
    
    // 处理创建留言表单
    const messageForm = document.getElementById('messageForm');
    if (messageForm) {
        messageForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // 显示加载状态
            const submitBtn = messageForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';
            submitBtn.disabled = true;
            
            // 创建接收人数组
            const formData = new FormData(messageForm);
            const recipients = [];
            const names = formData.getAll('recipient_name[]');
            const contacts = formData.getAll('recipient_contact[]');
            const types = formData.getAll('recipient_type[]');
            
            // 验证接收人信息
            let hasEmptyRecipient = false;
            for (let i = 0; i < names.length; i++) {
                if (!names[i] || !contacts[i]) {
                    hasEmptyRecipient = true;
                    break;
                }
                recipients.push({
                    name: names[i],
                    contact: contacts[i],
                    contact_type: types[i]
                });
            }
            
            if (hasEmptyRecipient) {
                alert('请完整填写所有接收人信息');
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                return;
            }
            
            if (recipients.length === 0) {
                alert('请至少添加一个接收人');
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                return;
            }
            
            // 获取内容和延迟时间
            const content = formData.get('content');
            const initialDelay = parseInt(formData.get('initialDelay'));
            
            if (!content) {
                alert('请输入留言内容');
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                return;
            }
            
            const data = {
                content: content,
                initial_delay_months: initialDelay,
                recipients: recipients
            };
            
            console.log('准备提交数据:', data);
            console.log('接收人数量:', recipients.length);
            console.log('接收人第一个:', recipients[0]);
            
            // 先测试JWT令牌
            const jwtValid = await testJwtToken();
            if (!jwtValid) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger fade-in';
                errorDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> 身份验证已失效，请刷新页面重试';
                messageForm.parentElement.insertBefore(errorDiv, messageForm);
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                return;
            }
            
            try {
                // 从cookie获取JWT令牌
                const jwtToken = getCookie('jwt_token');
                console.log('使用JWT令牌:', jwtToken ? '有效' : '无效');
                
                if (!jwtToken) {
                    throw new Error('身份验证令牌缺失，请重新登录');
                }
                
                const requestOptions = {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${jwtToken}`
                    },
                    body: JSON.stringify(data)
                };
                
                console.log('请求选项:', {
                    method: requestOptions.method,
                    headers: {
                        ...requestOptions.headers,
                        'Authorization': 'Bearer ***' // 隐藏实际令牌
                    }
                });
                
                const response = await fetch('/api/message', requestOptions);
                const contentType = response.headers.get('content-type');
                console.log('响应状态:', response.status, response.statusText);
                console.log('响应内容类型:', contentType);
                
                let result;
                if (contentType && contentType.includes('application/json')) {
                    result = await response.json();
                } else {
                    const text = await response.text();
                    console.log('非JSON响应:', text);
                    result = { error: '服务器返回了非JSON响应' };
                }
                
                console.log('API响应:', result);
                
                if (response.ok) {
                    // 显示成功消息
                    const successDiv = document.createElement('div');
                    successDiv.className = 'alert alert-success fade-in';
                    successDiv.innerHTML = '<i class="fas fa-check-circle"></i> 留言创建成功！';
                    messageForm.parentElement.insertBefore(successDiv, messageForm);
                    
                    // 显示撤销密钥弹窗
                    if (result.revocation_key) {
                        showKeyModal(result.revocation_key);
                    } else {
                        console.warn('响应中无撤销密钥');
                    }
                    
                    // 重置表单
                    messageForm.reset();
                    // 只保留一个接收人表单
                    const recipientsDiv = document.getElementById('recipients');
                    const recipients = recipientsDiv.querySelectorAll('.recipient-entry');
                    for (let i = 1; i < recipients.length; i++) {
                        recipientsDiv.removeChild(recipients[i]);
                    }
                } else {
                    // 显示错误消息
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'alert alert-danger fade-in';
                    errorDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + (result.error || '创建失败，请重试');
                    messageForm.parentElement.insertBefore(errorDiv, messageForm);
                }
            } catch (error) {
                console.error('Error:', error);
                
                // 显示错误消息
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger fade-in';
                errorDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + (error.message || '创建失败，请重试');
                messageForm.parentElement.insertBefore(errorDiv, messageForm);
            } finally {
                // 恢复按钮状态
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
            }
        });
    }
    
    // 处理撤销留言表单
    const revokeForm = document.getElementById('revokeForm');
    if (revokeForm) {
        revokeForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // 显示加载状态
            const submitBtn = revokeForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';
            submitBtn.disabled = true;
            
            try {
                const revocationKey = document.getElementById('revocationKeyInput').value.trim();
                
                if (!revocationKey) {
                    alert('请输入撤销密钥');
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.disabled = false;
                    return;
                }
                
                // 执行撤销操作
                const response = await fetch(`/api/message/revoke/${revocationKey}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    // 显示成功消息
                    const successDiv = document.createElement('div');
                    successDiv.className = 'alert alert-success fade-in';
                    successDiv.innerHTML = '<i class="fas fa-check-circle"></i> 留言撤销成功！数据已被删除。';
                    revokeForm.parentElement.insertBefore(successDiv, revokeForm);
                    
                    // 重置表单
                    revokeForm.reset();
                } else {
                    // 显示错误消息
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'alert alert-danger fade-in';
                    errorDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + (result.error || '撤销失败，请检查密钥是否正确');
                    revokeForm.parentElement.insertBefore(errorDiv, revokeForm);
                }
            } catch (error) {
                console.error('Error:', error);
                
                // 显示错误消息
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger fade-in';
                errorDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + (error.message || '撤销失败，请重试');
                revokeForm.parentElement.insertBefore(errorDiv, revokeForm);
            } finally {
                // 恢复按钮状态
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
            }
        });
        
        // 添加查看按钮事件处理
        const viewBtn = document.getElementById('viewMessageBtn');
        if (viewBtn) {
            viewBtn.addEventListener('click', async function(e) {
                e.preventDefault();
                
                const revocationKey = document.getElementById('revocationKeyInput').value.trim();
                
                if (!revocationKey) {
                    alert('请输入撤销密钥');
                    return;
                }
                
                try {
                    // 显示加载状态
                    const originalBtnText = viewBtn.innerHTML;
                    viewBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 查询中...';
                    viewBtn.disabled = true;
                    
                    // 先通过密钥查找消息ID
                    const response = await fetch(`/api/message/find-by-key/${revocationKey}`, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    // 恢复按钮状态
                    viewBtn.innerHTML = originalBtnText;
                    viewBtn.disabled = false;
                    
                    if (response.ok) {
                        const result = await response.json();
                        
                        if (result.message_id) {
                            // 直接调用查看留言函数，因为我们已经知道密钥是匹配的
                            viewMessageWithKey(revocationKey);
                        } else {
                            alert('找不到对应的留言，请检查密钥是否正确');
                        }
                    } else {
                        const result = await response.json();
                        alert(result.error || '查找留言失败，请检查密钥是否正确');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    viewBtn.innerHTML = originalBtnText;
                    viewBtn.disabled = false;
                    alert('操作失败：' + (error.message || '未知错误'));
                }
            });
        }
    }
    
    // 加载当前用户的留言列表
    loadUserMessages();
});