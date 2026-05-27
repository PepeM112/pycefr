import { ref } from 'vue';
import { type ClassPublic, classLabel, Level } from '@/client';

const cache = ref<Array<ClassPublic>>([]);

export function useClassLabel(options?: { isForce?: boolean }) {
  const items = ref<ClassPublic[]>([]);
  const isLoading = ref<boolean>(false);

  async function fetch() {
    if (cache.value.length > 0 && !options?.isForce) {
      items.value = cache.value;
      return;
    }

    try {
      isLoading.value = true;
      const { data, error } = await classLabel();

      if (error) throw error;

      const results = data ?? [];
      cache.value = results;
      items.value = results;
    } catch (e) {
      console.error('Error loading labels:', e);
    } finally {
      isLoading.value = false;
    }
  }

  function getClassLevel(classId: number): Level {
    return cache.value.find(item => item.id === classId)?.level ?? Level.UNKNOWN;
  }

  return {
    items,
    isLoading,
    fetch,
    getClassLevel,
  };
}
