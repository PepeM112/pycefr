import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { SortDirection } from '@/client';

export type Sorting<T extends string | number = string> = {
  column: T;
  direction: SortDirection;
};

export const useSorting = () => {
  const route = useRoute();
  const router = useRouter();

  const sortFilter = computed<Sorting>({
    get: () => {
      const rawDir = Number(route.query.s_d);
      const isValidDir = [SortDirection.UNKNOWN, SortDirection.ASC, SortDirection.DESC].includes(rawDir);
      return {
        column: typeof route.query.s_c === 'string' ? route.query.s_c : '',
        direction: isValidDir ? rawDir : SortDirection.UNKNOWN,
      };
    },
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

      if (query.p) query.p = '1';

      void router.replace({ query });
    },
  });

  return sortFilter;
};
