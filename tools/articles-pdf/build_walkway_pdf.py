# Reconstruit articles/to-the-cleared-walkway.html depuis la version Canva complète de Zoey
# (Zoey_Article_PDFS_combined.pdf), en gardant sa mise en page : définitions côte à côte, images.
import os, re, html, warnings
warnings.filterwarnings('ignore')
import pymupdf
from PIL import Image

PDF = r'C:\Users\Thairone\Downloads\Telegram Desktop\Zoey_Article_PDFS_combined.pdf'
ROOT = r'C:\Users\Thairone\Desktop\park row'
SLUG = 'to-the-cleared-walkway'
IMG = os.path.join(ROOT, 'img', SLUG)
os.makedirs(IMG, exist_ok=True)
doc = pymupdf.open(PDF)

# ---------- texte, bloc par bloc (page, y, x) ----------
BLOCKS = {}
for pno, page in enumerate(doc, 1):
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0: continue
        lines = []
        for l in b['lines']:
            parts = []
            for s in l['spans']:
                t = html.escape(s['text'], quote=False)
                if t.strip():
                    lead, core, trail = re.match(r'^(\s*)(.*?)(\s*)$', t, re.S).groups()
                    if 'Italic' in s['font']: core = f'<em>{core}</em>'
                    if 'Bold' in s['font']: core = f'<strong>{core}</strong>'
                    t = lead + core + trail
                parts.append(t)
            lines.append(''.join(parts))
        out = ''
        for ln in lines:
            if not out: out = ln
            elif re.search(r'\S-$', out): out += ln.lstrip()
            else: out = out.rstrip() + ' ' + ln.lstrip()
        for tag in ('em', 'strong'):
            out = re.sub(rf'</{tag}>(\s*)<{tag}>', r'\1', out)
        BLOCKS[(pno, round(b['bbox'][1]), round(b['bbox'][0]))] = re.sub(r'\s{2,}', ' ', out).strip()

def T(p, y, x=None):
    hits = [v for (pp, yy, xx), v in BLOCKS.items() if pp == p and yy == y and (x is None or xx == x)]
    assert len(hits) == 1, (p, y, x, len(hits))
    return hits[0]

# ---------- images (rognées de 2 px contre les liserés clairs de Canva) ----------
def export(xref, name, shave=2):
    pix = pymupdf.Pixmap(doc, xref)
    if pix.alpha: pix = pymupdf.Pixmap(pix, 0)
    if pix.n - pix.alpha >= 4: pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    im = Image.frombytes('RGB' if pix.n >= 3 else 'L', (pix.width, pix.height), pix.samples).convert('RGB')
    im = im.crop((shave, shave, im.width - shave, im.height - shave))
    im.save(os.path.join(IMG, name), quality=88)
    return im.size

def img(xref, name, alt, lazy=True):
    w, h = export(xref, name)
    return f'<img src="../img/{SLUG}/{name}" alt="{alt}" width="{w}" height="{h}"{" loading=\"lazy\"" if lazy else ""}>'

def one(xref, name, alt, cap, cls='fig'):
    return f'<figure class="{cls}">\n  {img(xref, name, alt)}\n  <figcaption>{cap}</figcaption>\n</figure>'

def grid(items, cell, cap, cls='fig fig--pair'):
    tags = ''.join(img(x, n, a) for x, n, a in items)
    return f'<figure class="{cls}">\n  <div class="fig-grid" style="--cell: {cell}">{tags}</div>\n  <figcaption>{cap}</figcaption>\n</figure>'

P = lambda t: f'<p>{t}</p>'
SIXTH = 'Still from The Sixth Part of the World'

defs = f'''<figure class="defs">
  <div class="defs-col">
    <p class="defs-term"><strong>The Productive:</strong></p>
    <p>{T(1, 358, 39)}</p>
    <div class="fig-grid defs-imgs" style="--cell: 4 / 3">{img(27, '01-sixth-part-productive-a.jpg', SIXTH + ': machinery')}{img(28, '02-sixth-part-productive-b.jpg', SIXTH + ': a factory floor')}</div>
  </div>
  <div class="defs-col">
    <p class="defs-term"><strong>The Negative:</strong></p>
    <p>{T(1, 358, 353)}</p>
    <div class="fig-grid defs-imgs" style="--cell: 4 / 3">{img(25, '03-sixth-part-negative-a.jpg', SIXTH + ': a peasant and an ox in a field')}{img(26, '04-sixth-part-negative-b.jpg', SIXTH + ': crowds and cranes at a port')}</div>
  </div>
  <figcaption>Images from <em>The Sixth Part of the World</em> (1926) by Dziga Vertov</figcaption>
</figure>'''

