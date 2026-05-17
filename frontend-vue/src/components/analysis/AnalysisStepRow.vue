<template>
  <div class="step-row d-flex ga-3" :class="rowClass">
    <div class="step-icon-column d-flex flex-column align-center">
      <v-icon v-if="state === 'completed'" color="success" icon="mdi-check-circle" size="24" />
      <v-progress-circular v-else-if="state === 'active'" indeterminate size="24" width="2" color="primary-on-surface" />
      <v-icon v-else-if="state === 'failed'" color="error" icon="mdi-alert-circle" size="24" />
      <v-icon v-else-if="state === 'skipped'" color="grey-lighten-1" icon="mdi-minus-circle-outline" size="24" />
      <v-icon v-else color="grey-lighten-1" icon="mdi-circle-outline" size="24" />
      <div v-if="!isLast" class="step-connector flex-grow-1" :class="connectorClass" />
    </div>

    <div class="step-content flex-grow-1">
      <div class="d-flex align-center">
        <span :class="labelClass">{{ label }}</span>
        <span v-if="detail && state === 'active'" class="step-detail text-caption text-medium-emphasis ml-1">
          ({{ detail }})
        </span>
      </div>
      <div v-if="detail && state === 'failed'" class="mt-1 text-caption text-error">
        {{ detail }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type StepState = 'pending' | 'active' | 'completed' | 'failed' | 'skipped';

type Props = {
  label: string;
  state: StepState;
  connectorState?: StepState;
  detail?: string;
  isLast?: boolean;
};

const props = withDefaults(defineProps<Props>(), {
  connectorState: 'pending',
  detail: undefined,
  isLast: false,
});

const isExpanded = computed(() => props.state === 'active' || props.state === 'failed');

const rowClass = computed(() => ({
  'step-row--expanded': isExpanded.value,
  'step-row--compact': !isExpanded.value,
}));

const labelClass = computed(() => ({
  'font-weight-bold': props.state === 'active',
  'text-medium-emphasis': props.state === 'pending',
  'text-error': props.state === 'failed',
}));

const connectorClass = computed(() => ({
  'step-connector--success': props.connectorState === 'completed' || props.connectorState === 'active',
  'step-connector--error': props.connectorState === 'failed',
}));
</script>

<style scoped>
.step-icon-column {
  width: 24px;
  min-width: 24px;
}

.step-content {
  padding-top: 2px;
  transition: padding 0.3s ease;
}

.step-row--expanded .step-content {
  padding-top: 2px;
  padding-bottom: 16px;
}

.step-row--compact .step-content {
  padding-top: 2px;
  padding-bottom: 2px;
}

.step-row:last-child .step-content {
  padding-bottom: 0;
}

.step-connector {
  width: 2px;
  min-height: 4px;
  background-color: rgba(var(--v-border-color), var(--v-border-opacity));
  transition:
    background-color 0.3s ease,
    min-height 0.3s ease;
}

.step-row--expanded .step-connector {
  min-height: 16px;
}

.step-row--compact .step-connector {
  min-height: 4px;
}

.step-connector--success {
  background-color: rgb(var(--v-theme-success));
}

.step-connector--error {
  background-color: rgb(var(--v-theme-error));
}

.step-detail {
  font-variant-numeric: tabular-nums;
}
</style>
