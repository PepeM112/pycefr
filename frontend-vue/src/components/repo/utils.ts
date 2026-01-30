import { ClassId, Level } from '@/client';

const LEVEL_COLOR_MAP: Record<Level, string> = {
  [Level.UNKNOWN]: 'rgba(201, 203, 207, 1)',
  [Level.A1]: 'rgba(255, 99, 132, 1)',
  [Level.A2]: 'rgba(255, 159, 64, 1)',
  [Level.B1]: 'rgba(255, 206, 86, 1)',
  [Level.B2]: 'rgba(75, 192, 192, 1)',
  [Level.C1]: 'rgba(54, 162, 235, 1)',
  [Level.C2]: 'rgba(153, 102, 255, 1)',
};

export function getLevelColor(level: Level): string {
  return LEVEL_COLOR_MAP[level];
}

// Tables
export enum SortDirection {
  UNKNOWN = 0,
  ASC = 1,
  DESC = 2,
}

export interface Header {
  text: string;
  value: string;
  sort?: boolean | ((a: any, b: any) => number);
  width?: string;
}

export interface Sorting {
  column: string;
  direction: SortDirection;
}

export interface RepoData {
  elements?: Record<string, TableDataItem[]>;
  repoInfo?: any;
}

export interface RepoProperties {
  name: string;
  data: TableData;
}

export interface TableData {
  headers: string[];
  items: TableDataItem[];
}

export interface TableDataItem {
  class: ClassId;
  level: Level;
  instances: number;
}
