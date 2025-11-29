import 'vuetify/dist/vuetify.min.css';
import { createVuetify } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

export default createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  defaults: {
    global: {
      ripple: false,
    },
    VBtn: {
      elevation: 0,
      rounded: 'md',
      variant: 'text',
      style: 'text-transform: none; letter-spacing: normal;',
    },
    VCard: {
      rounded: 'lg',
    },
    VIcon: {
      style: 'opacity: 1',
    },
    
    VTextField: {
      density: 'compact',
      variant: 'outlined',
      hideDetails: 'auto',
      rounded: 'lg',
    }
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1f2937',
          'primary-light': '#374151',
          secondary: '#e2e8f0',
          'secondary-light': '#e5e7eb',
          error: '#f44336',
          info: '#2196f3',
          success: '#4caf50',
          warning: '#ff9800',
        },
      },
      dark: {
        colors: {
          primary: '#d1d5db',
          'primary-light': '#e5e7eb',
          secondary: '#4b5563',
          'secondary-light': '#6b7280',
          error: '#ef5350',
          info: '#42a5f5',
          success: '#66bb6a',
          warning: '#ffa726',
        },
      },
    },
  },
});
