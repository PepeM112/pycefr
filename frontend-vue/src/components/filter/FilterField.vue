<template>
  <div class="filter-field">
    <v-text-field
      class="bg-transparent"
      v-if="type === FilterType.TEXT || type === FilterType.NUMBER"
      v-model="simpleModel"
      :type="type === FilterType.NUMBER ? 'number' : 'text'"
      clearable
      hide-details
      variant="plain"
      clear-icon="mdi-close"
      @keydown.enter.stop
      @click:clear="model = undefined"
    />

    <v-select
      v-else-if="isSelectType"
      class="bg-transparent"
      v-model="model"
      :items="props.options?.items || []"
      :multiple="isMultiple"
      :chips="isMultiple"
      :closable-chips="isMultiple"
      clearable
      hide-details
      variant="plain"
      clear-icon="mdi-close"
      @keydown.enter.stop
      @click:clear="model = isMultiple ? [] : undefined"
    />

    <v-combobox
      v-else-if="type === FilterType.MULTIPLE_TEXT || type === FilterType.MULTIPLE_NUMBER"
      class="bg-transparent"
      v-model="arrayModel"
      multiple
      chips
      closable-chips
      clearable
      hide-details
      variant="plain"
      clear-icon="mdi-close"
      :delimiters="[',', ' ']"
      @keydown.enter.stop
    >
      <template #no-data>
        <div class="d-none"></div>
      </template>
    </v-combobox>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { FilterType, type FilterOptions } from '@/components/filter';

const props = defineProps<{ type: FilterType; label: string; options?: FilterOptions }>();

const model = defineModel<string | number | string[] | number[] | Date | undefined>();

const simpleModel = computed({
  get: () => (Array.isArray(model.value) || model.value instanceof Date ? undefined : model.value),
  set: val => {
    model.value = val;
  },
});

const arrayModel = computed<unknown[]>({
  get: () => (Array.isArray(model.value) ? (model.value as any[]) : []),
  set: val => {
    ensureCorrectTypes(val);
  },
});

const isMultiple = computed(() =>
  [
    FilterType.MULTIPLE_SELECT_TEXT,
    FilterType.MULTIPLE_SELECT_NUMBER,
    FilterType.MULTIPLE_TEXT,
    FilterType.MULTIPLE_NUMBER,
  ].includes(props.type)
);

const isSelectType = computed(() =>
  [
    FilterType.SELECT_TEXT,
    FilterType.SELECT_NUMBER,
    FilterType.MULTIPLE_SELECT_TEXT,
    FilterType.MULTIPLE_SELECT_NUMBER,
  ].includes(props.type)
);

function ensureCorrectTypes(val: unknown[] | null) {
  if (!val) {
    model.value = [];
    return;
  }

  if (props.type === FilterType.MULTIPLE_NUMBER) {
    const numbers = val
      .map((v): number | null => {
        if (typeof v === 'number') return v;
        if (typeof v === 'string') {
          const trimmed = v.trim().replace(',', '.');
          if (trimmed === '') return null;

          const parsed = Number(trimmed);
          return isNaN(parsed) ? null : parsed;
        }
        return null;
      })
      .filter((v): v is number => v !== null);

    model.value = [...new Set(numbers)];
  } else if (props.type === FilterType.MULTIPLE_TEXT) {
    const strings = val.map(v => String(v).trim()).filter(v => v !== '');

    model.value = [...new Set(strings)];
  }
}
</script>

<style lang="scss" scoped>
.filter-field {
  width: 100%;
}

:deep(.v-field--focused) {
  box-shadow: 0 0 0 2px rgba(var(--v-theme-primary), 0.1);
}

:deep(.v-field) {
  display: flex;
  align-items: center;

  .v-field__input {
    padding: 0;
  }

  .v-field__clearable {
    padding: 0 !important;
  }
}
</style>
