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
import { Star, ChatLineSquare } from '@element-plus/icons-vue'

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
  try {
    const res = await knowledgeApi.get(id)
    knowledge.value = res
    await loadComments(id)
  } catch (e) {
    console.error('获取知识详情失败:', e)
    ElMessage.error('获取知识详情失败')
  } finally {
    loading.value = false
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