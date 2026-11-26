# Run from the repo root: python tools/intro_tall.py <preview-folder>  (writes img/intro-sign-tall.jpg from img/intro-sign-wide-2.jpg)
# Tall version of the intro image for upright screens (phones): the drawing in the middle, and above / below it
# deep charcoal with a fine paper grain, the drawing fading into it like the dark edges of the wide version.
import numpy as np, sys
from PIL import Image, ImageFilter
S=sys.argv[1]; rng=np.random.default_rng(5)
wide=Image.open('img/intro-sign-wide-2.jpg').convert('RGB')
DW=1320; k=DW/2377; DH=round(1805*k)
drawing=wide.crop((605,0,2982,1805)).resize((DW,DH),Image.LANCZOS)
side=np.asarray(wide.crop((0,0,500,1805)),float)
tone=np.median(side.reshape(-1,3),axis=0); print('side tone',tone)
H=DH*3
g=rng.normal(0,6,(H,DW))
g=np.asarray(Image.fromarray((g+128).clip(0,255).astype('uint8')).filter(ImageFilter.GaussianBlur(.5)),float)-128
blot=np.asarray(Image.fromarray(rng.normal(128,30,(H//40,DW//40)).clip(0,255).astype('uint8')).resize((DW,H),Image.BICUBIC),float)-128
o=tone[None,None,:]+ (g*1.4+blot*.06)[...,None]
out=Image.fromarray(np.clip(o,0,255).astype('uint8'))
f=round(DH*.28); m=np.ones((DH,DW)); r=np.linspace(0,1,f)[:,None]**1.3; m[:f]*=r; m[-f:]*=r[::-1]
out.paste(drawing,(0,DH),Image.fromarray((m*255).astype('uint8')))
out.save('img/intro-sign-tall.jpg',quality=80,optimize=True,progressive=True)
out.resize((DW//4,H//4)).save(S+'/tall-s.png')
print(out.size)
