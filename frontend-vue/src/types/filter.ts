import type { Primitive } from 'vuetify/lib/util';

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
  };
}[FilterType];

export type FilterEntity = {
  label: string;
  value: Primitive;
};

export type FilterOptions = {
  items: Primitive[] | FilterEntity[];
  number?: boolean;
  returnObject?: boolean;
  itemTitle?: string;
  itemValue?: string;
  sortItems?: (a: Primitive | FilterEntity, b: Primitive | FilterEntity) => number;
};

export type FilterValue = Record<string, string | number | string[] | number[] | undefined>;

export type DateFilterValue = {
  from?: Date;
  to?: Date;
};
