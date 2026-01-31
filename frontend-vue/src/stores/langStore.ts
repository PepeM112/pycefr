import { ref, computed } from 'vue';
import dayjs from 'dayjs';
import 'dayjs/locale/en';
import 'dayjs/locale/es';
import { defineStore } from 'pinia';

/*
Multiple packs available. Right now using:
https://icon-sets.iconify.design/flagpack/
*/

export const LANGUAGE_OPTIONS = [
  { code: 'en', label: 'english', flag: 'flagpack:gb-ukm' },
  { code: 'es', label: 'spanish', flag: 'flagpack:es' },
] as const;

export type LanguageCode = (typeof LANGUAGE_OPTIONS)[number]['code'];

export interface LanguageOption {
  code: LanguageCode;
  label: string;
  flag: string;
}

export const useLangStore = defineStore('lang', () => {
  const currentLang = ref<LanguageCode>(
    (localStorage.getItem('user-lang') || navigator.language.split('-')[0] || 'en') as LanguageCode
  );

  const currentFlag = computed(() => {
    return LANGUAGE_OPTIONS.find(opt => opt.code === currentLang.value)?.flag || 'gb';
  });

  function setLanguage(lang: LanguageCode) {
    const exists = LANGUAGE_OPTIONS.some(opt => opt.code === lang);
    if (exists) {
      currentLang.value = lang;
      dayjs.locale(lang);
      localStorage.setItem('user-lang', lang);
    }
  }

  function initLanguage() {
    const savedLang = localStorage.getItem('user-lang') as LanguageCode;

    const isValid = LANGUAGE_OPTIONS.some(opt => opt.code === savedLang);

    if (savedLang && isValid) {
      setLanguage(savedLang);
    } else {
      setLanguage(currentLang.value);
    }
  }

  return {
    currentLang,
    currentFlag,
    setLanguage,
    initLanguage,
  };
});
