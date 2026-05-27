import { nextTick, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { serializeFilterValue, deserializeFilterValue } from '@/utils/filter';
import { useQuery } from './useQuery';
import type { LocationQuery } from 'vue-router';
import type { FilterItem, FilterValue } from '@/types/filter';

/**
 * Orchestrates the synchronization between local filter state and the browser URL.
 */
export function useFilter(filterList: FilterItem[]) {
  const route = useRoute();
  const { updateQuery } = useQuery();

  const filters = ref<FilterValue>({});
  let isHydrating = true;

  /**
   * Updates query using filter values.
   *
   * Maps filter values to their 'query' aliases defined in filterList.
   */
  const syncToUrl = () => {
    const serializedEntries = filterList.flatMap(item => Object.entries(serializeFilterValue(item, filters.value)));

    const queryToUpdate = serializedEntries.reduce<LocationQuery>(
      (query, [key, val]) => {
        if (val === undefined) {
          delete query[key];
        } else if (Array.isArray(val)) {
          query[key] = val.map(String);
        } else {
          query[key] = String(val);
        }
        return query;
      },
      { ...route.query }
    );

    queryToUpdate.p = '1';

    void updateQuery(queryToUpdate);
  };

  /**
   * Updates filter values using query.
   *
   * Maps URL aliases back to local filter values.
   */
  const hydrateFromUrl = () => {
    filters.value = filterList.reduce<FilterValue>(
      (acc, item) => {
        const deserialized = deserializeFilterValue(item, route.query);
        if (deserialized !== undefined) acc[item.key] = deserialized;
        return acc;
      },
      { ...filters.value }
    );
  };

  hydrateFromUrl();
  void nextTick(() => {
    isHydrating = false;
  });

  watch(
    () => filters.value,
    () => {
      if (!isHydrating) syncToUrl();
    },
    { deep: true }
  );

  function getValue<R>(key: string): R | undefined {
    return filters.value[key] as R | undefined;
  }

  return { filters, getValue };
}
