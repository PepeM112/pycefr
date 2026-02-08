<template>
  <page-view :header="repoTitle" :back="{ name: 'home' }">
    <template #actions>
      <three-dots-menu :model-value="MENU_ITEMS" />
    </template>
    <div class="charts"></div>
    <generic-loader :model-value="loaderStatus">
      <g-container title="properties">
        <div class="d-flex">
          <file-tree
            :model-value="fileTreeData"
            v-model:selected="selectedTreeNodeIds"
            @update:selected="onUpdateSelected"
          />
          <v-divider class="mx-8" vertical thickness="2px" color="secondary" opacity="100" />
          <v-card class="pa-4 w-100">
            <div class="d-flex align-center ga-4 mb-4">
              <v-text-field
                v-model="search"
                class="bg-background rounded-lg"
                density="compact"
                variant="outlined"
                placeholder="Search..."
                :append-inner-icon="'mdi-magnify'"
                hide-details
                max-width="240"
                min-width="240"
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
      </g-container>
    </generic-loader>
  </page-view>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import FileTree, { type TreeNode } from '@/components/repo/FileTree.vue';
import PropertiesTable from '@/components/repo/PropertiesTable.vue';
import Enums from '@/utils/enums';
import { getLevelColor, type TableDataItem } from '@/components/repo/utils';
import { type AnalysisPublic, type AnalysisClassPublic, type AnalysisFilePublic, ClassId, Level } from '@/client';
import { getAnalysisDetail } from '@/client';
import { useRoute } from 'vue-router';
import { useClassLabel } from '@/composables/useClassLabel';
import PageView from '@/components/PageView.vue';
import ThreeDotsMenu, { type MenuProps } from '@/components/ThreeDotsMenu.vue';
import GenericLoader from '@/components/GenericLoader.vue';
import { LoadingStatus } from '@/types/loading';
import { useI18n } from 'vue-i18n';
import GContainer from '@/components/GContainer.vue';

const { t } = useI18n();
const classLabel = useClassLabel();

const LEVELS = Enums.buildList(Level);

const route = useRoute();
const analysisId = Number(route.params.id);
const loaderStatus = ref<LoadingStatus>(LoadingStatus.IDLE);
const repoTitle = ref<string>('');
const search = ref<string>('');
const analysisData = ref<AnalysisPublic | undefined>(undefined);
const selectedTreeNodeIds = ref<number[]>([]);
const fileTreeData = ref<TreeNode[]>([]);
const selectedLevels = ref<Level[]>(LEVELS.map(level => level.value as Level));

const ID_PATH_MAP: Record<number, string> = {};

const MENU_ITEMS: MenuProps[] = [
  {
    label: 'refresh_data',
    icon: 'mdi-refresh',
    onClick: async () => {
      await loadData();
    },
  },
];

const tableData = computed<TableDataItem[]>(() => {
  const elements: AnalysisFilePublic[] = analysisData.value?.fileClasses ?? [];
  if (!elements || elements.length === 0) return [];

  return elements
    .filter(it => isFileSelected(it.filename))
    .flatMap(it => it.classes ?? [])
    .reduce((acc: TableDataItem[], item: AnalysisClassPublic) => {
      const classAlreadyAdded = acc.find(i => i.class === item.classId);
      if (classAlreadyAdded) {
        classAlreadyAdded.instances = (classAlreadyAdded.instances ?? 0) + item.instances;
      } else {
        acc.push({
          class: item.classId,
          instances: item.instances,
          level: classLabel.getClassLevel(item.classId),
        });
      }
      return acc;
    }, [])
    .filter(item => {
      if (!selectedLevels.value?.includes(item.level)) return false;

      if (!search.value) return true;
      const className = t(Enums.getLabel(ClassId, item.class)).toString().toLowerCase();
      return className.includes(search.value.toLowerCase());
    });
});

function isFileSelected(filePath: string): boolean {
  const elements = analysisData.value?.fileClasses;
  if (!elements || elements.length === 0) return false;

  return selectedTreeNodeIds.value.some(id => ID_PATH_MAP[id] === filePath);
}

function toggleLevel(level: Level) {
  if (selectedLevels.value.includes(level)) {
    selectedLevels.value = selectedLevels.value.filter(l => l !== level);
  } else {
    selectedLevels.value.push(level);
  }
}

function buildRepoDataTree(data: AnalysisPublic | undefined): TreeNode[] {
  if (!data?.fileClasses) return [];
  const paths = data.fileClasses.map(fc => fc.filename);

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
    if (currentPath === '') clearIDPathMap();

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

async function loadData() {
  loaderStatus.value = LoadingStatus.LOADING;
  const { data, error } = await getAnalysisDetail({ path: { analysis_id: analysisId ?? 0 } });
  if (error) {
    loaderStatus.value = LoadingStatus.ERROR;
    console.error('Error fetching repo data:', error);
    return;
  }
  analysisData.value = data;
  repoTitle.value = analysisData.value?.repo?.name || '';
  loaderStatus.value = LoadingStatus.SUCCESS;
}

function clearIDPathMap() {
  Object.keys(ID_PATH_MAP).forEach(key => delete ID_PATH_MAP[Number(key)]);
}

onMounted(async () => {
  classLabel.fetch();
  await loadData();
  fileTreeData.value = buildRepoDataTree(analysisData.value);
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
