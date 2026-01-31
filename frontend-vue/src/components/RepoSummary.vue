<template>
  <v-card variant="flat" class="pa-4 border h-100">
    <div class="d-flex align-center ga-4 mb-4">
      <v-avatar size="48">
        <v-img :src="analysis?.repo?.owner?.avatar || '@/assets/img/default_avatar.jpg'" alt="Avatar" />
      </v-avatar>
      <h3 class="font-weight-bold text-truncate">
        {{ analysis?.repo?.name || 'Unknown' }}
      </h3>
      <v-spacer />
      <span class="status-badge" :class="`bg-${getAnalysisStatusColor(analysis?.status)}`">
        {{ $t(analysis?.status) }}
      </span>
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
</template>
<script setup lang="ts">
import { formatDate } from '@/utils/utils';
import type { AnalysisSummaryPublic } from '@/client';

const props = defineProps<{
  analysis: AnalysisSummaryPublic;
}>();

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
</script>
<style lang="scss" scoped>
.status-badge {
  font-size: 0.75rem;
  border-radius: 1rem;
  padding: 2px 8px;
}

.description {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.25;
  font-size: 0.875rem;
  height: 2.5em;
  color: rgba(var(--v-theme-on-surface), 0.7);
}
</style>
