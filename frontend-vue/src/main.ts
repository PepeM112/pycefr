import { createApp } from 'vue';
import MainApp from '@/layout/MainApp.vue';
import vuetify from '@/plugins/vuetify';
import i18n from '@/plugins/i18n';
import router from '@/router';
import CountryFlag from 'vue-country-flag-next';

import '@mdi/font/css/materialdesignicons.css';

const app = createApp(MainApp);
app.component('CountryFlag', CountryFlag)
app.use(vuetify);
app.use(i18n);
app.use(router);
app.mount('#app');
