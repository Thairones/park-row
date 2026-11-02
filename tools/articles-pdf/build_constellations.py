# Construit articles/the-constellations.html depuis « Article EN.pdf » (Word → PDF, italique simulé).
import os, re, sys, html, warnings
warnings.filterwarnings('ignore')
import pymupdf
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdf_oblique import italic_lookup

PDF = r'C:\Users\Thairone\Downloads\Telegram Desktop\Article EN.pdf'
SP = os.path.dirname(os.path.abspath(__file__))
ROOT = r'C:\Users\Thairone\Desktop\park row'
SLUG = 'the-constellations'
IMG = os.path.join(ROOT, 'img', SLUG)
os.makedirs(IMG, exist_ok=True)
doc = pymupdf.open(PDF)

def ref(n):
    return f'<sup class="noteref"><a href="#note-{n}" id="ref-{n}">{n}</a></sup>'

# ---------- images ----------
def export(xref, name):
    pix = pymupdf.Pixmap(doc, xref)
    if pix.alpha: pix = pymupdf.Pixmap(pix, 0)
    if pix.n - pix.alpha >= 4: pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    im = Image.frombytes('RGB' if pix.n >= 3 else 'L', (pix.width, pix.height), pix.samples).convert('RGB')
    if im.width > 1200:
        im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
    im.save(os.path.join(IMG, name), quality=88)
    return im.size

def one(xref, name, alt, cap, cls='fig', style=''):
    w, h = export(xref, name)
    st = f' style="{style}"' if style else ''
    return (f'<figure class="{cls}"{st}>\n  <img src="../img/{SLUG}/{name}" alt="{alt}" width="{w}" height="{h}" loading="lazy">\n'
            f'  <figcaption>{cap}</figcaption>\n</figure>')

def pair(items, cell, cap):
    tags = []
    for xref, name, alt in items:
        w, h = export(xref, name)
        tags.append(f'<img src="../img/{SLUG}/{name}" alt="{alt}" width="{w}" height="{h}" loading="lazy">')
    return (f'<figure class="fig fig--pair">\n  <div class="fig-grid" style="--cell: {cell}">{"".join(tags)}</div>\n'
            f'  <figcaption>{cap}</figcaption>\n</figure>')

def end_prince():
    # dessin de fin : fond transparent (masque SMask), sinon le fond sort en noir
    pix = pymupdf.Pixmap(pymupdf.Pixmap(doc, 80), pymupdf.Pixmap(doc, 79))
    name = '14-the-little-prince.png'
    pix.save(os.path.join(IMG, name))
    old = os.path.join(IMG, '14-the-little-prince.jpg')
    if os.path.exists(old): os.remove(old)
    return (f'<figure class="fig fig--end-prince">\n  <img src="../img/{SLUG}/{name}" alt="The Little Prince and the fox, seen from behind, under the stars" width="{pix.width}" height="{pix.height}" loading="lazy">\n'
            f'  <figcaption><em>The Little Prince</em>, Antoine de Saint-Exupéry (1943)</figcaption>\n</figure>')

