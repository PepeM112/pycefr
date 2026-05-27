<template>
  <page-view :header="$t('analyses')">
    <template #actions>
      <three-dots-menu :model-value="menuItems" />
    </template>
    <div class="d-flex align-center bg-primary mb-6 rounded-lg">
      <v-menu :close-on-content-click="false" eager>
        <template #activator="{ props: menuProps }">
          <v-btn
            v-bind="menuProps"
            class="h-100 pa-4 rounded-ts-lg rounded-bs-lg rounded-te-0 rounded-be-0"
            size="large"
            variant="text"
            prepend-icon="mdi-filter-variant"
          >
            {{ $t('filter') }}
          </v-btn>
        </template>
        <v-card class="bg-primary" width="420">
          <filter-table v-model:filter="filter" :filter-list="filterList" />
        </v-card>
      </v-menu>
      <v-spacer />
      <v-btn-toggle v-model="viewMode" class="mr-2" density="comfortable" mandatory variant="text">
        <v-btn value="table" icon="mdi-table" size="small" />
        <v-btn value="cards" icon="mdi-view-grid" size="small" />
      </v-btn-toggle>
    </div>
    <g-container class="mb-4">
      <generic-loader :model-value="loadingStatus">
        <!-- TABLE VIEW -->
        <template v-if="viewMode === 'table'">
          <g-table
            v-model:pagination="pagination"
            v-model:sort="sorting"
            :model-value="analysesData"
            :headers="headers"
          >
            <template #item-status="{ item }">
              <span class="status-badge" :class="`bg-${getStatusColor(item.status)}`">
                {{ $t(item.status) }}
              </span>
            </template>
            <template #item-origin="{ item }">
              <a
                v-if="item.origin === Origin.GITHUB && item.repo?.url"
                class="origin-link"
                :href="item.repo.url"
                target="_blank"
                rel="noopener noreferrer"
              >
                <v-icon class="mr-2" :icon="getOriginIcon(item.origin)" />
                {{ $t(getLabel(Origin, item.origin)) }}
              </a>
              <template v-else>
                <v-icon class="mr-2" :icon="getOriginIcon(item.origin)" />
                {{ $t(getLabel(Origin, item.origin)) }}
              </template>
            </template>
            <template #item-created_at="{ item }">
              <g-date :date="item.createdAt" is-relative />
            </template>
            <template #item-tags="{ item }">
              <div class="d-flex ga-1 flex-wrap">
                <v-chip v-for="tag in item.tags" :key="tag" size="small" label>
                  {{ tag }}
                </v-chip>
              </div>
            </template>
            <template #item-error_message="{ item }">
              {{ item.errorMessage }}
            </template>
            <template #actions="{ item }">
              <v-btn
                v-if="item.status === AnalysisStatus.IN_PROGRESS"
                density="comfortable"
                icon="mdi-progress-clock"
                @click="handleOpenProgress(item)"
              />
              <template v-if="item.status !== AnalysisStatus.IN_PROGRESS">
                <template v-if="item.status === AnalysisStatus.COMPLETED">
                  <v-btn
                    density="comfortable"
                    icon="mdi-eye-outline"
                    :to="{ name: RouteNames.ANALYSIS_DETAIL, params: { id: item.id } }"
                  />
                  <v-btn density="comfortable" icon="mdi-pencil-outline" @click="handleOpenEdit(item)" />
                  <v-btn density="comfortable" icon="mdi-tray-arrow-down" @click="handleDownload(item.id, item.name)" />
                </template>
                <v-tooltip v-else-if="item.status === AnalysisStatus.FAILED && item.repo?.url">
                  <template #activator="{ props: tooltipProps }">
                    <v-btn v-bind="tooltipProps" density="comfortable" icon="mdi-reload" @click="handleRetry(item)" />
                  </template>
                  <span>{{ $t('retry') }}</span>
                </v-tooltip>
                <v-btn
                  density="comfortable"
                  icon="mdi-trash-can-outline"
                  color="error"
                  variant="text"
                  @click="analysisBeingDeleted = item.id"
                />
              </template>
            </template>
          </g-table>
        </template>

        <!-- CARD VIEW -->
        <template v-else>
          <v-row>
            <v-col v-for="analysis in analysesData" :key="analysis.id" cols="12" sm="6" md="4">
              <analysis-card :model-value="analysis" @delete="handleDeleteAnalysis(analysis.id)" />
            </v-col>
          </v-row>
          <div v-if="hasMoreCards" class="d-flex justify-center mt-6">
            <v-btn variant="tonal" :loading="isLoadingMore" prepend-icon="mdi-chevron-down" @click="handleLoadMore">
              {{ $t('dashboard.load_more') }}
            </v-btn>
          </div>
        </template>
      </generic-loader>
      <new-analysis-dialog
        v-model="showNewAnalysisDialog"
        :reconnect-analysis-id="reconnectAnalysisId"
        @created="handleAnalysisCreated"
        @completed="handleAnalysisCompleted"
        @update:model-value="handleNewDialogClose"
      />
      <g-dialog-card
        v-model="showUploadDialog"
        title="upload_analysis"
        confirm-label="upload"
        width="400"
        show-size
        :is-confirm-disabled="fileToUpload.length === 0"
        @confirm-pre="handleUpload"
        @close-pre="handleUploadDialogClose"
      >
        <v-file-upload v-model="fileToUpload" accept="application/json" density="comfortable" rounded="lg" clearable />
      </g-dialog-card>
      <g-dialog-card
        :model-value="!!analysisBeingDeleted"
        title="delete_analysis"
        text="confirm_delete_analysis"
        width="400"
        @confirm-pre="() => analysisBeingDeleted !== undefined && handleDeleteAnalysis(analysisBeingDeleted)"
        @close-pre="() => (analysisBeingDeleted = undefined)"
      />
      <edit-analysis-dialog v-model="showEditDialog" :analysis="analysisBeingEdited" @saved="handleAnalysisEdited" />
      <bulk-analysis-dialog v-model="showBulkDialog" @created="handleAnalysisCreated" />
    </g-container>
  </page-view>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue';
