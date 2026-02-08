<template>
  <v-table density="compact">
    <thead>
      <tr>
        <th
          v-for="header in headers"
          :key="header.value"
          class="text-primary-on-surface"
          :class="{ sortable: header.sort, 'text-center': header.value !== 'class' }"
          :style="{ whiteSpace: 'nowrap', width: header.width || 'auto' }"
        >
          <span class="font-weight-bold">{{ $t(header.text) }}</span>
          <v-btn v-if="header.sort" class="ml-2" density="compact" icon @click="sortColumn(header.value)">
            <v-icon size="20">{{ getSortIcon(header.value) }}</v-icon>
          </v-btn>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(item, index) in displayedTableData" :key="index">
        <td>{{ $t(Enums.getLabel(ClassId, item.class)) }}</td>
        <td>
          <span class="level-bubble" :style="[{ backgroundColor: getLevelColor(item.level as Level) }]">
            {{ item.level }}
          </span>
        </td>
        <td class="text-center">{{ item.instances }}</td>
      </tr>
    </tbody>
  </v-table>
  <g-pagination class="mt-4" v-model="pagination" />
</template>
<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { Pagination } from '@/client';
import { type Header, getLevelColor, type Sorting, SortDirection, type TableDataItem } from '@/components/repo/utils';
import GPagination from '@/components/repo/GPagination.vue';
import { ClassId, type Level } from '@/client';
import Enums from '@/utils/enums';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

defineProps<{
  modelValue: TableDataItem[];
  levels: Level[];
  search?: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: TableDataItem[]): void;
}>();

const sortingColumn = ref<Sorting>({ column: '', direction: SortDirection.UNKNOWN });
const pagination = ref<Pagination>({ page: 1, perPage: 10, total: 0 });
const localModelValue = defineModel<TableDataItem[]>('modelValue');

const displayedTableData = computed<TableDataItem[]>(() => {
  if (!localModelValue.value) return [];

  return (
    [...localModelValue.value]
      // Sorting
      .sort((a, b) => {
        if (sortingColumn.value.direction === SortDirection.UNKNOWN || !sortingColumn.value.column) return 0;

        let comparison = 0;

        console.log('Sorting by:', sortingColumn.value);

        if (sortingColumn.value.column === 'class') {
          const labelA = t(Enums.getLabel(ClassId, a.class));
          const labelB = t(Enums.getLabel(ClassId, b.class));

          comparison = labelA.localeCompare(labelB);
        } else {
          const column = sortingColumn.value.column as keyof TableDataItem;
          const valA = a[column] ?? 0;
          const valB = b[column] ?? 0;

          if (valA < valB) comparison = -1;
          else if (valA > valB) comparison = 1;
        }

        return sortingColumn.value.direction === SortDirection.ASC ? comparison : -comparison;
      })
      // Pagination
      .slice(
        (pagination.value.page - 1) * pagination.value.perPage,
        pagination.value.page * pagination.value.perPage
      )
  );
});

const headers: Header[] = [
  { text: 'class', value: 'class', sort: true },
  { text: 'level', value: 'level', sort: true, width: '1px' },
  { text: 'instances', value: 'instances', sort: true, width: '1px' },
];

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

watch(
  () => localModelValue.value,
  newValue => {
    if (!newValue) return;
    pagination.value.total = newValue.length;
  }
);
</script>
<style lang="scss" scoped>
thead {
  background-color: var(--primary-color);
  color: white;
}

th,
td {
  width: auto;
  min-width: fit-content;
  max-width: none;
}

.level-bubble {
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  font-size: 0.75rem;
  width: 2.25em;
  height: 2.25em;
  min-width: unset;
  border-radius: 50%;
  margin: auto;
}
</style>
