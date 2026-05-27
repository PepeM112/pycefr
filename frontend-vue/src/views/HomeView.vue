<template>
  <page-view :header="$t('dashboard.title')">
    <generic-loader :model-value="loadingStatus">
      <v-row class="mb-2">
        <v-col v-for="card in statCards" :key="card.label" cols="6" sm="3">
          <v-card variant="outlined" class="pa-4 text-center">
            <p class="text-h4 font-weight-bold" :class="card.color">{{ card.value }}</p>
            <p class="text-body-2 text-medium-emphasis">{{ $t(card.label) }}</p>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" md="6">
          <chart-container :title="'charts.level_distribution'">
            <template v-if="hasLevelData">
              <bar :data="levelChartData" :options="barOptions" />
            </template>
            <div v-else class="d-flex justify-center align-center flex-column h-100" style="color: #9d9d9d">
              <v-icon class="mb-1" size="40">mdi-chart-arc</v-icon>
              <p class="text-grey text-body-2">{{ $t('no_data') }}</p>
            </div>
          </chart-container>
        </v-col>
        <v-col cols="12" md="6">
          <chart-container :title="'dashboard.top_constructs'">
            <template v-if="stats?.topConstructs?.length">
              <bar :data="topConstructsData" :options="horizontalBarOptions" />
            </template>
            <div v-else class="d-flex justify-center align-center flex-column h-100" style="color: #9d9d9d">
              <v-icon class="mb-1" size="40">mdi-chart-arc</v-icon>
              <p class="text-grey text-body-2">{{ $t('no_data') }}</p>
            </div>
          </chart-container>
        </v-col>
      </v-row>

      <v-row class="mt-2">
        <v-col cols="12">
          <v-card variant="outlined" class="pa-4">
            <h3 class="text-subtitle-1 font-weight-bold mb-3">{{ $t('dashboard.recent_analyses') }}</h3>
            <v-table v-if="stats?.recentAnalyses?.length" density="comfortable">
              <thead>
                <tr>
                  <th>{{ $t('name') }}</th>
                  <th>{{ $t('status') }}</th>
                  <th>{{ $t('date') }}</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in stats.recentAnalyses" :key="item.id">
                  <td>{{ item.repoName }}</td>
                  <td>
                    <span class="status-badge" :class="`bg-${getStatusColor(item.status as AnalysisStatus)}`">
                      {{ $t(item.status) }}
                    </span>
                  </td>
                  <td><g-date :date="item.createdAt" is-relative /></td>
                  <td class="text-right">
                    <v-btn
                      v-if="item.status === AnalysisStatus.COMPLETED"
                      density="comfortable"
                      icon="mdi-eye-outline"
                      variant="text"
                      :to="{ name: RouteNames.ANALYSIS_DETAIL, params: { id: item.id } }"
                    />
                  </td>
                </tr>
              </tbody>
            </v-table>
            <p v-else class="text-medium-emphasis text-body-2">{{ $t('no_data') }}</p>
          </v-card>
        </v-col>
      </v-row>
    </generic-loader>
  </page-view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
import { Bar } from 'vue-chartjs';
import { AnalysisStatus, getDashboardStats, Level, type DashboardStats } from '@/client';
import ChartContainer from '@/components/analysis/ChartContainer.vue';
import GDate from '@/components/GDate.vue';
import GenericLoader from '@/components/GenericLoader.vue';
import PageView from '@/components/PageView.vue';
import { RouteNames } from '@/router/route-names';
import { useSnackbarStore } from '@/stores/snackbarStore';
import { useThemeStore } from '@/stores/themeStore';
import { LoadingStatus } from '@/types/loading';
import { getLevelColor, getStatusColor } from '@/utils/utils';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const { t } = useI18n();
const snackbarStore = useSnackbarStore();
const themeStore = useThemeStore();

const stats = ref<DashboardStats | null>(null);
const loadingStatus = ref<LoadingStatus>(LoadingStatus.IDLE);

const statCards = computed(() => [
  { label: 'dashboard.total', value: stats.value?.totalAnalyses ?? 0, color: '' },
  { label: 'completed', value: stats.value?.completed ?? 0, color: 'text-success' },
  { label: 'failed', value: stats.value?.failed ?? 0, color: 'text-error' },
  { label: 'in_progress', value: stats.value?.inProgress ?? 0, color: 'text-warning' },
]);

const themeColors = computed(() => {
  const isDark = themeStore.currentTheme === 'dark';
  return {
    grid: isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)',
    textMuted: isDark ? '#BBB' : '#666',
  };
});

const barOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: themeColors.value.grid },
      ticks: { color: themeColors.value.textMuted },
    },
    x: { grid: { display: false }, ticks: { color: themeColors.value.textMuted } },
  },
}));

const horizontalBarOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y' as const,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { color: themeColors.value.grid }, ticks: { color: themeColors.value.textMuted } },
    y: { ticks: { color: themeColors.value.textMuted, font: { size: 11 } } },
  },
}));

const LEVEL_ORDER = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] as const;

const LEVEL_TO_ENUM: Record<string, Level> = {
  A1: Level.A1,
  A2: Level.A2,
  B1: Level.B1,
  B2: Level.B2,
  C1: Level.C1,
  C2: Level.C2,
};

const hasLevelData = computed(() => {
  if (!stats.value?.levelDistribution) return false;
  return Object.values(stats.value.levelDistribution).some(v => v > 0);
});

const levelChartData = computed(() => ({
  labels: [...LEVEL_ORDER],
  datasets: [
    {
      data: LEVEL_ORDER.map(l => stats.value?.levelDistribution?.[l] ?? 0),
      backgroundColor: LEVEL_ORDER.map(l => getLevelColor(LEVEL_TO_ENUM[l])),
    },
  ],
}));

const topConstructsData = computed(() => {
  const constructs = stats.value?.topConstructs ?? [];
  return {
    labels: constructs.map(c => t(`analysis_rules.${c.name}`)),
    datasets: [
      {
        data: constructs.map(c => c.count),
        backgroundColor: constructs.map(c => getLevelColor(LEVEL_TO_ENUM[c.level] ?? Level.UNKNOWN)),
      },
    ],
  };
});

async function loadData() {
  loadingStatus.value = LoadingStatus.LOADING;
  const { data, error } = await getDashboardStats();

  if (error || !data) {
    snackbarStore.add({
      text: 'error.fetching.summary',
      color: 'error',
      icon: 'mdi-alert-circle-outline',
      closable: true,
    });
    loadingStatus.value = LoadingStatus.ERROR;
    return;
  }

  stats.value = data;
  loadingStatus.value = data.totalAnalyses === 0 ? LoadingStatus.EMPTY : LoadingStatus.IDLE;
}

onMounted(loadData);
</script>

<style lang="scss" scoped>
.status-badge {
  font-size: 0.75rem;
  border-radius: 1rem;
  padding: 2px 8px;
}
</style>
