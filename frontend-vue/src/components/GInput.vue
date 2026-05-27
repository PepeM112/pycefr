<template>
  <div class="g-input-wrapper">
    <p class="mb-2">
      {{ $t(props.label) }}
      <span v-if="props.isRequired" class="font-weight-bold text-error">*</span>
    </p>
    <slot />
  </div>
</template>
<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    label: string;
    isRequired?: boolean;
  }>(),
  {
    isRequired: false,
  }
);
</script>
