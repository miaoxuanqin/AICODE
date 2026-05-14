<template>
  <div class="knowledge-manage-new">
    <!-- 左侧分类树 -->
    <div class="category-sidebar">
      <div class="sidebar-header">
        <span>知识分类</span>
        <el-button size="small" link type="primary" @click="showCategoryDialog('create')">+ 新增</el-button>
      </div>
      <el-tree
        ref="categoryTreeRef"
        :data="categoryTree"
        :props="{ children: 'children', label: 'name' }"
        node-key="id"
        default-expand-all
        highlight-current
        :expand-on-click-node="false"
        @node-click="handleCategoryNodeClick"
      >
        <template #default="{ node, data }">
          <span class="tree-node">
            <span v-if="data.id === ''" class="node-icon">📁</span>
            <span v-else-if="data.children && data.children.length > 0" class="node-icon">📂</span>
            <span v-else class="node-icon">📄</span>
            <span class="node-label">{{ node.label }}</span>
            <span class="node-actions">
              <el-button size="small" link type="primary" @click.stop="showCategoryDialog('edit', data)">编辑</el-button>
              <el-button size="small" link type="danger" @click.stop="handleDeleteCategory(data)">删除</el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </div>

    <!-- 右侧主内容 -->
    <div class="main-content">
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
          <el-option label="Word文档" value="docx" />
          <el-option label="文本" value="text" />
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
                {{ item.file_type === 'pdf' ? '📕 PDF' : item.file_type === 'html' ? '📝 文本' : item.file_type === 'docx' || item.file_type === 'doc' ? '📄 Word' : '📝 文本' }}
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
            <el-tag size="small">{{ item.file_type === 'pdf' ? 'PDF' : item.file_type === 'html' ? '文本' : (item.file_type === 'docx' || item.file_type === 'doc') ? 'Word' : '文本' }}</el-tag>
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
    </div>

    <!-- 分类管理弹窗 -->
    <el-dialog v-model="showCategoryDialogVisible" :title="categoryDialogTitle" width="400px">
      <el-form ref="categoryFormRef" :model="categoryForm" label-width="80px">
        <el-form-item label="分类名称" required>
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="上级分类">
          <el-select v-model="categoryForm.parent_id" placeholder="无上级分类（顶级）" clearable>
            <el-option v-for="cat in flatCategoryList" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="categoryForm.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCategoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCategory">确定</el-button>
      </template>
    </el-dialog>

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
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
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
            <el-option v-for="cat in flatCategoryList" :key="cat.id" :label="cat.name" :value="String(cat.id)" />
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
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>

    <!-- 文本弹窗 -->
    <el-dialog v-model="showTextDialog" title="手动添加知识" width="700px">
      <el-form ref="textFormRef" :model="textForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="textForm.title" placeholder="请输入知识标题" />
        </el-form-item>
        <el-form-item label="内容" required>
          <div class="editor-wrapper">
            <QuillEditor v-model:content="textForm.content" contentType="html" theme="snow" toolbar="full" />
          </div>
        </el-form-item>
        <el-form-item label="分类" required>
          <el-select v-model="textForm.category" placeholder="请选择分类">
            <el-option v-for="cat in flatCategoryList" :key="cat.id" :label="cat.name" :value="String(cat.id)" />
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
        <el-button type="primary" :loading="submitting" @click="handleTextSubmit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="showEditDialog" title="编辑知识" width="500px">
      <el-form ref="editFormRef" :model="editForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="editForm.title" placeholder="请输入知识标题" />
        </el-form-item>
        <el-form-item label="分类" required>
          <el-select v-model="editForm.category" placeholder="请选择分类">
            <el-option v-for="cat in flatCategoryList" :key="cat.id" :label="cat.name" :value="String(cat.id)" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="editForm.source" placeholder="如：国务院令第279号" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="editForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 预览弹窗 -->
    <el-dialog v-model="showPreview" title="知识预览" width="900px" top="5vh">
      <div class="preview-header">
        <div class="preview-title">
          <span>{{ previewItem.title }}</span>
          <el-tag :type="previewItem.file_type === 'pdf' ? 'danger' : 'primary'">
            {{ previewItem.file_type === 'pdf' ? 'PDF文档' : previewItem.file_type === 'html' ? '文本' : (previewItem.file_type === 'docx' || previewItem.file_type === 'doc') ? 'Word文档' : '文本' }}
          </el-tag>
        </div>
      </div>
      <div class="preview-content">
        <!-- 文本内容显示 -->
        <div v-if="!previewItem.file_type || previewItem.file_type === 'html' || previewItem.file_type === 'unknown'" class="text-preview" v-html="previewItem.content || '<p style=\'color:#999;text-align:center\'>内容加载中...</p>'"></div>
        <!-- PDF预览 -->
        <div v-if="previewItem.file_type === 'pdf'" id="pdf-preview-container" class="pdf-preview-container"></div>
        <div v-if="previewItem.file_type === 'pdf' && previewItem.loading" class="preview-loading">
          <el-icon class="is-loading"><Document /></el-icon>
          <div>正在加载PDF...</div>
        </div>
        <!-- Word预览 -->
        <div v-if="(previewItem.file_type === 'docx' || previewItem.file_type === 'doc') && previewItem.loading" class="preview-loading">
          <el-icon class="is-loading"><Document /></el-icon>
          <div>正在加载Word...</div>
        </div>
        <div v-if="(previewItem.file_type === 'docx' || previewItem.file_type === 'doc') && !previewItem.loading" class="word-preview text-preview" v-html="previewItem.wordContent"></div>
        <!-- 文件下载按钮 -->
        <div v-if="previewItem.file_type === 'pdf' || previewItem.file_type === 'docx' || previewItem.file_type === 'doc'" class="preview-toolbar">
          <el-button size="small" @click="downloadFile">下载</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
