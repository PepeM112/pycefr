<template>
  <g-dialog-card
    v-model="localModel"
    title="edit_analysis"
    width="440"
    :is-confirm-disabled="!form.name.trim()"
    :on-confirm-pre="handleSave"
  >
    <v-form class="d-flex flex-column ga-4">
      <g-input label="analysis_name" is-required>
        <v-text-field v-model="form.name" :rules="[rules.required]" />
      </g-input>
      <g-input label="tags">
        <v-combobox
          v-model="form.tags"
          :items="tagSuggestions"
          multiple
          variant="outlined"
          density="compact"
          chips
          closable-chips
        />
      </g-input>
    </v-form>
  </g-dialog-card>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { type AnalysisSummaryPublic, getTags, updateAnalysis } from '@/client';
import GDialogCard from '@/components/GDialogCard.vue';
import GInput from '@/components/GInput.vue';
import { useRules } from '@/composables/useRules';
import { useSnackbarStore } from '@/stores/snackbarStore';

type Props = {
  modelValue: boolean;
  analysis: AnalysisSummaryPublic | null;
};

const props = withDefaults(defineProps<Props>(), {
  analysis: null,
});

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  saved: [analysis: AnalysisSummaryPublic];
}>();

const rules = useRules();
const snackbarStore = useSnackbarStore();
const tagSuggestions = ref<string[]>([]);

const form = ref({
  name: '',
  tags: [] as string[],
});

const localModel = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

watch(
  () => props.analysis,
  analysis => {
    if (analysis) {
      form.value.name = analysis.name;
      form.value.tags = [...(analysis.tags ?? [])];
    }
  }
);

watch(
  () => props.modelValue,
  async isOpen => {
    if (isOpen) {
      const { data } = await getTags({ query: { limit: 50 } });
      if (data) tagSuggestions.value = data;
    }
  }
);

async function handleSave() {
  if (!props.analysis) throw new Error('No analysis');

  const { data, error } = await updateAnalysis({
    path: { analysis_id: props.analysis.id },
    body: {
      name: form.value.name.trim(),
      tags: form.value.tags,
    },
  });

  if (error || !data) {
    snackbarStore.add({ text: 'error.updating.analysis', color: 'error', icon: 'mdi-alert-circle-outline' });
    throw new Error('Update failed');
  }

  const updated: AnalysisSummaryPublic = {
    ...props.analysis,
    name: data.name,
    tags: data.tags,
  };
  emit('saved', updated);
  snackbarStore.add({ text: 'success.updating.analysis', color: 'success', icon: 'mdi-check-circle-outline' });
}
</script>
