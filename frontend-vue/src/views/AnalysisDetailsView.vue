<template>
  <page-view :header="analysisData?.repo?.name || $t('analysis')" :back="{ name: RouteNames.ANALYSIS_LIST }">
    <template #actions>
      <three-dots-menu :model-value="MENU_ITEMS" />
    </template>
    <generic-loader :model-value="loaderStatus">
      <g-container class="mb-8" title="insights" expandable>
        <analysis-charts v-if="chartData && loaderStatus === LoadingStatus.IDLE" :data="chartData" :items="tableData" />
      </g-container>
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
                  :key="`level-${level.value}`"
                  class="level-bubble-btn"
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
            <g-table :model-value="tableData" :headers="headers" :pagination="pagination" v-model:sort="sort">
              <template #item-classId="{ item }">
                {{ $t(`${Enums.getLabel(ClassId, item.classId).toLowerCase()}`) }}
              </template>
              <template #item-level="{ item }">
                <span class="level-bubble" :style="[{ backgroundColor: getLevelColor(item.level as Level) }]">
                  {{ $t(Enums.getLabel(Level, item.level)) }}
                </span>
              </template>
            </g-table>
          </v-card>
        </div>
      </g-container>
    </generic-loader>
  </page-view>
</template>
<script setup lang="ts">
import { ClassId, getAnalysisDetail, Level, SortDirection, type AnalysisPublic, type Pagination } from '@/client';
import AnalysisCharts from '@/components/analysis/AnalysisCharts.vue';
import GContainer from '@/components/GContainer.vue';
import GenericLoader from '@/components/GenericLoader.vue';
import GTable from '@/components/GTable.vue';
import PageView from '@/components/PageView.vue';
import FileTree from '@/components/repo/FileTree.vue';
import { getLevelColor } from '@/utils/utils';
import type { AnalysisClassPublicWithLevel, ChartCommitItem, ChartData, ChartFileItem } from '@/types/analysis';
import ThreeDotsMenu, { type MenuProps } from '@/components/ThreeDotsMenu.vue';
import { useClassLabel } from '@/composables/useClassLabel';
import { useSorting } from '@/composables/useSorting';
import { RouteNames } from '@/router/route-names';
import { LoadingStatus } from '@/types/loading';
import { type TableHeader } from '@/types/table';
import type { TreeNode } from '@/types/treeview';
import Enums from '@/utils/enums';
import { getExtensionIcon, type FileExtension } from '@/utils/utils';
import { computed, onMounted, ref, shallowRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';

const { t } = useI18n();
const route = useRoute();
const sort = useSorting();
const classLabel = useClassLabel();

const LEVELS = Enums.buildList(Level);

const analysisId = Number(route.params.id);
const loaderStatus = ref<LoadingStatus>(LoadingStatus.IDLE);
const analysisTitle = ref<string>('');
const search = ref<string>('');
const analysisData = shallowRef<AnalysisPublic | undefined>(undefined);
const pagination = ref<Pagination>({ page: 1, perPage: 10, total: 0 });
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

const chartData = computed<ChartData | null>(() => {
  if (!analysisData.value) return null;

  const selectedPathsSet = new Set<string>();
  selectedTreeNodeIds.value.forEach(id => {
    const path = ID_PATH_MAP[id];
    if (path) selectedPathsSet.add(path);
  });

  const hasSelection = selectedPathsSet.size > 0;

  const files: ChartFileItem[] = (analysisData.value.fileClasses || [])
    .filter(f => (hasSelection ? selectedPathsSet.has(f.filename) : true))
    .map(f => ({
      name: f.filename.split('/').pop() || f.filename,
      fullPath: f.filename,
      instances: f.classes?.reduce((acc, c) => acc + c.instances, 0) || 0,
    }))
    .sort((a, b) => b.instances - a.instances)
    .slice(0, 10);

  const commits: ChartCommitItem[] = (analysisData.value.repo?.commits || []).map(c => ({
    hash: c.githubUser || c.username || 'unknown',
    filesCount: c.totalFilesModified,
    complexity: c.loc,
  }));

  return {
    items: tableData.value,
    files,
    commits,
  };
});

const tableData = computed<AnalysisClassPublicWithLevel[]>(() => {
  const elements = analysisData.value?.fileClasses ?? [];
  if (elements.length === 0) return [];

  const groupingMap = new Map<number, AnalysisClassPublicWithLevel & { translatedLabel?: string }>();

  for (const file of elements) {
    if (!isFileSelected(file.filename)) continue;

    for (const item of file.classes ?? []) {
      const existing = groupingMap.get(item.classId);
      if (existing) {
        existing.instances += item.instances;
      } else {
        groupingMap.set(item.classId, {
          classId: item.classId,
          instances: item.instances,
          level: classLabel.getClassLevel(item.classId),
        });
      }
    }
  }

  const searchLower = search.value.toLowerCase();

  const processedElements = Array.from(groupingMap.values()).filter(item => {
    if (!selectedLevels.value?.includes(item.level)) return false;

    item.translatedLabel = t(Enums.getLabel(ClassId, item.classId)).toString();

    if (!searchLower) return true;
    return item.translatedLabel.toLowerCase().includes(searchLower);
  });

  processedElements.sort((a, b) => {
    if (sort.value.direction === SortDirection.UNKNOWN || !sort.value.column) return 0;

    let comparison = 0;
    if (sort.value.column === 'classId') {
      comparison = a.translatedLabel!.localeCompare(b.translatedLabel!);
    } else {
      const col = sort.value.column as keyof AnalysisClassPublicWithLevel;
      const valA = a[col] ?? 0;
      const valB = b[col] ?? 0;
      comparison = valA < valB ? -1 : valA > valB ? 1 : 0;
    }

    return sort.value.direction === SortDirection.ASC ? comparison : -comparison;
  });

  pagination.value.total = processedElements.length;
  return processedElements;
});

const headers: TableHeader[] = [
  { label: 'class', key: 'classId', sortColumn: 'classId' },
  { label: 'level', key: 'level', sortColumn: 'level', width: '1px', align: 'center' },
  { label: 'instances', key: 'instances', sortColumn: 'instances', width: '1px', align: 'center' },
];

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
      const hasChildren = Object.keys(child).length > 0;

      let icon = 'mdi-file-outline';
      if (!hasChildren) {
        const parts = key.split('.');
        const extension = (parts.length > 1 ? parts.pop()?.toLowerCase() : '') as FileExtension;
        icon = getExtensionIcon(extension) || 'mdi-file-outline';
      }

      const node: TreeNode = {
        id: id++,
        title: key,
        children: hasChildren ? fillTree(child, fullPath) : undefined,
        icon: hasChildren ? undefined : icon,
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
    console.error('error.fetching.analysis_data:', error);
    return;
  }
  analysisData.value = data;
  analysisTitle.value = analysisData.value?.repo?.name || '';
  loaderStatus.value = LoadingStatus.IDLE;
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
.level-bubble-btn {
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

td .level-bubble {
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  font-size: 0.75rem;
  width: 2.25em;
  height: 2.25em;
  min-width: unset;
  border-radius: 50%;
}
</style>
