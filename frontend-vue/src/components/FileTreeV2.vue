<template>
  <v-card v-bind="props" class="position-relative" :min-width="300" rounded="md">
    <v-text-field
      v-model="search"
      class="ma-4"
      density="compact"
      rounded="md"
      variant="outlined"
      hide-details
      style="font-size: 6px !important"
    />
    <v-treeview
      v-model:selected="selectedNodes"
      :items="localModelValue"
      color="primary"
      select-strategy="classic"
      item-value="id"
      selectable
      expand-icon="mdi-chevron-down"
      collapse-icon="mdi-chevron-up"
    >
      <template #prepend="{ item }">
        <v-icon :icon="getNodeIcon(item)" color="primary" />
      </template>
    </v-treeview>
  </v-card>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue';

export interface TreeNode {
  id: number;
  title: string;
  children?: TreeNode[];
}

const emit = defineEmits<{
  (e: 'update:modelValue', value: TreeNode[]): void;
  (e: 'update:selected', value: number[]): void;
}>();

const props = withDefaults(
  defineProps<{
    modelValue: TreeNode[];
    selected: number[];
  }>(),
  {
    modelValue: () => [],
  }
);

const search = ref<string>('');

const localModelValue = computed({
  get() {
    return props.modelValue;
  },
  set(value: TreeNode[]) {
    emit('update:modelValue', value);
  },
});

const selectedNodes = computed({
  get() {
    return props.selected;
  },
  set(value: number[]) {
    console.log('Selected nodes updated:', value);
    emit('update:selected', value);
  },
});

function getNodeIcon(node: TreeNode): string {
  const fileExtensions = ['py', 'js', 'ts', 'vue', 'html', 'css', 'json', 'md'];
  if (node.children) return 'mdi-folder';
  const extension = node.title.split('.').pop()?.toString() || '';
  return fileExtensions.includes(extension) ? 'mdi-language-python' : 'mdi-language-python';
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