SH = 'Jean-Marie Straub and Danièle Huillet'
FIGS = [  # (page, y de tri, html)
    (2, 382, pair([(6, '01-machorka-muff-telephone.jpg', 'Still from Machorka-Muff: a hand leaves a telephone'),
                   (4, '02-machorka-muff-too-late.jpg', 'Still from Machorka-Muff with the subtitle “… I’d arrived too late …”')], '7 / 5',
                  f'<em>Machorka-Muff</em> (1963) by {SH}')),
    (3, 280, one(10, '03-angelus-novus.jpg', 'Angelus Novus, drawing by Paul Klee', '<em>Angelus Novus</em> (1920) by Paul Klee', 'fig fig--narrow', 'max-width: 380px')),
    (4, 401, one(14, '04-anna-magdalena-bach.jpg', 'A woman at the harpsichord reading a score',
                 f'<em>Chronicle of Anna Magdalena Bach</em> by {SH}{ref(8)}')),
    (7, 71, one(25, '05-machorka-muff-energies.jpg', 'A city at night with the subtitle “There are energies out there not yet realized.”',
                f'<em>Machorka-Muff</em> (1963) by {SH}', 'fig fig--narrow')),
    (8, 299, pair([(30, '06-the-ground-capturing.jpg', 'Hands holding a stone in The Ground'),
                   (32, '07-the-ground-manufacture.jpg', 'A man seen from behind, raising a hammer, in The Ground')], '4 / 3',
                  f'Capturing a form [left], manufacture of the image [right]: <em>The Ground</em> (2001) by Robert Beavers{ref(17)}')),
    (8, 510, one(34, '08-swain.jpg', 'A small object on a pink surface in Swain',
                 f'Interdependence of the manipulation of the image and of matter: <em>Swain</em> (1950) by Gregory Markopoulos{ref(18)}', 'fig fig--narrow')),
    (12, 71, pair([(51, '09-from-the-cloud-to-the-resistance.jpg', 'A dead animal on a rock'),
                   (52, '10-en-rachachant.jpg', 'A boy sitting at a school desk')], '4 / 3',
                  f'<em>From the Cloud to the Resistance</em> (1979) [left] and <em>En rachâchant</em> (1982) [right] by {SH}')),
    (14, 418, one(59, '11-those-encounters-of-theirs.jpg', 'Two men among trees in a forest',
                  f'<em>Those Encounters of Theirs</em> (2006) by {SH}{ref(42)}', 'fig fig--narrow')),
    (16, 71, pair([(67, '12-from-today-until-tomorrow.jpg', 'Still with the subtitle “Well, that can change between today and tomorrow.”'),
                   (69, '13-lothringen.jpg', 'A woman looking over a valley, with the subtitle “Is it exclusive to many a German?”')], '4 / 3',
                  f'<em>From Today Until Tomorrow</em> (1997) [left] and <em>Lothringen!</em> (1994) [right] by {SH}')),
    (19, 379, end_prince()),
]

