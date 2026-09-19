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
import mobiliario as MB
import equipamiento as Q
from dibujo import (Lienzo, TRAZO, TINTA, POCHE, POCHE_PIL, POCHE_TAB,
                    VIDRIO, COTA_COL)
P3 = next(p for p in E.PILARES if p[0] == 'P3')   # (rotulo, nombre, x0, y0, x1, y1)
RESERVA = '#7a6a4a'   # reservas de espacio marcadas por el cliente
ACC = '#2a7f8f'       # itinerario accesible
MOB = '#8a6f4e'       # mobiliario de sala
APAR = '#4a5a68'      # aparatos (mismo color que la lamina 03)

AQUI = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- formato A3
W, H = 420.0, 297.0
ESC = 20.0                      # mm por metro  ->  1:50
MARGEN = 8.0
CAJ_X = W - MARGEN - 96.0       # borde izquierdo del cajetin
OX, OY = 62.0, 236.0            # papel del origen de obra

FECHA = '19 de septiembre de 2026'

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
def marco(L, titulo, numero, subtitulo, notas, leyenda, cuadro=None,
          tabla=None, esc_dibujo=None, esc_txt='1:50  (A3)', escala=True):
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

    # --- leyenda (solo si hay entradas)
    if leyenda:
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
            elif relleno == 'cota':
                L.p_linea('cajetin', x0 + 5, y - 1.2, x0 + 13, y - 1.2, trazo, 'cota')
                for xx in (x0 + 5, x0 + 13):
                    L.p_linea('cajetin', xx - 1.1, y + 0.1, xx + 1.1, y - 2.5, trazo, 'cota')
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

    # --- cuadro de pilares, o la tabla que se pase en su lugar
    if tabla is None:
        tabla = ('PILARES Y MACHONES  (secciones en m)',
                 [(f'{t}  {n}', f'{c - a:.2f} × {d - b:.2f}'.replace('.', ','))
                  for t, n, a, b, c, d in E.PILARES])
    y += 4.6
    L.p_texto('cajetin', x0 + 5, y, tabla[0], 2.1, 'start', '#777777')
    for etq, val in tabla[1]:
        y += 4.0
        L.p_texto('cajetin', x0 + 5, y, etq, 2.2, 'start', '#333333')
        L.p_texto('cajetin', x1 - 5, y, val, 2.2, 'end', TINTA, 'bold')
    y += 3.4
    L.p_linea('cajetin', x0 + 5, y, x1 - 5, y, TINTA, 'auxiliar')

    # --- notas
    y += 4.6
    L.p_texto('cajetin', x0 + 5, y, 'NOTAS', 2.1, 'start', '#777777')
    for n in notas:
        y += 3.8
        L.p_texto('cajetin', x0 + 5, y, n, 2.3, 'start', '#333333')

    # --- escala grafica + norte, al pie del cajetin (no en las laminas de texto)
    yb = y1 - 30.0
    ed = ESC if esc_dibujo is None else esc_dibujo
    if not escala:
        _pie(L, x0, x1, y1, esc_txt, numero)
        return
    # el paso se ajusta para que la barra grafica quepa siempre en el cajetin
    paso = 0.5 if ed * 2.5 <= 60 else 0.25
    rot = ('0', '', '1', '', '2') if paso == 0.5 else ('0', '', '0,5', '', '1')
    L.p_linea('cajetin', x0 + 5, yb - 6.0, x1 - 5, yb - 6.0, TINTA, 'auxiliar')
    for i in range(5):
        xa = x0 + 5 + i * ed * paso
        L.p_rect('cajetin', xa, yb, xa + ed * paso, yb + 2.2,
                 TINTA if i % 2 == 0 else '#ffffff', TINTA, 'auxiliar')
    for i, t in enumerate(rot):
        if t:
            L.p_texto('cajetin', x0 + 5 + i * ed * paso, yb - 1.2, t, 2.1, 'middle')
    L.p_texto('cajetin', x0 + 5 + 5 * ed * paso + 2, yb + 2.0, 'm', 2.1, 'start')

    cx, cy = x1 - 13.0, yb + 1.0
    L._add('cajetin', f'<circle cx="{cx}" cy="{cy}" r="7.2" fill="none" '
                      f'stroke="{TINTA}" stroke-width="0.25"/>')
    L._add('cajetin', f'<polygon points="{cx},{cy - 6.4} {cx - 2.6},{cy + 4.4} '
                      f'{cx},{cy + 2.0} {cx + 2.6},{cy + 4.4}" fill="{TINTA}"/>')
    L.p_texto('cajetin', cx, cy - 8.2, 'N', 3.0, 'middle', TINTA, 'bold')

    _pie(L, x0, x1, y1, esc_txt, numero)


