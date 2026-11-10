"""Build Farmhand app icons, favicon, Home banner and phone login crop from Paul's original image.
Everything is cut from brand/farmhand-original.jpg; nothing is redrawn or retyped."""
from PIL import Image, ImageFilter
import numpy as np
SRC='brand/farmhand-original.jpg'
im=Image.open(SRC).convert('RGB')
WORD=(345,60,1168,640)         # FARMHAND lettering (x 360-1153, y 268-399) tight left-right, plus the red rule and fog, barn and fence behind
def band_on_square(size, width_frac, band=WORD, feather=0.12):
    b=im.crop(band); w=round(size*width_frac); h=round(b.height*w/b.width); b=b.resize((w,h),Image.LANCZOS)
    arr=np.asarray(b).astype(float)
    top=arr[:max(2,h//12)].reshape(-1,3).mean(0); bot=arr[-max(2,h//12):].reshape(-1,3).mean(0)
    # backdrop: the band's own top/bottom colours, as a vertical blend (no invented detail)
    t=np.linspace(0,1,size)[:,None]; bg=(top*(1-t)+bot*t)[:,None,:].repeat(size,1)
    canvas=Image.fromarray(bg.clip(0,255).astype('uint8'))
    x=(size-w)//2; y=(size-h)//2
    # feather the band edges into the backdrop
    m=np.ones((h,w)); f=max(1,int(h*feather)); r=np.linspace(0,1,f)
    m[:f]*=r[:,None]; m[-f:]*=r[::-1][:,None]
    if width_frac<1: fx=max(1,int(w*0.06)); rx=np.linspace(0,1,fx); m[:,:fx]*=rx[None,:]; m[:,-fx:]*=rx[::-1][None,:]
    canvas.paste(b,(x,y),Image.fromarray((m*255).astype('uint8')))
    return canvas
for n,s in [('icon-512.png',512),('icon-192.png',192),('apple-touch-icon.png',180)]:
    big=band_on_square(1024,1.0).resize((s,s),Image.LANCZOS); big.save(n,optimize=True)
band_on_square(1024,0.76).resize((512,512),Image.LANCZOS).save('icon-maskable-512.png',optimize=True)
# favicon: the gold 'F' (x 360-425, y 268-399) cut from the same lettering
F=im.crop((350,262,436,406))
def fav(s):
    f=F.resize((round(F.width*s*0.92/F.height), round(s*0.92)),Image.LANCZOS)
    arr=np.asarray(F).astype(float); edge=np.concatenate([arr[:3].reshape(-1,3),arr[-3:].reshape(-1,3)]).mean(0)
    c=Image.new('RGB',(s,s),tuple(int(v) for v in edge)); c.paste(f,((s-f.width)//2,(s-f.height)//2)); return c
fav(32).save('favicon-32.png',optimize=True); fav(64).save('favicon.png',optimize=True)
# Home banner: the middle band of the picture (wordmark + slice of barn/fence), inside the image's own frame
im.crop((70,205,1430,520)).save('brand/banner.jpg',quality=84,optimize=True,progressive=True)
# blurred, darkened copy that fills the sides of the header banner on wide screens (v7)
from PIL import ImageFilter, ImageEnhance
_b=Image.open('brand/banner.jpg').convert('RGB').resize((480,111),Image.LANCZOS).filter(ImageFilter.GaussianBlur(10))
ImageEnhance.Brightness(_b).enhance(.55).save('brand/banner-blur.jpg',quality=70,optimize=True,progressive=True)
# phone login: wordmark + barn door + gloves, inside the frame
im.crop((300,120,1430,600)).save('brand/hero-phone.jpg',quality=84,optimize=True,progressive=True)
print('ok')
