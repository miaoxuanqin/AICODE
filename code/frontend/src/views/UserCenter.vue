<template>
  <div class="user-center">
    <div class="page-header">
      <h1>个人中心</h1>
    </div>

    <!-- 个人资料卡片 -->
    <el-card class="profile-card" shadow="hover">
      <div class="profile-content">
        <el-avatar :size="72" class="avatar">
          {{ userInfo.full_name?.charAt(0) || 'U' }}
        </el-avatar>
        <div class="profile-info">
          <h2 class="name">{{ userInfo.full_name || '未知用户' }}</h2>
          <div class="meta-list">
            <span class="meta-item">
              <el-icon><User /></el-icon>
              {{ userInfo.username || '-' }}
            </span>
            <span class="meta-item">
              <el-icon><Postcard /></el-icon>
              {{ userInfo.role_name || '普通用户' }}
            </span>
            <span class="meta-item">
              <el-icon><OfficeBuilding /></el-icon>
              {{ userInfo.org_name || '-' }}
            </span>
            <span class="meta-item">
              <el-icon><Calendar /></el-icon>
              注册于 {{ formatDate(userInfo.created_at) }}
            </span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Tab 切换 -->
    <el-tabs v-model="activeTab" class="content-tabs" @tab-change="handleTabChange">
      <!-- 我的收藏 -->
      <el-tab-pane label="我的收藏" name="favorites">
        <div class="list-container" v-loading="loading">
          <!-- 列表内容 -->
          <div v-if="favorites.length > 0" class="card-list">
            <div v-for="item in favorites" :key="item.id" class="list-item card-container">
              <div class="item-main" @click="goToDetail(item.knowledge_id)">
                <div class="item-header">
                  <el-tag size="small" :type="getCategoryType(item.category)">
                    {{ item.category_name }}
                  </el-tag>
                  <span class="file-type" v-if="item.file_type">
                    {{ item.file_type.toUpperCase() }}
                  </span>
                </div>
                <h3 class="item-title">{{ item.title }}</h3>
                <p class="item-summary">{{ item.summary || '暂无摘要' }}</p>
                <div class="item-footer">
                  <span class="time">
                    <el-icon><Star /></el-icon>
                    收藏于 {{ formatDate(item.favorited_at) }}
                  </span>
                </div>
              </div>
              <div class="item-actions">
                <el-button type="danger" plain size="small" @click.stop="handleUnfavorite(item)">
                  取消收藏
                </el-button>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <el-empty v-else description="暂无收藏内容" :image-size="80">
            <template #image>
              <el-icon :size="60" color="#c0c4cc"><Star /></el-icon>
            </template>
            <el-button type="primary" @click="goToSearch">去探索知识</el-button>
          </el-empty>

          <!-- 分页 -->
          <div class="pagination-wrapper" v-if="favoritesTotal > pageSize">
            <el-pagination
              v-model:current-page="favoritesPage"
              :page-size="pageSize"
              :total="favoritesTotal"
              layout="prev, pager, next"
              @current-change="loadFavorites"
            />
          </div>
        </div>
      </el-tab-pane>

      <!-- 我的评论 -->
      <el-tab-pane label="我的评论" name="comments">
        <div class="list-container" v-loading="loading">
          <!-- 列表内容 -->
          <div v-if="comments.length > 0" class="card-list">
            <div v-for="item in comments" :key="item.id" class="list-item card-container">
              <div class="item-main" @click="goToDetailWithComment(item.knowledge_id)">
                <div class="item-header">
                  <span class="knowledge-link">
                    <el-icon><Document /></el-icon>
                    {{ item.knowledge_title || '未知知识' }}
                  </span>
                </div>
                <div class="comment-content">{{ item.content }}</div>
                <div class="item-footer">
                  <span class="time">
                    <el-icon><ChatLineSquare /></el-icon>
                    评论于 {{ formatDate(item.created_at) }}
                  </span>
                </div>
              </div>
              <div class="item-actions">
                <el-button type="danger" plain size="small" @click.stop="handleDeleteComment(item)">
                  删除
                </el-button>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <el-empty v-else description="暂无评论记录" :image-size="80">
            <template #image>
              <el-icon :size="60" color="#c0c4cc"><ChatLineSquare /></el-icon>
            </template>
            <el-button type="primary" @click="goToSearch">去发表评论</el-button>
          </el-empty>

          <!-- 分页 -->
          <div class="pagination-wrapper" v-if="commentsTotal > pageSize">
            <el-pagination
              v-model:current-page="commentsPage"
              :page-size="pageSize"
              :total="commentsTotal"
              layout="prev, pager, next"
              @current-change="loadComments"
            />
          </div>
        </div>
      </el-tab-pane>

      <!-- 我的上传 -->
      <el-tab-pane label="我的上传" name="uploads">
        <div class="list-container" v-loading="loading">
          <!-- 列表内容 -->
          <div v-if="uploads.length > 0" class="card-list">
            <div v-for="item in uploads" :key="item.id" class="list-item card-container">
              <div class="item-main" @click="goToDetail(item.id)">
                <div class="item-header">
                  <el-tag size="small" :type="getCategoryType(item.category)">
                    {{ item.category_name }}
                  </el-tag>
                  <span class="file-type" v-if="item.file_type">
                    {{ item.file_type.toUpperCase() }}
                  </span>
                  <div class="index-status">
                    <el-tooltip content="全文索引" placement="top">
                      <span class="status-dot" :class="item.es_indexed"></span>
                    </el-tooltip>
                    <el-tooltip content="向量索引" placement="top">
                      <span class="status-dot" :class="item.vector_indexed"></span>
                    </el-tooltip>
                    <el-tooltip content="知识图谱" placement="top">
                      <span class="status-dot" :class="item.graph_indexed"></span>
                    </el-tooltip>
                  </div>
                </div>
                <h3 class="item-title">{{ item.title }}</h3>
                <p class="item-summary">{{ item.summary || '暂无摘要' }}</p>
                <div class="item-footer">
                  <span class="time">
                    <el-icon><Upload /></el-icon>
                    上传于 {{ formatDate(item.created_at) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <el-empty v-else description="暂无上传记录" :image-size="80">
            <template #image>
              <el-icon :size="60" color="#c0c4cc"><Upload /></el-icon>
            </template>
            <el-button type="primary" @click="goToUpload">上传知识</el-button>
          </el-empty>

          <!-- 分页 -->
          <div class="pagination-wrapper" v-if="uploadsTotal > pageSize">
            <el-pagination
              v-model:current-page="uploadsPage"
              :page-size="pageSize"
              :total="uploadsTotal"
              layout="prev, pager, next"
              @current-change="loadUploads"
            />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 知识详情弹窗 -->
    <KnowledgeDetailModal v-model="showDetailModal" :knowledge-id="currentDetailId" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api'
import {
  User, Postcard, OfficeBuilding, Calendar, Star,
  ChatLineSquare, Document, Upload, View
} from '@element-plus/icons-vue'
import KnowledgeDetailModal from '@/components/KnowledgeDetailModal.vue'

const router = useRouter()

const showDetailModal = ref(false)
const currentDetailId = ref('')

// 用户信息
const userInfo = reactive({
  id: '',
  username: '',
  full_name: '',
  role_name: '',
  org_name: '',
  created_at: ''
})

// Tab 状态
const activeTab = ref('favorites')
const loading = ref(false)

// 收藏列表
const favorites = ref([])
const favoritesPage = ref(1)
const favoritesTotal = ref(0)

// 评论列表
const comments = ref([])
const commentsPage = ref(1)
const commentsTotal = ref(0)

// 上传列表
const uploads = ref([])
const uploadsPage = ref(1)
const uploadsTotal = ref(0)

const pageSize = 10

// 分类颜色映射
const categoryMap = {
  law: 'danger',
  tech: 'success',
  case: 'warning',
  policy: 'info'
}

const getCategoryType = (category) => categoryMap[category] || 'info'

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

// Tab 切换
const handleTabChange = (tabName) => {
  switch (tabName) {
    case 'favorites':
      if (favorites.value.length === 0) loadFavorites()
      break
    case 'comments':
      if (comments.value.length === 0) loadComments()
      break
    case 'uploads':
      if (uploads.value.length === 0) loadUploads()
      break
  }
}

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const res = await request.get('/auth/me')
    Object.assign(userInfo, res)
  } catch (error) {
    console.error('加载用户信息失败', error)
  }
}

