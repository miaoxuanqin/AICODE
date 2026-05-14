<template>
  <el-dialog
    v-model="visible"
    :title="knowledge?.title || '知识详情'"
    width="900px"
    top="5vh"
    :close-on-click-modal="true"
  >
    <div v-loading="loading" class="detail-content">
      <!-- 元信息 -->
      <div class="detail-meta" v-if="knowledge">
        <el-tag :type="getCategoryType(knowledge.category)">{{ knowledge.category_name }}</el-tag>
        <span class="meta-item">{{ knowledge.source || '未知来源' }}</span>
        <span class="meta-item">{{ formatDate(knowledge.created_at) }}</span>
        <span class="meta-item">{{ knowledge.view_count || 0 }} 浏览</span>
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
  } catch (e) {
    console.error('获取知识详情失败:', e)
    ElMessage.error('获取知识详情失败')
  } finally {
    loading.value = false
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
</style>