def _pie(L, x0, x1, y1, esc_txt, numero):
    yp = y1 - 17.0
    L.p_linea('cajetin', x0, yp, x1, yp, TINTA, 'medio')
    L.p_texto('cajetin', x0 + 5, yp + 5.0, 'ESCALA', 2.1, 'start', '#777777')
    L.p_texto('cajetin', x0 + 5, yp + 10.4, esc_txt, 3.6, 'start', TINTA, 'bold')
    L.p_texto('cajetin', x0 + 45, yp + 5.0, 'FECHA', 2.1, 'start', '#777777')
    L.p_texto('cajetin', x0 + 45, yp + 10.4, FECHA.split(' de ')[0] + ' set. 2026',
              2.8, 'start', TINTA)
    L.p_texto('cajetin', x1 - 5, yp + 5.0, 'PLANO', 2.1, 'end', '#777777')
    L.p_texto('cajetin', x1 - 5, yp + 10.4, numero, 3.6, 'end', TINTA, 'bold')


def comprobar(L, y0=256.0, y1=287.0, x0=11.0, x1=W - 8.0 - 96.0 - 2.0):
    """Banda de comprobaciones en obra, al pie de la lamina."""
    import textwrap
    L.p_rect('cajetin', x0, y0, x1, y1, '#fbf6ee', '#9a2b2b', 'fino')
    L.p_texto('cajetin', x0 + 3.5, y0 + 4.6, 'COMPROBAR EN OBRA', 2.6, 'start',
              '#9a2b2b', 'bold', espaciado='0.6')
    L.p_texto('cajetin', x0 + 46, y0 + 4.6,
              'Puntos en los que los vídeos del local no cuadran con el '
              'levantamiento, o que el levantamiento no recoge. Se dibuja el '
              'levantamiento por ser la única fuente acotada.',
              2.0, 'start', '#7a5a3a')
    L.p_linea('cajetin', x0 + 3.5, y0 + 6.4, x1 - 3.5, y0 + 6.4, '#d8c6ae', 'cota')

    ncol, porcol = 3, 3
    ancho = (x1 - x0 - 7.0) / ncol
    for i, txt in enumerate(E.COMPROBAR):
        col, fila = divmod(i, porcol)
        cx = x0 + 3.5 + col * ancho
        cy = y0 + 10.4 + fila * 7.0
        L.p_texto('cajetin', cx, cy, f'{i + 1}', 2.2, 'start', '#9a2b2b', 'bold')
        for j, linea in enumerate(textwrap.wrap(txt, 84)[:2]):
            L.p_texto('cajetin', cx + 4.2, cy + j * 2.8, linea, 2.0, 'start',
                      '#3a3a3a')


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
_H = E.HUNDIMIENTO


def interior_pb(hund=True):
    if not hund:                      # planta alta: sin el trasdosado de PB
        return [(0.250, E.MURO_N), (9.890, E.MURO_N)] + interior_pb()[4:]
    return [(0.250, _H['y1']), (_H['x1'], _H['y1']), (_H['x1'], _H['y0']),
            (9.890, _H['y0']), (9.890, 1.429), (9.710, 1.429),
            (9.710, 0.379), (6.230, 0.379), (6.230, 0.960), (5.980, 0.960),
            (5.980, 1.621), (0.510, 1.621), (0.510, 2.009), (0.250, 2.009)]


def zona_doble_altura():
    return [(0.250, _H['y1']), (_H['x1'], _H['y1']), (_H['x1'], _H['y0']),
            (2.461, _H['y0']), (2.461, 7.509), (2.411, 7.509),
            (2.411, 3.939), (9.890, 3.939), (9.890, 1.429), (9.710, 1.429),
            (9.710, 0.379), (6.230, 0.379), (6.230, 0.960), (5.980, 0.960),
            (5.980, 1.621), (0.510, 1.621), (0.510, 2.009), (0.250, 2.009)]


# El tramo sur esta ocupado en toda su longitud por el ventanal: el plano de
# seccion lo corta por el vidrio, asi que no se macizan.
SIN_POCHE = ('Muro Sur (con ventanal)',)
# En planta baja este tramo se sustituye por el hundimiento medido.
SOLO_PA = ()   # la medianera del hundimiento ya se dibuja en las dos plantas


def muros(L, capa='muros', planta='baja'):
    for nm, x0, y0, x1, y1, _e in E.MUROS:
        if nm in SIN_POCHE or (planta == 'baja' and nm in SOLO_PA):
            continue
        L.rect(capa, x0, y0, x1, y1, POCHE, TINTA, 'corte')


def hundimiento(L, rotulo=(1.34, 8.28)):
    """Hundimiento del muro Norte en la cocina (19 set., noche).

    No es un hueco abierto en la medianera: el fondo del hundimiento ES la
    escalon de la cara interior del muro Norte: 9,008 en los 2,18 de la
    cocina y 8,957 en el resto. El muro es macizo hasta el borde del solar
    (9,156), asi que lo que cambia es su espesor: 0,148 en la cocina (el del
    levantamiento) y 0,199 en el resto. De la pared hundida a la cara Norte
    de P1 hay 3,651, los 3,65 que midio el cliente en el muro Oeste.
    """
    h = E.HUNDIMIENTO
    # el escalon lo dibujan ya los dos tramos de muro; aqui solo el rotulo
    if rotulo:
        L.texto('rotulos', rotulo[0], rotulo[1],
                f"HUNDIMIENTO  {h['p']:.2f}".replace('.', ',')
                + '  ·  muro más fino',
                2.0, 'middle', '#9a2b2b', 'bold')


