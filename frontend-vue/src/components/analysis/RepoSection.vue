<template>
  <div v-if="repo" class="repo-section">
    <div class="repo-header">
      <div class="repo-header-left">
        <v-avatar size="48">
          <v-img :src="repo.owner?.avatar || defaultAvatar" alt="Owner avatar" />
        </v-avatar>
        <div class="repo-header-info">
          <h3 class="text-subtitle-1 font-weight-bold mb-0">
            <a v-if="repo.owner?.profileUrl" :href="repo.owner.profileUrl" target="_blank" rel="noopener" class="repo-link">
              {{ repo.owner.githubUser }}
            </a>
            <span v-if="repo.owner?.profileUrl && repo.url" class="mx-1">/</span>
            <a v-if="repo.url" :href="repo.url" target="_blank" rel="noopener" class="repo-link">
              {{ repo.name }}
            </a>
            <span v-else>{{ repo.name }}</span>
          </h3>
          <p v-if="repo.description" class="text-body-2 text-medium-emphasis mb-0">{{ repo.description }}</p>
        </div>
      </div>
      <div class="repo-stats">
        <div class="repo-stat">
          <v-icon size="18" class="mr-1">mdi-account-group-outline</v-icon>
          <span class="font-weight-bold">{{ allRows.length }}</span>
          <span class="text-medium-emphasis ml-1">{{ $t('repo.contributors') }}</span>
        </div>
        <v-divider vertical class="mx-3" />
        <div class="repo-stat">
          <v-icon size="18" class="mr-1">mdi-source-commit</v-icon>
          <span class="font-weight-bold">{{ totalCommits }}</span>
          <span class="text-medium-emphasis ml-1">{{ $t('commits') }}</span>
        </div>
        <v-divider vertical class="mx-3" />
        <div class="repo-stat">
          <v-icon size="18" class="mr-1">mdi-clock-outline</v-icon>
          <span class="font-weight-bold">{{ totalHours }}</span>
          <span class="text-medium-emphasis ml-1">{{ $t('repo.estimated_hours') }}</span>
        </div>
        <v-divider vertical class="mx-3" />
        <div class="repo-stat">
          <v-icon size="18" class="mr-1">mdi-calendar-range</v-icon>
          <g-date :date="repo.createdAt" />
          <span class="mx-1">—</span>
          <g-date :date="repo.lastUpdatedAt" />
        </div>
      </div>
    </div>

    <v-divider class="my-5" />

    <div class="d-flex align-center justify-space-between mb-4">
      <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ $t('repo.contributors') }}</h3>
      <v-text-field
        v-model="search"
        class="bg-background rounded-lg"
        density="compact"
        variant="outlined"
        :placeholder="$t('repo.search_contributors')"
        append-inner-icon="mdi-magnify"
        hide-details
        max-width="240"
        clearable
      />
    </div>

    <div class="contributors-list">
      <div v-for="row in visibleRows" :key="row.githubUser" class="contributor-row">
        <div class="contributor-identity">
          <v-avatar size="36">
            <v-img :src="row.avatar" :alt="row.githubUser">
              <template #error>
                <v-img :src="defaultAvatar" />
              </template>
            </v-img>
          </v-avatar>
          <a :href="row.profileUrl" target="_blank" rel="noopener" class="repo-link font-weight-medium">
            {{ row.githubUser }}
          </a>
        </div>
        <div class="contributor-stats">
          <div class="contributor-stat">
            <span class="text-medium-emphasis">{{ $t('commits') }}</span>
            <span class="font-weight-bold">{{ row.commits }}</span>
          </div>
          <div class="contributor-stat">
            <span class="text-medium-emphasis">{{ $t('repo.lines_of_code') }}</span>
            <span class="font-weight-bold">{{ row.loc.toLocaleString() }}</span>
          </div>
          <div class="contributor-stat">
            <span class="text-medium-emphasis">{{ $t('repo.files_modified') }}</span>
            <span class="font-weight-bold">{{ row.totalFilesModified }}</span>
          </div>
          <div class="contributor-stat">
            <span class="text-medium-emphasis">{{ $t('repo.estimated_hours') }}</span>
            <span class="font-weight-bold">{{ row.estimatedHours.toFixed(1) }}h</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="hasMore" class="d-flex justify-center mt-4">
      <v-btn variant="tonal" @click="showMore">
        {{ $t('repo.view_more') }}
      </v-btn>
    </div>

    <p v-if="filteredRows.length === 0 && search" class="text-center text-medium-emphasis mt-4">
      {{ $t('no_data') }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import type { RepoPublic, RepoCommitPublic } from '@/client';
import defaultAvatar from '@/assets/img/default_avatar.jpg';
import GDate from '@/components/GDate.vue';

const INITIAL_SIZE = 10;
const BATCH_SIZE = 20;

type ContributorRow = {
  avatar: string;
  githubUser: string;
  profileUrl: string;
  commits: number;
  loc: number;
  totalFilesModified: number;
  estimatedHours: number;
};

const props = defineProps<{
  repo: RepoPublic;
}>();

const search = ref('');
const displayCount = ref(INITIAL_SIZE);

const contributors = computed(() => props.repo.contributors ?? []);
const commits = computed(() => props.repo.commits ?? []);

const sanitizeGitHubUser = (value: string) => value.replaceAll(' ', '');

const commitsByUser = computed(() => {
  const map = new Map<string, RepoCommitPublic>();
  commits.value.forEach(c => map.set(sanitizeGitHubUser(c.githubUser), c));
  return map;
});

const allRows = computed<ContributorRow[]>(() =>
  contributors.value.map(contributor => {
    const cleanUser = sanitizeGitHubUser(contributor.githubUser);
    const commitData = commitsByUser.value.get(cleanUser);
    return {
      avatar: contributor.avatar.replaceAll(' ', ''),
      githubUser: cleanUser,
      profileUrl: contributor.profileUrl.replaceAll(' ', ''),
      commits: commitData?.commits ?? contributor.contributions,
      loc: commitData?.loc ?? 0,
      totalFilesModified: commitData?.totalFilesModified ?? 0,
      estimatedHours: commitData?.estimatedHours ?? 0,
    };
  }),
);

const filteredRows = computed(() => {
  const query = search.value?.trim().toLowerCase();
  if (!query) return allRows.value;
  return allRows.value.filter(row => row.githubUser.toLowerCase().includes(query));
});

const visibleRows = computed(() => filteredRows.value.slice(0, displayCount.value));
const hasMore = computed(() => displayCount.value < filteredRows.value.length);

function showMore() {
  displayCount.value += BATCH_SIZE;
}

watch(search, () => {
  displayCount.value = INITIAL_SIZE;
});

const totalCommits = computed(() =>
  allRows.value.reduce((sum, row) => sum + row.commits, 0),
);

const totalHours = computed(() =>
  allRows.value.reduce((sum, row) => sum + row.estimatedHours, 0).toFixed(1),
);
</script>

<style lang="scss" scoped>
.repo-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;

  &-left {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  &-info {
    display: flex;
    flex-direction: column;
  }
}

.repo-stats {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.repo-stat {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  white-space: nowrap;
}

.repo-link {
  text-decoration: none;
  color: inherit;

  &:hover {
    text-decoration: underline;
    opacity: 0.8;
  }
}

.contributors-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.contributor-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.625rem 1rem;
  border-radius: 8px;
  background: rgba(var(--v-theme-on-surface), 0.03);
  gap: 1rem;
}

.contributor-identity {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
  flex-shrink: 1;
}

.contributor-stats {
  display: flex;
  gap: 1.5rem;
  flex-shrink: 0;
}

.contributor-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 0.8125rem;
  min-width: 5rem;
}
</style>
