<template>
  <div class="knowledge-detail">
    <el-page-header @back="goBack" content="知识详情">
      <template #extra>
        <div class="header-actions">
          <el-button :icon="Star" :type="knowledge.is_favorited ? 'warning' : 'default'" @click="toggleFavorite">
            {{ knowledge.is_favorited ? '已收藏' : '收藏' }}
          </el-button>
          <el-button :icon="ChatLineSquare" @click="scrollToComments">评论</el-button>
        </div>
      </template>
    </el-page-header>

    <el-row :gutter="24" class="content-wrapper" v-loading="loading">
      <!-- 主内容 -->
      <el-col :span="18">
        <div class="main-content card-container">
          <h1 class="title">{{ knowledge.title }}</h1>

          <div class="meta">
            <el-tag :type="getCategoryType(knowledge.category)">{{ knowledge.category_name }}</el-tag>
            <span class="meta-item">
              <el-icon><Document /></el-icon>
              {{ knowledge.source || '未知来源' }}
            </span>
            <span class="meta-item">
              <el-icon><Calendar /></el-icon>
              {{ formatDate(knowledge.created_at) }}
            </span>
            <span class="meta-item">
              <el-icon><View /></el-icon>
              {{ knowledge.view_count }} 浏览
            </span>
          </div>

          <el-divider />

          <!-- 文件预览区域 -->
          <div v-if="hasFile" class="file-preview-section">
            <el-tabs v-model="activePreviewTab" type="border-card">
              <el-tab-pane label="文件预览" name="preview">
                <div v-if="previewItem.loading" class="preview-loading">
                  <el-icon class="is-loading"><Loading /></el-icon>
                  正在加载文件预览...
                </div>
                <div v-else-if="previewItem.error" class="preview-error">
                  {{ previewItem.error }}
                </div>
                <!-- PDF预览容器 -->
                <div v-show="previewItem.type === 'pdf'" id="pdf-preview-container-detail" class="pdf-preview-container"></div>
                <!-- Word预览容器 -->
                <div v-show="previewItem.type === 'docx'" class="word-preview-container" v-html="wordContent"></div>
                <div v-if="!previewItem.type && hasFile" class="no-preview">
                  暂无预览内容
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>

          <div class="content-body" v-html="knowledge.content"></div>

          <el-divider />

          <!-- 标签 -->
          <div class="tags" v-if="knowledge.tags?.length">
            <el-tag v-for="tag in knowledge.tags" :key="tag" style="margin-right: 8px;">
              {{ tag }}
            </el-tag>
          </div>
        </div>

        <!-- 评论区 -->
        <div id="comments-section" class="comments card-container">
          <h3>评论 ({{ comments.length }})</h3>

          <div class="comment-form">
            <el-input
              v-model="newComment"
              type="textarea"
              :rows="3"
              placeholder="请输入评论..."
            />
            <el-button type="primary" style="margin-top: 12px;" @click="submitComment" :loading="commentLoading">
              发表评论
            </el-button>
          </div>

          <div class="comment-list" v-if="comments.length">
            <div v-for="comment in comments" :key="comment.id" class="comment-item">
              <div class="comment-avatar">
                <el-avatar>{{ comment.user_name?.charAt(0) || 'U' }}</el-avatar>
              </div>
              <div class="comment-body">
                <div class="comment-header">
                  <span class="comment-user">{{ comment.user_name || '未知用户' }}</span>
                  <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
                </div>
                <p class="comment-content">{{ comment.content }}</p>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无评论" />
        </div>
      </el-col>

      <!-- 侧边栏 -->
      <el-col :span="6">
        <!-- 知识信息 -->
        <el-card class="info-card">
          <template #header>
            <span>知识信息</span>
          </template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="分类">
              <el-tag :type="getCategoryType(knowledge.category)" size="small">
                {{ knowledge.category_name }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="来源">
              {{ knowledge.source || '未知' }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDate(knowledge.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="浏览次数">
              {{ knowledge.view_count }}
            </el-descriptions-item>
            <el-descriptions-item label="收藏次数">
              {{ knowledge.favorite_count }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 标签 -->
        <el-card class="info-card" style="margin-top: 16px;" v-if="knowledge.tags?.length">
          <template #header>
            <span>标签</span>
          </template>
          <el-tag
            v-for="tag in knowledge.tags"
            :key="tag"
            style="margin: 4px;"
          >
            {{ tag }}
          </el-tag>
        </el-card>

        <!-- 相关知识 -->
        <el-card class="info-card" style="margin-top: 16px;">
          <template #header>
            <span>相关知识</span>
          </template>
          <div class="related-list">
            <div
              v-for="item in relatedKnowledge"
              :key="item.id"
              class="related-item"
              @click="goToRelated(item.id)"
            >
              <el-tag :type="getCategoryType(item.category)" size="small">
                {{ item.category_name }}
              </el-tag>
              <p>{{ item.title }}</p>
            </div>
            <el-empty v-if="!relatedKnowledge.length" description="暂无相关知识" :image-size="60" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Star, ChatLineSquare, Document, Calendar, View, CaretTop, Loading
} from '@element-plus/icons-vue'
import mammoth from 'mammoth'
import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf.mjs'

// 为 legacy build 设置 workerSrc
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL('pdfjs-dist/legacy/build/pdf.worker.min.mjs', import.meta.url).href
import { knowledgeApi } from '@/api'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const commentLoading = ref(false)
const showCommentDialog = ref(false)
const newComment = ref('')

const knowledge = reactive({
  id: '',
  title: '',
  content: '',
  summary: '',
  category: '',
  category_name: '',
  source: '',
  tags: [],
  view_count: 0,
  favorite_count: 0,
  is_favorited: false,
  created_at: ''
})

const comments = ref([])
const relatedKnowledge = ref([])

// 文件预览相关
const activePreviewTab = ref('preview')
const wordContent = ref('')
const previewItem = ref({
  loading: false,
  error: null,
  type: null
})

// 计算是否有文件需要预览
const hasFile = computed(() => {
  return knowledge.file_type && knowledge.file_path
})

const categoryMap = {
  law: 'danger',
  tech: 'success',
  case: 'warning',
  policy: 'info'
}

const getCategoryType = (category) => categoryMap[category] || 'info'

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadKnowledgeDetail = async () => {
  loading.value = true
  previewItem.value = { loading: false, error: null, type: null }
  wordContent.value = ''
  try {
    const id = route.params.id
    if (!id) {
      loading.value = false
      return
    }
    const res = await knowledgeApi.get(id)
    Object.assign(knowledge, res)
    // 如果有文件，加载预览
    if (res.file_type && res.file_path) {
      await loadFilePreview(res)
    }
  } catch (error) {
    console.error('加载知识详情失败', error)
    ElMessage.error('加载知识详情失败')
  } finally {
    loading.value = false
  }
}

// 加载文件预览
const loadFilePreview = async (item) => {
  if (!item.file_type || !item.file_path) return
  previewItem.value.loading = true
  previewItem.value.error = null
  previewItem.value.type = item.file_type

  try {
    const response = await knowledgeApi.download(item.id)
    // 处理 axios response.data 或直接返回 data 的情况
    const rawData = response.data || response
    const blob = new Blob([rawData], {
      type: item.file_type === 'pdf'
        ? 'application/pdf'
        : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    })
    console.log('文件下载完成, blob size:', blob.size, 'type:', blob.type)

    if (item.file_type === 'pdf') {
      await renderPdfPreviewDetail(blob)
    } else if (item.file_type === 'docx') {
      await renderWordPreviewDetail(blob)
    }
  } catch (e) {
    console.error('文件预览加载失败:', e)
    previewItem.value.error = '文件预览加载失败'
  } finally {
    previewItem.value.loading = false
  }
}

// PDF 预览 (详情页)
const renderPdfPreviewDetail = async (blob) => {
  console.log('=== Detail Page PDF 预览开始 ===')
  try {
    const arrayBuffer = await blob.arrayBuffer()
    const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer })
    const pdf = await loadingTask.promise

    let container = document.getElementById('pdf-preview-container-detail')
    let waitCount = 0
    while (!container && waitCount < 100) {
      await new Promise(r => setTimeout(r, 100))
      container = document.getElementById('pdf-preview-container-detail')
      waitCount++
    }
    if (!container) {
      console.log('PDF容器不存在')
      return
    }

    container.innerHTML = ''
    container.style.overflow = 'auto'
    container.style.maxHeight = '60vh'

    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i)
      const scale = 1.2
      const viewport = page.getViewport({ scale })

      const canvas = document.createElement('canvas')
      canvas.style.display = 'block'
      canvas.style.margin = '0 auto 10px'
      canvas.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)'
      const context = canvas.getContext('2d')
      canvas.height = viewport.height
      canvas.width = viewport.width

      await page.render({ canvasContext: context, viewport }).promise
      container.appendChild(canvas)
    }
    console.log('=== Detail Page PDF 渲染完成 ===')
  } catch (error) {
    console.error('PDF 渲染失败:', error)
    previewItem.value.error = 'PDF渲染失败'
  }
}

