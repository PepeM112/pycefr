<template>
  <v-dialog v-model="localModel" :width="560" @keydown.esc="handleClose">
    <v-card rounded="lg">
      <v-card-title class="py-3">
        <span class="font-weight-bold text-h5">{{ $t('bulk_analysis.title') }}</span>
      </v-card-title>
      <v-divider />
      <v-card-text class="px-4">
        <div class="d-flex flex-column ga-4">
          <div>
            <div class="d-flex align-center justify-space-between mb-1">
              <span class="text-body-2 font-weight-medium">{{ $t('bulk_analysis.urls_label') }}</span>
              <v-tooltip location="top">
                <template #activator="{ props: tooltipProps }">
                  <span v-bind="tooltipProps" class="text-caption" :class="slotsTextColor">
                    {{ $t('bulk_analysis.slots_info', { used: inProgressCount, max: MAX_CONCURRENT }) }}
                  </span>
                </template>
                <span>{{ $t('bulk_analysis.slots_tooltip') }}</span>
              </v-tooltip>
            </div>
            <v-combobox
              v-model="urls"
              :disabled="isInputDisabled && urls.length === 0"
              :placeholder="isInputDisabled ? $t('bulk_analysis.no_slots') : $t('bulk_analysis.url_placeholder')"
              variant="outlined"
              density="compact"
              multiple
              chips
              closable-chips
              hide-details
              hide-no-data
              :items="[]"
              :error-messages="inputError ? [inputError] : []"
              @update:model-value="handleUrlsChange"
              @paste="handlePaste"
            >
              <template #chip="{ item, props: chipProps }">
                <v-chip
                  v-bind="chipProps"
                  label
                  variant="flat"
                  color="primary-on-surface"
                  @click.stop="openRepo(item.value)"
                >
                  <template #prepend>
                    <v-icon size="14" class="mr-2" icon="iconify:simple-icons:github" />
                  </template>
                  {{ extractRepoName(item.value) }}
                </v-chip>
              </template>
            </v-combobox>
          </div>

          <g-input label="tags">
            <v-combobox
              v-model="form.tags"
              :items="availableTags"
              multiple
              variant="outlined"
              density="compact"
              chips
              closable-chips
              hide-details
              :hide-no-data="false"
            >
              <template #item="{ props: itemProps }">
                <v-list-item v-bind="itemProps" :prepend-icon="undefined" />
              </template>
            </v-combobox>
          </g-input>

          <v-checkbox
            v-model="form.includeGit"
            :label="$t('include_git_analysis')"
            density="compact"
            hide-details
            color="primary-on-surface"
          />
        </div>
      </v-card-text>
      <v-divider />
      <v-card-actions>
        <v-btn variant="tonal" @click="handleClose">{{ $t('cancel') }}</v-btn>
        <v-btn
          color="primary-on-surface"
          variant="flat"
          :disabled="urls.length === 0"
          :loading="isSubmitting"
          @click="handleSubmit"
        >
          {{ $t('bulk_analysis.start', { count: urls.length }) }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { createAnalysis, getDashboardStats, getTags, type AnalysisPublic } from '@/client';
import GInput from '@/components/GInput.vue';
import { useSnackbarStore } from '@/stores/snackbarStore';

const MAX_CONCURRENT = 5;
const POLL_INTERVAL_MS = 5000;
const GITHUB_URL_REGEX = /^https?:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/;

type Props = {
  modelValue: boolean;
};

const props = defineProps<Props>();

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  created: [analysis: AnalysisPublic];
}>();

const { t } = useI18n();
const snackbarStore = useSnackbarStore();

const localModel = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const urls = ref<string[]>([]);
const inputError = ref<string | null>(null);
const previousUrls = ref<string[]>([]);
const inProgressCount = ref(0);
const isSubmitting = ref(false);
const tagSuggestions = ref<string[]>([]);
let pollTimer: ReturnType<typeof setInterval> | null = null;

const INCLUDE_GIT_STORAGE_KEY = 'pycefr_include_git';
const storedIncludeGit = localStorage.getItem(INCLUDE_GIT_STORAGE_KEY);

const form = ref({
  tags: [] as string[],
  includeGit: storedIncludeGit === null ? true : storedIncludeGit === 'true',
});

