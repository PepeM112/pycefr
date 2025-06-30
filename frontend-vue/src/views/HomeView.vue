<script setup lang="ts">
import { onMounted } from 'vue'
import Sidebar from '@/components/Sidebar.vue'
import { useRepoStore } from '@/stores/repoStore'

const repoStore = useRepoStore()

onMounted(async () => {
  await repoStore.fetchRepos()
})
</script>

<template>
  <Sidebar />
  <div class="content">
    <header>
      <h1>Resumen</h1>
    </header>
    <div class="repos-summary-list">
      <!-- Usar v-for para listar repos -->
    </div>
  </div>
</template>

<style scoped>
/* Tus estilos SCSS convertidos */
</style>