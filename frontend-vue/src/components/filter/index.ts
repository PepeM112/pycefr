export type FilterItem = {
  label: string;
  key: string;
  type: FilterType;
  options?: FilterOptions;
};

export type FilterOptions = {
  items: string[] | number[] | { label: string; value: string | number }[];
};

export type FilterValue = Record<string, string | number | string[] | number[] | Date | undefined>;

export enum FilterType {
  TEXT,
  NUMBER,
  MULTIPLE_TEXT,
  MULTIPLE_NUMBER,
  SELECT_TEXT,
  SELECT_NUMBER,
  MULTIPLE_SELECT_TEXT,
  MULTIPLE_SELECT_NUMBER,
  DATE,
}
