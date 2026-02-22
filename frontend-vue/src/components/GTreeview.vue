<template>
  <div class="g-tree-view">
    <v-virtual-scroll :items="flattenedItems" :height="height" item-height="32">
      <template #default="{ item }">
        <div
          class="g-tree-node"
          :style="{ paddingLeft: `${item.depth * 16}px` }"
          @click="item.hasChildren ? toggleExpand(item.id) : null"
        >
          <v-checkbox-btn
            v-if="selectable"
            :model-value="isSelected(item)"
            :indeterminate="isIndeterminate(item)"
            density="compact"
            class="mr-1"
            @click.stop="handleToggleSelect(item)"
          />

          <div class="icon-container mr-1">
            <v-icon
              v-if="item.hasChildren"
              size="small"
              :icon="isExpanded(item.id) ? 'mdi-chevron-down' : 'mdi-chevron-right'"
            />
          </div>

          <slot name="item" :item="item" :expanded="isExpanded(item.id)">
            <v-icon v-if="item.icon" :icon="`iconify:${item.icon}`" size="18" class="mr-2" />
            <span class="node-title text-truncate">{{ item.title }}</span>
          </slot>
        </div>
      </template>
    </v-virtual-scroll>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import type { TreeNode } from '@/types/treeview';

const emit = defineEmits(['update:selected']);

const props = withDefaults(defineProps<{
  items: TreeNode[] | undefined;
  selected: number[] | undefined;
  selectable?: boolean;
  search?: string;
  height?: string | number;
}>(), {
  items: () => [],
  selected: () => [],
  selectable: false,
  search: '',
  height: '400px',
});


const expandedIds = ref<Set<number>>(new Set());

const isExpanded = (id: number) => expandedIds.value.has(id) || props.search.length > 0;

function toggleExpand(id: number) {
  const newSet = new Set(expandedIds.value);
  newSet.has(id) ? newSet.delete(id) : newSet.add(id);
  expandedIds.value = newSet;
}

// --- Lógica de Selección en Cascada ---

function getDescendantIds(node: TreeNode): number[] {
  let ids: number[] = [node.id];
  if (node.children) {
    node.children.forEach(child => {
      ids = [...ids, ...getDescendantIds(child)];
    });
  }
  return ids;
}

function isSelected(node: TreeNode): boolean {
  if (!node.children || node.children.length === 0) {
    return props.selected.includes(node.id);
  }
  const descendants = getDescendantIds(node);
  return descendants.every(id => props.selected.includes(id));
}

function isIndeterminate(node: TreeNode): boolean {
  if (!node.children || node.children.length === 0) return false;
  const descendants = getDescendantIds(node);
  const selectedCount = descendants.filter(id => props.selected.includes(id)).length;
  return selectedCount > 0 && selectedCount < descendants.length;
}

function handleToggleSelect(node: TreeNode) {
  const idsToToggle = getDescendantIds(node);
  const currentlySelected = isSelected(node);

  let newSelected: number[];
  if (currentlySelected) {
    // Deseleccionar todo el grupo
    newSelected = props.selected.filter(id => !idsToToggle.includes(id));
  } else {
    // Seleccionar todo el grupo (evitando duplicados)
    newSelected = Array.from(new Set([...props.selected, ...idsToToggle]));
  }
  emit('update:selected', newSelected);
}

// --- Aplanado para Virtual Scroll ---

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
.g-tree-node {
  display: flex;
  align-items: center;
  height: 32px;
  cursor: pointer;
  white-space: nowrap;
  &:hover {
    background-color: rgba(var(--v-theme-primary), 0.08);
  }
  .icon-container {
    width: 24px;
    display: flex;
    justify-content: center;
  }
  .node-title {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>
