<template>
  <page-view>
    <header>
      <h1>{{ $t('summary') }}</h1>
    </header>

    <v-row gutter="16">
      <v-col v-for="(analysis, index) in analysesData" :key="index" cols="12" sm="6" md="4">
        <v-card variant="flat" class="pa-4 border h-100">
          <div class="d-flex align-center gap-4 mb-4">
            <v-avatar size="48">
              <v-img :src="analysis?.repo?.owner?.avatar || '@/assets/img/default_avatar.jpg'" alt="Avatar" />
            </v-avatar>
            <h3 class="font-weight-bold text-truncate">
              {{ analysis?.repo?.name || 'Unknown' }}
            </h3>
          </div>

          <p class="description mb-2">
            {{ analysis?.repo?.description || 'No description available' }}
          </p>

          <v-divider class="mb-4" />

          <div v-if="analysis?.repo" class="mb-4" style="font-size: 0.75rem">
            <div class="d-flex justify-space-between mb-1">
              <span class="font-weight-bold">{{ $t('creation_date') }}:</span>
              <span>{{ formatDate(analysis?.repo?.createdAt) }}</span>
            </div>
            <div class="d-flex justify-space-between">
              <span class="font-weight-bold">{{ $t('last_update') }}:</span>
              <span>{{ formatDate(analysis?.repo?.lastUpdatedAt) }}</span>
            </div>
          </div>

          <v-card-actions class="pa-0 align-end">
            <v-spacer />
            <v-btn color="primary" variant="flat" rounded="md" :to="`/repo/${analysis?.id}`">
              {{ $t('see_more') }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </page-view>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { formatDate } from '@/utils/utils';
import { listAnalysis } from '@/client';
import type { AnalysisSummaryPublic, Pagination } from '@/client';
import PageView from '@/components/PageView.vue';

const analysesData = ref<AnalysisSummaryPublic[]>([]);
const pagination = ref<Pagination>({ page: 1, perPage: 10, total: 0 });

async function loadData() {
  const { data, error } = await listAnalysis();

  if (error) {
    console.error('Error fetching repos data:', error);
    return;
  }
  analysesData.value = data.elements;
  pagination.value = data.pagination;
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