console.log('=== KnowledgeManageNew 初始化 ===')
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, Search, Connection, Grid, List, View, Edit, Delete,
  Upload, Clock, Folder, UploadFilled
} from '@element-plus/icons-vue'
import { knowledgeApi, categoryApi } from '@/api/index.js'
import { useRouter } from 'vue-router'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import mammoth from 'mammoth'
import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf.mjs'

// 为 legacy build 手动设置 workerSrc（legacy 默认的 ./pdf.worker.mjs 在 Vite 中解析不正确）
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL('pdfjs-dist/legacy/build/pdf.worker.min.mjs', import.meta.url).href
console.log('PDF workerSrc:', pdfjsLib.GlobalWorkerOptions.workerSrc)

const router = useRouter()

// 视图模式
const viewMode = ref('grid')

// 加载状态
const loading = ref(false)
const uploading = ref(false)
const submitting = ref(false)

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
const showCategoryDialogVisible = ref(false)

// 分类树相关
const categoryTree = ref([])
const categoryTreeRef = ref(null)
const categoryDialogTitle = ref('新增分类')
const categoryFormRef = ref(null)
const categoryForm = reactive({
  id: null,
  name: '',
  parent_id: null,
  sort_order: 0
})
const categoryAction = ref('create') // 'create' or 'edit'

// 扁平分类列表（用于上级分类选择）
const flatCategoryList = computed(() => {
  const flatten = (cats, result = []) => {
    cats.forEach(cat => {
      if (cat.id !== '') { // 跳过"全部"节点
        result.push(cat)
      }
      if (cat.children && cat.children.length > 0) {
        flatten(cat.children, result)
      }
    })
    return result
  }
  return flatten(categoryTree.value)
})

// 表单 ref
const uploadFormRef = ref(null)
const uploadRef = ref(null)
const textFormRef = ref(null)

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

// 编辑表单
const showEditDialog = ref(false)
const editFormRef = ref(null)
const editLoading = ref(false)
const editForm = reactive({
  id: '',
  title: '',
  category: '',
  source: '',
  tags: ''
})

