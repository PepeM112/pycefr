<template>
  <div class="content">
    <header>
      <h1>{{ repoTitle }}</h1>
    </header>
    <div class="charts"></div>
    <div class="container">
      <h2>Propiedades</h2>
      <div class="d-flex">
        <file-tree :data="[]" />
        <div class="properties">
          <div class="filters-wrapper pl-8">
            <v-text-field
              density="compact"
              variant="outlined"
              placeholder="Search..."
              :append-inner-icon="'mdi-magnify'"
              width="180px"
              clearable
              style="font-size: 12px !important"
            />
            <div class="d-flex ga-2">
              <v-btn
                v-for="level in levels"
                class="level-bubble"
                :class="{ selected: selectedLevels.includes(level.label) }"
                :style="{ backgroundColor: level.color }"
                size="small"
                density="comfortable"
                rounded="circle"
                @click="toggleLevel(level.label)"
              >
                {{ level.label }}
              </v-btn>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import FileTree from '@/components/FileTree.vue';

const route = useRoute();
const repoTitle = ref<string>('');
const selectedLevels = ref<string[]>([]);

const levels = [
  { label: 'A1', color: 'rgba(255, 99, 132, 1)' },
  { label: 'A2', color: 'rgba(255, 159, 64, 1)' },
  { label: 'B1', color: 'rgba(255, 206, 86, 1)' },
  { label: 'B2', color: 'rgba(75, 192, 192, 1)' },
  { label: 'C1', color: 'rgba(54, 162, 235, 1)' },
  { label: 'C2', color: 'rgba(153, 102, 255, 1)' },
];

function toggleLevel(level: string) {
  console.log(`Toggling level: ${level}`);
  if (selectedLevels.value.includes(level)) {
    selectedLevels.value = selectedLevels.value.filter(l => l !== level);
  } else {
    selectedLevels.value.push(level);
  }
}

onMounted(() => {
  repoTitle.value = route.params.repoName.toString();
  selectedLevels.value = levels.map(level => level.label);
});
</script>
<style lang="scss">
.properties {
  padding-left: 2rem;
  border-left: 2px solid var(--primary-color-light);
}

.level-bubble {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 0.875rem;
  width: 2rem;
  height: 2rem !important;
  min-width: unset;
  color: white;

  &:not(.selected) {
    background-color: rgb(155, 156, 164);
    color: var(--primary-color);
    opacity: 0.35;
    transition: all 0.3s ease;

    &:hover {
      opacity: 0.65;
      color: white;
    }
  }
}
</style>
