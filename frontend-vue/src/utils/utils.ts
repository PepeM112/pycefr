import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/es';

dayjs.extend(relativeTime);
dayjs.locale('es');

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

/**
 * Formats a date using the browser's local timezone.
 * @param value - Date in Date, String (ISO), or Timestamp format
 * @param format - Format pattern (e.g., 'DD-MM-YYYY')
 */
export function formatDate(
  value: Date | string | number | null | undefined,
  format: string = 'DD-MM-YYYY',
  relative: boolean = false
): string {
  if (!value) return 'N/A';

  const date = dayjs(value);

  if (!date.isValid()) {
    return 'Invalid date';
  }

  if (relative) {
    return date.fromNow();
  }

  return date.format(format);
}

// Manage dark mode
export function toggleDarkMode() {
  const body = document.body;

  const darkModeToggle = document.getElementById('dark-mode-toggle');
  if (!darkModeToggle) return;
  const icon = darkModeToggle.querySelector('i');
  if (!icon) return;

  const isDarkMode = body.classList.contains('dark-mode');

  if (isDarkMode) {
    body.classList.remove('dark-mode');
    icon.classList.remove('fa-sun');
    icon.classList.add('fa-moon');
    localStorage.setItem('dark-mode', 'false');
  } else {
    body.classList.add('dark-mode');
    icon.classList.remove('fa-moon');
    icon.classList.add('fa-sun');
    localStorage.setItem('dark-mode', 'true');
  }
}

export function checkDarkModeOnLoad() {
  const darkMode = localStorage.getItem('dark-mode') === 'true';
  if (darkMode) toggleDarkMode();
}