def pilares(L, solo=None, capa='pilares', etiquetas=True):
    for tag, nm, x0, y0, x1, y1 in E.PILARES:
        if solo and tag not in solo:
            continue
        L.rect(capa, x0, y0, x1, y1, POCHE_PIL, TINTA, 'corte')
        L.rect(capa, x0, y0, x1, y1, 'url(#horm)', None, 'auxiliar')
        if etiquetas:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            L.texto('rotulos', cx, cy, tag, 3.0 if len(tag) < 3 else 2.4,
                    'middle', '#ffffff', 'bold', dy=1.1)


def ventanal_sur(L):
    v = E.VENTANAL_SUR
    for a, b in v['panos']:
        L.rect('carpinteria', a, v['y'] + 0.012, b, v['y'] + v['e'] - 0.012,
               VIDRIO, '#3d6b80', 'fino')
    ja, jb = v['jamba']
    L.rect('carpinteria', ja, v['y'], jb, v['y'] + 0.249, POCHE, TINTA, 'tabique')


def zocalo_sur(L):
    """Zocalo de piedra del ventanal: 0,347 de fondo (2,72 desde P3)."""
    z = E.ZOCALO_SUR
    p2 = next(p for p in E.PILARES if p[0] == 'P2')
    for a, b in ((z['x0'], p2[2]), (p2[4], z['x1'])):
        L.rect('carpinteria', a, z['y0'], b, z['y1'], '#eceff1', '#3d6b80', 'fino')
    L.texto('rotulos', 3.75, (z['y0'] + z['y1']) / 2,
            'ZÓCALO DEL VENTANAL  ·  0,35', 1.8, 'middle', '#26485a', dy=0.6)


def escaparate(L, con_puerta=True):
    """La puerta solo se dibuja en planta baja: mide 2,10 y el plano de
    seccion de planta alta pasa muy por encima de su dintel."""
    s, p = E.ESCAPARATE, E.PUERTA_ACCESO
    if con_puerta:
        L.rect('carpinteria', s['x0'], s['y'] + 0.010, p['x0'],
               s['y'] + s['e'] - 0.010, VIDRIO, '#3d6b80', 'fino')
        L.rect('carpinteria', p['x0'] - 0.025, s['y'], p['x0'] + 0.025,
               s['y'] + s['e'], TINTA, TINTA, 'auxiliar')
        puerta_acceso(L)
    else:
        L.rect('carpinteria', s['x0'], s['y'] + 0.010, s['x1'],
               s['y'] + s['e'] - 0.010, VIDRIO, '#3d6b80', 'fino')


def puerta_acceso(L):
    """Doble hoja de 2,10 en total, barriendo 1,00 hacia el vestibulo."""
    p = E.PUERTA_ACCESO
    y, br = p['y'], p['barrido']
    media = (p['x1'] - p['x0']) / 2
    for lado, xg in ((+1, p['x0']), (-1, p['x1'])):
        # hoja abatida contra la jamba
        L.rect('carpinteria', xg - 0.02 * lado, y, xg + 0.02 * lado, y + br,
               TINTA, None)
        L.linea('carpinteria', xg, y, xg + lado * media, y, TINTA, 'fino')
        L._add('carpinteria',
               f'<path d="M {L.px(xg + lado * media):.3f} {L.py(y):.3f} '
               f'A {L.mm(br):.3f} {L.mm(br):.3f} 0 0 {0 if lado > 0 else 1} '
               f'{L.px(xg):.3f} {L.py(y + br):.3f}" fill="none" '
               f'stroke="{TINTA}" stroke-width="{TRAZO["auxiliar"]}" '
               f'stroke-dasharray="1.2 0.9"/>')


def pared_l(L, capa='muros'):
    """Pared en L nueva que sostiene el panel de vidrio de 1,35."""
    for nm, x0, y0, x1, y1 in (E.PARED_L_LAR, E.PARED_L_DOB):
        L.rect(capa, x0, y0, x1, y1, POCHE_TAB, TINTA, 'tabique')


def reservas(L):
    """Reservas de espacio marcadas por el cliente. No son estructura."""
    d = ' stroke-dasharray="2.6 1.4"'
    b = E.BARRA
    L.rect('reservas', b['x0'], b['y0'], b['x1'], b['y1'],
           'none', RESERVA, 'medio', d)
    L.texto('rotulos', (b['x0'] + b['x1']) / 2, (b['y0'] + b['y1']) / 2,
            'BARRA  ·  ' + f"{b['largo']:.2f}".replace('.', ','),
            2.1, 'middle', RESERVA, 'bold', rot=-90)

    p = E.PASO_PERS
    L.linea('reservas', p['x0'], p['y0'], p['x1'], p['y0'], RESERVA, 'fino', d)
    L.linea('reservas', p['x0'], p['y1'], p['x1'], p['y1'], RESERVA, 'fino', d)
    L.texto('rotulos', (p['x0'] + p['x1']) / 2, p['y1'] - 0.085,
            f"PASO {p['medido']:.2f}".replace('.', ','), 1.8, 'middle', RESERVA,
            'bold')

    s = E.SILLON
    L.rect('reservas', s['x0'], s['y'] - s['fondo'], s['x1'], s['y'],
           'none', RESERVA, 'medio', d)
    L.texto('rotulos', s['x0'] + 1.60, s['y'] - s['fondo'] / 2,
            f"SILLÓN CORRIDO  ·  {s['largo']:.2f}".replace('.', ',')
            + '  ·  fondo por medir', 2.0, 'middle', RESERVA, 'bold', dy=0.8)


