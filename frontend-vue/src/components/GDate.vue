<template>
  <v-tooltip>
    <template #activator="{ props }">
      <span v-bind="props" class="app-date">
        {{ displayDate }}
      </span>
    </template>
    <span>{{ tooltipDate }}</span>
  </v-tooltip>
</template>
<script setup lang="ts">
import { computed } from 'vue';
import { formatDate } from '@/utils/utils';
import { useI18n } from 'vue-i18n';

const { locale } = useI18n();

const props = withDefaults(
  defineProps<{
    date: string | Date | number | undefined | null;
    format?: string;
    relative?: boolean;
  }>(),
  {
    relative: true,
  }
);

const displayDate = computed(() => {
  // @ts-expect-error -> unused variable, needed to trigger re-computation when locale changes
  const l = locale.value;
  return formatDate(props.date, props.format, props.relative);
});

const tooltipDate = computed(() => {
  // @ts-expect-error -> unused variable, needed to trigger re-computation when locale changes
  const l = locale.value;
  return formatDate(props.date, 'LLL');
});
</script>
