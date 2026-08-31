# Tres propuestas de plotter A COBERTURA TOTAL para la pared (3350x3900 mm).
# El logo oficial (negro, vectorial) se mantiene tal cual en las tres.
import os

CREMA = '#EFE7D8'
LATON = '#C29A5B'
AZUL  = '#3A6B89'
AZUL2 = '#2F5872'    # azul mas profundo, para vetas y listones
W, H  = 3350, 3900
IZQ   = 760          # sangrado de campo hacia la izquierda
W2    = W + IZQ
CX    = W / 2
SP    = os.path.dirname(os.path.abspath(__file__))

LB_X, LB_Y, LB_W, LB_H = 163.2, 527.0, 1593.6, 866.1
logo_src = open(f'{SP}/logo_pagina.svg').read()
logo_src = logo_src[logo_src.index('<defs>'):logo_src.rindex('</svg>')]

def logo_svg(x, y, w):
    h = w * LB_H / LB_W
    return (f'<svg x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" '
            f'viewBox="{LB_X} {LB_Y} {LB_W} {LB_H}" '
            f'preserveAspectRatio="xMidYMid meet">{logo_src}</svg>')

def rombo(cx, cy, lado, color):
    return (f'<rect x="{cx-lado/2:.0f}" y="{cy-lado/2:.0f}" width="{lado}" height="{lado}" '
            f'fill="{color}" transform="rotate(45 {cx:.0f} {cy:.0f})"/>')

def botella(cx, base, alto, ancho, color):
    cuello = ancho * 0.32; h_cue = alto * 0.30; r = ancho / 2; top = base - alto
    return (f'<path fill="{color}" d="M {cx-r:.0f} {base} '
            f'L {cx-r:.0f} {top+h_cue+ancho*0.55:.0f} '
            f'Q {cx-r:.0f} {top+h_cue:.0f} {cx-cuello/2:.0f} {top+h_cue*0.72:.0f} '
            f'L {cx-cuello/2:.0f} {top+alto*0.06:.0f} L {cx+cuello/2:.0f} {top+alto*0.06:.0f} '
            f'L {cx+cuello/2:.0f} {top+h_cue*0.72:.0f} '
            f'Q {cx+r:.0f} {top+h_cue:.0f} {cx+r:.0f} {top+h_cue+ancho*0.55:.0f} '
            f'L {cx+r:.0f} {base} Z"/>'
            f'<rect fill="{color}" x="{cx-cuello/2-4:.0f}" y="{top:.0f}" '
            f'width="{cuello+8:.0f}" height="{alto*0.05:.0f}" rx="6"/>')

def botellero(colores, base=3480, escala=1.0):
    alturas = [230, 300, 260, 325, 245, 325, 260, 300, 230]
    anchos  = [86, 92, 78, 98, 84, 98, 78, 92, 86]
    sep = 68 * escala
    total = sum(a*escala for a in anchos) + sep * 8
    x, out = CX - total/2, []
    for a, an, c in zip(alturas, anchos, colores):
        out.append(botella(x + an*escala/2, base, a*escala, an*escala, c))
        x += an*escala + sep
    out.append(f'<line x1="{CX-total/2-70:.0f}" y1="{base+26}" x2="{CX+total/2+70:.0f}" '
               f'y2="{base+26}" stroke="{LATON}" stroke-width="8"/>')
    return ''.join(out)

def texto(y, t, color, fs, ls, dx=0):
    return (f'<text x="{CX+dx}" y="{y}" text-anchor="middle" fill="{color}" '
            f'font-family="\'Liberation Sans\', Arial, sans-serif" font-weight="bold" '
            f'font-size="{fs}" letter-spacing="{ls}">{t}</text>')

def abrir(fondo):
    return [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W2} {H}"
  width="{W2//10}mm" height="{H//10}mm">
