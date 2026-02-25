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

      <v-col cols="12" lg="6">
        <v-card variant="outlined" class="pa-4 h-100">
          <h3 class="text-subtitle-1 font-weight-bold mb-4">{{ t('charts.directory_density_map') }}</h3>
          <div class="chart-container">
            <component :is="Chart" type="treemap" :data="treemapData" :options="treemapOptions" />
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12">
        <v-card variant="flat" class="pa-6 insights-box">
          <div class="d-flex align-center mb-4">
            <v-icon color="primary" class="mr-2">mdi-lightbulb-outline</v-icon>
            <h3 class="text-h6 font-weight-bold mb-0">{{ t('charts.analysis_conclusions') }}</h3>
          </div>

          <div class="insights-content">
            <p v-for="(insight, index) in conclusions" :key="index" class="text-body-1 mb-3 d-flex align-start">
              <span class="mr-2 mt-1">•</span>
              <span>{{ insight }}</span>
            </p>

            <v-alert v-if="conclusions.length === 0" type="info" variant="tonal" density="compact">
              {{ t('charts.no_significant_insights') }}
            </v-alert>
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
  const list: string[] = [];
  const items = props.data.items;
  const totalInstances = items.reduce((s, it) => s + it.instances, 0);

  if (totalInstances === 0) return [];

  // --- 1. Complexity & Abstraction Insight ---
  // Un 1% de C1/C2 ya indica que hay metaprogramación, decoradores o generadores.
  const advancedCount = items
    .filter(it => it.level === Level.C1 || it.level === Level.C2)
    .reduce((s, it) => s + it.instances, 0);

  const advancedRatio = (advancedCount / totalInstances) * 100;

  if (advancedRatio >= 1.5) {
    list.push(
      `High Abstraction Layer: Advanced features (C1/C2) represent ${advancedRatio.toFixed(2)}% of the structural code, indicating extensive use of metaprogramming, complex decorators, or generators typical of framework-level architecture.`
    );
  } else if (advancedRatio >= 0.5) {
    list.push(
      `Professional Codebase: Moderate use of advanced features (${advancedRatio.toFixed(2)}%). The architecture relies on solid OOP and functional patterns without excessive metaprogramming.`
    );
  } else {
    list.push(
      `Standard Complexity: The codebase is predominantly structural (A1-B2). It favors straightforward execution flow over deep abstractions.`
    );
  }

  // --- 2. Pythonic Density Insight ---
  // Comparamos comprensiones y lambdas directamente contra los bucles FOR tradicionales.
  const pyCount = items
    .filter(it =>
      [ClassId.LISTCOMP_SIMPLE, ClassId.DICTCOMP_SIMPLE, ClassId.WITH_SIMPLE, ClassId.LAMBDA_SIMPLE].includes(
        it.classId
      )
    )
    .reduce((s, it) => s + it.instances, 0);

  const forLoopsCount = items
    .filter(it => [ClassId.LOOP_FOR_SIMPLE, ClassId.LOOP_FOR_NESTED].includes(it.classId))
    .reduce((s, it) => s + it.instances, 0);

  // Evitamos división por cero.
  const idiomRatio = forLoopsCount > 0 ? pyCount / forLoopsCount : 0;

  if (idiomRatio > 0.8) {
    list.push(
      `Highly Idiomatic: Strong preference for Pythonic constructs. For every traditional for-loop, there are nearly as many (or more) comprehensions, context managers, and functional elements.`
    );
  } else if (idiomRatio > 0.3) {
    list.push(
      `Balanced Idioms: The codebase mixes traditional iterative loops with Pythonic constructs like comprehensions appropriately.`
    );
  } else {
    list.push(
      `Imperative Style: The code relies heavily on traditional iterative loops and standard assignments rather than Pythonic shorthands.`
    );
  }

  // --- 3. Exception Handling Insight ---
  // Evaluamos la "Densidad de Excepciones": Cuánto control de errores hay respecto a las funciones definidas.
  const exceptionBlocks = items
    .filter(it =>
      [ClassId.EXCEPTION_TRY_EXCEPT, ClassId.EXCEPTION_TRY_FINALLY, ClassId.EXCEPTION_TRY_EXCEPT_ELSE_FINALLY].includes(
        it.classId
      )
    )
    .reduce((s, it) => s + it.instances, 0);

  const functionDefs = items
    .filter(it => [ClassId.FUNCTIONDEF_SIMPLE, ClassId.FUNCTIONDEF_RECURSIVE].includes(it.classId))
    .reduce((s, it) => s + it.instances, 0);

  const errorHandlingDensity = functionDefs > 0 ? exceptionBlocks / functionDefs : 0;

  if (errorHandlingDensity > 0.4) {
    list.push(
      `Defensive Programming: High density of error handling. Almost half of the functions are protected by explicit try-except blocks.`
    );
  } else if (errorHandlingDensity > 0.1) {
    list.push(
      `Standard Error Handling: Exceptions are caught at strategic points rather than wrapping every minor operation.`
    );
  } else {
    list.push(
      `Optimistic Execution: Very sparse explicit error handling. The system likely relies on a global exception handler or middleware to catch unhandled errors.`
    );
  }

  // --- 4. Structural Competence (Radar Focus) ---
  // Vemos cuál es la categoría predominante en el radar
  const oopCount = items
    .filter(it =>
      [ClassId.CLASS_SIMPLE, ClassId.CLASS_INHERITED, ClassId.CLASS_INIT, ClassId.CLASS_PROPERTIES].includes(it.classId)
    )
    .reduce((s, it) => s + it.instances, 0);

  const logicCount = items
    .filter(it => [ClassId.IF_SIMPLE, ClassId.IF_EXPRESSION, ClassId.LOOP_WHILE_SIMPLE].includes(it.classId))
    .reduce((s, it) => s + it.instances, 0);

  if (oopCount > logicCount * 0.5) {
    list.push(
      `Object-Oriented Focus: Heavy reliance on classes, encapsulation, and inheritance to structure the application logic.`
    );
  } else {
    list.push(
      `Procedural/Logic Focus: The application structure is driven primarily by conditional logic and standalone functions rather than heavy class hierarchies.`
    );
  }

  return list;
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
          props.data.items.filter(it => categories[cat].includes(it.classId)).reduce((s, it) => s + it.instances, 0)
        ),
        backgroundColor: 'rgba(92, 187, 246, 0.2)',
        borderColor: '#5CBBF6',
        fill: true,
      },
    ],
  };
});

