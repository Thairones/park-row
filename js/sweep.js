/* Park Row Magazine — la barre de papier journal au survol, sur l'accueil.
   Le dessin est en CSS (voir « Titre survolé » et « Survol du bouton » dans park-row.css) ;
   ce script anime les valeurs qui découpent les couches, et fait toujours aller chaque passage
   jusqu'au bout, même si la souris part ou revient en cours de route.
   - Titres des articles : la barre traverse le titre et se dissipe vers la droite, le titre passe
     en machine à écrire. Souris partie : une nouvelle barre fait le même trajet et rend la police normale.
   - Bouton du PDF : la barre remplit le bouton et reste tant que la souris est dessus,
     puis se dissipe vers la droite.
   Sans ce script (ou au doigt sur téléphone), titres et bouton restent normaux. */
(() => {
  'use strict';
  if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  if (!(window.CSS && CSS.registerProperty && Element.prototype.animate)) return;

  const still = window.matchMedia('(prefers-reduced-motion: reduce)');
  const EASE_IN = 'cubic-bezier(.7, 0, .3, 1)';   // la barre avance : lente, rapide, lente
  const EASE_OUT = 'cubic-bezier(.6, 0, .4, 1)';  // elle se dissipe
  const GROW = 530, FADE = 320;

  // anime une valeur en % de 0 à 100 sur el, puis appelle done
  const tween = (el, prop, ms, ease, done) => {
    el.style.setProperty(prop, '0%');
    if (still.matches) { el.style.setProperty(prop, '100%'); done(); return; }
    const a = el.animate([{ [prop]: '0%' }, { [prop]: '100%' }], { duration: ms, easing: ease, fill: 'forwards' });
    a.onfinish = () => { el.style.setProperty(prop, '100%'); a.cancel(); done(); };
  };

  // Titres : idle → in (aller) → shown (machine à écrire) → back (retour) → idle
  if (window.matchMedia('(min-width: 600px)').matches) {
    document.querySelectorAll('.story-title a[data-title]').forEach((el) => {
      let state = 'idle', hovered = false;
      const pass = (back, done) => {
        el.classList.toggle('sweep-back', back);
        el.style.setProperty('--tail', '0%');
        tween(el, '--edge', GROW, EASE_IN, () => tween(el, '--tail', FADE, EASE_OUT, done));
      };
      const goIn = () => { state = 'in'; pass(false, () => { state = 'shown'; if (!hovered) goBack(); }); };
      const goBack = () => {
        state = 'back';
        pass(true, () => {
          el.classList.remove('sweep-back');
          el.style.setProperty('--edge', '0%');
          el.style.setProperty('--tail', '0%');
          state = 'idle';
          if (hovered) goIn();
        });
      };
      el.classList.add('sweep-js');
      el.addEventListener('mouseenter', () => { hovered = true; if (state === 'idle') goIn(); });
      el.addEventListener('mouseleave', () => { hovered = false; if (state === 'shown') goBack(); });
    });
  }

  // Bouton du PDF : idle → filling → full → leaving → idle
  const btn = document.querySelector('.button--issue[data-label]');
  if (btn) {
    let state = 'idle', hovered = false;
    const set = (i, o) => { btn.style.setProperty('--in', i + '%'); btn.style.setProperty('--out', o + '%'); };
    const fill = () => {
      state = 'filling';
      set(0, 0);
      tween(btn, '--in', GROW, EASE_IN, () => { state = 'full'; if (!hovered) leave(); });
    };
    const leave = () => {
      state = 'leaving';
      tween(btn, '--out', GROW, EASE_IN, () => { set(0, 100); state = 'idle'; if (hovered) fill(); });
    };
    btn.classList.add('sweep-js');
    set(0, 100);
    btn.addEventListener('mouseenter', () => { hovered = true; if (state === 'idle') fill(); });
    btn.addEventListener('mouseleave', () => { hovered = false; if (state === 'full') leave(); });
  }
})();
