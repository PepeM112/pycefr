import { ref } from 'vue';
import { getOwners } from '@/client';
import { useSnackbarStore } from '@/stores/snackbarStore';
import type { ItemFetcher, FetcherOptions } from '@/types/fetcher';
import type { FilterEntity } from '@/types/filter';

export function useOwnerFetcher(options: FetcherOptions = {}): ItemFetcher {
  const items = ref<FilterEntity[]>([]);
  const loading = ref(false);

  let timeoutId: number | null = null;

  async function fetch(search?: string) {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }

    if (options.lazy && items.value.length > 0 && !search) {
      return items.value;
    }

    const executeFetch = async () => {
      try {
        loading.value = true;
        const { data, error } = await getOwners({ query: { search, limit: options.limit } });

        if (error) throw error;

        items.value =
          data?.map(owner => ({
            label: owner.label,
            value: owner.id,
          })) ?? [];

        return items.value;
      } catch (e) {
        useSnackbarStore().add({ color: 'error', text: 'error.fetching.owners' });
        return [];
      } finally {
        loading.value = false;
      }
    };

    if (search && options.debounce) {
      return new Promise<FilterEntity[]>(resolve => {
        timeoutId = window.setTimeout(async () => {
          const result = await executeFetch();
          resolve(result || []);
        }, options.debounce);
      });
    }

    return executeFetch();
  }

  return { items, loading, fetch };
}
