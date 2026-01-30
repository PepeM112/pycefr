import { ref, watch } from 'vue';
import { defineStore } from 'pinia';
import { useTheme } from 'vuetify';

export const useThemeStore = defineStore('theme', () => {
  const vTheme = useTheme();

  const savedTheme = localStorage.getItem('user-theme') as 'light' | 'dark' | null;
  const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  const currentTheme = ref<'light' | 'dark'>(savedTheme || (systemDark ? 'dark' : 'light'));

  function toggleTheme() {
    currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light';
    syncTheme();
  }

  function syncTheme() {
    vTheme.global.name.value = currentTheme.value;
    localStorage.setItem('user-theme', currentTheme.value);
  }

  function initTheme() {
    syncTheme();
  }

  return {
    currentTheme,
    toggleTheme,
    initTheme,
  };
});
