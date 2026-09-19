# -*- coding: utf-8 -*-
"""Vista axonometrica del modelo 3D, leida del mismo generador."""
import math, sys, os
sys.path.insert(0,'/home/user/modelo-2-italiano/docs/planos')
import export_sketchup as X
import cairosvg

CORTE = float(sys.argv[1]) if len(sys.argv) > 1 else 1.60   # altura de corte
SALIDA = sys.argv[2] if len(sys.argv) > 2 else '/tmp/vista.png'
ALTAS = ('02 Muros', '03 Pilares', '04 Carpinteria', '07 Bano', '08 Escalera',
         '09 Forjado', '14 Planta alta', '15 Techo', '13 Instalaciones')

C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
def proy(x, y, z):
    return ((x - y) * C30, (x + y) * S30 - z)

COL = {k: v[1] for k, v in X.MAT.items()}
def hexa(rgb, f=1.0):
    return '#%02x%02x%02x' % tuple(max(0, min(255, int(c * f))) for c in rgb)

PLANTA = os.environ.get('PLANTA', 'baja')
ZONA = os.environ.get('ZONA')
ZONA = [float(v) for v in ZONA.split(',')] if ZONA else None
def fuera(x0, y0, x1, y1):
    return ZONA and (x1 <= ZONA[0] or x0 >= ZONA[2] or y1 <= ZONA[1] or y0 >= ZONA[3])
Z_BASE = 2.560 if PLANTA == 'alta' else 0.0
solidos = []
for tg, mt, nm, x0, y0, x1, y1, z0, z1 in X.cajas:
    if PLANTA == 'alta':
        if z1 <= 2.560 + 1e-6 and tg != '09 Forjado':
            continue
        z0 = max(z0, 2.560)
    elif tg in ('09 Forjado', '15 Techo', '14 Planta alta'):
        continue
    if tg in ALTAS or PLANTA == 'alta':
        z1 = min(z1, Z_BASE + CORTE)
    if z1 <= z0 or fuera(x0, y0, x1, y1):
        continue
    solidos.append((tg, mt, x0, y0, x1, y1, z0, z1))
for tg, mt, nm, pts, z0, z1 in X.prismas:
    if tg != ('09 Forjado' if PLANTA == 'alta' else '01 Solera'):
        continue
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    if fuera(min(xs), min(ys), max(xs), max(ys)): continue
    solidos.append((tg, mt, min(xs), min(ys), max(xs), max(ys), z0, z1))
for tg, mt, nm, cx, cy, r, z0, z1 in X.cilindros:
    if PLANTA == 'alta':
        if z1 <= 2.560 + 1e-6: continue
        z0 = max(z0, 2.560)
    z1 = min(z1, Z_BASE + CORTE)
    if z1 <= z0 or fuera(cx - r, cy - r, cx + r, cy + r): continue
    solidos.append((tg, mt, cx - r, cy - r, cx + r, cy + r, z0, z1))

# paneles verticales (muros de canto variable): se dibujan aparte, con su
# perfil real, porque su coronacion no es horizontal
panelitos = []
for tg, mt, nm, pts, x0, x1 in X.paneles:
    if PLANTA == 'alta' or fuera(x0, min(p[0] for p in pts), x1,
                                 max(p[0] for p in pts)):
        continue
    tope = Z_BASE + CORTE if tg in ALTAS else 1e9
    q = [(y, min(z, tope)) for y, z in pts]
    panelitos.append((mt, q, x0, x1))

solidos.sort(key=lambda s: (s[2] + s[3] + s[6]))
pts = [proy(x, y, z) for _, _, x0, y0, x1, y1, z0, z1 in solidos
       for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
pts += [proy(x, y, z) for _, q, x0, x1 in panelitos for x in (x0, x1)
        for y, z in q]
us = [p[0] for p in pts]; vs = [p[1] for p in pts]
ESC = 1700 / (max(us) - min(us))
W = int((max(us) - min(us)) * ESC) + 80
H = int((max(vs) - min(vs)) * ESC) + 80
def px(u, v): return (40 + (u - min(us)) * ESC, 40 + (v - min(vs)) * ESC)

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#f4f2ee"/>']
for tg, mt, x0, y0, x1, y1, z0, z1 in solidos:
    base = COL.get(mt, (150, 150, 150))
    caras = [
        ([(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)], 1.00),   # techo
        ([(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)], 0.78),   # cara Sur
        ([(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)], 0.62),   # cara Este
    ]
    for vert, f in caras:
        d = ' '.join('%.2f,%.2f' % px(*proy(*p)) for p in vert)
        out.append(f'<polygon points="{d}" fill="{hexa(base,f)}" '
                   f'stroke="#3a3a3a" stroke-width="0.6" stroke-linejoin="round"/>')
for mt, q, x0, x1 in panelitos:
    base = COL.get(mt, (150, 150, 150))
    for xx, f in ((x1, 0.62), (x0, 0.70)):
        d = ' '.join('%.2f,%.2f' % px(*proy(xx, y, z)) for y, z in q)
        out.append(f'<polygon points="{d}" fill="{hexa(base,f)}" '
                   f'stroke="#3a3a3a" stroke-width="0.6"/>')
    for (ya, za), (yb, zb) in zip(q, q[1:] + q[:1]):
        d = ' '.join('%.2f,%.2f' % px(*proy(*p)) for p in
                     ((x0, ya, za), (x1, ya, za), (x1, yb, zb), (x0, yb, zb)))
        out.append(f'<polygon points="{d}" fill="{hexa(base,0.95)}" '
                   f'stroke="#3a3a3a" stroke-width="0.6"/>')

out.append('</svg>')
svg = '\n'.join(out)
cairosvg.svg2png(bytestring=svg.encode(), write_to=SALIDA, output_width=W)
print(SALIDA, W, H, len(solidos), 'solidos')
