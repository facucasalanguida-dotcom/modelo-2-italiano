# Vinilo de corte para la pared de pizarra (3350 x 3900 mm, 1 unidad = 1 mm).
# Tres vinilos mate: crema, laton y azul Napoli. La pizarra queda vista
# entre las piezas, asi que no hay ningun fondo.
import math, os

CREMA = '#EFE7D8'
LATON = '#C29A5B'
AZUL  = '#3A6B89'      # azul Napoli aclarado un punto para leerse en pizarra

W, H = 3350, 3900
CX = W / 2

def onda(y, x0, x1, amp=26, ciclos=5):
    paso = (x1 - x0) / (ciclos * 2)
    d = f'M {x0} {y}'
    for i in range(ciclos * 2):
        xa = x0 + paso * i
        d += f' q {paso/2} {amp if i%2==0 else -amp} {paso} 0'
    return d

def botella(cx, base, alto, ancho, color):
    """Silueta de botella: cuerpo, hombro, cuello y tapon."""
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

p = []
p.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
  width="{W//10}mm" height="{H//10}mm" font-family="'Bitstream Charter', Charter, Georgia, serif">''')

# ------------------------------------------------------------------ marco
m = 120
p.append(f'<rect x="{m}" y="{m}" width="{W-2*m}" height="{H-2*m}" fill="none" stroke="{LATON}" stroke-width="5"/>')
for x in (m, W - m):
    for y in (m, H - m):
        p.append(f'<rect x="{x-26}" y="{y-26}" width="52" height="52" fill="{CREMA}" transform="rotate(45 {x} {y})"/>')

# ---------------------------------------------------------------- emblema
ecx, ecy, R = CX, 1210, 760
p.append(f'<circle cx="{ecx}" cy="{ecy}" r="{R}" fill="none" stroke="{CREMA}" stroke-width="12"/>')
p.append(f'<circle cx="{ecx}" cy="{ecy}" r="{R-54}" fill="none" stroke="{LATON}" stroke-width="4"/>')
p.append(f'<clipPath id="esc"><circle cx="{ecx}" cy="{ecy}" r="{R-70}"/></clipPath>')
p.append('<g clip-path="url(#esc)">')

hor = ecy + 150
# sol de laton tras la ladera del Somma
p.append(f'<circle cx="{ecx-415}" cy="{hor-505}" r="165" fill="{LATON}"/>')
# Vesubio (Somma + cono) en azul, silueta llena hasta el horizonte
p.append(f'''<path fill="{AZUL}" d="M {ecx-660} {hor}
  L {ecx-390} {hor-350} L {ecx-305} {hor-415} L {ecx-220} {hor-400}
  L {ecx-105} {hor-310} L {ecx-30} {hor-345}
  L {ecx+90} {hor-505} L {ecx+235} {hor-490}
  L {ecx+400} {hor-300} L {ecx+660} {hor} Z"/>''')
# humo del crater: dos volutas crema
p.append(f'''<path fill="none" stroke="{CREMA}" stroke-width="15" stroke-linecap="round"
  d="M {ecx+125} {hor-545} C {ecx+55} {hor-625} {ecx+165} {hor-680} {ecx+95} {hor-760}"/>''')
p.append(f'''<path fill="none" stroke="{CREMA}" stroke-width="11" stroke-linecap="round"
  d="M {ecx+205} {hor-540} C {ecx+270} {hor-615} {ecx+185} {hor-655} {ecx+250} {hor-730}"/>''')
# velero en la bahia
p.append(f'''<path fill="{CREMA}" d="M {ecx+355} {hor+152} L {ecx+355} {hor+38}
  L {ecx+428} {hor+152} Z"/>''')
p.append(f'''<path fill="{LATON}" d="M {ecx+318} {hor+164} L {ecx+462} {hor+164}
  L {ecx+436} {hor+206} L {ecx+344} {hor+206} Z"/>''')
# mar: tres ondas
for dy, col, an in ((95, CREMA, 15), (205, AZUL, 13), (315, CREMA, 15)):
    p.append(f'<path fill="none" stroke="{col}" stroke-width="{an}" stroke-linecap="round" d="{onda(hor+dy, ecx-700, ecx+700)}"/>')
p.append('</g>')

# --------------------------------------------------------------- rombos
for dx in (-110, 0, 110):
    lado = 30 if dx else 42
    p.append(f'<rect x="{CX+dx-lado/2}" y="{2130-lado/2}" width="{lado}" height="{lado}" fill="{LATON}" transform="rotate(45 {CX+dx} 2130)"/>')

# -------------------------------------------------------------- palabras
p.append(f'''<text x="{CX-59}" y="2372" text-anchor="middle" fill="{LATON}"
  font-size="150" letter-spacing="118">CAFÉ</text>''')
for lado_ in (-1, 1):
    x0 = CX + lado_ * 500
    x1 = CX + lado_ * 1180
    p.append(f'<line x1="{x0}" y1="2322" x2="{x1}" y2="2322" stroke="{LATON}" stroke-width="5"/>')
p.append(f'''<text x="{CX-28}" y="2860" text-anchor="middle" fill="{CREMA}"
  font-size="500" font-weight="bold" letter-spacing="56">NAPOLI</text>''')
p.append(f'''<text x="{CX-10}" y="3082" text-anchor="middle" fill="{CREMA}"
  font-family="'Liberation Sans', Arial, sans-serif" font-weight="bold"
  font-size="76" letter-spacing="20">UN OBRADOR ITALIANO A PIE DE CALLE</text>''')

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

p.append(f'''<text x="{CX-9}" y="3212" text-anchor="middle" fill="{LATON}"
  font-family="'Liberation Sans', Arial, sans-serif" font-weight="bold"
  font-size="56" letter-spacing="20">MÁLAGA · CIUDAD DE LA JUSTICIA</text>''')

p.append('</svg>')
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pared_napoli.svg')
open(out, 'w').write('\n'.join(p))
print('svg:', out, os.path.getsize(out)//1024, 'KB')
