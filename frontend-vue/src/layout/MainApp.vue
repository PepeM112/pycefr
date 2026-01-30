<template>
  <v-app>
    <sidebar v-model:showMenu="showSidebar" />
    <v-main class="m-app">
      <transition name="fade" mode="out-in">
        <router-view />
      </transition>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import { useThemeStore } from '@/stores/themeStore';

const showSidebar = ref(true);

const themeStore = useThemeStore();

themeStore.initTheme();
</script>

<style lang="scss" scoped></style>
