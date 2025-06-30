import { createApp } from 'vue';
import MainApp from '@/layout/MainApp.vue';
import vuetify from '@/plugins/vuetify';
import router from '@/router';
import '@mdi/font/css/materialdesignicons.css';

const app = createApp(MainApp);
app.use(vuetify);
app.use(router);
app.mount('#app');
