<template>
  <div class="qa-chat-page">
    <div class="page-header">
      <h2>问答助手</h2>
      <p class="subtitle">智能问答，常见问题快速查询</p>
    </div>

    <el-row :gutter="24">
      <el-col :span="18">
        <el-card class="chat-card">
          <!-- 快捷问题 -->
          <div class="quick-questions">
            <span class="quick-label">猜你想问：</span>
            <el-tag
              v-for="q in quickQuestions"
              :key="q"
              class="quick-tag"
              @click="selectQuestion(q)"
            >
              {{ q }}
            </el-tag>
          </div>

          <el-divider />

          <!-- 对话区域 -->
          <div class="chat-messages" ref="chatMessagesRef">
            <div v-if="!messages.length && !isThinking" class="empty-state">
              <el-icon class="empty-icon"><ChatDotRound /></el-icon>
              <p>请输入您的问题，我将尽力为您解答</p>
            </div>

            <div v-for="(msg, index) in sortedMessages" :key="msg.id || index" class="chat-message">
              <div :class="['message', msg.role]">
                <div class="message-avatar">
                  <el-avatar :size="36" :icon="msg.role === 'user' ? 'User' : 'ChatDotRound'" />
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="sender-name">{{ msg.role === 'user' ? '我' : '问答助手' }}</span>
                    <span class="message-time">{{ msg.time }}</span>
                  </div>
                  <div class="message-body">
                    <div v-html="renderMarkdown(msg.content)"></div>

                    <!-- 显示推荐答案卡片 -->
                    <div v-if="msg.cards?.length" class="answer-cards">
                      <div
                        v-for="card in msg.cards"
                        :key="card.id"
                        class="answer-card"
                        @click="viewCard(card)"
                      >
                        <h4>{{ card.title }}</h4>
                        <p>{{ card.summary }}</p>
                        <div class="card-footer">
                          <el-tag size="small">{{ card.type }}</el-tag>
                          <span class="confidence">
                            <el-icon><Star /></el-icon>
                            置信度 {{ card.confidence }}%
                          </span>
                        </div>
                      </div>
                    </div>

                    <!-- 相关问题推荐 -->
                    <div v-if="msg.relatedQuestions?.length" class="related-questions">
                      <span class="related-label">相关问题：</span>
                      <el-tag
                        v-for="q in msg.relatedQuestions"
                        :key="q"
                        size="small"
                        @click="selectQuestion(q)"
                      >
                        {{ q }}
                      </el-tag>
                    </div>
                  </div>

                  <!-- 评价 -->
                  <div v-if="msg.role === 'assistant'" class="message-actions">
                    <span class="action-label">答案是否有用：</span>
                    <el-button size="small" @click="rateAnswer(index, 'up')">
                      <el-icon><Check /></el-icon>
                      有用 ({{ msg.likes || 0 }})
                    </el-button>
                    <el-button size="small" @click="rateAnswer(index, 'down')">
                      <el-icon><Close /></el-icon>
                      没帮助
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 思考中提示 -->
            <div v-if="isThinking" class="chat-message">
              <div class="message assistant">
                <div class="message-avatar">
                  <el-avatar :size="36" :icon="ChatDotRound" />
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="sender-name">问答助手</span>
                  </div>
                  <div class="message-body thinking">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    <span>正在检索知识库并生成回答，请稍候...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="chat-input">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="2"
              placeholder="请输入问题，例如：建设工程竣工验收需要哪些条件？"
              @keydown.enter.ctrl="handleSend"
            />
            <div class="input-actions">
              <span class="hint">按 Ctrl+Enter 发送</span>
              <el-button type="primary" @click="handleSend" :disabled="!inputMessage.trim()">
                <el-icon><Promotion /></el-icon>
                发送
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <!-- 会话列表 -->
        <el-card class="session-card">
          <template #header>
            <div class="session-header">
              <span>会话列表</span>
              <el-button size="small" type="primary" @click="createNewSession">
                <el-icon><Plus /></el-icon>
                新建
              </el-button>
            </div>
          </template>
          <div class="session-list">
            <div
              v-for="session in sessions"
              :key="session.id"
              :class="['session-item', { active: session.id === currentSessionId }]"
              @click="switchSession(session.id)"
            >
              <div class="session-info">
                <span class="session-title">{{ session.title }}</span>
                <span class="session-time">{{ formatTime(session.updated_at) }}</span>
              </div>
              <div class="session-actions">
                <el-button
                  size="small"
                  type="danger"
                  link
                  @click.stop="clearSessionMessages(session.id)"
                  title="清除历史"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            <div v-if="!sessions.length" class="no-sessions">
              暂无会话记录
            </div>
          </div>
        </el-card>

        <!-- 问答统计 -->
        <el-card class="stat-card">
          <template #header>
            <span>问答统计</span>
          </template>
          <el-row :gutter="16">
            <el-col :span="12" class="stat-item">
              <div class="stat-value">{{ stats.answerCount }}</div>
              <div class="stat-label">累计问答</div>
            </el-col>
            <el-col :span="12" class="stat-item">
              <div class="stat-value">{{ stats.todayCount }}</div>
              <div class="stat-label">今日问答</div>
            </el-col>
          </el-row>
          <el-progress :percentage="stats.satisfaction" style="margin-top: 16px;" />
          <div style="text-align: center; color: #909399; font-size: 13px; margin-top: 4px;">
            满意度
          </div>
        </el-card>

        <!-- 热门问题 -->
        <el-card class="hot-card">
          <template #header>
            <span>热门问题</span>
          </template>
          <div class="hot-list">
            <div
              v-for="(item, index) in hotQuestions"
              :key="index"
              class="hot-item"
              @click="selectQuestion(item.question)"
            >
              <span class="hot-rank" :class="getRankClass(index)">{{ index + 1 }}</span>
              <span class="hot-text">{{ item.question }}</span>
              <span class="hot-count">{{ item.count }}次</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatDotRound, Promotion, Star, User, ChatLineSquare, Check, Close, Loading, Plus, Delete
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import { qaApi } from '@/api'
import request from '@/api'

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true
})