import {
  type AnalysisPublic,
  type AnalysisSummaryPublic,
  AnalysisSortColumn,
  AnalysisStatus,
  createAnalysis,
  downloadAnalysis,
  listAnalysis,
  Origin,
  uploadAnalysis,
} from '@/client';
import { client } from '@/client/client.gen';
import AnalysisCard from '@/components/analysis/AnalysisCard.vue';
import BulkAnalysisDialog from '@/components/analysis/BulkAnalysisDialog.vue';
import FilterTable from '@/components/filter/FilterTable.vue';
import GContainer from '@/components/GContainer.vue';
import GDate from '@/components/GDate.vue';
import GDialogCard from '@/components/GDialogCard.vue';
import GenericLoader from '@/components/GenericLoader.vue';
import GTable from '@/components/GTable.vue';
import EditAnalysisDialog from '@/components/analysis/EditAnalysisDialog.vue';
import NewAnalysisDialog from '@/components/analysis/NewAnalysisDialog.vue';
import PageView from '@/components/PageView.vue';
import ThreeDotsMenu from '@/components/ThreeDotsMenu.vue';
import { useAnalysisDelete } from '@/composables/analysis/useAnalysisDelete';
import { useOwnerFetcher } from '@/composables/fetcher/useOwnerFetcher';
import { useTagFetcher } from '@/composables/fetcher/useTagFetcher';
import { useFilter } from '@/composables/useFilter';
import { useSorting } from '@/composables/useSorting';
import { RouteNames } from '@/router/route-names';
import { useSnackbarStore } from '@/stores/snackbarStore';
import { type DateFilterValue, type FilterItem, FilterType } from '@/types/filter';
import { LoadingStatus } from '@/types/loading';
import { type TableHeader } from '@/types/table';
import { buildList, getLabel } from '@/utils/enums';
import { getOriginIcon, getStatusColor } from '@/utils/utils';
import { usePagination } from '@/composables/usePagination';
import { useFetchOnQuery } from '@/composables/useFetchOnQuery';
import type { MenuAction } from '@/types/menu';

const CARDS_PER_PAGE = 9;
const VIEW_MODE_KEY = 'pycefr-analyses-view-mode';

type ViewMode = 'table' | 'cards';

const snackbarStore = useSnackbarStore();
const { removeAnalysis } = useAnalysisDelete();
const ownerFetcher = useOwnerFetcher({ limit: 10, debounce: 300 });
const tagFetcher = useTagFetcher({ limit: 20, debounce: 300 });

const analysesData = ref<(AnalysisSummaryPublic | AnalysisPublic)[]>([]);
const showNewAnalysisDialog = ref<boolean>(false);
const showUploadDialog = ref<boolean>(false);
const showBulkDialog = ref<boolean>(false);
const fileToUpload = ref<File[]>([]);
const analysisBeingDeleted = ref<number | undefined>(undefined);
const showEditDialog = ref(false);
const analysisBeingEdited = ref<AnalysisSummaryPublic | null>(null);
const reconnectAnalysisId = ref<number | null>(null);
const loadingStatus = ref<LoadingStatus>(LoadingStatus.IDLE);
const viewMode = ref<ViewMode>((localStorage.getItem(VIEW_MODE_KEY) as ViewMode) || 'table');
const cardPage = ref(1);
const cardTotal = ref(0);
const isLoadingMore = ref(false);

