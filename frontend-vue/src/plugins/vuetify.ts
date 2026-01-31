import { Icon } from '@iconify/vue';
import { h } from 'vue';
import { createVuetify } from 'vuetify';
import 'vuetify/dist/vuetify.min.css';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

const savedTheme = localStorage.getItem('theme') || 'light';

export default createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
      iconify: {
        component: (props: any) => h(Icon, { ...props }),
      },
    },
  },
  defaults: {
    global: {
      ripple: false,
    },
    VBtn: {
      class: 'text-none',
      elevation: 0,
      rounded: 'md',
      style: 'text-transform: none; letter-spacing: normal;',
      variant: 'flat',
    },
    VCard: {
      class: 'border-thin',
      rounded: 'lg',
    },
    VIcon: {
      style: 'opacity: 1',
    },
    VTextField: {
      density: 'compact',
      hideDetails: 'auto',
      rounded: 'lg',
      variant: 'outlined',
    },
  },
  theme: {
    defaultTheme: savedTheme,
    themes: {
      light: {
        dark: false,
        colors: {
          background: '#f8fafc',
          surface: '#ffffff',
          'on-surface': '#1e293b',
          primary: '#1e293b',
          'primary-on-surface': '#1e293b',
          secondary: '#64748b',
          'secondary-light': '#94a3b8',
          error: '#ef4444',
          info: '#3b82f6',
          success: '#22c55e',
          'on-success': '#1e293b',
          warning: '#f59e0b',
          'on-warning': '#1e293b',
          text: '#1e293b',
          'border-color': '#1e293b',
        },
        variables: {
          'border-color': '#1e293b',
          'border-opacity': 0.12,
        },
      },
      dark: {
        dark: true,
        colors: {
          background: '#1e293b',
          surface: '#0f172a',
          'on-surface': '#ffffff',
          primary: '#0f172a',
          'primary-on-surface': '#ffffff',
          secondary: '#475569',
          'secondary-light': '#64748b',
          error: '#f87171',
          info: '#60a5fa',
          success: '#4ade80',
          'on-success': '#1e293b',
          warning: '#fbbf24',
          'on-warning': '#1e293b',
          text: '#ffffff',
          'border-color': '#94a3b8',
        },
        variables: {
          'border-color': '#94a3b8',
          'border-opacity': 0.5,
        },
      },
    },
  },
});
