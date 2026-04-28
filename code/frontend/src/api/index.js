import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 120000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // 支持 AbortController signal
    if (config.signal) {
      config.cancelToken = new axios.CancelToken((cancel) => {
        config._cancel = cancel
      })
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        localStorage.clear()
        router.push('/login')
        ElMessage.error('登录已过期，请重新登录')
      } else if (status === 403) {
        ElMessage.error(data.detail || '没有权限')
      } else {
        ElMessage.error(data.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误')
    }
    return Promise.reject(error)
  }
)

// ============ 用户管理 API ============
export const userApi = {
  list: (params) => request.get('/users/', { params }),
  get: (userId) => request.get(`/users/${userId}`),
  create: (data) => request.post('/users/', data),
  update: (userId, data) => request.patch(`/users/${userId}`, data),
  delete: (userId) => request.delete(`/users/${userId}`),
  assignRoles: (userId, roleIds) => request.post(`/users/${userId}/roles`, roleIds)
}

// ============ 角色管理 API ============
export const roleApi = {
  list: (params) => request.get('/roles/', { params }),
  get: (roleId) => request.get(`/roles/${roleId}`),
  create: (data) => request.post('/roles/', data),
  update: (roleId, data) => request.patch(`/roles/${roleId}`, data),
  delete: (roleId) => request.delete(`/roles/${roleId}`)
}

// ============ 权限管理 API ============
export const permissionApi = {
  list: (params) => request.get('/permissions/', { params })
}

// ============ 知识管理 API ============
export const knowledgeApi = {
  // 上传知识
  upload: (formData) => request.post('/knowledge/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  // 手动创建知识
  createManual: (data) => request.post('/knowledge/manual', data),
  // 知识列表
  list: (params) => request.get('/knowledge', { params }),
  // 知识详情
  get: (id) => request.get(`/knowledge/${id}`),
  // 更新知识
  update: (id, data) => request.put(`/knowledge/${id}`, data),
  // 删除知识
  delete: (id) => request.delete(`/knowledge/${id}`),
  // 搜索知识
  search: (params) => request.get('/knowledge/search', { params }),
  // 热搜词
  hotTerms: (limit) => request.get('/knowledge/search/hot-terms', { params: { limit } }),
  // 搜索建议
  suggest: (q) => request.get('/knowledge/suggest', { params: { q } }),
  // 热门知识
  hot: (limit) => request.get('/knowledge/hot', { params: { limit } }),
  // 最新知识
  latest: (limit) => request.get('/knowledge/latest', { params: { limit } }),
  // 收藏
  favorite: (id) => request.post(`/knowledge/${id}/favorite`),
  unfavorite: (id) => request.delete(`/knowledge/${id}/favorite`),
  // 评论
  comments: (id) => request.get(`/knowledge/${id}/comments`),
  addComment: (id, content) => request.post(`/knowledge/${id}/comments`, { content })
}

// ============ 问答助手 API ============
export const qaApi = {
  // ============ 会话管理 ============
  // 创建新会话
  createSession: (title = '新对话', category = 'qa') =>
    request.post('/qa/session', { title, category }),
  // 获取用户所有会话
  getSessions: () => request.get('/qa/sessions'),
  // 获取会话详情（含消息历史）
  getSession: (sessionId) => request.get(`/qa/session/${sessionId}`),
  // 删除会话
  deleteSession: (sessionId) => request.delete(`/qa/session/${sessionId}`),
  // 清除会话消息
  clearMessages: (sessionId) => request.delete(`/qa/session/${sessionId}/messages`),

  // ============ 问答 ============
  // 问答对话（支持会话）
  chat: (question, userId, sessionId) =>
    request.post('/qa/chat', {
      question,
      user_id: userId,
      session_id: sessionId
    }),
  // 问答统计
  stats: () => request.get('/qa/stats'),
  // 热门问题
  hotQuestions: (limit) => request.get('/qa/hot-questions', { params: { limit } }),
  // 评价
  rate: (questionId, rating) => request.post('/qa/rate', { question_id: questionId, rating }),
  // 历史记录
  history: (limit) => request.get('/qa/history', { params: { limit } })
}

// ============ 图谱问答 API ============
export const graphApi = {
  // 图谱增强问答
  qa: (question, useNeo4j = false) =>
    request.post('/graph/qa', { question, use_neo4j: useNeo4j }),
  // 提取实体
  extractEntities: (text) => request.get('/graph/entity/extract', { params: { q: text } }),
  // 构建图谱
  buildGraph: (entities) => request.post('/graph/graph/build', entities)
}

export default request