const pythonicData = computed(() => {
  const pyClasses = [ClassId.LISTCOMP_SIMPLE, ClassId.DICTCOMP_SIMPLE, ClassId.LAMBDA_SIMPLE, ClassId.WITH_SIMPLE];
  const standardClasses = [ClassId.LOOP_FOR_SIMPLE, ClassId.LOOP_FOR_NESTED, ClassId.IF_SIMPLE, ClassId.FILE_OPEN];

  const pyCount = props.data.items.filter(it => pyClasses.includes(it.classId)).reduce((s, it) => s + it.instances, 0);
  const stdCount = props.data.items
    .filter(it => standardClasses.includes(it.classId))
    .reduce((s, it) => s + it.instances, 0);

  return {
    labels: [t('standard'), t('pythonic')],
    datasets: [{ data: [stdCount, pyCount], backgroundColor: ['#9E9E9E', '#4CAF50'] }],
  };
});

const exceptionData = computed(() => {
  // Gestión Activa: El código intenta solucionar el problema (Catch)
  const catching = [
    ClassId.EXCEPTION_TRY_EXCEPT,
    ClassId.EXCEPTION_TRY_EXCEPT_ELSE_FINALLY,
    ClassId.EXCEPTION_TRY_FINALLY,
  ];

  // Gestión de Señalización: El código avisa de un error (Raise/Assert)
  const signaling = [ClassId.EXCEPTION_RAISE, ClassId.EXCEPTION_ASSERT];

  const catchingCount = props.data.items
    .filter(it => catching.includes(it.classId))
    .reduce((s, it) => s + it.instances, 0);

  const signalingCount = props.data.items
    .filter(it => signaling.includes(it.classId))
    .reduce((s, it) => s + it.instances, 0);

  return {
    labels: ['Error Catching (Try)', 'Error Signaling (Raise)'],
    datasets: [
      {
        data: [catchingCount, signalingCount],
        backgroundColor: ['#2196F3', '#FFC107'],
      },
    ],
  };
});

const topClassesData = computed(() => {
  const top = [...props.data.items].sort((a, b) => b.instances - a.instances).slice(0, 10);
  return {
    labels: top.map(it => t(Enums.getLabel(ClassId, it.classId))),
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

.insights-box {
  background-color: rgba(var(--v-theme-primary), 0.05) !important;
  border: 1px dashed rgb(var(--v-theme-primary));
  border-radius: 12px;
}

.insights-content {
  color: rgb(var(--v-theme-on-surface));
  line-height: 1.6;
}
</style>
