<template>
  <v-container fluid class="pa-6 fill-height align-start d-block">
    <slot name="header">
      <header>
        <div class="d-flex align-center">
          <v-btn v-if="props.back" icon="mdi-arrow-left" variant="text" density="comfortable" @click="navigateBack()" />
          <h1 v-if="props.header">{{ props.header }}</h1>
          <v-spacer />
          <slot name="actions" />
        </div>
      </header>
    </slot>
    <slot></slot>
  </v-container>
</template>
<script setup lang="ts">
import { type RouteLocationRaw, useRouter } from 'vue-router';

const router = useRouter();

const props = defineProps<{
  header?: string;
  back?: RouteLocationRaw;
}>();

function navigateBack() {
  if (props.back) {
    router.push(props.back);
  }
}
</script>
<style scoped lang="scss">
header {
  margin-bottom: 2rem;
  background-color: rgb(var(--v-theme-primary));
  color: rgb(var(--v-theme-on-primary));
  border-radius: var(--border-radius);
  padding: 0.75rem;
  margin-bottom: 1rem;

  h1 {
    font-size: 1.5rem;
    margin-left: 0.75rem;
  }
}
</style>
