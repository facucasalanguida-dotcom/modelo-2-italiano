# -*- coding: utf-8 -*-
"""
Planos tecnicos de ESTRUCTURA del local: planta baja y planta alta.

Solo se representa la caja construida —muros, medianeras, pilares, machones,
viga descolgada, forjado, escalera, carpinteria de fachada y puntos de luz del
techo—. No se dibuja mobiliario, barra, cocina ni equipamiento: el plano se
entrega vacio para acotar a mano sobre el.

    python3 build_planos.py        ->  PLANTA_BAJA.pdf, PLANTA_ALTA.pdf,
                                       Planos_Estructura.pdf y PNG de control
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estructura as E
from dibujo import Lienzo, TRAZO, TINTA, POCHE, POCHE_PIL, POCHE_TAB, VIDRIO, COTA_COL

AQUI = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- formato A3
W, H = 420.0, 297.0
ESC = 20.0                      # mm por metro  ->  1:50
MARGEN = 8.0
CAJ_X = W - MARGEN - 96.0       # borde izquierdo del cajetin
OX, OY = 62.0, 236.0            # papel del origen de obra

FECHA = '12 de septiembre de 2026'

DEFS = '''<defs>
<pattern id="doble" width="3.2" height="3.2" patternTransform="rotate(45)"
         patternUnits="userSpaceOnUse">
  <line x1="0" y1="0" x2="0" y2="3.2" stroke="#c3ced6" stroke-width="0.28"/>
</pattern>
<pattern id="vacio" width="2.4" height="2.4" patternTransform="rotate(45)"
         patternUnits="userSpaceOnUse">
  <line x1="0" y1="0" x2="0" y2="2.4" stroke="#b9c6cf" stroke-width="0.35"/>
</pattern>
<pattern id="horm" width="1.6" height="1.6" patternTransform="rotate(45)"
         patternUnits="userSpaceOnUse">
  <line x1="0" y1="0" x2="0" y2="1.6" stroke="#ffffff" stroke-width="0.30"/>
</pattern>
</defs>'''


# ============================================================ hoja y cajetin
def marco(L, titulo, numero, subtitulo, notas, leyenda, cuadro=None):
    L.p_rect('hoja', MARGEN, MARGEN, W - MARGEN, H - MARGEN, 'none', TINTA, 'corte')
    L.p_rect('hoja', MARGEN + 1.2, MARGEN + 1.2, W - MARGEN - 1.2, H - MARGEN - 1.2,
             'none', TINTA, 'auxiliar')
    x0, y0, x1, y1 = CAJ_X, MARGEN, W - MARGEN, H - MARGEN
    L.p_rect('cajetin', x0, y0, x1, y1, '#ffffff', TINTA, 'corte')

    y = y0 + 9.0
    L.p_texto('cajetin', x0 + 5, y, 'GRUPO SUMA', 6.2, 'start', TINTA, 'bold',
              espaciado='1.2')
    y += 4.6
    L.p_texto('cajetin', x0 + 5, y, 'Reformas y proyectos · Málaga', 2.5, 'start',
              '#666666')
    y += 3.2
    L.p_linea('cajetin', x0 + 5, y, x1 - 5, y, TINTA, 'medio')

    def bloque(etiqueta, valor, alto=3.0, peso='bold'):
        nonlocal y
        y += 5.2
        L.p_texto('cajetin', x0 + 5, y, etiqueta, 2.1, 'start', '#777777')
        y += 4.0
        for i, linea in enumerate(valor.split('\n')):
            if i:
                y += alto + 1.0
            L.p_texto('cajetin', x0 + 5, y, linea, alto, 'start', TINTA, peso)

    bloque('PROYECTO', 'Reforma integral de local\nde hostelería', 3.2)
    bloque('EMPLAZAMIENTO', 'Local en planta baja y altillo\nMálaga', 2.9, 'normal')
    bloque('PLANO', titulo, 4.4)
    L.p_texto('cajetin', x0 + 5, y + 4.6, subtitulo, 2.5, 'start', '#555555')
    y += 7.0
    L.p_linea('cajetin', x0 + 5, y, x1 - 5, y, TINTA, 'auxiliar')

    # --- leyenda
    y += 5.5
    L.p_texto('cajetin', x0 + 5, y, 'LEYENDA', 2.1, 'start', '#777777')
    y += 1.6
    for relleno, trazo, txt in leyenda:
        y += 5.0
        if relleno == 'linea':
            L.p_linea('cajetin', x0 + 5, y - 1.2, x0 + 13, y - 1.2, trazo, 'fino',
                      ' stroke-dasharray="1.6 1.1"')
        elif relleno == 'punto':
            L._add('cajetin', f'<circle cx="{x0 + 9:.2f}" cy="{y - 1.2:.2f}" '
                              f'r="1.5" fill="none" stroke="{trazo}" stroke-width="0.25"/>')
        else:
            L.p_rect('cajetin', x0 + 5, y - 3.4, x0 + 13, y + 0.2, relleno, trazo,
                     'fino')
        L.p_texto('cajetin', x0 + 15.5, y, txt, 2.4, 'start', TINTA)

    y += 5.0
    L.p_linea('cajetin', x0 + 5, y, x1 - 5, y, TINTA, 'auxiliar')

    # --- cuadro de superficies / alturas
    if cuadro:
        y += 4.6
        L.p_texto('cajetin', x0 + 5, y, cuadro[0], 2.1, 'start', '#777777')
        for etq, val in cuadro[1]:
            y += 4.2
            L.p_texto('cajetin', x0 + 5, y, etq, 2.4, 'start', '#333333')
            L.p_texto('cajetin', x1 - 5, y, val, 2.4, 'end', TINTA, 'bold')
        y += 3.4
        L.p_linea('cajetin', x0 + 5, y, x1 - 5, y, TINTA, 'auxiliar')

    # --- cuadro de pilares
    y += 4.6
    L.p_texto('cajetin', x0 + 5, y, 'PILARES Y MACHONES  (secciones en m)', 2.1,
              'start', '#777777')
    for tag, nm, a, b, c, d in E.PILARES:
        y += 4.2
        L.p_texto('cajetin', x0 + 5, y, f'{tag}  {nm}', 2.3, 'start', '#333333')
        L.p_texto('cajetin', x1 - 5, y,
                  f'{c - a:.2f} × {d - b:.2f}'.replace('.', ','), 2.3, 'end',
                  TINTA, 'bold')
    y += 3.4
    L.p_linea('cajetin', x0 + 5, y, x1 - 5, y, TINTA, 'auxiliar')

    # --- notas
    y += 4.6
    L.p_texto('cajetin', x0 + 5, y, 'NOTAS', 2.1, 'start', '#777777')
    for n in notas:
        y += 3.8
        L.p_texto('cajetin', x0 + 5, y, n, 2.3, 'start', '#333333')

    # --- escala grafica + norte, al pie del cajetin
    yb = y1 - 30.0
    L.p_linea('cajetin', x0 + 5, yb - 6.0, x1 - 5, yb - 6.0, TINTA, 'auxiliar')
    for i in range(5):
        xa = x0 + 5 + i * ESC * 0.5
        L.p_rect('cajetin', xa, yb, xa + ESC * 0.5, yb + 2.2,
                 TINTA if i % 2 == 0 else '#ffffff', TINTA, 'auxiliar')
    for i, t in enumerate(('0', '', '1', '', '2')):
        if t:
            L.p_texto('cajetin', x0 + 5 + i * ESC * 0.5, yb - 1.2, t, 2.1, 'middle')
    L.p_texto('cajetin', x0 + 5 + 5 * ESC * 0.5 + 2, yb + 2.0, 'm', 2.1, 'start')

    cx, cy = x1 - 13.0, yb + 1.0
    L._add('cajetin', f'<circle cx="{cx}" cy="{cy}" r="7.2" fill="none" '
                      f'stroke="{TINTA}" stroke-width="0.25"/>')
    L._add('cajetin', f'<polygon points="{cx},{cy - 6.4} {cx - 2.6},{cy + 4.4} '
                      f'{cx},{cy + 2.0} {cx + 2.6},{cy + 4.4}" fill="{TINTA}"/>')
    L.p_texto('cajetin', cx, cy - 8.2, 'N', 3.0, 'middle', TINTA, 'bold')

    # --- pie
    yp = y1 - 17.0
    L.p_linea('cajetin', x0, yp, x1, yp, TINTA, 'medio')
    L.p_texto('cajetin', x0 + 5, yp + 5.0, 'ESCALA', 2.1, 'start', '#777777')
    L.p_texto('cajetin', x0 + 5, yp + 10.4, '1:50  (A3)', 3.6, 'start', TINTA, 'bold')
    L.p_texto('cajetin', x0 + 45, yp + 5.0, 'FECHA', 2.1, 'start', '#777777')
    L.p_texto('cajetin', x0 + 45, yp + 10.4, FECHA.split(' de ')[0] + ' set. 2026',
              2.8, 'start', TINTA)
    L.p_texto('cajetin', x1 - 5, yp + 5.0, 'PLANO', 2.1, 'end', '#777777')
    L.p_texto('cajetin', x1 - 5, yp + 10.4, numero, 3.6, 'end', TINTA, 'bold')


def nivel(L, x, y, txt):
    """Simbolo de cota de nivel: triangulo sobre linea."""
    X, Y = L.px(x), L.py(y)
    L._add('rotulos', f'<polygon points="{X},{Y} {X - 1.7},{Y - 2.9} '
                      f'{X + 1.7},{Y - 2.9}" fill="none" stroke="{TINTA}" '
                      f'stroke-width="{TRAZO["medio"]}"/>')
    L._add('rotulos', f'<polygon points="{X},{Y} {X - 1.7},{Y - 2.9} '
                      f'{X},{Y - 2.9}" fill="{TINTA}"/>')
    L.p_texto('rotulos', X + 3.0, Y - 0.4, txt, 2.6, 'start', TINTA, 'bold')


# =============================================================== geometrias
def interior_pb():
    return [(0.250, 9.008), (9.890, 9.008), (9.890, 1.429), (9.710, 1.429),
            (9.710, 0.379), (6.230, 0.379), (6.230, 0.960), (5.980, 0.960),
            (5.980, 1.621), (0.510, 1.621), (0.510, 2.009), (0.250, 2.009)]


def zona_doble_altura():
    return [(0.250, 9.008), (2.461, 9.008), (2.461, 7.509), (2.411, 7.509),
            (2.411, 3.939), (9.890, 3.939), (9.890, 1.429), (9.710, 1.429),
            (9.710, 0.379), (6.230, 0.379), (6.230, 0.960), (5.980, 0.960),
            (5.980, 1.621), (0.510, 1.621), (0.510, 2.009), (0.250, 2.009)]


def muros(L, capa='muros'):
    for nm, x0, y0, x1, y1, _e in E.MUROS:
        L.rect(capa, x0, y0, x1, y1, POCHE, TINTA, 'corte')


def pilares(L, solo=None, capa='pilares', etiquetas=True):
    for tag, nm, x0, y0, x1, y1 in E.PILARES:
        if solo and tag not in solo:
            continue
        L.rect(capa, x0, y0, x1, y1, POCHE_PIL, TINTA, 'corte')
        L.rect(capa, x0, y0, x1, y1, 'url(#horm)', None, 'auxiliar')
        if etiquetas:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            L.texto('rotulos', cx, cy, tag, 3.0, 'middle', '#ffffff', 'bold', dy=1.1)


def ventanal_sur(L):
    v = E.VENTANAL_SUR
    n, mo = v['panos'], v['montante']
    ancho = (v['x1'] - v['x0'] - (n - 1) * mo) / n
    x = v['x0']
    for i in range(n):
        L.rect('carpinteria', x, v['y'] + 0.012, x + ancho, v['y'] + v['e'] - 0.012,
               VIDRIO, '#3d6b80', 'fino')
        if i < n - 1:
            L.rect('carpinteria', x + ancho, v['y'], x + ancho + mo,
                   v['y'] + v['e'], TINTA, TINTA, 'auxiliar')
        x += ancho + mo
    return [v['x0'] + i * (ancho + mo) for i in range(n + 1)]


def escaparate(L):
    s = E.ESCAPARATE
    mx0, mx1 = s['montante_x']
    for a, b in ((s['x0'], mx0), (mx1, s['x1'])):
        L.rect('carpinteria', a, s['y'] + 0.010, b, s['y'] + s['e'] - 0.010,
               VIDRIO, '#3d6b80', 'fino')
    L.rect('carpinteria', mx0, s['y'], mx1, s['y'] + s['e'], TINTA, TINTA, 'auxiliar')


def escalera(L, planta):
    """planta: 'baja' dibuja el tramo con linea de rotura; 'alta' la llegada."""
    x0, x1 = E.ESC_X0, E.ESC_X1
    corte = E.ESC_Y_PIE + 7.5 * E.ESC_HUELLA        # plano de seccion a ~1,30 m

    # peldano de arranque ensanchado
    if planta == 'baja':
        L.rect('escalera', 8.638, E.ESC_Y_PIE, x0, 3.838, 'none', TINTA, 'medio')

    for i in range(E.ESC_N_HUELLAS + 1):
        y = E.ESC_Y_PIE + i * E.ESC_HUELLA
        visible = (y <= corte) if planta == 'baja' else True
        L.linea('escalera', x0, y, x1, y, TINTA if visible else '#9a9a9a',
                'medio' if visible else 'fino',
                '' if visible else ' stroke-dasharray="1.2 1.0"')
    L.linea('escalera', x0, E.ESC_Y_PIE, x0, E.ESC_Y_ALTO, TINTA, 'medio')
    L.linea('escalera', x1, E.ESC_Y_PIE, x1, E.ESC_Y_ALTO, TINTA, 'medio')

    # linea de rotura a 45 grados sobre el plano de corte
    if planta == 'baja':
        for d in (0.0, 0.22):
            L.linea('escalera', x0 - 0.04, corte - 0.30 + d, x1 + 0.04,
                    corte + 0.30 + d, TINTA, 'medio')

    # flecha de sentido
    xm = (x0 + x1) / 2
    ya, yb = (E.ESC_Y_PIE + 0.20, corte - 0.30) if planta == 'baja' \
        else (E.ESC_Y_ALTO - 0.20, corte + 0.30)
    L.linea('escalera', xm, ya, xm, yb, TINTA, 'fino')
    d = -0.16 if planta == 'baja' else 0.16
    L.poly('escalera', [(xm, yb), (xm - 0.09, yb + d), (xm + 0.09, yb + d)],
           TINTA, TINTA, 'auxiliar')
    L.circulo('escalera', xm, ya, 0.055, '#ffffff', TINTA, 'fino')
    L.texto('rotulos', xm, (ya + yb) / 2, 'SUBE' if planta == 'baja' else 'BAJA',
            2.1, 'middle', TINTA, 'bold', rot=-90, dx=-3.4)


def luces(L, empotrados=True):
    if empotrados:
        for x, y in E.EMPOTRADOS:
            L.circulo('luces', x, y, 0.085, 'none', '#7d7d7d', 'fino')
            L.linea('luces', x - 0.06, y, x + 0.06, y, '#7d7d7d', 'auxiliar')
            L.linea('luces', x, y - 0.06, x, y + 0.06, '#7d7d7d', 'auxiliar')
    for x, y in E.COLGANTES:
        L.circulo('luces', x, y, 0.10, 'none', '#7d7d7d', 'fino')
        L.circulo('luces', x, y, 0.028, '#7d7d7d', '#7d7d7d', 'auxiliar')


# ============================================================== PLANTA BAJA
def planta_baja():
    L = Lienzo(W, H, ESC, OX, OY)
    for c in ('hoja', 'trama', 'proyeccion', 'muros', 'pilares', 'carpinteria',
              'escalera', 'luces', 'cotas', 'rotulos', 'cajetin'):
        L.capa(c)

    # zona de doble altura
    L.poly('trama', zona_doble_altura(), 'url(#doble)', None)

    # proyeccion del forjado superior y de la viga descolgada
    L.poly('proyeccion', E.FORJADO, 'none', '#8a8a8a', 'fino',
           ' stroke-dasharray="3.2 1.6"')
    nm, vx0, vy0, vx1, vy1 = E.VIGA
    L.rect('proyeccion', vx0, vy0, vx1, vy1, 'none', '#8a8a8a', 'fino',
           ' stroke-dasharray="3.2 1.6"')
    L.texto('rotulos', (vx0 + vx1) / 2, vy1, 'VIGA DESCOLGADA  intradós +2,60',
            2.0, 'middle', '#5f5f5f', dy=-1.4)

    muros(L)
    pilares(L)
    ventanal_sur(L)
    escaparate(L)
    escalera(L, 'baja')
    luces(L)

    # contorno interior, para reforzar el recinto
    L.poly('muros', interior_pb(), 'none', TINTA, 'fino')

    # ---- rotulos
    L.texto('rotulos', 4.8, 6.6, 'ZONA CON FORJADO SUPERIOR', 2.6, 'middle',
            '#4a4a4a', 'bold')
    L.texto('rotulos', 4.8, 6.6, 'altura libre 2,70 m', 2.3, 'middle', '#4a4a4a',
            dy=3.4)
    L.texto('rotulos', 4.3, 2.65, 'DOBLE ALTURA · 5,50 m', 2.6, 'middle', '#3c5a68',
            'bold')
    L.texto('rotulos', 7.95, 1.22, 'VESTÍBULO DE ACCESO', 2.3, 'middle', '#3c5a68',
            'bold')
    L.texto('rotulos', 1.33, 6.90, 'DOBLE ALTURA', 2.3, 'middle', '#3c5a68', 'bold',
            rot=-90)
    nivel(L, 7.95, 0.72, '±0,00')

    L.texto('rotulos', 5.02, 9.082, 'MEDIANERA NORTE  e=0,148', 2.0, 'middle', '#ffffff')
    L.texto('rotulos', 0.125, 5.9, 'MURO OESTE  e=0,25', 2.0, 'middle', '#ffffff',
            rot=-90)
    L.texto('rotulos', 9.965, 5.9, 'MEDIANERA ESTE  e=0,15', 2.0, 'middle', '#ffffff',
            rot=-90)
    L.texto('rotulos', 3.25, 1.561, 'VENTANAL SUR  ·  acristalamiento de doble altura',
            2.1, 'middle', '#26485a', dy=4.6)
    L.texto('rotulos', 7.97, 0.330, 'ESCAPARATE  ·  doble altura', 2.1,
            'middle', '#26485a', dy=4.6)
    L.texto('rotulos', 9.35, 7.30,
            f'ESCALERA  {E.ESC_N_HUELLAS} huellas × 0,26', 1.95, 'middle', TINTA,
            rot=-90)
    L.texto('rotulos', 9.35, 7.30, f'{E.ESC_N_TABICAS} tabicas × 0,176', 1.95,
            'middle', TINTA, rot=-90, dx=3.0)

    # ---- cotas
    ys = L.py(0.0) + 10.0
    L.cota_h('cotas', [0.0, 0.510, 5.731, 5.980, 6.230, 9.710, 10.040], ys,
             ext_desde=0.0)
    L.cota_h('cotas', [0.0, 10.040], ys + 8.0, 2.4)

    yn = L.py(9.156) - 8.0
    L.cota_h('cotas', [0.0, 0.250, 2.411, 2.461, 5.620, 6.219, 8.811, 9.890, 10.040],
             yn, 1.9, ext_desde=9.156)

    xw = L.px(0.0) - 9.0
    L.cota_v('cotas', [0.0, 1.561, 2.009, 4.759, 5.357, 9.008, 9.156], xw,
             ext_desde=0.0)
    L.cota_v('cotas', [0.0, 9.156], xw - 8.0)

    xe = L.px(10.040) + 9.0
    L.cota_v('cotas', [0.330, 1.429, 3.579, 3.939, 4.708, 5.309, 7.738, 9.156], xe,
             1.9, ext_desde=10.040)

    # cotas interiores utiles
    L.cota_h('cotas', [0.250, 1.300, 1.901, 5.980], L.py(2.30), 1.9)
    L.cota_v('cotas', [1.621, 3.939], L.px(3.30), 1.9)

    marco(L, 'PLANTA BAJA', '01 / 02', 'Estado actual · estructura',
          ['Cotas en metros, tomadas sobre el levantamiento.',
           'Plano de estructura: no se representa mobiliario',
           'ni equipamiento. Cota de referencia ±0,00 en el',
           'pavimento de planta baja.',
           'Sección horizontal a 1,20 m sobre el pavimento.',
           'Los puntos de luz proceden del proyecto de reforma,',
           'no están replanteados en obra.'],
          [(POCHE, TINTA, 'Muro de carga / medianera'),
           (POCHE_PIL, TINTA, 'Pilar o machón de hormigón'),
           (VIDRIO, '#3d6b80', 'Carpintería acristalada'),
           ('url(#doble)', '#c3ced6', 'Espacio de doble altura'),
           ('linea', '#8a8a8a', 'Forjado y viga sobre el corte'),
           ('punto', '#7d7d7d', 'Punto de luz s/ proyecto')],
          ('SUPERFICIES Y ALTURAS',
           [('Planta baja, dentro de muros', f'{E.SUP_PB_UTIL:.2f} m²'.replace('.', ',')),
            ('Zona de doble altura', f'{E.SUP_DOBLE_ALT:.2f} m²'.replace('.', ',')),
            ('Altura libre bajo forjado', '2,70 m'),
            ('Altura en doble altura', '5,50 m'),
            ('Acristalamiento de fachada', '≈ 4,70 m')]))
    return L


# ============================================================== PLANTA ALTA
def planta_alta():
    L = Lienzo(W, H, ESC, OX, OY)
    for c in ('hoja', 'trama', 'proyeccion', 'muros', 'pilares', 'tabiques',
              'carpinteria', 'escalera', 'luces', 'cotas', 'rotulos', 'cajetin'):
        L.capa(c)

    # vacio sobre planta baja
    L.poly('trama', zona_doble_altura(), 'url(#vacio)', None)

    # contorno del local en planta alta (muros que siguen subiendo)
    for nm, x0, y0, x1, y1, _e in E.MUROS:
        L.rect('muros', x0, y0, x1, y1, POCHE, TINTA, 'corte')

    # borde del forjado
    L.poly('proyeccion', E.FORJADO, 'none', TINTA, 'medio')

    # barandillas de vidrio
    for nm, x0, y0, x1, y1 in E.BARANDILLAS:
        L.rect('carpinteria', x0, y0, x1, y1, VIDRIO, '#3d6b80', 'medio')

    # tabiqueria
    for nm, x0, y0, x1, y1 in E.TABIQUES_PA:
        L.rect('tabiques', x0, y0, x1, y1, POCHE_TAB, TINTA, 'tabique')

    # huecos de paso con barrido de hoja
    for nm, x0, y0, x1, y1, ancho, eje in E.HUECOS_PA:
        L.rect('tabiques', x0, y0, x1, y1, '#ffffff', 'none', 'auxiliar')
        if eje == 'x':
            xa, ym = x0, (y0 + y1) / 2
            L.rect('tabiques', xa, ym - 0.02, xa + ancho, ym + 0.02, TINTA, None)
            L.linea('tabiques', xa, ym, xa, ym + ancho, TINTA, 'fino')
            L._add('tabiques', f'<path d="M {L.px(xa + ancho):.3f} {L.py(ym):.3f} '
                               f'A {L.mm(ancho):.3f} {L.mm(ancho):.3f} 0 0 0 '
                               f'{L.px(xa):.3f} {L.py(ym + ancho):.3f}" fill="none" '
                               f'stroke="{TINTA}" stroke-width="{TRAZO["auxiliar"]}" '
                               f'stroke-dasharray="1.2 0.9"/>')
        else:
            xm, ya = (x0 + x1) / 2, y0
            L.rect('tabiques', xm - 0.02, ya, xm + 0.02, ya + ancho, TINTA, None)
            L.linea('tabiques', xm, ya, xm - ancho, ya, TINTA, 'fino')
            L._add('tabiques', f'<path d="M {L.px(xm):.3f} {L.py(ya + ancho):.3f} '
                               f'A {L.mm(ancho):.3f} {L.mm(ancho):.3f} 0 0 0 '
                               f'{L.px(xm - ancho):.3f} {L.py(ya):.3f}" fill="none" '
                               f'stroke="{TINTA}" stroke-width="{TRAZO["auxiliar"]}" '
                               f'stroke-dasharray="1.2 0.9"/>')

    pilares(L, solo=E.PILARES_PA)
    escalera(L, 'alta')

    # ---- rotulos
    nivel(L, 4.30, 5.10, '+3,00')
    L.texto('rotulos', 5.9, 6.30, 'ALTILLO · PLANTA ALTA', 3.0, 'middle', '#4a4a4a',
            'bold')
    L.texto('rotulos', 5.9, 6.30, 'altura libre 2,50 m   ·   nivel +3,00', 2.4,
            'middle', '#4a4a4a', dy=3.8)
    L.texto('rotulos', 5.6, 2.55, 'VACÍO SOBRE PLANTA BAJA', 2.8, 'middle', '#3c5a68',
            'bold')
    L.texto('rotulos', 5.6, 2.55, 'doble altura · 5,50 m', 2.3, 'middle', '#3c5a68',
            dy=3.6)
    L.texto('rotulos', 1.33, 5.6, 'VACÍO', 2.3, 'middle', '#3c5a68', 'bold', rot=-90)
    L.texto('rotulos', 3.60, 8.30, 'ASEO', 2.4, 'middle', '#4a4a4a', 'bold')
    L.texto('rotulos', 5.00, 8.62, 'INODORO', 2.1, 'middle', '#4a4a4a', 'bold')
    L.texto('rotulos', 6.48, 8.30, 'ALMACÉN', 2.4, 'middle', '#4a4a4a', 'bold')
    L.texto('rotulos', 8.60, 8.45, 'PASO', 2.2, 'middle', '#4a4a4a', 'bold')
    L.texto('rotulos', 5.6, 4.20, 'BARANDILLA DE VIDRIO  h=1,00', 2.1, 'middle',
            '#26485a')
    L.texto('rotulos', 2.65, 5.7, 'BARANDILLA DE VIDRIO', 2.0, 'middle', '#26485a',
            rot=-90, dx=2.6)
    L.texto('rotulos', 9.35, 5.95, 'ESCALERA · llegada +3,00', 2.0, 'middle', TINTA,
            rot=-90, dx=3.4)
    # ---- cotas
    yn = L.py(9.156) - 8.0
    L.cota_h('cotas', [0.0, 0.250, 2.461, 2.560, 3.089, 3.849, 4.461, 4.560,
                       5.459, 5.558, 7.408, 7.511, 9.890, 10.040], yn, 1.75,
             ext_desde=9.156)
    L.cota_h('cotas', [0.0, 10.040], yn - 8.0, 2.4)

    ys = L.py(0.0) + 10.0
    L.cota_h('cotas', [0.0, 2.411, 5.620, 6.219, 8.759, 8.811, 10.040], ys,
             ext_desde=0.0)

    xw = L.px(0.0) - 9.0
    L.cota_v('cotas', [1.561, 3.939, 7.509, 7.607, 9.008, 9.156], xw, ext_desde=1.561)
    L.cota_v('cotas', [0.0, 9.156], xw - 8.0)

    xe = L.px(10.040) + 9.0
    L.cota_v('cotas', [3.939, 4.708, 5.309, 7.738, 8.072, 8.208, 9.156], xe, 1.9,
             ext_desde=10.040)

    L.cota_v('cotas', [7.509, 9.008], L.px(2.72), 1.9)

    marco(L, 'PLANTA ALTA', '02 / 02', 'Altillo +3,00 · estructura',
          ['Cotas en metros, tomadas sobre el levantamiento.',
           'Plano de estructura: no se representa mobiliario',
           'ni equipamiento.',
           'El forjado del altillo no cubre todo el local: la',
           'franja sur y oeste es un vacío a doble altura.',
           'Sección horizontal a 1,20 m sobre el forjado.'],
          [(POCHE, TINTA, 'Muro de carga / medianera'),
           (POCHE_PIL, TINTA, 'Pilar o machón de hormigón'),
           (POCHE_TAB, TINTA, 'Tabiquería'),
           (VIDRIO, '#3d6b80', 'Barandilla de vidrio'),
           ('url(#vacio)', '#b9c6cf', 'Vacío sobre planta baja')],
          ('SUPERFICIES Y ALTURAS',
           [('Forjado de planta alta', f'{E.SUP_FORJADO:.2f} m²'.replace('.', ',')),
            ('Altillo diáfano', '26,17 m²'),
            ('Aseo (lavabo + inodoro)', '3,92 m²'),
            ('Almacén', '2,59 m²'),
            ('Altura libre de planta alta', '2,50 m')]))
    return L


# ==================================================================== salida
def exportar(L, nombre):
    svg = os.path.join(AQUI, nombre + '.svg')
    pdf = os.path.join(AQUI, nombre + '.pdf')
    png = os.path.join(AQUI, nombre + '.png')
    open(svg, 'w', encoding='utf-8').write(L.svg(DEFS))
    import cairosvg
    cairosvg.svg2pdf(url=svg, write_to=pdf)
    cairosvg.svg2png(url=svg, write_to=png, dpi=200, output_width=int(W / 25.4 * 200))
    print(f'  {nombre}.pdf  ·  {nombre}.png')
    return pdf


if __name__ == '__main__':
    print('Generando planos 1:50 en A3...')
    pb = exportar(planta_baja(), 'PLANTA_BAJA')
    pa = exportar(planta_alta(), 'PLANTA_ALTA')
    import fitz
    doc = fitz.open()
    for f in (pb, pa):
        doc.insert_pdf(fitz.open(f))
    salida = os.path.join(AQUI, 'Planos_Estructura.pdf')
    doc.save(salida)
    print(f'  Planos_Estructura.pdf  ({doc.page_count} páginas)')
