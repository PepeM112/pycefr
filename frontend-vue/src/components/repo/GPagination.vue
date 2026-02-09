<template>
  <div class="d-flex align-center justify-end" style="font-size: 0.875rem">
    <span>{{ $t('show') }}</span>
    <v-select
      class="items-per-page-select"
      v-model="localModel.perPage"
      :items="ITEMS_PER_PAGE_OPTIONS"
      density="compact"
      size="small"
      variant="outlined"
      hide-details
    />
    <span>{{ $t('of_total', { total: localModel?.total }) }}</span>
    <v-pagination
      v-model="localModel.page"
      :length="totalPages"
      :total-visible="3"
      density="compact"
      style="transform: scale(0.85) translate(0, 0)"
    />
  </div>
</template>
<script setup lang="ts">
import { computed, watch } from 'vue';
import type { Pagination } from '@/client';

const ITEMS_PER_PAGE_OPTIONS = [5, 10, 25, 50, 100];

const emit = defineEmits<{
  (e: 'update:modelValue', value: Pagination): void;
}>();

const props = defineProps<{
  modelValue: Pagination;
}>();

const localModel = computed<Pagination>({
  get() {
    return props.modelValue;
  },
  set(value: Pagination) {
    emit('update:modelValue', value);
  },
});

const totalPages = computed<number>(() => {
  return Math.ceil(localModel.value.total / localModel.value.perPage);
});

watch(
  () => localModel.value.perPage,
  () => {
    if (localModel.value.page > totalPages.value) {
      localModel.value = { ...localModel.value, page: totalPages.value || 1 };
    }
  }
);
</script>
<style scoped>
.items-per-page-select {
  margin: 0 -8px;
  max-width: fit-content;
  transform: scale(0.65) translate(0, 0);
}
</style>