# David Golder : deux colonnes de quatre dans le PDF, remises ligne par ligne
golder_order = [52, 56, 53, 57, 54, 58, 55, 59]
golder = grid([(x, f'{10 + i:02d}-david-golder-{i + 1}.jpg', 'Still from David Golder') for i, x in enumerate(golder_order)],
              '6 / 5', 'Decoupage from <em>David Golder</em> (1931) by Julien Duvivier', 'fig fig--golder')

collage = f'''<figure class="fig fig-collage">
  <div class="collage-side">{img(64, '20-collage-a.jpg', 'A woman lying down, eyes closed')}</div>
  <div class="collage-mid">{img(66, '21-collage-b.jpg', 'A red flower before the sea at dusk')}{img(67, '22-collage-c.jpg', 'A tree house among pines')}{img(68, '23-collage-d.jpg', 'A tree house among pines, lower part')}</div>
  <div class="collage-side">{img(65, '24-collage-e.jpg', 'Waves breaking on rocks')}</div>
</figure>'''

body = '\n'.join([
    P(T(1, 100)),
    P(T(1, 279)),
    defs,
    P(T(2, 43)),
    P(T(2, 613)),
    P(T(2, 734) + ' ' + T(3, 28)),
    P(T(3, 180)),
    P(T(3, 327)),
    P(T(3, 543)),
    one(36, '05-where-does-your-hidden-smile-lie.jpg', 'A man sitting alone in a dark red room',
        'Ending of <em>Where Does Your Hidden Smile Lie?</em> by Pedro Costa'),
    '<h2>Duvivier, Schroeter</h2>',
    P(T(4, 37)),
    P(T(4, 577).rstrip() + ' ' + T(4, 91).lstrip(',').lstrip()),
    P(T(4, 361) + ' ' + T(5, 37)),
    P(T(5, 78)),
    one(46, '06-sergeant-york.jpg', 'Soldiers among rocks and trees', 'Shot from <em>Sergeant York</em> (1941) by Howard Hawks'),
    grid([(44, '07-la-belle-equipe-a.jpg', 'Still from La Belle Équipe'), (45, '08-la-belle-equipe-b.jpg', 'Still from La Belle Équipe')],
         '4 / 3', 'Shots from <em>La Belle Équipe</em> (1936) by Julien Duvivier'),
    P(T(6, 38) + ' ' + T(7, 39)),
    golder,
    collage,
])
FIX = [('Symbolism andmetaphor', 'Symbolism and metaphor')]
for a, b in FIX:
    assert body.count(a) == 1, a
    body = body.replace(a, b)

tpl = open(os.path.join(ROOT, 'articles', 'anima-of-animals.html'), encoding='utf-8').read()
start = tpl.index('    <main class="article">')
end = tpl.index('    </main>') + len('    </main>')
main = f'''    <main class="article">
      <header class="article-head">
        <p class="article-kicker">Issue #1 — To Utopia</p>
        <h1 class="article-title">The Cleared Walkway</h1>
        <p class="article-byline">by Zoey M. Hogan</p>
      </header>

{body}
    </main>'''
page = tpl[:start] + main + tpl[end:]
page = page.replace('<title>Anima of Animals — Park Row Magazine</title>', '<title>The Cleared Walkway — Park Row Magazine</title>')
page = re.sub(r'<meta name="description" content="[^"]*">',
              '<meta name="description" content="An essay by Zoey M. Hogan. Park Row Magazine, Issue #1.">', page)
open(os.path.join(ROOT, 'articles', SLUG + '.html'), 'w', encoding='utf-8', newline='\n').write(page)
print('ok', len(re.findall(r'<img ', body)), 'images')
