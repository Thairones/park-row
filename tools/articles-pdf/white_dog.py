# White Dog (Anima of Animals) : ré-extrait les deux images du PDF final et les recadre en rectangles
# sans le coin noir de la découpe en biais, au même rapport, pour la paire de l'article.
import pymupdf
from PIL import Image
SP = r'C:\Users\Thairone\AppData\Local\Temp\claude\C--Users-Thairone-Desktop-park-row\a45769c3-b703-48ee-a8b4-cae9d5a34cb9\scratchpad'
OUT = r'C:\Users\Thairone\Desktop\park row\img\anima'
doc = pymupdf.open(r'C:\Users\Thairone\Downloads\Telegram Desktop\AnimaOfAnimals_Finalized.pdf')

def get(xref):
    pix = pymupdf.Pixmap(doc, xref)
    if pix.alpha: pix = pymupdf.Pixmap(pix, 0)
    if pix.n - pix.alpha >= 4: pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)

def wedge_profile(im):
    # pour chaque ligne : largeur du noir pur collé au bord gauche et au bord droit
    g = im.convert('L'); px = g.load(); W, H = im.size
    left, right = [], []
    for y in range(H):
        x = 0
        while x < W and px[x, y] < 12: x += 1
        left.append(x)
        x = W - 1
        while x >= 0 and px[x, y] < 12: x -= 1
        right.append(W - 1 - x)
    return left, right

def clean_spans(im, side, margin=8):
    # zone propre de chaque ligne : on enlève le noir collé au bord du coin, plus le filet blanc de la découpe
    l, r = wedge_profile(im)
    W = im.width
    if side == 'right':      # coin noir à droite (Keys)
        return [(0, W - r[y] - margin) for y in range(im.height)]
    return [(l[y] + margin, W) for y in range(im.height)]    # coin noir à gauche (le chien)

def best_rect(spans, aspect, step=2):
    # plus grand rectangle de rapport largeur/hauteur donné, entièrement dans la zone propre
    H = len(spans); best = None
    for y0 in range(0, H, step):
        lo, hi = 0, 10 ** 9
        for y1 in range(y0 + 1, H + 1):
            a, b = spans[y1 - 1]; lo = max(lo, a); hi = min(hi, b)
            h = y1 - y0; w = round(h * aspect)
            if hi - lo < w: break
            if not best or h > best[3] - best[1]:
                # sur l'axe horizontal on se cale contre le bord de l'image (côté opposé au coin)
                x0 = lo if spans[0][0] > 0 else 0
                x0 = max(lo, min(x0, hi - w))
                best = (x0, y0, x0 + w, y1)
    return best

ASPECT = 1
for name, xref, side, out in (('keys', 12, 'right', '05-white-dog-keys-v2.jpg'), ('dog', 10, 'left', '06-white-dog-dog-v2.jpg')):
    im = get(xref)
    box = best_rect(clean_spans(im, side), ASPECT)
    crop = im.crop(box)
    crop.save(OUT + '\\' + out, quality=90)
    print(name, im.size, '->', box, crop.size)