const inputMessage = ref('')
const messages = ref([])
const isThinking = ref(false)
const chatMessagesRef = ref(null)

// 请求追踪，确保消息顺序
let currentRequestId = 0

// 会话相关
const sessions = ref([])
const currentSessionId = ref(null)

const quickQuestions = [
  '建设工程竣工验收条件',
  '施工许可证办理流程',
  '安全生产许可证有效期',
  '工程质量问题投诉渠道'
]

const stats = ref({
  answerCount: 0,
  todayCount: 0,
  satisfaction: 0
})

const hotQuestions = ref([])

// 确保消息按时间顺序显示
const sortedMessages = computed(() => {
  return [...messages.value].sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0))
})

// 渲染 Markdown
const renderMarkdown = (content) => {
  if (!content) return ''
  try {
    return marked(content)
  } catch (e) {
    console.error('Markdown render error:', e)
    return content
  }
}

// 缓存 user_id，避免重复查询
let cachedUserId = null

const ensureUserId = async () => {
  if (cachedUserId) return cachedUserId

  let userId = localStorage.getItem('user_id')
  if (!userId && localStorage.getItem('token')) {
    try {
      const userInfo = await request.get('/auth/me')
      userId = userInfo.id
      localStorage.setItem('user_id', userId)
    } catch (e) {
      console.error('获取用户信息失败', e)
      userId = '1'
    }
  }
  cachedUserId = userId || '1'
  return cachedUserId
}

// ============ 会话管理 ============

const loadSessions = async () => {
  try {
    const data = await qaApi.getSessions()
    // 过滤掉执法助手创建的会话（category=law_general）
    sessions.value = (data.items || []).filter(s => s.category !== 'law_general')
  } catch (error) {
    console.error('加载会话列表失败:', error)
  }
}

