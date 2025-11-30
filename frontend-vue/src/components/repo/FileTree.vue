<template>
  <v-card class="position-relative" :min-width="300" rounded="lg">
    <div class="pa-2 pt-4 pr-4" style="border-bottom: 1px solid #dedede">
      <div class="d-flex align-center">
        <v-btn
          class="mr-2"
          density="compact"
          :icon="searchOptions.visible ? 'mdi-chevron-up' : 'mdi-chevron-down'"
          @click="searchOptions.visible = !searchOptions.visible"
        />
        <v-text-field
          v-model="searchOptions.searchText"
          class="bg-white"
          density="compact"
          variant="outlined"
          hide-details
          style="font-size: 6px !important"
        />
      </div>
      <div v-if="searchOptions.visible" class="d-flex justify-space-between align-center pt-2">
        <v-tooltip>
          <template #activator="{ props }">
            <v-btn
              v-bind="props"
              class="px-2"
              style="min-width: unset"
              color="primary"
              density="compact"
              variant="text"
              @click="toggleAllowFilterByFiles"
            >
              <v-icon>
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
            color="primary"
            density="compact"
            size="small"
            variant="text"
            style="min-width: unset; height: 24px"
            @click="selectedNodes = []"
          >
            {{ $t('clear') }}
          </v-btn>
          <v-btn
            color="primary"
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
    <!-- activatable props does the opposite. I believe its a component mistake -->
    <v-treeview
      class="pa-0 pb-8"
      v-model:selected="selectedNodes"
      color="primary"
      density="compact"
      :items="localModelValue"
      item-value="id"
      :selectable="searchOptions.allowFilterByFiles"
      :activatable="!searchOptions.allowFilterByFiles"
      select-strategy="classic"
      expand-icon="mdi-chevron-down"
      collapse-icon="mdi-chevron-up"
      open-all
    >
      <template #prepend="{ item, isOpen }">
        <v-icon v-if="item.children" :icon="isOpen ? 'mdi-folder-open' : 'mdi-folder'" size="small" />
        <v-icon v-else size="small">
          <img :src="getTreeNodeIcon(item)" />
        </v-icon>
      </template>
    </v-treeview>
  </v-card>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import { getExtensionIcon, type FileExtension } from '@/utils/utils';

export interface TreeNode {
  id: number;
  title: string;
  children?: TreeNode[];
}

const emit = defineEmits<{
  (e: 'update:modelValue', value: TreeNode[]): void;
  (e: 'update:selected', value: number[] | 'all'): void;
}>();

defineProps<{
  modelValue: TreeNode[];
  selected: number[];
}>();

const localModelValue = defineModel<TreeNode[]>('modelValue');
const selectedNodes = defineModel<number[]>('selected');

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

function getTreeNodeIcon(node: TreeNode): string {
  if (node.children && node.children.length > 0) return 'mdi-folder';

  const extension = (node.title.split('.').pop()?.toString() || '') as FileExtension;
  return getExtensionIcon(extension);
}
</script>
<style lang="scss" scoped>
.v-card {
  overflow-x: scroll;
}
.v-treeview {
  overflow: scroll;
  ::v-deep(.v-list-item-title) {
    font-size: 14px !important;
  }
}
</style>
