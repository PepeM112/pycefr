<template>
  <section class="g-container" :class="{ 'pa-6': !isExpandable }">
    <template v-if="!isExpandable">
      <div class="d-flex mb-4">
        <h2 v-if="title" class="text-h5 font-weight-bold">{{ $t(title) }}</h2>
        <v-spacer />
        <div class="actions-container">
          <slot name="actions" />
        </div>
      </div>
      <slot />
    </template>

    <v-expansion-panels v-else eager>
      <v-expansion-panel elevation="0" rounded="lg">
        <v-expansion-panel-title>
          <div class="d-flex py-2">
            <h2 v-if="title" class="text-h5 font-weight-bold mb-0">{{ $t(title) }}</h2>
            <v-spacer />
            <div class="actions-container" @click.stop><slot name="actions" /></div>
          </div>
        </v-expansion-panel-title>

        <v-expansion-panel-text eager>
          <div class="pt-4">
            <slot />
          </div>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </section>
</template>
<script setup lang="ts">
defineProps<{
  title?: string;
  isExpandable?: boolean;
}>();
</script>
<style lang="scss">
.g-container {
  position: relative;
  background-color: rgb(var(--v-theme-surface));
  color: rgb(var(--v-theme-on-surface));
  border-radius: var(--border-radius);
  box-shadow:
    var(--v-shadow-key-umbra-opacity, rgba(0, 0, 0, 0.2)) 0px 2px 1px -1px,
    var(--v-shadow-key-penumbra-opacity, rgba(0, 0, 0, 0.14)) 0px 1px 1px 0px,
    var(--v-shadow-key-ambient-opacity, rgba(0, 0, 0, 0.12)) 0px 1px 3px 0px;

  h2 {
    margin: 0 0 2rem;
  }
}
</style>
