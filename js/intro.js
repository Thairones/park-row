/* Park Row Magazine — l'entrée.
   Une fois par visite, l'accueil s'ouvre sur le dessin du panneau en grand. Au clic
   (ou Entrée), le dessin rétrécit, se penche et glisse jusqu'au logo du coin en haut
   à gauche, qui prend le relais ; le voile s'efface et dévoile la page.
   Le script dans <head> pose la classe « intro » sur <html> pour éviter tout flash. */
(() => {
  'use strict';
  const root = document.documentElement;
  if (!root.classList.contains('intro')) return;

  const veil = document.querySelector('.intro-veil');
  const flyer = document.querySelector('.intro-flyer');
  const hint = document.querySelector('.intro-hint');
  const logo = document.querySelector('.corner-logo');
  if (!veil || !flyer || !logo) { root.classList.remove('intro'); return; }
  const full = flyer.querySelector('.intro-full');
  const cut = flyer.querySelector('.intro-cut');
  const RATIO = 1321 / 1003; // le dessin d'origine, au centre de l'image élargie
  const ANGLE = 22; // la même inclinaison que .corner-logo dans le CSS
  let geo = null, busy = false;

  function measure() {
    const cs = getComputedStyle(logo);
    const L = parseFloat(cs.left), T = parseFloat(cs.top), W = parseFloat(cs.width);
    const vw = innerWidth, vh = innerHeight;
    const Wi = Math.min(vw, vh * RATIO); // le dessin entier, bord à bord sur un côté
    geo = { L, T, W, x0: (vw - Wi) / 2, y0: (vh - Wi / RATIO) / 2, s0: Wi / W };
    Object.assign(flyer.style, { left: L + 'px', top: T + 'px', width: W + 'px', height: W / RATIO + 'px' });
    flyer.style.transform = start();
  }
  const start = () => `translate(${geo.x0 - geo.L}px, ${geo.y0 - geo.T}px) scale(${geo.s0}) rotate(0deg)`;
  const end = () => `translate(0px, 0px) scale(1) rotate(${ANGLE}deg)`;

  function finish() {
    root.classList.remove('intro');
    try { sessionStorage.setItem('pr-intro', '1'); } catch (e) { /* navigation privée */ }
  }

  function enter() {
    if (busy) return;
    busy = true;
    scrollTo(0, 0);
    measure();
    if (hint) hint.style.opacity = '0';
    const d = 1500;
    const move = flyer.animate([{ transform: start() }, { transform: end() }], { duration: d, easing: 'cubic-bezier(.65, 0, .25, 1)', fill: 'forwards' });
    full.animate([{ opacity: 1 }, { opacity: 1, offset: .12 }, { opacity: 0, offset: .45 }, { opacity: 0 }], { duration: d, fill: 'forwards' });
    cut.animate([{ opacity: 0 }, { opacity: 0, offset: .1 }, { opacity: 1, offset: .4 }, { opacity: 1 }], { duration: d, fill: 'forwards' });
    veil.animate([{ opacity: 1 }, { opacity: 1, offset: .2 }, { opacity: 0, offset: .75 }, { opacity: 0 }], { duration: d, fill: 'forwards' });
    move.finished.then(finish, finish);
  }

  measure();
  addEventListener('resize', () => { if (!busy) measure(); });
  [veil, flyer].forEach((el) => el.addEventListener('click', enter));
  addEventListener('keydown', (e) => {
    if (!root.classList.contains('intro')) return;
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); enter(); }
    if (e.key === 'Escape') finish();
  });
  flyer.focus({ preventScroll: true });
})();
