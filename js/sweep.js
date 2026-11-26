/* Park Row Magazine — la barre de papier journal au survol, sur l'accueil.
   Le dessin est en CSS (voir « Titre survolé » et « Survol du bouton » dans park-row.css) ;
   ce script anime les valeurs qui découpent les couches, et fait toujours aller chaque passage
   jusqu'au bout, même si la souris part ou revient en cours de route.
   - Titres des articles et bouton du PDF : la barre remplit le titre / le bouton (le titre en machine à écrire
     dessus) et reste tant que la souris est dessus, puis se dissipe vers la droite.
   - Au doigt (téléphone, tablette), pas de survol : toucher un titre ou le bouton le remplit, puis la page s'ouvre.
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
  const GROW = 530;

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

  // Remplir / vider : même logique pour un titre (--edge / --tail) et pour le bouton (--in / --out).
  // idle → filling → full → leaving → idle ; le remplissage va toujours au bout, puis la barre part si la souris est partie.
  const filler = (el, R, L) => {
    let state = 'idle', hovered = false;
    const set = (r, l) => { el.style.setProperty(R, r + '%'); el.style.setProperty(L, l + '%'); };
    const rest = () => { set(0, 0); state = 'idle'; };
    const fill = (then) => {
      state = 'filling';
      set(0, 0);
      tween(el, R, GROW, EASE_IN, () => { state = 'full'; if (then) then(); else if (!hovered) leave(); });
    };
    const leave = () => {
      state = 'leaving';
      tween(el, L, GROW, EASE_IN, () => { rest(); if (hovered) fill(); });
    };
    rest();
    if (mouse) {
      el.addEventListener('mouseenter', () => { hovered = true; if (state === 'idle') fill(); });
      el.addEventListener('mouseleave', () => { hovered = false; if (state === 'full') leave(); });
    } else {
      // au doigt : remplir, puis ouvrir la page
      el.addEventListener('click', (e) => {
        if (!plain(e)) return;
        e.preventDefault();
        if (state === 'idle') fill(() => { location.href = el.href; });
      });
      window.addEventListener('pageshow', rest);   // retour arrière : de nouveau normal
    }
  };

  const titles = document.querySelectorAll('.story-title a[data-title]');
  if (touch) {
    (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => fitTap(titles));
    titles.forEach((el) => { el.classList.add('sweep-tap'); filler(el, '--edge', '--tail'); });
  } else if (window.matchMedia('(min-width: 600px)').matches) {
    const refit = () => fit(titles);
    (document.fonts ? document.fonts.ready : Promise.resolve()).then(refit);
    let t; window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(refit, 150); });
    titles.forEach((el) => { el.classList.add('sweep-js'); filler(el, '--edge', '--tail'); });
  }

  // Bouton du PDF
  const btn = document.querySelector('.button--issue[data-label]');
  if (btn) {
    btn.classList.add('sweep-js');
    filler(btn, '--in', '--out');
  }
})();
