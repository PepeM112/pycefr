import type { RouteLocationRaw } from 'vue-router';

export type MenuAction = {
  readonly label: string;
  readonly icon?: string;
  readonly to?: RouteLocationRaw;
  readonly onClick?: () => void;
};
