import MainApp from '@/layout/MainApp.vue';
import i18n from '@/plugins/i18n';
import vuetify from '@/plugins/vuetify';
import router from '@/router';
import { useLangStore } from '@/stores/langStore';
import { createPinia } from 'pinia';
import { createApp } from 'vue';
import './assets/styles/globals.scss';
import { client } from './client/client.gen';

client.setConfig({
  baseUrl: 'http://localhost:8000',
});

import '@mdi/font/css/materialdesignicons.css';

const app = createApp(MainApp);
const pinia = createPinia();
app.use(pinia);
app.use(vuetify);
app.use(i18n);
app.use(router);

const langStore = useLangStore();
langStore.initLanguage();

app.mount('#app');
