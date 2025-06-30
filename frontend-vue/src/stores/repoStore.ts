import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/composables/useApi'

export const useRepoStore = defineStore('repo', () => {
  const repos = ref([])
  
  const fetchRepos = async () => {
    repos.value = await api.get('/api/results')
  }

  return { repos, fetchRepos }
})