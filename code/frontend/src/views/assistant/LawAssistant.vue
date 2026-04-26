<template>
  <div class="assistant-page">
    <div class="page-header">
      <h2>执法智能助手</h2>
      <p class="subtitle">基于知识图谱的执法处置方案推荐</p>
    </div>

    <el-row :gutter="24">
      <el-col :span="16">
        <!-- 对话区域 -->
        <el-card class="chat-card">
          <template #header>
            <div class="chat-header">
              <span>执法处置推荐</span>
              <el-button text @click="clearHistory">
                <el-icon><Delete /></el-icon> 清空对话
              </el-button>
            </div>
          </template>

          <div class="chat-messages" ref="chatMessagesRef">
            <div v-if="!messages.length && !isThinking" class="empty-state">
              <el-icon class="empty-icon"><Service /></el-icon>
              <p>请描述您的执法场景，我将为您提供处置方案推荐和相关法律法规参考</p>
            </div>

            <div v-for="(msg, index) in messages" :key="index" class="chat-message">
              <div :class="['message', msg.role]">
                <div class="message-avatar">
                  <el-avatar :size="36" :icon="msg.role === 'user' ? 'User' : 'Service'" />
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="sender-name">{{ msg.role === 'user' ? '我' : '执法助手' }}</span>
                    <span class="message-time">{{ msg.time }}</span>
                  </div>
                  <div class="message-body">
                    <div v-html="renderMarkdown(msg.content)"></div>

                    <!-- 知识卡片 -->
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
                          <el-tag size="small">{{ card.category || '知识' }}</el-tag>
                          <span class="confidence">
                            <el-icon><Star /></el-icon>
                            置信度 {{ card.confidence || 0 }}%
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
                </div>
              </div>
            </div>

            <!-- 思考中提示 -->
            <div v-if="isThinking" class="chat-message">
              <div class="message assistant">
                <div class="message-avatar">
                  <el-avatar :size="36" :icon="Service" />
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="sender-name">执法助手</span>
                  </div>
                  <div class="message-body thinking">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    <span>正在检索知识库并生成回答，请稍候...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="chat-input">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="3"
              placeholder="请描述执法场景，例如：某工地未按规定进行施工，导致安全隐患..."
              @keydown.enter.meta="handleSend"
              @keydown.enter.ctrl="handleSend"
            />
            <div class="input-actions">
              <el-upload
                :show-file-list="false"
                action="#"
                :before-upload="() => false"
              >
                <el-button text>
                  <el-icon><Upload /></el-icon>
                  上传附件
                </el-button>
              </el-upload>
              <el-button type="primary" @click="handleSend" :disabled="!inputMessage.trim()">
                <el-icon><Promotion /></el-icon>
                发送
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <!-- 场景选择 -->
        <el-card class="scene-card">
          <template #header>
            <span>执法场景模板</span>
          </template>
          <div class="scene-list">
            <div
              v-for="scene in scenes"
              :key="scene.id"
              class="scene-item"
              @click="selectScene(scene)"
            >
              <el-icon><FolderOpened /></el-icon>
              <span>{{ scene.name }}</span>
            </div>
          </div>
        </el-card>

        <!-- 推荐知识 -->
        <el-card class="knowledge-card">
          <template #header>
            <span>关联知识</span>
          </template>
          <div v-if="isLoadingKnowledge" class="loading-knowledge">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>
          <div v-else-if="relatedKnowledge.length === 0" class="empty-knowledge">
            <span>暂无关联知识</span>
          </div>
          <div v-else class="knowledge-list">
            <div
              v-for="item in relatedKnowledge"
              :key="item.id"
              class="knowledge-item"
              @click="viewKnowledge(item)"
            >
              <el-tag size="small" :type="getCategoryType(item.type)">
                {{ item.typeName }}
              </el-tag>
              <p>{{ item.title }}</p>
            </div>
          </div>
        </el-card>

        <!-- 历史记录 -->
        <el-card class="history-card">
          <template #header>
            <span>最近案例</span>
          </template>
          <div v-if="recentCases.length === 0" class="empty-cases">
            <span>暂无案例记录</span>
          </div>
          <div v-else class="history-list">
            <div
              v-for="item in recentCases"
              :key="item.id"
              class="history-item"
              @click="viewCase(item)"
            >
              <span>{{ item.title }}</span>
              <el-tag size="small" type="success">{{ item.result }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Delete, Service, Upload, Promotion, Loading,
  FolderOpened, User, Star
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import { qaApi, knowledgeApi } from '@/api'
import request from '@/api'

// 配置 marked
marked.setOptions({
  breaks: true,  // 换行符转为 <br>
  gfm: true     // GitHub 风格 Markdown
})

const inputMessage = ref('')
const isThinking = ref(false)
const messages = ref([])
const chatMessagesRef = ref(null)

// 会话管理
const currentSessionId = ref(null)

// 缓存 user_id
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

const scenes = [
  { id: 1, name: '工地安全违规' },
  { id: 2, name: '违法建设' },
  { id: 3, name: '施工许可违规' },
  { id: 4, name: '质量安全隐患' },
  { id: 5, name: '扬尘污染' },
  { id: 6, name: '综合执法通用' }
]

// 关联知识 - 动态加载
const relatedKnowledge = ref([])
const isLoadingKnowledge = ref(false)

// 最近案例 - 复用执法助手会话历史
const recentCases = ref([])

const getCategoryType = (type) => {
  const types = { law: 'danger', case: 'warning', tech: 'success', policy: 'info' }
  return types[type] || 'info'
}

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

// 加载关联知识
const loadRelatedKnowledge = async (query) => {
  if (!query || !query.trim()) return

  isLoadingKnowledge.value = true
  try {
    const result = await knowledgeApi.search({ q: query, page: 1, page_size: 5 })
    relatedKnowledge.value = (result.items || []).map(item => ({
      id: item.id,
      type: item.category || 'tech',
      typeName: getTypeName(item.category),
      title: item.title,
      summary: item.summary || item.content?.slice(0, 100) || ''
    }))
  } catch (error) {
    console.error('加载关联知识失败:', error)
    relatedKnowledge.value = []
  } finally {
    isLoadingKnowledge.value = false
  }
}

// 获取类型名称
const getTypeName = (category) => {
  const names = { law: '法律', case: '案例', tech: '技术', policy: '政策' }
  return names[category] || '知识'
}

// 加载最近案例 - 从执法助手会话历史获取
const loadRecentCases = async () => {
  if (!currentSessionId.value) {
    recentCases.value = []
    return
  }

  try {
    const data = await qaApi.getSession(currentSessionId.value)
    if (data && data.messages) {
      // 获取用户的问题作为案例
      const userMessages = data.messages
        .filter(m => m.role === 'user')
        .slice(-5)
        .reverse()

      recentCases.value = userMessages.map((m, index) => ({
        id: m.id || index,
        title: m.content.length > 20 ? m.content.slice(0, 20) + '...' : m.content,
        result: '已处理'
      }))
    }
  } catch (error) {
    console.error('加载最近案例失败:', error)
    recentCases.value = []
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    chatMessagesRef.value?.scrollTo({
      top: chatMessagesRef.value.scrollHeight,
      behavior: 'smooth'
    })
  })
}

