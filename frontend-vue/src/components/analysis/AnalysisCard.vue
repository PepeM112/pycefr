<template>
  <v-card variant="flat" class="pa-4 border h-100">
    <div class="d-flex align-center ga-4 mb-4">
      <v-avatar size="48">
        <v-img :src="modelValue?.repo?.owner?.avatar || defaultAvatar" alt="Avatar" />
      </v-avatar>
      <h3 class="font-weight-bold text-truncate">
        <router-link v-if="modelValue?.status === 'completed'" :to="`/repo/${modelValue?.id}`" class="analysis-link">
          {{ modelValue?.name || 'N/A' }}
        </router-link>
        <span v-else>
          {{ modelValue?.name || 'N/A' }}
        </span>
      </h3>
      <v-spacer />
      <span class="status-badge" :class="`bg-${getAnalysisStatusColor(modelValue?.status)}`">
        {{ $t(modelValue?.status) }}
      </span>
    </div>

    <p class="description mb-2">
      {{ modelValue?.repo?.description || 'No description available' }}
    </p>

    <v-divider class="mb-4" />

    <div v-if="modelValue?.repo" class="mb-4" style="font-size: 0.75rem">
      <div class="d-flex justify-space-between mb-1">
        <span class="font-weight-bold">{{ $t('creation_date') }}:</span>
        <span>{{ formatDate(modelValue?.createdAt) }}</span>
      </div>
      <div class="d-flex justify-space-between">
        <span class="font-weight-bold">{{ $t('last_update') }}:</span>
        <span>{{ formatDate(modelValue?.repo?.lastUpdatedAt) }}</span>
      </div>
    </div>

    <v-card-actions class="pa-0 align-end">
      <v-spacer />
      <v-btn
        v-if="modelValue?.status === 'completed'"
        color="primary-on-surface"
        variant="flat"
        rounded="md"
        :to="{ name: RouteNames.ANALYSIS_DETAIL, params: { id: modelValue.id } }"
      >
        {{ $t('see_more') }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
<script setup lang="ts">
import defaultAvatar from '@/assets/img/default_avatar.jpg';
import type { AnalysisSummaryPublic } from '@/client';
import { RouteNames } from '@/router/route-names';
import { formatDate } from '@/utils/utils';

const props = defineProps<{
  modelValue: AnalysisSummaryPublic;
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

.analysis-link {
  text-decoration: none;
  color: inherit;

  &:hover {
    text-decoration: underline;
    opacity: 0.8;
  }
}
</style>
