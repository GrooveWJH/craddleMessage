// 加载统计数据
async function loadStats() {
    try {
        const response = await fetch('/api/admin/stats', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('userCount').textContent = stats.userCount;
            document.getElementById('messageCount').textContent = stats.messageCount;
            document.getElementById('pendingCount').textContent = stats.pendingCount;
        } else {
            throw new Error('Failed to load stats');
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('userCount').textContent = '加载失败';
        document.getElementById('messageCount').textContent = '加载失败';
        document.getElementById('pendingCount').textContent = '加载失败';
    }
}

// 加载系统设置
async function loadSettings() {
    try {
        const response = await fetch('/api/admin/settings', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const settings = await response.json();
            document.getElementById('alertInterval').value = settings.alertInterval;
            document.getElementById('maxRetries').value = settings.maxRetries;
        } else {
            throw new Error('Failed to load settings');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// 保存系统设置
document.addEventListener('DOMContentLoaded', function() {
    const settingsForm = document.getElementById('systemSettings');
    if (settingsForm) {
        settingsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const data = {
                alertInterval: parseInt(document.getElementById('alertInterval').value),
                maxRetries: parseInt(document.getElementById('maxRetries').value)
            };
            
            try {
                const response = await fetch('/api/admin/settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    alert('设置保存成功！');
                } else {
                    const error = await response.json();
                    alert(error.error || '保存失败，请重试');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('保存失败，请重试');
            }
        });
    }
    
    // 初始加载
    loadStats();
    loadSettings();
});