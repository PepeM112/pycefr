<template>
  <page-view :header="analysisData?.repo?.name || $t('analysis')" :back="{ name: RouteNames.ANALYSIS_LIST }">
    <template #actions>
      <three-dots-menu :model-value="MENU_ITEMS" />
    </template>
    <generic-loader :model-value="loaderStatus">
      <g-container class="mb-8" title="insights" is-expandable>
        <analysis-charts v-if="chartData && loaderStatus === LoadingStatus.IDLE" :data="chartData" :items="tableData" />
      </g-container>
      <g-container v-if="analysisData?.repo" class="mb-8" title="repository" is-expandable>
        <repo-section :repo="analysisData.repo" />
      </g-container>
      <g-container title="properties">
        <div class="d-flex">
          <file-tree
            v-model:selected="selectedTreeNodeIds"
            :model-value="fileTreeData"
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
                append-inner-icon="mdi-magnify"
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
            <g-table v-model:pagination="pagination" v-model:sort="sort" :model-value="tableData" :headers="headers">
              <template #item-classId="{ item }">
                {{ $t(`${Enums.getLabel(ClassId, item.classId).toLowerCase()}`) }}
              </template>
              <template #item-level="{ item }">
                <span class="level-bubble" :style="{ backgroundColor: getLevelColor(item.level as Level) }">
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
import { computed, onMounted, ref, shallowRef, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { ClassId, getAnalysisDetail, Level, type AnalysisPublic } from '@/client';
import AnalysisCharts from '@/components/analysis/AnalysisCharts.vue';
import RepoSection from '@/components/analysis/RepoSection.vue';
import GContainer from '@/components/GContainer.vue';
import GenericLoader from '@/components/GenericLoader.vue';
import GTable from '@/components/GTable.vue';
import PageView from '@/components/PageView.vue';
import FileTree from '@/components/repo/FileTree.vue';
import ThreeDotsMenu, { type MenuProps } from '@/components/ThreeDotsMenu.vue';
import { useClassLabel } from '@/composables/useClassLabel';
import { usePagination } from '@/composables/usePagination';
import { useSorting } from '@/composables/useSorting';
import { RouteNames } from '@/router/route-names';
import { useSnackbarStore } from '@/stores/snackbarStore';
import { LoadingStatus } from '@/types/loading';
import { type TableHeader } from '@/types/table';
import { buildChartData } from '@/utils/analysisCharts';
import { filterAndSortClasses, groupClassesBySelection } from '@/utils/analysisTable';
import { buildFileTree, resolveSelectedPaths } from '@/utils/analysisTree';
import Enums from '@/utils/enums';
import { getLevelColor } from '@/utils/utils';
import type { AnalysisClassPublicWithLevel, ChartData } from '@/types/analysis';
import type { TreeNode } from '@/types/treeview';

const { t } = useI18n();
const route = useRoute();
const snackbarStore = useSnackbarStore();
const sort = useSorting();
const pagination = usePagination();
const classLabel = useClassLabel();

const LEVELS = Enums.buildList(Level);

const analysisId = Number(route.params.id);
const loaderStatus = ref<LoadingStatus>(LoadingStatus.IDLE);
const search = ref<string>('');
const analysisData = shallowRef<AnalysisPublic | undefined>(undefined);
const selectedTreeNodeIds = ref<number[]>([]);
const fileTreeData = ref<TreeNode[]>([]);
const selectedLevels = ref<Level[]>(LEVELS.map(level => level.value as Level));
const idPathMap = ref<Record<number, string>>({});

const MENU_ITEMS: MenuProps[] = [
  {
    label: 'refresh_data',
    icon: 'mdi-refresh',
    onClick: async () => {
      await loadData();
    },
  },
];

const headers: TableHeader[] = [
  { label: 'class', key: 'classId', sortColumn: 'classId' },
  { label: 'level', key: 'level', sortColumn: 'level', width: '1px', align: 'center' },
  { label: 'instances', key: 'instances', sortColumn: 'instances', width: '1px', align: 'center' },
];

const selectedPaths = computed(() => resolveSelectedPaths(selectedTreeNodeIds.value, idPathMap.value));

const processedData = computed<AnalysisClassPublicWithLevel[]>(() => {
  const fileClasses = analysisData.value?.fileClasses ?? [];
  if (fileClasses.length === 0) return [];

  const grouped = groupClassesBySelection(fileClasses, selectedPaths.value, classLabel.getClassLevel);
  return filterAndSortClasses(grouped, selectedLevels.value, search.value, sort.value, classId =>
    t(Enums.getLabel(ClassId, classId))
  );
});

const tableData = computed<AnalysisClassPublicWithLevel[]>(() => {
  const { page, perPage } = pagination.value;
  return processedData.value.slice((page - 1) * perPage, page * perPage);
});

const chartData = computed<ChartData | null>(() => {
  if (!analysisData.value) return null;
  return buildChartData(
    analysisData.value.fileClasses || [],
    analysisData.value.repo?.commits || [],
    selectedPaths.value,
    processedData.value
  );
});

function toggleLevel(level: Level) {
  if (selectedLevels.value.includes(level)) {
    selectedLevels.value = selectedLevels.value.filter(l => l !== level);
  } else {
    selectedLevels.value.push(level);
  }
}

function onUpdateSelected(value: number[] | 'all') {
  if (value === 'all') {
    selectedTreeNodeIds.value = Object.keys(idPathMap.value).map(id => parseInt(id));
  } else {
    selectedTreeNodeIds.value = value;
  }
}

async function loadData() {
  if (isNaN(analysisId)) {
    loaderStatus.value = LoadingStatus.ERROR;
    return;
  }
  loaderStatus.value = LoadingStatus.LOADING;
  const { data, error } = await getAnalysisDetail({ path: { analysis_id: analysisId } });
  if (error) {
    loaderStatus.value = LoadingStatus.ERROR;
    snackbarStore.add({ text: 'error.fetching.analysis_data', color: 'error', icon: 'mdi-alert-circle-outline', closable: true });
    return;
  }
  analysisData.value = data;
  loaderStatus.value = LoadingStatus.IDLE;
}

function initializeTree() {
  const fileClasses = analysisData.value?.fileClasses;
  if (!fileClasses) return;

  const result = buildFileTree(fileClasses);
  fileTreeData.value = result.tree;
  idPathMap.value = result.idPathMap;
  selectedTreeNodeIds.value = result.selectedIds;
}

watch(
  () => processedData.value,
  newValue => {
    pagination.value = { ...pagination.value, total: newValue.length };
  }
);

onMounted(async () => {
  classLabel.fetch();
  await loadData();
  initializeTree();
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
