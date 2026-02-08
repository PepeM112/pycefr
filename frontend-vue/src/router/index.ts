import { RouteNames } from '@/router/route-names';
import HomeView from '@/views/HomeView.vue';
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: RouteNames.HOME, component: HomeView },
    { path: '/repo/:id', name: RouteNames.ANALYSIS_DETAIL, component: () => import('@/views/AnalysisDetailsView.vue') },
    { path: '/analyses', name: RouteNames.ANALYSIS_LIST, component: () => import('@/views/AnalysesView.vue') },
  ],
});

export default router;
