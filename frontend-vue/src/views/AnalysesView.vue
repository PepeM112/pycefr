<template>
  <page-view :header="$t('analyses')">
    <template #actions>
      <three-dots-menu :model-value="MENU_ITEMS" />
    </template>
    <div class="bg-primary mb-6 rounded-lg">
      <v-menu :close-on-content-click="false">
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
        <v-card class="bg-primary" width="400">
          <filter-table v-model:filter="filter" :filterList="FILTER_LIST" />
        </v-card>
      </v-menu>
    </div>
    <g-dialog-card
      v-model="showAnalysisForm"
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
    <g-container class="mb-4">
      <g-table :model-value="analysesData" :headers="HEADERS" :pagination="pagination" :sort-filter="sortFilter">
        <template #item-status="{ item }">
          <span class="status-badge" :class="`bg-${getAnalysisStatusColor(item.status)}`">
            {{ $t(item.status) }}
          </span>
        </template>
        <template #item-created_at="{ item }">
          <g-date :date="item.createdAt" />
        </template>
        <template #actions="{ item }">
          <v-btn
            density="comfortable"
            icon="mdi-eye-outline"
            :to="{ name: RouteNames.ANALYSIS_DETAIL, params: { id: item.id } }"
          />
        </template>
      </g-table>
    </g-container>
  </page-view>
</template>
<script setup lang="ts">
import type { AnalysisSummaryPublic, Pagination } from '@/client';
import { createAnalysis, listAnalysis } from '@/client';
import { type FilterItem, type FilterValue, FilterType } from '@/components/filter';
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
import { onMounted, ref } from 'vue';
import GTable from '@/components/GTable.vue';
import { useSortFilter } from '@/composables/useSortFilter';

const rules = useRules();
const sortFilter = useSortFilter();
const snackbarStore = useSnackbarStore();

const analysesData = ref<AnalysisSummaryPublic[]>([]);
const pagination = ref<Pagination>({ page: 1, perPage: 10, total: 0 });
const filter = ref<FilterValue>({});
const showAnalysisForm = ref<boolean>(false);
const newAnalysisName = ref<string>('');
const isFormValid = ref(false);

const FILTER_LIST: FilterItem[] = [
  { label: 'name', type: FilterType.MULTIPLE_TEXT, key: 'name' },
  { label: 'owner', type: FilterType.MULTIPLE_NUMBER, key: 'owner' },
  { label: 'created_before', type: FilterType.DATE, key: 'created_before' },
  { label: 'created_after', type: FilterType.DATE, key: 'created_after' },
];

const MENU_ITEMS: MenuProps[] = [
  {
    label: 'new_analysis',
    icon: 'mdi-plus',
    onClick: async () => (showAnalysisForm.value = true),
  },
];

const HEADERS = [
  { label: 'id', key: 'id', width: '1px' },
  { label: 'name', key: 'name' },
  { label: 'status', key: 'status' },
  { label: 'creation_date', key: 'created_at' },
];

async function loadData() {
  const { data, error } = await listAnalysis({
    query: {
      page: pagination.value.page,
      per_page: pagination.value.perPage,
    },
  });

  if (error) {
    console.error('error.fetching.analyses:', error);
    snackbarStore.add({
      text: 'error.fetching.summary',
      color: 'error',
      icon: 'mdi-alert-circle-outline',
      closable: true,
    });
    return;
  }

  analysesData.value = data.elements;
  pagination.value = data.pagination;
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
  showAnalysisForm.value = false;
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

onMounted(async () => {
  await loadData();
});
</script>
<style lang="scss" scoped>
.status-badge {
  font-size: 0.75rem;
  border-radius: 1rem;
  padding: 2px 8px;
}
</style>
