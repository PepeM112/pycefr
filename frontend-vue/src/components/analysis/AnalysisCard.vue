<template>
  <v-card variant="flat" class="pa-4 border h-100 d-flex flex-column">
    <div class="d-flex align-center ga-4 mb-4">
      <v-avatar size="48">
        <v-img :src="modelValue?.repo?.owner?.avatar || defaultAvatar" alt="Avatar" />
      </v-avatar>
      <div class="d-flex flex-column">
        <h3 class="font-weight-bold text-truncate">
          <router-link
            v-if="modelValue?.status === AnalysisStatus.COMPLETED"
            :to="`/repo/${modelValue?.id}`"
            class="analysis-link"
          >
            {{ modelValue?.name || 'N/A' }}
          </router-link>
          <span v-else>
            {{ modelValue?.name || 'N/A' }}
          </span>
        </h3>
        <span class="text-caption text-medium-emphasis">
          <g-date :date="modelValue?.createdAt" />
        </span>
      </div>
      <v-spacer />
      <span class="status-badge" :class="`bg-${getStatusColor(modelValue?.status)}`">
        {{ $t(modelValue?.status) }}
      </span>
    </div>

    <v-divider class="mb-4" />

    <v-sheet class="repo-summary bg-background pa-3 h-100" rounded="lg">
      <template v-if="modelValue.status === AnalysisStatus.FAILED">
        <p class="text-body-2">
          <v-icon class="mr-2" icon="mdi-alert-circle-outline" color="error" />
          {{ modelValue.errorMessage || $t('error_during_analysis') }}
        </p>
      </template>
      <template v-else-if="modelValue?.repo">
        <p class="mb-4">
          <v-icon class="mr-2" size="22" icon="iconify:simple-icons:github" />
          <span v-if="modelValue?.repo?.url">
            <a :href="modelValue?.repo?.owner?.profileUrl" target="_blank">
              {{ getProfileNameFromUrl(modelValue?.repo?.owner?.profileUrl || modelValue?.repo?.url) }}
            </a>
            <span class="mx-1">/</span>
            <a :href="modelValue?.repo?.url" target="_blank">{{ modelValue?.repo?.name }}</a>
          </span>
          <span v-else>{{ modelValue?.repo?.name }}</span>
        </p>
        <dl class="text-caption">
          <p class="description mb-4">
            {{ modelValue?.repo?.description || $t('no_description') }}
          </p>
          <div class="d-flex justify-space-between mb-1">
            <dt class="font-weight-bold">{{ $t('creation_date') }}:</dt>
            <dd><g-date :date="modelValue?.repo?.createdAt" /></dd>
          </div>

          <div class="d-flex justify-space-between">
            <dt class="font-weight-bold">{{ $t('last_update') }}:</dt>
            <dd><g-date :date="modelValue?.repo?.lastUpdatedAt" /></dd>
          </div>
        </dl>
      </template>
      <template v-else>
        <p class="text-body-2 text-medium-emphasis">
          <v-icon class="mr-2" icon="mdi-source-branch-remove" />
          {{ $t('git_analysis_not_included') }}
        </p>
      </template>
    </v-sheet>

    <v-spacer />

    <v-card-actions class="pa-0 align-end">
      <v-spacer />
      <v-btn
        v-if="modelValue?.status === AnalysisStatus.COMPLETED"
        color="primary-on-surface"
        variant="flat"
        density="comfortable"
        rounded="md"
        :to="{ name: RouteNames.ANALYSIS_DETAIL, params: { id: modelValue.id } }"
      >
        {{ $t('see_more') }}
      </v-btn>
      <v-btn
        v-else-if="modelValue?.status === AnalysisStatus.FAILED"
        color="error"
        variant="flat"
        density="comfortable"
        rounded="md"
        @click="$emit('delete', modelValue?.id ?? 0)"
      >
        {{ $t('delete') }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
<script setup lang="ts">
import defaultAvatar from '@/assets/img/default_avatar.jpg';
import { AnalysisStatus, type AnalysisSummaryPublic } from '@/client';
import GDate from '@/components/GDate.vue';
import { RouteNames } from '@/router/route-names';
import { getStatusColor } from '@/utils/utils';

defineEmits<{
  (e: 'delete', value: number): void;
}>();

defineProps<{
  modelValue: AnalysisSummaryPublic;
}>();

function getProfileNameFromUrl(url: string): string {
  try {
    const parsedUrl = new URL(url);
    return parsedUrl.pathname.split('/')[1] || '';
  } catch {
    return '';
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
  font-size: 0.75rem;
  height: 2.5em;
  color: rgba(var(--v-theme-on-surface), 0.7);
}

.analysis-link,
.repo-summary a {
  text-decoration: none;
  color: inherit;

  &:hover {
    text-decoration: underline;
    opacity: 0.8;
  }
}
</style>
