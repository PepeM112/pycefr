<template>
  <v-text-field
    v-if="type === FilterType.SINGLE"
    class="bg-transparent w-100 px-4"
    v-model="simpleModel"
    :type="props.options?.number ? 'number' : 'text'"
    clearable
    hide-details
    variant="plain"
    clear-icon="mdi-close"
    @keydown.enter.stop
  />

  <v-combobox
    v-else-if="type === FilterType.MULTIPLE"
    class="bg-transparent w-100 px-4"
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

  <v-autocomplete
    v-else-if="isSelectType"
    class="bg-transparent w-100 px-4"
    v-model="selectModel"
    :type="props.options?.number ? 'number' : 'text'"
    :items="sortedItems"
    :multiple="isMultiple"
    :chips="isMultiple"
    :closable-chips="isMultiple"
    :return-object="props.options?.returnObject"
    :item-title="(item: any) => $t(item[props.options?.itemTitle ?? 'title'])"
    :item-value="props.options?.itemValue"
    :custom-filter="trimmedStringFilter"
    clearable
    hide-details
    hide-selected
    hide-spin-buttons
    variant="plain"
    clear-icon="mdi-close"
    @keydown.enter.stop
  />

  <datetime-filter v-else-if="type === FilterType.DATE" v-model="dateModel" />
</template>

<script setup lang="ts">
import DatetimeFilter from '@/components/filter/DatetimeFilter.vue';
import type { DateFilterValue, FilterEntity, FilterOptions } from '@/types/filter';
import { FilterType } from '@/types/filter';
import { computed } from 'vue';
import type { Primitive } from 'vuetify/lib/util';
import { useI18n } from 'vue-i18n';

type modelTypes = Primitive | FilterEntity | Primitive[] | FilterEntity[] | undefined;

const emit = defineEmits(['update:modelValue']);

const { t } = useI18n();

const props = defineProps<{
  modelValue: modelTypes | DateFilterValue;
  type: FilterType;
  options?: FilterOptions;
}>();

const localModel = computed<modelTypes | DateFilterValue>({
  get: () => props.modelValue,
  set: val => emit('update:modelValue', val),
});

function remove(itemToRemove: any) {
  if (Array.isArray(localModel.value)) {
    // Si el modelo usa item-value (ej. IDs), comparamos el ID
    const valueKey = props.options?.itemValue || 'id';
    localModel.value = localModel.value.filter(i => {
      const val = typeof i === 'object' ? i[valueKey] : i;
      const target = typeof itemToRemove === 'object' ? itemToRemove[valueKey] : itemToRemove;
      return val !== target;
    });
  }
}

const simpleModel = computed({
  get: () => (Array.isArray(props.modelValue) ? undefined : props.modelValue),
  set: val => (localModel.value = val),
});

const arrayModel = computed<string[], unknown[]>({
  get: () => ensureStringArray(props.modelValue),
  set: val => (localModel.value = ensureStringArray(val)),
});

// Array if isMultiple
const selectModel = computed<modelTypes>({
  get: () => {
    if (isDateFilterValue(props.modelValue)) return undefined;
    if (isMultiple.value && !props.modelValue) return [];
    return props.modelValue;
  },
  set: (val: modelTypes) => (localModel.value = val),
});

const dateModel = computed<DateFilterValue | undefined>({
  get: () => (isDateFilterValue(props.modelValue) ? props.modelValue : undefined),
  set: val => (localModel.value = val),
});

const isMultiple = computed(() => [FilterType.MULTIPLE, FilterType.MULTIPLE_SELECT].includes(props.type));

const isSelectType = computed(() => [FilterType.SELECT, FilterType.MULTIPLE_SELECT].includes(props.type));

const sortedItems = computed(() => {
  if (!props.options?.items) return [];

  if (props.options?.sortItems) {
    return props.options.items.sort(props.options.sortItems);
  }

  const titleKey = props.options?.itemTitle ?? 'title';
  return [...props.options.items].sort((a, b) => {
    const labelA = t(String(a[titleKey as keyof typeof a] || ''));
    const labelB = t(String(b[titleKey as keyof typeof b] || ''));

    return labelA.localeCompare(labelB, undefined, { sensitivity: 'base' });
  });
});

function ensureStringArray(val?: unknown[] | unknown | null): string[] {
  if (!val) return [];

  const strArray = Array.isArray(val) ? val.map(String) : [String(val)];

  return [...new Set(strArray)];
}

function trimmedStringFilter(value: string, query: string, _item?: any) {
  return value.toLowerCase().includes(query.trim().toLowerCase());
}

function isDateFilterValue(val: any): val is DateFilterValue {
  return !!val && typeof val === 'object' && 'from' in val && 'to' in val;
}
</script>

<style lang="scss" scoped>
.filter-field {
  width: 100%;
}

:deep(.v-field) {
  display: flex;
  align-items: center;

  .v-field__append-inner,
  .v-field__clearable,
  .v-field__input {
    padding: 0 !important;
  }
}
</style>
