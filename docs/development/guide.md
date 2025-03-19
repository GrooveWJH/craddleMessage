# 开发指南

## 1. 开发环境设置

### 1.1 环境准备
```bash
# 克隆代码库
git clone https://github.com/your-repo/cradle-message.git
cd cradle-message

# 创建虚拟环境
python3.8 -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装前端依赖
cd frontend
npm install
```

### 1.2 IDE配置
- **VS Code推荐插件**
  - Python
  - Vue Language Features
  - ESLint
  - Prettier
  - GitLens
  - Docker

- **VS Code设置**
  ```json
  {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.eslint": true
    },
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true
  }
  ```

## 2. 代码规范

### 2.1 Python代码规范
- **遵循PEP 8规范**
  - 使用4个空格缩进
  - 行长度限制在79个字符
  - 使用空行分隔函数和类
  - 使用有意义的变量名

- **类型注解**
  ```python
  from typing import List, Optional

  def get_user(user_id: int) -> Optional[User]:
      pass

  def process_messages(messages: List[Message]) -> None:
      pass
  ```

- **文档字符串**
  ```python
  def calculate_warning_dates(
      initial_delay: int,
      warning_levels: List[int]
  ) -> List[datetime]:
      """
      计算预警日期列表。

      Args:
          initial_delay: 初始延迟月数
          warning_levels: 预警级别列表

      Returns:
          List[datetime]: 预警日期列表

      Raises:
          ValueError: 当参数无效时
      """
      pass
  ```

### 2.2 JavaScript代码规范
- **遵循ESLint规则**
  ```javascript
  // 使用const和let
  const user = { id: 1, name: 'John' };
  let count = 0;

  // 使用箭头函数
  const getData = async () => {
    const response = await fetch('/api/data');
    return response.json();
  };

  // 使用解构赋值
  const { id, name } = user;
  ```

- **Vue组件规范**
  ```vue
  <template>
    <div class="message-form">
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm">提交</el-button>
        </el-form-item>
      </el-form>
    </div>
  </template>

  <script setup lang="ts">
  import { ref, reactive } from 'vue'
  import type { FormInstance } from 'element-plus'

  const formRef = ref<FormInstance>()
  const form = reactive({
    content: ''
  })

  const rules = {
    content: [
      { required: true, message: '请输入内容', trigger: 'blur' }
    ]
  }

  const submitForm = async () => {
    if (!formRef.value) return
    await formRef.value.validate()
    // 提交表单
  }
  </script>

  <style scoped>
  .message-form {
    max-width: 600px;
    margin: 0 auto;
  }
  </style>
  ```

## 3. 开发流程

### 3.1 分支管理
- **分支命名**
  - feature/功能名称
  - bugfix/问题描述
  - hotfix/紧急修复
  - release/版本号

- **工作流程**
  1. 从main分支创建功能分支
  2. 在功能分支开发
  3. 提交代码前进行代码审查
  4. 合并到main分支

### 3.2 提交规范
- **提交信息格式**
  ```
  <type>(<scope>): <subject>

  <body>

  <footer>
  ```

- **类型说明**
  - feat: 新功能
  - fix: 修复bug
  - docs: 文档更新
  - style: 代码格式
  - refactor: 重构
  - test: 测试
  - chore: 构建过程或辅助工具的变动

### 3.3 代码审查
- **审查清单**
  - 代码是否符合规范
  - 是否有足够的测试
  - 是否有安全隐患
  - 是否有性能问题
  - 是否考虑向后兼容

## 4. 测试规范

### 4.1 单元测试
```python
# tests/test_message.py
import pytest
from datetime import datetime, timedelta
from app.models import Message

def test_calculate_warning_dates():
    message = Message(
        content="Test message",
        initial_delay_months=12
    )
    warning_dates = message.calculate_warning_dates()
    
    assert len(warning_dates) == 5
    assert warning_dates[0] == datetime.now() + timedelta(days=365)
```

### 4.2 集成测试
```python
# tests/test_api.py
def test_create_message(client, auth_token):
    response = client.post(
        '/api/message',
        json={
            'content': 'Test message',
            'initial_delay_months': 12,
            'recipients': [
                {
                    'name': 'John',
                    'contact': 'john@example.com',
                    'type': 'email'
                }
            ]
        },
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    assert 'id' in response.json['data']
```

### 4.3 前端测试
```javascript
// tests/components/MessageForm.spec.js
import { mount } from '@vue/test-utils'
import MessageForm from '@/components/MessageForm.vue'

describe('MessageForm', () => {
  it('validates required fields', async () => {
    const wrapper = mount(MessageForm)
    await wrapper.find('button').trigger('click')
    
    expect(wrapper.find('.el-form-item__error').text())
      .toBe('请输入内容')
  })
})
```

## 5. 调试技巧

### 5.1 后端调试
```python
# 使用pdb调试
import pdb; pdb.set_trace()

# 使用logging调试
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_message(message):
    logger.debug(f'Processing message: {message.id}')
    # 处理逻辑
```

### 5.2 前端调试
```javascript
// 使用Vue DevTools
import { createDevtools } from '@vue/devtools'

// 使用console调试
console.log('Debug info:', data)
console.error('Error:', error)
console.warn('Warning:', warning)
```

## 6. 性能优化

### 6.1 后端优化
- **数据库优化**
  ```python
  # 使用索引
  class Message(db.Model):
      __table_args__ = (
          db.Index('idx_next_warning_date', 'next_warning_date'),
      )

  # 使用缓存
  @cache.cached(timeout=300)
  def get_message(message_id):
      return Message.query.get(message_id)
  ```

- **异步处理**
  ```python
  # 使用Celery处理异步任务
  @celery.task
  def send_notification(message_id):
      message = Message.query.get(message_id)
      # 发送通知
  ```

### 6.2 前端优化
- **组件优化**
  ```vue
  <!-- 使用v-show代替v-if -->
  <div v-show="isVisible">内容</div>

  <!-- 使用计算属性缓存结果 -->
  <script setup>
  const filteredMessages = computed(() => {
    return messages.value.filter(m => m.status === 'active')
  })
  </script>
  ```

- **资源优化**
  ```javascript
  // 路由懒加载
  const routes = [
    {
      path: '/messages',
      component: () => import('./views/Messages.vue')
    }
  ]

  // 图片懒加载
  <img v-lazy="imageUrl" />
  ```

## 7. 安全开发

### 7.1 数据安全
- **输入验证**
  ```python
  from marshmallow import Schema, fields

  class MessageSchema(Schema):
      content = fields.Str(required=True)
      initial_delay_months = fields.Int(required=True, validate=lambda n: n > 0)
  ```

- **SQL注入防护**
  ```python
  # 使用参数化查询
  result = db.session.execute(
      'SELECT * FROM messages WHERE id = :id',
      {'id': message_id}
  )
  ```

### 7.2 认证授权
- **JWT认证**
  ```python
  def create_access_token(user):
      return jwt.encode(
          {
              'user_id': user.id,
              'exp': datetime.utcnow() + timedelta(hours=24)
          },
          SECRET_KEY,
          algorithm='HS256'
      )
  ```

- **权限控制**
  ```python
  def require_permission(permission):
      def decorator(f):
          @wraps(f)
          def decorated_function(*args, **kwargs):
              if not current_user.has_permission(permission):
                  abort(403)
              return f(*args, **kwargs)
          return decorated_function
      return decorator
  ``` 