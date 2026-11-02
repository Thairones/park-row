import re, sys, html, difflib, warnings
warnings.filterwarnings('ignore')
import pymupdf

SITE = r'C:\Users\Thairone\Desktop\park row\articles'
PAIRS = {
    'og': (r'C:\Users\Thairone\Downloads\Telegram Desktop\WeStillBowtotheOldGods_Finalized_1.pdf', SITE + r'\we-still-bow-to-the-old-gods.html'),
    'an': (r'C:\Users\Thairone\Downloads\Telegram Desktop\AnimaOfAnimals_Finalized.pdf', SITE + r'\anima-of-animals.html'),
}
OPEN, CLOSE = '\u00ab', '\u00bb'

def pdf_words(path):
    doc = pymupdf.open(path)
    out = []
    for page in doc:
        for b in page.get_text('dict')['blocks']:
            if b['type'] != 0: continue
            for l in b['lines']:
                for s in l['spans']:
                    f = s['font']
                    if s['size'] > 11.5 or s['size'] < 9.5: continue  # headers, captions, notes
                    if 'Bold' in f: continue
                    t = s['text']
                    if 'Italic' in f and t.strip():
                        t = OPEN + t + CLOSE
                    out.append(t)
                out.append('\n')
    txt = ''.join(out)
    txt = re.sub(r'-\n(?=[a-z])', '', txt)
    txt = txt.replace('\u00ad\n', '').replace('\u00ad', '')
    txt = re.sub(CLOSE + r'\s*' + OPEN, ' ', txt)
    return txt.split()

def html_words(path):
    s = open(path, encoding='utf-8').read()
    s = s[s.index('</header>', s.index('article-head')):s.index('<footer class="notes"')]
    s = re.sub(r'<figure.*?</figure>', ' ', s, flags=re.S)
    s = re.sub(r'<h2>.*?</h2>', ' ', s, flags=re.S)
    s = s.replace('<em>', OPEN).replace('</em>', CLOSE)
    s = re.sub(r'<sup.*?</sup>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = re.sub(CLOSE + r'\s*' + OPEN, ' ', s)
    return s.split()

key = sys.argv[1]
strict = len(sys.argv) > 2
a = html_words(PAIRS[key][1])
b = pdf_words(PAIRS[key][0])
def norm(w):
    if strict:
        return OPEN in w or CLOSE in w, w.replace(OPEN, '').replace(CLOSE, '')
    return w.strip(OPEN + CLOSE)
sm = difflib.SequenceMatcher(None, [norm(w) for w in a], [norm(w) for w in b], autojunk=False)
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == 'equal': continue
    ctx = ' '.join(a[max(0, i1 - 6):i1])
    print(f'--- {op} @ ...{ctx}')
    print('   SITE:', ' '.join(a[i1:i2])[:300])
    print('   PDF :', ' '.join(b[j1:j2])[:300])
