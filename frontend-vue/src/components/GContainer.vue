<template>
  <section>
    <h2 v-if="title">{{ $t(title) }}</h2>
    <slot />
  </section>
</template>
<script setup lang="ts">
const props = defineProps<{
  title?: string;
}>();
</script>
<style lang="scss" scoped>
section {
  position: relative;
  background-color: rgb(var(--v-theme-surface));
  color: rgb(var(--v-theme-on-surface));
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  padding: 1.5rem;

  h2 {
    margin: 0 0 2rem;
  }
}
</style>
