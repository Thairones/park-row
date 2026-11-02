# Construit articles/a-cold-approach-to-phoenix.html depuis le PDF InDesign de l'interview.
import os, re, html, warnings
warnings.filterwarnings('ignore')
import pymupdf
from PIL import Image

PDF = r'C:\Users\Thairone\Downloads\Telegram Desktop\ColdApproachToPhenix_ClosetoFinal.pdf'
SP = r'C:\Users\Thairone\AppData\Local\Temp\claude\C--Users-Thairone-Desktop-park-row\a45769c3-b703-48ee-a8b4-cae9d5a34cb9\scratchpad'
ROOT = r'C:\Users\Thairone\Desktop\park row'
SLUG = 'a-cold-approach-to-phoenix'
IMG = os.path.join(ROOT, 'img', SLUG)
os.makedirs(IMG, exist_ok=True)
doc = pymupdf.open(PDF)

def export(xref, name):
    pix = pymupdf.Pixmap(doc, xref)
    if pix.n - pix.alpha >= 4: pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    im = Image.frombytes('RGB' if pix.n >= 3 else 'L', (pix.width, pix.height), pix.samples).convert('RGB')
    if im.width > 1200:
        im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
    im.save(os.path.join(IMG, name), quality=88)
    return im.size

def one(xref, name, alt, cap, cls='fig'):
    w, h = export(xref, name)
    return (f'<figure class="{cls}">\n  <img src="../img/{SLUG}/{name}" alt="{alt}" width="{w}" height="{h}" loading="lazy">\n'
            f'  <figcaption>{cap}</figcaption>\n</figure>')

def pair(items, cell, cap):
    tags = []
    for xref, name, alt in items:
        w, h = export(xref, name)
        tags.append(f'<img src="../img/{SLUG}/{name}" alt="{alt}" width="{w}" height="{h}" loading="lazy">')
    return (f'<figure class="fig fig--pair">\n  <div class="fig-grid" style="--cell: {cell}">{"".join(tags)}</div>\n'
            f'  <figcaption>{cap}</figcaption>\n</figure>')

NG = '<em>Nightgame</em> by Parker Corey'
# (page, y de tri, html) : chaque figure sort avant le premier nouveau paragraphe qui la suit
FIGS = [
    (1, 540, one(175, '01-nightgame-portrait.jpg', 'Still from Nightgame: a bearded man in shadow', NG, 'fig fig--narrow')),
    (2, 420, one(5, '02-nightgame-living-room.jpg', 'Still from Nightgame: two men watching a screen in a living room', NG, 'fig fig--narrow')),
    (3, 280, one(17, '03-bitter-victory.jpg', 'A figure wrapped in white standing on a dune', 'Shot from <em>Bitter Victory</em> (1957) by Nicholas Ray')),
    (3, 760, one(15, '04-nightgame-phone.jpg', 'Still from Nightgame: a face seen through a phone screen', NG, 'fig fig--narrow')),
    (4, 760, pair([(26, '05-nightgame-open.jpg', 'Still from Nightgame: two men behind a shop window'),
                   (27, '06-nightgame-credits.jpg', 'Still from Nightgame: the credit “Directed and produced by Parker Corey”')], '16 / 9', NG)),
    (5, 150, one(39, '07-the-rules-of-the-game.jpg', 'Two men in caps in profile', '<em>The Rules of the Game</em> (1939) by Jean Renoir', 'fig fig--narrow')),
    (6, 60, one(43, '08-nightgame-van.jpg', 'Still from Nightgame: a man sitting in the open trunk of a van', NG)),
]

SPEAKER = re.compile(r'^(Chaz Mullis|Parker Corey|CM|PC):\s*')

