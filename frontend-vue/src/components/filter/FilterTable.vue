<template>
  <v-table>
    <tbody>
      <tr v-for="filterItem in props.filterList" :key="filterItem.key">
        <th class="text-left" scope="row" style="width: 1px">{{ $t(filterItem.label) }}</th>
        <td class="bg-background px-0" style="width: 100%">
          <filter-field
            :model-value="filter[filterItem.key]"
            :type="filterItem.type"
            :options="filterItem.options"
            @update:model-value="val => (filter[filterItem.key] = val)"
          />
        </td>
      </tr>
    </tbody>
  </v-table>
</template>
<script setup lang="ts">
import FilterField from './FilterField.vue';
import type { FilterItem, FilterValue } from '@/types/filter';

const filter = defineModel<FilterValue>('filter', { required: true });
const props = withDefaults(
  defineProps<{
    filterList: FilterItem[];
  }>(),
  {
    filterList: () => [],
  }
);
</script>
<style scoped lang="scss">
th,
td {
  height: 46px !important;
}
:deep(.v-field__field input) {
  padding: 0;
}
</style>
