<template>
  <v-dialog v-model="localModel" :width="480" :close-on-content-click="false" @keydown.esc="handleClose">
    <v-card rounded="lg" min-height="200">
      <!-- FORM VIEW -->
      <template v-if="!isRunning && !isTerminal">
        <v-card-title class="py-3">
          <span class="font-weight-bold text-h5">{{ $t('new_analysis') }}</span>
        </v-card-title>
        <v-divider />
        <v-card-text class="px-4">
          <v-form v-model="isFormValid" class="d-flex flex-column ga-4">
            <g-input label="analysis_name">
              <v-text-field v-model="form.name" />
            </g-input>
            <g-input label="repository_url" required>
              <v-text-field v-model="form.repoUrl" :rules="[rules.required, rules.url]" />
            </g-input>
            <v-checkbox v-model="form.includeGit" :label="$t('include_git_analysis')" density="compact" hide-details color="primary-on-surface" />
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-btn variant="tonal" @click="handleClose">{{ $t('cancel') }}</v-btn>
          <v-btn color="primary-on-surface" variant="flat" :disabled="!isFormValid" @click="handleSubmit">
            {{ $t('apply') }}
          </v-btn>
        </v-card-actions>
      </template>

      <!-- PROGRESS VIEW -->
      <template v-else>
        <v-card-title class="d-flex align-center py-3">
          <span class="font-weight-bold text-h5 flex-grow-1">{{ progressTitle }}</span>
          <v-btn icon="mdi-close" variant="text" density="comfortable" @click="handleClose" />
        </v-card-title>
        <v-divider />
        <v-card-text class="px-4 py-5">
          <div class="d-flex flex-column">
            <analysis-step-row
              v-for="(step, index) in visibleSteps"
              :key="step.key"
              :label="$t(step.labelKey)"
              :state="step.state"
              :connector-state="step.connectorState"
              :detail="step.detail"
              :is-last="index === visibleSteps.length - 1"
            />
          </div>
        </v-card-text>
        <template v-if="isCompleted">
          <v-divider />
          <v-card-actions>
            <v-btn color="primary-on-surface" variant="flat" @click="handleViewResults">
              {{ $t('view_results') }}
            </v-btn>
          </v-card-actions>
        </template>
      </template>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { type AnalysisPublic, createAnalysis } from '@/client';
import GInput from '@/components/GInput.vue';
import AnalysisStepRow from '@/components/analysis/AnalysisStepRow.vue';
import { type AnalysisStep, useAnalysisProgress } from '@/composables/analysis/useAnalysisProgress';
import { useRules } from '@/composables/useRules';
import { useSnackbarStore } from '@/stores/snackbarStore';
import { RouteNames } from '@/router/route-names';
import { useI18n } from 'vue-i18n';

type StepState = 'pending' | 'active' | 'completed' | 'failed' | 'skipped';

type StepDef = {
  key: string;
  labelKey: string;
  state: StepState;
  connectorState: StepState;
  detail?: string;
};

type Props = {
  modelValue: boolean;
  reconnectAnalysisId?: number | null;
  reconnectAnalysisName?: string;
};

const INCLUDE_GIT_STORAGE_KEY = 'pycefr_include_git';

const props = withDefaults(defineProps<Props>(), {
  reconnectAnalysisId: null,
  reconnectAnalysisName: undefined,
});

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  created: [analysis: AnalysisPublic];
  completed: [];
}>();

const rules = useRules();
const snackbarStore = useSnackbarStore();
const router = useRouter();
const { t } = useI18n();

const { currentStep, fileCurrent, fileTotal, errorMessage, isTerminal, completedAnalysisId, connect, disconnect } =
  useAnalysisProgress();

const isFormValid = ref(false);
const isRunning = ref(false);
const activeAnalysisId = ref<number | null>(null);

const storedIncludeGit = localStorage.getItem(INCLUDE_GIT_STORAGE_KEY);
const form = ref({
  name: '',
  repoUrl: '',
  includeGit: storedIncludeGit === null ? true : storedIncludeGit === 'true',
});

const localModel = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const isCompleted = computed(() => currentStep.value === 'COMPLETED');
const isFailed = computed(() => currentStep.value === 'FAILED');

