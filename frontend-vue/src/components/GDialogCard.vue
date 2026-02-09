<template>
  <v-dialog
    v-model="localModel"
    :close-on-content-click="false"
    :persistent="true"
    :width="width"
    :min-width="width"
    :height="height"
    @keydown.esc="close"
  >
    <v-card rounded="lg" min-height="180" :width="width" :min-width="width" :disabled="innerLoading">
      <v-card-title v-if="title" class="py-3">
        <span class="font-weight-bold text-h5">{{ $t(title) }}</span>
        <br />
        <p
          v-if="subtitle"
          class="mt-2 font-weight-regular"
          style="font-size: 1rem; line-height: 1.25rem; white-space: normal"
        >
          {{ $t(subtitle) }}
        </p>
      </v-card-title>
      <v-divider v-if="title" />
      <v-card-text class="px-4">
        <slot>
          <template v-if="text">
            <p>{{ $t(text) }}</p>
          </template>
        </slot>
        <template v-if="confirmationKey">
          <v-divider class="my-2" />
          <p class="mb-2">
            {{ $t('type') }}
            <b>"{{ confirmationKey }}"</b>
            {{ $t('to_confirm') }}
          </p>
          <v-text-field v-model="confirmationKeyInput" density="compact" outlined hide-details />
        </template>
      </v-card-text>
      <v-divider />
      <v-card-actions>
        <slot name="actions">
          <v-btn variant="tonal" @click="close">
            {{ $t(cancelLabel) }}
          </v-btn>
          <v-btn
            color="primary-on-surface"
            variant="flat"
            :disabled="props.disableConfirm || (!!confirmationKey && confirmationKeyInput !== confirmationKey)"
            data-cy="confirm-dialog-btn-confirm"
            @click="confirm"
          >
            {{ $t(confirmLabel) }}
          </v-btn>
        </slot>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue';

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'confirmPost'): void;
  (e: 'closePost'): void;
}>();

const props = withDefaults(
  defineProps<{
    modelValue: boolean;
    width?: string;
    height?: string;
    title?: string;
    subtitle?: string;
    text?: string;
    confirmLabel?: string;
    cancelLabel?: string;
    confirmationKey?: string;
    disableConfirm?: boolean;
    // Will run BEFORE emitting events
    onConfirmPre?: () => Promise<void>;
    onClosePre?: () => Promise<void>;
  }>(),
  {
    width: '400px',
    height: 'auto',
    title: undefined,
    subtitle: undefined,
    text: undefined,
    confirmLabel: 'apply',
    cancelLabel: 'cancel',
    confirmationKey: undefined,
    onConfirmPre: undefined,
    onClosePre: undefined,
    disableConfirm: false,
  }
);

const confirmationKeyInput = ref<string | undefined>(undefined);
const innerLoading = ref(false);

const localModel = computed({
  get: () => props.modelValue,
  set: (val: boolean) => {
    emit('update:modelValue', val);
  },
});

async function confirm() {
  try {
    if (props.onConfirmPre) {
      innerLoading.value = true;
      await props.onConfirmPre();
      innerLoading.value = false;
    }
    emit('confirmPost');
    localModel.value = false;
  } catch (error) {
    innerLoading.value = false;
  }
}

async function close() {
  try {
    if (props.onClosePre) {
      innerLoading.value = true;
      await props.onClosePre();
      innerLoading.value = false;
    }
    emit('closePost');
    localModel.value = false;
  } catch (error) {
    innerLoading.value = false;
  }
}
</script>