const selectScene = (scene) => {
  inputMessage.value = `【${scene.name}】请推荐处置方案`
}

const selectQuestion = (question) => {
  inputMessage.value = question
  handleSend()
}

const handleSend = async () => {
  if (!inputMessage.value.trim()) return

  const userMsg = {
    role: 'user',
    content: inputMessage.value,
    time: new Date().toLocaleTimeString()
  }
  messages.value.push(userMsg)
  inputMessage.value = ''
  isThinking.value = true

  scrollToBottom()

  try {
    const userId = cachedUserId || await ensureUserId()
    const result = await qaApi.chat(userMsg.content, userId, currentSessionId.value)

    const aiMsg = {
      role: 'assistant',
      content: result.answer,
      cards: result.cards || [],
      relatedQuestions: result.related_questions || [],
      time: new Date().toLocaleTimeString()
    }
    messages.value.push(aiMsg)

    if (result.session_id && result.session_id !== currentSessionId.value) {
      currentSessionId.value = result.session_id
    }

    // 加载关联知识和最近案例
    await Promise.all([
      loadRelatedKnowledge(userMsg.content),
      loadRecentCases()
    ])
  } catch (error) {
    ElMessage.error('问答服务出错，请稍后重试')
    console.error('QA error:', error)
  } finally {
    isThinking.value = false
  }

  scrollToBottom()
}

