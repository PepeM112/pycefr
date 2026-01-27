<template>
  <div class="content">
    <header>
      <h1>{{ $t('summary') }}</h1>
    </header>
    <div class="repo-list">
      <div class="repo-wrapper" v-for="(analysis, index) in analysesData" :key="'repo' + index">
        <div class="container h-100">
          <div class="repo-header">
            <img
              :src="analysis?.repo?.owner.avatar || '@/assets/img/default_avatar.jpg'"
              :alt="`${analysis?.repo?.owner.name}'s avatar`"
            />
            <div>
              <h3>
                {{ analysis?.repo?.name || analysis.data.name + ' (local)' }}
              </h3>
            </div>
          </div>
          <p class="description">
            {{ analysis?.repo?.description || 'No description available' }}
          </p>

          <template v-if="analysis?.repo">
            <p>
              {{ $t('creation_date') }}:
              <span>{{ formatDate(analysis?.repo?.createdAt) }}</span>
            </p>
            <p>
              {{ $t('last_update') }}:
              <span>{{ formatDate(analysis?.repo?.lastUpdatedAt) }}</span>
            </p>
            <!-- <p>
              {{ $t('commits') }}:
              <span>{{ totalCommits(analysis?.repo?.commits) }}</span>
            </p> -->
          </template>

          <a :href="`/repo/${analysis?.name}`" class="glb-btn-main">
            {{ $t('see_more') }}
          </a>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { formatDate } from '@/utils/utils';
import { listAnalysisApiV1AnalysesGet } from '@/client';
import type { AnalysisSummary, Pagination } from '@/client';
/* import axios from 'axios'; */

const analysesData = ref<AnalysisSummary[]>([]);
const pagination = ref<Pagination>({ page: 1, perPage: 10, total: 0 });

async function loadData() {
  const { data, error } = await listAnalysisApiV1AnalysesGet();

  if (error) {
    console.error('Error fetching repos data:', error);
    return;
  }
  analysesData.value = data.elements;
  pagination.value = data.pagination;
}

/* function totalCommits(commits: Array<{ commits: number }>) {
  return commits.reduce((acc, curr) => acc + curr.commits, 0);
} */

onMounted(async () => {
  await loadData();
});
</script>
<style lang="scss" scoped>
.repo-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2em;
}

.repo-list {
  h3 {
    font-weight: 600;
    line-height: 1.75rem;
    margin: 0;
  }

  p:not(.description) {
    font-size: 0.875rem;
    font-weight: bold;
    margin: 0 0 1rem;

    span {
      font-weight: normal;
    }
  }

  a {
    position: absolute;
    right: 1rem;
    bottom: 1rem;
  }
}

p.description {
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  white-space: normal;
  overflow: hidden;
  word-break: break-word;
  text-overflow: ellipsis !important;
  line-height: 1.125rem;
  height: calc(2 * 1.125rem);
  text-overflow: ellipsis;
  font-size: 0.875rem;
  margin: 0 0 1.25rem;
}

.repo-header {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;

  img {
    border-radius: 50%;
    height: 48px;
    width: 48px;
  }
}
</style>
