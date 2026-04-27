<template>
  <div class="role-management">
    <div class="page-header">
      <h2>角色管理</h2>
      <p class="subtitle">管理系统角色和权限配置</p>
    </div>

    <el-row :gutter="24">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>角色列表</span>
              <el-button type="primary" size="small" @click="handleCreateRole">
                <el-icon><Plus /></el-icon> 新建角色
              </el-button>
            </div>
          </template>

          <div v-loading="loading">
            <div
              v-for="role in roles"
              :key="role.id"
              :class="['role-item', { active: selectedRole?.id === role.id }]"
              @click="selectRole(role)"
            >
              <div class="role-info">
                <el-icon><Key /></el-icon>
                <span class="role-name">{{ role.name }}</span>
                <el-tag v-if="role.is_system" size="small" type="info">系统</el-tag>
              </div>
              <span class="role-code">{{ role.code }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card v-if="selectedRole">
          <template #header>
            <div class="card-header">
              <span>角色详情 - {{ selectedRole.name }}</span>
              <el-button
                type="danger"
                size="small"
                @click="handleDeleteRole"
                :disabled="selectedRole.is_system"
              >
                删除角色
              </el-button>
            </div>
          </template>

          <el-descriptions :column="2" border>
            <el-descriptions-item label="角色标识">
              {{ selectedRole.code }}
            </el-descriptions-item>
            <el-descriptions-item label="角色类型">
              <el-tag :type="selectedRole.is_system ? 'info' : 'success'" size="small">
                {{ selectedRole.is_system ? '系统预置' : '自定义' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">
              {{ selectedRole.description }}
            </el-descriptions-item>
          </el-descriptions>

          <el-divider>权限配置</el-divider>

          <div class="permission-groups">
            <div v-for="group in permissionGroups" :key="group.module" class="permission-group">
              <h4>{{ group.moduleName }}</h4>
              <el-checkbox-group v-model="selectedPermissions">
                <el-checkbox
                  v-for="perm in group.permissions"
                  :key="perm.id"
                  :label="perm.id"
                  :disabled="selectedRole.is_system"
                >
                  {{ perm.name }} ({{ perm.code }})
                </el-checkbox>
              </el-checkbox-group>
            </div>
          </div>

          <div class="action-bar" v-if="!selectedRole.is_system">
            <el-button type="primary" @click="handleSavePermissions">保存配置</el-button>
          </div>
        </el-card>

        <el-card v-else>
          <div class="empty-state">
            <el-icon class="empty-icon"><Key /></el-icon>
            <p>请从左侧选择一个角色查看详情</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新建角色对话框 -->
    <el-dialog v-model="roleDialogVisible" title="新建角色" width="400px">
      <el-form ref="roleFormRef" :model="roleForm" :rules="roleRules" label-width="80px">
        <el-form-item label="角色标识" prop="code">
          <el-input v-model="roleForm.code" placeholder="如: custom_role" />
        </el-form-item>
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="如: 自定义角色" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="roleForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveRole">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Key } from '@element-plus/icons-vue'
import { roleApi, permissionApi } from '@/api'

const loading = ref(false)
const roles = ref([])
const permissions = ref([])
const selectedRole = ref(null)
const selectedPermissions = ref([])

const permissionGroups = computed(() => {
  const modules = ['system', 'knowledge', 'portal']
  const moduleNames = { system: '系统管理', knowledge: '知识管理', portal: '门户配置' }

  return modules.map(module => ({
    module,
    moduleName: moduleNames[module],
    permissions: permissions.value.filter(p => p.module === module)
  }))
})

// 获取角色列表
const fetchRoles = async () => {
  loading.value = true
  try {
    const data = await roleApi.list()
    roles.value = data
  } catch (error) {
    // 403错误已在拦截器提示，不需要重复提示
    if (error.response?.status !== 403) {
      console.error('获取角色列表失败:', error)
      ElMessage.error('获取角色列表失败')
    }
  } finally {
    loading.value = false
  }
}

// 获取权限列表
const fetchPermissions = async () => {
  try {
    const data = await permissionApi.list()
    permissions.value = data
  } catch (error) {
    console.error('获取权限列表失败:', error)
  }
}

// 选择角色
const selectRole = async (role) => {
  selectedRole.value = role
  selectedPermissions.value = []

  if (!role.is_system) {
    // 获取角色详情（含权限）
    try {
      const detail = await roleApi.get(role.id)
      selectedPermissions.value = detail.permissions.map(p => p.id)
    } catch (error) {
      console.error('获取角色详情失败:', error)
    }
  } else {
    // 系统预置角色，显示其拥有的权限
    try {
      const detail = await roleApi.get(role.id)
      selectedPermissions.value = detail.permissions.map(p => p.id)
    } catch (error) {
      console.error('获取角色详情失败:', error)
    }
  }
}

onMounted(() => {
  fetchRoles()
  fetchPermissions()
})

const roleDialogVisible = ref(false)
const roleFormRef = ref(null)
const roleForm = reactive({
  code: '',
  name: '',
  description: ''
})

const roleRules = {
  code: [{ required: true, message: '请输入角色标识', trigger: 'blur' }],
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }]
}

const handleCreateRole = () => {
  roleForm.code = ''
  roleForm.name = ''
  roleForm.description = ''
  roleDialogVisible.value = true
}

const handleSaveRole = async () => {
  if (!roleFormRef.value) return
  await roleFormRef.value.validate()

  try {
    await roleApi.create({
      code: roleForm.code,
      name: roleForm.name,
      description: roleForm.description,
      permission_ids: []
    })
    ElMessage.success('角色创建成功')
    roleDialogVisible.value = false
    fetchRoles()
  } catch (error) {
    console.error('创建角色失败:', error)
    ElMessage.error(error.response?.data?.detail || '创建角色失败')
  }
}

const handleSavePermissions = async () => {
  if (!selectedRole.value) return

  try {
    await roleApi.update(selectedRole.value.id, {
      name: selectedRole.value.name,
      description: selectedRole.value.description,
      permission_ids: selectedPermissions.value
    })
    ElMessage.success('权限配置保存成功')
    fetchRoles()
  } catch (error) {
    console.error('保存权限失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存权限失败')
  }
}

const handleDeleteRole = async () => {
  if (!selectedRole.value) return

  try {
    await ElMessageBox.confirm('确定要删除该角色吗？', '提示', { type: 'warning' })
    await roleApi.delete(selectedRole.value.id)
    ElMessage.success('角色删除成功')
    selectedRole.value = null
    fetchRoles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除角色失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除角色失败')
    }
  }
}
</script>

<style scoped>
.role-management {
  max-width: 1400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.role-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.role-item {
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.role-item:hover {
  background: #f5f7fa;
}

.role-item.active {
  background: #ecf5ff;
  border-left: 3px solid #1a3a6b;
}

.role-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.role-name {
  font-weight: 500;
  color: #303133;
}

.role-code {
  font-size: 13px;
  color: #909399;
}

.permission-groups {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.permission-group h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  color: #303133;
}

.permission-group :deep(.el-checkbox) {
  margin-right: 16px;
  margin-bottom: 8px;
}

.action-bar {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
  text-align: right;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
</style>
