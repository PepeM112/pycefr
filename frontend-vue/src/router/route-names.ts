export const RouteNames = {
  HOME: 'home',
  ANALYSIS_DETAIL: 'analysis-detail',
  ANALYSIS_LIST: 'analysis-list',
} as const;

export type RouteName = (typeof RouteNames)[keyof typeof RouteNames];
