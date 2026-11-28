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
  const RATIO = 2377 / 1805; // le dessin d'origine, au centre de l'image élargie (img/intro-sign-wide-2.jpg)
  const DRAW = 2377, WIDE = 3599, LEFT = 605; // largeurs du dessin et de l'image élargie, début du dessin (px)
  const COVER = matchMedia('(hover: hover) and (pointer: fine)').matches; // ordinateur, à la souris
  const ANGLE = 22; // la même inclinaison que .corner-logo dans le CSS
  let geo = null, busy = false;

  function measure() {
    const cs = getComputedStyle(logo);
    const L = parseFloat(cs.left), T = parseFloat(cs.top), W = parseFloat(cs.width);
    const vw = innerWidth, vh = innerHeight;
    // À la souris (ordinateur), l'image élargie couvre tout l'écran (comme « cover ») : pas de bandes grises,
    // quitte à rogner ses bords. Au doigt (téléphone, tablette), le dessin entier, bord à bord sur un côté.
    const Wi = COVER ? Math.max(vw * DRAW / WIDE, vh * RATIO) : Math.min(vw, vh * RATIO);
    // Le dessin est posé à sa taille plein écran et ne fait que rétrécir vers le logo du coin :
    // jamais agrandi depuis une petite taille, il reste net (sinon certains navigateurs l'étirent, flou).
    // x0 : en plein écran, l'image élargie centrée (le dessin y commence à 605 px) ; sinon le dessin centré.
    const x0 = COVER ? (vw - Wi * WIDE / DRAW) / 2 + Wi * LEFT / DRAW : (vw - Wi) / 2;
    geo = { L, T, W, Wi, x0, y0: (vh - Wi / RATIO) / 2 };
    Object.assign(flyer.style, { left: L + 'px', top: T + 'px', width: Wi + 'px', height: Wi / RATIO + 'px' });
    flyer.style.transform = start();
  }
  const start = () => `translate(${geo.x0 - geo.L}px, ${geo.y0 - geo.T}px) scale(1) rotate(0deg)`;
  const end = () => `translate(0px, 0px) scale(${geo.W / geo.Wi}) rotate(${ANGLE}deg)`;

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
