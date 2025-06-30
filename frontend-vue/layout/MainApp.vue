<template>
  <v-app>
    <sidebar v-model:showMenu="menu" />
    <v-main app class="m-app">
      <transition name="fade" mode="out-in">
        <v-container fluid class="main-container-app" style="max-width: 1676px">
          <router-view />
        </v-container>
      </transition>
    </v-main>
  </v-app>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
const menu = ref(false);
</script>
<style lang="scss">
.m-app {
  background-color: rgb(var(--v-theme-appBk));
}
</style>
