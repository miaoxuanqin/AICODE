<template>
  <div class="permission-management">
    <div class="page-header">
      <h2>权限管理</h2>
      <p class="subtitle">查看系统所有权限定义</p>
    </div>

    <el-card>
      <!-- 筛选 -->
      <div class="filter-bar">
        <el-select v-model="filterModule" placeholder="按模块筛选" clearable style="width: 200px;">
          <el-option label="系统管理" value="system" />
          <el-option label="知识管理" value="knowledge" />
          <el-option label="门户配置" value="portal" />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索权限名称或编码"
          style="width: 300px;"
          :prefix-icon="Search"
          clearable
        />
      </div>

      <!-- 权限列表 -->
      <el-table v-loading="loading" :data="filteredPermissions" stripe style="margin-top: 16px;">
        <el-table-column prop="code" label="权限编码" width="250">
          <template #default="{ row }">
            <code style="font-size: 13px;">{{ row.code }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="权限名称" width="180" />
        <el-table-column prop="module" label="所属模块" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ getModuleName(row.module) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="300" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 模块统计 -->
    <el-row :gutter="24" style="margin-top: 24px;">
      <el-col :span="8">
        <el-card class="stat-card">
          <el-statistic title="系统管理权限" :value="stats.system" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <el-statistic title="知识管理权限" :value="stats.knowledge" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <el-statistic title="门户配置权限" :value="stats.portal" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { permissionApi } from '@/api'

const filterModule = ref('')
const searchKeyword = ref('')
const loading = ref(false)
const permissions = ref([])

const fetchPermissions = async () => {
  loading.value = true
  try {
    const data = await permissionApi.list()
    permissions.value = data
  } catch (error) {
    console.error('获取权限列表失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPermissions()
})

const filteredPermissions = computed(() => {
  return permissions.value.filter(p => {
    const matchModule = !filterModule.value || p.module === filterModule.value
    const matchKeyword = !searchKeyword.value ||
      p.name.includes(searchKeyword.value) ||
      p.code.includes(searchKeyword.value)
    return matchModule && matchKeyword
  })
})

const stats = computed(() => ({
  system: permissions.value.filter(p => p.module === 'system').length,
  knowledge: permissions.value.filter(p => p.module === 'knowledge').length,
  portal: permissions.value.filter(p => p.module === 'portal').length
}))

const getModuleName = (module) => {
  const names = { system: '系统管理', knowledge: '知识管理', portal: '门户配置' }
  return names[module] || module
}
</script>

<style scoped>
.permission-management {
  max-width: 1400px;
}

.filter-bar {
  display: flex;
  gap: 12px;
}

.stat-card {
  text-align: center;
}
</style>
