<template>
  <div class="knowledge-detail">
    <el-page-header @back="goBack" content="知识详情">
      <template #extra>
        <div class="header-actions">
          <el-button :icon="Star" :type="knowledge.is_favorited ? 'warning' : 'default'" @click="toggleFavorite">
            {{ knowledge.is_favorited ? '已收藏' : '收藏' }}
          </el-button>
          <el-button :icon="ChatLineSquare" @click="showCommentDialog = true">评论</el-button>
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
        <div class="comments card-container">
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Star, ChatLineSquare, Document, Calendar, View, CaretTop
} from '@element-plus/icons-vue'
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
  try {
    const id = route.params.id
    const res = await knowledgeApi.get(id)
    Object.assign(knowledge, res)
  } catch (error) {
    console.error('加载知识详情失败', error)
    ElMessage.error('加载知识详情失败')
  } finally {
    loading.value = false
  }
}

const loadComments = async () => {
  try {
    const id = route.params.id
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

onMounted(() => {
  loadKnowledgeDetail()
  loadComments()
})
</script>

<style scoped>
.knowledge-detail {
  max-width: 1400px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.content-wrapper {
  margin-top: 24px;
}

.main-content {
  padding: 32px;
}

.title {
  margin: 0 0 16px 0;
  font-size: 28px;
  color: #303133;
}

.meta {
  display: flex;
  align-items: center;
  gap: 20px;
  color: #909399;
  font-size: 14px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.content-body {
  line-height: 1.8;
  font-size: 15px;
  color: #303133;
}

.content-body p {
  margin: 12px 0;
}

.tags {
  margin-top: 16px;
}

.info-card {
  font-size: 14px;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-item {
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background 0.3s;
}

.related-item:hover {
  background: #f5f7fa;
}

.related-item p {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: #606266;
}

.comments {
  margin-top: 24px;
  padding: 24px;
}

.comments h3 {
  margin: 0 0 20px 0;
}

.comment-form {
  margin-bottom: 24px;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment-item {
  display: flex;
  gap: 12px;
}

.comment-body {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-user {
  font-weight: 600;
  color: #303133;
}

.comment-time {
  color: #c0c4cc;
  font-size: 13px;
}

.comment-content {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.card-container {
  background: #fff;
  border-radius: 8px;
}
</style>
