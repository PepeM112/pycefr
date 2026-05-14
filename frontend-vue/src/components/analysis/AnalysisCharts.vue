<template>
  <div class="analysis-charts w-100">
    <v-row v-if="props.data?.items?.length > 0">
      <v-col v-for="(chart, index) in charts" :key="index" v-bind="chart.grid">
        <chart-container :title="chart.title">
          <component
            :is="chart.component"
            :data="chart.data"
            :options="chart.options"
            v-bind="chart.type ? { type: chart.type } : {}"
          />
        </chart-container>
      </v-col>
    </v-row>

    <v-row v-if="conclusions.length > 0" class="mt-4">
      <v-col cols="12">
        <v-card variant="flat" class="pa-6 insights-box">
          <div class="d-flex align-center mb-4">
            <v-icon class="mr-2">mdi-lightbulb-outline</v-icon>
            <h3 class="text-h6 font-weight-bold mb-0">{{ t('charts.analysis_conclusions') }}</h3>
          </div>

          <v-list class="text-on-surface" density="compact">
            <v-list-item v-for="(insight, index) in conclusions" :key="index" class="px-0 py-2" align-start>
              <template #prepend>
                <v-icon class="mr-n2" size="small">mdi-rhombus-medium</v-icon>
              </template>

              <v-list-item-title class="text-body-1 text-wrap">
                {{ insight }}
              </v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import Enums from '@/utils/enums';
import { ClassId, Level } from '@/client';
import { getLevelColor } from '@/utils/utils';
import type { ChartData } from '@/types/analysis';
import { useThemeStore } from '@/stores/themeStore';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
} from 'chart.js';
import { TreemapController, TreemapElement } from 'chartjs-chart-treemap';
import { Bar, Radar, Doughnut, Pie, Chart } from 'vue-chartjs';
import * as AnalysisChartsUtils from '@/utils/analysisCharts';
import ChartContainer from './ChartContainer.vue';

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  TreemapController,
  TreemapElement
);

const { t } = useI18n();
const themeStore = useThemeStore();

const props = defineProps<{ data: ChartData }>();

const conclusions = computed(() => {
  const items = props.data.items;
  const totalInstances = items.reduce((s, it) => s + it.instances, 0);

  if (totalInstances === 0) return [];

  return [
    AnalysisChartsUtils.getComplexityAbstractionInsight(items, totalInstances),
    AnalysisChartsUtils.getPythonicDensityInsight(items),
    AnalysisChartsUtils.getExceptionHandlingInsight(items),
    AnalysisChartsUtils.getStructuralCompetenceInsight(items),
  ];
});

const themeColors = computed(() => {
  const isDark = themeStore.currentTheme === 'dark';
  return {
    grid: isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)',
    angleLines: isDark ? 'rgba(255, 255, 255, 0.25)' : 'rgba(0, 0, 0, 0.1)',
    textMain: isDark ? '#EEE' : '#333',
    textMuted: isDark ? '#BBB' : '#666',
    pointLabels: isDark ? '#FFFFFF' : '#666666',
  };
});

const baseOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { color: themeColors.value.textMain },
    },
  },
}));

const levelBarOptions = computed(() => ({
  ...baseOptions.value,
  scales: {
    y: {
      beginAtZero: true,
      title: { display: true, text: t('charts.instances'), color: themeColors.value.textMain },
      grid: { color: themeColors.value.grid },
      ticks: { color: themeColors.value.textMuted },
    },
    x: { grid: { display: false }, ticks: { color: themeColors.value.textMuted } },
  },
  plugins: { ...baseOptions.value.plugins, legend: { display: false } },
}));

const radarOptions = computed(() => ({
  ...baseOptions.value,
  scales: {
    r: {
      grid: { color: themeColors.value.grid },
      angleLines: { color: themeColors.value.angleLines },
      pointLabels: { color: themeColors.value.pointLabels, font: { size: 11 } },
      ticks: { display: false },
    },
  },
}));

const horizontalBarOptions = computed(() => ({
  ...baseOptions.value,
  indexAxis: 'y' as const,
  plugins: { ...baseOptions.value.plugins, legend: { display: false } },
  scales: {
    x: { grid: { color: themeColors.value.grid }, ticks: { color: themeColors.value.textMuted } },
    y: { ticks: { color: themeColors.value.textMuted } },
  },
}));

const treemapOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      displayColors: false,
      callbacks: {
        title: (items: any) => {
          const item = items[0].raw;
          return item.g;
        },
        label: (item: any) => {
          return `${t('charts.instances')}: ${item.raw.v}`;
        },
      },
    },
  },
}));

const charts = computed(() => [
  {
    title: 'charts.level_distribution',
    component: Bar,
    data: levelData.value,
    options: levelBarOptions.value,
    grid: { cols: 12, md: 6, lg: 4 },
  },
  {
    title: 'charts.competency_radar',
    component: Radar,
    data: radarData.value,
    options: radarOptions.value,
    grid: { cols: 12, md: 6, lg: 4 },
  },
  {
    title: 'charts.top_patterns',
    component: Bar,
    data: topClassesData.value,
    options: horizontalBarOptions.value,
    grid: { cols: 12, md: 6, lg: 4 },
  },
  {
    title: 'charts.pythonic_ratio',
    component: Doughnut,
    data: pythonicData.value,
    options: baseOptions.value,
    grid: { cols: 12, md: 6, lg: 3 },
  },
  {
    title: 'charts.exception_strategy',
    component: Pie,
    data: exceptionData.value,
    options: baseOptions.value,
    grid: { cols: 12, md: 6, lg: 3 },
  },
  {
    title: 'charts.directory_density_map',
    component: Chart,
    data: treemapData.value,
    options: treemapOptions.value,
    grid: { cols: 12, lg: 6 },
    type: 'treemap',
  },
]);


const levelData = computed(() => {
  const levels = Enums.buildList(Level);
  return {
    labels: levels.map(l => t(l.label)),
    datasets: [
      {
        data: AnalysisChartsUtils.getLevelDistributionStats(props.data.items),
        backgroundColor: levels.map(l => getLevelColor(l.value as Level)),
      },
    ],
  };
});

const radarData = computed(() => {
  const categories = ['logic', 'loops', 'data_structs', 'oop', 'functions'];
  return {
    labels: categories.map(l => t(`categories.${l}`)),
    datasets: [
      {
        label: t('intensity'),
        data: AnalysisChartsUtils.getRadarStats(props.data.items),
        backgroundColor: 'rgba(92, 187, 246, 0.2)',
        borderColor: '#5CBBF6',
        fill: true,
      },
    ],
  };
});

const pythonicData = computed(() => ({
  labels: [t('standard'), t('pythonic')],
  datasets: [
    {
      data: AnalysisChartsUtils.getPythonicStats(props.data.items),
      backgroundColor: ['#9E9E9E', '#4CAF50'],
    },
  ],
}));

const exceptionData = computed(() => ({
  labels: ['Error Catching (Try)', 'Error Signaling (Raise)'],
  datasets: [
    {
      data: AnalysisChartsUtils.getExceptionStats(props.data.items),
      backgroundColor: ['#2196F3', '#FFC107'],
    },
  ],
}));

const topClassesData = computed(() => {
  const top = AnalysisChartsUtils.getTopPatterns(props.data.items);
  return {
    labels: top.map(it => t(Enums.getLabel(ClassId, it.classId))),
    datasets: [{ data: top.map(it => it.instances), backgroundColor: '#5CBBF6' }],
  };
});

const treemapData = computed<any>(() => {
  const flatData = AnalysisChartsUtils.getTreemapFlatData(props.data.files);
  const maxVal = Math.max(...flatData.map(d => d.v), 1);
  const getLogRatio = (v: number) => Math.log(v + 1) / Math.log(maxVal + 1);

  return {
    datasets: [
      {
        tree: flatData,
        key: 'v',
        groups: ['g'],
        spacing: 1,
        borderWidth: 1,
        borderColor: themeStore.currentTheme === 'dark' ? '#1E1E1E' : '#FFFFFF',
        backgroundColor: (ctx: any) => {
          if (!ctx.raw) return '#CCC';
          return AnalysisChartsUtils.getTreemapBackgroundColor(getLogRatio(ctx.raw.v));
        },
        labels: {
          display: true,
          color: (ctx: any) => (getLogRatio(ctx.raw?.v || 0) > 0.45 ? '#FFFFFF' : '#333333'),
          formatter: (ctx: any) => ctx.raw?.g || '',
          font: { size: 12, weight: 'bold' },
        },
      },
    ],
  };
});
</script>

<style scoped>
.chart-container {
  height: 280px;
}
</style>