watch(viewMode, val => {
  localStorage.setItem(VIEW_MODE_KEY, val);
  if (val === 'cards') {
    cardPage.value = 1;
    void loadCardsData(true);
  }
});

const hasMoreCards = computed(() => analysesData.value.length < cardTotal.value);

const statusList = buildList(AnalysisStatus);

const filterList: FilterItem[] = [
  {
    label: 'name',
    type: FilterType.MULTIPLE,
    key: 'name',
    query: 'n',
  },
  {
    label: 'owner',
    type: FilterType.MULTIPLE_SELECT,
    key: 'owner',
    query: 'o',
    options: {
      fetcher: ownerFetcher,
    },
  },
  {
    label: 'status',
    type: FilterType.MULTIPLE_SELECT,
    key: 'status',
    query: 's',
    options: {
      items: statusList,
    },
  },
  {
    label: 'tags',
    type: FilterType.MULTIPLE_SELECT,
    key: 'tags',
    query: 't',
    options: {
      fetcher: tagFetcher,
    },
  },
  {
    label: 'dates',
    type: FilterType.DATE,
    key: 'dates',
    query: 'd',
  },
];

const sorting = useSorting();
const pagination = usePagination();
const { filters: filter, getValue: getFilterValue } = useFilter(filterList);

useFetchOnQuery(loadData, {
  immediate: true,
  debounceWait: 400,
});

const menuItems: MenuAction[] = [
  {
    label: 'new_analysis',
    icon: 'mdi-plus',
    onClick: () => (showNewAnalysisDialog.value = true),
  },
  {
    label: 'bulk_analysis.title',
    icon: 'mdi-playlist-plus',
    onClick: () => (showBulkDialog.value = true),
  },
  {
    label: 'upload_analysis',
    icon: 'mdi-tray-arrow-up',
    onClick: () => (showUploadDialog.value = true),
  },
];

const headers: TableHeader[] = [
  { label: 'id', key: 'id', width: '1px', sortColumn: AnalysisSortColumn.ID },
  { label: 'name', key: 'name', sortColumn: AnalysisSortColumn.NAME },
  { label: 'origin', key: 'origin', sortColumn: AnalysisSortColumn.ORIGIN },
  { label: 'creation_date', key: 'created_at', sortColumn: AnalysisSortColumn.CREATED_AT },
  { label: 'status', key: 'status', sortColumn: AnalysisSortColumn.STATUS },
  { label: 'tags', key: 'tags' },
  { label: 'error_message', key: 'error_message' },
];

function buildFilterQuery(page: number, perPage: number) {
  const dates = getFilterValue<DateFilterValue>('dates');
  return {
    page,
    per_page: perPage,
    sort_column: Number(sorting.value.column),
    sort_direction: sorting.value.direction,
    name: getFilterValue<string[]>('name'),
    owner: getFilterValue<string[]>('owner'),
    status: getFilterValue<AnalysisStatus[]>('status'),
    tags: getFilterValue<string[]>('tags'),
    date_from: dates?.from,
    date_to: dates?.to,
  };
}

async function loadData() {
  if (viewMode.value === 'cards') {
    await loadCardsData(true);
    return;
  }

  loadingStatus.value = LoadingStatus.LOADING;
  const { data, error } = await listAnalysis({
    query: buildFilterQuery(pagination.value.page, pagination.value.perPage),
  });

  if (error) {
    snackbarStore.add({
      text: 'error.fetching.analyses',
      color: 'error',
      icon: 'mdi-alert-circle-outline',
      closable: true,
    });
    loadingStatus.value = LoadingStatus.ERROR;
    return;
  }

  analysesData.value = data.elements;
  loadingStatus.value = analysesData.value.length === 0 ? LoadingStatus.EMPTY : LoadingStatus.IDLE;
  pagination.value = data.pagination;
}

async function loadCardsData(reset: boolean) {
  if (reset) {
    cardPage.value = 1;
    loadingStatus.value = LoadingStatus.LOADING;
  } else {
    isLoadingMore.value = true;
  }

  const { data, error } = await listAnalysis({
    query: buildFilterQuery(cardPage.value, CARDS_PER_PAGE),
  });

  isLoadingMore.value = false;

  if (error) {
    snackbarStore.add({
      text: 'error.fetching.analyses',
      color: 'error',
      icon: 'mdi-alert-circle-outline',
      closable: true,
    });
    loadingStatus.value = LoadingStatus.ERROR;
    return;
  }

  if (reset) {
    analysesData.value = data.elements;
  } else {
    analysesData.value = [...analysesData.value, ...data.elements];
  }

  cardTotal.value = data.pagination.total;
  loadingStatus.value = analysesData.value.length === 0 ? LoadingStatus.EMPTY : LoadingStatus.IDLE;
}

