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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search, Document, View
} from '@element-plus/icons-vue'
import { knowledgeApi } from '@/api'

const router = useRouter()

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
  router.push(`/knowledge/detail/${id}`)
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
  background: linear-gradient(135deg, #409eff 0%, #1677ff 100%);
  padding: 60px 40px;
  border-radius: 12px;
  text-align: center;
  color: #fff;
  margin-bottom: 24px;
}

.search-hero h1 {
  margin: 0 0 12px 0;
  font-size: 32px;
}

.search-hero .subtitle {
  margin: 0 0 32px 0;
  font-size: 16px;
  opacity: 0.9;
}

.search-box {
  display: flex;
  max-width: 700px;
  margin: 0 auto;
  gap: 12px;
}

.search-box .search-input {
  flex: 1;
}

.search-type-switch {
  margin-top: 16px;
}

.hot-tags {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.hot-label {
  color: rgba(255, 255, 255, 0.8);
}

.hot-tag {
  cursor: pointer;
}

.filter-section {
  margin-bottom: 24px;
  padding: 20px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.results-count {
  color: #606266;
}

.result-item {
  cursor: pointer;
  transition: all 0.3s;
  padding: 20px;
  margin-bottom: 16px;
}

.result-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.result-title {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.result-title :deep(em) {
  color: #f56c6c;
  font-style: normal;
  font-weight: bold;
}

.result-summary {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.result-summary :deep(em) {
  color: #f56c6c;
  font-style: normal;
  background: #fef0f0;
  padding: 0 2px;
}

.result-meta {
  display: flex;
  gap: 20px;
  color: #909399;
  font-size: 13px;
  margin-bottom: 12px;
}

.result-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.result-tags {
  display: flex;
  flex-wrap: wrap;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

.float-tools {
  position: fixed;
  top: 80px;
  right: 20px;
  width: 260px;
}

.tool-card {
  font-size: 14px;
}

.hot-list,
.latest-list {
  max-height: 200px;
  overflow-y: auto;
}

.hot-item {
  padding: 8px 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.hot-item:hover {
  color: #409eff;
}

.hot-item .rank {
  width: 18px;
  height: 18px;
  background: #f0f0f0;
  border-radius: 4px;
  text-align: center;
  line-height: 18px;
  font-size: 12px;
  color: #909399;
}

.hot-item .title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hot-item .views {
  color: #c0c4cc;
  font-size: 12px;
}

.latest-item {
  padding: 8px 4px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.latest-item:hover {
  color: #409eff;
}

.card-container {
  background: #fff;
  border-radius: 8px;
}
</style>
