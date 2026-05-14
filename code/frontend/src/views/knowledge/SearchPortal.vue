<template>
  <div class="search-portal">
    <!-- 搜索区域 -->
    <div class="search-hero">
      <h1>海南省住建知识库</h1>
      <p class="subtitle">一站式搜索工程施工技术规范、建筑行业标准、执法依据等</p>

      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="请输入关键词搜索..."
          size="large"
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" size="large" @click="handleSearch">搜索</el-button>
      </div>

      <!-- 搜索类型切换 -->
      <div class="search-type-switch">
        <el-radio-group v-model="searchType" size="small" @change="handleSearch">
          <el-radio-button value="hybrid">混合搜索</el-radio-button>
          <el-radio-button value="keyword">关键词</el-radio-button>
          <el-radio-button value="vector">语义搜索</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 热门标签 -->
      <div class="hot-tags">
        <span class="hot-label">热门搜索：</span>
        <el-tag
          v-for="tag in hotTags"
          :key="tag.term"
          class="hot-tag"
          @click="handleTagClick(tag.term)"
        >
          {{ tag.term }}
        </el-tag>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-section card-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="filters.category" placeholder="知识分类" clearable @change="handleSearch">
            <el-option label="法律法规" value="law" />
            <el-option label="技术标准" value="tech" />
            <el-option label="执法案例" value="case" />
            <el-option label="政策文件" value="policy" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.source" placeholder="来源" clearable @change="handleSearch">
            <el-option label="国家法规" value="national" />
            <el-option label="省级法规" value="provincial" />
            <el-option label="行业标准" value="industry" />
          </el-select>
        </el-col>
        <el-col :span="6" style="text-align: right;">
          <el-button @click="resetFilters">重置</el-button>
          <el-button type="primary" @click="handleSearch">查询</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索结果 -->
    <div class="search-results">
      <div class="results-header">
        <span class="results-count">共找到 <strong>{{ totalResults }}</strong> 条相关知识</span>
        <el-radio-group v-model="sortBy" size="small" @change="handleSearch">
          <el-radio-button value="relevance">相关度</el-radio-button>
          <el-radio-button value="date">最新</el-radio-button>
          <el-radio-button value="views">热度</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 结果列表 -->
      <div class="results-list" v-loading="loading">
        <div
          v-for="item in searchResults"
          :key="item.id"
          class="result-item card-container"
          @click="goToDetail(item.id)"
        >
          <div class="result-header">
            <h3 class="result-title" v-html="item.highlight?.title || item.title"></h3>
            <el-tag :type="getCategoryType(item.category)" size="small">
              {{ item.category_name }}
            </el-tag>
          </div>

          <p class="result-summary" v-html="item.highlight?.content || item.summary || item.highlight?.summary || ''"></p>

          <div class="result-meta">
            <span><el-icon><Document /></el-icon> {{ item.source }}</span>
            <span><el-icon><View /></el-icon> {{ item.view_count }} 次浏览</span>
          </div>

          <div class="result-tags">
            <el-tag
              v-for="tag in item.tags"
              :key="tag"
              size="small"
              effect="plain"
              style="margin-right: 8px;"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>

        <el-empty v-if="!loading && searchResults.length === 0 && hasSearched" description="未找到相关知识" />
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="totalResults > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalResults"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 右侧悬浮工具 -->
    <div class="float-tools">
      <el-card class="tool-card">
        <template #header>
          <span>热门知识</span>
        </template>
        <div class="hot-list">
          <div
            v-for="(item, index) in hotKnowledge"
            :key="item.id"
            class="hot-item"
            @click="goToDetail(item.id)"
          >
            <span class="rank">{{ index + 1 }}</span>
            <span class="title">{{ item.title }}</span>
            <span class="views">{{ item.view_count }}</span>
          </div>
          <el-empty v-if="!hotKnowledge.length" description="暂无数据" :image-size="60" />
        </div>
      </el-card>

      <el-card class="tool-card" style="margin-top: 16px;">
        <template #header>
          <span>最新知识</span>
        </template>
        <div class="latest-list">
          <div
            v-for="item in latestKnowledge"
            :key="item.id"
            class="latest-item"
            @click="goToDetail(item.id)"
          >
            {{ item.title }}
          </div>
          <el-empty v-if="!latestKnowledge.length" description="暂无数据" :image-size="60" />
        </div>
      </el-card>
    </div>

    <!-- 知识详情弹窗 -->
    <KnowledgeDetailModal v-model="showDetailModal" :knowledge-id="currentDetailId" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search, Document, View
} from '@element-plus/icons-vue'
import { knowledgeApi } from '@/api'
import KnowledgeDetailModal from '@/components/KnowledgeDetailModal.vue'

const router = useRouter()

const showDetailModal = ref(false)
const currentDetailId = ref('')

const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalResults = ref(0)
const sortBy = ref('relevance')
const searchType = ref('hybrid')
const loading = ref(false)
const hasSearched = ref(false)

const filters = reactive({
  category: '',
  source: ''
})

const hotTags = ref([])

const searchResults = ref([])
const hotKnowledge = ref([])
const latestKnowledge = ref([])

const getCategoryType = (category) => {
  const types = {
    law: 'danger',
    tech: 'success',
    case: 'warning',
    policy: 'info'
  }
  return types[category] || 'info'
}

const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    return
  }

  loading.value = true
  hasSearched.value = true

  try {
    const params = {
      q: searchKeyword.value,
      search_type: searchType.value,
      page: currentPage.value,
      page_size: pageSize.value,
      sort: sortBy.value === 'relevance' ? 'relevance' : (sortBy.value === 'date' ? 'created_at desc' : 'view_count desc')
    }

    if (filters.category) params.category = filters.category
    if (filters.source) params.source = filters.source

    const res = await knowledgeApi.search(params)
    searchResults.value = res.items
    totalResults.value = res.total
  } catch (error) {
    console.error('搜索失败', error)
  } finally {
    loading.value = false
  }
}

