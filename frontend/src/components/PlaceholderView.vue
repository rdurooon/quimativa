<script setup>
import { ArrowLeft } from '@lucide/vue';
import { useRouter } from 'vue-router';

defineProps({
  title: { type: String, required: true },
  description: { type: String, required: true },
  icon: { type: [Object, Function], required: true },
});

const router = useRouter();

function voltar() {
  router.push('/menu');
}
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
