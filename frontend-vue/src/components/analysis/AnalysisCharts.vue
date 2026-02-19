<template>
  <div class="analysis-charts w-100">
    <v-row>
      <v-col v-for="(chart, index) in mainCharts" :key="index" cols="12" lg="4" md="6">
        <v-card variant="outlined" class="pa-4 h-100">
          <h3 class="text-subtitle-1 font-weight-bold mb-4">{{ t(chart.title) }}</h3>
          <div class="chart-container">
            <component :is="chart.component" :data="chart.data" :options="chart.options" />
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" lg="3">
        <v-card variant="outlined" class="pa-4 h-100">
          <h3 class="text-subtitle-1 font-weight-bold mb-4">{{ t('charts.pythonic_ratio') }}</h3>
          <div class="chart-container"><Doughnut :data="pythonicData" :options="baseOptions" /></div>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" lg="3">
        <v-card variant="outlined" class="pa-4 h-100">
          <h3 class="text-subtitle-1 font-weight-bold mb-4">{{ t('charts.exception_strategy') }}</h3>
          <div class="chart-container"><Pie :data="exceptionData" :options="baseOptions" /></div>
        </v-card>
      </v-col>

      <v-col cols="6">
        <v-card variant="outlined" class="pa-4 h-100">
          <h3 class="text-subtitle-1 font-weight-bold mb-4">{{ t('charts.directory_density_map') }}</h3>
          <div class="chart-container">
            <component :is="Chart" type="treemap" :data="treemapData" :options="treemapOptions" />
          </div>
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
import { getLevelColor, type ChartData } from '@/components/repo/utils';
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

const mainCharts = computed(() => [
  { title: 'charts.level_distribution', component: Bar, data: levelData.value, options: levelBarOptions.value },
  { title: 'charts.competency_radar', component: Radar, data: radarData.value, options: radarOptions.value },
  { title: 'charts.top_patterns', component: Bar, data: topClassesData.value, options: horizontalBarOptions.value },
]);

const levelData = computed(() => {
  const levels = Enums.buildList(Level);
  return {
    labels: levels.map(l => t(l.label)),
    datasets: [
      {
        data: levels.map(l =>
          props.data.items.filter(it => it.level === l.value).reduce((s, it) => s + it.instances, 0)
        ),
        backgroundColor: levels.map(l => getLevelColor(l.value as Level)),
      },
    ],
  };
});

const radarData = computed(() => {
  const categories: Record<string, ClassId[]> = {
    logic: [ClassId.IF_SIMPLE, ClassId.IF_EXPRESSION],
    loops: [ClassId.LOOP_FOR_SIMPLE, ClassId.LOOP_WHILE_SIMPLE],
    data_structs: [ClassId.LIST_SIMPLE, ClassId.DICT_SIMPLE, ClassId.LISTCOMP_SIMPLE],
    oop: [ClassId.CLASS_SIMPLE, ClassId.CLASS_INHERITED],
    functions: [ClassId.FUNCTIONDEF_SIMPLE, ClassId.LAMBDA_SIMPLE],
  };
  const labels = Object.keys(categories);
  return {
    labels: labels.map(l => t(`categories.${l}`)),
    datasets: [
      {
        label: t('intensity'),
        data: labels.map(cat =>
          props.data.items.filter(it => categories[cat].includes(it.class)).reduce((s, it) => s + it.instances, 0)
        ),
        backgroundColor: 'rgba(92, 187, 246, 0.2)',
        borderColor: '#5CBBF6',
        fill: true,
      },
    ],
  };
});

const pythonicData = computed(() => {
  const py = [ClassId.LISTCOMP_SIMPLE, ClassId.DICTCOMP_SIMPLE, ClassId.LAMBDA_SIMPLE, ClassId.WITH_SIMPLE];
  const pyCount = props.data.items.filter(it => py.includes(it.class)).reduce((s, it) => s + it.instances, 0);
  const total = props.data.items.reduce((s, it) => s + it.instances, 0);
  return {
    labels: [t('standard'), t('pythonic')],
    datasets: [{ data: [total - pyCount, pyCount], backgroundColor: ['#9E9E9E', '#4CAF50'] }],
  };
});

const exceptionData = computed(() => {
  const basic = [ClassId.EXCEPTION_TRY_EXCEPT, ClassId.EXCEPTION_RAISE];
  const robust = [ClassId.EXCEPTION_TRY_EXCEPT_ELSE_FINALLY, ClassId.EXCEPTION_ASSERT];
  return {
    labels: [t('basic_handling'), t('robust_handling')],
    datasets: [
      {
        data: [
          props.data.items.filter(it => basic.includes(it.class)).reduce((s, it) => s + it.instances, 0),
          props.data.items.filter(it => robust.includes(it.class)).reduce((s, it) => s + it.instances, 0),
        ],
        backgroundColor: ['#FFC107', '#2196F3'],
      },
    ],
  };
});

const topClassesData = computed(() => {
  const top = [...props.data.items].sort((a, b) => b.instances - a.instances).slice(0, 10);
  return {
    labels: top.map(it => t(Enums.getLabel(ClassId, it.class))),
    datasets: [{ data: top.map(it => it.instances), backgroundColor: '#5CBBF6' }],
  };
});

const treemapData = computed<any>(() => {
  const groups: Record<string, number> = {};

  props.data.files.forEach(f => {
    const parts = f.fullPath.split('/');
    const folder = parts.length > 1 ? '/' + parts.slice(0, -1).join('/') : '/';
    groups[folder] = (groups[folder] || 0) + f.instances;
  });

  const flatData = Object.entries(groups).map(([name, value]) => ({
    g: name,
    v: value,
  }));

  const maxVal = Math.max(...flatData.map(d => d.v), 1);

  const getLogRatio = (v: number) => {
    return Math.log(v + 1) / Math.log(maxVal + 1);
  };

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

          const ratio = getLogRatio(ctx.raw.v);

          if (ratio > 0.85) return '#BF360C';
          if (ratio > 0.65) return '#E64A19';
          if (ratio > 0.45) return '#FF8A65';
          if (ratio > 0.25) return '#FFAB91';
          return '#FFCCBC';
        },
        labels: {
          display: true,
          color: (ctx: any) => {
            const ratio = getLogRatio(ctx.raw?.v || 0);
            return ratio > 0.45 ? '#FFFFFF' : '#333333';
          },
          formatter: (ctx: any) => {
            if (!ctx.raw) return '';
            return ctx.raw.g;
          },
          font: {
            size: 12,
            weight: 'bold',
          },
        },
      },
    ],
  };
});
</script>

<style scoped>
.chart-container {
  height: 280px;
  position: relative;
}
</style>
