<template>
  <v-menu>
    <template #activator="{ props: menuProps }">
      <v-btn v-bind="menuProps" icon="mdi-dots-vertical" density="comfortable" color="transparent" />
    </template>
    <v-list rounded="lg">
      <v-list-item
        v-for="(item, index) in props.modelValue"
        :key="index"
        :to="item.to"
        @click="item.onClick && item.onClick()"
      >
        <div class="d-flex">
          <v-icon v-if="item.icon" class="mr-4">{{ item.icon }}</v-icon>
          <v-list-item-title>{{ $t(item.label) }}</v-list-item-title>
        </div>
      </v-list-item>
    </v-list>
  </v-menu>
</template>
<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router';

export interface MenuProps {
  readonly label: string;
  readonly icon?: string;
  readonly to?: RouteLocationRaw;
  readonly onClick?: () => void;
}

const props = withDefaults(
  defineProps<{
    modelValue: MenuProps[];
  }>(),
  {
    modelValue: () => [],
  }
);
</script>
<style></style>
