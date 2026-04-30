<template>
  <div class="knowledge-manage-new">
    <!-- 页面标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">知识管理</h1>
        <p class="page-subtitle">管理所有知识内容，包括文档和文本</p>
      </div>
      <div class="header-actions">
        <el-button type="success" @click="showTextDialog = true">
          <el-icon><Edit /></el-icon>
          添加文本
        </el-button>
        <el-button type="primary" @click="showUploadDialog = true">
          <el-icon><Upload /></el-icon>
          上传文档
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card" @click="handleStatsClick('total')">
        <div class="stat-header">
          <div class="stat-icon total">
            <el-icon><Document /></el-icon>
          </div>
          <span class="stat-trend up">+12%</span>
        </div>
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">知识总数</div>
        <div class="stat-bar">
          <div class="stat-bar-fill total" :style="{ width: '100%' }"></div>
        </div>
      </div>
      <div class="stat-card" @click="handleStatsClick('es')">
        <div class="stat-header">
          <div class="stat-icon es">
            <el-icon><Search /></el-icon>
          </div>
          <span class="stat-trend">{{ Math.round(stats.esIndexed / stats.total * 100) || 0 }}%</span>
        </div>
        <div class="stat-value">{{ stats.esIndexed }}</div>
        <div class="stat-label">全文检索 已索引</div>
        <div class="stat-bar">
          <div class="stat-bar-fill es" :style="{ width: (stats.esIndexed / stats.total * 100) + '%' }"></div>
        </div>
      </div>
      <div class="stat-card" @click="handleStatsClick('vector')">
        <div class="stat-header">
          <div class="stat-icon vector">
            <el-icon><Connection /></el-icon>
          </div>
          <span class="stat-trend pending">{{ Math.round(stats.vectorDone / stats.total * 100) || 0 }}%</span>
        </div>
        <div class="stat-value">{{ stats.vectorDone }}</div>
        <div class="stat-label">已语义搜索</div>
        <div class="stat-bar">
          <div class="stat-bar-fill vector" :style="{ width: (stats.vectorDone / stats.total * 100) + '%' }"></div>
        </div>
      </div>
      <div class="stat-card" @click="handleStatsClick('graph')">
        <div class="stat-header">
          <div class="stat-icon graph">
            <el-icon><Grid /></el-icon>
          </div>
          <span class="stat-trend pending">{{ Math.round(stats.graphDone / stats.total * 100) || 0 }}%</span>
        </div>
        <div class="stat-value">{{ stats.graphDone }}</div>
        <div class="stat-label">已入知识图谱</div>
        <div class="stat-bar">
          <div class="stat-bar-fill graph" :style="{ width: (stats.graphDone / stats.total * 100) + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="search-box">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索知识标题..."
          clearable
          @keyup.enter="handleFilter"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <el-select v-model="filters.type" placeholder="全部类型" clearable @change="handleFilter" style="width: 120px;">
        <el-option label="全部类型" value="" />
        <el-option label="PDF文档" value="pdf" />
        <el-option label="Word文档" value="doc" />
        <el-option label="文本" value="text" />
      </el-select>
      <el-select v-model="filters.category" placeholder="全部分类" clearable @change="handleFilter" style="width: 140px;">
        <el-option label="全部分类" value="" />
        <el-option label="法律法规" value="law" />
        <el-option label="技术标准" value="tech" />
        <el-option label="执法案例" value="case" />
        <el-option label="政策文件" value="policy" />
      </el-select>
      <div class="status-filters">
        <el-tag
          :class="['filter-tag', allStatusCleared ? 'active' : '']"
          @click="clearStatusFilter"
          type="info"
        >全部</el-tag>
        <el-tag
          :class="['filter-tag', filters.fullTextStatus === 'indexed' ? 'active' : '']"
          @click="toggleStatusFilter('es')"
          type="info"
        >全文检索</el-tag>
        <el-tag
          :class="['filter-tag', filters.vectorStatus === 'done' ? 'active' : '']"
          @click="toggleStatusFilter('vector')"
          type="info"
        >语义搜索</el-tag>
        <el-tag
          :class="['filter-tag', filters.graphStatus === 'done' ? 'active' : '']"
          @click="toggleStatusFilter('graph')"
          type="info"
        >知识图谱</el-tag>
      </div>
      <div class="view-toggle">
        <el-button-group>
          <el-button :type="viewMode === 'list' ? 'primary' : ''" @click="viewMode = 'list'">
            <el-icon><List /></el-icon>
          </el-button>
          <el-button :type="viewMode === 'grid' ? 'primary' : ''" @click="viewMode = 'grid'">
            <el-icon><Grid /></el-icon>
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 列表视图 -->
    <div v-if="viewMode === 'list'" class="knowledge-list">
      <div
        v-for="item in knowledgeList"
        :key="item.id"
        class="knowledge-card"
        @click="viewFile(item)"
      >
        <div class="knowledge-main">
          <div class="knowledge-header">
            <el-tag :type="getTypeIcon(item.file_type)" size="small">
              {{ item.file_type === 'pdf' ? '📕 PDF' : item.file_type === 'html' ? '📝 文本' : '📄 Word' }}
            </el-tag>
            <el-tag :type="getCategoryType(item.category)" size="small">{{ item.category_name }}</el-tag>
          </div>
          <div class="knowledge-title">{{ item.title }}</div>
          <div class="knowledge-meta">
            <span class="meta-item">
              <el-icon><Document /></el-icon>
              {{ item.source || '无来源' }}
            </span>
            <span class="meta-item">
              <el-icon><Clock /></el-icon>
              {{ item.created_at }}
            </span>
          </div>
        </div>
        <div class="status-list">
          <div :class="['status-item', 'es', item.es_indexed === 'indexed' ? 'active' : 'pending']">
            <div class="status-header">
              <el-icon><Search /></el-icon>
              <span class="status-label">全文检索</span>
            </div>
            <div class="status-value">{{ item.es_indexed === 'indexed' ? '已索引' : '待索引' }}</div>
            <div class="status-actions">
              <el-button size="small" type="success" @click.stop="retryProcess(item, 'es')">重建</el-button>
              <el-button size="small" type="danger" @click.stop="clearProcess(item, 'es')">清空</el-button>
            </div>
          </div>
          <div :class="['status-item', 'vector', item.vector_indexed === 'done' ? 'active' : 'pending']">
            <div class="status-header">
              <el-icon><Connection /></el-icon>
              <span class="status-label">语义搜索</span>
            </div>
            <div class="status-value">{{ item.vector_indexed === 'done' ? '已完成' : '待处理' }}</div>
            <div class="status-actions">
              <el-button size="small" type="success" @click.stop="retryProcess(item, 'vector')">重建</el-button>
              <el-button size="small" type="danger" @click.stop="clearProcess(item, 'vector')">清空</el-button>
            </div>
          </div>
          <div :class="['status-item', 'graph', item.graph_indexed === 'done' ? 'active' : 'pending']">
            <div class="status-header">
              <el-icon><Grid /></el-icon>
              <span class="status-label">知识图谱</span>
            </div>
            <div class="status-value">{{ item.graph_indexed === 'done' ? '已完成' : '待处理' }}</div>
            <div class="status-actions">
              <el-button size="small" type="success" @click.stop="retryProcess(item, 'graph')">重建</el-button>
              <el-button size="small" type="danger" @click.stop="clearProcess(item, 'graph')">清空</el-button>
            </div>
          </div>
        </div>
        <div class="action-buttons">
          <el-button circle type="primary" @click.stop="viewFile(item)" title="查看">
            <el-icon><View /></el-icon>
          </el-button>
          <el-button circle type="success" @click.stop="editItem(item)" title="编辑">
            <el-icon><Edit /></el-icon>
          </el-button>
          <el-button circle type="danger" @click.stop="deleteItem(item)" title="删除">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
      <el-empty v-if="knowledgeList.length === 0" description="暂无知识内容" />
    </div>

    <!-- 网格视图 -->
    <div v-if="viewMode === 'grid'" class="knowledge-grid">
      <div
        v-for="item in knowledgeList"
        :key="item.id"
        class="knowledge-grid-card"
        @click="viewFile(item)"
      >
        <div class="grid-card-header">
          <div class="grid-card-title">{{ item.title }}</div>
          <el-tag size="small">{{ item.file_type === 'pdf' ? 'PDF' : item.file_type === 'html' ? '文本' : 'Word' }}</el-tag>
        </div>
        <div class="grid-card-meta">
          <el-tag :type="getCategoryType(item.category)" size="small">{{ item.category_name }}</el-tag>
          <span class="meta-item">{{ item.source || '无来源' }}</span>
          <span class="meta-item">{{ item.created_at }}</span>
        </div>
        <div class="grid-card-status">
          <div :class="['grid-status-item', 'es', item.es_indexed === 'indexed' ? 'active' : 'pending']">
            <div class="grid-status-header">
              <el-icon><Search /></el-icon>
              <span class="grid-status-label">全文检索</span>
            </div>
            <div class="grid-status-value">{{ item.es_indexed === 'indexed' ? '已索引' : '待索引' }}</div>
            <div class="status-actions">
              <el-button size="small" type="success" @click.stop="retryProcess(item, 'es')">重建</el-button>
              <el-button size="small" type="danger" @click.stop="clearProcess(item, 'es')">清空</el-button>
            </div>
          </div>
          <div :class="['grid-status-item', 'vector', item.vector_indexed === 'done' ? 'active' : 'pending']">
            <div class="grid-status-header">
              <el-icon><Connection /></el-icon>
              <span class="grid-status-label">语义搜索</span>
            </div>
            <div class="grid-status-value">{{ item.vector_indexed === 'done' ? '已完成' : '待处理' }}</div>
            <div class="status-actions">
              <el-button size="small" type="success" @click.stop="retryProcess(item, 'vector')">重建</el-button>
              <el-button size="small" type="danger" @click.stop="clearProcess(item, 'vector')">清空</el-button>
            </div>
          </div>
          <div :class="['grid-status-item', 'graph', item.graph_indexed === 'done' ? 'active' : 'pending']">
            <div class="grid-status-header">
              <el-icon><Grid /></el-icon>
              <span class="grid-status-label">知识图谱</span>
            </div>
            <div class="grid-status-value">{{ item.graph_indexed === 'done' ? '已完成' : '待处理' }}</div>
            <div class="status-actions">
              <el-button size="small" type="success" @click.stop="retryProcess(item, 'graph')">重建</el-button>
              <el-button size="small" type="danger" @click.stop="clearProcess(item, 'graph')">清空</el-button>
            </div>
          </div>
        </div>
        <div class="grid-card-footer">
          <div></div>
          <div class="grid-card-actions">
            <el-button circle type="primary" size="small" @click.stop="viewFile(item)">
              <el-icon><View /></el-icon>
            </el-button>
            <el-button circle type="success" size="small" @click.stop="editItem(item)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button circle type="danger" size="small" @click.stop="deleteItem(item)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
      <el-empty v-if="knowledgeList.length === 0" description="暂无知识内容" />
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>

    <!-- 上传弹窗 -->
    <el-dialog v-model="showUploadDialog" title="上传知识" width="500px">
      <el-form ref="uploadFormRef" :model="uploadForm" label-width="80px">
        <el-form-item label="文件" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileSelect"
            :on-remove="handleFileRemove"
            accept=".pdf,.doc,.docx"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持 PDF、Word 格式，大小不超过 50MB</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="uploadForm.title" placeholder="不填则使用文件名" />
        </el-form-item>
        <el-form-item label="分类" required>
          <el-select v-model="uploadForm.category" placeholder="请选择分类">
            <el-option label="法律法规" value="law" />
            <el-option label="技术标准" value="tech" />
            <el-option label="执法案例" value="case" />
            <el-option label="政策文件" value="policy" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="uploadForm.source" placeholder="如：国务院令第279号" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="uploadForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :disabled="!uploadForm.file || !uploadForm.category">上传</el-button>
      </template>
    </el-dialog>

    <!-- 文本弹窗 -->
    <el-dialog v-model="showTextDialog" title="手动添加知识" width="600px">
      <el-form ref="textFormRef" :model="textForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="textForm.title" placeholder="请输入知识标题" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input
            v-model="textForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入知识内容"
          />
        </el-form-item>
        <el-form-item label="分类" required>
          <el-select v-model="textForm.category" placeholder="请选择分类">
            <el-option label="法律法规" value="law" />
            <el-option label="技术标准" value="tech" />
            <el-option label="执法案例" value="case" />
            <el-option label="政策文件" value="policy" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="textForm.source" placeholder="如：国务院令第279号" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="textForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTextDialog = false">取消</el-button>
        <el-button type="primary" @click="handleTextSubmit" :disabled="!textForm.title || !textForm.content || !textForm.category">保存</el-button>
      </template>
    </el-dialog>

    <!-- 预览弹窗 -->
    <el-dialog v-model="showPreview" title="知识预览" width="900px" top="5vh">
      <div class="preview-header">
        <div class="preview-title">
          <span>{{ previewItem.title }}</span>
          <el-tag :type="previewItem.file_type === 'pdf' ? 'danger' : 'primary'">
            {{ previewItem.file_type === 'pdf' ? 'PDF文档' : previewItem.file_type === 'html' ? '文本' : 'Word文档' }}
          </el-tag>
        </div>
      </div>
      <div class="preview-toolbar">
        <el-button size="small">放大</el-button>
        <el-button size="small">缩小</el-button>
        <el-button size="small">下载</el-button>
        <el-button size="small">打印</el-button>
      </div>
      <div class="preview-content">
        <div class="preview-placeholder">
          <el-icon class="preview-icon"><Document /></el-icon>
          <div class="preview-text">{{ previewItem.file_type === 'pdf' ? 'PDF 文件预览' : 'Word 文档预览' }}</div>
          <div class="preview-hint">{{ previewItem.title }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, Search, Connection, Grid, List, View, Edit, Delete,
  Upload, Clock, Folder
} from '@element-plus/icons-vue'
import { knowledgeApi } from '@/api/index.js'
import { useRouter } from 'vue-router'

