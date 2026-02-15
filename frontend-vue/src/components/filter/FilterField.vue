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
    :type="props.options?.number ? 'number' : 'text'"
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
    :items="sortedItems"
    :multiple="isMultiple"
    :chips="isMultiple"
    :closable-chips="isMultiple"
    :return-object="props.options?.returnObject"
    :custom-filter="trimmedStringFilter"
    item-title="label"
    item-value="value"
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
import type { DateFilterValue, FilterEntity, FilterMapping, FilterOptions } from '@/types/filter';
import { FilterType } from '@/types/filter';
import { isDateFilterValue, isFilterEntity, isPrimitiveValue, normalizeToFilterEntity } from '@/utils/filter';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Primitive } from 'vuetify/lib/util';

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
      return props.options?.returnObject
        ? arr.map(item => normalizeToFilterEntity(item))
        : arr
            .map(item => (isPrimitiveValue(item) ? item : isFilterEntity(item) ? item.value : undefined))
            .filter((v: Primitive | undefined) => v !== undefined);
    } else {
      if (Array.isArray(val)) {
        console.error('Expected single value for non-multiple filter, but got array. Using first item.', val);
      }
      const singleVal = Array.isArray(val) ? val[0] : val;

      if (props.options?.returnObject) return normalizeToFilterEntity(singleVal);
      else if (isPrimitiveValue(singleVal)) return singleVal;
      else if (isFilterEntity(singleVal)) return singleVal.value;
      else {
        console.error('Unexpected value type for select filter', val);
        return undefined;
      }
    }
  },
  set: val => (localModel.value = val),
});

const dateModel = computed<DateFilterValue | undefined>({
  get: () => (isDateFilterValue(props.modelValue) ? props.modelValue : undefined),
  set: val => (localModel.value = val),
});

const isMultiple = computed(() => [FilterType.MULTIPLE, FilterType.MULTIPLE_SELECT].includes(props.type));

const isSelectType = computed(() => [FilterType.SELECT, FilterType.MULTIPLE_SELECT].includes(props.type));

const sortedItems = computed<FilterEntity[]>(() => {
  if (!props.options?.items) return [];

  if (props.options?.sortItems) {
    return props.options.items.sort(props.options.sortItems).map(it => normalizeToFilterEntity(it));
  }

  const normalized = props.options.items.map(it => normalizeToFilterEntity(it));

  return normalized.sort((a, b) =>
    t(String(a.label)).localeCompare(t(String(b.label)), undefined, { sensitivity: 'base' })
  );
});

function trimmedStringFilter(value: string, query: string, _item?: any) {
  return value.toLowerCase().includes(query.trim().toLowerCase());
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
