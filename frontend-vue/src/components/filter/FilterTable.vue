<template>
  <v-table>
    <tbody>
      <tr v-for="filterItem in props.filterList" :key="filterItem.key">
        <th class="text-left" scope="row" style="width: 1px">{{ $t(filterItem.label) }}</th>
        <td class="bg-background" style="width: 100%">
          <filter-field
            v-model="filter[filterItem.key]"
            :type="filterItem.type"
            :label="$t(filterItem.label)"
            :options="filterItem.options"
          />
        </td>
      </tr>
    </tbody>
  </v-table>
</template>
<script setup lang="ts">
import type { FilterItem, FilterValue } from '@/components/filter';
import FilterField from './FilterField.vue';

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
::v-deep(.v-field__field input) {
  padding: 0;
}
</style>