# page de titre du PDF : le ciel étoilé (transparent, agrandi et rogné comme dans le PDF) et le Petit Prince
MOBILE_PRINCE_TOP, MOBILE_SKY_H = 62, 158                     # en cqw, repris dans le style de .title-page
def title_page():
    page = doc[0]
    stars = pymupdf.Pixmap(pymupdf.Pixmap(doc, 679), pymupdf.Pixmap(doc, 678))
    stars.save(os.path.join(SP, 'en_stars_full.png'))
    im = Image.open(os.path.join(SP, 'en_stars_full.png'))
    info = {i['xref']: i['bbox'] for i in page.get_image_info(xrefs=True)}
    x0, y0, x1, y1 = info[679]
    sx, sy = im.width / (x1 - x0), im.height / (y1 - y0)
    # Le ciel reste cadré comme dans le PDF (avec ses deux étoiles en traînée à gauche du dessin), sauf :
    #  - les étoiles coupées par le haut de la page, cachées derrière le dessin ou qui touchent le texte de l'en-tête ;
    #  - quelques étoiles entières ajoutées en haut, là où c'était vide.
    for f in ('00-hand-star-1.png', '00-hand-star-2.png', '00-star-trail.png'):
        if os.path.exists(os.path.join(IMG, f)): os.remove(os.path.join(IMG, f))
    W = page.rect.width
    cq = lambda v: v / 100 * W                               # cqw → points du PDF (page de 595 pt de large)
    px0, py0, px1, py1 = info[681]
    prince_box = (px0, py0, px1, py1)                        # .title-prince { top: 77.77cqw } = sa place dans le PDF
    # lignes de texte de l'en-tête, mesurées dans le navigateur à 760 px de large (en cqw), avec une marge de 1,5 cqw
    HEAD = [(30.03, 7.52, 69.96, 10.29), (10.17, 13.20, 89.83, 22.28), (35.10, 22.11, 64.90, 24.87), (25.48, 29.23, 74.52, 31.99)]
    head_boxes = [(cq(a - 1.5), cq(b - 1.5), cq(c + 1.5), cq(d + 1.5)) for a, b, c, d in HEAD]
    hits = lambda g, r: g[0] < r[2] and g[2] > r[0] and g[1] < r[3] and g[3] > r[1]
    alpha = im.getchannel('A').load()
    seen = set()
    for yy in range(im.height):
        for xx in range(im.width):
            if alpha[xx, yy] <= 20 or (xx, yy) in seen: continue
            stack, pts = [(xx, yy)], []
            seen.add((xx, yy))
            while stack:
                p = stack.pop(); pts.append(p)
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        q = (p[0] + dx, p[1] + dy)
                        if 0 <= q[0] < im.width and 0 <= q[1] < im.height and q not in seen and alpha[q] > 20:
                            seen.add(q); stack.append(q)
            ax0, ay0 = min(p[0] for p in pts), min(p[1] for p in pts)
            ax1, ay1 = max(p[0] for p in pts) + 1, max(p[1] for p in pts) + 1
            g = (x0 + ax0 / sx, y0 + ay0 / sy, x0 + ax1 / sx, y0 + ay1 / sy)   # en points du PDF
            if g[1] < 0 < g[3] or hits(g, prince_box) or any(hits(g, r) for r in head_boxes):
                im.paste((0, 0, 0, 0), (ax0 - 1, ay0 - 1, ax1 + 1, ay1 + 1))
    # étoiles ajoutées en haut (centres en cqw), prises dans le ciel lui-même ; ignorées si la place est prise
    src = Image.open(os.path.join(SP, 'en_stars_full.png'))
    SPRITES = [(366, 284, 384, 300), (236, 301, 252, 316), (181, 255, 198, 269), (233, 187, 249, 201),
               (106, 249, 122, 263), (455, 192, 469, 206), (208, 297, 222, 311)]
    ADD = [(12, 3.4), (37, 3.2), (63, 3.3), (88, 3.6), (4, 24), (96, 30), (50, 0.5 + 3.0)]
    alpha = im.getchannel('A').load()
    for (cx, cy), c in zip(ADD, SPRITES):
        sp = src.crop((c[0] - 1, c[1] - 1, c[2] + 2, c[3] + 2))
        ix = round((cq(cx) - x0) * sx - sp.width / 2); iy = round((cq(cy) - y0) * sy - sp.height / 2)
        g = (x0 + ix / sx, y0 + iy / sy, x0 + (ix + sp.width) / sx, y0 + (iy + sp.height) / sy)
        busy = any(alpha[xx, yy] > 20 for xx in range(max(0, ix - 4), min(im.width, ix + sp.width + 4))
                   for yy in range(max(0, iy - 4), min(im.height, iy + sp.height + 4)))
        if busy or g[1] < 0 or any(hits(g, r) for r in head_boxes):
            print('  étoile ajoutée ignorée', (cx, cy)); continue
        im.alpha_composite(sp, (ix, iy))
    # téléphone : fenêtre fixe dans le ciel d'origine (167 px du ciel = 100cqw), mise en page en cqw (voir CSS mobile) ;
    # on retire toute étoile qui touche le texte (mesuré à 375 px, marge 2,5cqw), le dessin ou un bord
    MOB_K = 2.6                                              # px du ciel par cqw (étoiles un peu plus petites, plus de ciel)
    MOB_X, MOB_Y = 0, 0                                      # coin haut gauche de la fenêtre dans le ciel
    MOB_HEAD = [(16.99, 9.53, 83, 14.07), (41.35, 17.23, 58.65, 27.9), (11.97, 26.19, 88.02, 36.85),
                (25.37, 36.75, 74.63, 41.28), (9.46, 46.04, 90.54, 50.58)]
    MOB_PRINCE = (18, MOBILE_PRINCE_TOP, 82, MOBILE_PRINCE_TOP + 64 * 644 / 475)
    win = src.crop((MOB_X, MOB_Y, MOB_X + round(100 * MOB_K), MOB_Y + round(MOBILE_SKY_H * MOB_K)))
    wa = win.getchannel('A').load(); wseen = set()
    blocks = [(a - 2.5, b - 2.5, c + 2.5, d + 2.5) for a, b, c, d in MOB_HEAD] + [(MOB_PRINCE[0] - 1, MOB_PRINCE[1] - 1, MOB_PRINCE[2] + 1, MOB_PRINCE[3] + 1)]
    for yy in range(win.height):
        for xx in range(win.width):
            if wa[xx, yy] <= 20 or (xx, yy) in wseen: continue
            stack, pts = [(xx, yy)], []
            wseen.add((xx, yy))
            while stack:
                p = stack.pop(); pts.append(p)
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        q = (p[0] + dx, p[1] + dy)
                        if 0 <= q[0] < win.width and 0 <= q[1] < win.height and q not in wseen and wa[q] > 20:
                            wseen.add(q); stack.append(q)
            bx0, by0 = min(p[0] for p in pts), min(p[1] for p in pts)
            bx1, by1 = max(p[0] for p in pts) + 1, max(p[1] for p in pts) + 1
            g = (bx0 / MOB_K, by0 / MOB_K, bx1 / MOB_K, by1 / MOB_K)
            edge = bx0 <= 1 or by0 <= 1 or bx1 >= win.width - 1 or by1 >= win.height - 1
            if edge or any(hits(g, r) for r in blocks):
                win.paste((0, 0, 0, 0), (bx0 - 1, by0 - 1, bx1 + 1, by1 + 1))
    win.save(os.path.join(IMG, 'title-stars-mobile.png'), optimize=True)
    vis = (round((0 - x0) * sx), round((0 - y0) * sy), round((page.rect.width - x0) * sx), round((min(page.rect.height, y1) - y0) * sy))
    im.crop(tuple(int(v) for v in vis)).save(os.path.join(IMG, 'title-stars.png'), optimize=True)
    # ciel entier pour l'ordinateur : posé comme dans le PDF (voir .title-sky dans le CSS)
    im.save(os.path.join(IMG, 'title-stars-full.png'), optimize=True)
    w, h = export(681, '00-the-little-prince-stars.jpg')
    return (f'<figure class="fig title-prince">\n  <img src="../img/{SLUG}/00-the-little-prince-stars.jpg" alt="The Little Prince holding stars in his hands, the fox at his feet" width="{w}" height="{h}">\n</figure>')
