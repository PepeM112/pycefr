<template>
  <div class="content">
    <header>
      <h1>{{ repoTitle }}</h1>
    </header>
    <div class="charts"></div>
    <div class="container">
      <h2>Propiedades</h2>
      <div class="d-flex">
        <file-tree :model-value="fileTreeData" v-model:selected="selectedTreeNodeIds" @update:selected="onUpdateSelected" />
        <v-divider class="mx-8" vertical thickness="2px" color="primary" opacity="100" />
        <v-card class="pa-4 w-100">
          <div class="d-flex align-center ga-4 mb-4">
            <v-text-field
              v-model="search"
              class="bg-white"
              density="compact"
              variant="outlined"
              placeholder="Search..."
              :append-inner-icon="'mdi-magnify'"
              hide-details
              max-width="240"
            />
            <div class="d-flex ga-2">
              <v-btn
                v-for="level in LEVELS"
                class="level-bubble"
                :class="{ selected: selectedLevels.includes(level.value as Level) }"
                :style="{ backgroundColor: getLevelColor(level.value as Level) }"
                size="small"
                density="comfortable"
                rounded="circle"
                @click="toggleLevel(level.value as Level)"
              >
                {{ level.label }}
              </v-btn>
            </div>
          </div>
          <properties-table v-model="tableData" :levels="selectedLevels" :search="search" />
        </v-card>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import FileTree, { type TreeNode } from '@/components/repo/FileTree.vue';
import PropertiesTable from '@/components/repo/PropertiesTable.vue';
import Enums from '@/utils/enums';
import { getLevelColor, Level, type RepoData, type TableDataItem } from '@/components/repo/utils';
import mockReportData from '@/utils/mocked-results/pycefr.json';

const LEVELS = Enums.buildList(Level);

const isLoading = ref<boolean>(false);
const repoTitle = ref<string>('');
const search = ref<string>('');
const repoData = ref<RepoData>({});
const selectedTreeNodeIds = ref<number[]>([]);
const fileTreeData = ref<TreeNode[]>([]);
const selectedLevels = ref<Level[]>(LEVELS.map(level => Level[level.value]));

const ID_PATH_MAP: Record<number, string> = {};

const tableData = computed<TableDataItem[]>(() => {
  const elements = repoData.value.elements;
  if (!elements || Object.keys(elements).length === 0) return [];

  return Object.entries(elements)
    .filter(([key, _value]) => isFileSelected(key))
    .flatMap(([_, items]) => items)
    .reduce((acc: TableDataItem[], item: TableDataItem) => {
      const classAlreadyAdded = acc.find(i => i.class === item.class);
      classAlreadyAdded ? (classAlreadyAdded.instances += item.instances) : acc.push({ ...item });
      return acc;
    }, [])
    .filter(item => selectedLevels.value.includes(item.level));
});

function isFileSelected(filePath: string): boolean {
  const elements = repoData.value.elements;
  if (!elements || Object.keys(elements).length === 0) return false;

  return selectedTreeNodeIds.value.some(id => ID_PATH_MAP[id] === filePath);
}

function toggleLevel(level: Level) {
  if (selectedLevels.value.includes(level)) {
    selectedLevels.value = selectedLevels.value.filter(l => l !== level);
  } else {
    selectedLevels.value.push(level);
  }
}

function buildRepoDataTree(data: RepoData): TreeNode[] {
  if (!data?.elements) return [];
  const paths = Object.keys(data.elements);

  const treeSkeleton: Record<string, any> = {};

  paths.forEach(path => {
    const parts = path.split('/');
    let current: Record<string, any> = treeSkeleton;
    parts.forEach(part => {
      if (!current[part]) {
        current[part] = {};
      }
      current = current[part];
    });
  });

  let id = 1;

  function fillTree(parentNode: Record<string, any>, currentPath: string = ''): TreeNode[] {
    return Object.keys(parentNode).map(key => {
      const child: Record<string, any> = parentNode[key];
      const fullPath = currentPath ? `${currentPath}/${key}` : key;

      const node: TreeNode = {
        id: id++,
        title: key,
        children: Object.keys(child).length > 0 ? fillTree(child, fullPath) : undefined,
      };

      if (!node.children || node.children.length === 0) {
        ID_PATH_MAP[node.id] = fullPath;
      }

      selectedTreeNodeIds.value.push(node.id);

      return node;
    });
  }

  const tree = fillTree(treeSkeleton);

  return tree;
}

function onUpdateSelected(value: number[] | 'all') {
  if (value === 'all') {
    selectedTreeNodeIds.value = Object.keys(ID_PATH_MAP).map(id => parseInt(id));
  } else {
    selectedTreeNodeIds.value = value;
  }
}

async function fetch() {
  // get Repo data
  try {
    isLoading.value = true;
    await new Promise(resolve => setTimeout(resolve, 500));
    const response = mockReportData as RepoData;

    repoData.value = response;
    repoTitle.value = repoData.value.repoInfo.data.name;
  } catch (error) {
    console.error('Error fetching repo data:', error);
  } finally {
    isLoading.value = false;
  }
}

onMounted(async () => {
  await fetch();
  fileTreeData.value = buildRepoDataTree(repoData.value);
});
</script>
<style lang="scss" scoped>
.level-bubble {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.875rem;
  width: 2.25em;
  height: 2.25em !important;
  min-width: unset;
  color: white;
  
  &:focus {
    outline: 2px solid var(--primary-color);
  }

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
