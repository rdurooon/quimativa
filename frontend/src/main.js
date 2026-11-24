import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './styles/variables.css';
import './styles/global.css';
import './styles/animations.css';
import './styles/placeholders.css';
import './styles/popup.css';

createApp(App).use(createPinia()).use(router).mount('#app');
