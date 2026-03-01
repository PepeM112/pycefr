import { Level, type AnalysisClassPublic } from '@/client';

export type AnalysisClassPublicWithLevel = AnalysisClassPublic & { level: Level };

export type ChartFileItem = {
  name: string;
  fullPath: string;
  instances: number;
};

export type ChartCommitItem = {
  hash: string;
  filesCount: number;
  complexity: number;
};

export type ChartData = {
  items: AnalysisClassPublicWithLevel[];
  files: ChartFileItem[];
  commits: ChartCommitItem[];
};
