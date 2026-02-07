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
          <filter-table v-model:filter="filter" :filterList="filterList" />
        </v-card>
      </v-menu>
    </div>
  </page-view>
</template>
<script setup lang="ts">
import type { AnalysisSummaryPublic, Pagination } from '@/client';
import { listAnalysis } from '@/client';
import PageView from '@/components/PageView.vue';
import FilterTable from '@/components/filter/FilterTable.vue';
import { type FilterItem, type FilterValue, FilterType } from '@/components/filter';
import ThreeDotsMenu, { type MenuProps } from '@/components/ThreeDotsMenu.vue';
import { onMounted, ref } from 'vue';

const analysesData = ref<AnalysisSummaryPublic[]>([]);
const pagination = ref<Pagination>({ page: 1, perPage: 10, total: 0 });
const filter = ref<FilterValue>({});
const filterList = ref<FilterItem[]>([
  { label: 'name', type: FilterType.MULTIPLE_TEXT, key: 'name' },
  { label: 'owner', type: FilterType.MULTIPLE_NUMBER, key: 'owner' },
  { label: 'created_before', type: FilterType.DATE, key: 'created_before' },
  { label: 'created_after', type: FilterType.DATE, key: 'created_after' },
]);

const MENU_ITEMS: MenuProps[] = [
  {
    label: 'new_analysis',
    icon: 'mdi-refresh',
    onClick: async () => {
      await loadData();
    },
  },
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
    return;
  }

  analysesData.value = data.elements;
  pagination.value = data.pagination;
}

onMounted(async () => {
  await loadData();
});
</script>
<style lang="scss" scoped></style>
