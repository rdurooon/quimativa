const COLORS = ['#006b10', '#008e15', '#31b84b', '#a8e3ae'];
const DEFAULT_COVER_DURATION = 1250;
const DEFAULT_REVEAL_DURATION = 1100;

export const GAME_TRANSITION = Object.freeze({
  coverDuration: 700,
  revealDuration: 650,
});

function random(seed) {
  const value = Math.sin(seed * 12.9898) * 43758.5453;
  return value - Math.floor(value);
}

function createEdge(seed, base, count, drops) {
  const points = [];
  for (let index = 0; index <= count; index += 1) {
    const x = (index / count) * 1000;
    let y = base + Math.sin(index * 0.72 + seed) * 13 + (random(seed + index * 3.7) - 0.5) * 18;
    drops.forEach((drop) => {
      const distance = Math.abs(x - drop.x);
      if (distance < drop.width) y += (1 - distance / drop.width) ** 2 * drop.height;
    });
    points.push(`${x.toFixed(1)} ${y.toFixed(1)}`);
  }
  return points;
}

function smooth(points) {
  let path = `M${points[0]}`;
  for (let index = 1; index < points.length - 1; index += 1) {
    const current = points[index].split(' ');
    const next = points[index + 1].split(' ');
    path += ` Q${points[index]} ${((Number(current[0]) + Number(next[0])) / 2).toFixed(1)} ${((Number(current[1]) + Number(next[1])) / 2).toFixed(1)}`;
  }
  return `${path} Q${points.at(-1)} ${points.at(-1)}`;
}

function massPath(index) {
  const drops = Array.from({ length: 6 }, (_, dropIndex) => ({
    x: 55 + random(index * 23 + dropIndex + 1) * 890,
    width: 13 + random(index * 29 + dropIndex + 5) * 26,
    height: 45 + random(index * 41 + dropIndex + 9) * 105,
  }));
  const top = createEdge(index + 20, 32 + index * 5, 28, []);
  const bottom = createEdge(index + 2, 1160 + index * 9, 28, drops).reverse();
  return `${smooth(top)} L1000 1400 ${smooth(bottom).replace(/^M/, 'L')} Z`;
}

function createLayer(index) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 1000 1400');
  svg.setAttribute('preserveAspectRatio', 'none');
  svg.classList.add('transicao-camada');
  svg.innerHTML = `<path fill="${COLORS[index]}" d="${massPath(index)}"/>${
    index === 2
      ? '<g class="transicao-quimica"><circle class="transicao-bolha-svg" cx="230" cy="500" r="10"/><circle class="transicao-bolha-svg" cx="810" cy="720" r="6"/><path class="transicao-molecula" d="m640 470 28-16 28 16v32l-28 16-28-16z m28-16v-28 m28 44 26 15 m-54 13-25 16"/></g>'
      : ''
  }`;
  return svg;
}

export function initializeTransition({
  coverDuration = DEFAULT_COVER_DURATION,
  revealDuration = DEFAULT_REVEAL_DURATION,
} = {}) {
  const root = document.documentElement;
  let overlay = document.querySelector('.transicao-liquido');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'transicao-liquido';
    overlay.setAttribute('aria-hidden', 'true');
    document.body.prepend(overlay);
  }
  root.style.setProperty('--duracao-cobrir', `${coverDuration}ms`);
  root.style.setProperty('--duracao-revelar', `${revealDuration}ms`);
  if (!overlay.querySelector('.transicao-camada')) {
    COLORS.forEach((_, index) => overlay.appendChild(createLayer(index)));
  }
  const layers = Array.from(overlay.querySelectorAll('.transicao-camada'));

  function waitForAnimation(layer, fallbackDelay) {
    return new Promise((resolve) => {
      let finished = false;
      const finish = () => {
        if (finished) return;
        finished = true;
        layer.removeEventListener('animationend', finish);
        resolve();
      };
      layer.addEventListener('animationend', finish, { once: true });
      window.setTimeout(finish, fallbackDelay);
    });
  }

  return {
    cover: () => new Promise((resolve) => {
      root.classList.remove('transicao-coberta', 'transicao-revelando');
      root.classList.add('transicao-entrada');
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        window.setTimeout(resolve, 250);
        return;
      }
      waitForAnimation(layers[3] || overlay, coverDuration + 400).then(resolve);
    }),
    reveal: () => {
      root.classList.remove('transicao-entrada');
      root.classList.add('transicao-revelando');
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        window.setTimeout(() => {
          root.classList.remove('transicao-revelando', 'transicao-coberta');
        }, 250);
        return;
      }
      waitForAnimation(layers[0] || overlay, revealDuration + 300).then(() => {
        root.classList.remove('transicao-revelando', 'transicao-coberta');
      });
    },
  };
}
