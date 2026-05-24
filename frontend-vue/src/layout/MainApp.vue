<template>
  <v-app>
    <sidebar v-model:show-menu="showSidebar" />

    <v-main class="m-app">
      <transition name="fade" mode="out-in">
        <router-view />
      </transition>
    </v-main>

    <Snackbar />
  </v-app>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import dayjs from 'dayjs';
import Sidebar from '@/components/Sidebar.vue';
import Snackbar from '@/components/Snackbar.vue';
import { useThemeStore } from '@/stores/themeStore';

const { locale } = useI18n();

const showSidebar = ref(true);
const themeStore = useThemeStore();

themeStore.initTheme();

watch(
  locale,
  newLocale => {
    dayjs.locale(newLocale);
  },
  { immediate: true }
);
</script>
