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

const displayDate = computed(() => formatDate(props.date, props.format, props.relative));

const tooltipDate = computed(() => formatDate(props.date, 'DD [de] MMMM [de] YYYY, HH:mm'));
</script>
