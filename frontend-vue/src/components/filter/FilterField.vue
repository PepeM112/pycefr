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
import type { DateFilterValue, FilterEntity, FilterOptions, FilterMapping } from '@/types/filter';
import { FilterType } from '@/types/filter';
import { computed } from 'vue';
import type { Primitive } from 'vuetify/lib/util';
import { useI18n } from 'vue-i18n';

const emit = defineEmits(['update:modelValue']);

const { t } = useI18n();

const props = defineProps<{
  modelValue: FilterMapping[FilterType] | undefined;
  type: FilterType;
  options?: FilterOptions;
}>();

const localModel = computed({
  get: () => props.modelValue,
  set: val => emit('update:modelValue', val),
});

const simpleModel = computed<Primitive | undefined>({
  get: () => (isPrimitiveValue(props.modelValue) ? props.modelValue : undefined),
  set: (val: Primitive | undefined) => (localModel.value = val),
});

const arrayModel = computed<Primitive[] | undefined>({
  get: () => {
    if (!props.modelValue || isDateFilterValue(props.modelValue)) return undefined;
    const aux = Array.isArray(props.modelValue) ? props.modelValue : [props.modelValue];
    return aux.filter(val => isPrimitiveValue(val));
  },
  set: val => (localModel.value = val),
});

/*
FilterEntity if return-object
Array if multiple
*/
const selectModel = computed<Primitive | FilterEntity | Primitive[] | FilterEntity[] | undefined>({
  get: () => {
    const val = props.modelValue;
    if (!val || isDateFilterValue(val)) return undefined;

    if (isMultiple.value) {
      const arr = Array.isArray(val) ? val : [val];
      return props.options?.returnObject ? arr.filter(isFilterEntity) : arr.filter(isPrimitiveValue);
    }

    if (props.options?.returnObject) return isFilterEntity(val) ? val : undefined;
    return isPrimitiveValue(val) ? val : undefined;
  },
  set: val => (localModel.value = val),
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

function trimmedStringFilter(value: string, query: string, _item?: any) {
  return value.toLowerCase().includes(query.trim().toLowerCase());
}

function isDateFilterValue(val: any): val is DateFilterValue {
  return !!val && typeof val === 'object' && 'from' in val && 'to' in val;
}

function isPrimitiveValue(val: any): val is Primitive {
  if (val === null) return true;

  const type = typeof val;
  return ['string', 'number', 'boolean', 'bigint', 'symbol'].includes(type);
}

function isFilterEntity(val: any): val is FilterEntity {
  return !!val && typeof val === 'object' && typeof val.label === 'string' && isPrimitiveValue(val.value);
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
