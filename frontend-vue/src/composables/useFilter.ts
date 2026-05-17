import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import type { LocationQuery } from 'vue-router';
import { useQuery } from './useQuery';
import type { FilterItem, FilterValue } from '@/types/filter';
import { serializeFilterValue, deserializeFilterValue } from '@/utils/filter';

/**
 * Orchestrates the synchronization between local filter state and the browser URL.
 */
export function useFilter(filterList: FilterItem[]) {
  const route = useRoute();
  const { updateQuery } = useQuery();

  const filters = ref<FilterValue>({});

  /**
   * Updates query using filter values.
   *
   * Maps filter values to their 'query' aliases defined in filterList.
   */
  const syncToUrl = () => {
    const queryToUpdate: LocationQuery = { ...route.query };

    filterList.forEach(item => {
      const serialized = serializeFilterValue(item, filters.value);
      Object.entries(serialized).forEach(([key, val]) => {
        if (val === undefined) {
          delete queryToUpdate[key];
        } else if (Array.isArray(val)) {
          queryToUpdate[key] = val.map(String);
        } else {
          queryToUpdate[key] = String(val);
        }
      });
    });

    // Reset to page 1 when filters change
    queryToUpdate.p = '1';

    updateQuery(queryToUpdate);
  };

  /**
   * Updates filter values using query.
   *
   * Maps URL aliases back to local filter values.
   */
  const hydrateFromUrl = () => {
    const newFilters: FilterValue = { ...filters.value };

    filterList.forEach(item => {
      const deserialized = deserializeFilterValue(item, route.query);
      if (deserialized !== undefined) newFilters[item.key] = deserialized;
    });
    filters.value = newFilters;
  };

  hydrateFromUrl();

  watch(
    () => filters.value,
    () => syncToUrl(),
    { deep: true }
  );

  return filters;
}
