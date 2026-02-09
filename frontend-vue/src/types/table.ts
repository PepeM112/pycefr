export type TableHeader = {
  readonly label: string;
  readonly key: string;
  readonly width?: string;
  readonly sortColumn?: number | string; // Meant to be number for Enums, but allow string for flexibility
  readonly align?: 'start' | 'center' | 'end';
};
