<script setup lang="ts">
import { ref } from 'vue'

const isDarkMode = ref(false)
const toggleSidebar = () => {
  // Lógica del sidebar
}
</script>

<template>
  <aside class="sidebar" :class="{ 'dark-mode': isDarkMode }">
    <!-- Contenido del sidebar -->
  </aside>
</template>

<style scoped lang="scss">
@import '@/assets/scss/sidebar';
</style>