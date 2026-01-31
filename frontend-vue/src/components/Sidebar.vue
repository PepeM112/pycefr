<template>
  <v-navigation-drawer
    :rail="!showMenu"
    permanent
    color="primary"
    width="240"
    disable-resize-watcher
    disable-route-watcher
  >
    <div class="d-flex align-center pa-2" :class="showMenu ? 'justify-space-between' : 'justify-center'">
      <h2 v-if="showMenu" class="ml-2 text-h6">pycefr</h2>

      <div class="d-flex" :class="{ 'flex-column-reverse ga-2': !showMenu }">
        <v-btn icon variant="text" density="comfortable" @click.stop="themeStore.toggleTheme">
          <v-icon
            :icon="
              themeStore.currentTheme === 'dark'
                ? 'iconify:solar:moon-stars-bold-duotone'
                : 'iconify:solar:sun-bold-duotone'
            "
          />
        </v-btn>

        <v-btn icon variant="text" density="comfortable" @click.stop="toggleSidebar">
          <v-icon>mdi-menu</v-icon>
        </v-btn>
      </div>
    </div>
    <v-divider v-if="showMenu" class="mb-2" style="opacity: 0.2"></v-divider>
    <v-list nav>
      <v-list-item to="/" prepend-icon="mdi-home" title="Home" class="text-white" />
    </v-list>

    <template #append>
      <div class="d-flex justify-end pr-1 pb-1">
        <language-selector />
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import LanguageSelector from '@/components/LanguageSelector.vue';
import { useThemeStore } from '@/stores/themeStore';

const themeStore = useThemeStore();

const showMenu = defineModel<boolean>('showMenu', { default: true });

function toggleSidebar() {
  showMenu.value = !showMenu.value;
}
</script>

<style scoped lang="scss">
.text-snow {
  color: snow;
}
</style>
