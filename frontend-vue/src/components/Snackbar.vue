<template>
  <v-snackbar
    v-model="active"
    location="top right"
    color="transparent"
    variant="text"
    elevation="0"
    :timeout="-1"
    opacity="0"
    flat
    content-class="pa-0"
    :z-index="99999"
  >
    <v-alert
      v-for="snack in displayMessages"
      :key="snack.id"
      class="mb-2 elevation-4"
      :class="{ 'cursor-pointer': !!snack.onClick }"
      :color="snack.color || 'success'"
      :icon="snack.icon"
      density="compact"
      @click="snack.onClick?.()"
    >
      <div class="d-flex align-center">
        <div class="flex-grow-1">
          <v-alert-title v-if="snack.title" class="text-subtitle-1 font-weight-bold">
            {{ $t(snack.title) }}
          </v-alert-title>
          <div class="text-body-2">{{ $t(snack.text) }}</div>
        </div>

        <v-btn
          v-if="snack.closable"
          :icon="snack.closeIcon"
          variant="text"
          density="comfortable"
          size="small"
          @click.stop="snackbarStore.remove(snack.id)"
        />
      </div>
    </v-alert>
  </v-snackbar>
</template>

<script lang="ts" setup>
import { computed } from 'vue';
import { useSnackbarStore } from '@/stores/snackbarStore';

const snackbarStore = useSnackbarStore();

const active = computed(() => snackbarStore.messages.length > 0);

const displayMessages = computed(() => [...snackbarStore.messages].reverse().slice(0, 5));
</script>

<style scoped>
:deep(.v-snackbar__content) {
  padding: 0 !important;
}
</style>
