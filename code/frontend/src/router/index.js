import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import Layout from '@/components/layout/MainLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/knowledge/search',
    children: [
      {
        path: 'knowledge/search',
        name: 'KnowledgeSearch',
        component: () => import('@/views/knowledge/SearchPortal.vue'),
        meta: { title: '知识搜索', icon: 'Search' }
      },
      {
        path: 'knowledge/manage',
        name: 'KnowledgeManage',
        component: () => import('@/views/knowledge/KnowledgeManage.vue'),
        meta: { title: '知识管理', icon: 'Folder' }
      },
      {
        path: 'knowledge/detail/:id',
        name: 'KnowledgeDetail',
        component: () => import('@/views/knowledge/KnowledgeDetail.vue'),
        meta: { title: '知识详情', hidden: true }
      },
      {
        path: 'assistant/law',
        name: 'LawAssistant',
        component: () => import('@/views/assistant/LawAssistant.vue'),
        meta: { title: '执法智能助手', icon: 'Service' }
      },
      {
        path: 'assistant/supervise',
        name: 'SuperviseAssistant',
        component: () => import('@/views/assistant/SuperviseAssistant.vue'),
        meta: { title: '工程监管助手', icon: 'Monitor' }
      },
      {
        path: 'assistant/graph',
        name: 'GraphQA',
        component: () => import('@/views/graph/GraphQAChat.vue'),
        meta: { title: '图谱增强问答', icon: 'Connection' }
      },
      {
        path: 'qa/chat',
        name: 'QAChat',
        component: () => import('@/views/qa/QAChat.vue'),
        meta: { title: '问答助手', icon: 'ChatDotRound' }
      },
      {
        path: 'system/users',
        name: 'UserManagement',
        component: () => import('@/views/system/UserManagement.vue'),
        meta: { title: '用户管理', icon: 'User', requireAdmin: true }
      },
      {
        path: 'system/roles',
        name: 'RoleManagement',
        component: () => import('@/views/system/RoleManagement.vue'),
        meta: { title: '角色管理', icon: 'Key', requireAdmin: true }
      },
      {
        path: 'system/permissions',
        name: 'PermissionManagement',
        component: () => import('@/views/system/PermissionManagement.vue'),
        meta: { title: '权限管理', icon: 'Lock', requireAdmin: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '知识库'} - 海南省住建知识库`
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else if (to.path !== '/login' && token) {
    // 检查是否访问系统管理页面
    if (to.meta.requireAdmin) {
      const isSuperuser = localStorage.getItem('isSuperuser') === 'true'
      if (!isSuperuser) {
        ElMessage.warning('您没有访问该页面的权限')
        next('/knowledge/search')
      } else {
        next()
      }
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
