import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../views/DashboardView.vue'), meta: { title: '仪表盘', requiresAuth: true } },
    { path: '/analysis', component: () => import('../views/AnalysisView.vue'), meta: { title: '股票分析', requiresAuth: true } },
    { path: '/trade', component: () => import('../views/TradeView.vue'), meta: { title: '模拟交易', requiresAuth: true } },
    { path: '/login', component: () => import('../views/LoginView.vue'), meta: { title: '登录', guestOnly: true } },
    { path: '/register', component: () => import('../views/RegisterView.vue'), meta: { title: '注册', guestOnly: true } },
  ],
})

// 全局前置守卫
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated

  // 已登录用户访问登录/注册页 → 跳转首页
  if (to.meta.guestOnly && isAuthenticated) {
    return next('/')
  }

  // 需要认证的页面
  if (to.meta.requiresAuth && !isAuthenticated) {
    const redirect = to.fullPath !== '/' ? to.fullPath : ''
    const target = redirect ? `/login?redirect=${encodeURIComponent(redirect)}` : '/login'
    return next(target)
  }

  next()
})

export default router
