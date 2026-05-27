<template>
  <v-menu class="language-selector">
    <template #activator="{ props }">
      <v-btn v-bind="props" density="comfortable" :icon="`iconify:${langStore.currentFlag}`" variant="text" />
    </template>

    <v-list class="rounded-lg pa-0">
      <v-list-item
        v-for="lang in LANGUAGE_OPTIONS"
        :key="lang.code"
        class="px-3"
        density="comfortable"
        @click="changeLanguage(lang.code)"
      >
        <template #prepend>
          <v-icon :icon="`iconify:${lang.flag}`" size="20" />
        </template>
        <v-list-item-title>{{ t(lang.label) }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { useLangStore, type LanguageCode, LANGUAGE_OPTIONS } from '@/stores/langStore';

const { t } = useI18n();
const langStore = useLangStore();

function changeLanguage(code: LanguageCode) {
  langStore.setLanguage(code);
}
</script>
<style scoped lang="scss">
:deep(.v-list-item__prepend .v-list-item__spacer) {
  width: auto !important;
  min-width: unset !important;
  margin-inline-end: 12px !important;
}

:deep(.v-list-item-title) {
  font-size: 0.875rem !important;
  font-weight: 500;
}
</style>
