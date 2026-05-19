<template>
  <v-tooltip :disabled="!props.date">
    <template #activator="{ props: tooltipProps }">
      <span v-bind="tooltipProps" class="app-date">
        {{ displayDate }}
      </span>
    </template>
    <span>{{ tooltipDate }}</span>
  </v-tooltip>
</template>
<script setup lang="ts">
import { computed } from 'vue';
import { formatDate } from '@/utils/datetime';
import { useI18n } from 'vue-i18n';

const { locale } = useI18n();

const props = withDefaults(
  defineProps<{
    date: string | Date | number | undefined | null;
    format?: string;
    relative?: boolean;
  }>(),
  {
    relative: false,
  }
);

const displayDate = computed(() => {
  void locale.value;
  return formatDate(props.date, props.format, props.relative);
});

const tooltipDate = computed(() => {
  void locale.value;
  return formatDate(props.date, 'LLL');
});
</script>
