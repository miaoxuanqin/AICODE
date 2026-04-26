import { defineStore } from 'pinia'
import request from '@/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null,
    token: localStorage.getItem('token') || '',
    permissions: []
  }),

  getters: {
    isLoggedIn: state => !!state.token,
    isSuperuser: state => state.userInfo?.isSuperuser || false
  },

  actions: {
    async login(username, password) {
      const res = await request.post('/v1/auth/login', { username, password })
      this.token = res.access_token
      localStorage.setItem('token', res.access_token)
      await this.getUserInfo()
    },

    async getUserInfo() {
      try {
        const res = await request.get('/v1/auth/me')
        this.userInfo = res
        localStorage.setItem('user_id', res.id)
        localStorage.setItem('username', res.username)
        localStorage.setItem('isSuperuser', res.isSuperuser)
      } catch (error) {
        console.error('获取用户信息失败', error)
      }
    },

    logout() {
      this.token = ''
      this.userInfo = null
      this.permissions = []
      localStorage.clear()
    }
  }
})
