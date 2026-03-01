<template>
  <v-card class="pa-4 h-100" variant="outlined">
    <h3 class="text-subtitle-1 font-weight-bold mb-4">{{ $t(title) }}</h3>
    <div class="chart-container w-100">
      <slot />
    </div>
  </v-card>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
}>();
</script>

<style lang="scss" scoped>
.chart-container {
  height: 280px;
  position: relative;
}
</style>
