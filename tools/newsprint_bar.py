# Old-newspaper texture for the title hover bar: yellowed newsprint, grain, fibres,
# Run from the repo root: python tools/newsprint_bar.py preview.png  (writes img/newsprint-bar.jpg)
# foxing, and faint columns of text bleeding through from the other side (mirrored).
import random, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
random.seed(4); rng=np.random.default_rng(4)
W,H=1000,160
base=np.array([226,214,186],float)           # aged newsprint, a little darker/yellower than #efe6d3
img=np.ones((H,W,3))*base
# large-scale blotchy discoloration
low=rng.normal(0,1,(H//20+2,W//20+2)); low=np.array(Image.fromarray(((low-low.min())/(np.ptp(low))*255).astype('uint8')).resize((W,H),Image.BICUBIC),float)/255
img-= (low[...,None]-.5)*np.array([18,20,28])
# fine grain
img+= rng.normal(0,5,(H,W))[...,None]
# ghost text from the reverse side
t=Image.new('L',(W,H),0); d=ImageDraw.Draw(t)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',9)
words='the of and a to in film cinema picture press city night street editor reel theatre screen news print late edition review the house light'.split()
colw=150
for x0 in range(4,W,colw+12):
    y=3
    while y<H:
        line='';
        while len(line)<34: line+=random.choice(words)+' '
        d.text((x0,y),line[:34],fill=255,font=f); y+=11
t=t.transpose(Image.FLIP_LEFT_RIGHT).filter(ImageFilter.GaussianBlur(.7))
img-= (np.array(t,float)/255)[...,None]*np.array([30,30,26])
# column rules
for x0 in range(W%(colw+12),W,colw+12): img[:,max(0,x0-6):x0-5]-=12
# fibres
fib=Image.new('L',(W,H),0); d=ImageDraw.Draw(fib)
for _ in range(260):
    x,y=random.uniform(0,W),random.uniform(0,H); a=random.uniform(0,6.28); L=random.uniform(3,14)
    d.line((x,y,x+L*np.cos(a),y+L*np.sin(a)),fill=random.randint(40,120),width=1)
img-= (np.array(fib,float)/255)[...,None]*np.array([22,24,28])
# foxing spots
for _ in range(14):
    cx,cy,r=random.uniform(0,W),random.uniform(0,H),random.uniform(2,9)
    yy,xx=np.ogrid[:H,:W]; m=np.exp(-((xx-cx)**2+(yy-cy)**2)/(2*r*r))
    img-= m[...,None]*np.array([14,26,44])*random.uniform(.4,1)
out=Image.fromarray(np.clip(img,0,255).astype('uint8'))
out.save('img/newsprint-bar.jpg',quality=82,optimize=True,progressive=True)
out.crop((0,0,420,40)).resize((1260,120),Image.NEAREST).save(__import__('sys').argv[1])
