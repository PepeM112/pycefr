import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { Pagination } from '@/client';

export interface PaginationOptions {
  defaultPerPage?: number;
}

export const usePagination = (options: PaginationOptions = {}) => {
  const route = useRoute();
  const router = useRouter();
  const defaultPerPage = options.defaultPerPage ?? 10;

  // The 'total' does not live in the URL, we keep it in a local reactive state
  const total = ref(0);

  return computed<Pagination>({
    get: () => ({
      page: Number(route.query.p) || 1,
      perPage: Number(route.query.pp) || defaultPerPage,
      total: total.value,
    }),
    set: newVal => {
      const query = { ...route.query };
      // If perPage changes, reset to page 1
      query.p = (Number(route.query.pp) || defaultPerPage) !== newVal.perPage ? '1' : String(newVal.page);
      query.pp = String(newVal.perPage);

      total.value = newVal.total;
      router.push({ query });
    },
  });
};
