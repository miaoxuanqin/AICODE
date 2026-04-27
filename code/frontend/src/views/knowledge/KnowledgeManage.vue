<template>
  <div class="knowledge-manage">
    <div class="page-header">
      <h2>我的知识库</h2>
      <el-button type="primary" @click="showUploadDialog = true">
        <el-icon><Upload /></el-icon>
        上传知识
      </el-button>
      <el-button type="success" @click="showManualDialog = true">
        <el-icon><Edit /></el-icon>
        手动添加
      </el-button>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section card-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="filters.category" placeholder="知识分类" clearable @change="handleFilterChange">
            <el-option label="法律法规" value="law" />
            <el-option label="技术标准" value="tech" />
            <el-option label="执法案例" value="case" />
            <el-option label="政策文件" value="policy" />
          </el-select>
        </el-col>
        <el-col :span="12">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索知识标题..."
            @keyup.enter="handleFilterChange"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6" style="text-align: right;">
          <el-button @click="resetFilters">重置</el-button>
          <el-button type="primary" @click="handleFilterChange">查询</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 知识列表 -->
    <div class="knowledge-list">
      <el-table :data="knowledgeList" v-loading="loading" style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="300">
          <template #default="{ row }">
            <div class="knowledge-title" @click="goToDetail(row.id)">
              <span>{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" size="small">
              {{ row.category_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="180" show-overflow-tooltip />
        <el-table-column prop="view_count" label="浏览" width="80" align="center" />
        <el-table-column prop="favorite_count" label="收藏" width="80" align="center" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goToDetail(row.id)">查看</el-button>
            <el-button link type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadKnowledge"
          @current-change="loadKnowledge"
        />
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传知识" width="500px">
      <el-form ref="uploadFormRef" :model="uploadForm" label-width="80px">
        <el-form-item label="文件" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
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
        <el-form-item label="标题" prop="title">
          <el-input v-model="uploadForm.title" placeholder="不填则使用文件名" />
        </el-form-item>
        <el-form-item label="分类" required prop="category">
          <el-select v-model="uploadForm.category" placeholder="请选择分类">
            <el-option label="法律法规" value="law" />
            <el-option label="技术标准" value="tech" />
            <el-option label="执法案例" value="case" />
            <el-option label="政策文件" value="policy" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源" prop="source">
          <el-input v-model="uploadForm.source" placeholder="如：国务院令第279号" />
        </el-form-item>
        <el-form-item label="标签" prop="tags">
          <el-input v-model="uploadForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>

    <!-- 手动添加对话框 -->
    <el-dialog v-model="showManualDialog" title="手动添加知识" width="700px">
      <el-form ref="manualFormRef" :model="manualForm" label-width="80px">
        <el-form-item label="标题" required prop="title">
          <el-input v-model="manualForm.title" placeholder="请输入知识标题" />
        </el-form-item>
        <el-form-item label="内容" required prop="content">
          <div class="editor-wrapper">
            <QuillEditor v-model:content="manualForm.content" contentType="html" theme="snow" toolbar="full" />
          </div>
        </el-form-item>
        <el-form-item label="分类" required prop="category">
          <el-select v-model="manualForm.category" placeholder="请选择分类">
            <el-option label="法律法规" value="law" />
            <el-option label="技术标准" value="tech" />
            <el-option label="执法案例" value="case" />
            <el-option label="政策文件" value="policy" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源" prop="source">
          <el-input v-model="manualForm.source" placeholder="如：国务院令第279号" />
        </el-form-item>
        <el-form-item label="标签" prop="tags">
          <el-input v-model="manualForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showManualDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleManualSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { knowledgeApi } from '@/api'
import { Upload, Search, Edit } from '@element-plus/icons-vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

const router = useRouter()

const loading = ref(false)
const uploading = ref(false)
const submitting = ref(false)
const showUploadDialog = ref(false)
const showManualDialog = ref(false)
const knowledgeList = ref([])
const uploadFormRef = ref(null)
const uploadRef = ref(null)
const manualFormRef = ref(null)

const manualForm = reactive({
  title: '',
  content: '',
  category: '',
  source: '',
  tags: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const filters = reactive({
  category: '',
  keyword: ''
})

const uploadForm = reactive({
  file: null,
  title: '',
  category: '',
  source: '',
  tags: ''
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

const loadKnowledge = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filters.category) params.category = filters.category
    if (filters.keyword) params.keyword = filters.keyword

    const res = await knowledgeApi.list(params)
    knowledgeList.value = res.items
    pagination.total = res.total
  } catch (error) {
    console.error('加载知识列表失败', error)
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  pagination.page = 1
  loadKnowledge()
}

const resetFilters = () => {
  filters.category = ''
  filters.keyword = ''
  pagination.page = 1
  loadKnowledge()
}

const handleFileChange = (file) => {
  uploadForm.file = file.raw
}

const handleFileRemove = () => {
  uploadForm.file = null
}

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
    loadKnowledge()
  } catch (error) {
    console.error('上传失败', error)
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

const goToDetail = (id) => {
  router.push(`/knowledge/detail/${id}`)
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条知识吗？删除后不可恢复。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await knowledgeApi.delete(id)
    ElMessage.success('删除成功')
    loadKnowledge()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败', error)
    }
  }
}

onMounted(() => {
  loadKnowledge()
})

// 监听手动添加对话框关闭时重置表单
watch(showManualDialog, (val) => {
  if (!val) {
    resetManualForm()
  }
})

const resetManualForm = () => {
  manualForm.title = ''
  manualForm.content = ''
  manualForm.category = ''
  manualForm.source = ''
  manualForm.tags = ''
}

const handleManualSubmit = async () => {
  if (!manualForm.title) {
    ElMessage.warning('请输入标题')
    return
  }
  if (!manualForm.content || manualForm.content === '<p><br></p>' || manualForm.content === '<p></p>') {
    ElMessage.warning('请输入内容')
    return
  }
  if (!manualForm.category) {
    ElMessage.warning('请选择分类')
    return
  }

  submitting.value = true
  try {
    const data = {
      title: manualForm.title,
      content: manualForm.content,
      category: manualForm.category,
      source: manualForm.source || null,
      tags: manualForm.tags ? manualForm.tags.split(',').map(t => t.trim()).filter(t => t) : []
    }
    await knowledgeApi.createManual(data)
    ElMessage.success('添加成功')
    showManualDialog.value = false
    loadKnowledge()
  } catch (error) {
    console.error('添加失败', error)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.knowledge-manage {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.page-header .el-button {
  margin-left: 10px;
}

.filter-section {
  padding: 20px;
  margin-bottom: 20px;
}

.knowledge-list {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.knowledge-title {
  cursor: pointer;
  color: #1a3a6b;
}

.knowledge-title:hover {
  text-decoration: underline;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.card-container {
  background: #fff;
  border-radius: 8px;
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
