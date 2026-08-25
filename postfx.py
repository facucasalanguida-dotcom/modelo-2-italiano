# Postproceso fotografico: bloom, viñeteo y dispersion de lente ligera.
import numpy as np, sys, os
from PIL import Image, ImageFilter

def postfx(fn, pano=False):
    im = Image.open(fn).convert('RGB')
    a = np.asarray(im, np.float32) / 255.0
    h, w, _ = a.shape
    # revelado calido: balance de blancos, curva S y saturacion
    a *= np.array([1.055, 1.0, 0.925], np.float32)
    a = np.clip(a, 0, 1)
    a = a*a*(3 - 2*a) * 0.35 + a * 0.65          # curva S suave
    g = a.mean(-1, keepdims=True)
    a = np.clip(g + (a - g) * 1.14, 0, 1)        # saturacion
    # sombras ligeramente calidas
    sh = np.clip(1 - a.mean(-1, keepdims=True)*1.6, 0, 1)
    a = np.clip(a + sh * np.array([0.012, 0.006, -0.006], np.float32), 0, 1)
    if not pano:
        # bloom: umbral de altas luces + desenfoque + mezcla screen
        # (en equirectangular el desenfoque no envuelve y marcaria la costura)
        lum = a.max(-1)
        hi = np.clip((lum - 0.82) / 0.18, 0, 1)[..., None] * a
        bl = np.asarray(Image.fromarray((hi*255).astype(np.uint8))
                        .filter(ImageFilter.GaussianBlur(w*0.008)), np.float32)/255.0
        bl2 = np.asarray(Image.fromarray((hi*255).astype(np.uint8))
                         .filter(ImageFilter.GaussianBlur(w*0.03)), np.float32)/255.0
        glow = np.clip(bl*0.55 + bl2*0.35, 0, 1)
        a = 1 - (1 - a) * (1 - glow)      # screen
    if not pano:
        # dispersion: canales R y B escalados radialmente medio pixel
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        cxp, cyp = w/2, h/2
        for c, k in ((0, 1.0009), (2, 0.9991)):
            sx = np.clip((xx - cxp)*k + cxp, 0, w-1)
            sy = np.clip((yy - cyp)*k + cyp, 0, h-1)
            a[..., c] = a[sy.astype(int), sx.astype(int), c]
        # viñeteo elipsoidal suave
        r2 = (((xx-cxp)/(0.78*w))**2 + ((yy-cyp)/(0.78*h))**2)
        vig = 1 - 0.16*np.clip(r2, 0, 1)**1.4
        a *= vig[..., None]
    # grano fino
    rng = np.random.default_rng(5)
    a += rng.normal(0, 0.0045, a.shape).astype(np.float32)
    Image.fromarray((np.clip(a, 0, 1)*255).astype(np.uint8)).save(fn)
    print('postfx', fn)

for fn in sys.argv[1:]:
    if os.path.exists(fn):
        postfx(fn, pano=os.path.basename(fn).startswith('p_'))
