<template>
  <div v-if="props.modelValue === LoadingStatus.LOADING" class="d-flex justify-center pa-6">
    <v-progress-linear indeterminate />
  </div>
  <div v-else-if="props.modelValue === LoadingStatus.ERROR" class="d-flex justify-center pa-6">
    <v-icon color="error" size="48">mdi-alert-circle</v-icon>
  </div>
  <div v-else-if="props.modelValue === LoadingStatus.EMPTY" class="d-flex justify-center pa-6">
    <div class="d-flex justify-center align-center flex-column" style="color: #9d9d9d; margin: 2rem auto">
      <v-icon class="mb-1" size="60">mdi-alert-circle</v-icon>
      <p class="text-grey ml-2">{{ $t('no_data') }}</p>
    </div>
  </div>
  <div v-else-if="props.modelValue === LoadingStatus.IDLE">
    <slot />
  </div>
</template>
<script setup lang="ts">
import { LoadingStatus } from '@/types/loading';

const props = defineProps<{
  modelValue?: LoadingStatus;
}>();
</script>
