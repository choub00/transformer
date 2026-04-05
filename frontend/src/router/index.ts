import { createRouter, createWebHistory } from 'vue-router'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../views/DashboardView.vue'), meta: { title: '仪表盘' } },
    { path: '/analysis', component: () => import('../views/AnalysisView.vue'), meta: { title: '股票分析' } },
    { path: '/trade', component: () => import('../views/TradeView.vue'), meta: { title: '模拟交易' } },
  ],
})
