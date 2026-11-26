# Run from the repo root: python tools/intro_tall.py <preview-folder>  (writes img/intro-sign-tall.jpg from img/intro-sign-wide-2.jpg)
# Tall version of the intro image for upright screens (phones): the drawing in the middle, and above / below it
# the same dark charcoal texture as the wide image's side strips, pieced together from vertical slices of the left
# strip (random slice, some turned upside down, cross-faded where they meet). Short overlap into the drawing, no vignette.
import numpy as np, sys
from PIL import Image
S=sys.argv[1]; rng=np.random.default_rng(21)
wide=np.asarray(Image.open('img/intro-sign-wide-2.jpg').convert('RGB'),float)   # 3599x1805, drawing at x 605..2982
src=wide[40:-40,30:560]                          # left strip, away from the outer edge, the drawing and the top/bottom rows
BW,BH=2377,1805
src=np.asarray(Image.fromarray(src.astype('uint8')).resize((src.shape[1],BH),Image.LANCZOS),float)
def band():
    out=np.zeros((BH,BW,3)); ws=np.zeros((BH,BW,1)); x=0; ov=120; last=-999
    while x<BW:
        sw=int(rng.integers(200,320))
        for _ in range(30):                      # not the same slice twice in a row
            x0=int(rng.integers(0,src.shape[1]-sw))
            if abs(x0-last)>90: break
        last=x0; p=src[:,x0:x0+sw]
        if rng.random()<.5: p=p[::-1]
        w=np.ones(sw); r=np.linspace(0,1,ov); w[:ov]=r; w[-ov:]=r[::-1]
        x1=min(BW,x+sw); n=x1-x
        out[:,x:x1]+=p[:,:n]*w[None,:n,None]; ws[:,x:x1]+=w[None,:n,None]
        x+=sw-ov
    return out/np.maximum(ws,1e-6)
top=band(); bot=band()
draw=wide[:,605:2982].copy()
f=70; a=np.linspace(0,1,f)[:,None,None]
draw[:f]=top[-f:]*(1-a)+draw[:f]*a              # the band runs a little way over the drawing's edge
draw[-f:]=draw[-f:]*(1-a)+bot[:f]*a
full=np.concatenate([top[:-f] if False else top,draw,bot])
img=Image.fromarray(np.clip(full,0,255).astype('uint8'))
DW=1320; img=img.resize((DW,round(img.height*DW/BW)),Image.LANCZOS)
img.save('img/intro-sign-tall.jpg',quality=80,optimize=True,progressive=True)
print(img.size)
img.crop((0,0,DW,1100)).resize((660,550)).save(S+'/tall-top.png')
img.resize((DW//4,img.height//4)).save(S+'/tall-s.png')
