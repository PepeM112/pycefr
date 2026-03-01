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

  const pagination = computed<Pagination>({
    get: () => ({
      page: Number(route.query.p) || 1,
      perPage: Number(route.query.pp) || defaultPerPage,
      total: total.value,
    }),
    set: (value: Pagination) => {
      const query = { ...route.query };

      // If perPage changes, we reset page to 1. Otherwise, we keep the current page.
      const oldPerPage = Number(route.query.pp) || defaultPerPage;
      const perPageChanged = oldPerPage !== value.perPage;
      const nextP = perPageChanged ? 1 : value.page;

      // Update 'p'
      if (nextP <= 1) {
        delete query.p;
      } else {
        query.p = String(nextP);
      }

      // Update 'pp'
      if (value.perPage === defaultPerPage) {
        delete query.pp;
      } else {
        query.pp = String(value.perPage);
      }

      // Update internal total
      total.value = value.total;

      router.push({ query });
    },
  });

  return pagination;
};
