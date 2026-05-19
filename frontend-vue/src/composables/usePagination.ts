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
      total.value = newVal.total;

      const currentPage = Number(route.query.p) || 1;
      const currentPerPage = Number(route.query.pp) || defaultPerPage;
      const nextPage = currentPerPage !== newVal.perPage ? 1 : newVal.page;

      if (nextPage === currentPage && newVal.perPage === currentPerPage) return;

      const query = { ...route.query };
      query.p = String(nextPage);
      query.pp = String(newVal.perPage);
      router.replace({ query });
    },
  });
};
