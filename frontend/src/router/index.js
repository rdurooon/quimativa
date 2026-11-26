import { createRouter, createWebHashHistory } from 'vue-router';

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: () => import('../views/IntroView.vue') },
    { path: '/menu', component: () => import('../views/MenuView.vue') },
    { path: '/game', component: () => import('../views/GameView.vue') },
    { path: '/game/quick', component: () => import('../views/QuickGameView.vue') },
  ],
});

export default router;