const createNewSession = async () => {
  try {
    const data = await qaApi.createSession()
    sessions.value.unshift(data)
    switchSession(data.id)
    ElMessage.success('已创建新会话')
  } catch (error) {
    console.error('创建会话失败:', error)
    ElMessage.error('创建会话失败')
  }
}

const switchSession = async (sessionId) => {
  // 切换会话时递增请求ID，使旧请求失效
  ++currentRequestId
  currentSessionId.value = sessionId
  messages.value = []

  try {
    const data = await qaApi.getSession(sessionId)
    if (data && data.messages) {
      messages.value = data.messages.map((m, idx) => ({
        role: m.role,
        content: m.content,
        time: m.time,
        id: m.id,
        cards: [],
        relatedQuestions: [],
        likes: 0,
        timestamp: idx
      }))
    }
  } catch (error) {
    console.error('加载会话详情失败:', error)
  }

  scrollToBottom()
}

const clearSessionMessages = async (sessionId) => {
  try {
    await ElMessageBox.confirm('确定要清除该会话的所有记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await qaApi.clearMessages(sessionId)

    if (sessionId === currentSessionId.value) {
      messages.value = []
    }

    // 更新会话标题
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      session.title = '新对话'
    }

    ElMessage.success('已清除会话记录')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清除会话失败:', error)
      ElMessage.error('清除会话失败')
    }
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  return date.toLocaleDateString()
}

// ============ 问答 ============

const getRankClass = (index) => {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}

const selectQuestion = (question) => {
  inputMessage.value = question
  handleSend()
}

const handleSend = async () => {
  if (!inputMessage.value.trim()) return

  const thisRequestId = ++currentRequestId
  const sessionIdAtSend = currentSessionId.value

  const userMsg = {
    role: 'user',
    content: inputMessage.value,
    time: new Date().toLocaleTimeString(),
    id: `user-${Date.now()}`,
    timestamp: Date.now()
  }
  messages.value.push(userMsg)
  inputMessage.value = ''
  isThinking.value = true

  scrollToBottom()

  try {
    const userId = cachedUserId || await ensureUserId()
    const result = await qaApi.chat(userMsg.content, userId, sessionIdAtSend)

    // 检查是否是最新的请求，避免旧请求覆盖新消息
    if (thisRequestId !== currentRequestId) {
      console.warn('Ignoring stale response')
      return
    }

    // 添加助手回复
    const aiMsg = {
      role: 'assistant',
      content: result.answer,
      id: result.id,
      cards: result.cards || [],
      relatedQuestions: result.related_questions || [],
      likes: 0,
      time: new Date().toLocaleTimeString(),
      timestamp: Date.now()
    }
    messages.value.push(aiMsg)

    // 更新 session_id（如果是新会话）
    if (result.session_id && result.session_id !== currentSessionId.value) {
      currentSessionId.value = result.session_id

      // 刷新会话列表
      await loadSessions()
    }

    // 更新当前会话标题
    if (currentSessionId.value) {
      const session = sessions.value.find(s => s.id === currentSessionId.value)
      if (session && session.title === '新对话') {
        session.title = result.question?.slice(0, 20) + (result.question?.length > 20 ? '...' : '')
      }
    }
  } catch (error) {
    if (thisRequestId === currentRequestId) {
      ElMessage.error('问答服务出错，请稍后重试')
      console.error('QA error:', error)
    }
  } finally {
    if (thisRequestId === currentRequestId) {
      isThinking.value = false
    }
  }

  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    chatMessagesRef.value?.scrollTo({
      top: chatMessagesRef.value.scrollHeight,
      behavior: 'smooth'
    })
  })
}

