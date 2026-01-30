<template>
  <div class="d-flex align-center justify-end" style="font-size: 0.875rem">
    <span>Mostrar</span>
    <v-select
      class="items-per-page-select"
      v-model="localModel.itemsPerPage"
      :items="[5, 10, 25, 50, 100]"
      density="compact"
      size="small"
      variant="outlined"
      hide-details
    />
    <span>de {{ localModel?.total }}</span>
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

const ITEMS_PER_PAGE_OPTIONS = [5, 10, 25, 50, 100];

export interface PaginationItem {
  page: number;
  itemsPerPage: (typeof ITEMS_PER_PAGE_OPTIONS)[number];
  total: number;
}
const emit = defineEmits<{
  (e: 'update:modelValue', value: PaginationItem): void;
}>();

const props = defineProps<{
  modelValue: PaginationItem;
}>();

const localModel = computed<PaginationItem>({
  get() {
    return props.modelValue;
  },
  set(value: PaginationItem) {
    emit('update:modelValue', value);
  },
});

const totalPages = computed<number>(() => Math.ceil(localModel.value.total / localModel.value.itemsPerPage));

watch(
  () => localModel.value.itemsPerPage,
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