TITLE_PRINCE = title_page()

SKIP = {(4, 649), (8, 442), (8, 467), (8, 659), (8, 684), (8, 701), (14, 653)}
QUOTES = {(3, 281): 'benjamin', (7, 369): 'aquinas', (10, 332): 'rumi', (10, 366): 'rumi', (15, 137): 'rimbaud',
          (18, 391): 'chekhov', (18, 408): 'chekhov', (18, 425): 'chekhov', (18, 450): 'chekhov',
          (19, 295): 'prince', (19, 312): 'prince', (19, 329): 'prince'}
HEADS = {'On Encounter', 'Toward Constellations', 'The Curious Astrologers', 'On Black Holes'}

def clean(s):
    return s.replace('\ufb01', 'fi').replace('\ufb02', 'fl')

def block_lines(b, it, note_mode=False):
    """Lignes du bloc en HTML ; les petits chiffres deviennent des appels (ou des débuts de note)."""
    lines = []
    for l in b['lines']:
        out, em = [], False
        for s in l['spans']:
            txt = clean(''.join(c['c'] for c in s['chars']))
            if s['size'] < 8.5 and txt.strip().isdigit():
                if em: out.append('</em>'); em = False
                out.append(f'\x00{txt.strip()}\x00')
                continue
            for c in s['chars']:
                ch = clean(c['c'])
                ital = it(*c['origin']) and ch.strip() != ''
                if ital and not em: out.append('<em>'); em = True
                if not ital and em and ch.strip(): out.append('</em>'); em = False
                out.append(html.escape(ch, quote=False))
        if em: out.append('</em>')
        lines.append(''.join(out))
    return lines