def block_html(b):
    lines = []
    for l in b['lines']:
        parts = []
        for s in l['spans']:
            t = html.escape(s['text'], quote=False)
            if 'Italic' in s['font'] and t.strip():
                lead, core, trail = re.match(r'^(\s*)(.*?)(\s*)$', t, re.S).groups()
                t = f'{lead}<em>{core}</em>{trail}'
            parts.append(t)
        lines.append(''.join(parts))
    out = ''
    for ln in lines:
        if not out: out = ln
        elif out.endswith('\u00ad'): out = out[:-1] + ln
        elif re.search(r'\S-$', out): out += ln
        else: out = out.rstrip() + ' ' + ln.lstrip()
    out = out.replace('\u00ad', '').replace('</em><em>', '').replace('</em> <em>', ' ')
    return re.sub(r'\s{2,}', ' ', out).strip()

items = []  # (page, y, kind, payload)
for pno, page in enumerate(doc, 1):
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0: continue
        fonts = {s['font'] for l in b['lines'] for s in l['spans']}
        if fonts & {'Augustus', 'Oldtypewriter'}: continue
        if any(f.startswith('MinionPro') for f in fonts): continue   # note de bas de page
        if all('Bold' in f for f in fonts): continue                  # légendes
        t = block_html(b)
        if t: items.append((pno, b['bbox'][1], 'p', t))
for pno, y, f in FIGS:
    items.append((pno, y, 'f', f))
items.sort(key=lambda it: (it[0], it[1]))

paras, pending = [], []
for pno, y, kind, t in items:
    if kind == 'f':
        pending.append(t); continue
    m = SPEAKER.match(t)
    if paras and not m and not re.search(r'[.!?”’)]$', paras[-1]):
        paras[-1] += ' ' + t                       # phrase coupée par la page ou une image
        continue
    paras.extend('FIG:' + f for f in pending); pending = []
    if m: t = f'<strong>{m.group(1)}:</strong> ' + t[m.end():]
    paras.append(t)
paras.extend('FIG:' + f for f in pending)

body = '\n'.join(p[4:] if p.startswith('FIG:') else f'<p>{p}</p>' for p in paras)
# corrections
FIX = [
    ('runand-gun', 'run-and-gun'),
    ('environments1.', 'environments<sup class="noteref"><a href="#note-1" id="ref-1">1</a></sup>.'),
    ('Michael Regrave', 'Michael Redgrave'),
]
for a, b in FIX:
    assert body.count(a) == 1, a
    body = body.replace(a, b)

tpl = open(os.path.join(ROOT, 'articles', 'anima-of-animals.html'), encoding='utf-8').read()
start = tpl.index('    <main class="article">')
end = tpl.index('    </main>') + len('    </main>')
main = f'''    <main class="article">
      <header class="article-head">
        <p class="article-kicker">Issue #1 — To Utopia</p>
        <h1 class="article-title">A Cold Approach to Phoenix</h1>
        <p class="article-dek">Interview with Parker Corey on <em>Nightgame</em></p>
        <p class="article-byline">by Chaz Mullis</p>
      </header>

{body}

      <footer class="notes" aria-label="Notes">
        <div class="rule rule--double"></div>
        <ol>
    <li id="note-1">Pedro Costa and Chris Fujiwara / Conversation about Jacques Tourneur: Tokyo (May 11 2010) <a href="#ref-1" aria-label="Back to text">↩</a></li>
        </ol>
      </footer>
    </main>'''
page = tpl[:start] + main + tpl[end:]
page = page.replace('<title>Anima of Animals — Park Row Magazine</title>', '<title>A Cold Approach to Phoenix — Park Row Magazine</title>')
page = re.sub(r'<meta name="description" content="[^"]*">',
              '<meta name="description" content="Chaz Mullis interviews Parker Corey on Nightgame. Park Row Magazine, Issue #1.">', page)
open(os.path.join(ROOT, 'articles', SLUG + '.html'), 'w', encoding='utf-8', newline='\n').write(page)

cov = Image.open(os.path.join(SP, 'ca-cover.webp')).convert('RGB').resize((1600, 900), Image.LANCZOS)
cov.save(os.path.join(IMG, 'cover-nightgame.jpg'), quality=86)
print(len([p for p in paras if not p.startswith('FIG:')]), 'paragraphes')
