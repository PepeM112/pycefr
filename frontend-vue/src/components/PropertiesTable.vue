<template>
  <p>Selected file: {{ selectedFile }}</p>
  <v-table density="comfortable" class="properties-table">
    <thead>
      <tr>
        <th
          v-for="header in headers"
          :key="header.value"
          :class="{ sortable: header.sort, 'text-center': header.value !== 'class' }"
        >
          <span>{{ header.text }}</span>
          <v-btn v-if="header.sort" class="ml-2" density="compact" icon @click="sortColumn(header.value)">
            <v-icon size="20">{{ getSortIcon(header.value) }}</v-icon>
          </v-btn>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(item, index) in displayedTableData" :key="index">
        <td>{{ item.class }}</td>
        <td>
          <span class="level-bubble" :style="[{ backgroundColor: getLevelColor(item) }]">
            {{ item.level }}
          </span>
        </td>
        <td class="text-center">{{ item.numberOfInstances }}</td>
      </tr>
    </tbody>
  </v-table>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue';

const props = defineProps<{
  modelValue: any[];
  levels: { label: string; color: string }[];
  search?: string;
  selectedFile?: string;
}>();

enum SortDirection {
  UNKNOWN = 0,
  ASC = 1,
  DESC = 2,
}

interface Header {
  text: string;
  value: string;
  sort?: boolean | ((a: any, b: any) => number);
}

interface Sorting {
  value: string;
  direction: SortDirection;
}

const sortingColumn = ref<Sorting>({ value: '', direction: SortDirection.UNKNOWN });
const tableData = ref<any[]>(props.modelValue || []);

const headers: Header[] = [
  { text: 'Clase', value: 'class', sort: true },
  { text: 'Nivel', value: 'level', sort: true },
  { text: 'Instancias', value: 'numberOfInstances', sort: true },
];

const displayedTableData = computed<any[]>(() => {
  return [...tableData.value]
    .filter(item => {
      const matchesLevel = props.levels.some(level => level.label === item.level);
      const matchesSearch = !props.search || item.class.toLowerCase().includes(props.search.toLowerCase());
      return matchesLevel && matchesSearch;
    })
    .sort((a, b) => {
      if (sortingColumn.value.value && sortingColumn.value.direction !== SortDirection.UNKNOWN) {
        const aValue = a[sortingColumn.value.value];
        const bValue = b[sortingColumn.value.value];

        if (aValue < bValue) return sortingColumn.value.direction === SortDirection.ASC ? -1 : 1;
        if (aValue > bValue) return sortingColumn.value.direction === SortDirection.ASC ? 1 : -1;
      }
      return 0;
    });
});

function getLevelColor(item: any): string {
  const level = props.levels.find(level => level.label === item.level);
  return level ? level.color : 'transparent';
}

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
