import { ref } from 'vue';
import { useSnackbarStore } from '@/stores/snackbarStore';
import type { FetcherOptions, ItemFetcher } from '@/types/fetcher';
import type { FilterEntity } from '@/types/filter';

type ApiFn = (params: { query: { search?: string; limit?: number } }) => Promise<{ data?: unknown; error?: unknown }>;

type MapperFn<T> = (items: T[]) => FilterEntity[];

export function createFetcher<T>(
  apiFn: ApiFn,
  mapper: MapperFn<T>,
  errorKey: string,
  options: FetcherOptions = {}
): ItemFetcher {
  const items = ref<FilterEntity[]>([]);
  const isLoading = ref(false);

  let timeoutId: number | null = null;

  async function fetch(search?: string) {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }

    if (options.isLazy && items.value.length > 0 && !search) {
      return items.value;
    }

    const executeFetch = async () => {
      try {
        isLoading.value = true;
        const { data, error } = await apiFn({ query: { search, limit: options.limit } });

        if (error) throw error;

        items.value = data ? mapper(data as T[]) : [];
        return items.value;
      } catch {
        useSnackbarStore().add({ color: 'error', text: errorKey });
        return [];
      } finally {
        isLoading.value = false;
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

  return { items, isLoading, fetch };
}