def join(lines):
    out = ''
    for ln in lines:
        if not out: out = ln
        elif re.search(r'\S-$', out): out += ln.lstrip()
        else: out = out.rstrip() + ' ' + ln.lstrip()
    out = re.sub(r'\s*</em>(\s*)<em>\s*', r'\1', out)
    out = re.sub(r'<em>(\s+)', r'\1<em>', out); out = re.sub(r'(\s+)</em>', r'</em>\1', out)
    return re.sub(r'[ \t]{2,}', ' ', out).strip()

items, notes = [], {}
last_note = None
for pno, page in enumerate(doc, 1):
    if pno == 1: continue
    it = italic_lookup(page)
    for b in page.get_text('rawdict')['blocks']:
        if b['type'] != 0: continue
        y = round(b['bbox'][1])
        if (pno, y) in SKIP: continue
        chars = [c for l in b['lines'] for s in l['spans'] for c in s['chars'] if c['c'].strip()]
        if not chars: continue
        sizes = [s['size'] for l in b['lines'] for s in l['spans'] for c in s['chars'] if c['c'].strip()]
        if sum(1 for z in sizes if z <= 10.5) > len(sizes) / 2:     # notes de bas de page
            txt = join(block_lines(b, it))
            for part in re.split(r'(\x00\d+\x00)', txt):
                m = re.fullmatch(r'\x00(\d+)\x00', part)
                if m: last_note = int(m.group(1)); notes[last_note] = ''
                elif last_note and part.strip(): notes[last_note] = (notes[last_note] + ' ' + part).strip()
            continue
        lines = block_lines(b, it)
        bold = all(s['flags'] & 16 for l in b['lines'] for s in l['spans'] if ''.join(c['c'] for c in s['chars']).strip())
        items.append((pno, y, 'q' if (pno, y) in QUOTES else 'h' if bold else 'p', (QUOTES.get((pno, y)), lines)))
for pno, y, f in FIGS:
    items.append((pno, y, 'f', f))
items.sort(key=lambda t: (t[0], t[1]))

def refs(s):
    return re.sub(r'\s*\x00(\d+)\x00', lambda m: ref(int(m.group(1))), s)

out, pending, qbuf = [], [], None
def flush_quote():
    global qbuf
    if not qbuf: return
    key, lines = qbuf; qbuf = None
    if key == 'benjamin':
        out.append(f'<blockquote>\n  <p><em>{refs(join(lines)).replace("<em>", "").replace("</em>", "")}</em></p>\n  <footer>— Walter Benjamin, “On the Concept of History”</footer>\n</blockquote>')
    elif key == 'aquinas':
        t = refs(join(lines))
        q, who = t.rsplit(' Thomas Aquinas', 1)
        out.append(f'<blockquote>\n  <p><em>{q.replace("<em>", "").replace("</em>", "")}</em></p>\n  <footer>— Thomas Aquinas{who}</footer>\n</blockquote>')
    elif key == 'prince':
        # citation finale, mise comme dans le PDF : centrée, gras italique, dernière phrase seule sur sa ligne
        t = re.sub(r"</?em>", "", refs(join(lines))).replace(' But how far away', '<br>But how far away', 1)
        t = t.replace('just above us…', 'just&nbsp;above&nbsp;us…', 1)     # « us… » jamais seul sur une ligne
        assert 'above&nbsp;us' in t
        out.append(f'<blockquote class="closing-quote">\n  <p><em>{t}</em></p>\n</blockquote>')
    elif key in ('rumi', 'rimbaud'):
        ls = [refs(l).strip() for l in lines if l.strip()]
        body = '<br>'.join(re.sub(r'</?em>', '', l) for l in ls)
        out.append(f'<blockquote class="verse">\n  <p><em>{body}</em></p>\n</blockquote>')
    elif key == 'chekhov':
        t = re.sub(r'</?em>', '', refs(join(lines)))
        a, m = t.split('MARINA', 1)
        out.append(f'<blockquote>\n  <p><em>{a.strip()}</em></p>\n  <p><em>MARINA{m}</em></p>\n</blockquote>')

