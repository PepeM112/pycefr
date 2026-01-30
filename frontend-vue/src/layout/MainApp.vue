<template>
  <v-app>
    <sidebar v-model:showMenu="showSidebar" />
    <v-main class="m-app">
      <v-container fluid class="pa-0 fill-height align-start">
        <transition name="fade" mode="out-in">
          <router-view />
        </transition>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Sidebar from '@/components/Sidebar.vue';

const showSidebar = ref(true);
</script>

<style lang="scss" scoped></style>