// Word 预览 (详情页)
const renderWordPreviewDetail = async (blob) => {
  console.log('=== Detail Page Word 预览开始 ===')
  try {
    const arrayBuffer = await blob.arrayBuffer()
    const result = await mammoth.convertToHtml({ arrayBuffer })
    wordContent.value = result.value
    console.log('=== Detail Page Word 渲染完成 ===')
  } catch (error) {
    console.error('Word 渲染失败:', error)
    previewItem.value.error = 'Word渲染失败'
  }
}

const loadComments = async () => {
  try {
    const id = route.params.id
    if (!id) return
    comments.value = await knowledgeApi.comments(id)
  } catch (error) {
    console.error('加载评论失败', error)
  }
}

const loadRelatedKnowledge = async () => {
  try {
    const res = await knowledgeApi.search({ q: knowledge.title, page_size: 5 })
    relatedKnowledge.value = res.items.filter(item => item.id !== route.params.id).slice(0, 5)
  } catch (error) {
    console.error('加载相关知识失败', error)
  }
}

const toggleFavorite = async () => {
  try {
    const id = route.params.id
    if (knowledge.is_favorited) {
      await knowledgeApi.unfavorite(id)
      knowledge.is_favorited = false
      knowledge.favorite_count--
    } else {
      await knowledgeApi.favorite(id)
      knowledge.is_favorited = true
      knowledge.favorite_count++
    }
  } catch (error) {
    console.error('收藏操作失败', error)
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }

  commentLoading.value = true
  try {
    const id = route.params.id
    const comment = await knowledgeApi.addComment(id, newComment.value)
    comments.value.unshift(comment)
    newComment.value = ''
    ElMessage.success('评论成功')
  } catch (error) {
    console.error('评论失败', error)
    ElMessage.error('评论失败')
  } finally {
    commentLoading.value = false
  }
}

