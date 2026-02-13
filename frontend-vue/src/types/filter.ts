import type { Primitive } from 'vuetify/lib/util';

export type FilterItem = {
  label: string;
  key: string;
  type: FilterType;
  options?: FilterOptions;
};

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

export enum FilterType {
  SINGLE,
  MULTIPLE,
  SELECT,
  MULTIPLE_SELECT,
  DATE,
}
