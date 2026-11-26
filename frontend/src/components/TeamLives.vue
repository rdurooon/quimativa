<script setup>
import { Heart } from '@lucide/vue';

defineProps({
  vidas: { type: Number, required: true },
});
</script>

<template>
  <div class="equipe-vidas" role="img" :aria-label="`${vidas} ${vidas === 1 ? 'vida' : 'vidas'}`">
    <TransitionGroup name="coracao">
      <Heart v-for="vida in vidas" :key="vida" aria-hidden="true" />
    </TransitionGroup>
  </div>
</template>

<style scoped>
.equipe-vidas {
  display: flex;
  justify-content: center;
  gap: 5px;
  flex-shrink: 0;
  color: var(--cor-principal);
}
.equipe-vidas svg {
  width: clamp(14px, 1.65cqw, 21px);
  height: clamp(14px, 1.65cqw, 21px);
  fill: currentColor;
}
.coracao-leave-active { animation: perder-vida 450ms ease-out both; }
@keyframes perder-vida {
  35% { transform: scale(1.45) rotate(-12deg); }
  to { transform: scale(.25) translateY(-14px); opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
  .coracao-leave-active { animation: none; }
}
</style>
