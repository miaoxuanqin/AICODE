<template>
  <el-dialog
    v-model="visible"
    :title="knowledge?.title || '知识详情'"
    width="900px"
    top="5vh"
    :close-on-click-modal="true"
  >
    <div v-loading="loading" class="detail-content">
      <!-- 操作按钮 -->
      <div class="detail-actions" v-if="knowledge">
        <el-button
          :type="knowledge.is_favorited ? 'warning' : 'default'"
          :icon="Star"
          @click="toggleFavorite"
        >
          {{ knowledge.is_favorited ? '已收藏' : '收藏' }}
        </el-button>
        <el-button :icon="ChatLineSquare" @click="scrollToComments">
          评论
        </el-button>
      </div>

      <!-- 元信息 -->
      <div class="detail-meta" v-if="knowledge">
        <el-tag :type="getCategoryType(knowledge.category)">{{ knowledge.category_name }}</el-tag>
        <span class="meta-item">{{ knowledge.source || '未知来源' }}</span>
        <span class="meta-item">{{ formatDate(knowledge.created_at) }}</span>
        <span class="meta-item">{{ knowledge.view_count || 0 }} 浏览</span>
        <span class="meta-item">{{ knowledge.favorite_count || 0 }} 收藏</span>
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
            <!-- 无预览支持提示 -->
            <div v-if="!previewItem.type && hasFile" class="no-preview">
              暂无预览内容
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 内容 -->
      <div class="detail-body" v-if="knowledge?.content" v-html="knowledge.content"></div>
      <div v-else-if="!loading" class="no-content">暂无内容</div>

      <!-- 标签 -->
      <div class="detail-tags" v-if="knowledge?.tags?.length">
        <el-tag v-for="tag in knowledge.tags" :key="tag" style="margin-right: 8px;">
          {{ tag }}
        </el-tag>
      </div>

      <el-divider />

      <!-- 评论区 -->
      <div id="comments-section" class="detail-comments">
        <h4>评论 ({{ comments.length }})</h4>

        <div class="comment-form">
          <el-input
            v-model="newComment"
            type="textarea"
            :rows="2"
            placeholder="请输入评论..."
          />
          <el-button type="primary" style="margin-top: 8px;" @click="submitComment" :loading="commentLoading">
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
        <el-empty v-else description="暂无评论" :image-size="60" />
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { knowledgeApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Star, ChatLineSquare, Loading } from '@element-plus/icons-vue'
import mammoth from 'mammoth'
import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf.mjs'

// 为 legacy build 设置 workerSrc
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL('pdfjs-dist/legacy/build/pdf.worker.min.mjs', import.meta.url).href

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  knowledgeId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const knowledge = ref(null)
const comments = ref([])
const newComment = ref('')
const commentLoading = ref(false)

// 文件预览相关
const activePreviewTab = ref('preview')
const wordContent = ref('')
const previewItem = ref({
  loading: false,
  error: null,
  type: null // 'pdf' | 'docx' | null
})

// 计算是否有文件需要预览
const hasFile = computed(() => {
  return knowledge.value?.file_type && knowledge.value?.file_path
})

const getCategoryType = (category) => {
  const types = { law: 'danger', tech: 'success', case: 'warning', policy: '' }
  return types[category] || ''
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

const loadDetail = async (id) => {
  if (!id) return
  loading.value = true
  previewItem.value = { loading: false, error: null, type: null }
  wordContent.value = ''
  try {
    const res = await knowledgeApi.get(id)
    knowledge.value = res
    await loadComments(id)
    // 如果有文件，加载预览
    if (res.file_type && res.file_path) {
      await loadFilePreview(res)
    }
  } catch (e) {
    console.error('获取知识详情失败:', e)
    ElMessage.error('获取知识详情失败')
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
    const blob = new Blob([rawData], { type: item.file_type === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
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

// PDF 预览 (详情弹窗)
const renderPdfPreviewDetail = async (blob) => {
  console.log('=== Detail PDF 预览开始 ===')
  try {
    const arrayBuffer = await blob.arrayBuffer()
    const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer })
    const pdf = await loadingTask.promise

    // 等待容器出现
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
    console.log('=== Detail PDF 渲染完成 ===')
  } catch (error) {
    console.error('PDF 渲染失败:', error)
    previewItem.value.error = 'PDF渲染失败'
  }
}

// Word 预览 (详情弹窗)
const renderWordPreviewDetail = async (blob) => {
  console.log('=== Detail Word 预览开始 ===')
  try {
    const arrayBuffer = await blob.arrayBuffer()
    const result = await mammoth.convertToHtml({ arrayBuffer })
    wordContent.value = result.value
    console.log('=== Detail Word 渲染完成 ===')
  } catch (error) {
    console.error('Word 渲染失败:', error)
    previewItem.value.error = 'Word渲染失败'
  }
}

const loadComments = async (id) => {
  try {
    const res = await knowledgeApi.comments(id)
    comments.value = res || []
  } catch (e) {
    console.error('获取评论失败:', e)
    comments.value = []
  }
}

const toggleFavorite = async () => {
  if (!knowledge.value) return
  try {
    if (knowledge.value.is_favorited) {
      await knowledgeApi.unfavorite(knowledge.value.id)
      knowledge.value.is_favorited = false
      knowledge.value.favorite_count = (knowledge.value.favorite_count || 1) - 1
    } else {
      await knowledgeApi.favorite(knowledge.value.id)
      knowledge.value.is_favorited = true
      knowledge.value.favorite_count = (knowledge.value.favorite_count || 0) + 1
    }
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  if (!knowledge.value) return
  commentLoading.value = true
  try {
    await knowledgeApi.addComment(knowledge.value.id, newComment.value)
    newComment.value = ''
    await loadComments(knowledge.value.id)
    ElMessage.success('评论成功')
  } catch (e) {
    ElMessage.error('评论失败')
  } finally {
    commentLoading.value = false
  }
}

const scrollToComments = () => {
  const el = document.getElementById('comments-section')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}

watch(() => props.modelValue, (val) => {
  if (val && props.knowledgeId) {
    loadDetail(props.knowledgeId)
  }
})

watch(() => props.knowledgeId, (val) => {
  if (props.modelValue && val) {
    loadDetail(val)
  }
})

const open = (id) => {
  loadDetail(id)
  visible.value = true
}

defineExpose({ open })
</script>

<style scoped>
.detail-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.meta-item {
  color: #666;
  font-size: 14px;
}

.detail-body {
  line-height: 1.8;
  max-height: 500px;
  overflow-y: auto;
}

.detail-tags {
  margin-top: 16px;
}

.no-content {
  color: #999;
  text-align: center;
  padding: 40px;
}

.detail-actions {
  margin-bottom: 16px;
}

.detail-comments {
  margin-top: 16px;
}

.file-preview-section {
  margin-bottom: 16px;
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

.word-preview-container >>> table {
  border-collapse: collapse;
  width: 100%;
}

.word-preview-container >>> td,
.word-preview-container >>> th {
  border: 1px solid #ddd;
  padding: 8px;
}

.no-preview {
  text-align: center;
  padding: 40px;
  color: #999;
}

.comment-form {
  margin-bottom: 16px;
}

.comment-list {
  margin-top: 16px;
}

.comment-item {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-body {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.comment-user {
  font-weight: 500;
  color: #333;
}

.comment-time {
  color: #999;
  font-size: 12px;
}

.comment-content {
  margin: 0;
  color: #666;
  line-height: 1.5;
}
</style>