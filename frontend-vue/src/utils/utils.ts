// File Extensions
export type FileExtension = 'py' | 'js' | 'ts' | 'vue' | 'html' | 'css' | 'json' | 'md';

const EXTENSION_ICON_MAP: Record<FileExtension, string> = {
  py: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg',
  js: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg',
  ts: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/typescript/typescript-original.svg',
  vue: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vuejs/vuejs-original.svg',
  html: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg',
  css: 'https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg',
  json: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/json/json-original.svg',
  md: 'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/markdown/markdown-original.svg',
};

export function getExtensionIcon(extension: FileExtension): string {
  return EXTENSION_ICON_MAP[extension];
}

// Formatting
export function formatDate(dateString: string) {
  const options = { day: '2-digit', month: '2-digit', year: 'numeric' } as Intl.DateTimeFormatOptions;
  const date = new Date(dateString);
  return date.toLocaleDateString('es-ES', options);
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
