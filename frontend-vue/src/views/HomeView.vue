<template>
  <page-view :header="$t('summary')">
    <v-row gutter="16">
      <v-col v-for="(analysis, index) in analysesData" :key="index" cols="12" sm="6" md="4">
        <analysis-card :modelValue="analysis" />
      </v-col>
    </v-row>
  </page-view>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { listAnalysis } from '@/client';
import type { AnalysisSummaryPublic } from '@/client';
import PageView from '@/components/PageView.vue';
import AnalysisCard from '@/components/AnalysisCard.vue';

const analysesData = ref<AnalysisSummaryPublic[]>([]);

const PER_PAGE = 9;
async function loadData() {
  const { data, error } = await listAnalysis({
    query: {
      page: 1,
      per_page: PER_PAGE,
    },
  });

  if (error) {
    console.error('error.fetching.analyses:', error);
    return;
  }
  analysesData.value = data.elements;
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