const availableTags = computed(() =>
  tagSuggestions.value.filter(tag => !form.value.tags.includes(tag)).sort((a, b) => a.localeCompare(b))
);
const availableSlots = computed(() => Math.max(0, MAX_CONCURRENT - inProgressCount.value));
const isInputDisabled = computed(() => urls.value.length >= availableSlots.value);
const slotsTextColor = computed(() => (availableSlots.value === 0 ? 'text-error' : 'text-medium-emphasis'));

async function fetchInProgressCount() {
  const { data } = await getDashboardStats();
  if (data) {
    inProgressCount.value = data.inProgress;
  }
}

async function fetchTagSuggestions() {
  const { data } = await getTags({ query: { limit: 50 } });
  if (data) tagSuggestions.value = data;
}

function startPolling() {
  void fetchInProgressCount();
  void fetchTagSuggestions();
  pollTimer = setInterval(() => void fetchInProgressCount(), POLL_INTERVAL_MS);
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

watch(
  () => props.modelValue,
  isOpen => {
    if (isOpen) {
      startPolling();
    } else {
      stopPolling();
    }
  }
);

onUnmounted(stopPolling);

function openRepo(url: string) {
  window.open(url, '_blank', 'noopener,noreferrer');
}

function extractRepoName(url: string): string {
  try {
    const parts = new URL(url).pathname.split('/').filter(Boolean);
    return parts.length >= 2 ? `${parts[0]}/${parts[1]}` : url;
  } catch {
    return url;
  }
}

function handleUrlsChange(newUrls: string[]) {
  const added = newUrls.filter(u => !previousUrls.value.includes(u));

  if (added.length === 0) {
    previousUrls.value = [...newUrls];
    inputError.value = null;
    return;
  }

  const validated: string[] = [...previousUrls.value];
  for (const raw of added) {
    const url = raw.trim().replace(/\/+$/, '');
    if (!url) continue;

    if (!GITHUB_URL_REGEX.test(url)) {
      inputError.value = t('invalid_url_format');
      continue;
    }

    if (validated.includes(url)) {
      inputError.value = t('bulk_analysis.duplicate_url');
      continue;
    }

    if (validated.length >= availableSlots.value) {
      inputError.value = t('bulk_analysis.no_slots');
      break;
    }

    inputError.value = null;
    validated.push(url);
  }

  urls.value = validated;
  previousUrls.value = [...validated];
}

function handlePaste(event: ClipboardEvent) {
  const text = event.clipboardData?.getData('text') ?? '';
  const lines = text
    .split(/[\n,]/)
    .map(s => s.trim())
    .filter(Boolean);

  if (lines.length > 1) {
    event.preventDefault();
    const combined = [...urls.value, ...lines];
    handleUrlsChange(combined);
  }
}

async function handleSubmit() {
  if (urls.value.length === 0) return;

  isSubmitting.value = true;
  try {
    localStorage.setItem(INCLUDE_GIT_STORAGE_KEY, String(form.value.includeGit));

    const results = await Promise.allSettled(
      urls.value.map(url =>
        createAnalysis({
          body: {
            repoUrl: url,
            includeGit: form.value.includeGit,
            tags: form.value.tags,
          },
        })
      )
    );

    let successCount = 0;
    results.forEach((result, index) => {
      if (result.status === 'rejected') {
        snackbarStore.add({
          text: t('bulk_analysis.error_single', { repo: extractRepoName(urls.value[index]) }),
          color: 'error',
          icon: 'mdi-alert-circle-outline',
        });
        return;
      }

      const { data, error } = result.value;
      if (error || !data) {
        snackbarStore.add({
          text: t('bulk_analysis.error_single', { repo: extractRepoName(urls.value[index]) }),
          color: 'error',
          icon: 'mdi-alert-circle-outline',
        });
        return;
      }

      successCount++;
      emit('created', data);
    });

    if (successCount > 0) {
      snackbarStore.add({
        text: t('bulk_analysis.success', { count: successCount }),
        color: 'success',
        icon: 'mdi-check-circle-outline',
      });
    }

    urls.value = [];
    previousUrls.value = [];
    form.value.tags = [];
    localModel.value = false;
  } finally {
    isSubmitting.value = false;
  }
}

function handleClose() {
  urls.value = [];
  previousUrls.value = [];
  inputError.value = null;
  form.value.tags = [];
  localModel.value = false;
}
</script>
