<template>
  <page-view :header="$t('analyses')">
    <template #actions>
      <three-dots-menu :model-value="menuItems" />
    </template>
    <div class="bg-primary mb-6 rounded-lg">
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
          <filter-table v-model:filter="filter" :filterList="filterList" />
        </v-card>
      </v-menu>
    </div>
    <g-container class="mb-4">
      <generic-loader :model-value="loadingStatus">
        <g-table :model-value="analysesData" :headers="headers" :pagination="pagination" v-model:sort="sorting">
          <template #item-status="{ item }">
            <span class="status-badge" :class="`bg-${getAnalysisStatusColor(item.status)}`">
              {{ $t(item.status) }}
            </span>
          </template>
          <template #item-origin="{ item }">
            <v-icon class="mr-2" :icon="getOriginIcon(item.origin)" />
            {{ $t(Enums.getLabel(Origin, item.origin)) }}
          </template>
          <template #item-created_at="{ item }">
            <g-date :date="item.createdAt" />
          </template>
          <template #item-error_message="{ item }">
            {{ item.errorMessage }}
          </template>
          <template #actions="{ item }">
            <v-btn
              density="comfortable"
              icon="mdi-eye-outline"
              :to="{ name: RouteNames.ANALYSIS_DETAIL, params: { id: item.id } }"
            />
            <v-btn density="comfortable" icon="mdi-tray-arrow-down" @click="handleDownload(item.id, item.name)" />
            <v-btn
              density="comfortable"
              icon="mdi-trash-can-outline"
              color="error"
              variant="text"
              @click="analysisBeingDeleted = item.id"
            />
          </template>
        </g-table>
      </generic-loader>
      <g-dialog-card
        v-model="showNewAnalysisDialog"
        title="new_analysis"
        width="400"
        :disable-confirm="!isFormValid"
        @confirm-pre="saveForm"
      >
        <v-form v-model="isFormValid">
          <g-input label="Repository url" required>
            <v-text-field v-model="newAnalysisName" :rules="[rules.required, rules.url]" />
          </g-input>
        </v-form>
      </g-dialog-card>
      <g-dialog-card
        v-model="showUploadDialog"
        title="upload_analysis"
        confirm-label="upload"
        width="400"
        show-size
        :disableConfirm="fileToUpload.length === 0"
        @confirm-pre="() => handleUpload()"
        @close-pre="
          () => {
            fileToUpload = [];
          }
        "
      >
        <v-file-upload v-model="fileToUpload" accept="application/json" density="comfortable" rounded="lg" clearable />
      </g-dialog-card>
      <g-dialog-card
        :model-value="!!analysisBeingDeleted"
        title="delete_analysis"
        text="confirm_delete_analysis"
        width="400"
        @confirm-pre="() => removeAnalysis(analysisBeingDeleted)"
        @close-pre="() => (analysisBeingDeleted = undefined)"
      />
    </g-container>
  </page-view>
</template>
<script setup lang="ts">
import {
  AnalysisSortColumn,
  AnalysisStatus,
  type AnalysisSummaryPublic,
  type EntityLabelString,
  type Pagination,
  Origin,
} from '@/client';
import { createAnalysis, deleteAnalysis, getOwners, listAnalysis, uploadAnalysis, downloadAnalysis } from '@/client';
import { type DateFilterValue, type FilterEntity, type FilterItem, type FilterValue, FilterType } from '@/types/filter';
import FilterTable from '@/components/filter/FilterTable.vue';
import GContainer from '@/components/GContainer.vue';
import GDate from '@/components/GDate.vue';
import GDialogCard from '@/components/GDialogCard.vue';
import GInput from '@/components/GInput.vue';
import PageView from '@/components/PageView.vue';
import ThreeDotsMenu, { type MenuProps } from '@/components/ThreeDotsMenu.vue';
import { useRules } from '@/composables/useRules';
import { RouteNames } from '@/router/route-names';
import { useSnackbarStore } from '@/stores/snackbarStore';
import { computed, onMounted, ref } from 'vue';
import GTable from '@/components/GTable.vue';
import { useSortFilter } from '@/composables/useSortFilter';
import { type TableHeader } from '@/types/table';
import GenericLoader from '@/components/GenericLoader.vue';
import { LoadingStatus } from '@/types/loading';
import Enums from '@/utils/enums';
import { useFilters } from '@/composables/useFilter';

const rules = useRules();
const sorting = useSortFilter();
const snackbarStore = useSnackbarStore();

const analysesData = ref<AnalysisSummaryPublic[]>([]);
const pagination = ref<Pagination>({ page: 1, perPage: 10, total: 0 });
const filter = ref<FilterValue>({});
const showNewAnalysisDialog = ref<boolean>(false);
const showUploadDialog = ref<boolean>(false);
const fileToUpload = ref<File[]>([]);
const isUploading = ref<boolean>(false);
const analysisBeingDeleted = ref<number | undefined>(undefined);
const newAnalysisName = ref<string>('');
const isFormValid = ref(false);
const loadingStatus = ref<LoadingStatus>(LoadingStatus.IDLE);
const ownersList = ref<FilterEntity[]>([]);