// 加载收藏列表
const loadFavorites = async () => {
  loading.value = true
  try {
    const res = await request.get(`/users/${userInfo.id}/favorites`, {
      params: { page: favoritesPage.value, page_size: pageSize }
    })
    favorites.value = res.items
    favoritesTotal.value = res.total
  } catch (error) {
    console.error('加载收藏列表失败', error)
  } finally {
    loading.value = false
  }
}

// 加载评论列表
const loadComments = async () => {
  loading.value = true
  try {
    const res = await request.get(`/users/${userInfo.id}/comments`, {
      params: { page: commentsPage.value, page_size: pageSize }
    })
    comments.value = res.items
    commentsTotal.value = res.total
  } catch (error) {
    console.error('加载评论列表失败', error)
  } finally {
    loading.value = false
  }
}

// 加载上传列表
const loadUploads = async () => {
  loading.value = true
  try {
    const res = await request.get(`/knowledge`, {
      params: { page: uploadsPage.value, page_size: pageSize, user_id: userInfo.id }
    })
    uploads.value = res.items
    uploadsTotal.value = res.total
  } catch (error) {
    console.error('加载上传列表失败', error)
  } finally {
    loading.value = false
  }
}

// 取消收藏
const handleUnfavorite = async (item) => {
  try {
    await ElMessageBox.confirm(`确定要取消收藏"${item.title}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await request.delete(`/users/${userInfo.id}/favorites/${item.knowledge_id}`)
    ElMessage.success('已取消收藏')
    loadFavorites()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消收藏失败', error)
    }
  }
}

// 删除评论
const handleDeleteComment = async (item) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await request.delete(`/users/${userInfo.id}/comments/${item.id}`)
    ElMessage.success('评论已删除')
    loadComments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除评论失败', error)
    }
  }
}

// 跳转知识详情
const goToDetail = (id) => {
  currentDetailId.value = id
  showDetailModal.value = true
}

// 跳转知识详情并定位到评论区
const goToDetailWithComment = (id) => {
  currentDetailId.value = id
  showDetailModal.value = true
}

// 跳转到搜索页
const goToSearch = () => {
  router.push('/knowledge/search')
}

// 跳转到上传页
const goToUpload = () => {
  router.push('/knowledge/manage-new?action=upload')
}

onMounted(async () => {
  await loadUserInfo()
  await loadFavorites()
})
</script>

<style scoped>
.user-center {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* 个人资料卡片 */
.profile-card {
  margin-bottom: 24px;
}

.profile-card :deep(.el-card__body) {
  padding: 24px;
}

.profile-content {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  font-size: 28px;
  font-weight: 600;
}

.profile-info {
  flex: 1;
}

.profile-info .name {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.meta-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 14px;
}

.meta-item .el-icon {
  color: var(--text-placeholder);
}

/* Tab 样式 */
.content-tabs {
  margin-top: 24px;
}

.content-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.content-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  height: 40px;
  line-height: 40px;
}

.content-tabs :deep(.el-tabs__item.is-active) {
  font-weight: 600;
}

/* 列表容器 */
.list-container {
  min-height: 300px;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.list-item {
  display: flex;
  align-items: flex-start;
  padding: 20px;
  transition: all 0.2s;
  cursor: pointer;
}

.list-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.item-main {
  flex: 1;
  min-width: 0;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.file-type {
  font-size: 12px;
  color: var(--text-placeholder);
  background: var(--bg-color);
  padding: 2px 6px;
  border-radius: 4px;
}

.index-status {
  display: flex;
  gap: 4px;
  margin-left: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-placeholder);
}

.status-dot.indexed,
.status-dot.done {
  background: #10b981;
}

.status-dot.pending {
  background: #f59e0b;
}

.status-dot.failed {
  background: #ef4444;
}

.knowledge-link {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--accent-color);
  font-weight: 500;
}

.knowledge-link:hover {
  text-decoration: underline;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.item-summary {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.comment-content {
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-color);
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 12px;
  line-height: 1.5;
}

.item-footer {
  display: flex;
  align-items: center;
  gap: 16px;
}

.time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-placeholder);
}

.item-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-left: 16px;
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* 空状态 */
.user-center :deep(.el-empty) {
  padding: 40px 0;
}

.user-center :deep(.el-empty__description) {
  margin-top: 12px;
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 768px) {
  .user-center {
    padding: 16px;
  }

  .profile-content {
    flex-direction: column;
    text-align: center;
  }

  .meta-list {
    justify-content: center;
  }

  .list-item {
    flex-direction: column;
  }

  .item-actions {
    flex-direction: row;
    margin-left: 0;
    margin-top: 12px;
    width: 100%;
  }

  .item-actions .el-button {
    flex: 1;
  }
}
</style>