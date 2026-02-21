import type { Ref } from 'vue';
import type { FilterEntity } from './filter';
import type { Primitive } from 'vuetify/lib/util';
/**
 * T : type of items used in the component
 *
 * R : type of raw data returned by the API
 */
export interface FetcherOptions<T extends Primitive | FilterEntity = Primitive | FilterEntity, R = T> {
  map?: (item: R) => T;
  compare?: (a: T, b: T) => boolean;
  lazy?: boolean;
  limit?: number; // Limit for the number of items to fetch from the API (by default API returns all items)
  debounce?: number; // Time in ms to debounce the fetch function
}

export interface ItemFetcher {
  items: Ref<Primitive[] | FilterEntity[]>;
  loading: Ref<boolean>;
  fetch: (search?: string, values?: any) => Promise<Primitive[] | FilterEntity[]>;
}
