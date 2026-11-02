# Repère l'italique « simulé » de Word (matrice de texte penchée) dans un PDF.
# italic_chars(page) -> fonction (x, y) -> bool pour l'origine d'un caractère (coordonnées PyMuPDF).
import re
import pymupdf

TOK = re.compile(rb'\((?:\\.|[^\\)])*\)|<[0-9A-Fa-f\s]*>|\[|\]|/[^\s/\[\]()<>]+|[-+]?\d*\.?\d+|[A-Za-z\'"*]+')

def mul(m, n):
    a, b, c, d, e, f = m; A, B, C, D, E, F = n
    return (a*A + b*C, a*B + b*D, c*A + d*C, c*B + d*D, e*A + f*C + E, e*B + f*D + F)

def shows(page):
    data = page.read_contents()
    ctm = (1, 0, 0, 1, 0, 0); stack = []; tm = tlm = (1, 0, 0, 1, 0, 0); tl = 0
    ops, out = [], []
    for t in TOK.findall(data):
        if re.fullmatch(rb'[A-Za-z\'"*]+', t) and t not in (b'true', b'false', b'null'):
            op = t.decode('latin1'); nums = []
            for o in ops:
                try: nums.append(float(o))
                except ValueError: pass
            ops = []
            if op == 'q': stack.append(ctm)
            elif op == 'Q': ctm = stack.pop() if stack else ctm
            elif op == 'cm' and len(nums) >= 6: ctm = mul(tuple(nums[-6:]), ctm)
            elif op == 'BT': tm = tlm = (1, 0, 0, 1, 0, 0)
            elif op == 'Tm' and len(nums) >= 6: tm = tlm = tuple(nums[-6:])
            elif op in ('Td', 'TD') and len(nums) >= 2:
                if op == 'TD': tl = -nums[-1]
                tm = tlm = mul((1, 0, 0, 1, nums[-2], nums[-1]), tlm)
            elif op == 'TL' and nums: tl = nums[-1]
            elif op in ('T*', "'", '"'): tm = tlm = mul((1, 0, 0, 1, 0, -tl), tlm)
            if op in ('Tj', 'TJ', "'", '"'):
                m = mul(tm, ctm)
                skew = abs(tm[2]) > 1e-3 * abs(tm[3] or 1)
                out.append((m[4], m[5], skew))
        else:
            ops.append(t)
    # en coordonnées PyMuPDF (origine en haut à gauche)
    M = page.transformation_matrix
    return [(pymupdf.Point(x, y) * M, s) for x, y, s in out]

def italic_lookup(page):
    pts = shows(page)
    def is_italic(x, y):
        best = None
        for p, s in pts:
            if abs(p.y - y) < 2.5 and p.x <= x + 0.6 and (best is None or p.x > best[0]):
                best = (p.x, s)
        return bool(best and best[1])
    return is_italic

if __name__ == '__main__':
    import sys
    doc = pymupdf.open(sys.argv[1])
    for pn in map(int, sys.argv[2:]):
        page = doc[pn - 1]; it = italic_lookup(page)
        cur = []
        for b in page.get_text('rawdict')['blocks']:
            for l in b.get('lines', []):
                for s in l['spans']:
                    for ch in s['chars']:
                        if it(*ch['origin']): cur.append(ch['c'])
                        elif cur and cur[-1] != '|': cur.append('|')
        print(pn, ''.join(cur)[:1500])
