<template>
  <div v-if="props.modelValue === LoadingStatus.LOADING" class="d-flex justify-center pa-6">
    <v-progress-circular indeterminate size="48" />
  </div>
  <div v-else-if="props.modelValue === LoadingStatus.ERROR" class="d-flex justify-center pa-6">
    <v-icon color="error" size="48">mdi-alert-circle</v-icon>
  </div>
  <div v-else-if="props.modelValue === LoadingStatus.SUCCESS">
    <slot />
  </div>
</template>
<script setup lang="ts">
import { LoadingStatus } from '@/types/loading';
import { watch } from 'vue';

const props = defineProps<{
  modelValue?: LoadingStatus;
}>();

watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      console.warn('modelValue is undefined: ', newValue);
    }
  },
  { immediate: true }
);
</script>
