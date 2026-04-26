<template>
  <div class="assistant-page">
    <div class="page-header">
      <h2>工程监管智能助手</h2>
      <p class="subtitle">基于知识图谱的工程质量安全问题定位与处置推荐</p>
    </div>

    <el-row :gutter="24">
      <el-col :span="16">
        <el-card class="chat-card">
          <template #header>
            <div class="chat-header">
              <span>工程监管辅助</span>
              <el-button text @click="clearHistory">
                <el-icon><Delete /></el-icon> 清空对话
              </el-button>
            </div>
          </template>

          <div class="chat-messages" ref="chatMessagesRef">
            <div v-if="!messages.length && !isThinking" class="empty-state">
              <el-icon class="empty-icon"><Monitor /></el-icon>
              <p>请描述工程现场发现的问题，我将为您提供相关的技术标准、规范要求和处置建议</p>
            </div>

            <div v-for="(msg, index) in messages" :key="index" class="chat-message">
              <div :class="['message', msg.role]">
                <div class="message-avatar">
                  <el-avatar :size="36" :icon="msg.role === 'user' ? 'User' : 'Monitor'" />
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="sender-name">{{ msg.role === 'user' ? '我' : '监管助手' }}</span>
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
                          <el-tag size="small">{{ card.type || '知识' }}</el-tag>
                          <span class="confidence">
                            <el-icon><Star /></el-icon>
                            置信度 {{ card.confidence || 0 }}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 思考中提示 -->
            <div v-if="isThinking" class="chat-message">
              <div class="message assistant">
                <div class="message-avatar">
                  <el-avatar :size="36" :icon="Monitor" />
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="sender-name">监管助手</span>
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
              placeholder="请描述工程现场发现的问题，例如：某工地混凝土强度不达标..."
              @keydown.enter.ctrl="handleSend"
            />
            <div class="input-actions">
              <el-button type="primary" @click="handleSend" :disabled="!inputMessage.trim()">
                <el-icon><Promotion /></el-icon>
                发送
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <!-- 问题类型 -->
        <el-card class="type-card">
          <template #header>
            <span>常见问题类型</span>
          </template>
          <el-tag-group>
            <el-tag
              v-for="type in problemTypes"
              :key="type.id"
              :type="type.type"
              style="margin: 4px; cursor: pointer;"
              @click="selectProblem(type)"
            >
              {{ type.name }}
            </el-tag>
          </el-tag-group>
        </el-card>

        <!-- 关联知识 -->
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

        <!-- 处置记录 -->
        <el-card class="record-card">
          <template #header>
            <span>最近监管记录</span>
          </template>
          <div v-if="recentRecords.length === 0" class="empty-records">
            <span>暂无记录</span>
          </div>
          <div v-else class="record-list">
            <div
              v-for="item in recentRecords"
              :key="item.id"
              class="record-item"
              @click="selectRecord(item)"
            >
              <span class="record-title">{{ item.title }}</span>
              <el-tag size="small" type="success">{{ item.statusName }}</el-tag>
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
  Delete, Promotion, Document, User, Monitor, Loading, Star
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import { qaApi, knowledgeApi } from '@/api'
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

// 会话管理
const currentSessionId = ref(null)

// 关联知识
const relatedKnowledge = ref([])
const isLoadingKnowledge = ref(false)

// 最近记录（复用会话历史）
const recentRecords = ref([])

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
      userId = '1'
    }
  }
  cachedUserId = userId || '1'
  return cachedUserId
}

// 渲染 Markdown
const renderMarkdown = (content) => {
  if (!content) return ''
  try {
    return marked(content)
  } catch (e) {
    return content
  }
}

// 问题类型（静态数据）
const problemTypes = [
  { id: 1, name: '混凝土强度不足', type: 'danger' },
  { id: 2, name: '钢筋配置不规范', type: 'warning' },
  { id: 3, name: '防水工程缺陷', type: 'warning' },
  { id: 4, name: '脚手架安全隐患', type: 'danger' },
  { id: 5, name: '施工缝处理不当', type: '' },
  { id: 6, name: '材料以次充好', type: 'danger' }
]

