# Construit la galerie, rangée par numéro puis par article (dans l'ordre du sommaire du numéro) :
# un sommaire en haut, puis pour chaque article son titre (lien), son auteur et ses images.
import os, re, html
ROOT = r'C:\Users\Thairone\Desktop\park row'
# (numéro, rubrique, fichier, titre, auteur) — même ordre que la page Issues
ISSUES = [
    ('Issue #1 : To Utopia', [
        (None, 'articles/to-utopia.html', 'Introduction: To Utopia', 'The Park Row Editors'),
        (None, 'articles/to-the-cleared-walkway.html', 'The Cleared Walkway', 'Zoey M. Hogan'),
        (None, 'articles/the-constellations.html', 'The Constellations', 'Timothé Legrand-Hug'),
        (None, 'articles/we-still-bow-to-the-old-gods.html', 'We Still Bow to the Old Gods', 'Jean-Luc Jacques'),
        (None, 'articles/cinema-without-a-world.html', 'Cinema Without a World', 'The Park Row Editors'),
        (None, 'articles/a-cold-approach-to-phoenix.html', 'A Cold Approach to Phoenix', 'Chaz Mullis'),
        ('Miscellaneous', 'articles/anima-of-animals.html', 'Anima of Animals', 'Aron Mishktar'),
    ]),
]

FIG = re.compile(r'<figure class="((?:fig|defs)[^"]*)"(?: id="img-\d+")?')

def anchor(path):
    # donne une ancre à chaque figure de l'article (img-1, img-2…), pour que la galerie y mène directement
    p = os.path.join(ROOT, path)
    s = open(p, encoding='utf-8').read()
    n = iter(range(1, 1000))
    s2 = FIG.sub(lambda m: f'<figure class="{m.group(1)}" id="img-{next(n)}"', s)
    if s2 != s:
        open(p, 'w', encoding='utf-8', newline='\n').write(s2)
    return s2

def images(path):
    s = anchor(path)
    out = []
    for cls, k, fig in re.findall(r'<figure class="((?:fig|defs)[^"]*)" id="img-(\d+)"[^>]*>(.*?)</figure>', s, flags=re.S):
        if 'title-prince' in cls: continue        # illustration de la page de titre (The Constellations) : pas dans la galerie
        imgs = re.findall(r'<img src="\.\./([^"]+)" alt="([^"]*)" width="(\d+)" height="(\d+)"', fig)
        m = re.search(r'<figcaption>(.*?)</figcaption>', fig, flags=re.S)
        cap = re.sub(r'<sup class="noteref">.*?</sup>', '', m.group(1)).strip() if m else ''   # sans les appels de note
        films = re.findall(r'<em>[^<]+</em> \(\d{4}\)', cap)
        for i, (src, alt, w, h) in enumerate(imgs):
            if len(imgs) == 1 or not cap:
                label = cap
            elif '[left]' in cap and len(films) == len(imgs):        # paire de deux films : celui de cette image
                label = films[i]
            elif cap.count('<em>') == 1:                             # plusieurs images d'un même film
                label = cap
            elif alt.startswith('Still from '):                      # plusieurs films : d'après le texte alternatif
                label = html.escape(re.split(r': | with the subtitle', alt[len('Still from '):])[0])
            else:
                label = cap
            out.append((src, alt, w, h, label, f'#img-{k}'))
    return out

slug = lambda path: os.path.splitext(os.path.basename(path))[0]
blocks, total = [], 0
for issue, arts in ISSUES:
    toc, sections = [], []
    for section, path, title, author in arts:
        imgs = images(path)
        if not imgs: continue
        total += len(imgs)
        if section:
            toc.append(f'<li class="gal-toc-section">{section}</li>')
            sections.append(f'        <p class="gal-section">{section}</p>')
        toc.append(f'<li><a href="#{slug(path)}">{html.escape(title)}</a> <span class="gal-count">{len(imgs)}</span></li>')
        tiles = '\n'.join(
            f'          <figure class="tile">\n            <a href="{path}{frag}"><img src="{src}" alt="{html.escape(alt)}" width="{w}" height="{h}" loading="lazy"></a>\n'
            f'{"            <figcaption>" + label + "</figcaption>" + chr(10) if label else ""}          </figure>' for src, alt, w, h, label, frag in imgs)
        sections.append(f'''        <section class="gal-article" id="{slug(path)}">
          <header class="gal-head">
            <h3 class="gal-title"><a href="{path}">{html.escape(title)}</a></h3>
            <p class="gal-meta">{html.escape(author)} <span class="gal-sep" aria-hidden="true">✱</span> {len(imgs)} image{'s' if len(imgs) > 1 else ''}</p>
          </header>
          <div class="tiles">
{tiles}
          </div>
        </section>''')
    blocks.append(f'''      <section class="gal-issue" aria-label="{html.escape(issue)}">
        <h2 class="issue-head">{html.escape(issue)}</h2>
        <ul class="gal-toc">{''.join(toc)}</ul>
{chr(10).join(sections)}
      </section>''')

p = os.path.join(ROOT, 'gallery.html')
s = open(p, encoding='utf-8').read()
start = s.index('      </header>\n', s.index('class="giant"')) + len('      </header>\n')
end = s.index('    </main>')
s = s[:start] + '\n' + '\n'.join(blocks) + '\n' + s[end:]
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print(total, 'images dans la galerie')
