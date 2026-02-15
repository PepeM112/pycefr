import { watch, type Ref, type ComputedRef } from 'vue';
import { useRoute } from 'vue-router';
import { useQuery } from './useQuery';
import { useFetchOnQuery } from './useFetchOnQuery';
import type { FilterItem, FilterValue } from '@/types/filter';
import { serializeFilterValue, deserializeFilterValue } from '@/utils/filter';

interface FilterOptions {
  debounceWait?: number;
  ignoreParams?: string[];
  immediate?: boolean;
}

/**
 * Orchestrates the synchronization between local filter state, the browser URL,
 * and API data fetching.
 */
export function useFilters(
  filters: Ref<FilterValue>,
  filterList: ComputedRef<FilterItem[]>,
  fetcher: () => Promise<void> | void,
  options: FilterOptions = {}
) {
  const route = useRoute();
  const { currentQuery, updateQuery } = useQuery();

  /**
   * Updates query using filter values.
   *
   * Maps filter values to their 'query' aliases defined in filterList.
   */
  const syncToUrl = () => {
    let queryToUpdate: Record<string, any> = {};

    filterList.value.forEach(item => {
      const serialized = serializeFilterValue(item, filters.value);
      queryToUpdate = { ...queryToUpdate, ...serialized };
    });

    updateQuery(queryToUpdate);
  };

  /**
   * Updates filter values using query.
   *
   * Maps URL aliases back to local filter values.
   */
  const hydrateFromUrl = () => {
    const newFilters: FilterValue = { ...filters.value };

    filterList.value.forEach(item => {
      const deserialized = deserializeFilterValue(item, route.query);
      if (deserialized === undefined) return;
      newFilters[item.key] = deserialized;
    });

    filters.value = newFilters;
  };

  // Keep hydrate before useFetchOnQuery to ensure filters are in sync with URL on initial load
  hydrateFromUrl();

  useFetchOnQuery(currentQuery, route.path, fetcher, {
    immediate: options.immediate ?? true,
    debounceWait: options.debounceWait ?? 400,
    ignoreParams: options.ignoreParams,
  });

  watch(
    filters,
    () => {
      syncToUrl();
    },
    { deep: true }
  );

  return {
    currentQuery,
    updateQuery,
    syncToUrl,
  };
}
