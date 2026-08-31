# Vinilo para la pared de pizarra (3350 x 3900 mm, 1 unidad = 1 mm).
# CASA MARGOT - cucina italiana. El logo oficial (negro) va sobre un panel
# crema en arco con los colores del local; el resto es vinilo de corte
# directamente sobre la pizarra vista.
import os, re

CREMA = '#EFE7D8'
LATON = '#C29A5B'
AZUL  = '#3A6B89'
NEGRO = '#1B1B1B'

W, H = 3350, 3900
CX = W / 2
SP = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------ logo vectorial oficial
# caja util del arte dentro de la pagina de 1920x1920 pt del PDF
LB_X, LB_Y, LB_W, LB_H = 163.2, 527.0, 1593.6, 866.1
logo = open(f'{SP}/logo_pagina.svg').read()
logo = logo[logo.index('<defs>'):]                       # fuera la etiqueta <svg> externa
logo = logo[:logo.rindex('</svg>')]

def logo_svg(x, y, w):
    h = w * LB_H / LB_W
    return (f'<svg x="{x}" y="{y}" width="{w}" height="{h}" '
            f'viewBox="{LB_X} {LB_Y} {LB_W} {LB_H}" '
            f'preserveAspectRatio="xMidYMid meet">{logo}</svg>')

def botella(cx, base, alto, ancho, color):
    cuello = ancho * 0.32
    h_cue  = alto * 0.30
    r      = ancho / 2
    top    = base - alto
    return (f'<path fill="{color}" d="M {cx-r} {base} '
            f'L {cx-r} {top+h_cue+ancho*0.55} '
            f'Q {cx-r} {top+h_cue} {cx-cuello/2} {top+h_cue*0.72} '
            f'L {cx-cuello/2} {top+alto*0.06} '
            f'L {cx+cuello/2} {top+alto*0.06} '
            f'L {cx+cuello/2} {top+h_cue*0.72} '
            f'Q {cx+r} {top+h_cue} {cx+r} {top+h_cue+ancho*0.55} '
            f'L {cx+r} {base} Z"/>'
            f'<rect fill="{color}" x="{cx-cuello/2-4}" y="{top}" '
            f'width="{cuello+8}" height="{alto*0.05}" rx="6"/>')

def rombo(cx, cy, lado, color):
    return (f'<rect x="{cx-lado/2}" y="{cy-lado/2}" width="{lado}" height="{lado}" '
            f'fill="{color}" transform="rotate(45 {cx} {cy})"/>')

p = []
p.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
  width="{W//10}mm" height="{H//10}mm" font-family="'Bitstream Charter', Charter, Georgia, serif">''')

# ------------------------------------------------------------------ marco
m = 120
p.append(f'<rect x="{m}" y="{m}" width="{W-2*m}" height="{H-2*m}" fill="none" stroke="{LATON}" stroke-width="5"/>')
for x in (m, W - m):
    for y in (m, H - m):
        p.append(rombo(x, y, 52, CREMA))

# ------------------------------------------------- panel crema en arco
PW   = 2360                    # ancho del panel
PX0, PX1 = CX - PW/2, CX + PW/2
ARR  = PW / 2                  # radio del arco = medio ancho
YARR = 300 + ARR               # linea de arranque del arco (la cima queda en y=300)
PYB  = 2760                    # base del panel
p.append(f'''<path fill="{CREMA}" d="M {PX0} {PYB} L {PX0} {YARR}
  A {ARR} {ARR} 0 0 1 {PX1} {YARR} L {PX1} {PYB} Z"/>''')
ins = 55                       # filete interior de laton
p.append(f'''<path fill="none" stroke="{LATON}" stroke-width="4"
  d="M {PX0+ins} {PYB-ins} L {PX0+ins} {YARR}
  A {ARR-ins} {ARR-ins} 0 0 1 {PX1-ins} {YARR} L {PX1-ins} {PYB-ins} Z"/>''')

# rombo azul en la clave del arco
p.append(rombo(CX, 545, 40, AZUL))

# logo oficial en negro sobre el panel
p.append(logo_svg(CX - 940, 830, 1880))

# rotulacion bajo el logo, en azul del local
p.append(rombo(CX, 2020, 34, AZUL))
p.append(f'''<text x="{CX-15}" y="2225" text-anchor="middle" fill="{AZUL}"
  font-family="'Liberation Sans', Arial, sans-serif" font-weight="bold"
  font-size="92" letter-spacing="30">CUCINA ITALIANA</text>''')
p.append(f'''<text x="{CX-9}" y="2360" text-anchor="middle" fill="{AZUL}"
  font-family="'Liberation Sans', Arial, sans-serif" font-weight="bold"
  font-size="54" letter-spacing="19">MÁLAGA · CIUDAD DE LA JUSTICIA</text>''')

# --------------------------------------------------------------- rombos
for dx in (-110, 0, 110):
    p.append(rombo(CX + dx, 2950, 30 if dx else 42, LATON))

# -------------------------------------------------- botellero del fondo
alturas = [230, 300, 260, 325, 245, 325, 260, 300, 230]
colores = [AZUL, LATON, CREMA, AZUL, LATON, AZUL, CREMA, LATON, AZUL]
anchos  = [86, 92, 78, 98, 84, 98, 78, 92, 86]
sep, base = 68, 3600
total = sum(anchos) + sep * (len(anchos) - 1)
x = CX - total / 2
for a, c, an in zip(alturas, colores, anchos):
    p.append(botella(x + an/2, base, a, an, c))
    x += an + sep
p.append(f'<line x1="{CX-total/2-70}" y1="3626" x2="{CX+total/2+70}" y2="3626" stroke="{LATON}" stroke-width="8"/>')

p.append('</svg>')
out = os.path.join(SP, 'pared_margot.svg')
open(out, 'w').write('\n'.join(p))
print('svg:', out, os.path.getsize(out)//1024, 'KB')
