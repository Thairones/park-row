# The Cleared Walkway, version finale : texte des deux .docx (parties 1, 2 et épilogue)
# avec la mise en page et les images de la version Canva (définitions côte à côte, figures).
# Les figures sont reprises de la page construite par build_walkway_pdf.py (à lancer avant).
import os, re, html, zipfile
from xml.etree import ElementTree as ET

DL = r'C:\Users\Thairone\Downloads\Telegram Desktop'
DOCS = [os.path.join(DL, 'Part 1_ To The Cleared Walkway (1).docx'), os.path.join(DL, 'Epilogue(1).docx')]
ROOT = r'C:\Users\Thairone\Desktop\park row'
PAGE = os.path.join(ROOT, 'articles', 'to-the-cleared-walkway.html')
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

cur = open(PAGE, encoding='utf-8').read()
figs = re.findall(r'<figure class="[^"]*">.*?\n</figure>', cur, flags=re.S)
assert len(figs) == 6, len(figs)
DEFS, COSTA, YORK, BELLE, GOLDER, COLLAGE = figs
assert 'class="defs"' in DEFS and 'Costa' in COSTA and 'Sergeant York' in YORK and 'Belle' in BELLE and 'Golder' in GOLDER

def on(rpr, tag):
    e = rpr.find(W + tag) if rpr is not None else None
    return e is not None and e.get(W + 'val') not in ('0', 'false')

def para(p):
    out = []
    for r in p.iter(W + 'r'):
        rpr = r.find(W + 'rPr')
        t = ''.join(c.text or '' for c in r if c.tag == W + 't')
        if not t: continue
        t = html.escape(t, quote=False)
        if t.strip():
            lead, core, trail = re.match(r'^(\s*)(.*?)(\s*)$', t, re.S).groups()
            if on(rpr, 'i'): core = f'<em>{core}</em>'
            if on(rpr, 'b'): core = f'<strong>{core}</strong>'
            t = lead + core + trail
        out.append(t)
    s = ''.join(out)
    for tag in ('em', 'strong'):
        s = s.replace(f'</{tag}><{tag}>', '').replace(f'</{tag}> <{tag}>', ' ')
    return re.sub(r'\s{2,}', ' ', s).strip()

blocks = []
for d in DOCS:
    body = ET.fromstring(zipfile.ZipFile(d).read('word/document.xml')).find(W + 'body')
    blocks += [t for t in (para(p) for p in body.iter(W + 'p')) if t]

defs_text = {}
out = []
for t in blocks:
    m = re.fullmatch(r'<strong>((?:Part \d|Epilogue)[^<]*)</strong>', t)
    if m:
        if m.group(1).startswith('Part 2'): out.append(COSTA)          # fin de la partie 1
        if m.group(1).startswith('Epilogue'): out.append(COLLAGE)     # fin de la partie 2
        out.append(f'<h2>{m.group(1).replace(" - ", " — ")}</h2>'); continue
    m = re.match(r'The (Productive|Negative) Realm - ', t)
    if m:
        defs_text[m.group(1)] = t[m.end():]
        if len(defs_text) == 2: out.append('DEFS')
        continue
    if re.fullmatch(r'<em>[^<]*</em>', t):
        out.append(f'<blockquote>\n  <p>{t}</p>\n  <footer>— Tag Gallagher, <em>Making Reality</em></footer>\n</blockquote>'); continue
    out.append(f'<p>{t}</p>')
    if t.startswith('The infinity present through the relative materialism'): out += [YORK, BELLE]
    if t.startswith('It must be said, though'): out.append(GOLDER)

# définitions : même mise en page, texte des .docx
defs = re.sub(r'<strong>The Productive:</strong>', '<strong>The Productive Realm:</strong>', DEFS)
defs = re.sub(r'<strong>The Negative:</strong>', '<strong>The Negative Realm:</strong>', defs)
cols = re.findall(r'(<p class="defs-term">.*?</p>\n    )<p>(.*?)</p>', defs, flags=re.S)
assert len(cols) == 2
defs = defs.replace(f'<p>{cols[0][1]}</p>', f'<p>{defs_text["Productive"]}</p>', 1)
defs = defs.replace(f'<p>{cols[1][1]}</p>', f'<p>{defs_text["Negative"]}</p>', 1)
# sur téléphone : les définitions courtes de la version Canva, texte au-dessus des images (classes defs-mobile / defs-desktop)
import pymupdf
canva = pymupdf.open(os.path.join(DL, 'Zoey_Article_PDFS_combined.pdf'))[0]
def canva_text(x0):
    b = next(b for b in canva.get_text('dict')['blocks'] if b['type'] == 0 and round(b['bbox'][1]) == 358 and round(b['bbox'][0]) == x0)
    def span(sp):
        t = html.escape(sp['text'], quote=False)
        if 'Italic' in sp['font'] and t.strip():
            lead, core, trail = re.match(r'^(\s*)(.*?)(\s*)$', t, re.S).groups()
            t = f'{lead}<em>{core}</em>{trail}'
        return t
    s = ' '.join(''.join(span(sp) for sp in l['spans']) for l in b['lines'])
    return re.sub(r'\s{2,}', ' ', s).strip()
mobile = {'Productive': canva_text(39), 'Negative': canva_text(353)}
for k in ('Productive', 'Negative'):
    defs = defs.replace(f'<p class="defs-term"><strong>The {k} Realm:</strong></p>\n    <p>{defs_text[k]}</p>',
                        f'<p class="defs-term defs-desktop"><strong>The {k} Realm:</strong></p>\n    <p class="defs-desktop">{defs_text[k]}</p>\n'
                        f'    <p class="defs-term defs-mobile"><strong>The {k}:</strong></p>\n    <p class="defs-mobile">{mobile[k]}</p>', 1)
assert defs.count('defs-mobile') == 4, defs
body = '\n'.join(defs if o == 'DEFS' else o for o in out)
for f in (YORK, BELLE, GOLDER, COSTA, COLLAGE):
    assert body.count(f) == 1

start = cur.index('      </header>\n') + len('      </header>\n')
end = cur.index('    </main>')
cur = cur[:start] + '\n' + body + '\n' + cur[end:]
open(PAGE, 'w', encoding='utf-8', newline='\n').write(cur)
print('ok', len(out), 'blocs')
for o in out: print('  ', re.sub(r'<[^>]+>', '', o).strip().replace('\n', ' ')[:80])
