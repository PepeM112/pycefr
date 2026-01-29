import { type ClassItem, classLabel } from '@/client';
import { ref } from 'vue';

const cache = ref<Array<ClassItem>>([]);

export function useClassLabel<T = ClassItem>(options?: { mapper?: (item: ClassItem) => T; force?: boolean }) {
  const items = ref<T[]>([]);
  const loading = ref<boolean>(false);

  async function fetch() {
    if (cache.value.length > 0 && !options?.force) {
      applyData(cache.value);
      return;
    }

    try {
      loading.value = true;
      const { data, error } = await classLabel();

      if (error) throw error;

      const results = data ?? [];
      cache.value = results;

      applyData(results);
    } catch (e) {
      console.error('Error loading labels:', e);
    } finally {
      loading.value = false;
    }
  }

  function applyData(data: ClassItem[]) {
    items.value = options?.mapper ? data.map(options.mapper) : (data as T[]);
  }

  return {
    items,
    loading,
    fetch,
  };
}
