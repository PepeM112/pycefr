<template>
  <v-table density="compact">
    <thead>
      <tr>
        <th v-for="header in headers" :key="header.key" class="font-weight-bold" :style="{ width: header.width }">
          <span class="font-weight-bold">{{ $t(header.label) }}</span>
          <v-btn v-if="header.sortColumn" class="ml-2" density="compact" icon @click="sortColumn(header.key)">
            <v-icon size="20">{{ getSortIcon(header.key) }}</v-icon>
          </v-btn>
        </th>
        <th v-if="$slots['actions']" class="font-weight-bold" style="width: 1px">{{ $t('actions') }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(item, index) in localModel" :key="index">
        <td v-for="header in headers" :key="header.key">
          <slot v-if="$slots[`item-${header.key}`]" :name="`item-${header.key}`" :item="item" />
          <template v-else>{{ item[header.key] ?? '' }}</template>
        </td>
        <td v-if="$slots['actions']">
          <div class="d-flex justify-end">
            <slot name="actions" :item="item" />
          </div>
        </td>
      </tr>
    </tbody>
  </v-table>
  <g-pagination v-if="pagination" v-model="pagination" class="mt-4" />
</template>
<script setup lang="ts" generic="T extends Record<string, unknown>">
import { ref, computed } from 'vue';
import { type Pagination, SortDirection } from '@/client';
import GPagination from '@/components/repo/GPagination.vue';
import { type Sorting, type SortFilter } from '@/composables/useSortFilter';

type TableHeader = {
  readonly label: string;
  readonly key: string;
  readonly width?: string;
  readonly sortColumn?: number;
};

const emit = defineEmits<{
  (e: 'update:modelValue', value: T[]): void;
}>();

const sortingColumn = ref<Sorting>({ column: '', direction: SortDirection.UNKNOWN });
const pagination = defineModel<Pagination>('pagination');
const props = withDefaults(
  defineProps<{
    modelValue: T[];
    headers: TableHeader[];
    sortFilter?: SortFilter;
  }>(),
  {
    modelValue: () => [],
    headers: () => [],
  }
);

const localModel = computed<T[]>({
  get() {
    if (!pagination.value) return props.modelValue;
    return props.modelValue.slice(
      (pagination.value.page - 1) * pagination.value.perPage,
      pagination.value.page * pagination.value.perPage
    );
  },
  set(value) {
    emit('update:modelValue', value);
  },
});

function getSortIcon(column: string): string {
  if (sortingColumn.value.column !== column) return 'mdi-swap-vertical';
  switch (sortingColumn.value.direction) {
    case SortDirection.ASC:
      return 'mdi-arrow-up-thin';
    case SortDirection.DESC:
      return 'mdi-arrow-down-thin';
    default:
      return 'mdi-swap-vertical';
  }
}

function sortColumn(column: string) {
  if (sortingColumn.value.column === column) {
    sortingColumn.value.direction = (sortingColumn.value.direction + 1) % 3;
  } else {
    sortingColumn.value = { column: column, direction: SortDirection.ASC };
  }
}
</script>
