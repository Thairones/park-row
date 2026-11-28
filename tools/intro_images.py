# Builds img/intro-sign-wide-2.jpg and img/logo-sign-2.webp from the new photo of the drawing (IMG_7573.jpg)
# and the cut-out PNG (parkrowpng.png). Paths point to where they were uploaded; adjust before rerunning.
# M.npy = where the PNG sits on the photo (found with SIFT + RANSAC: scale 2.394, -0.5 deg, offset 213.6, 24.2).
import cv2, numpy as np, sys
from PIL import Image, ImageFilter
S=sys.argv[1]
M=np.load(S+'/M.npy')
Dimg=Image.open('/mnt/user-data/attachments/89895db2-013d-5e57-9a49-fa30d2ef3831/c16a4889-image.jpg').convert('RGB')
Dw,Dh=Dimg.size
P=cv2.imread('/mnt/user-data/attachments/89895db2-013d-5e57-9a49-fa30d2ef3831/f6943b09-image.png',cv2.IMREAD_UNCHANGED)
A=cv2.warpAffine(P[...,3],M,(Dw,Dh),flags=cv2.INTER_LINEAR,borderValue=0)
cut=Dimg.copy().convert('RGBA'); cut.putalpha(Image.fromarray(A))
W=1600; H=round(W*Dh/Dw)
cut.resize((W,H),Image.LANCZOS).save('img/logo-sign-2.webp',quality=88,method=6)
print('logo',W,H)
# wide: old wide upscaled for the side strips, new drawing in the middle, feathered seam
old=Image.open('img/intro-sign-wide.jpg').convert('RGB')     # 2000x1003, drawing at x 336..1657
TH=1805; k=TH/1003; TW=round(2000*k)
dw=round(1321*k); dx=round(336*k)
base=old.resize((TW,TH),Image.LANCZOS)
d=Dimg.resize((dw,TH),Image.LANCZOS)
# match the side strips' brightness to the new drawing's edges
oldc=np.asarray(base,float); dn=np.asarray(d,float)
band=40
for side in ('l','r'):
    if side=='l': o=oldc[:,dx:dx+band].mean(); n=dn[:,:band].mean(); sl=slice(0,dx+band)
    else: o=oldc[:,dx+dw-band:dx+dw].mean(); n=dn[:,-band:].mean(); sl=slice(dx+dw-band,TW)
    oldc[:,sl]*= n/o
    print(side,'old',round(o,1),'new',round(n,1))
base=Image.fromarray(np.clip(oldc,0,255).astype('uint8'))
mask=Image.new('L',(dw,TH),255); m=np.asarray(mask,float).copy()
f=220
ramp=np.linspace(0,1,f)
m[:,:f]*=ramp; m[:,-f:]*=ramp[::-1]
base.paste(d,(dx,0),Image.fromarray(m.astype('uint8')))
base.save('img/intro-sign-wide-2.jpg',quality=80,optimize=True,progressive=True)
print('wide',TW,TH,'drawing at',dx,dw)
base.resize((TW//4,TH//4)).save(S+'/wide2-s.png')
bg=Image.new('RGBA',(W,H),(18,17,16,255)); bg.alpha_composite(Image.open('img/logo-sign-2.webp').convert('RGBA')); bg.convert('RGB').resize((W//3,H//3)).save(S+'/logo2-s.png')
