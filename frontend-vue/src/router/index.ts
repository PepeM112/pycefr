import { RouteNames } from '@/router/route-names';
import HomeView from '@/views/HomeView.vue';
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: RouteNames.HOME, component: HomeView },
    { path: '/repo/:id', name: RouteNames.REPO_DETAIL, component: () => import('@/views/RepoView.vue') },
    { path: '/analyses', name: RouteNames.ANALYSES, component: () => import('@/views/AnalysesView.vue') },
  ],
});

export default router;
