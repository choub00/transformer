import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import AnalysisView from '../views/AnalysisView.vue'
import TradeView from '../views/TradeView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: DashboardView, meta: { title: '仪表盘' } },
    { path: '/analysis', component: AnalysisView, meta: { title: '股票分析' } },
    { path: '/trade', component: TradeView, meta: { title: '模拟交易' } },
  ],
})
