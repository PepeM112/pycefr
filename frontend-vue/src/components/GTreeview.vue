<template>
  <div class="g-tree-view">
    <v-virtual-scroll :items="flattenedItems" :height="height" item-height="32" class="bg-card">
      <template #default="{ item }">
        <div
          class="g-tree-node"
          :style="{ paddingLeft: `${item.depth * 16}px` }"
          :class="{ 'is-searching': search.length > 0 }"
          @click="item.hasChildren ? toggleExpand(item.id) : null"
        >
          <v-checkbox-btn
            v-if="selectable"
            :model-value="selected.includes(item.id)"
            @update:model-value="toggleSelect(item.id)"
            density="compact"
            class="mr-1"
            @click.stop
          />

          <div class="icon-container mr-1">
            <v-icon
              v-if="item.hasChildren"
              size="small"
              :icon="expandedIds.has(item.id) || search.length > 0 ? 'mdi-chevron-down' : 'mdi-chevron-right'"
            />
          </div>

          <slot name="item" :item="item" :expanded="expandedIds.has(item.id) || search.length > 0">
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

export interface TreeNode {
  id: number;
  title: string;
  children?: TreeNode[];
  icon?: string;
}

const props = defineProps<{
  items: TreeNode[];
  selected: number[];
  selectable: boolean;
  search: string;
  height: string | number;
}>();

const emit = defineEmits(['update:selected']);

// Usamos un Set para que la búsqueda de IDs sea O(1)
const expandedIds = ref<Set<number>>(new Set());

function toggleExpand(id: number) {
  const newSet = new Set(expandedIds.value);
  if (newSet.has(id)) newSet.delete(id);
  else newSet.add(id);
  expandedIds.value = newSet;
}

function toggleSelect(id: number) {
  const newSelected = [...props.selected];
  const index = newSelected.indexOf(id);
  if (index > -1) newSelected.splice(index, 1);
  else newSelected.push(id);
  emit('update:selected', newSelected);
}

/**
 * Lógica de filtrado:
 * Un nodo se muestra si:
 * 1. Su título coincide con la búsqueda.
 * 2. ALGUNO de sus descendientes coincide con la búsqueda (para mostrar la ruta).
 */
const flattenedItems = computed(() => {
  const result: any[] = [];
  const searchLower = props.search.toLowerCase();

  // Función auxiliar para saber si un nodo o sus hijos cumplen el filtro
  function nodeMatches(node: TreeNode): boolean {
    if (!searchLower) return true;
    if (node.title.toLowerCase().includes(searchLower)) return true;
    if (node.children) {
      return node.children.some(child => nodeMatches(child));
    }
    return false;
  }

  function traverse(nodes: TreeNode[], depth = 0) {
    for (const node of nodes) {
      if (!nodeMatches(node)) continue; // Si ni él ni sus hijos coinciden, lo ignoramos

      const hasChildren = !!(node.children && node.children.length > 0);
      const isExpanded = expandedIds.value.has(node.id) || searchLower.length > 0;

      result.push({
        ...node,
        depth,
        hasChildren,
      });

      if (hasChildren && isExpanded) {
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
  border: 1px solid rgba(var(--v-theme-border-color), 0.12);
  border-radius: inherit;
}

.g-tree-node {
  display: flex;
  align-items: center;
  height: 32px;
  cursor: pointer;
  padding-right: 12px;
  user-select: none;
  font-size: 0.875rem;

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
  }
}
</style>
