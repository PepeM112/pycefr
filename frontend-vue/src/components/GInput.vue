<template>
  <p class="mb-2">
    {{ $t(props.label) }}
    <span v-if="props.required" class="font-weight-bold text-error">*</span>
  </p>
  <slot />
</template>
<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    label: string;
    required?: boolean;
  }>(),
  {
    required: false,
  }
);
</script>
<style lang="scss" scoped></style>
