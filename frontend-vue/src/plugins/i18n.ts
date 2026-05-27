import { createI18n } from 'vue-i18n';
import { messages } from '@/locales/locales';

const savedLocale = localStorage.getItem('user-lang');
const initialLocale = savedLocale && savedLocale in messages ? savedLocale : 'en';

export default createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: 'en',
  messages: messages,
});
