import { SortDirection } from '@/client';
import { ref, type Ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export type Sorting = {
  column: string;
  direction: SortDirection;
};

export type SortFilter = {
  sortingColumn: Ref<Sorting>;
  toggleSort: (column: string) => void;
};

export const useSortFilter = () => {
  const route = useRoute();
  const router = useRouter();

  const sortingColumn = ref<Sorting>({ column: '', direction: SortDirection.UNKNOWN });

  const toggleSort = (column: string) => {
    if (sortingColumn.value.column === column) {
      sortingColumn.value.direction =
        sortingColumn.value.direction === SortDirection.ASC ? SortDirection.DESC : SortDirection.ASC;
    } else {
      sortingColumn.value.column = column;
      sortingColumn.value.direction = SortDirection.ASC;
    }
    updateQueryParams();
  };

  const updateQueryParams = () => {
    const query: Record<string, any> = {
      ...route.query,
      sort_column: sortingColumn.value.column,
      sort_direction: sortingColumn.value.direction,
    };

    if (sortingColumn.value.direction === SortDirection.UNKNOWN) {
      delete query.sort_column;
      delete query.sort_direction;
    }

    router.push({ query });
  };

  return {
    sortingColumn,
    toggleSort,
  };
};
