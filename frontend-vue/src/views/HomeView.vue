<template>
  <page-view :header="$t('summary')">
    <generic-loader :model-value="loadingStatus">
      <v-row>
        <v-col v-for="(analysis, index) in analysesData" :key="index" cols="12" sm="6" md="4">
          <analysis-card :modelValue="analysis" @delete="handleDelete(analysis.id)" />
        </v-col>
      </v-row>
    </generic-loader>
  </page-view>
</template>
<script setup lang="ts">
import type { AnalysisSummaryPublic } from '@/client';
import { listAnalysis } from '@/client';
import AnalysisCard from '@/components/analysis/AnalysisCard.vue';
import GenericLoader from '@/components/GenericLoader.vue';
import PageView from '@/components/PageView.vue';
import { useAnalysisDelete } from '@/composables/analysis/useAnalysisDelete';
import { useSnackbarStore } from '@/stores/snackbarStore';
import { LoadingStatus } from '@/types/loading';
import { onMounted, ref } from 'vue';

const snackbarStore = useSnackbarStore();
const { removeAnalysis } = useAnalysisDelete();

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

async function handleDelete(id: number) {
  const success = await removeAnalysis(id);
  if (success) {
    analysesData.value = analysesData.value.filter(analysis => analysis.id !== id);
  }
}

onMounted(async () => {
  await loadData();
});
</script>
