<template>
  <v-table density="compact">
    <thead>
      <tr>
        <th
          v-for="header in headers"
          :key="header.key"
          :class="`font-weight-bold text-no-wrap text-${header.align || 'start'}`"
          :style="{ width: header.width }"
        >
          <span class="font-weight-bold">{{ $t(header.label) }}</span>
          <v-btn v-if="header.sortColumn" class="ml-2" density="compact" icon @click="handleSort(header.sortColumn)">
            <v-icon size="20">{{ getSortIcon(header.sortColumn) }}</v-icon>
          </v-btn>
        </th>
        <th v-if="$slots['actions']" class="font-weight-bold text-center" style="width: 1px">
          {{ $t('actions') }}
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(item, index) in localModel" :key="index">
        <td v-for="header in headers" :key="header.key">
          <div
            class="d-flex align-center"
            :class="{
              'justify-start': header.align === 'start',
              'justify-center': header.align === 'center',
              'justify-end': header.align === 'end',
            }"
          >
            <slot v-if="$slots[`item-${header.key}`]" :name="`item-${header.key}`" :item="item" />
            <template v-else>{{ item[header.key] ?? '' }}</template>
          </div>
        </td>
        <td v-if="$slots['actions']">
          <div class="d-flex justify-end align-center">
            <slot name="actions" :item="item" />
          </div>
        </td>
      </tr>
    </tbody>
  </v-table>
  <g-pagination v-if="pagination" v-model="pagination" class="mt-4" />
</template>

<script setup lang="ts" generic="T extends Record<string, any>">
import { computed } from 'vue';
import { type Pagination, SortDirection } from '@/client';
import GPagination from '@/components/repo/GPagination.vue';
import { type Sorting } from '@/composables/useSortFilter';
import { type TableHeader } from '@/types/table';

const emit = defineEmits<{
  (e: 'update:modelValue', value: T[]): void;
  (e: 'update:sort', value: Sorting): void;
}>();

const pagination = defineModel<Pagination>('pagination');
const sort = defineModel<Sorting>('sort', {
  default: () => ({ column: '', direction: SortDirection.UNKNOWN }),
});

const props = withDefaults(
  defineProps<{
    modelValue: T[];
    headers: TableHeader[];
    pagination?: Pagination;
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

function handleSort(column: string | number) {
  sort.value = { column: String(column), direction: sort.value.direction };
}

function getSortIcon(column: number | string): string {
  const colStr = String(column);
  if (sort.value.column !== colStr || sort.value.direction === SortDirection.UNKNOWN) {
    return 'mdi-swap-vertical';
  }
  return sort.value.direction === SortDirection.ASC ? 'mdi-arrow-up-thin' : 'mdi-arrow-down-thin';
}
</script>
