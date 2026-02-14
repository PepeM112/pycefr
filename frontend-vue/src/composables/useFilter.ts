import { watch, onMounted, type Ref, type ComputedRef } from 'vue';
import { useRoute } from 'vue-router';
import { useQuery } from './useQuery';
import { useFetchOnQuery } from './useFetchOnQuery';
import type { FilterItem, FilterValue } from '@/types/filter';

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
    const queryToUpdate: Record<string, any> = {};

    filterList.value.forEach(item => {
      const value = filters.value[item.key];
      // Only sync non-empty values
      if (value !== undefined && value !== null && value !== '' && !(Array.isArray(value) && value.length === 0)) {
        const urlKey = item.query || item.key;
        queryToUpdate[urlKey] = value;
      }
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
      const urlKey = item.query || item.key;
      const urlValue = route.query[urlKey];

      if (urlValue !== undefined && urlValue !== null) {
        // Fix: Cast LocationQueryValue | LocationQueryValue[] to your expected types
        if (Array.isArray(urlValue)) {
          // Filter out null values from the array to satisfy string[] or number[]
          newFilters[item.key] = urlValue.filter((v): v is string => v !== null);
        } else {
          newFilters[item.key] = urlValue as string;
        }
      }
    });

    filters.value = newFilters;
  };

  watch(
    filters,
    () => {
      syncToUrl();
    },
    { deep: true }
  );

  useFetchOnQuery(currentQuery, route.path, fetcher, {
    immediate: options.immediate ?? true,
    debounceWait: options.debounceWait ?? 400,
    ignoreParams: options.ignoreParams,
  });

  onMounted(() => {
    hydrateFromUrl();
  });

  return {
    currentQuery,
    updateQuery,
    syncToUrl,
  };
}
