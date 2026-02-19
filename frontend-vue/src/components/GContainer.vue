<template>
  <section :class="{ 'pa-6': !expandable }">
    <template v-if="!expandable">
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
const props = defineProps<{
  title?: string;
  expandable?: boolean;
}>();
</script>
<style lang="scss" scoped>
section {
  position: relative;
  background-color: rgb(var(--v-theme-surface));
  color: rgb(var(--v-theme-on-surface));
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);

  h2 {
    margin: 0 0 2rem;
  }
}
</style>