def viga(L):
    """Viga P1b, de P1 a la pared en L. Sobre el plano de seccion."""
    nm, x0, y0, x1, y1 = E.VIGA
    L.rect('proyeccion', x0, y0, x1, y1, 'none', '#6a6a6a', 'fino',
           ' stroke-dasharray="2.4 1.4"')
    L.texto('rotulos', 1.70, (y0 + y1) / 2, 'VIGA P1b  1,83 × 0,25',
            1.9, 'middle', '#5f5f5f', dy=0.7)


def bano(L):
    """Bano nuevo de planta baja, con su puerta y los aparatos en reserva."""
    for nm, x0, y0, x1, y1 in E.BANO_TABIQUES:
        L.rect('tabiques', x0, y0, x1, y1, POCHE_TAB, TINTA, 'tabique')
    p = E.BANO_PUERTA
    xh, ya, an = p['x1'], p['y'], p['ancho']
    L.rect('tabiques', p['x0'], ya, p['x1'], ya + 0.10, '#ffffff', 'none', 'auxiliar')
    L.rect('tabiques', xh - 0.02, ya, xh + 0.02, ya + an, TINTA, None)
    L.linea('tabiques', xh, ya, xh - an, ya, TINTA, 'fino')
    L._add('tabiques', f'<path d="M {L.px(xh - an):.3f} {L.py(ya):.3f} '
                       f'A {L.mm(an):.3f} {L.mm(an):.3f} 0 0 0 '
                       f'{L.px(xh):.3f} {L.py(ya + an):.3f}" fill="none" '
                       f'stroke="{TINTA}" stroke-width="{TRAZO["auxiliar"]}" '
                       f'stroke-dasharray="1.2 0.9"/>')
    b = E.BANO
    d = ' stroke-dasharray="1.6 1.0"'
    # inodoro contra la medianera Este y lavabo en el tabique Oeste
    L.rect('reservas', b['x1'] - 0.70, b['y1'] - 0.75, b['x1'] - 0.05, b['y1'] - 0.35,
           'none', RESERVA, 'fino', d)
    L.circulo('reservas', b['x1'] - 0.42, b['y1'] - 0.62, 0.17, 'none', RESERVA, 'fino', d)
    L.rect('reservas', b['x0'] + 0.10, b['y1'] - 0.55, b['x0'] + 0.55, b['y1'] - 0.15,
           'none', RESERVA, 'fino', d)
    L.texto('rotulos', 8.55, 8.72, 'BAÑO', 2.4, 'middle', '#4a4a4a', 'bold')


