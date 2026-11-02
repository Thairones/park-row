# Construit articles/cinema-without-a-world.html depuis le PDF InDesign de la table ronde.
import os, re, html, warnings
warnings.filterwarnings('ignore')
import pymupdf
from PIL import Image

PDF = r'C:\Users\Thairone\Downloads\Telegram Desktop\CinemaWithoutAWorld_FinalizedMaybe.pdf'
SP = r'C:\Users\Thairone\AppData\Local\Temp\claude\C--Users-Thairone-Desktop-park-row\a45769c3-b703-48ee-a8b4-cae9d5a34cb9\scratchpad'
ROOT = r'C:\Users\Thairone\Desktop\park row'
SLUG = 'cinema-without-a-world'
IMG = os.path.join(ROOT, 'img', SLUG)
os.makedirs(IMG, exist_ok=True)

doc = pymupdf.open(PDF)

# ---------- images ----------
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

FIGS = {  # page -> figures, placed before the next speaker turn
    2: [pair([(3, '01-cassandras-dream.jpg', 'Set photograph of Cassandra’s Dream'),
              (4, '02-the-mule.jpg', 'Set photograph of The Mule')], '2 / 3',
             'Set photographs of <em>Cassandra’s Dream</em> (2007) by Woody Allen [left] and <em>The Mule</em> (2018) by Clint Eastwood [right]')],
    4: [one(9, '03-seats-of-alcazar.jpg', 'A couple reading in the seats of a repertory theatre',
            'Repertory theatre ‘Alcazar’ from <em>The Seats of Alcazar</em> (1989) by Luc Moullet')],
    5: [one(12, '04-cinerama.jpg', 'Illustration of a Cinerama projection set-up', 'Illustration of the projector set-up for CINERAMA projections', 'fig fig--narrow'),
        one(13, '05-imax-diagram.jpg', 'Diagram of an IMAX theatre', 'Diagram of the projector set-up for IMAX', 'fig fig--narrow')],
    7: [one(22, '06-christopher-columbus.jpg', 'Title card of Christopher Columbus on RAI',
            'Title card of <em>Christopher Columbus</em> (1968) by Vittorio Cottafavi during a television screening on RAI', 'fig fig--narrow'),
        one(23, '07-acts-of-the-apostles.jpg', 'Title card of Acts of the Apostles on RAI HD',
            'Title card of <em>Acts of the Apostles</em> (1969) by Roberto Rossellini during a modern television screening on RAI HD', 'fig fig--narrow')],
    9: [one(29, '08-the-illiac-passion.jpg', 'Title card of The Illiac Passion',
            'Title card of <em>The Illiac Passion</em> (1967) by Gregory J. Markopoulos, which was restored and appeared online, causing a wave of people seeing the film', 'fig fig--narrow')],
}

# ---------- texte ----------
SPEAKER = re.compile(r'^(Chaz Mullis|Zoey M\. Hogan|Jean-Luc Jacques|CM|ZMH|JLJ):\s*')

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
        if not out:
            out = ln
        elif out.endswith('\u00ad'):
            out = out[:-1] + ln
        elif re.search(r'\S-$', out):
            out += ln
        else:
            out = out.rstrip() + ' ' + ln.lstrip()
    out = out.replace('\u00ad', '').replace('</em><em>', '').replace('</em> <em>', ' ')
    return re.sub(r'\s{2,}', ' ', out).strip()

paras = []   # list of [html]
pending = []
TOP = {4, 9}  # figures en haut de page
for pno, page in enumerate(doc, 1):
    if pno in TOP: pending += FIGS[pno]
    blocks = [b for b in page.get_text('dict')['blocks'] if b['type'] == 0]
    blocks.sort(key=lambda b: b['bbox'][1])
    for b in blocks:
        fonts = {s['font'] for l in b['lines'] for s in l['spans']}
        if b['bbox'][1] < 45: continue                      # folio
        if fonts & {'Augustus', 'Oldtypewriter'}: continue   # titre, noms, sous-titre
        if all('Bold' in f for f in fonts): continue        # légendes
        t = block_html(b)
        if not t: continue
        m = SPEAKER.match(t)
        if m or not paras:
            paras.extend(['FIG:' + f for f in pending]); pending = []
            if m:
                t = f'<strong>{m.group(1)}:</strong> ' + t[m.end():]
            paras.append(t)
        else:
            paras[-1] = paras[-1] + ' ' + t                  # suite d'une réplique sur la page suivante
    if pno not in TOP: pending += FIGS.get(pno, [])
paras.extend(['FIG:' + f for f in pending])

body = '\n'.join(p[4:] if p.startswith('FIG:') else f'<p>{p}</p>' for p in paras)

# ---------- page ----------
tpl = open(os.path.join(ROOT, 'articles', 'anima-of-animals.html'), encoding='utf-8').read()
start = tpl.index('    <main class="article">')
end = tpl.index('    </main>') + len('    </main>')
main = f'''    <main class="article">
      <header class="article-head">
        <p class="article-kicker">Issue #1 — To Utopia</p>
        <h1 class="article-title">Cinema Without a World</h1>
        <p class="article-dek">Modern Filmmaking and Exclusivity</p>
        <p class="article-byline">A roundtable with Chaz Mullis, Zoey M. Hogan and Jean-Luc Jacques</p>
      </header>

{body}
    </main>'''
page = tpl[:start] + main + tpl[end:]
page = page.replace('<title>Anima of Animals — Park Row Magazine</title>', '<title>Cinema Without a World — Park Row Magazine</title>')
page = re.sub(r'<meta name="description" content="[^"]*">',
              '<meta name="description" content="A roundtable with Chaz Mullis, Zoey M. Hogan and Jean-Luc Jacques on modern filmmaking and exclusivity. Park Row Magazine, Issue #1.">', page)
open(os.path.join(ROOT, 'articles', SLUG + '.html'), 'w', encoding='utf-8', newline='\n').write(page)
print(len([p for p in paras if not p.startswith('FIG:')]), 'paragraphes,', sum(len(v) for v in FIGS.values()), 'figures')