const getCategoryType = (type) => {
  const types = { law: 'danger', case: 'warning', tech: 'success', policy: 'info' }
  return types[type] || 'info'
}

const getTypeName = (category) => {
  const names = { law: '法律', case: '案例', tech: '技术', policy: '政策' }
  return names[category] || '知识'
}

// 初始化会话
const initSession = async () => {
  try {
    const sessionsData = await qaApi.getSessions()
    const superviseSessions = (sessionsData.items || []).filter(s => s.category === 'supervise')

    if (superviseSessions.length > 0) {
      currentSessionId.value = superviseSessions[0].id
      await loadSessionHistory()
    } else {
      const data = await qaApi.createSession('【监管】新对话', 'supervise')
      currentSessionId.value = data.id
    }
  } catch (error) {
    console.error('初始化监管会话失败:', error)
  }
}

// 加载会话历史
const loadSessionHistory = async () => {
  if (!currentSessionId.value) return

  try {
    const data = await qaApi.getSession(currentSessionId.value)
    if (data && data.messages) {
      messages.value = data.messages.map(m => ({
        role: m.role,
        content: m.content,
        time: m.time
      }))
    }

    // 加载关联知识
    const lastUserMsg = messages.value.filter(m => m.role === 'user').slice(-1)[0]
    if (lastUserMsg) {
      await loadRelatedKnowledge(lastUserMsg.content)
    }

    // 加载最近记录
    await loadRecentRecords()
  } catch (error) {
    console.error('加载会话历史失败:', error)
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
      title: item.title
    }))
  } catch (error) {
    console.error('加载关联知识失败:', error)
    relatedKnowledge.value = []
  } finally {
    isLoadingKnowledge.value = false
  }
}

// 加载最近记录（复用会话历史）
const loadRecentRecords = async () => {
  if (!currentSessionId.value) {
    recentRecords.value = []
    return
  }

  try {
    const data = await qaApi.getSession(currentSessionId.value)
    if (data && data.messages) {
      const userMessages = data.messages
        .filter(m => m.role === 'user')
        .slice(-5)
        .reverse()

      recentRecords.value = userMessages.map((m, index) => ({
        id: m.id || index,
        title: m.content.length > 20 ? m.content.slice(0, 20) + '...' : m.content,
        statusName: '已处理'
      }))
    }
  } catch (error) {
    console.error('加载最近记录失败:', error)
    recentRecords.value = []
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

const selectProblem = (type) => {
  inputMessage.value = `现场发现${type.name}问题，请提供处置建议`
}

const selectRecord = (item) => {
  inputMessage.value = item.title
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
      time: new Date().toLocaleTimeString()
    }
    messages.value.push(aiMsg)

    if (result.session_id && result.session_id !== currentSessionId.value) {
      currentSessionId.value = result.session_id
    }

    // 动态加载关联知识和记录
    await Promise.all([
      loadRelatedKnowledge(userMsg.content),
      loadRecentRecords()
    ])
  } catch (error) {
    ElMessage.error('问答服务出错，请稍后重试')
    console.error('监管助手问答失败:', error)
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

const clearHistory = () => {
  messages.value = []
  currentSessionId.value = null
  relatedKnowledge.value = []
  recentRecords.value = []
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
  background: #f5f7fa;
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

.chat-message {
  margin-bottom: 20px;
}

.message {
  display: flex;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 75%;
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

/* 知识卡片 */
.answer-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
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

.chat-input {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.type-card,
.knowledge-card,
.record-card {
  margin-bottom: 16px;
}

.knowledge-list,
.record-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.knowledge-item {
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.knowledge-item:hover {
  background: #f5f7fa;
}

.knowledge-item p {
  margin: 6px 0 0 0;
  font-size: 14px;
  color: #606266;
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.record-item:hover {
  background: #f5f7fa;
}

.record-title {
  font-size: 14px;
  color: #606266;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.loading-knowledge,
.empty-knowledge,
.empty-records {
  text-align: center;
  padding: 20px;
  color: #909399;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
</style>
