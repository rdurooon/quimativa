<template>
  <TransitionOverlay />
  <div class="route-stage">
    <RouterView v-slot="{ Component }">
      <component :is="Component" />
    </RouterView>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted } from 'vue';
import TransitionOverlay from './components/TransitionOverlay.vue';
import { iniciarControlesTelaCheia } from './services/fullscreen';

let pararControles;
onMounted(() => { pararControles = iniciarControlesTelaCheia(); });
onBeforeUnmount(() => pararControles?.());
</script>

<style>
.route-stage {
  width: 100%;
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.route-stage > * {
  width: 100%;
  height: 100%;
}
</style>
