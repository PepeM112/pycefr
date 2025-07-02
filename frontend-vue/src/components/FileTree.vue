<template>
  <div class="file-tree-wrapper">
    <div class="file-tree" />
  </div>
</template>
<script setup lang="ts">
import { onMounted } from 'vue';

const emit = defineEmits<{
  (e: 'select-element', value: string): void;
}>();

const props = defineProps<{
  paths: string[];
}>();

function buildTree(data: string[]): Record<string, any> {
  const root = {};

  data.forEach(path => {
    const parts = path.split('/');
    let current: Record<string, any> = root;

    parts.forEach(part => {
      if (!current[part]) {
        current[part] = {};
      }
      current = current[part];
    });
  });

  return root;
}

function createTreeHTML(tree: Record<string, any>, isRoot: boolean = false) {
  const ul = document.createElement('ul');

  if (isRoot) {
    const rootLi = document.createElement('li');
    const rootSpan = document.createElement('span');
    rootSpan.textContent = window.location.pathname.split('/').filter(Boolean).pop() + '/' || 'root';
    rootSpan.classList.add('root');
    rootLi.appendChild(rootSpan);

    rootLi.appendChild(createTreeHTML(tree));
    ul.appendChild(rootLi);

    return ul;
  }

  for (const key in tree) {
    const li = document.createElement('li');
    const span = document.createElement('span');

    if (Object.keys(tree[key]).length) {
      span.textContent = `${key}/`;
      span.classList.add('folder');
      span.addEventListener('click', toggleFolder);
      li.classList.add('collapsed');
    } else {
      span.textContent = key;
      span.classList.add('file');
    }

    li.appendChild(span);

    if (Object.keys(tree[key]).length) {
      li.appendChild(createTreeHTML(tree[key]));
    }

    ul.appendChild(li);
  }

  return ul;
}

function getFullPathFromElement(el: HTMLElement | null): string {
  const parts = [];

  while (el && !el.classList.contains('root')) {
    if (el.tagName === 'LI') {
      const span = el.querySelector(':scope > span');
      if (span) {
        parts.unshift(span.textContent?.trim());
      }
    }
    el = el.parentElement?.closest('li') || null;
  }

  return parts.slice(1).join('');
}

function toggleFolder(event: MouseEvent) {
  if (!event.target) return;
  const li = (event.target as HTMLElement).closest('li');
  if (!li) return;
  li.classList.toggle('collapsed');
  li.classList.toggle('expanded');
}

function initializeFileTree(containerSelector: string, data: string[]) {
  const container = document.querySelector(containerSelector);

  if (!container) {
    console.error(`Element with selector "${containerSelector}" not found.`);
    return;
  }

  const treeData = buildTree(data);
  container.innerHTML = ''; // Clear the container
  container.appendChild(createTreeHTML(treeData, true));

  // Listener for when clicking entry
  container.addEventListener('click', e => {
    if (!e.target) return;
    const element = e.target as HTMLElement;

    if (element.classList.contains('root')) {
      const lastSelected = document.querySelector('.file-tree li.selected');
      if (lastSelected) lastSelected.classList.remove('selected');

      emit('select-element', '');
    }
    if (element.tagName === 'SPAN') {
      if (element.classList.contains('file')) {
        selectFile(element);
      }
    }
  });
}

function selectFile(element: HTMLElement) {
  const lastSelected = document.querySelector('.file-tree li.selected');
  if (lastSelected) lastSelected.classList.remove('selected');

  if (!element.parentElement) return;
  element.parentElement.classList.add('selected');

  emit('select-element', getFullPathFromElement(element) || '');
}

onMounted(() => {
  initializeFileTree('.file-tree', props.paths);
});
</script>
<style lang="scss">
.file-tree-wrapper {
  background: white;
  border: 2px solid var(--primary-color);
  border-radius: var(--border-radius);
  min-width: 270px;
  height: fit-content;
  min-height: 600px;
  max-height: 100%;
  overflow-x: auto;
  overflow-y: auto;
  padding: 1rem;

  ul {
    list-style: none;
    padding-left: 1rem;
    margin: 0;
    position: relative;

    &:first-child {
      padding: 0;
      &::before,
      &::after {
        content: none;
      }
    }
  }

  .file-tree > ul > li {
    padding-left: 0;

    &::before,
    &::after {
      content: none;
    }
  }

  li {
    position: relative;
    padding-left: 18px;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: -6px;
      height: 100%;
      border-left: 1px solid var(--primary-color-light);
    }

    &::after {
      content: '';
      position: absolute;
      top: 12px;
      left: -6px;
      width: 0.5rem;
      border-top: 1px solid var(--primary-color-light);
    }

    &:last-child::before {
      height: 12px;
    }

    &.collapsed {
      ul {
        display: none;
      }

      span.folder::before {
        background-image: url('@/assets/img/folder.svg');
      }

      span.folder:hover::before {
        background-image: url('@/assets/img/folder-snow.svg') !important;
      }
    }

    &.expanded span.folder:not(.root):hover::before {
      background-image: url('@/assets/img/folder-open-snow.svg');
      height: 1em;
    }

    &.selected {
      > span {
        background-color: var(--primary-color);
        color: snow;
      }

      > span::before {
        background-color: var(--primary-color);
        border-radius: 6px;
      }
    }

    /* &.highlighted {
      &::before,
      &::after {
        border-color: red;
      }
    } */
  }

  span {
    position: relative;
    margin-left: 4px;
    padding: 1px 4px 4px;
    line-height: 1.5em;
    border-radius: 0 6px 6px 0;
    cursor: pointer;
    display: flex;

    &.file {
      &::before {
        content: '';
        position: absolute;
        left: -20px;
        top: 50%;
        box-sizing: content-box;
        transform: translateY(-50%);
        width: 1em;
        height: 1em;
        background-image: url('@/assets/img/python.svg');
        background-size: 0.875rem;
        background-position: center;
        background-repeat: no-repeat;
        padding: 9px 0 4px 8px;
        border-radius: 6px 0 0 6px;
      }
    }

    &.folder:not(.root)::before {
      content: '';
      position: absolute;
      left: -20px;
      top: 50%;
      box-sizing: content-box;
      transform: translateY(-50%);
      width: 1em;
      height: 1em;
      background-image: url('@/assets/img/folder-open.svg');
      background-size: 0.875rem;
      background-position: center;
      background-repeat: no-repeat;
      padding: 9px 0 4px 8px;
      border-radius: 6px 0 0 6px;
    }

    &:hover {
      background-color: var(--primary-color);
      color: snow !important;

      &::before {
        background-color: var(--primary-color);
      }
    }

    &.root {
      margin: 0;
      border-radius: 6px !important;

      &::before,
      &::after {
        content: none;
      }
    }
  }
}
</style>
