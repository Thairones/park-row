# Construit articles/to-utopia.html : l'introduction du numéro 1, d'après la dernière page de
# sampleintro.pdf (InDesign) : texte avec italique/gras, 4 images de Park Row (Fuller), signature dessous.
import os, re, html, warnings
warnings.filterwarnings('ignore')
import pymupdf
from PIL import Image

PDF = r'C:\Users\Thairone\Downloads\Telegram Desktop\sampleintro.pdf'
ROOT = r'C:\Users\Thairone\Desktop\park row'
SLUG = 'to-utopia'
IMG = os.path.join(ROOT, 'img', SLUG)
os.makedirs(IMG, exist_ok=True)
doc = pymupdf.open(PDF)
page = doc[-1]

# ---------- texte : les blocs Palatino 11 pt entre « TO UTOPIA » et les images ----------
paras, cur, last_y = [], [], None
for b in page.get_text('dict')['blocks']:
    if b['type'] != 0: continue
    for l in b['lines']:
        spans = [s for s in l['spans'] if s['text'].strip()]
        if not spans or not all(s['font'].startswith('Palatino') for s in spans): continue
        if l['bbox'][1] > 420 or any(s['size'] > 14 for s in spans): continue      # titre « TO UTOPIA », légende, signature
        y = l['bbox'][1]
        if last_y is not None and y - last_y > 20 and cur:                          # ligne vide = nouveau paragraphe
            paras.append(cur); cur = []
        last_y = y
        for s in l['spans']:
            t = html.escape(s['text'], quote=False)
            if t.strip():
                lead, core, trail = re.match(r'^(\s*)(.*?)(\s*)$', t, re.S).groups()
                if 'Italic' in s['font']: core = f'<em>{core}</em>'
                elif 'Bold' in s['font']: core = f'<strong>{core}</strong>'
                t = lead + core + trail
            cur.append(t)
        cur.append(' ')
if cur: paras.append(cur)
def clean(p):
    s = ''.join(p)
    for tag in ('em', 'strong'):
        s = re.sub(rf'</{tag}>(\s*)<{tag}>', r'\1', s)
    return re.sub(r'\s{2,}', ' ', s).strip()
paras = [clean(p) for p in paras]
assert len(paras) == 3 and paras[0].startswith('Beginnings') and paras[2].startswith('These we share'), paras

# ---------- images : trois plans en 4:3 puis le plan large des sous-titres, légende et signature dessous ----------
names = []
for i, x in enumerate((37, 38, 39, 40)):
    pix = pymupdf.Pixmap(doc, x)
    if pix.alpha: pix = pymupdf.Pixmap(pix, 0)
    if pix.n - pix.alpha >= 4: pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    im = Image.frombytes('RGB' if pix.n >= 3 else 'L', (pix.width, pix.height), pix.samples).convert('RGB')
    name = f'park-row-1952-{i + 1}.jpg'
    im.save(os.path.join(IMG, name), quality=88)
    names.append((name, im.size))
for old in [f'0{i}-steve-brodie.jpg' for i in range(1, 5)]:
    if os.path.exists(os.path.join(IMG, old)): os.remove(os.path.join(IMG, old))

ALT = ['Bowery saloon: “Did you hear the splash? I done it!”', 'Bowery saloon: “Done what?” “I jumped off the Brooklyn Bridge.”',
       'A newspaper headline: “Steve Brodie drops 120 feet to the water below!”', '“The officer won’t like this.” “The readers will.”']
img = lambda k: f'<img src="../img/{SLUG}/{names[k][0]}" alt="Still from Park Row (1952): {html.escape(ALT[k], quote=False)}" width="{names[k][1][0]}" height="{names[k][1][1]}" loading="lazy">'
figure = (f'<figure class="fig fig-brodie">\n  <div class="brodie-grid">{img(0)}{img(1)}{img(2)}'
          f'<div class="brodie-cell">{img(3)}<figcaption><em>Park Row</em> (1952) by Samuel Fuller</figcaption>'
          f'<p class="brodie-sign">— The Park Row Editors</p></div></div>\n</figure>')

body = '\n'.join(['<p class="intro-kicker"><strong>“To Utopia”</strong></p>'] + [f'<p>{p}</p>' for p in paras] + [figure])

tpl = open(os.path.join(ROOT, 'articles', 'anima-of-animals.html'), encoding='utf-8').read()
start = tpl.index('    <main class="article">')
end = tpl.index('    </main>') + len('    </main>')
main = f'''    <main class="article">
      <header class="article-head">
        <p class="article-kicker">Issue #1</p>
        <h1 class="article-title">Introduction: To Utopia</h1>
        <p class="article-byline">by the Park Row Editors</p>
      </header>

{body}
    </main>'''
page_html = tpl[:start] + main + tpl[end:]
page_html = page_html.replace('<title>Anima of Animals — Park Row Magazine</title>', '<title>Introduction: To Utopia — Park Row Magazine</title>')
page_html = re.sub(r'<meta name="description" content="[^"]*">',
                   '<meta name="description" content="Introduction to Issue #1 of Park Row Magazine, by the Park Row Editors.">', page_html)
open(os.path.join(ROOT, 'articles', SLUG + '.html'), 'w', encoding='utf-8', newline='\n').write(page_html)
for p in paras: print(' ', p[:120])
