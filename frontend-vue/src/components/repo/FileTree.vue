<template>
  <v-card class="file-tree-card" rounded="lg">
    <div class="file-tree-header">
      <div class="d-flex align-center">
        <v-btn
          class="mr-2"
          density="compact"
          :icon="searchOptions.visible ? 'mdi-chevron-up' : 'mdi-chevron-down'"
          @click="searchOptions.visible = !searchOptions.visible"
        />
        <v-text-field v-model="searchOptions.searchText" class="bg-background rounded-lg" hide-details />
      </div>
      <div v-if="searchOptions.visible" class="d-flex justify-space-between align-center pt-2">
        <v-tooltip>
          <template #activator="{ props }">
            <v-btn
              v-bind="props"
              class="px-2"
              style="min-width: unset"
              color="primary-on-surface"
              density="compact"
              variant="text"
              icon
              @click="toggleAllowFilterByFiles"
            >
              <v-icon size="sm">
                {{ searchOptions.allowFilterByFiles ? 'mdi-filter' : 'mdi-filter-off-outline' }}
              </v-icon>
            </v-btn>
          </template>
          <span style="font-size: 0.75rem">
            {{ searchOptions.allowFilterByFiles ? $t('enable_filtering_by_files') : $t('disable_filtering_by_files') }}
          </span>
        </v-tooltip>

        <div v-if="searchOptions.allowFilterByFiles" style="display: flex; gap: 0.5rem">
          <v-btn
            v-if="selectedNodes?.length"
            color="primary-on-surface"
            density="compact"
            size="small"
            variant="text"
            style="min-width: unset; height: 24px"
            @click="selectedNodes = []"
          >
            {{ $t('clear') }}
          </v-btn>
          <v-btn
            color="primary-on-surface"
            density="compact"
            size="small"
            variant="text"
            style="min-width: unset; height: 24px"
            @click="emit('update:selected', 'all')"
          >
            {{ $t('select_all') }}
          </v-btn>
        </div>
      </div>
    </div>

    <g-treeview
      :items="localModelValue"
      :selected="selectedNodes"
      @update:selected="val => (selectedNodes = val)"
      :search="searchOptions.searchText"
      :selectable="searchOptions.allowFilterByFiles"
      height="800"
      class="pa-0 pb-8"
    >
      <template #item="{ item, expanded }">
        <v-icon v-if="item.children" :icon="expanded ? 'mdi-folder-open' : 'mdi-folder'" size="small" class="mr-2" />
        <v-icon v-else size="18" :icon="`iconify:${item.icon}`" class="mr-2" />
        <span class="node-title">{{ item.title }}</span>
      </template>
    </g-treeview>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { getExtensionIcon, type FileExtension } from '@/utils/utils';
import GTreeview from '@/components/GTreeview.vue';
import type { TreeNode } from '@/types/treeview';

const emit = defineEmits<{
  (e: 'update:modelValue', value: TreeNode[]): void;
  (e: 'update:selected', value: number[] | 'all'): void;
}>();

const localModelValue = defineModel<TreeNode[]>('modelValue', { required: true, default: () => [] });
const selectedNodes = defineModel<number[]>('selected', { required: true, default: () => [] });

const searchOptions = ref({
  searchText: '',
  visible: false,
  allowFilterByFiles: false,
});

function toggleAllowFilterByFiles() {
  searchOptions.value.allowFilterByFiles = !searchOptions.value.allowFilterByFiles;
  if (!searchOptions.value.allowFilterByFiles) {
    emit('update:selected', 'all');
  }
}
</script>

<style lang="scss" scoped>
.file-tree-card {
  display: flex;
  flex-direction: column;
  min-width: 300px;
  max-height: 900px;
  height: fit-content;
}

.file-tree-header {
  border-bottom: 1px solid rgba(var(--v-theme-border-color), 0.5);
  padding: 1rem 1rem 0.5rem 0.5rem;
}

.node-title {
  font-size: 14px;
  white-space: nowrap;
}
</style>
