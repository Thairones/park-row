/* Park Row Magazine — la barre de papier journal au survol, sur l'accueil.
   Le dessin est en CSS (voir « Titre survolé » et « Survol du bouton » dans park-row.css) ;
   ce script anime les valeurs qui découpent les couches, et fait toujours aller chaque passage
   jusqu'au bout, même si la souris part ou revient en cours de route.
   - Titres des articles : la barre traverse le titre et se dissipe vers la droite, le titre passe
     en machine à écrire. Souris partie : une nouvelle barre fait le même trajet et rend la police normale.
   - Bouton du PDF : la barre remplit le bouton et reste tant que la souris est dessus,
     puis se dissipe vers la droite.
   - Au doigt (téléphone, tablette), pas de survol : toucher un titre ou le bouton joue l'animation
     (le titre passe en machine à écrire, le bouton se remplit), puis la page s'ouvre.
   Sans ce script, titres et bouton restent normaux. */
(() => {
  'use strict';
  if (!(window.CSS && CSS.registerProperty && Element.prototype.animate)) return;
  const mouse = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const touch = !mouse && window.matchMedia('(hover: none), (pointer: coarse)').matches;
  if (!mouse && !touch) return;
  // un clic « normal » (pas d'ouverture dans un nouvel onglet, etc.)
  const plain = (e) => e.button === 0 && !e.metaKey && !e.ctrlKey && !e.shiftKey && !e.altKey;

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

  // Un titre long, en machine à écrire, peut être plus large que sa place (plus large que le titre normal) :
  // on réduit alors la taille de sa version machine à écrire juste assez pour qu'elle tienne, sans rien déplacer.
  const ruler = document.createElement('span');
  ruler.setAttribute('aria-hidden', 'true');
  ruler.style.cssText = "position:absolute;left:-9999px;top:0;white-space:nowrap;visibility:hidden;font:400 22px/1.25 'Special Elite','Courier New',monospace";
  const fit = (titles) => {
    document.body.appendChild(ruler);
    titles.forEach((el) => {
      const head = el.closest('.story-head');
      const credit = head && head.querySelector('.story-credit');
      if (!head) return;
      el.style.setProperty('--tw-size', '1px');               // mesurer la place sans la version machine à écrire
      ruler.textContent = el.dataset.title;
      const tw = ruler.getBoundingClientRect().width;
      ruler.style.font = getComputedStyle(el).font;          // largeur du titre normal, seul
      ruler.textContent = el.dataset.title;
      const base = ruler.getBoundingClientRect().width;
      ruler.style.font = "400 22px/1.25 'Special Elite','Courier New',monospace";
      const gap = parseFloat(getComputedStyle(head).columnGap) || 0;
      const inline = head.clientWidth - (credit ? credit.getBoundingClientRect().width + gap : 0);
      const room = base <= inline ? inline : head.clientWidth;   // le crédit reste sur la ligne du titre, si c'était déjà le cas
      if (tw > room) el.style.setProperty('--tw-size', (22 * room / tw).toFixed(2) + 'px');
      else el.style.removeProperty('--tw-size');
    });
    ruler.remove();
  };

  // Au doigt : la version machine à écrire, posée par-dessus le titre, à la taille qui donne la même longueur
  // de texte que le titre normal, pour que les lignes se coupent au même endroit.
  const fitTap = (titles) => {
    document.body.appendChild(ruler);
    titles.forEach((el) => {
      ruler.style.font = "400 22px/1.25 'Special Elite','Courier New',monospace";
      ruler.textContent = el.dataset.title;
      const tw = ruler.getBoundingClientRect().width;
      ruler.style.font = getComputedStyle(el.querySelector('span')).font;
      const base = ruler.getBoundingClientRect().width;
      el.style.setProperty('--tw-size', (22 * base / tw).toFixed(2) + 'px');
    });
    ruler.remove();
  };

  if (touch) {
    const titles = document.querySelectorAll('.story-title a[data-title]');
    (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => fitTap(titles));
    titles.forEach((el) => {
      let busy = false;
      el.classList.add('sweep-tap');
      el.addEventListener('click', (e) => {
        if (!plain(e)) return;
        e.preventDefault();
        if (busy) return;
        busy = true;
        el.style.setProperty('--tail', '0%');
        tween(el, '--edge', GROW, EASE_IN, () => tween(el, '--tail', FADE, EASE_OUT, () => { location.href = el.href; }));
      });
      // retour arrière (page gardée en mémoire) : le titre redevient normal
      window.addEventListener('pageshow', () => { busy = false; el.style.setProperty('--edge', '0%'); el.style.setProperty('--tail', '0%'); });
    });
  }

  // Titres : idle → in (aller) → shown (machine à écrire) → back (retour) → idle
  if (mouse && window.matchMedia('(min-width: 600px)').matches) {
    const titles = document.querySelectorAll('.story-title a[data-title]');
    const refit = () => fit(titles);
    (document.fonts ? document.fonts.ready : Promise.resolve()).then(refit);
    let t; window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(refit, 150); });
    titles.forEach((el) => {
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
    if (mouse) {
      btn.addEventListener('mouseenter', () => { hovered = true; if (state === 'idle') fill(); });
      btn.addEventListener('mouseleave', () => { hovered = false; if (state === 'full') leave(); });
    } else {
      // au doigt : le bouton se remplit, puis le PDF s'ouvre
      btn.addEventListener('click', (e) => {
        if (!plain(e)) return;
        e.preventDefault();
        if (state !== 'idle') return;
        state = 'filling';
        set(0, 0);
        tween(btn, '--in', GROW, EASE_IN, () => { location.href = btn.href; });
      });
      window.addEventListener('pageshow', () => { state = 'idle'; set(0, 100); });
    }
  }
})();