// 预览项
const previewItem = ref({ id: '', title: '', file_type: 'pdf', url: '', content: '', wordContent: '', loading: false })

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
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.type) params.type = filters.type
    if (filters.category) params.category = filters.category
    if (filters.fullTextStatus) params.es_indexed = filters.fullTextStatus
    if (filters.vectorStatus) params.vector_indexed = filters.vectorStatus
    if (filters.graphStatus) params.graph_indexed = filters.graphStatus

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
  } finally {
    loading.value = false
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
  if (!uploadForm.file) {
    ElMessage.warning('请选择文件')
    return
  }
  if (!uploadForm.category) {
    ElMessage.warning('请选择分类')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadForm.file)
    if (uploadForm.title) formData.append('title', uploadForm.title)
    formData.append('category', uploadForm.category)
    if (uploadForm.source) formData.append('source', uploadForm.source)
    if (uploadForm.tags) formData.append('tags', uploadForm.tags)

    await knowledgeApi.upload(formData)
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    resetUploadForm()
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const resetUploadForm = () => {
  uploadForm.file = null
  uploadForm.title = ''
  uploadForm.category = ''
  uploadForm.source = ''
  uploadForm.tags = ''
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 添加文本
const handleTextSubmit = async () => {
  if (!textForm.title) {
    ElMessage.warning('请输入标题')
    return
  }
  if (!textForm.content || textForm.content === '<p><br></p>' || textForm.content === '<p></p>') {
    ElMessage.warning('请输入内容')
    return
  }
  if (!textForm.category) {
    ElMessage.warning('请选择分类')
    return
  }

  submitting.value = true
  try {
    const data = {
      title: textForm.title,
      content: textForm.content,
      category: textForm.category,
      source: textForm.source || null,
      tags: textForm.tags ? textForm.tags.split(',').map(t => t.trim()).filter(t => t) : []
    }
    await knowledgeApi.createManual(data)
    ElMessage.success('知识添加成功')
    showTextDialog.value = false
    loadData()
    loadStats()
  } catch (error) {
    ElMessage.error('添加失败')
  } finally {
    submitting.value = false
  }
}

const resetTextForm = () => {
  textForm.title = ''
  textForm.content = ''
  textForm.category = ''
  textForm.source = ''
  textForm.tags = ''
}

// 监听文本弹窗关闭时重置表单
watch(showTextDialog, (val) => {
  if (!val) {
    resetTextForm()
  }
})

// 下载文件
const downloadFile = async () => {
  if (!previewItem.value.title) return
  try {
    ElMessage.info('正在准备下载...')
    const response = await knowledgeApi.download(previewItem.value.id || previewItem.value.title)
    const blob = new Blob([response])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${previewItem.value.title}.${previewItem.value.file_type}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

// 查看
const viewFile = async (item) => {
  console.log('=== viewFile 开始 ===')
  console.log('点击知识:', item.title, 'file_type:', item.file_type, 'file_path:', item.file_path)
  const hasFile = item.file_type && item.file_path
  console.log('hasFile:', hasFile)

  if (hasFile) {
    console.log('走文件预览路线, file_type:', item.file_type)
    previewItem.value = { id: item.id, title: item.title, file_type: item.file_type, url: '', content: '', wordContent: '', loading: true }
    showPreview.value = true

    try {
      console.log('调用 knowledgeApi.download, id:', item.id)
      const response = await knowledgeApi.download(item.id)
      console.log('download 返回, type:', typeof response, 'is Blob:', response instanceof Blob)
      console.log('响应数据 keys:', Object.keys(response))
      if (!response) {
        throw new Error('响应为空')
      }
      console.log('下载完成，准备创建Blob')
      // Axios response 对象: response.data 才是真正的数据
      const rawData = response.data || response
      const blob = new Blob([rawData], { type: 'application/pdf' })
      console.log('Blob创建完成, 大小:', blob.size)

      if (item.file_type === 'pdf') {
        console.log('进入PDF预览')
        await renderPdfPreview(blob)
      } else if (item.file_type === 'docx') {
        await renderWordPreview(blob)
      } else {
        showPreview.value = false
        ElMessage.warning('此文件格式不支持预览，将开始下载')
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${item.title}.${item.file_type}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      }
      return
    } catch (error) {
      console.error('获取文件失败:', error)
      ElMessage.error('获取文件失败')
      showPreview.value = false
      return
    }
  }

  // 无文件的知识（如文本类型），直接从API获取内容
  previewItem.value = { id: item.id, title: item.title, file_type: item.file_type, url: '', content: '', wordContent: '', loading: true }
  showPreview.value = true

  try {
    const detail = await knowledgeApi.get(item.id)
    previewItem.value.content = detail.content || ''
  } catch (e) {
    console.error('获取内容失败:', e)
  }
  previewItem.value.loading = false
}

// 渲染 PDF 预览
const renderPdfPreview = async (blob) => {
  console.log('=== renderPdfPreview 开始 ===')
  console.log('blob type:', blob.type, 'size:', blob.size)

  // 等待容器出现
  let container = document.getElementById('pdf-preview-container')
  let waitCount = 0
  while (!container && waitCount < 100) {
    await new Promise(r => setTimeout(r, 100))
    container = document.getElementById('pdf-preview-container')
    waitCount++
  }
  if (!container) {
    console.log('容器不存在!')
    return
  }
  console.log('找到容器!')

  try {
    console.log('创建ArrayBuffer...')
    const arrayBuffer = await blob.arrayBuffer()
    console.log('ArrayBuffer创建完成，长度:', arrayBuffer.byteLength)

    console.log('创建PDF文档...')
    const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer })
    console.log('LoadingTask created')

    console.log('等待PDF文档加载...')
    const pdf = await loadingTask.promise
    console.log('PDF加载成功, 页数:', pdf.numPages)

    container.innerHTML = ''
    container.style.overflow = 'auto'
    container.style.maxHeight = '70vh'

    for (let i = 1; i <= pdf.numPages; i++) {
      console.log('渲染第', i, '页')
      const page = await pdf.getPage(i)
      const scale = 1.5
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
      console.log('第', i, '页渲染完成')
    }
    previewItem.value.loading = false
    console.log('=== PDF渲染完成 ===')
  } catch (error) {
    console.error('PDF 渲染失败:', error)
    previewItem.value.loading = false
  }
}

// 渲染 Word 预览
const renderWordPreview = async (blob) => {
  console.log('=== renderWordPreview 开始 ===')
  try {
    const arrayBuffer = await blob.arrayBuffer()
    console.log('ArrayBuffer ready, converting with mammoth...')
    const result = await mammoth.convertToHtml({ arrayBuffer })
    console.log('Mammoth conversion done, html length:', result.value?.length)
    previewItem.value.wordContent = result.value
    previewItem.value.loading = false
    console.log('=== Word渲染完成 ===')
  } catch (error) {
    console.error('Word 渲染失败:', error)
    ElMessage.error('Word加载失败: ' + error.message)
    previewItem.value.loading = false
  }
}

// 编辑
const editItem = (item) => {
  editForm.id = item.id
  editForm.title = item.title || ''
  editForm.category = item.category || ''
  editForm.source = item.source || ''
  editForm.tags = Array.isArray(item.tags) ? item.tags.join(', ') : (item.tags || '')
  showEditDialog.value = true
}

// 保存编辑
const handleEditSave = async () => {
  if (!editForm.category) {
    ElMessage.warning('请选择分类')
    return
  }
  editLoading.value = true
  try {
    await knowledgeApi.update(editForm.id, {
      category: editForm.category,
      source: editForm.source || null,
      tags: editForm.tags ? editForm.tags.split(',').map(t => t.trim()).filter(t => t) : []
    })
    ElMessage.success('更新成功')
    showEditDialog.value = false
    loadData()
  } catch (e) {
    ElMessage.error('更新失败')
  } finally {
    editLoading.value = false
  }
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
  console.log('retryProcess called, item:', item.id, 'type:', type)
  try {
    const res = await knowledgeApi.rebuild(item.id, type)
    console.log('rebuild 返回:', res)

    if (type === 'graph') {
      // 图谱处理需要时间，显示进度提示并等待
      ElMessage.info('正在处理知识图谱，请稍候...')
      // 每2秒轮询一次，最多6次（12秒）
      let retries = 6
      const checkStatus = async () => {
        if (retries <= 0) {
          ElMessage.warning('图谱处理超时，请稍后刷新页面查看结果')
          loadData()
          return
        }
        retries--
        await new Promise(r => setTimeout(r, 2000))
        // 重新获取数据检查状态
        const checkRes = await knowledgeApi.get(item.id)
        if (checkRes && checkRes.graph_indexed === 'done') {
          ElMessage.success('知识图谱重建完成')
          loadData()
        } else if (checkRes && checkRes.graph_indexed === 'failed') {
          ElMessage.error('知识图谱重建失败')
          loadData()
        } else {
          checkStatus()
        }
      }
      checkStatus()
    } else {
      ElMessage.success(`已提交${names[type]}重建任务`)
      loadData()
    }
  } catch (error) {
    console.error('重建失败:', error)
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
  console.log('=== onMounted 调用 ===')
  loadCategoryTree()
  loadData()
  loadStats()
})

// 加载分类树
const loadCategoryTree = async () => {
  try {
    const res = await categoryApi.list() || []
    // 添加"全部"总级别节点
    categoryTree.value = [{
      id: '',
      name: '全部',
      parent_id: null,
      level: 0,
      children: res
    }]
  } catch (error) {
    console.error('加载分类树失败:', error)
  }
}

// 分类树节点点击
const handleCategoryNodeClick = (data) => {
  filters.category = data.id === '' ? '' : String(data.id)
  handleFilter()
}

// 显示分类弹窗
const showCategoryDialog = (action, data) => {
  categoryAction.value = action
  if (action === 'edit' && data) {
    categoryDialogTitle.value = '编辑分类'
    categoryForm.id = data.id
    categoryForm.name = data.name
    categoryForm.parent_id = data.parent_id
    categoryForm.sort_order = data.sort_order || 0
  } else {
    categoryDialogTitle.value = '新增分类'
    categoryForm.id = null
    categoryForm.name = ''
    categoryForm.parent_id = null
    categoryForm.sort_order = 0
  }
  showCategoryDialogVisible.value = true
}

// 保存分类
const handleSaveCategory = async () => {
  if (!categoryForm.name) {
    ElMessage.warning('请输入分类名称')
    return
  }
  try {
    if (categoryAction.value === 'edit') {
      await categoryApi.update(categoryForm.id, {
        name: categoryForm.name,
        parent_id: categoryForm.parent_id,
        sort_order: categoryForm.sort_order
      })
      ElMessage.success('分类已更新')
    } else {
      await categoryApi.create({
        name: categoryForm.name,
        parent_id: categoryForm.parent_id,
        sort_order: categoryForm.sort_order
      })
      ElMessage.success('分类已创建')
    }
    showCategoryDialogVisible.value = false
    loadCategoryTree()
  } catch (error) {
    console.error('保存分类失败:', error)
    ElMessage.error(error.detail || '保存失败')
  }
}

// 删除分类
const handleDeleteCategory = async (data) => {
  try {
    await ElMessageBox.confirm(`确定要删除分类"${data.name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await categoryApi.delete(data.id)
    ElMessage.success('分类已删除')
    loadCategoryTree()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除分类失败:', error)
      ElMessage.error(error.detail || '删除失败')
    }
  }
}
</script>

<style scoped>
.knowledge-manage-new {
  padding: 24px;
  display: flex;
  gap: 24px;
}

.category-sidebar {
  width: 260px;
  min-width: 260px;
  background: linear-gradient(180deg, #f8fafc 0%, #fff 100%);
  border-radius: 12px;
  padding: 0;
  position: sticky;
  top: 24px;
  max-height: calc(100vh - 48px);
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px 12px 0 0;
  color: #fff;
  font-weight: 600;
  font-size: 14px;
}

.sidebar-header .el-button {
  color: rgba(255, 255, 255, 0.85);
  font-size: 12px;
}

.sidebar-header .el-button:hover {
  color: #fff;
}

/* 分类树容器 */
.category-sidebar :deep(.el-tree) {
  background: transparent;
  padding: 12px 8px;
  min-height: 200px;
}

.category-sidebar :deep(.el-tree-node__content) {
  height: 38px;
  border-radius: 8px;
  margin: 2px 4px;
  padding-left: 12px !important;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.category-sidebar :deep(.el-tree-node__content:hover) {
  background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);
  border-color: #c7d2fe;
}

.category-sidebar :deep(.el-tree-node__content:active) {
  background: #e0e7ff;
}

/* 选中节点高亮 */
.category-sidebar :deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%) !important;
  border-color: #667eea40 !important;
  box-shadow: 0 0 0 2px #667eea20;
}

.category-sidebar :deep(.el-tree-node.is-current > .el-tree-node__content .node-label) {
  color: #667eea;
  font-weight: 600;
}

/* 展开/收起图标 */
.category-sidebar :deep(.el-tree-node__expand-icon) {
  color: #94a3b8;
  font-size: 14px;
  transition: transform 0.3s ease;
}

.category-sidebar :deep(.el-tree-node__expand-icon.expanded) {
  transform: rotate(90deg);
}

/* 叶节点图标 */
.category-sidebar :deep(.el-tree-node__content:has(.is-leaf)) {
  padding-left: 28px !important;
}

/* 树节点整体布局 */
.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0 8px 0 0;
  gap: 8px;
}

.node-label {
  flex: 1;
  font-size: 13px;
  color: #475569;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.2s;
}

/* 文件夹图标 */
.node-icon {
  width: 18px;
  height: 18px;
  margin-right: 8px;
  color: #64748b;
  flex-shrink: 0;
}

.category-sidebar :deep(.el-tree-node__content:hover .node-label) {
  color: #334155;
}

/* 操作按钮（编辑/删除） */
.node-actions {
  display: none;
  gap: 2px;
  flex-shrink: 0;
}

.tree-node:hover .node-actions {
  display: inline-flex;
}

.node-actions .el-button {
  padding: 4px 8px;
  font-size: 11px;
  border-radius: 4px;
  opacity: 0.7;
  transition: all 0.2s;
}

.node-actions .el-button:hover {
  opacity: 1;
}

/* "全部" 节点特殊样式 */
.category-sidebar :deep(.el-tree-node__content:has(> .tree-node > .node-label[style*="全部"]) ) {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px dashed #cbd5e1;
}

.category-sidebar :deep(.el-tree-node__content:has(> .tree-node > .node-label[style*="全部"]) .node-label) {
  font-weight: 600;
  color: #64748b;
}

/* 滚动条美化 */
.category-sidebar::-webkit-scrollbar {
  width: 6px;
}

.category-sidebar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.category-sidebar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.category-sidebar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.main-content {
  flex: 1;
  min-width: 0;
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

.file-preview-iframe {
  width: 100%;
  height: 600px;
  border: none;
}

.text-preview {
  padding: 20px;
  line-height: 1.8;
  max-height: 600px;
  overflow-y: auto;
}

.text-preview :deep(p) {
  margin-bottom: 12px;
}

.preview-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 60px 20px;
  color: var(--el-text-color-secondary);
}

.preview-loading .el-icon {
  font-size: 48px;
}

.pdf-preview-container {
  padding: 10px;
  background: #f5f5f5;
  text-align: center;
}

.pdf-preview-container canvas {
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 10px;
}

.word-preview {
  background: white;
}

.word-preview :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 16px 0;
}

.word-preview :deep(td) {
  border: 1px solid #ddd;
  padding: 8px;
}

/* 富文本编辑器样式 */
.editor-wrapper {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-wrapper :deep(.ql-toolbar) {
  border: none;
  border-bottom: 1px solid #dcdfe6;
  background: #f5f7fa;
}

.editor-wrapper :deep(.ql-container) {
  border: none;
  font-size: 14px;
}

.editor-wrapper :deep(.ql-editor) {
  min-height: 200px;
  max-height: 300px;
  overflow-y: auto;
  writing-mode: horizontal-tb !important;
}

.editor-wrapper :deep(.ql-editor.ql-blank::before) {
  writing-mode: horizontal-tb !important;
  color: #c0c4cc;
  font-style: normal;
  left: 12px;
}
</style>