const handleTagClick = (tag) => {
  searchKeyword.value = tag
  handleSearch()
}

const resetFilters = () => {
  filters.category = ''
  filters.source = ''
  handleSearch()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  handleSearch()
}

const handlePageChange = (val) => {
  currentPage.value = val
  handleSearch()
}

const goToDetail = (id) => {
  currentDetailId.value = id
  showDetailModal.value = true
}

const loadHotAndLatest = async () => {
  try {
    const [hotRes, latestRes, hotTermsRes] = await Promise.all([
      knowledgeApi.hot(10),
      knowledgeApi.latest(10),
      knowledgeApi.hotTerms(10)
    ])
    hotKnowledge.value = hotRes
    latestKnowledge.value = latestRes
    hotTags.value = hotTermsRes
  } catch (error) {
    console.error('加载热门和最新知识失败', error)
  }
}

onMounted(() => {
  loadHotAndLatest()
})
</script>

<style scoped>
.search-portal {
  position: relative;
  padding-right: 280px;
}

.search-hero {
  background: var(--primary-gradient);
  padding: 64px 40px;
  border-radius: var(--border-radius);
  text-align: center;
  color: #fff;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

/* 装饰图案 */
.search-hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.3;
}

.search-hero h1 {
  margin: 0 0 14px 0;
  font-size: 34px;
  font-weight: 600;
  position: relative;
  z-index: 1;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.search-hero .subtitle {
  margin: 0 0 36px 0;
  font-size: 16px;
  opacity: 0.9;
  position: relative;
  z-index: 1;
}

.search-box {
  display: flex;
  max-width: 720px;
  margin: 0 auto;
  gap: 14px;
  position: relative;
  z-index: 1;
}

.search-box :deep(.el-input__wrapper) {
  padding: 16px 18px;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.search-box :deep(.el-input__wrapper:focus-within) {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.2);
}

.search-box :deep(.el-input__inner) {
  font-size: 16px;
}

.search-box :deep(.el-button) {
  padding: 16px 32px;
  border-radius: var(--border-radius);
  font-size: 16px;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.search-type-switch {
  margin-top: 20px;
  position: relative;
  z-index: 1;
}

.search-type-switch :deep(.el-radio-button__inner) {
  border-radius: var(--border-radius-sm);
}

.hot-tags {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}

.hot-label {
  color: rgba(255, 255, 255, 0.8);
}

.hot-tag {
  cursor: pointer;
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
  transition: all var(--transition-fast);
}

.hot-tag:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.filter-section {
  margin-bottom: 24px;
  padding: 24px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.results-count {
  color: var(--text-secondary);
}

.results-count strong {
  color: var(--primary-color);
  font-size: 18px;
}

.result-item {
  cursor: pointer;
  transition: all var(--transition-normal);
  padding: 24px;
  margin-bottom: 16px;
  border-radius: var(--border-radius);
  border-left: 4px solid transparent;
  position: relative;
}

.result-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -1px;
  width: 4px;
  height: 100%;
  background: var(--accent-light);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.result-item:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.result-item:hover::before {
  opacity: 1;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
}

.result-title {
  margin: 0;
  font-size: 18px;
  color: var(--text-primary);
  font-weight: 600;
  transition: color var(--transition-fast);
}

.result-item:hover .result-title {
  color: var(--primary-color);
}

.result-title :deep(em) {
  color: var(--danger-color);
  font-style: normal;
  font-weight: bold;
}

.result-summary {
  margin: 0 0 14px 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-summary :deep(em) {
  color: var(--danger-color);
  font-style: normal;
  background: #fef0f0;
  padding: 0 3px;
  border-radius: 2px;
}

.result-meta {
  display: flex;
  gap: 24px;
  color: var(--text-light);
  font-size: 13px;
  margin-bottom: 14px;
}

.result-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.result-tags {
  display: flex;
  flex-wrap: wrap;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 36px;
}

.float-tools {
  position: fixed;
  top: 84px;
  right: 24px;
  width: 260px;
}

.tool-card {
  font-size: 14px;
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
}

.tool-card:hover {
  box-shadow: var(--shadow-md);
}

.tool-card :deep(.el-card__header) {
  background: var(--primary-gradient);
  color: #fff;
  padding: 14px 18px;
  font-weight: 600;
}

.hot-list,
.latest-list {
  max-height: 200px;
  overflow-y: auto;
}

.hot-item {
  padding: 10px 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid var(--border-color);
  transition: all var(--transition-fast);
  border-radius: var(--border-radius-sm);
}

.hot-item:hover {
  background: var(--bg-color);
  color: var(--primary-color);
  padding-left: 10px;
}

.hot-item .rank {
  width: 22px;
  height: 22px;
  background: var(--bg-color);
  border-radius: var(--border-radius-sm);
  text-align: center;
  line-height: 22px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-light);
}

.hot-item:hover .rank {
  background: var(--accent-light);
  color: #fff;
}

.hot-item .title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
}

.hot-item .views {
  color: var(--text-light);
  font-size: 12px;
}

.latest-item {
  padding: 10px 6px;
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  transition: all var(--transition-fast);
  border-radius: var(--border-radius-sm);
}

.latest-item:hover {
  background: var(--bg-color);
  color: var(--primary-color);
  padding-left: 10px;
}

.card-container {
  background: #fff;
  border-radius: var(--border-radius);
}
</style>
