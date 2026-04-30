<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <el-icon><OfficeBuilding /></el-icon>
        <h1>海南省住建知识库</h1>
        <p>行业知识图谱平台</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="rememberMe">记住密码</el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p>技术支持：海南省住房和城乡建设厅</p>
      </div>
    </div>

    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import request from '@/api'

const router = useRouter()

const loginFormRef = ref(null)
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true

    try {
      // 调用后端登录API
      const response = await request.post('/auth/login', {
        username: loginForm.username,
        password: loginForm.password
      })

      // 保存token
      localStorage.setItem('token', response.access_token)
      localStorage.setItem('username', loginForm.username)
      // admin用户默认有系统访问权限
      localStorage.setItem('isSuperuser', loginForm.username === 'admin' ? 'true' : 'false')

      // 获取并存储用户ID
      try {
        const userInfo = await request.get('/auth/me')
        localStorage.setItem('user_id', userInfo.id)
      } catch (e) {
        console.error('获取用户信息失败', e)
      }

      ElMessage.success('登录成功')
      // 根据用户角色跳转
      if (loginForm.username === 'admin') {
        router.push('/system/users')
      } else {
        router.push('/knowledge/search')
      }
    } catch (error) {
      console.error('登录失败:', error)
      ElMessage.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-gradient);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 - 几何图形 */
.bg-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(4px);
}

.circle-1 {
  width: 500px;
  height: 500px;
  top: -150px;
  right: -150px;
  animation: float 20s ease-in-out infinite;
}

.circle-2 {
  width: 350px;
  height: 350px;
  bottom: -100px;
  left: -100px;
  animation: float 15s ease-in-out infinite reverse;
}

.circle-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  left: 10%;
  transform: translate(-50%, -50%);
  animation: pulse 8s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.08; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.15; transform: translate(-50%, -50%) scale(1.1); }
}

.login-box {
  width: 440px;
  padding: 48px 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-xl);
  position: relative;
  z-index: 10;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

/* 内光效果 */
.login-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: var(--border-radius-lg);
  box-shadow: inset 0 2px 20px rgba(30, 77, 123, 0.08);
  pointer-events: none;
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.login-header h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 600;
  color: var(--primary-color);
  letter-spacing: 2px;
}

.login-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.login-form {
  margin-top: 28px;
}

/* 输入框样式优化 */
.login-form :deep(.el-input__wrapper) {
  padding: 14px 16px;
  border-radius: var(--border-radius-sm);
  box-shadow: 0 0 0 1px var(--border-color);
  transition: all var(--transition-fast);
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 2px rgba(30, 77, 123, 0.15);
}

.login-form :deep(.el-input__wrapper:focus-within) {
  box-shadow: 0 0 0 2px rgba(30, 77, 123, 0.25);
}

.login-form :deep(.el-input__prefix) {
  color: var(--text-light);
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: var(--border-radius-sm);
  background: var(--primary-gradient);
  border: none;
  transition: all var(--transition-fast);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(30, 77, 123, 0.35);
}

.login-btn:active {
  transform: translateY(0);
}

.login-footer {
  text-align: center;
  margin-top: 28px;
  color: var(--text-light);
  font-size: 12px;
}

.login-footer p {
  margin: 0;
}

/* 金色logo图标 */
.login-header :deep(.el-icon) {
  font-size: 42px;
  color: var(--accent-light);
  margin-bottom: 12px;
  filter: drop-shadow(0 3px 6px rgba(218, 165, 32, 0.3));
}

/* 记住密码checkbox */
.login-form :deep(.el-checkbox__label) {
  color: var(--text-secondary);
}
</style>
