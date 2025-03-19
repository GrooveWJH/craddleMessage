// 添加接收人
function addRecipient() {
    const recipientsDiv = document.getElementById('recipients');
    const newRecipient = document.createElement('div');
    newRecipient.className = 'recipient';
    newRecipient.innerHTML = `
        <input type="text" name="recipient_name[]" placeholder="姓名" required>
        <input type="text" name="recipient_contact[]" placeholder="联系方式" required>
        <select name="recipient_type[]" required>
            <option value="email">邮箱</option>
            <option value="phone">电话</option>
            <option value="wechat">微信</option>
        </select>
        <button type="button" onclick="this.parentElement.remove()">删除</button>
    `;
    recipientsDiv.appendChild(newRecipient);
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

// 处理表单提交
document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('messageForm');
    if (messageForm) {
        messageForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(messageForm);
            const recipients = [];
            const names = formData.getAll('recipient_name[]');
            const contacts = formData.getAll('recipient_contact[]');
            const types = formData.getAll('recipient_type[]');
            
            for (let i = 0; i < names.length; i++) {
                recipients.push({
                    name: names[i],
                    contact: contacts[i],
                    contact_type: types[i]
                });
            }
            
            const data = {
                content: formData.get('content'),
                initial_delay_months: parseInt(formData.get('initialDelay')),
                recipients: recipients
            };
            
            try {
                const response = await fetch('/api/message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    // 显示撤销密钥
                    document.getElementById('revocationKey').textContent = result.revocation_key;
                    document.querySelector('.revocation-key').style.display = 'block';
                    // 重置表单
                    messageForm.reset();
                } else {
                    const error = await response.json();
                    alert(error.error || '创建失败，请重试');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('创建失败，请重试');
            }
        });
    }
});