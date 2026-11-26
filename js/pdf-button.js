/* Park Row Magazine — le bouton du PDF en haut de l'accueil.
   Au survol, la barre de papier journal remplit le bouton de gauche à droite (lente, rapide, lente)
   et reste tant que la souris est dessus. Quand la souris s'en va, elle se dissipe vers la droite.
   Si la souris part avant la fin du remplissage, le remplissage se termine d'abord, puis la barre part.
   Le dessin est en CSS (::before / ::after de .button--issue, découpés par --in et --out) ;
   ce script ne fait qu'animer ces deux valeurs. Sans lui, le bouton reste un bouton normal. */
(() => {
  'use strict';
  const btn = document.querySelector('.button--issue[data-label]');
  if (!btn || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  if (!(window.CSS && CSS.registerProperty !== undefined && CSS.supports('clip-path', 'inset(0 0 0 0)'))) return;

  const still = window.matchMedia('(prefers-reduced-motion: reduce)');
  const EASE = 'cubic-bezier(.7, 0, .3, 1)';
  const DUR = 530;
  let state = 'idle';            // idle → filling → full → leaving → idle
  let hovered = false;
  let anim = null;

  const set = (inV, outV) => {
    btn.style.setProperty('--in', inV + '%');
    btn.style.setProperty('--out', outV + '%');
  };

  const run = (prop, done) => {
    if (anim) anim.cancel();
    if (still.matches) { done(); return; }
    anim = btn.animate([{ [prop]: '0%' }, { [prop]: '100%' }], { duration: DUR, easing: EASE, fill: 'forwards' });
    anim.onfinish = () => { anim.cancel(); anim = null; done(); };
  };

  const fill = () => {
    state = 'filling';
    set(0, 0);
    run('--in', () => {
      set(100, 0);
      state = 'full';
      if (!hovered) leave();
    });
  };

  const leave = () => {
    state = 'leaving';
    run('--out', () => {
      set(0, 100);
      state = 'idle';
      if (hovered) fill();
    });
  };

  btn.classList.add('sweep-js');
  set(0, 100);
  btn.addEventListener('mouseenter', () => {
    hovered = true;
    if (state === 'idle') fill();
  });
  btn.addEventListener('mouseleave', () => {
    hovered = false;
    if (state === 'full') leave();
  });
})();