<rect x="0" y="0" width="{W2}" height="{H}" fill="{fondo}"/>
<g transform="translate({IZQ},0)">''']

# ================================================= A. GALLERIA (crema total)
p = abrir(CREMA)
BOT = 3640            # el marco remata por encima del corte contra el suelo
p.append(f'<rect x="100" y="100" width="{W-200}" height="{BOT-100}" fill="none" stroke="{LATON}" stroke-width="5"/>')
p.append(f'<rect x="150" y="150" width="{W-300}" height="{BOT-200}" fill="none" stroke="{LATON}" stroke-width="2.5"/>')
for x in (150, W-150):
    for y in (150, BOT-50):
        p.append(rombo(x, y, 44, AZUL))
p.append(rombo(CX, 470, 40, LATON))
p.append(logo_svg(CX-1025, 640, 2050))
p.append(rombo(CX, 1990, 34, AZUL))
p.append(texto(2210, 'CUCINA ITALIANA', AZUL, 104, 34, -17))
p.append(texto(2360, 'MÁLAGA · CIUDAD DE LA JUSTICIA', AZUL, 58, 21, -10))
p.append(f'<line x1="{CX-560}" y1="2560" x2="{CX-80}" y2="2560" stroke="{LATON}" stroke-width="5"/>')
p.append(f'<line x1="{CX+80}" y1="2560" x2="{CX+560}" y2="2560" stroke="{LATON}" stroke-width="5"/>')
p.append(rombo(CX, 2560, 36, LATON))
p.append(botellero([AZUL, LATON, AZUL2, AZUL, LATON, AZUL, AZUL2, LATON, AZUL], base=3420, escala=1.18))
p.append('</g></svg>')
open(f'{SP}/pared_A.svg', 'w').write('\n'.join(p))

# ============================================ B. MEDALLONE (azul total)
p = abrir(AZUL)
# veta de listones sutiles sobre el azul (raya profunda cada 140 mm)
for i in range(-5, 24):
    x = i * 140
    p.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{AZUL2}" stroke-width="7"/>')
BOT = 3640
p.append(f'<rect x="100" y="100" width="{W-200}" height="{BOT-100}" fill="none" stroke="{LATON}" stroke-width="5"/>')
for x in (100, W-100):
    for y in (100, BOT):
        p.append(rombo(x, y, 52, CREMA))
PW = 2400; PX0 = CX-PW/2; PX1 = CX+PW/2; ARR = PW/2; YARR = 380+ARR; PYB = 2740
p.append(f'''<path fill="{CREMA}" d="M {PX0} {PYB} L {PX0} {YARR}
  A {ARR} {ARR} 0 0 1 {PX1} {YARR} L {PX1} {PYB} Z"/>''')
ins = 55
p.append(f'''<path fill="none" stroke="{LATON}" stroke-width="4"
  d="M {PX0+ins} {PYB-ins} L {PX0+ins} {YARR}
  A {ARR-ins} {ARR-ins} 0 0 1 {PX1-ins} {YARR} L {PX1-ins} {PYB-ins} Z"/>''')
p.append(rombo(CX, 625, 40, AZUL))
p.append(logo_svg(CX-950, 900, 1900))
p.append(rombo(CX, 2085, 34, AZUL))
p.append(texto(2290, 'CUCINA ITALIANA', AZUL, 96, 31, -16))
p.append(texto(2430, 'MÁLAGA · CIUDAD DE LA JUSTICIA', AZUL, 56, 20, -10))
p.append(botellero([CREMA, LATON, CREMA, LATON, CREMA, LATON, CREMA, LATON, CREMA], base=3450, escala=1.05))
p.append('</g></svg>')
open(f'{SP}/pared_B.svg', 'w').write('\n'.join(p))

# ========================================= C. BOTTEGA (zocalo de listones)
p = abrir(CREMA)
ZY = 2620                                     # arranque del zocalo
p.append(f'<rect x="{-IZQ}" y="{ZY}" width="{W2}" height="{H-ZY}" fill="{AZUL}"/>')
paso, listn = 112, 92                         # listones verticales del zocalo
x = (W % paso) / 2 - IZQ
while x < W:
    p.append(f'<rect x="{x:.0f}" y="{ZY}" width="{listn}" height="{H-ZY}" fill="{AZUL2}"/>')
    x += paso
p.append(f'<line x1="{-IZQ}" y1="{ZY-14}" x2="{W}" y2="{ZY-14}" stroke="{LATON}" stroke-width="12"/>')
p.append(f'<line x1="{-IZQ}" y1="{ZY+26}" x2="{W}" y2="{ZY+26}" stroke="{LATON}" stroke-width="4"/>')
# zona crema superior
p.append(f'<path fill="none" stroke="{LATON}" stroke-width="4" '
         f'd="M 100 {ZY-14} L 100 100 L {W-100} 100 L {W-100} {ZY-14}"/>')
for x_ in (100, W-100):
    p.append(rombo(x_, 100, 44, AZUL))
# arco de linea alrededor del logo
p.append(f'''<path fill="none" stroke="{LATON}" stroke-width="6"
  d="M {CX-1130} 2255 L {CX-1130} 1445 A 1130 1130 0 0 1 {CX+1130} 1445 L {CX+1130} 2255"/>''')
p.append(rombo(CX, 500, 40, AZUL))
p.append(logo_svg(CX-975, 760, 1950))
p.append(rombo(CX, 1965, 34, AZUL))
p.append(texto(2160, 'CUCINA ITALIANA', AZUL, 96, 31, -16))
p.append(texto(2300, 'MÁLAGA · CIUDAD DE LA JUSTICIA', AZUL, 54, 19, -9))
# botellas crema y laton sobre los listones del zocalo
p.append(botellero([CREMA, LATON, CREMA, LATON, CREMA, LATON, CREMA, LATON, CREMA], base=3430, escala=1.1))
p.append('</g></svg>')
open(f'{SP}/pared_C.svg', 'w').write('\n'.join(p))

for v in 'ABC':
    print(f'pared_{v}.svg', os.path.getsize(f'{SP}/pared_{v}.svg')//1024, 'KB')