function handleLoadMore() {
  cardPage.value += 1;
  void loadCardsData(false);
}

async function handleDeleteAnalysis(id: number) {
  const success = await removeAnalysis(id);
  if (!success) return;

  analysisBeingDeleted.value = undefined;
  analysesData.value = analysesData.value.filter(analysis => analysis.id !== id);
  if (viewMode.value === 'table') {
    pagination.value.total -= 1;
  } else {
    cardTotal.value -= 1;
  }
}

const activeTrackers = new Map<number, EventSource>();

function trackAnalysis(analysisId: number) {
  if (activeTrackers.has(analysisId)) return;

  const baseUrl = client.getConfig().baseUrl ?? '';
  const es = new EventSource(`${baseUrl}/api/v1/analyses/${analysisId}/progress`);
  activeTrackers.set(analysisId, es);

  es.onmessage = (event: MessageEvent) => {
    const data = JSON.parse(String(event.data)) as { step: string; error?: string };
    if (data.step !== 'COMPLETED' && data.step !== 'FAILED') return;

    const newStatus = data.step === 'COMPLETED' ? AnalysisStatus.COMPLETED : AnalysisStatus.FAILED;
    const match = analysesData.value.find(a => a.id === analysisId);
    if (match) {
      match.status = newStatus;
      if (data.step === 'FAILED' && data.error) {
        match.errorMessage = data.error;
      }
    }

    stopTracking(analysisId);
  };

  es.onerror = () => {
    stopTracking(analysisId);
  };
}

function stopTracking(analysisId: number) {
  const es = activeTrackers.get(analysisId);
  if (es) {
    es.close();
    activeTrackers.delete(analysisId);
  }
}

function stopAllTracking() {
  activeTrackers.forEach(es => es.close());
  activeTrackers.clear();
}

onUnmounted(stopAllTracking);

function handleAnalysisCreated(analysis: AnalysisSummaryPublic | AnalysisPublic) {
  analysesData.value.unshift(analysis);
  if (viewMode.value === 'table') {
    pagination.value.total += 1;
  } else {
    cardTotal.value += 1;
  }

  if (analysis.status === AnalysisStatus.IN_PROGRESS) {
    trackAnalysis(analysis.id);
  }
}

function handleAnalysisCompleted() {
  void loadData();
}

async function handleRetry(item: AnalysisSummaryPublic) {
  const { data, error } = await createAnalysis({
    body: {
      name: item.name || undefined,
      repoUrl: item.repo?.url ?? '',
      includeGit: true,
    },
  });

  if (error || !data) {
    snackbarStore.add({
      text: 'error.creating.analysis',
      color: 'error',
      icon: 'mdi-alert-circle-outline',
      closable: true,
    });
    return;
  }

  handleAnalysisCreated(data);
  reconnectAnalysisId.value = data.id;
  showNewAnalysisDialog.value = true;
}

function handleOpenProgress(item: AnalysisSummaryPublic) {
  reconnectAnalysisId.value = item.id;
  showNewAnalysisDialog.value = true;
}

async function handleUpload() {
  if (!fileToUpload.value) return;

  const { data, error } = await uploadAnalysis({
    body: { file: fileToUpload.value[0] },
  });

  if (error) {
    snackbarStore.add({
      text: 'error.uploading.analysis',
      color: 'error',
      icon: 'mdi-alert-circle-outline',
    });
    return;
  }

  snackbarStore.add({
    text: 'success.uploading.analysis',
    color: 'success',
    icon: 'mdi-check-circle-outline',
  });

  fileToUpload.value = [];
  showUploadDialog.value = false;

  if (data) analysesData.value.unshift(data);
}

function handleOpenEdit(item: AnalysisSummaryPublic) {
  analysisBeingEdited.value = item;
  showEditDialog.value = true;
}

function handleAnalysisEdited(updated: AnalysisSummaryPublic) {
  analysesData.value = analysesData.value.map(a => (a.id === updated.id ? updated : a));
}

function handleNewDialogClose(val: boolean) {
  if (!val) {
    reconnectAnalysisId.value = null;
  }
}

function handleUploadDialogClose() {
  fileToUpload.value = [];
}

async function handleDownload(id: number, name: string) {
  const { data, error } = await downloadAnalysis({
    path: { analysis_id: id },
    parseAs: 'blob',
  });

  if (error || !data) {
    snackbarStore.add({
      text: 'error.downloading.analysis',
      color: 'error',
      icon: 'mdi-alert-circle-outline',
    });
    return;
  }

  const blob = data instanceof Blob ? data : new Blob([JSON.stringify(data)], { type: 'application/json' });

  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `downloaded_${name}.json`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
</script>

<style lang="scss" scoped>
.origin-link {
  display: inline-flex;
  color: inherit;
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
}
</style>