const viewCard = (card) => {
  window.location.href = `/knowledge/detail/${card.id}`
}

const viewKnowledge = (item) => {
  window.location.href = `/knowledge/detail/${item.id}`
}

const viewCase = (item) => {
  // 点击案例时，将内容填充到输入框
  inputMessage.value = item.title
}

const clearHistory = () => {
  messages.value = []
  currentSessionId.value = null
  relatedKnowledge.value = []
  recentCases.value = []
}

const initSession = async () => {
  try {
    console.log('=== initSession 开始 ===')
    // 先获取已有的执法助手会话
    const sessionsData = await qaApi.getSessions()
    console.log('所有会话:', sessionsData)
    const lawSessions = (sessionsData.items || []).filter(s => s.category === 'law_general')
    console.log('执法助手会话:', lawSessions)

    if (lawSessions.length > 0) {
      console.log('使用已有会话:', lawSessions[0].id)
      // 使用最新的执法会话
      currentSessionId.value = lawSessions[0].id
      await loadSessionHistory()
    } else {
      console.log('创建新会话')
      // 创建新会话
      const data = await qaApi.createSession('【执法】新对话', 'law_general')
      console.log('创建会话返回:', data)
      currentSessionId.value = data.id
    }
    console.log('=== initSession 结束 ===')
  } catch (error) {
    console.error('初始化执法会话失败:', error)
  }
}

const loadSessionHistory = async () => {
  if (!currentSessionId.value) {
    console.log('loadSessionHistory: 无sessionId')
    return
  }

  console.log('loadSessionHistory: 加载会话', currentSessionId.value)
  try {
    const data = await qaApi.getSession(currentSessionId.value)
    console.log('会话详情:', data)
    if (data && data.messages) {
      messages.value = data.messages.map(m => ({
        role: m.role,
        content: m.content,
        time: m.time
      }))
      console.log('消息列表:', messages.value)
    }

    // 加载关联知识（从最后一条用户消息获取关键词）
    const lastUserMsg = messages.value.filter(m => m.role === 'user').slice(-1)[0]
    if (lastUserMsg) {
      console.log('加载关联知识，关键词:', lastUserMsg.content)
      await loadRelatedKnowledge(lastUserMsg.content)
    }

    // 加载最近案例
    await loadRecentCases()
  } catch (error) {
    console.error('加载会话历史失败:', error)
  }
}

onMounted(async () => {
  await ensureUserId()
  await initSession()
})
</script>

<style scoped>
.assistant-page {
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

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.message.assistant .message-header {
  flex-direction: row;
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

/* 知识卡片 */
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

/* 相关问题 */
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

.loading {
  animation: rotating 2s linear infinite;
  margin-right: 8px;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
}

.scene-card,
.knowledge-card,
.history-card {
  margin-bottom: 16px;
}

.scene-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.scene-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.scene-item:hover {
  background: #e4e7ed;
  color: #409eff;
}

.knowledge-list,
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.knowledge-item p,
.history-item span {
  margin: 6px 0 0 0;
  font-size: 14px;
  color: #606266;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

/* 关联知识 */
.knowledge-item {
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.knowledge-item:hover {
  background: #f5f7fa;
}

.loading-knowledge,
.empty-knowledge,
.empty-cases {
  text-align: center;
  padding: 20px;
  color: #909399;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.history-item {
  cursor: pointer;
  transition: background 0.2s;
  padding: 8px;
  border-radius: 4px;
}

.history-item:hover {
  background: #f5f7fa;
}
</style>
