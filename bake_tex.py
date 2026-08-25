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