def mobiliario(L, mesas):
    """Mesas y sillas con medidas promedio, en su propia capa."""
    for m in mesas:
        tag, tipo, x0, y0, x1, y1, lados = m
        if tipo == 'redonda':
            L.circulo('mobiliario', (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2,
                      '#f4efe6', MOB, 'medio')
        else:
            L.rect('mobiliario', x0, y0, x1, y1, '#f4efe6', MOB, 'medio')
        for sx0, sy0, sx1, sy1 in MB.sillas(m):
            L.rect('mobiliario', sx0, sy0, sx1, sy1, 'none', MOB, 'fino',
                   ' rx="0.6"')
        L.texto('rotulos', (x0 + x1) / 2, (y0 + y1) / 2, tag, 2.0, 'middle', MOB,
                'bold', dy=0.7)


def nevera_bebidas(L):
    """Nevera expositora de bebidas A7, contra la cara Sur de P3 (19 set.).

    Sale 0,58 del pilar hacia el ventanal y deja 0,92 hasta el canto Norte
    de M2: es el punto mas estrecho del recorrido de la sala.
    """
    n, q = Q.NEVERA_BEBIDAS, Q.NEVERA_BEBIDAS_POS
    L.rect('mobiliario', q['x0'], q['y0'], q['x1'], q['y1'], '#eaeff2', APAR, 'medio')
    # puerta de cristal, al Sur: doble linea fina
    for d in (0.045, 0.075):
        L.linea('mobiliario', q['x0'] + 0.03, q['y0'] + d, q['x1'] - 0.03,
                q['y0'] + d, '#3d6b80', 'fino')
    # rotulo corto dentro del aparato, como las mesas; el nombre completo
    # va en la leyenda y en las laminas 03 y 04
    L.texto('rotulos', (q['x0'] + q['x1']) / 2, (q['y0'] + q['y1']) / 2,
            n['tag'], 2.0, 'middle', APAR, 'bold', dy=0.7)


def accesibilidad(L):
    """Itinerario accesible de 1,20, giros de 1,50, plaza PMR y anchos libres."""
    d = ' stroke-dasharray="3.0 1.2 0.6 1.2"'
    for tramo in MB.ACC_ITINERARIO:
        for (xa, ya), (xb, yb) in zip(tramo, tramo[1:]):
            L.linea('reservas', xa, ya, xb, yb, ACC, 'medio', d)
    for (x, y), (tx, ty) in MB.ACC_GIROS:
        L.circulo('reservas', x, y, 0.75, 'none', ACC, 'fino', ' stroke-dasharray="1.6 1.1"')
        L.texto('rotulos', tx, ty, 'Ø 1,50', 1.8, 'middle', ACC, 'bold', dy=0.6)
    if MB.ACC_PMR:
        x0, y0, x1, y1 = MB.ACC_PMR
        L.rect('reservas', x0, y0, x1, y1, 'none', ACC, 'fino',
               ' stroke-dasharray="1.6 1.1"')
        L.texto('rotulos', (x0 + x1) / 2, (y0 + y1) / 2, 'PMR', 1.8, 'middle', ACC,
                'bold', dy=0.6)
    cotas_paso(L, MB.ACC_ANCHOS)


def cotas_paso(L, lista, color=ACC):
    """Anchos libres entre mobiliario: cota sencilla con el texto donde no
    tape nada (tipo, posicion de la linea, extremos, sitio del texto)."""
    ACCc = color
    for tipo, pos, a, b, tx, ty in lista:
        if tipo == 'v':
            X = L.px(pos)
            L.p_linea('cotas', X, L.py(a), X, L.py(b), ACCc, 'cota')
            for y in (a, b):
                L.p_linea('cotas', X - 1.1, L.py(y) + 1.1, X + 1.1, L.py(y) - 1.1, ACCc, 'cota')
        else:
            Y = L.py(pos)
            L.p_linea('cotas', L.px(a), Y, L.px(b), Y, ACCc, 'cota')
            for x in (a, b):
                L.p_linea('cotas', L.px(x) - 1.1, Y + 1.1, L.px(x) + 1.1, Y - 1.1, ACCc, 'cota')
        L.texto('rotulos', tx, ty, L._fmt(b - a), 1.8, 'middle', ACCc, 'bold',
                rot=-90 if tipo == 'v' else 0, dy=0.6)


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


def aire(L):
    """Cassettes de aire acondicionado del techo (fotos del cliente)."""
    dd = ' stroke-dasharray="2.0 1.3"'
    rw, rh = E.AIRE_REJILLA
    for tag, nm, cx, cy, a, f in E.AIRE:
        L.rect('luces', cx - a / 2, cy - f / 2, cx + a / 2, cy + f / 2,
               'none', '#6f8a99', 'medio', dd)
        L.linea('luces', cx - a / 2, cy - f / 2, cx + a / 2, cy + f / 2,
                '#6f8a99', 'auxiliar', dd)
        L.linea('luces', cx - a / 2, cy + f / 2, cx + a / 2, cy - f / 2,
                '#6f8a99', 'auxiliar', dd)
        L.rect('luces', cx - rw / 2, cy + f / 2 + 0.06, cx + rw / 2,
               cy + f / 2 + 0.06 + rh, 'none', '#6f8a99', 'fino', dd)
        L.texto('rotulos', cx, cy + f / 2 + rh + 0.10, tag, 1.9, 'middle',
                '#4c6b7c', 'bold')


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
    for c in ('hoja', 'trama', 'proyeccion', 'muros', 'pilares', 'tabiques',
              'carpinteria', 'escalera', 'reservas', 'mobiliario', 'luces',
              'cotas', 'rotulos', 'cajetin'):
        L.capa(c)

    # zona de doble altura
    L.poly('trama', zona_doble_altura(), 'url(#doble)', None)

    # proyeccion del forjado superior
    L.poly('proyeccion', E.FORJADO, 'none', '#8a8a8a', 'fino',
           ' stroke-dasharray="3.2 1.6"')

    muros(L)
    hundimiento(L)
    pared_l(L)
    pilares(L)
    viga(L)
    bano(L)
    ventanal_sur(L)
    zocalo_sur(L)
    escaparate(L)
    escalera(L, 'baja')
    reservas(L)
    # cerramiento de la escalera en planta baja (cara Oeste a 2,35 de P3)
    L.rect('tabiques', *E.CAJA_ESC_PB[1:], POCHE_TAB, TINTA, 'tabique')
    mobiliario(L, MB.MESAS_PB)
    nevera_bebidas(L)
    accesibilidad(L)
    luces(L)                      # puntos de luz del proyecto original
    aire(L)                       # cassettes de aire acondicionado (fotos)

    # contorno interior, para reforzar el recinto
    L.poly('muros', interior_pb(), 'none', TINTA, 'fino')

    # ---- rotulos
    L.texto('rotulos', 6.70, 6.25, 'ZONA CON FORJADO SUPERIOR  ·  +2,56',
            2.2, 'middle', '#4a4a4a', 'bold')
    L.texto('rotulos', 9.00, 3.25, 'DOBLE ALTURA', 2.6, 'middle', '#3c5a68',
            'bold')
    L.texto('rotulos', 0.70, 7.30, 'COCINA', 2.6, 'middle', '#3c5a68', 'bold',
            rot=-90)
    L.texto('rotulos', 0.70, 3.10, 'BARRA', 2.4, 'middle', '#3c5a68', 'bold',
            rot=-90)
    L.texto('rotulos', 8.78, 1.22, 'VESTÍBULO DE ACCESO', 2.3, 'middle', '#3c5a68',
            'bold')
    L.texto('rotulos', E.PARED_L_X, 7.00,
            f'PARED EN L  ·  {E.PARED_L_LARGO:.2f} + 0,74  ·  h=1,22'.replace('.', ','),
            2.0, 'middle', '#4a4a4a', rot=-90, dx=-4.6)
    nivel(L, 7.95, 0.72, '±0,00')

    L.texto('rotulos', 5.02, 8.967,
            f'MURO NORTE  e={E.MED_EXT - E.MURO_N:.2f}'.replace('.', ',')
            + f'  ·  {E.MED_EXT - E.MURO_N_COCINA:.2f}'.replace('.', ',')
            + ' en la cocina', 2.0, 'middle', '#ffffff')
    L.texto('rotulos', 0.125, 5.9, 'MURO OESTE  e=0,25', 2.0, 'middle', '#ffffff',
            rot=-90)
    L.texto('rotulos', 9.965, 5.9, 'MEDIANERA ESTE  e=0,15', 2.0, 'middle', '#ffffff',
            rot=-90)
    L.texto('rotulos', 3.60, 1.561, 'VENTANAL SUR  ·  paño de 4,00  ·  travesaño ≈ +2,30',
            2.1, 'middle', '#26485a', dy=4.6)
    L.texto('rotulos', 6.99, 0.370, 'ESCAPARATE  1,31', 2.1, 'middle', '#26485a',
            dy=4.6)
    L.texto('rotulos', 8.66, 0.370, 'PUERTA  2,06  ·  barrido 1,00', 2.0,
            'middle', '#26485a', dy=4.6)
    L.texto('rotulos', 9.35, 6.30,
            f'ESCALERA  {E.ESC_N_HUELLAS} huellas × 0,26', 1.95, 'middle', TINTA,
            rot=-90)
    L.texto('rotulos', 9.35, 6.30,
            f'{E.ESC_N_TABICAS} tabicas × {E.ESC_TABICA:.3f}'.replace('.', ','),
            1.95, 'middle', TINTA, rot=-90, dx=3.0)

    # ---- cotas
    HU, PL = E.HUNDIMIENTO, E.PARED_L_LAR
    ys = L.py(0.0) + 10.0
    L.cota_h('cotas', [0.0, 0.510, 1.290, 1.870, 5.870, 5.980, 6.331, 7.641,
                       9.701, 10.040], ys, 1.8, ext_desde=0.0)
    L.cota_h('cotas', [0.0, 10.040], ys + 8.0, 2.4)

    yn = L.py(9.156) - 8.0
    L.cota_h('cotas', [0.0, 0.250, HU['x1'], PL[3], P3[2], P3[4], 7.400,
                       8.811, 9.890, 10.040], yn, 1.8, ext_desde=9.156)

    xw = L.px(0.0) - 9.0
    L.cota_v('cotas', [0.0, 1.561, 2.009, 4.759, 5.357, E.MURO_N_COCINA,
                       9.156], xw,
             ext_desde=0.0)
    L.cota_v('cotas', [0.0, 9.156], xw - 8.0)

    xe = L.px(10.040) + 9.0
    L.cota_v('cotas', [0.370, 1.429, 3.579, 3.939, P3[3], P3[5], 7.738,
                       E.MURO_N, 9.156],
             xe, 1.9, ext_desde=10.040)

    # cotas interiores medidas en obra (19 set.)
    L.cota_h('cotas', [0.510, 1.290, 1.870], L.py(2.42), 1.8)
    # cadena del cliente: 3,01 de la pared en L a P3 y 2,33 a la caja
    L.cota_h('cotas', [PL[3], P3[2], P3[4], E.CAJA_ESC_PB[1]], L.py(6.95), 1.9)
    L.cota_v('cotas', [E.BARRA['y0'], E.BARRA['y1'], E.PASO_PERS['y1'],
                       E.MURO_N_COCINA],
             L.px(0.95), 1.9)
    L.cota_v('cotas', [E.ZOCALO_SUR['y0'], E.ZOCALO_SUR['y1']], L.px(5.30), 1.7)
    L.cota_h('cotas', [E.BARRA['x0'], E.BARRA['x1']], L.py(2.16), 1.7)
    L.cota_h('cotas', [0.250, E.BARRA['x0']], L.py(3.72), 1.8)   # 1,65 medido
    L.cota_h('cotas', [7.641, 9.890], L.py(1.52), 1.8)          # vestibulo: 2,25
    L.cota_h('cotas', [7.400, 7.770, 8.470, 9.890], L.py(7.55), 1.8)
    L.cota_v('cotas', [7.730, E.MURO_N], L.px(9.83), 1.8)
    L.cota_v('cotas', [P3[5], E.MURO_N], L.px(P3[2] - 0.07), 1.9)
    L.cota_v('cotas', [E.ZOCALO_SUR['y1'], P3[3]], L.px(7.00), 1.8,
             ext_desde=5.99)                                    # 2,72

    marco(L, 'PLANTA BAJA', '01 / 04', 'Estado actual · estructura',
          ['Cotas en metros. Hundimiento, pared en L, P3, barra,',
           'zócalo y puerta con las medidas del 19 set.; el resto,',
           'del levantamiento. Sección a 1,20 m sobre el pavimento.',
           'Muro Norte: la barra (2,79) + 0,60 de paso llevan la base',
           'de la pared en L a la cara Norte de P1; la L mide 3,60 y',
           'llega al muro. El muro es macizo hasta el solar: 0,20 de',
           'espesor, 0,15 en la cocina por el hundimiento de 0,05.',
           'Mesas dobles de 0,70 × 0,70 que el personal junta. El',
           'sillón, 0,60 de fondo sin medir. Luces del proyecto.',
           'La nevera A7 sale 0,58 de la cara Sur de P3 y deja 0,45',
           'hasta las sillas de M2: el paso a la barra da la vuelta',
           'por el Norte, con 0,70. Baño no accesible: 0,70.'],
          [(POCHE, TINTA, 'Muro de carga / medianera'),
           (POCHE_PIL, TINTA, 'Pilar o machón de hormigón'),
           (POCHE_TAB, TINTA, 'Pared en L y trasdosado del muro Norte'),
           (VIDRIO, '#3d6b80', 'Carpintería acristalada'),
           ('url(#doble)', '#c3ced6', 'Espacio de doble altura'),
           ('linea', '#8a8a8a', 'Forjado sobre el corte'),
           ('linea', RESERVA, 'Reserva de espacio del cliente'),
           ('#f4efe6', MOB, 'Mesas dobles de 0,70 × 0,70 y sillas'),
           ('#eaeff2', APAR, 'Nevera A7 · 0,54 × 0,58 (cara Sur de P3)'),
           ('linea', ACC, 'Recorrido de sala · 0,70 por el Norte'),
           ('punto', '#7d7d7d', 'Punto de luz s/ proyecto original'),
           ('linea', '#6f8a99', 'Aire acondicionado (cassette de techo)')],
          ('SUPERFICIES Y ALTURAS',
           [('Planta baja, dentro de muros', f'{E.SUP_PB_UTIL:.2f} m²'.replace('.', ',')),
            ('Zona de doble altura', f'{E.SUP_DOBLE_ALT:.2f} m²'.replace('.', ',')),
            ('Suelo a suelo, medido en obra', '2,56 m'),
            ('Altura libre bajo forjado', '2,56 − canto'),
            ('Pared en L, altura', '1,22 m'),
            ('Mesas dobles / plazas sentadas',
             f'{len(MB.MESAS_PB)} / {MB.PLAZAS_PB}'),
            ('Acristalamiento de fachada', '≈ 4,70 m')]))
    comprobar(L)
    return L


# ============================================================== PLANTA ALTA
def planta_alta():
    L = Lienzo(W, H, ESC, OX, OY)
    for c in ('hoja', 'trama', 'proyeccion', 'muros', 'pilares', 'tabiques',
              'carpinteria', 'escalera', 'mobiliario', 'luces', 'cotas',
              'rotulos', 'cajetin'):
        L.capa(c)

    # vacio sobre planta baja
    L.poly('trama', zona_doble_altura(), 'url(#vacio)', None)

    # contorno del local en planta alta (muros que siguen subiendo)
    muros(L, planta='alta')
    # el acristalamiento de fachada es de doble altura: el plano de seccion a
    # +4,20 lo sigue cortando
    ventanal_sur(L)
    escaparate(L, con_puerta=False)

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
    L.poly('muros', interior_pb(hund=False), 'none', '#8a8a8a', 'auxiliar')
    mobiliario(L, MB.MESAS_PA)
    cotas_paso(L, MB.PASOS_PA)

    # ---- rotulos
    nivel(L, 5.75, 6.55, '+2,56')
    L.texto('rotulos', 5.75, 7.22, 'ALTILLO · COWORK', 2.8, 'middle', '#4a4a4a',
            'bold')
    L.texto('rotulos', 5.75, 7.22, 'nivel +2,56  ·  altura libre por medir',
            2.2, 'middle', '#4a4a4a', dy=3.4)
    L.texto('rotulos', 1.34, 8.62,
            f"El hundimiento de {E.HUNDIMIENTO['p']:.2f} del muro Norte".replace('.', ','),
            1.9, 'middle', '#9a2b2b')
    L.texto('rotulos', 1.34, 8.62, 'sólo se ha medido en planta baja (lámina 01)',
            1.9, 'middle', '#9a2b2b', dy=2.6)
    L.texto('rotulos', 5.6, 2.55, 'VACÍO SOBRE PLANTA BAJA', 2.8, 'middle', '#3c5a68',
            'bold')
    L.texto('rotulos', 5.6, 2.55, 'altura total por medir', 2.3, 'middle',
            '#3c5a68', dy=3.6)
    L.texto('rotulos', 1.33, 5.6, 'VACÍO', 2.3, 'middle', '#3c5a68', 'bold', rot=-90)
    L.texto('rotulos', 3.60, 8.30, 'ASEO', 2.4, 'middle', '#4a4a4a', 'bold')
    L.texto('rotulos', 5.00, 8.62, 'INODORO', 2.1, 'middle', '#4a4a4a', 'bold')
    L.texto('rotulos', 6.48, 8.30, 'ALMACÉN', 2.4, 'middle', '#4a4a4a', 'bold')
    L.texto('rotulos', 8.60, 8.45, 'PASO', 2.2, 'middle', '#4a4a4a', 'bold')
    L.texto('rotulos', 7.0, 4.12, 'BARANDILLA  h=1,00', 2.1, 'middle',
            '#26485a')
    L.texto('rotulos', 2.65, 5.7, 'BARANDILLA DE VIDRIO', 2.0, 'middle', '#26485a',
            rot=-90, dx=2.6)
    L.texto('rotulos', 9.35, 5.95, 'ESCALERA · llegada +2,56', 2.0, 'middle', TINTA,
            rot=-90, dx=3.4)
    L.texto('rotulos', 3.25, 1.561, 'VENTANAL SUR · doble altura', 2.1, 'middle',
            '#26485a', dy=4.6)
    L.texto('rotulos', 7.97, 0.330, 'ESCAPARATE · doble altura', 2.1, 'middle',
            '#26485a', dy=4.6)
    # ---- cotas
    yn = L.py(9.156) - 8.0
    L.cota_h('cotas', [0.0, 0.250, 2.461, 2.560, 3.089, 3.849, 4.461, 4.560,
                       5.459, 5.558, 7.408, 7.511, 9.890, 10.040], yn, 1.75,
             ext_desde=9.156)
    L.cota_h('cotas', [0.0, 10.040], yn - 8.0, 2.4)

    ys = L.py(0.0) + 10.0
    L.cota_h('cotas', [0.0, 2.411, 5.731, 6.331, 8.759, 8.811, 10.040], ys,
             ext_desde=0.0)

    xw = L.px(0.0) - 9.0
    L.cota_v('cotas', [1.561, 3.939, 7.509, 7.607, E.MURO_N, 9.156], xw,
             ext_desde=1.561)
    L.cota_v('cotas', [0.0, 9.156], xw - 8.0)

    xe = L.px(10.040) + 9.0
    L.cota_v('cotas', [3.939, P3[3], 5.309, P3[5], 7.738, 8.072, 8.208, 9.156],
             xe, 1.9, ext_desde=10.040)

    L.cota_v('cotas', [7.509, E.MURO_N], L.px(2.72), 1.9)

    marco(L, 'PLANTA ALTA', '02 / 04', 'Altillo +2,56 · estructura',
          ['Cotas en metros, tomadas sobre el levantamiento.',
           'Nivel del forjado +2,56, medido en obra.',
           'El forjado del altillo no cubre todo el local: la',
           'franja sur y oeste es un vacío a doble altura.',
           'Mesa de cowork 2,40 × 1,00 para 8 puestos y una',
           'redonda de Ø 1,20 con 6 sillas. Medidas promedio.',
           'Pasos libres entre mobiliario acotados en azul:',
           '1,01 hacia el aseo y el almacén; 1,30 en el',
           'desembarco; 0,26 a 0,85 en los accesos a las sillas.'],
          [(POCHE, TINTA, 'Muro de carga / medianera'),
           (POCHE_PIL, TINTA, 'Pilar o machón de hormigón'),
           (POCHE_TAB, TINTA, 'Tabiquería'),
           (VIDRIO, '#3d6b80', 'Barandilla de vidrio'),
           ('#f4efe6', MOB, 'Mesas y sillas (medidas promedio)'),
           ('cota', ACC, 'Paso libre entre mobiliario (m)'),
           ('url(#vacio)', '#b9c6cf', 'Vacío sobre planta baja')],
          ('SUPERFICIES Y ALTURAS',
           [('Forjado de planta alta', f'{E.SUP_FORJADO:.2f} m²'.replace('.', ',')),
            ('Altillo diáfano', '26,17 m²'),
            ('Aseo (lavabo + inodoro)', '3,92 m²'),
            ('Almacén', '2,59 m²'),
            ('Nivel del forjado, medido', '+2,56 m'),
            ('Puestos de cowork', f'{MB.PLAZAS_PA}')]))
    comprobar(L)
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
