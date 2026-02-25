<template>
  <div class="g-tree-view">
    <v-virtual-scroll :items="flattenedItems" :height="height" item-height="34">
      <template #default="{ item }">
        <div
          class="g-tree-node"
          :style="{ paddingLeft: `${item.depth * 16 + 8}px` }"
          @click="item.hasChildren ? toggleExpand(item.id) : null"
        >
          <v-checkbox-btn
            v-if="selectable"
            class="tree-checkbox"
            :model-value="isSelected(item)"
            :indeterminate="isIndeterminate(item)"
            density="compact"
            @click.stop="handleToggleSelect(item)"
          />

          <div class="icon-container">
            <v-icon
              v-if="item.hasChildren"
              size="24"
              :icon="isExpanded(item.id) ? 'mdi-chevron-down' : 'mdi-chevron-right'"
            />
          </div>

          <div class="node-content">
            <slot name="item" :item="item" :expanded="isExpanded(item.id)">
              <v-icon v-if="item.icon" :icon="`iconify:${item.icon}`" size="18" class="mr-2" />
              <span class="node-title">{{ item.title }}</span>
            </slot>
          </div>
        </div>
      </template>
    </v-virtual-scroll>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import type { TreeNode } from '@/types/treeview';

type FlattenedNode = TreeNode & {
  depth: number;
  hasChildren: boolean;
};

const emit = defineEmits(['update:selected']);

const props = withDefaults(
  defineProps<{
    items: TreeNode[];
    selected: number[] | 'all';
    selectable?: boolean;
    search?: string;
    height?: string | number;
  }>(),
  {
    items: () => [],
    selected: () => [],
    selectable: false,
    search: '',
    height: '400px',
  }
);

const expandedIds = ref<Set<number>>(new Set());

const isExpanded = (id: number) => expandedIds.value.has(id) || props.search.length > 0;

function toggleExpand(id: number) {
  const newSet = new Set(expandedIds.value);
  newSet.has(id) ? newSet.delete(id) : newSet.add(id);
  expandedIds.value = newSet;
}

function getDescendantIds(node: TreeNode): number[] {
  let ids = [node.id];
  if (node.children) {
    for (const child of node.children) {
      ids = [...ids, ...getDescendantIds(child)];
    }
  }
  return ids;
}

function isSelected(node: TreeNode): boolean {
  if (props.selected === 'all') return true;
  const selectedIds = props.selected as number[];

  if (!node.children || node.children.length === 0) {
    return selectedIds.includes(node.id);
  }

  return node.children.every(child => isSelected(child));
}

function isIndeterminate(node: TreeNode): boolean {
  if (props.selected === 'all') return false;

  if (!node.children || node.children.length === 0) return false;

  const fullySelected = isSelected(node);
  if (fullySelected) return false;

  // Indeterminate unless all children are all selected or all unselected
  return node.children.some(child => isSelected(child) || isIndeterminate(child));
}

function handleToggleSelect(node: TreeNode) {
  const idsToBranch = getDescendantIds(node);
  let currentSelected: number[] = [];

  if (props.selected === 'all') {
    currentSelected = props.items.flatMap(item => getDescendantIds(item));
  } else {
    currentSelected = [...props.selected];
  }

  const currentlySelected = isSelected(node);
  let newSelected: number[];

  if (currentlySelected) {
    newSelected = currentSelected.filter(id => !idsToBranch.includes(id));
  } else {
    newSelected = Array.from(new Set([...currentSelected, ...idsToBranch]));
  }

  emit('update:selected', newSelected);
}

function nodeMatches(node: TreeNode, search: string): boolean {
  if (!search) return true;
  if (node.title.toLowerCase().includes(search)) return true;
  return node.children?.some(child => nodeMatches(child, search)) || false;
}

const flattenedItems = computed<FlattenedNode[]>(() => {
  const searchLower = props.search.toLowerCase();

  const traverse = (nodes: TreeNode[], depth = 0): FlattenedNode[] => {
    return nodes.reduce((acc, node) => {
      if (!nodeMatches(node, searchLower)) return acc;

      const hasChildren = !!(node.children && node.children.length > 0);

      return [
        ...acc,
        { ...node, depth, hasChildren },
        ...(hasChildren && isExpanded(node.id) ? traverse(node.children!, depth + 1) : []),
      ];
    }, [] as FlattenedNode[]);
  };

  return traverse(props.items);
});
</script>

<style lang="scss" scoped>
.g-tree-view {
  width: 100%;
  user-select: none;
  overflow-x: auto;
}

:deep(.v-virtual-scroll__container) {
  min-width: max-content;
  display: inline-block;
  width: 100%;
}

.g-tree-node {
  display: flex;
  align-items: center;
  height: 34px;
  cursor: pointer;
  white-space: nowrap;
  padding-right: 16px;
  transition: background-color 0.15s ease;

  &:hover {
    background-color: rgba(var(--v-theme-background));
  }

  .tree-checkbox {
    flex: 0 0 auto;
    margin-right: 8px;

    // Remove interal padding from Vuetify
    :deep(.v-selection-control) {
      min-height: unset;
      justify-content: center;
    }
  }

  .icon-container {
    width: 20px;
    flex: 0 0 auto;
    display: flex;
    justify-content: center;
    margin-right: 8px;
  }

  .node-content {
    flex: 1 0 auto;
    display: flex;
    align-items: center;
  }

  .node-title {
    font-size: 0.875rem;
    overflow: visible;
    text-overflow: clip;
  }
}
</style>
