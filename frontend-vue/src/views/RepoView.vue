<template>
  <div class="content">
    <header>
      <h1>{{ repoTitle }}</h1>
    </header>
    <div class="charts"></div>
    <div class="container">
      <h2>Propiedades</h2>
      <div class="d-flex">
        <file-tree :paths="treePaths" @select-element="(value: string) => (selectedElementInFileTree = value)" />
        <v-divider class="mx-8" vertical thickness="2px" color="primary" opacity="100" />
        <div class="d-flex flex-column w-100">
          <div class="filters-wrapper mb-4">
            <v-text-field
              v-model="search"
              class="search-field mb-4"
              density="compact"
              variant="outlined"
              placeholder="Search..."
              :append-inner-icon="'mdi-magnify'"
              hide-details
              width="180px"
              height="32px"
              border="md"
            />
            <div class="d-flex ga-2">
              <v-btn
                v-for="level in levels"
                class="level-bubble"
                :class="{ selected: selectedLevels.includes(level.label) }"
                :style="{ backgroundColor: level.color }"
                size="small"
                density="comfortable"
                rounded="circle"
                @click="toggleLevel(level.label)"
              >
                {{ level.label }}
              </v-btn>
            </div>
          </div>
          <properties-table
            v-if="tableData.length > 0"
            v-model="tableData"
            :levels="filteredLevels"
            :search="search"
            :selected-file="selectedElementInFileTree"
          />
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import FileTree from '@/components/FileTree.vue';
import PropertiesTable from '@/components/PropertiesTable.vue';

const route = useRoute();
const repoTitle = ref<string>('');
const selectedLevels = ref<string[]>([]);
const tableData = ref<any[]>([]);
const search = ref<string>('');
const selectedElementInFileTree = ref<string>('');

const treePaths = ref([
  'pycerfl.py',
  'backend/scripts/levels.py',
  'backend/scripts/analyzer.py',
  'backend/scripts/console.py',
  'backend/scripts/iter_tree.py',
]);

const levels = [
  { label: 'A1', color: 'rgba(255, 99, 132, 1)' },
  { label: 'A2', color: 'rgba(255, 159, 64, 1)' },
  { label: 'B1', color: 'rgba(255, 206, 86, 1)' },
  { label: 'B2', color: 'rgba(75, 192, 192, 1)' },
  { label: 'C1', color: 'rgba(54, 162, 235, 1)' },
  { label: 'C2', color: 'rgba(153, 102, 255, 1)' },
];

const filteredLevels = computed(() => {
  return levels.filter(level => selectedLevels.value.includes(level.label));
});

function toggleLevel(level: string) {
  if (selectedLevels.value.includes(level)) {
    selectedLevels.value = selectedLevels.value.filter(l => l !== level);
  } else {
    selectedLevels.value.push(level);
  }
}

