<template>
  <div class="d-flex align-center justify-end" style="font-size: 0.875rem">
    <span>{{ $t('show') }}</span>
    <v-select
      class="items-per-page-select"
      :model-value="modelValue.perPage"
      :items="ITEMS_PER_PAGE_OPTIONS"
      density="compact"
      size="small"
      variant="outlined"
      hide-details
      @update:model-value="onPerPageChange"
    />
    <span>{{ $t('of_total', { total: modelValue.total }) }}</span>
    <v-pagination
      :model-value="modelValue.page"
      :length="totalPages"
      :total-visible="3"
      density="compact"
      style="transform: scale(0.85) translate(0, 0)"
      @update:model-value="onPageChange"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Pagination } from '@/client';

const ITEMS_PER_PAGE_OPTIONS = [5, 10, 25, 50, 100];

const emit = defineEmits<{
  (e: 'update:modelValue', value: Pagination): void;
}>();

const props = defineProps<{
  modelValue: Pagination;
}>();

const totalPages = computed<number>(() => Math.ceil(props.modelValue.total / props.modelValue.perPage));

function onPageChange(page: number) {
  emit('update:modelValue', { ...props.modelValue, page });
}

function onPerPageChange(perPage: number) {
  const newTotalPages = Math.ceil(props.modelValue.total / perPage);
  const page = props.modelValue.page > newTotalPages ? newTotalPages || 1 : props.modelValue.page;
  emit('update:modelValue', { ...props.modelValue, perPage, page });
}
</script>
<style scoped>
.items-per-page-select {
  margin: 0 -8px;
  max-width: fit-content;
  transform: scale(0.65) translate(0, 0);
}
</style>
