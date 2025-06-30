<template>
  <v-app class="app-layout">
    <sidebar v-model:showMenu="menu" />
    <v-main app class="m-app">
      <transition name="fade" mode="out-in">
        <v-container fluid class="main-container-app pa-0">
          <router-view />
        </v-container>
      </transition>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
const menu = ref(false);
</script>
<style lang="scss">
.app-layout {
  display: flex !important;
  flex-direction: row !important;
  min-height: 100vh;
  width: 100vw;
}
.m-app {
  display: flex;
  flex: 1;
  overflow-y: auto;
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
