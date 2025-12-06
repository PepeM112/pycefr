<template>
  <v-menu v-model="isMenuOpen" class="language-selector">
    <template #activator="{ props }">
      <button v-bind="props" class="d-flex justify-center align-center">
        <country-flag
          :country="getLanguageFlag(selectedLanguage)"
          style="
            margin: 0em -0.9em -0.6em;
            transform: scale(0.35) translate(0, -25%);
            -webkit-transform: scale(0.35) translate(0, -25%);
          "
        />
      </button>
      <v-list v-if="isMenuOpen" class="rounded-lg">
        <v-list-item
          v-for="option in languageOptions"
          :key="option.code"
          class="pl-0"
          style="cursor: pointer"
          @click="changeLanguage(option.code)"
        >
          <country-flag class="ml-1" :country="option.flag || option.code" size="small" style="transform: scale(0.4)" />
          <span class="ml-3">{{ t(option.label) }}</span>
        </v-list-item>
      </v-list>
    </template>
  </v-menu>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { locale, t } = useI18n();

const selectedLanguage = ref<string>(locale.value);
const isMenuOpen = ref(false);

const languageOptions = [
  { code: 'en', label: 'english', flag: 'gb' },
  { code: 'es', label: 'spanish' },
];

function getLanguageFlag(code: string): string {
  const option = languageOptions.find(opt => opt.code === code);
  return option?.flag || code;
}

function changeLanguage(code: string) {
  selectedLanguage.value = code;
  locale.value = code;
}
</script>
<style lang="scss"></style>
