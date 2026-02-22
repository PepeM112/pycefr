<template>
  <page-view :header="$t('summary')">
    <generic-loader :model-value="loadingStatus">
      <v-row gutter="16">
        <v-col v-for="(analysis, index) in analysesData" :key="index" cols="12" sm="6" md="4">
          <analysis-card :modelValue="analysis" @delete="removeAnalysis(analysis.id)" />
        </v-col>
      </v-row>
    </generic-loader>
  </page-view>
</template>
<script setup lang="ts">
import type { AnalysisSummaryPublic } from '@/client';
import { deleteAnalysis, listAnalysis } from '@/client';
import AnalysisCard from '@/components/analysis/AnalysisCard.vue';
import GenericLoader from '@/components/GenericLoader.vue';
import PageView from '@/components/PageView.vue';
import { useSnackbarStore } from '@/stores/snackbarStore';
import { LoadingStatus } from '@/types/loading';
import { onMounted, ref } from 'vue';

const snackbarStore = useSnackbarStore();

const analysesData = ref<AnalysisSummaryPublic[]>([]);
const loadingStatus = ref<LoadingStatus>(LoadingStatus.IDLE);

const PER_PAGE = 9;
async function loadData() {
  loadingStatus.value = LoadingStatus.LOADING;
  const { data, error } = await listAnalysis({
    query: {
      page: 1,
      per_page: PER_PAGE,
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

  analysesData.value = analysesData.value.filter(analysis => analysis.id !== id);
}

onMounted(async () => {
  await loadData();
});
</script>
<style lang="scss" scoped>
.description {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.25;
  font-size: 0.875rem;
  height: 2.5em;
  color: rgb(var(--v-theme-on-surface), 0.7);
}

.gap-4 {
  gap: 1rem;
}
</style>