const progressTitle = computed(() => {
  if (isCompleted.value) return t('analysis_completed');
  if (isFailed.value) return t('analysis_failed');
  return t('analysis_in_progress');
});

const STEP_ORDER: AnalysisStep[] = ['VALIDATING', 'CLONING', 'ANALYSING', 'GIT_ANALYSIS', 'SAVING'];

const STEP_LABELS: Record<string, string> = {
  VALIDATING: 'step_validating',
  CLONING: 'step_cloning',
  ANALYSING: 'step_analysing',
  GIT_ANALYSIS: 'step_git_analysis',
  SAVING: 'step_saving',
};

function getStepState(stepKey: string): StepState {
  const step = currentStep.value;
  if (!step) return 'pending';

  if (step === 'FAILED') {
    const failedIndex = STEP_ORDER.indexOf(lastActiveStep.value);
    const thisIndex = STEP_ORDER.indexOf(stepKey as AnalysisStep);
    if (thisIndex < failedIndex) return 'completed';
    if (thisIndex === failedIndex) return 'failed';
    return 'pending';
  }

  if (step === 'COMPLETED') return 'completed';

  const currentIndex = STEP_ORDER.indexOf(step);
  const thisIndex = STEP_ORDER.indexOf(stepKey as AnalysisStep);

  if (thisIndex < currentIndex) return 'completed';
  if (thisIndex === currentIndex) return 'active';
  return 'pending';
}

const lastActiveStep = ref<AnalysisStep>('VALIDATING');
watch(currentStep, newStep => {
  if (newStep && STEP_ORDER.includes(newStep)) {
    lastActiveStep.value = newStep;
  }
});

const visibleSteps = computed<StepDef[]>(() => {
  const shouldShowGit = form.value.includeGit;
  const keys = STEP_ORDER.filter(key => key !== 'GIT_ANALYSIS' || shouldShowGit);

  return keys.map((key, index) => {
    const state = getStepState(key);
    const nextState = index < keys.length - 1 ? getStepState(keys[index + 1]) : 'pending';
    let detail: string | undefined;

    if (key === 'ANALYSING' && state === 'active' && fileTotal.value > 0) {
      // x1.35 to prevent jump from ~75% to 100%
      detail = `${Math.min(Math.round((fileCurrent.value / fileTotal.value) * 100 * 1.35), 100)}%`;
    }
    if (state === 'failed' && errorMessage.value) {
      detail = errorMessage.value;
    }

    return { key, labelKey: STEP_LABELS[key], state, connectorState: nextState, detail };
  });
});

async function handleSubmit() {
  localStorage.setItem(INCLUDE_GIT_STORAGE_KEY, String(form.value.includeGit));

  const { data, error } = await createAnalysis({
    body: {
      name: form.value.name || undefined,
      repoUrl: form.value.repoUrl,
      includeGit: form.value.includeGit,
    },
  });

  if (error || !data) {
    snackbarStore.add({
      text: 'error.creating.analysis',
      color: 'error',
      icon: 'mdi-alert-circle-outline',
      closable: true,
    });
    return;
  }

  activeAnalysisId.value = data.id;
  isRunning.value = true;
  emit('created', data);
  connect(data.id);
}

function handleClose() {
  disconnect();
  resetState();
  localModel.value = false;
}

function handleViewResults() {
  const id = completedAnalysisId.value ?? activeAnalysisId.value;
  resetState();
  localModel.value = false;
  if (id) {
    router.push({ name: RouteNames.ANALYSIS_DETAIL, params: { id } });
  }
}

function resetState() {
  isRunning.value = false;
  activeAnalysisId.value = null;
  form.value.name = '';
  form.value.repoUrl = '';
}

watch(
  () => props.reconnectAnalysisId,
  newId => {
    if (newId && props.modelValue) {
      activeAnalysisId.value = newId;
      isRunning.value = true;
      connect(newId);
    }
  },
);

watch(
  () => props.modelValue,
  isOpen => {
    if (isOpen && props.reconnectAnalysisId) {
      activeAnalysisId.value = props.reconnectAnalysisId;
      isRunning.value = true;
      connect(props.reconnectAnalysisId);
    }
  },
);

watch(isTerminal, isTerminalNow => {
  if (isTerminalNow && isCompleted.value) {
    emit('completed');
  }
});
</script>