const statusList = Enums.buildList(AnalysisStatus);

const filterList = computed<FilterItem[]>(() => [
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
      items: ownersList.value,
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
    label: 'dates',
    type: FilterType.DATE,
    key: 'dates',
    query: 'd',
  },
]);

useFilters(filter, filterList, loadData, { debounceWait: 500 });

const menuItems: MenuProps[] = [
  {
    label: 'new_analysis',
    icon: 'mdi-plus',
    onClick: async () => (showNewAnalysisDialog.value = true),
  },
  {
    label: 'upload_analysis',
    icon: 'mdi-tray-arrow-up',
    onClick: async () => (showUploadDialog.value = true),
  },
];

const headers: TableHeader[] = [
  { label: 'id', key: 'id', width: '1px', sortColumn: AnalysisSortColumn.ID },
  { label: 'name', key: 'name', sortColumn: AnalysisSortColumn.NAME },
  { label: 'origin', key: 'origin', sortColumn: AnalysisSortColumn.ORIGIN },
  { label: 'creation_date', key: 'created_at', sortColumn: AnalysisSortColumn.CREATED_AT },
  { label: 'status', key: 'status', sortColumn: AnalysisSortColumn.STATUS },
  { label: 'error_message', key: 'error_message' },
];

async function getOwnersList() {
  const { data, error } = await getOwners();
  if (error) {
    console.error('error.fetching.owners:', error);
    snackbarStore.add({
      text: 'error.fetching.owners',
      color: 'error',
      icon: 'mdi-alert-circle-outline',
      closable: true,
    });
    return;
  }
  ownersList.value = data?.map((owner: EntityLabelString) => ({ label: owner.label, value: owner.id })) ?? [];
}

async function loadData() {
  loadingStatus.value = LoadingStatus.LOADING;
  const { data, error } = await listAnalysis({
    query: {
      page: pagination.value.page,
      per_page: pagination.value.perPage,
      sort_column: Number(sorting.value.column) as AnalysisSortColumn,
      sort_direction: sorting.value.direction,
      // Filters
      name: filter.value.name as string[],
      owner: filter.value.owner as string[],
      status: filter.value.status as AnalysisStatus[],
      date_from: (filter.value.dates as DateFilterValue)?.from,
      date_to: (filter.value.dates as DateFilterValue)?.to,
    },
  });

  if (error) {
    console.error('error.fetching.analyses:', error);
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

async function removeAnalysis(id: number = 0) {
  if (!id) return;

  const { error } = await deleteAnalysis({
    path: { analysis_id: id },
  });

  if (error) {
    console.error('error.deleting.analysis:', error);
    snackbarStore.add({
      text: 'error.deleting.analysis',
      color: 'error',
      icon: 'mdi-alert-circle-outline',
      closable: true,
    });
    return;
  }

  snackbarStore.add({
    text: 'success.deleting.analysis',
    color: 'success',
    icon: 'mdi-check-circle-outline',
    closable: true,
  });

  analysisBeingDeleted.value = undefined;
  analysesData.value = analysesData.value.filter(analysis => analysis.id !== id);
  pagination.value.total -= 1;
}

async function saveForm() {
  const { data, error } = await createAnalysis({
    body: { repoUrl: newAnalysisName.value },
  });

  if (error) {
    console.error('error.creating.analysis:', error);
    snackbarStore.add({
      text: 'error.creating.analysis',
      color: 'error',
      icon: 'mdi-alert-circle-outline',
      closable: true,
    });
    return;
  }
  snackbarStore.add({
    text: 'success.creating.analysis',
    color: 'success',
    icon: 'mdi-check-circle-outline',
    closable: true,
  });
  analysesData.value.unshift(data);
  showNewAnalysisDialog.value = false;
}

async function handleUpload() {
  if (!fileToUpload.value) return;

  isUploading.value = true;

  const { data, error } = await uploadAnalysis({
    body: { file: fileToUpload.value[0] as File },
  });

  isUploading.value = false;

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

function getAnalysisStatusColor(status: string): string {
  switch (status) {
    case 'completed':
      return 'success';
    case 'in_progress':
      return 'warning';
    case 'failed':
      return 'error';
    default:
      return 'grey';
  }
}

function getOriginIcon(origin: Origin): string {
  switch (origin) {
    case Origin.GITHUB:
      return 'iconify:simple-icons:github';
    case Origin.LOCAL:
      return 'mdi-laptop';
    default:
      return '';
  }
}

onMounted(async () => {
  await getOwnersList();
});
</script>
<style lang="scss" scoped>
.status-badge {
  font-size: 0.75rem;
  border-radius: 1rem;
  padding: 2px 8px;
}
</style>
