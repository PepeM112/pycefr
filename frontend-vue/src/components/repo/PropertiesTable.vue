<template>
  <v-table class="properties-table" density="comfortable">
    <thead>
      <tr>
        <th
          v-for="header in headers"
          :key="header.value"
          :class="{ sortable: header.sort, 'text-center': header.value !== 'class' }"
          style="white-space: nowrap"
        >
          <span>{{ header.text }}</span>
          <v-btn v-if="header.sort" class="ml-2" density="compact" icon @click="sortColumn(header.value)">
            <v-icon size="20">{{ getSortIcon(header.value) }}</v-icon>
          </v-btn>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(item, index) in tableData" :key="index">
        <td>{{ item.class }}</td>
        <td>
          <span class="level-bubble" :style="[{ backgroundColor: getLevelColor(item.level) }]">
            {{ item.level }}
          </span>
        </td>
        <td class="text-center">{{ item.instances }}</td>
      </tr>
    </tbody>
  </v-table>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import {
  type Header,
  getLevelColor,
  Level,
  type Sorting,
  SortDirection,
  type TableDataItem,
} from '@/components/repo/utils';

defineProps<{
  modelValue: TableDataItem[];
  levels: Level[];
  search?: string;
}>();

const sortingColumn = ref<Sorting>({ value: '', direction: SortDirection.UNKNOWN });
const tableData = defineModel<TableDataItem[]>('modelValue');

const headers: Header[] = [
  { text: 'Clase', value: 'class', sort: true },
  { text: 'Nivel', value: 'level', sort: true },
  { text: 'Instancias', value: 'numberOfInstances', sort: true },
];

function getSortIcon(column: string): string {
  if (sortingColumn.value.value !== column) return 'mdi-swap-vertical';
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
  if (sortingColumn.value.value === column) {
    sortingColumn.value.direction = (sortingColumn.value.direction + 1) % 3;
  } else {
    sortingColumn.value = { value: column, direction: SortDirection.ASC };
  }
}
</script>
<style lang="scss" scoped>
.properties-table {
  .full-width-table {
    width: 100%;
    table-layout: fixed;
  }
}

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
  width: 2rem;
  height: 2rem;
  min-width: unset;
  border-radius: 50%;
  font-size: 0.875rem;
  margin: auto;
}
</style>
