# Hornea texturas PBR 2K procedurales: difuso + rugosidad + normal.
import numpy as np
from PIL import Image, ImageFilter
import os
os.makedirs('tex', exist_ok=True)
N = 2048
rng = np.random.default_rng(11)

def save(name, arr):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(f'tex/{name}.png')
    print(name)

def fbm(shape, octaves=5, base=4, seed=0):
    r = np.random.default_rng(seed)
    out = np.zeros(shape, np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = base * (2 ** o)
        g = r.random((n, n)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize(shape[::-1], Image.BICUBIC)
        out += amp * (np.asarray(im, np.float32) / 255.0)
        tot += amp; amp *= 0.5
    return out / tot

def normal_from_height(h, strength=2.0):
    gy, gx = np.gradient(h.astype(np.float32))
    nx = -gx * strength; ny = gy * strength; nz = np.ones_like(h)
    l = np.sqrt(nx*nx + ny*ny + nz*nz)
    n = np.stack([nx/l, ny/l, nz/l], -1)
    return (n * 0.5 + 0.5) * 255

# ---------------------------------------------------------------- SUELO ROBLE
# El tile cubre 2,40 x 2,40 m -> tablas de 1,20 x 0,20 m (2 x 12 tablas)
PLW, PLH = N // 2, (N + 11) // 12
diff = np.zeros((N, N, 3), np.float32)
rough = np.zeros((N, N), np.float32)
height = np.zeros((N, N), np.float32)
yy, xx = np.mgrid[0:N, 0:N]
tonos = [(216,192,152),(206,180,138),(222,199,160),(199,172,130),(212,186,144)]
for row in range(12):
    off = (row % 2) * (PLW // 2)
    for colk in range(3):
        x0 = colk * PLW - off
        x1 = x0 + PLW
        m = (yy // PLH == row) & (xx >= x0) & (xx < x1)
        if not m.any(): continue
        t = np.array(tonos[rng.integers(len(tonos))], np.float32)
        t = t * rng.uniform(0.97, 1.04)
        g = fbm((N, N), 5, 3, seed=int(rng.integers(9999)))
        # veta estirada a lo largo de la tabla
        gr = np.asarray(Image.fromarray((g*255).astype(np.uint8))
                        .resize((N, N//14), Image.BICUBIC)
                        .resize((N, N), Image.BICUBIC), np.float32)/255.0
        vet = 0.5 + 0.5*np.sin(gr*10 + xx/N*420 + rng.uniform(0, 9))
        sh = (0.955 + 0.055*vet)
        for c in range(3):
            diff[..., c][m] = t[c] * sh[m]
        rough[m] = 0.33 + 0.05*vet[m] + rng.uniform(-0.02, 0.02)
        height[m] = rng.uniform(0.35, 0.65)
# juntas oscuras entre tablas
seamy = (yy % PLH < 2) | (yy % PLH > PLH-3)
seamx = np.zeros_like(seamy)
for row in range(12):
    off = (row % 2) * (PLW // 2)
    rm = (yy // PLH == row)
    sx = ((xx + off) % PLW < 2) | ((xx + off) % PLW > PLW-3)
    seamx |= rm & sx
seam = seamy | seamx
diff[seam] *= 0.55
rough[seam] = 0.75
height[seam] = 0.0
hblur = np.asarray(Image.fromarray((height*255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(1.2)), np.float32)/255.0
save('floor_diff', diff)
save('floor_rough', np.dstack([rough*255]*3))
save('floor_nrm', normal_from_height(hblur, 3.0))

# ---------------------------------------------------------------- MADERA FINA
g = fbm((N, N), 6, 4, seed=77)
gr = np.asarray(Image.fromarray((g*255).astype(np.uint8))
                .resize((N, N//44), Image.BICUBIC)
                .resize((N, N), Image.BICUBIC), np.float32)/255.0
vet = 0.5 + 0.5*np.sin(gr*16 + xx/N*130)
fino = fbm((N, N), 6, 32, seed=78)
base = np.array([201, 158, 105], np.float32)
d2 = np.zeros((N, N, 3), np.float32)
sh = (0.93 + 0.11*vet) * (0.97 + 0.06*fino)
for c in range(3): d2[..., c] = base[c] * sh
save('wood_diff', d2)
save('wood_rough', np.dstack([(0.34 + 0.12*vet + 0.06*fino)*255]*3))
save('wood_nrm', normal_from_height(vet*0.4 + fino*0.2, 1.2))

# ---------------------------------------------------------------- YESO PARED
p1 = fbm((N, N), 6, 6, seed=5)
p2 = fbm((N, N), 4, 48, seed=6)
base = np.array([218, 216, 201], np.float32)
d3 = np.zeros((N, N, 3), np.float32)
sh = 0.96 + 0.05*p1 + 0.04*p2
for c in range(3): d3[..., c] = base[c] * sh
save('wall_diff', d3)
save('wall_rough', np.dstack([(0.82 + 0.10*p2)*255]*3))
save('wall_nrm', normal_from_height(p1*0.5 + p2*0.5, 0.9))

# ---------------------------------------------------------------- TELA
wx = 0.5 + 0.5*np.sin(xx/N*2*np.pi*420)
wy = 0.5 + 0.5*np.sin(yy/N*2*np.pi*420)
weave = wx*wy
fuzz = fbm((N, N), 5, 24, seed=9)
save('fabric_nrm', normal_from_height(weave*0.5 + fuzz*0.4, 1.6))
save('fabric_rough', np.dstack([(0.86 + 0.10*fuzz)*255]*3))

# ---------------------------------------------------------------- LAMINAS ARTE
for i, (a, b, c) in enumerate([((62,107,153),(226,214,190),(201,158,105)),
                               ((201,158,105),(62,107,153),(246,243,236)),
                               ((150,120,84),(226,214,190),(62,107,153))]):
    art = np.full((512, 400, 3), (238, 232, 220), np.float32)
    r = np.random.default_rng(40 + i)
    for k in range(5):
        col = [a, b, c][k % 3]
        cx, cy = r.integers(60, 340), r.integers(70, 440)
        rad = r.integers(40, 130)
        m = (np.mgrid[0:512, 0:400][1]-cx)**2 + (np.mgrid[0:512, 0:400][0]-cy)**2 < rad**2
        art[m] = np.array(col, np.float32) * r.uniform(0.92, 1.05)
    save(f'art_{i}', art)
# versiones giradas 90 grados para superficies de veta vertical
for nm in ('wood_diff', 'wood_rough', 'wood_nrm'):
    im = Image.open(f'tex/{nm}.png').transpose(Image.ROTATE_90)
    im.save(f'tex/{nm}_v.png')
    print(nm + '_v')
print('texturas horneadas')

# ---------------------------------------------------------------- FOTOS B/N
# Láminas fotográficas en blanco y negro con paspartú blanco, como las de
# la referencia: horizonte de mar, faro y calle italiana en silueta.
for i in range(3):
    H, W = 520, 400
    img = np.full((H, W, 3), 244.0, np.float32)
    r = np.random.default_rng(70 + i)
    m0, m1 = 58, 62            # margen del paspartú
    ph, pw = H - m0*2, W - m0*2
    yy2, xx2 = np.mgrid[0:ph, 0:pw]
    # cielo en degradado
    foto = 205 - 90 * (yy2 / ph)
    hor = int(ph * (0.55 + 0.08*i))
    foto[hor:, :] = 78 + 26 * ((yy2[hor:, :] - hor) / max(ph - hor, 1))
    if i == 0:
        # faro
        cx = int(pw*0.62)
        for dy in range(hor-90, hor):
            w = 8 + (dy-(hor-90))//12
            foto[dy, max(cx-w,0):min(cx+w,pw)] = 38
        foto[hor-104:hor-90, cx-16:cx+16] = 30
    elif i == 1:
        # barca en el mar
        bx0, by0 = int(pw*0.35), hor+18
        foto[by0:by0+8, bx0:bx0+56] = 34
        foto[by0-16:by0, bx0+24:bx0+28] = 40
    else:
        # skyline
        x = 0
        while x < pw:
            w = int(r.integers(22, 48)); h2 = int(r.integers(30, 110))
            foto[hor-h2:hor, x:min(x+w, pw)] = 30 + r.integers(0, 22)
            x += w
    g = np.asarray(Image.fromarray(foto.astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(0.8)), np.float32)
    img[m0:m0+ph, m0:m0+pw] = g[..., None]
    save(f'art_{i}', img)
print('fotos b/n horneadas')

# ---------------------------------------------------------------- FACHADA VECINA
# Edificio de enfrente para el fondo de las vistas por el escaparate.
fw, fh = 1024, 768
fac = np.full((fh, fw, 3), (232, 228, 218), np.float32)
r = np.random.default_rng(21)
fac *= (0.96 + 0.06*fbm((fh, fw), 4, 6, seed=31))[..., None]
for fila in range(4):
    for colu in range(9):
        x0 = 40 + colu*110; y0 = 80 + fila*170
        w, h = 70, 110
        tone = 52 + r.integers(0, 30)
        fac[y0:y0+h, x0:x0+w] = tone
        fac[y0:y0+h, x0:x0+6] = tone + 40      # brillo lateral del cristal
        fac[y0+h:y0+h+8, x0-6:x0+w+6] = 190    # vierteaguas
save('facade', fac)
print('fachada vecina horneada')

# ---------------------------------------------------------------- LATTE ART
# Rosetta/corazon de leche sobre la crema del capuchino (se ve desde arriba).
from PIL import ImageDraw, ImageFont
N2 = 512
yy, xx = np.mgrid[0:N2, 0:N2].astype(np.float32)
u = (xx - N2/2) / (N2*0.36)
v = (N2/2 - yy) / (N2*0.36)
crema = np.zeros((N2, N2, 3), np.float32)
crema[..., 0] = 178; crema[..., 1] = 128; crema[..., 2] = 82
rr2 = u*u + v*v
crema *= (1.0 - 0.18*np.clip(rr2, 0, 1))[..., None]
# corazon: (x^2+y^2-1)^3 - x^2 y^3 < 0
hu, hv = u/0.78, v/0.78 - 0.12
heart = (hu*hu + hv*hv - 1)**3 - hu*hu*hv**3
mask = np.clip(-heart*6, 0, 1)
# tallo del rosetta
tallo = np.exp(-(hu/0.05)**2) * np.clip(1 - np.abs(hv+0.55)/0.75, 0, 1) * 0.9
mask = np.clip(mask + tallo, 0, 1)
mask = np.asarray(Image.fromarray((mask*255).astype(np.uint8))
                  .filter(ImageFilter.GaussianBlur(4)), np.float32)/255
leche = np.array((244, 238, 226), np.float32)
img = crema*(1-mask[..., None]) + leche*mask[..., None]
img *= (0.97 + 0.05*fbm((N2, N2), 3, 8, seed=77))[..., None]
save('latte', img)
print('latte art horneado')

# ---------------------------------------------------------------- DIARIO SUR
pw, ph = 768, 560
pap = np.full((ph, pw, 3), (238, 235, 228), np.float32)
pap *= (0.97 + 0.05*fbm((ph, pw), 3, 6, seed=41))[..., None]
pil = Image.fromarray(pap.astype(np.uint8))
dr = ImageDraw.Draw(pil)
f_mast = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 84)
f_head = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
f_sub  = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
dr.text((pw/2, 66), 'Diario SUR', font=f_mast, fill=(20, 20, 24), anchor='mm')
dr.line((40, 122, pw-40, 122), fill=(30, 30, 34), width=4)
dr.line((40, 130, pw-40, 130), fill=(30, 30, 34), width=2)
dr.text((44, 128), 'MALAGA', font=f_sub, fill=(60, 60, 64), anchor='ls')
dr.text((pw-44, 128), 'EDICION DE LA MANANA', font=f_sub, fill=(60, 60, 64), anchor='rs')
dr.text((44, 175), 'Malaga estrena su paseo maritimo', font=f_head, fill=(25, 25, 28), anchor='lm')
dr.text((44, 213), 'renovado frente al Mediterraneo', font=f_head, fill=(25, 25, 28), anchor='lm')
# foto del articulo
dr.rectangle((44, 250, 370, 452), fill=(120, 138, 150))
dr.rectangle((44, 380, 370, 452), fill=(96, 110, 118))
dr.rectangle((44, 250, 370, 300), fill=(168, 186, 196))
# columnas de texto simulado
rng2 = np.random.default_rng(5)
for cx0 in (396, 586):
    yy0 = 258
    while yy0 < 530:
        wln = int(rng2.integers(120, 172))
        dr.line((cx0, yy0, cx0 + wln, yy0), fill=(94, 92, 90), width=3)
        yy0 += 11
for cx0 in (44,):
    yy0 = 470
    while yy0 < 530:
        wln = int(rng2.integers(240, 322))
        dr.line((cx0, yy0, cx0 + wln, yy0), fill=(94, 92, 90), width=3)
        yy0 += 11
save('diario', np.asarray(pil, np.float32))
print('diario horneado')

# ---------------------------------------------------------------- CARTA
cw, chh = 384, 512
cara = np.full((chh, cw, 3), (58, 44, 36), np.float32)
cara *= (0.92 + 0.14*fbm((chh, cw), 4, 5, seed=51))[..., None]
pil = Image.fromarray(cara.astype(np.uint8))
dr = ImageDraw.Draw(pil)
f_c1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 44)
f_c2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
oro = (196, 158, 84)
dr.rectangle((28, 28, cw-28, chh-28), outline=oro, width=3)
dr.text((cw/2, 200), 'CAFE', font=f_c1, fill=oro, anchor='mm')
dr.text((cw/2, 258), 'NAPOLI', font=f_c1, fill=oro, anchor='mm')
dr.text((cw/2, 330), 'MALAGA', font=f_c2, fill=oro, anchor='mm')
save('carta', np.asarray(pil, np.float32))
print('carta horneada')
