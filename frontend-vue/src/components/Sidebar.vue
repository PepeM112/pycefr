<template>
  <aside class="sidebar" :class="{ hidden: isSidebarHidden }">
    <h2>pycefr</h2>
    <div class="top-buttons ma-2">
      <v-btn icon density="comfortable">
        <v-icon color="white">mdi-theme-light-dark</v-icon>
      </v-btn>
      <v-btn icon density="comfortable" @click="toggleSidebar">
        <v-icon color="white">mdi-menu</v-icon>
      </v-btn>
    </div>
    <nav class="repos-wrapper">
      <a href="/">Home</a>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';

const emit = defineEmits<{
  (e: 'update:showMenu', value: boolean): void;
}>();
const props = defineProps<{
  showMenu?: boolean;
}>();

const isSidebarHidden = ref(props.showMenu ?? false);

function toggleSidebar() {
  isSidebarHidden.value = !isSidebarHidden.value;
  emit('update:showMenu', !isSidebarHidden.value);
}

onMounted(() => {
  toggleSidebar();
  toggleSidebar();
  emit('update:showMenu', !isSidebarHidden.value);
});
</script>

<style scoped lang="scss">
.sidebar {
  position: relative;
  background-color: rgb(var(--v-theme-primary));
  color: snow;
  min-height: 100vh;
  width: 240px;
  min-width: 240px;
  padding: 1rem 0.5rem;
  transition: all 0.25s ease;
}

h2 {
  font-size: 1.125rem;
  line-height: 1.75rem;
  margin: 0;
  padding-left: 0.5rem;
}

.hidden {
  width: 2.75rem;
  min-width: 2.75rem;
  padding: 0;

  > *:not(.top-buttons) {
    display: none;
  }

  .top-buttons {
    position: sticky;
    flex-direction: column-reverse;
    justify-content: center;

    #dark-mode-toggle {
      margin: 0;
    }
  }

  button.sidebar-toggle {
    padding: 0.25rem 0.5rem;
  }
}

.top-buttons {
  position: absolute;
  top: 0.5rem;
  right: 0;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

nav {
  display: flex;
  flex-direction: column;
  margin-top: 1.25rem;

  a {
    color: snow;
    border-radius: var(--border-radius);
    font-size: 0.875rem;
    font-weight: 500;
    line-height: 1.25rem;
    margin-bottom: 0.25rem;
    padding: 0.5rem;
    text-decoration: none;

    &:hover {
      background-color: var(--primary-color-light);
    }
  }
}
</style>
