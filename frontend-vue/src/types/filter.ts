import type { Primitive } from 'vuetify/lib/util';
import type { LocationQuery } from 'vue-router';
import type { ItemFetcher } from '@/types/fetcher';

export enum FilterType {
  SINGLE, // Single value, written by user
  MULTIPLE, // Multiple values, written by user
  SELECT, // Single value, selected from options
  MULTIPLE_SELECT, // Multiple values, selected from options
  DATE, // Date range, with "from" and "to" values
}

export type FilterMapping = {
  [FilterType.SINGLE]: Primitive;
  [FilterType.MULTIPLE]: Primitive[];
  [FilterType.SELECT]: Primitive | FilterEntity;
  [FilterType.MULTIPLE_SELECT]: Primitive[] | FilterEntity[];
  [FilterType.DATE]: DateFilterValue;
};

export type FilterItem = {
  [K in FilterType]: {
    label: string;
    key: string;
    type: K;
    query?: string;
    options?: FilterOptions;
    serializer?: (value: any) => Record<string, any>;
    deserializer?: (query: LocationQuery) => any;
  };
}[FilterType];

export type FilterEntity = {
  label: string;
  value: Primitive;
};

export type FilterOptions = {
  items?: Primitive[] | FilterEntity[];
  number?: boolean; // Limit filter values to numbers only. Meant to be used with Primitives
  returnObject?: boolean; // If true, model uses the full object, URL uses the value
  sortItems?: (a: Primitive | FilterEntity, b: Primitive | FilterEntity) => number;
  fetcher?: ItemFetcher;
};

export type FilterValue = Record<string, Primitive | Primitive[] | FilterEntity | FilterEntity[] | DateFilterValue>;

export type DateFilterValue = {
  from?: Date;
  to?: Date;
};
