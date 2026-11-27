<script setup>
import { Heart } from '@lucide/vue';

defineProps({
  vidas: { type: Number, required: true },
});
</script>

<template>
  <div class="equipe-vidas" :class="{ 'ultima-vida': vidas === 1 }" role="img" :aria-label="`${vidas} ${vidas === 1 ? 'vida' : 'vidas'}`">
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
.ultima-vida svg:not(.coracao-leave-active) { animation: pulsar 900ms ease-in-out infinite; }
.equipe-vidas .coracao-leave-active { animation: perder-vida 950ms ease-out both; }
@keyframes pulsar {
  0%, 15%, 39%, 100% { transform: scale(1); }
  7% { transform: scale(1.23); }
  23% { transform: scale(1.13); }
}
@keyframes perder-vida {
  from { transform: scale(1); opacity: 1; }
  35% { transform: scale(1.45) rotate(-12deg); }
  to { transform: scale(.25) translateY(-14px); opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
  .equipe-vidas svg { animation: none !important; }
}
</style>
