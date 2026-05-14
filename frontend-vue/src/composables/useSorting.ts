import { SortDirection } from '@/client';
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export type Sorting<T extends string | number = string> = {
  column: T;
  direction: SortDirection;
};

export const useSorting = (onQueryChange?: () => void) => {
  const route = useRoute();
  const router = useRouter();

  const sortFilter = computed<Sorting>({
    get: () => ({
      column: (route.query.s_c as string) || '',
      direction: route.query.s_d ? (Number(route.query.s_d) as SortDirection) : SortDirection.UNKNOWN,
    }),
    set: (newVal: Sorting) => {
      const isSameColumn = sortFilter.value.column === String(newVal.column);
      let nextDir: SortDirection;

      if (!isSameColumn) {
        nextDir = SortDirection.ASC;
      } else {
        nextDir = (sortFilter.value.direction + 1) % 3;
      }

      const query = { ...route.query };

      if (nextDir === SortDirection.UNKNOWN) {
        delete query.s_c;
        delete query.s_d;
      } else {
        query.s_c = String(newVal.column);
        query.s_d = String(nextDir);
      }

      if (query.p) query.p = '1'; // Reset page to 1 when sorting

      router.push({ query });
      if (onQueryChange) {
        onQueryChange();
      }
    },
  });

  return sortFilter;
};