const router = useRouter()

// 视图模式
const viewMode = ref('grid')

// 知识列表
const knowledgeList = ref([])

// 统计
const stats = reactive({
  total: 0,
  esIndexed: 0,
  vectorDone: 0,
  graphDone: 0
})

// 筛选
const filters = reactive({
  type: '',
  category: '',
  fullTextStatus: '',
  vectorStatus: '',
  graphStatus: '',
  keyword: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 弹窗状态
const showUploadDialog = ref(false)
const showTextDialog = ref(false)
const showPreview = ref(false)

// 上传表单
const uploadForm = reactive({
  file: null,
  title: '',
  category: '',
  source: '',
  tags: ''
})

// 文本表单
const textForm = reactive({
  title: '',
  content: '',
  category: '',
  source: '',
  tags: ''
})

// 预览项
const previewItem = ref({ title: '', file_type: 'pdf' })

// 状态筛选
const allStatusCleared = computed(() => !filters.fullTextStatus && !filters.vectorStatus && !filters.graphStatus)

const getCategoryType = (category) => {
  const types = { law: 'danger', tech: 'success', case: 'warning', policy: '' }
  return types[category] || ''
}

const getTypeIcon = (fileType) => {
  const types = { pdf: 'danger', doc: 'primary', html: 'info' }
  return types[fileType] || ''
}

const clearStatusFilter = () => {
  filters.fullTextStatus = ''
  filters.vectorStatus = ''
  filters.graphStatus = ''
  handleFilter()
}

const toggleStatusFilter = (type) => {
  if (type === 'es') filters.fullTextStatus = filters.fullTextStatus === 'indexed' ? '' : 'indexed'
  if (type === 'vector') filters.vectorStatus = filters.vectorStatus === 'done' ? '' : 'done'
  if (type === 'graph') filters.graphStatus = filters.graphStatus === 'done' ? '' : 'done'
  handleFilter()
}

const handleFilter = () => {
  pagination.page = 1
  loadData()
}

// 加载数据
const loadData = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filters.category) params.category = filters.category
    if (filters.keyword) params.keyword = filters.keyword

    const res = await knowledgeApi.list(params)
    knowledgeList.value = (res.items || []).map(item => ({
      ...item,
      es_indexed: item.es_indexed || 'indexed',
      vector_indexed: item.vector_indexed || 'done',
      graph_indexed: item.graph_indexed || 'pending',
      file_type: item.file_type || (item.content ? 'html' : 'unknown')
    }))
    pagination.total = res.total || 0
  } catch (error) {
    console.error('加载知识列表失败:', error)
  }
}