onMounted(() => {
  repoTitle.value = route.params.repoName.toString();
  selectedLevels.value = levels.map(level => level.label);
  tableData.value = [
    {
      class: 'Simple List',
      level: 'A1',
      numberOfInstances: 39,
    },
    {
      class: 'Print',
      level: 'A1',
      numberOfInstances: 67,
    },
    {
      class: 'Simple Attribute',
      level: 'A2',
      numberOfInstances: 733,
    },
    {
      class: 'Simple Assignment',
      level: 'A1',
      numberOfInstances: 339,
    },
    {
      class: 'Import',
      level: 'A2',
      numberOfInstances: 18,
    },
    {
      class: 'From',
      level: 'A2',
      numberOfInstances: 12,
    },
    {
      class: "If statements using → __name__ == '__main__'",
      level: 'B2',
      numberOfInstances: 2,
    },
    {
      class: 'Simple If statements',
      level: 'A1',
      numberOfInstances: 186,
    },
    {
      class: 'Simple For Loop',
      level: 'A1',
      numberOfInstances: 34,
    },
    {
      class: 'Exception → try/except',
      level: 'B1',
      numberOfInstances: 12,
    },
    {
      class: 'Function',
      level: 'A1',
      numberOfInstances: 9,
    },
    {
      class: 'Simple Tuple',
      level: 'A1',
      numberOfInstances: 11,
    },
    {
      class: "'range' call function",
      level: 'A2',
      numberOfInstances: 4,
    },
    {
      class: "Files → 'open' call function",
      level: 'A2',
      numberOfInstances: 9,
    },
    {
      class: 'Generator Expression',
      level: 'C1',
      numberOfInstances: 8,
    },
    {
      class: 'Assignment with sum (total = total + 1)',
      level: 'A1',
      numberOfInstances: 8,
    },
    {
      class: 'Simplified incremental Assignment with increase amount',
      level: 'A2',
      numberOfInstances: 46,
    },
    {
      class: "'raise' exception",
      level: 'B1',
      numberOfInstances: 2,
    },
    {
      class: "'pass' statement",
      level: 'B1',
      numberOfInstances: 6,
    },
    {
      class: '1 Nested For Loop',
      level: 'A2',
      numberOfInstances: 6,
    },
    {
      class: 'With',
      level: 'B1',
      numberOfInstances: 10,
    },
    {
      class: 'Function with Simple argument',
      level: 'A1',
      numberOfInstances: 72,
    },
    {
      class: 'Return',
      level: 'A1',
      numberOfInstances: 31,
    },
    {
      class: 'Simple Dictionary',
      level: 'A2',
      numberOfInstances: 23,
    },
    {
      class: '1 List Dictionary',
      level: 'B1',
      numberOfInstances: 2,
    },
    {
      class: '1 Nested Dictionary',
      level: 'B1',
      numberOfInstances: 3,
    },
    {
      class: "'enumerate' call function",
      level: 'C2',
      numberOfInstances: 1,
    },
    {
      class: "Files → 'read' call function",
      level: 'A2',
      numberOfInstances: 2,
    },
    {
      class: 'Simple List Comprehension',
      level: 'C1',
      numberOfInstances: 4,
    },
    {
      class: 'List Comprehension with 1 If statements',
      level: 'C1',
      numberOfInstances: 2,
    },
    {
      class: 'For Loop with Tuple as name',
      level: 'A2',
      numberOfInstances: 6,
    },
    {
      class: 'While with Else Loop',
      level: 'B1',
      numberOfInstances: 3,
    },
    {
      class: "'break' statement",
      level: 'B1',
      numberOfInstances: 3,
    },
    {
      class: "'continue' statement",
      level: 'B1',
      numberOfInstances: 3,
    },
    {
      class: 'Recursive Functions',
      level: 'B2',
      numberOfInstances: 1,
    },
    {
      class: 'Function with Simple argument with Default argument',
      level: 'A2',
      numberOfInstances: 1,
    },
    {
      class: 'Lambda',
      level: 'B1',
      numberOfInstances: 2,
    },
    {
      class: '2 Nested Tuple',
      level: 'A2',
      numberOfInstances: 2,
    },
    {
      class: "Import with 'as' extension",
      level: 'B1',
      numberOfInstances: 1,
    },
    {
      class: 'Simple Class using the constructor method → __init__',
      level: 'B1',
      numberOfInstances: 1,
    },
  ];
});
</script>
<style lang="scss" scoped>
.level-bubble {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.875rem;
  width: 2rem;
  height: 2rem !important;
  min-width: unset;
  color: white;

  &:not(.selected) {
    background-color: rgb(155, 156, 164);
    color: var(--primary-color);
    opacity: 0.35;
    transition: all 0.3s ease;

    &:hover {
      opacity: 0.65;
      color: white;
    }
  }
}
</style>
<style lang="scss">
.filters-wrapper {
  display: flex;
  gap: 1rem;
}
.search-field {
  max-width: 240px;

  .v-input__control .v-field {
    border-radius: var(--border-radius);

    &.v-field--appended {
      padding-right: 0.25rem;
    }

    input {
      height: 32px !important;
      min-height: 0 !important;
      font-size: 0.875em;
      padding: 0 0.5rem;
    }
  }
}
</style>