const goBack = () => {
  router.back()
}

const goToRelated = (id) => {
  router.push(`/knowledge/detail/${id}`)
}

const scrollToComments = () => {
  document.getElementById('comments-section')?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(async () => {
  await loadKnowledgeDetail()
  if (route.params.id) {
    await loadComments()
  }
})

watch(() => route.params.id, async (newId) => {
  if (newId) {
    await loadKnowledgeDetail()
    await loadComments()
  }
})
</script>

<style scoped>
.knowledge-detail {
  max-width: 1400px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.header-actions :deep(.el-button) {
  border-radius: var(--border-radius-sm);
  transition: all var(--transition-fast);
}

.header-actions :deep(.el-button:hover) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.content-wrapper {
  margin-top: 24px;
}

.main-content {
  padding: 32px;
  border-radius: var(--border-radius);
}

.title {
  margin: 0 0 18px 0;
  font-size: 30px;
  color: var(--text-primary);
  font-weight: 700;
  line-height: 1.4;
}

.meta {
  display: flex;
  align-items: center;
  gap: 24px;
  color: var(--text-secondary);
  font-size: 14px;
  flex-wrap: wrap;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-item .el-icon {
  color: var(--primary-color);
}

.content-body {
  line-height: 1.8;
  font-size: 15px;
  color: var(--text-primary);
  padding: 24px 0;
}

.content-body p {
  margin: 14px 0;
}

.tags {
  margin-top: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.info-card {
  font-size: 14px;
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
}

.info-card:hover {
  box-shadow: var(--shadow-md);
}

.info-card :deep(.el-card__header) {
  background: var(--primary-gradient);
  color: #fff;
  padding: 14px 18px;
  font-weight: 600;
  border-bottom: none;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.related-item {
  cursor: pointer;
  padding: 10px;
  border-radius: var(--border-radius-sm);
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}

.related-item:hover {
  background: var(--bg-color);
  border-color: var(--accent-light);
}

.related-item :deep(.el-tag) {
  margin-bottom: 8px;
}

.related-item p {
  margin: 0;
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.5;
}

/* 评论区样式 */
.comments {
  margin-top: 24px;
  padding: 28px;
  border-radius: var(--border-radius);
}

.comments h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: var(--text-primary);
  font-weight: 600;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--accent-light);
  display: inline-block;
}

.comment-form {
  margin-bottom: 28px;
  padding: 20px;
  background: var(--bg-color);
  border-radius: var(--border-radius);
}

.comment-form :deep(.el-textarea__inner) {
  border-radius: var(--border-radius-sm);
}

.comment-form :deep(.el-button) {
  margin-top: 12px;
  border-radius: var(--border-radius-sm);
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.comment-item {
  display: flex;
  gap: 14px;
  padding: 16px;
  background: var(--bg-color);
  border-radius: var(--border-radius);
  transition: all var(--transition-fast);
}

.comment-item:hover {
  background: #fff;
  box-shadow: var(--shadow-sm);
}

.comment-body {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.comment-user {
  font-weight: 600;
  color: var(--primary-color);
  font-size: 14px;
}

.comment-time {
  color: var(--text-light);
  font-size: 12px;
}

.comment-content {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 14px;
}

.comment-item :deep(.el-avatar) {
  border: 2px solid var(--primary-light);
}

.card-container {
  background: #fff;
  border-radius: var(--border-radius);
}

.file-preview-section {
  margin: 20px 0;
}

.preview-loading {
  text-align: center;
  padding: 40px;
  color: #999;
}

.preview-error {
  text-align: center;
  padding: 40px;
  color: #f56c6c;
}

.pdf-preview-container {
  padding: 16px;
  background: #f5f5f5;
  border-radius: 4px;
}

.pdf-preview-container canvas {
  display: block;
  margin: 0 auto 10px;
}

.word-preview-container {
  padding: 16px;
  background: #f5f5f5;
  border-radius: 4px;
  max-height: 60vh;
  overflow: auto;
}

.word-preview-container :deep(table) {
  border-collapse: collapse;
  width: 100%;
}

.word-preview-container :deep(td),
.word-preview-container :deep(th) {
  border: 1px solid #ddd;
  padding: 8px;
}

.no-preview {
  text-align: center;
  padding: 40px;
  color: #999;
}
</style>