def done(p):
    t = re.sub(r'(<sup class="noteref"><a [^>]*>\d+</a></sup>)+$', '', p).rstrip()
    t = re.sub(r'</em>$', '', t)
    return re.search(r'[.!?”"):;]$', t) is not None

for pno, y, kind, payload in items:
    if kind == 'f':
        pending.append(payload); continue
    if kind == 'q':
        key, lines = payload
        if qbuf and qbuf[0] == key:
            qbuf[1].extend(lines); continue
        flush_quote()
        out.extend(pending); pending = []
        qbuf = [key, list(lines)]; continue
    key, lines = payload
    t = refs(join(lines))
    if kind == 'p' and not qbuf and out and out[-1].startswith('<p>') and not done(out[-1][3:-4]):
        out[-1] = out[-1][:-4] + ' ' + t + '</p>'
        continue
    flush_quote()
    out.extend(pending); pending = []
    if kind == 'h':
        out.append(f'<h2>{re.sub(r"</?em>", "", t)}</h2>')
    else:
        out.append(f'<p>{t}</p>')
flush_quote()
out.extend(pending)
body = '\n'.join(out)

notes_html = '\n'.join(f'    <li id="note-{n}">{refs(notes[n])} <a href="#ref-{n}" aria-label="Back to text">↩</a></li>' for n in sorted(notes))
missing = [n for n in range(1, 55) if n not in notes]
used = set(int(x) for x in re.findall(r'id="ref-(\d+)"', body))
print('notes', len(notes), 'manquantes', missing, '| appels absents', sorted(set(notes) - used), '| doublons', len(re.findall(r'id="ref-', body)) - len(used))

tpl = open(os.path.join(ROOT, 'articles', 'anima-of-animals.html'), encoding='utf-8').read()
start = tpl.index('    <main class="article">')
end = tpl.index('    </main>') + len('    </main>')
main = f'''    <main class="article">
      <div class="title-page" style="--prince-top: {MOBILE_PRINCE_TOP}cqw; --sky-h: {MOBILE_SKY_H}cqw">
      <div class="title-sky" aria-hidden="true"></div>
      <header class="article-head">
        <p class="article-kicker">Issue #1 — To Utopia</p>
        <h1 class="article-title">The Constellations</h1>
        <p class="article-dek">The End of the Straubs’ Films</p>
        <p class="article-byline">by Timothé Legrand-Hug</p>
      </header>
{TITLE_PRINCE}
      </div>

{body}

      <footer class="notes" aria-label="Notes">
        <div class="rule rule--double"></div>
        <ol>
{notes_html}
        </ol>
      </footer>
    </main>'''
page = tpl[:start] + main + tpl[end:]
page = page.replace('<title>Anima of Animals — Park Row Magazine</title>', '<title>The Constellations — Park Row Magazine</title>')
page = re.sub(r'<meta name="description" content="[^"]*">',
              '<meta name="description" content="The End of the Straubs’ Films, an essay by Timothé Legrand-Hug. Park Row Magazine, Issue #1.">', page)
open(os.path.join(ROOT, 'articles', SLUG + '.html'), 'w', encoding='utf-8', newline='\n').write(page)
Image.open(os.path.join(SP, 'en-cover.jpg')).convert('RGB').save(os.path.join(IMG, 'cover-anna-magdalena-bach.jpg'), quality=90)
for o in out: print('  ', re.sub(r'<[^>]+>', '', o).replace('\n', ' ')[:100])
