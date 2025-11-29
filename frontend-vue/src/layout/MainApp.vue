<template>
  <v-app class="app-layout">
    <sidebar v-model:showMenu="showSidebar" />
    <v-main app class="m-app" :class="{ 'sidebar-hidden': !showSidebar }">
      <transition name="fade" mode="out-in">
        <v-container fluid class="main-container-app pa-0">
          <router-view />
        </v-container>
      </transition>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import Sidebar from '@/components/Sidebar.vue';

const showSidebar = ref<boolean>(true);

const sidebarWidth = computed(() => {
  return showSidebar.value ? '240px' : '44px';
});

</script>
<style lang="scss">
.app-layout {
  display: flex !important;
  flex-direction: row !important;
  min-height: 100vh;
  max-width: 100vw;
  width: 100vw;
}
.m-app {
  display: flex;
  flex: 1;
  overflow-y: auto;
  max-width: calc(100% - v-bind(sidebarWidth)) !important;
  transition: all 0.3 ease;

  &.sidebar-hidden {
    max-width: calc(100% - v-bind(sidebarWidth)) !important;
  }
}

.main-container-app {
  width: 100%;
  height: 100%;
}
</style>
<style>
.app-layout .v-application__wrap {
  flex-direction: unset !important;
}
</style>