// 加载统计
const loadStats = async () => {
  try {
    const res = await knowledgeApi.stats()
    Object.assign(stats, res)
  } catch (error) {
    console.error('加载统计失败:', error)
    // 使用默认值
    stats.total = knowledgeList.value.length
    stats.esIndexed = knowledgeList.value.filter(i => i.es_indexed === 'indexed').length
    stats.vectorDone = knowledgeList.value.filter(i => i.vector_indexed === 'done').length
    stats.graphDone = knowledgeList.value.filter(i => i.graph_indexed === 'done').length
  }
}

// 文件选择
const handleFileSelect = (file) => {
  uploadForm.file = file.raw
  if (!uploadForm.title) {
    uploadForm.title = file.name.replace(/\.[^.]+$/, '')
  }
}

const handleFileRemove = () => {
  uploadForm.file = null
}

// 上传
const handleUpload = async () => {
  if (!uploadForm.file || !uploadForm.category) {
    ElMessage.warning('请选择文件并填写分类')
    return
  }

  const formData = new FormData()
  formData.append('file', uploadForm.file)
  formData.append('category', uploadForm.category)
  if (uploadForm.title) formData.append('title', uploadForm.title)
  if (uploadForm.source) formData.append('source', uploadForm.source)
  if (uploadForm.tags) formData.append('tags', uploadForm.tags)

  try {
    await knowledgeApi.upload(formData)
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    uploadForm.file = null
    uploadForm.title = ''
    uploadForm.category = ''
    uploadForm.source = ''
    uploadForm.tags = ''
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

// 添加文本
const handleTextSubmit = async () => {
  if (!textForm.title || !textForm.content || !textForm.category) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    const data = {
      title: textForm.title,
      content: textForm.content,
      category: textForm.category
    }
    if (textForm.source) data.source = textForm.source
    if (textForm.tags) data.tags = textForm.tags.split(',').map(t => t.trim()).filter(Boolean)

    await knowledgeApi.createManual(data)
    ElMessage.success('知识添加成功')
    showTextDialog.value = false
    textForm.title = ''
    textForm.content = ''
    textForm.category = ''
    textForm.source = ''
    textForm.tags = ''
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

// 查看
const viewFile = (item) => {
  previewItem.value = { title: item.title, file_type: item.file_type }
  showPreview.value = true
}

// 编辑
const editItem = (item) => {
  router.push(`/knowledge/detail/${item.id}`)
}

// 删除
const deleteItem = async (item) => {
  try {
    await ElMessageBox.confirm(`确定要删除知识「${item.title}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await knowledgeApi.delete(item.id)
    ElMessage.success('删除成功')
    loadData()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 重建
const retryProcess = async (item, type) => {
  const names = { es: '全文检索', vector: '语义搜索', graph: '知识图谱' }
  try {
    await knowledgeApi.rebuild(item.id, type)
    ElMessage.success(`已提交${names[type]}重建任务`)
    loadData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 清空
const clearProcess = async (item, type) => {
  const names = { es: '全文检索', vector: '语义搜索', graph: '知识图谱' }
  try {
    await ElMessageBox.confirm(`确定要清空${names[type]}数据吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await knowledgeApi.clear(item.id, type)
    ElMessage.success(`已清空${names[type]}数据`)
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 统计卡片点击
const handleStatsClick = (type) => {
  if (type === 'total') {
    clearStatusFilter()
  } else if (type === 'es') {
    filters.fullTextStatus = filters.fullTextStatus === 'indexed' ? '' : 'indexed'
    handleFilter()
  } else if (type === 'vector') {
    filters.vectorStatus = filters.vectorStatus === 'done' ? '' : 'done'
    handleFilter()
  } else if (type === 'graph') {
    filters.graphStatus = filters.graphStatus === 'done' ? '' : 'done'
    handleFilter()
  }
}

onMounted(() => {
  loadData()
  loadStats()
})
</script>

<style scoped>
.knowledge-manage-new {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0;
}

.page-subtitle {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin: 4px 0 0 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--el-bg-color);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--el-border-color-light);
  cursor: pointer;
  transition: all 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-icon.total {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: #fff;
}

.stat-icon.es {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
}

.stat-icon.vector {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #fff;
}

.stat-icon.graph {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: #fff;
}

.stat-trend {
  font-size: 12px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 20px;
}

.stat-trend.up {
  background: #dcfce7;
  color: #16a34a;
}

.stat-trend.pending {
  background: #fef3c7;
  color: #d97706;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.stat-bar {
  height: 4px;
  background: var(--el-border-color-extra-light);
  border-radius: 2px;
  margin-top: 12px;
  overflow: hidden;
}

.stat-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
}

.stat-bar-fill.total {
  background: linear-gradient(90deg, #6366f1, #818cf8);
}

.stat-bar-fill.es {
  background: linear-gradient(90deg, #10b981, #34d399);
}

.stat-bar-fill.vector {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}

.stat-bar-fill.graph {
  background: linear-gradient(90deg, #8b5cf6, #a78bfa);
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
  background: var(--el-bg-color);
  padding: 16px 20px;
  border-radius: 12px;
  border: 1px solid var(--el-border-color-light);
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 200px;
  max-width: 300px;
}

.status-filters {
  display: flex;
  gap: 8px;
}

.filter-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tag.active {
  background: var(--el-color-primary);
  color: #fff;
}

.view-toggle {
  margin-left: auto;
}

/* 知识列表 */
.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.knowledge-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  padding: 20px;
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 24px;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
}

.knowledge-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: var(--el-color-primary-light-5);
}

.knowledge-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.knowledge-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.knowledge-title {
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.knowledge-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 状态项 */
.status-list {
  display: flex;
  gap: 12px;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  border-radius: 10px;
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-light);
  cursor: pointer;
  position: relative;
  min-width: 100px;
}

.status-item:hover .status-actions {
  opacity: 1;
}

.status-item.es.active {
  background: #dcfce7;
  border-color: #10b981;
}

.status-item.vector.active {
  background: #dbeafe;
  border-color: #3b82f6;
}

.status-item.graph.active {
  background: #ede9fe;
  border-color: #8b5cf6;
}

.status-item.pending {
  background: #fef3c7;
  border-color: #f59e0b;
}

.status-header {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
}

.status-value {
  font-size: 14px;
  font-weight: 700;
}

.status-item.es .status-value { color: #10b981; }
.status-item.vector .status-value { color: #3b82f6; }
.status-item.graph .status-value { color: #8b5cf6; }
.status-item.pending .status-value { color: #f59e0b; }

.status-actions {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.2s;
  position: absolute;
  bottom: -32px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--el-bg-color);
  padding: 4px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

/* 网格视图 */
.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.knowledge-grid-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  cursor: pointer;
  transition: all 0.25s;
}

.knowledge-grid-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: var(--el-color-primary-light-5);
}

.grid-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.grid-card-title {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.grid-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.grid-card-status {
  display: flex;
  gap: 10px;
}

.grid-status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-light);
  flex: 1;
  position: relative;
}

.grid-status-item:hover .status-actions {
  opacity: 1;
}

.grid-status-item.es.active { background: #dcfce7; border-color: #10b981; }
.grid-status-item.vector.active { background: #dbeafe; border-color: #3b82f6; }
.grid-status-item.graph.active { background: #ede9fe; border-color: #8b5cf6; }
.grid-status-item.pending { background: #fef3c7; border-color: #f59e0b; }

.grid-status-header {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 6px;
}

.grid-status-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
}

.grid-status-value {
  font-size: 13px;
  font-weight: 700;
}

.grid-status-item.es .grid-status-value { color: #10b981; }
.grid-status-item.vector .grid-status-value { color: #3b82f6; }
.grid-status-item.graph .grid-status-value { color: #8b5cf6; }
.grid-status-item.pending .grid-status-value { color: #f59e0b; }

.grid-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-light);
}

.grid-card-actions {
  display: flex;
  gap: 8px;
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* 预览弹窗 */
.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
}

.preview-toolbar {
  display: flex;
  gap: 8px;
  padding: 12px 0;
  border-bottom: 1px solid var(--el-border-color-light);
  margin-bottom: 16px;
}

.preview-content {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-fill-color-lighter);
  border-radius: 8px;
}

.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--el-text-color-secondary);
}

.preview-icon {
  font-size: 64px;
  opacity: 0.5;
}

.preview-text {
  font-size: 16px;
  font-weight: 500;
}

.preview-hint {
  font-size: 14px;
  opacity: 0.7;
}
</style>