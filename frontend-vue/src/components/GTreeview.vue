<template>
  <div class="g-tree-view">
    <v-virtual-scroll :items="flattenedItems" :height="height" item-height="32">
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

          <div class="node-content text-truncate">
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

const emit = defineEmits(['update:selected']);

const props = withDefaults(
  defineProps<{
    items: TreeNode[] | undefined;
    selected: number[] | undefined;
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
  let ids: number[] = [node.id];
  if (node.children) {
    node.children.forEach(child => {
      ids = [...ids, ...getDescendantIds(child)];
    });
  }
  return ids;
}

function getOnlyChildrenIds(node: TreeNode): number[] {
  let ids: number[] = [];
  if (node.children) {
    node.children.forEach(child => {
      ids.push(child.id);
      ids = [...ids, ...getOnlyChildrenIds(child)];
    });
  }
  return ids;
}

function isSelected(node: TreeNode): boolean {
  if (!node.children || node.children.length === 0) {
    return props.selected.includes(node.id);
  }
  const childIds = getOnlyChildrenIds(node);
  return childIds.every(id => props.selected.includes(id));
}

function isIndeterminate(node: TreeNode): boolean {
  if (!node.children || node.children.length === 0) return false;

  const childIds = getOnlyChildrenIds(node);
  const selectedCount = childIds.filter(id => props.selected.includes(id)).length;

  return selectedCount > 0 && selectedCount < childIds.length;
}

function handleToggleSelect(node: TreeNode) {
  const idsToToggle = getDescendantIds(node);
  const currentlySelected = isSelected(node);

  let newSelected: number[];
  if (currentlySelected) {
    newSelected = props.selected.filter(id => !idsToToggle.includes(id));
  } else {
    newSelected = Array.from(new Set([...props.selected, ...idsToToggle]));
  }
  emit('update:selected', newSelected);
}

const flattenedItems = computed(() => {
  const result: any[] = [];
  const searchLower = props.search.toLowerCase();

  function nodeMatches(node: TreeNode): boolean {
    if (!searchLower) return true;
    if (node.title.toLowerCase().includes(searchLower)) return true;
    return node.children?.some(child => nodeMatches(child)) || false;
  }

  function traverse(nodes: TreeNode[], depth = 0) {
    for (const node of nodes) {
      if (!nodeMatches(node)) continue;
      const hasChildren = !!(node.children && node.children.length > 0);
      result.push({ ...node, depth, hasChildren });
      if (hasChildren && isExpanded(node.id)) {
        traverse(node.children!, depth + 1);
      }
    }
  }

  traverse(props.items);
  return result;
});
</script>

<style lang="scss" scoped>
.g-tree-view {
  width: 100%;
  user-select: none;
}

.g-tree-node {
  display: flex;
  align-items: center;
  height: 34px;
  cursor: pointer;
  white-space: nowrap;
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
    flex: 1;
    display: flex;
    align-items: center;
    min-width: 0; // Required for text-truncate to work properly
  }

  .node-title {
    font-size: 0.875rem;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>
