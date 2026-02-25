import { Level } from '@/client';

// File Extensions
export type FileExtension = 'py' | 'js' | 'ts' | 'vue' | 'html' | 'css' | 'json' | 'md';

const EXTENSION_ICON_MAP: Record<FileExtension, string> = {
  py: 'logos:python',
  js: 'logos:javascript',
  ts: 'logos:typescript-icon',
  vue: 'logos:vue',
  html: 'logos:html-5',
  css: 'logos:css-3',
  json: 'vscode-icons:file-type-json',
  md: 'logos:markdown',
};

export function getExtensionIcon(extension: FileExtension): string {
  return EXTENSION_ICON_MAP[extension];
}

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

export function getStatusColor(status: string): string {
  switch (status) {
    case 'completed':
      return 'success';
    case 'in_progress':
      return 'warning';
    case 'failed':
      return 'error';
    default:
      return 'grey';
  }
}
