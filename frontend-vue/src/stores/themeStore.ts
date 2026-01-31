import { ref, watch } from 'vue';
import { defineStore } from 'pinia';
import { useTheme } from 'vuetify';

export const useThemeStore = defineStore('theme', () => {
  const savedTheme = localStorage.getItem('user-theme') as 'light' | 'dark' | null;
  const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  const currentTheme = ref<'light' | 'dark'>(savedTheme || (systemDark ? 'dark' : 'light'));

  function toggleTheme() {
    currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light';
  }

  function initTheme() {
    const vTheme = useTheme();
    vTheme.global.name.value = currentTheme.value;

    watch(
      currentTheme,
      newVal => {
        vTheme.global.name.value = newVal;
        localStorage.setItem('user-theme', newVal);
      },
      { immediate: true }
    );
  }

  return {
    currentTheme,
    toggleTheme,
    initTheme,
  };
});
