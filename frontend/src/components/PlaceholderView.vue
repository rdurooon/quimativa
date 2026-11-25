<script setup>
import { nextTick, onMounted } from 'vue';
import { ArrowLeft } from '@lucide/vue';
import { useRouter } from 'vue-router';
import { GAME_TRANSITION, initializeTransition } from '../services/transition';

const props = defineProps({
  title: { type: String, required: true },
  description: { type: String, required: true },
  icon: { type: [Object, Function], required: true },
  animatedBack: { type: Boolean, default: false },
});

const router = useRouter();
let transition;

async function voltar() {
  if (transition) await transition.cover();
  await router.push('/menu');
  if (transition) {
    await nextTick();
    transition.reveal();
  }
}

onMounted(() => {
  if (props.animatedBack) transition = initializeTransition(GAME_TRANSITION);
});
</script>

<template>
  <main class="placeholder-view">
    <button class="placeholder-voltar" type="button" aria-label="Voltar ao menu" @click="voltar">
      <ArrowLeft aria-hidden="true" />
      <span>Voltar</span>
    </button>
    <component :is="icon" aria-hidden="true" />
    <h1>{{ title }}</h1>
    <p>{{ description }}</p>
  </main>
</template>