const rateAnswer = async (index, type) => {
  const msg = messages.value[index]
  const qaId = msg.id

  if (!qaId) {
    ElMessage.info('无法评价，请刷新页面重试')
    return
  }

  try {
    await qaApi.rate(qaId, type)
    if (type === 'up') {
      msg.likes = (msg.likes || 0) + 1
      ElMessage.success('感谢您的评价')
    } else {
      ElMessage.info('抱歉，我会继续改进')
    }
  } catch (error) {
    ElMessage.error('评价失败')
  }
}

const viewCard = (card) => {
  window.location.href = `/knowledge/detail/${card.id}`
}

// ============ 数据加载 ============

const loadStats = async () => {
  try {
    const data = await qaApi.stats()
    stats.value = {
      answerCount: data.total_count || 0,
      todayCount: data.today_count || 0,
      satisfaction: data.satisfaction || 0
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadHotQuestions = async () => {
  try {
    const data = await qaApi.hotQuestions(5)
    hotQuestions.value = data.items || []
  } catch (error) {
    console.error('加载热门问题失败:', error)
  }
}

onMounted(async () => {
  await ensureUserId()

  // 并行加载数据
  await Promise.all([
    loadSessions(),
    loadStats(),
    loadHotQuestions()
  ])

  // 如果有会话，加载最新的
  if (sessions.value.length > 0) {
    switchSession(sessions.value[0].id)
  }
})
</script>

<style scoped>
.qa-chat-page {
  max-width: 1400px;
}

.chat-card {
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.chat-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.quick-questions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-label {
  color: #909399;
  font-size: 14px;
}

.quick-tag {
  cursor: pointer;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  color: #dcdfe6;
}

.thinking {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  padding: 8px 0;
}

.thinking .el-icon {
  font-size: 18px;
}

.chat-message {
  margin-bottom: 24px;
}

.message {
  display: flex;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 80%;
}

.message-header {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 13px;
}

.message.user .message-header {
  flex-direction: row-reverse;
}

.sender-name {
  font-weight: 600;
  color: #303133;
}

.message-time {
  color: #c0c4cc;
}

.message-body {
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.6;
}

.message.assistant .message-body {
  background: #fff;
  border: 1px solid #e4e7ed;
}

.message.user .message-body {
  background: #409eff;
  color: #fff;
}

.message.user .message-body p {
  margin: 0;
}

.answer-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.answer-card {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.answer-card:hover {
  background: #e4e7ed;
}

.answer-card h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #303133;
}

.answer-card p {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #606266;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.confidence {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 12px;
}

.related-questions {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.related-label {
  color: #909399;
  font-size: 13px;
}

.message-actions {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-label {
  color: #c0c4cc;
  font-size: 13px;
}

.chat-input {
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.hint {
  color: #c0c4cc;
  font-size: 13px;
}

/* Session Card */
.session-card {
  margin-bottom: 16px;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-list {
  max-height: 200px;
  overflow-y: auto;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 8px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.session-item:hover {
  background: #f5f7fa;
}

.session-item.active {
  background: #ecf5ff;
  border-left: 3px solid #409eff;
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-title {
  display: block;
  font-size: 14px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-time {
  font-size: 12px;
  color: #c0c4cc;
}

.session-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .session-actions {
  opacity: 1;
}

.no-sessions {
  text-align: center;
  color: #c0c4cc;
  padding: 20px;
  font-size: 14px;
}

/* Stat Card */
.stat-card,
.hot-card {
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #409eff;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* Hot List */
.hot-list {
  display: flex;
  flex-direction: column;
}

.hot-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 4px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.hot-item:hover {
  color: #409eff;
}

.hot-rank {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  background: #f0f0f0;
  color: #909399;
}

.hot-rank.gold {
  background: #fdf6ec;
  color: #e6a23c;
}

.hot-rank.silver {
  background: #f4f4f5;
  color: #909399;
}

.hot-rank.bronze {
  background: #fdf0f0;
  color: #e6a23c;
}

.hot-text {
  flex: 1;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hot-count {
  color: #c0c4cc;
  font-size: 12px;
}
</style>
