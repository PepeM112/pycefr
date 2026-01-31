import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '@/views/HomeView.vue';
import RepoView from '@/views/RepoView.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/repo/:id', name: 'repo-detail', component: RepoView },
  ],
});

export default router;
