<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapsed ? '64px' : '220px'" class="sidebar">
      <div class="logo">
        <el-icon v-if="!isCollapsed" :size="28" color="#daa520"><OfficeBuilding /></el-icon>
        <span v-if="!isCollapsed">住建知识库</span>
        <el-icon v-else><OfficeBuilding /></el-icon>
      </div>

      <el-menu
        :default-active="currentRoute"
        :collapse="isCollapsed"
        router
        class="sidebar-menu"
      >
        <el-sub-menu index="knowledge">
          <template #title>
            <el-icon><Reading /></el-icon>
            <span>知识库</span>
          </template>
          <el-menu-item index="/knowledge/search">
            <el-icon><Search /></el-icon>
            <span>知识搜索</span>
          </el-menu-item>
          <el-menu-item index="/knowledge/graph">
            <el-icon><Box /></el-icon>
            <span>知识图谱</span>
          </el-menu-item>
          <el-menu-item index="/knowledge/manage">
            <el-icon><Folder /></el-icon>
            <span>知识管理</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="assistant">
          <template #title>
            <el-icon><Service /></el-icon>
            <span>智能助手</span>
          </template>
          <el-menu-item index="/assistant/law">
            <el-icon><Document /></el-icon>
            <span>执法智能助手</span>
          </el-menu-item>
          <el-menu-item index="/assistant/supervise">
            <el-icon><Monitor /></el-icon>
            <span>工程监管助手</span>
          </el-menu-item>
          <el-menu-item index="/assistant/graph">
            <el-icon><Connection /></el-icon>
            <span>图谱增强问答</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/qa/chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>问答助手</span>
        </el-menu-item>

        <el-sub-menu index="system" v-if="hasSystemAccess">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/system/roles">
            <el-icon><Key /></el-icon>
            <span>角色管理</span>
          </el-menu-item>
          <el-menu-item index="/system/permissions">
            <el-icon><Lock /></el-icon>
            <span>权限管理</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapsed = !isCollapsed">
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="$route.meta.title !== '首页'">
              {{ $route.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 视角切换 -->
          <el-select v-model="currentOrg" placeholder="请选择视角" size="default" style="width: 160px; margin-right: 16px;">
            <el-option label="海南省（省级）" value="province" />
            <el-option label="海口市" value="haikou" />
            <el-option label="三亚市" value="sanya" />
          </el-select>

          <!-- 消息通知 -->
          <el-badge :value="3" class="notification-badge">
            <el-icon class="header-icon"><Bell /></el-icon>
          </el-badge>

          <!-- 用户信息 -->
          <el-dropdown @command="handleUserCommand">
            <span class="user-info">
              <el-avatar :size="32" style="margin-right: 8px;">
                {{ userInfo.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span>{{ userInfo.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  账号设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const isCollapsed = ref(false)
const currentOrg = ref('province')
const userInfo = ref({
  username: localStorage.getItem('username') || 'Admin',
  isSuperuser: localStorage.getItem('isSuperuser') === 'true'
})

const currentRoute = computed(() => route.path)
const hasSystemAccess = computed(() => userInfo.value.isSuperuser)

const handleUserCommand = (command) => {
  if (command === 'logout') {
    localStorage.clear()
    router.push('/login')
    ElMessage.success('已退出登录')
  } else if (command === 'profile') {
    ElMessage.info('个人中心功能开发中')
  }
}

onMounted(() => {
  // 模拟加载用户信息
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
  }
})
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.sidebar {
  background: linear-gradient(180deg, #1a3a6b 0%, #2c5282 100%);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  transition: width 0.3s;
  overflow-x: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.logo .el-icon {
  color: #daa520;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

/* 菜单样式 */
:deep(.el-menu) {
  background: transparent;
  border: none;
}

:deep(.el-sub-menu__title),
:deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.85);
  height: 50px;
  line-height: 50px;
}

:deep(.el-sub-menu__title:hover),
:deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(184, 134, 11, 0.3) 0%, rgba(184, 134, 11, 0.1) 100%);
  color: #fff;
  border-right: 3px solid #daa520;
}

:deep(.el-sub-menu .el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.1);
}

:deep(.el-sub-menu__title .el-icon),
:deep(.el-menu-item .el-icon) {
  color: rgba(255, 255, 255, 0.7);
}

.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(26, 58, 107, 0.08);
  border-bottom: 1px solid #e2e8f0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #1a3a6b;
}

.header-right {
  display: flex;
  align-items: center;
}

.notification-badge {
  margin-right: 20px;
}

.header-icon {
  font-size: 20px;
  cursor: pointer;
  color: #1a3a6b;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  color: #1a3a6b;
}

.user-info:hover {
  background: #f0f4f8;
}

.main-content {
  padding: 20px;
  background: #f0f4f8;
  overflow-y: auto;
}
</style>
