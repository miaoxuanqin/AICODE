<template>
  <div class="user-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <p class="subtitle">管理系统用户账号和权限分配</p>
    </div>

    <el-card>
      <!-- 工具栏 -->
      <div class="toolbar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户名、姓名..."
          style="width: 300px;"
          :prefix-icon="Search"
          clearable
        />
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建用户
        </el-button>
      </div>

      <!-- 用户表格 -->
      <el-table v-loading="loading" :data="filteredUsers" stripe style="width: 100%; margin-top: 16px;">
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="full_name" label="姓名" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="phone" label="手机号" width="150" />
        <el-table-column label="已分配角色" width="200">
          <template #default="{ row }">
            <el-tag
              v-for="roleId in (row.role_ids || [])"
              :key="roleId"
              size="small"
              style="margin-right: 4px;"
            >
              {{ getRoleName(roleId) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="success" @click="handleAssignRoles(row)">分配角色</el-button>
            <el-button link type="danger" @click="handleDelete(row)" :disabled="row.username === 'admin'">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="userDialogVisible"
      :title="isEdit ? '编辑用户' : '新建用户'"
      width="500px"
    >
      <el-form ref="userFormRef" :model="userForm" :rules="userRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="userForm.full_name" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveUser">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分配角色对话框 -->
    <el-dialog v-model="roleDialogVisible" title="分配角色" width="500px">
      <el-form label-width="80px">
        <el-form-item label="用户">
          <span>{{ currentUser?.username }}</span>
        </el-form-item>
        <el-form-item label="选择角色">
          <el-checkbox-group v-model="selectedRoles">
            <el-checkbox
              v-for="role in allRoles"
              :key="role.id"
              :label="role.id"
            >
              {{ role.name }} ({{ role.code }})
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveRoles">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { userApi, roleApi } from '@/api'

const searchKeyword = ref('')
const loading = ref(false)
const users = ref([])
const allRoles = ref([])

const filteredUsers = computed(() => {
  return users.value.filter(user => {
    const matchKeyword = !searchKeyword.value ||
      user.username.includes(searchKeyword.value) ||
      (user.full_name && user.full_name.includes(searchKeyword.value)) ||
      (user.email && user.email.includes(searchKeyword.value))
    return matchKeyword
  })
})

// 根据角色ID获取角色名称
const getRoleName = (roleId) => {
  const role = allRoles.value.find(r => r.id === roleId)
  return role ? role.name : roleId
}

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const data = await userApi.list()
    users.value = data
  } catch (error) {
    // 403错误已在拦截器提示，不需要重复提示
    if (error.response?.status !== 403) {
      console.error('获取用户列表失败:', error)
      ElMessage.error('获取用户列表失败')
    }
  } finally {
    loading.value = false
  }
}

// 获取角色列表
const fetchRoles = async () => {
  try {
    const data = await roleApi.list()
    allRoles.value = data
  } catch (error) {
    // 403错误已在拦截器提示，不需要重复提示
    if (error.response?.status !== 403) {
      console.error('获取角色列表失败:', error)
    }
  }
}

onMounted(() => {
  fetchUsers()
  fetchRoles()
})

// 创建/编辑用户
const userDialogVisible = ref(false)
const isEdit = ref(false)
const userFormRef = ref(null)
const userForm = reactive({
  username: '',
  full_name: '',
  email: '',
  phone: '',
  password: '',
  is_active: true
})

const userRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur', validator: (rule, value, callback) => {
      if (!isEdit.value && !value) {
        callback(new Error('请输入密码'))
      } else if (value && value.length < 6) {
        callback(new Error('密码至少6位'))
      } else {
        callback()
      }
    }}
  ]
}

const handleCreate = () => {
  isEdit.value = false
  Object.assign(userForm, {
    username: '',
    full_name: '',
    email: '',
    phone: '',
    password: '',
    is_active: true
  })
  userDialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(userForm, {
    username: row.username,
    full_name: row.full_name || '',
    email: row.email || '',
    phone: row.phone || '',
    password: '',
    is_active: row.is_active
  })
  userDialogVisible.value = true
}

const handleSaveUser = async () => {
  if (!userFormRef.value) return
  await userFormRef.value.validate()

  try {
    if (isEdit.value) {
      const updateData = {
        full_name: userForm.full_name,
        email: userForm.email,
        phone: userForm.phone,
        is_active: userForm.is_active
      }
      await userApi.update(userForm.username, updateData)
      ElMessage.success('用户更新成功')
    } else {
      await userApi.create({
        username: userForm.username,
        password: userForm.password,
        full_name: userForm.full_name,
        email: userForm.email,
        phone: userForm.phone,
        is_active: userForm.is_active
      })
      ElMessage.success('用户创建成功')
    }
    userDialogVisible.value = false
    fetchUsers()
  } catch (error) {
    console.error('保存用户失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存用户失败')
  }
}

// 分配角色
const roleDialogVisible = ref(false)
const currentUser = ref(null)
const selectedRoles = ref([])

const handleAssignRoles = async (row) => {
  currentUser.value = row
  selectedRoles.value = row.role_ids || []
  roleDialogVisible.value = true
}

const handleSaveRoles = async () => {
  if (!currentUser.value) return

  try {
    await userApi.assignRoles(currentUser.value.id, selectedRoles.value)
    ElMessage.success('角色分配成功')
    roleDialogVisible.value = false
  } catch (error) {
    console.error('角色分配失败:', error)
    ElMessage.error(error.response?.data?.detail || '角色分配失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户"${row.username}"吗？`, '提示', {
      type: 'warning'
    })
    await userApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除用户失败')
    }
  }
}
</script>

<style scoped>
.user-management {
  max-width: 1400px;
}

.toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
