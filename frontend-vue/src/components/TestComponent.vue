<template>
  <div>{{ msg }}</div>
  <img src="x" />
  <MyComponent />
</template>
<script setup lang="ts">
import { ref } from 'vue';

import { type FileTreeData, type iFoo } from '@/components/FileTree.vue';

const fooVar: iFoo | FileTreeData = {
  a: 'test',
  b: 42,
  // Add any additional properties for FileTreeData here
};

console.log(fooVar);

const msg = ref('Hola');
</script>
<style scoped></style>
