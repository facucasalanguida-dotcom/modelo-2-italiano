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
AZZ = '#12a0d7'       # toldos: azzurro Napoli
AZZ_T = '#0b6f99'     # rotulos de los toldos, mas oscuro para que se lea
LUZ = '#7d7d7d'       # puntos de luz

AQUI = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- formato A3
W, H = 420.0, 297.0
ESC = 20.0                      # mm por metro  ->  1:50
MARGEN = 8.0
CAJ_X = W - MARGEN - 96.0       # borde izquierdo del cajetin
OX, OY = 62.0, 236.0            # papel del origen de obra
# La planta baja sube 27,5 mm para que quepan los toldos, que vuelan hasta
# 1,66 por delante de la fachada, y bajo ellos las cadenas de cotas.
OY_PB = 208.5

FECHA = '29 de septiembre de 2026'

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
            elif relleno == 'luces':
                # empotrado (circulo con cruz) y colgante (circulo con punto)
                ce, cc, cy_ = x0 + 6.8, x0 + 11.4, y - 1.2
                L._add('cajetin', f'<circle cx="{ce:.2f}" cy="{cy_:.2f}" r="1.7" '
                                  f'fill="none" stroke="{trazo}" stroke-width="0.18"/>')
                L.p_linea('cajetin', ce - 1.2, cy_, ce + 1.2, cy_, trazo, 'auxiliar')
                L.p_linea('cajetin', ce, cy_ - 1.2, ce, cy_ + 1.2, trazo, 'auxiliar')
                L._add('cajetin', f'<circle cx="{cc:.2f}" cy="{cy_:.2f}" r="2.0" '
                                  f'fill="none" stroke="{trazo}" stroke-width="0.18"/>')
                L._add('cajetin', f'<circle cx="{cc:.2f}" cy="{cy_:.2f}" r="0.56" '
                                  f'fill="{trazo}"/>')
            elif relleno == 'toldo':
                # lona en proyeccion, barra de carga y un poste
                L.p_rect('cajetin', x0 + 5, y - 3.4, x0 + 13, y + 0.2, trazo, trazo,
                         'fino', ' fill-opacity="0.10" stroke-dasharray="1.6 1.0"')
                L.p_rect('cajetin', x0 + 5, y - 0.6, x0 + 13, y + 0.2, trazo, trazo,
                         'auxiliar')
                L._add('cajetin', f'<circle cx="{x0 + 11.5:.2f}" cy="{y + 0.9:.2f}" '
                                  f'r="0.5" fill="#ffffff" stroke="{trazo}" '
                                  f'stroke-width="0.25"/>')
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


# Borde Sur del interior (29 set.): la linea de los vidrios y la de la
# puerta, como el pavimento del modelo 3D. La puerta esta al fondo del
# vestibulo, asi que el vestibulo queda fuera; P5 tambien, y el rincon entre
# P5 y el ventanal lo cierra el retorno acristalado.
_R = E.RETORNO
SUR_INTERIOR = [(9.890, E.PUERTA_FONDO), (E.VESTIBULO_VIDRIO[2], E.PUERTA_FONDO),
                (E.VESTIBULO_VIDRIO[2], 0.419), (6.331, 0.419), (6.331, 1.000),
                (_R['x1'], 1.000), (_R['x1'], 1.621), (0.510, 1.621),
                (0.510, 2.009), (0.250, 2.009)]


def interior_pb(hund=True, final=True):
    if not final:
        # el del levantamiento, con la puerta en la linea de fachada: es el que
        # sigue usando export_sketchup.py para la solera, porque su modelo
        # conserva esa puerta y el muro del cuello
        return [(0.250, _H['y1']), (_H['x1'], _H['y1']), (_H['x1'], _H['y0']),
                (9.890, _H['y0']), (9.890, 1.429), (9.710, 1.429),
                (9.710, 0.379), (6.230, 0.379), (6.230, 0.960), (5.980, 0.960),
                (5.980, 1.621), (0.510, 1.621), (0.510, 2.009), (0.250, 2.009)]
    if not hund:
        # planta alta: sin el hundimiento, y por encima del cubo de la
        # entrada el interior llega hasta el escaparate
        return ([(0.250, E.MURO_N), (9.890, E.MURO_N), (9.890, 1.429),
                 (9.710, 1.429), (9.710, 0.419)] + SUR_INTERIOR[3:])
    return [(0.250, _H['y1']), (_H['x1'], _H['y1']), (_H['x1'], _H['y0']),
            (9.890, _H['y0'])] + SUR_INTERIOR


def zona_doble_altura():
    """Lo que no tiene techo hasta el del altillo. Fuera la cocina, que lleva
    techo de pladur a 2,31 desde la viga P1b, y el cubo de la entrada, con
    techo a 2,10."""
    t = E.TECHO_COCINA
    return [(0.250, t['y0']), (2.411, t['y0']), (2.411, 3.939),
            (9.890, 3.939)] + SUR_INTERIOR


# El tramo sur esta ocupado en toda su longitud por el ventanal: el plano de
# seccion lo corta por el vidrio, asi que no se macizan.
SIN_POCHE = ('Muro Sur (con ventanal)',)
# En planta baja este tramo se sustituye por el hundimiento medido.
SOLO_PA = ()   # la medianera del hundimiento ya se dibuja en las dos plantas


def muros(L, capa='muros', planta='baja'):
    for nm, x0, y0, x1, y1, _e in E.MUROS:
        if nm in SIN_POCHE or nm in E.NO_EXISTEN or (planta == 'baja' and nm in SOLO_PA):
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
    """Los dos panos del ventanal y el retorno acristalado junto a P5.

    El levantamiento cerraba el rincon con un muro y una jamba que en obra no
    existen (video de la fachada): el pano Este llega al retorno de vidrio,
    que baja hasta la cara Norte de P5.
    """
    v, r = E.VENTANAL_SUR, E.RETORNO
    ya, yb = v['y'] + 0.012, v['y'] + v['e'] - 0.012
    for a, b in v['panos']:
        L.rect('carpinteria', a, ya, min(b, r['x1']), yb, VIDRIO, '#3d6b80', 'fino')
    xm = (r['x0'] + r['x1']) / 2
    L.rect('carpinteria', xm - 0.018, 1.000, xm + 0.018, ya, VIDRIO, '#3d6b80', 'fino')


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
        # costado Oeste del vestibulo: vidrio con su marco, de la fachada a
        # la puerta. En la linea de fachada queda el hueco de 2,06 abierto.
        x0, y0, x1, y1 = E.VESTIBULO_VIDRIO
        L.rect('carpinteria', x0, y0, x1, y1, '#ffffff', TINTA, 'fino')
        xm = (x0 + x1) / 2
        L.rect('carpinteria', xm - 0.018, y0 + 0.060, xm + 0.018, y1 - 0.060,
               VIDRIO, '#3d6b80', 'fino')
        puerta_acceso(L)
    else:
        L.rect('carpinteria', s['x0'], s['y'] + 0.010, s['x1'],
               s['y'] + s['e'] - 0.010, VIDRIO, '#3d6b80', 'fino')


def puerta_acceso(L):
    """Doble hoja de 2,06 al fondo del vestibulo, barriendo 1,00 hacia la
    calle: las hojas abiertas quedan contra los costados del vestibulo."""
    p = E.PUERTA_ACCESO
    y, br = E.PUERTA_FONDO, p['barrido']
    media = (p['x1'] - p['x0']) / 2
    for lado, xg in ((+1, p['x0']), (-1, p['x1'])):
        # hoja abatida contra el costado
        L.rect('carpinteria', xg - 0.02 * lado, y - br, xg + 0.02 * lado, y,
               TINTA, None)
        L.linea('carpinteria', xg, y, xg + lado * media, y, TINTA, 'fino')
        L._add('carpinteria',
               f'<path d="M {L.px(xg + lado * media):.3f} {L.py(y):.3f} '
               f'A {L.mm(br):.3f} {L.mm(br):.3f} 0 0 {1 if lado > 0 else 0} '
               f'{L.px(xg):.3f} {L.py(y - br):.3f}" fill="none" '
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


def mobiliario(L, mesas, luces=()):
    """Mesas y sillas con medidas promedio, en su propia capa.

    Si un punto de luz cae sobre la mesa, el rotulo baja a su canto Sur para
    no quedar debajo del simbolo.
    """
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
        tx, ty = (x0 + x1) / 2, (y0 + y1) / 2
        if any(x0 < lx < x1 and y0 < ly < y1 for lx, ly in luces):
            ty = y0 + 0.15
            # y si ahi cae el cassette del aire (M5), al rincon Oeste
            if any(abs(tx - cx) < a / 2 + 0.08 and abs(ty - cy) < f / 2
                   for _t, _n, cx, cy, a, f in E.AIRE):
                tx = x0 + 0.16
        L.texto('rotulos', tx, ty, tag, 2.0, 'middle', MOB, 'bold', dy=0.7)


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
    rw, rh = E.AIRE_REJILLA or (0.0, 0.0)
    for tag, nm, cx, cy, a, f in E.AIRE:
        L.rect('luces', cx - a / 2, cy - f / 2, cx + a / 2, cy + f / 2,
               'none', '#6f8a99', 'medio', dd)
        L.linea('luces', cx - a / 2, cy - f / 2, cx + a / 2, cy + f / 2,
                '#6f8a99', 'auxiliar', dd)
        L.linea('luces', cx - a / 2, cy + f / 2, cx + a / 2, cy - f / 2,
                '#6f8a99', 'auxiliar', dd)
        if rh:
            L.rect('luces', cx - rw / 2, cy + f / 2 + 0.06, cx + rw / 2,
                   cy + f / 2 + 0.06 + rh, 'none', '#6f8a99', 'fino', dd)
        L.texto('rotulos', cx, cy + f / 2 + rh + 0.10, tag, 1.9, 'middle',
                '#4c6b7c', 'bold')


NUM_LUZ = '#a8480c'   # numero de cada luz
# donde va el numero respecto de su luz (m) cuando no cabe arriba a la derecha
NUM_SITIO = {8: (-0.13, 0.13, 'end'), 9: (0.13, -0.22, 'start'),
             14: (-0.14, -0.22, 'end'), 15: (-0.14, 0.14, 'end')}


def luces(L, empotrados=True, numeros=False, tam=1.8, sitio_num=None):
    if empotrados:
        for x, y in E.EMPOTRADOS:
            L.circulo('luces', x, y, 0.085, 'none', '#7d7d7d', 'fino')
            L.linea('luces', x - 0.06, y, x + 0.06, y, '#7d7d7d', 'auxiliar')
            L.linea('luces', x, y - 0.06, x, y + 0.06, '#7d7d7d', 'auxiliar')
    for x, y in E.COLGANTES:
        L.circulo('luces', x, y, 0.10, 'none', '#7d7d7d', 'fino')
        L.circulo('luces', x, y, 0.028, '#7d7d7d', '#7d7d7d', 'auxiliar')
    if numeros:
        # numero de cada luz, el mismo de la lamina 05 (replanteo)
        sitios = {**NUM_SITIO, **(sitio_num or {})}
        for n, x, y, *_r in E.LUCES_PB:
            dx, dy, anc = sitios.get(n, (0.13, 0.13, 'start'))
            L.texto('rotulos', x + dx, y + dy, str(n), tam, anc, NUM_LUZ, 'bold')


def cerramiento_escalera(L, z_corte=1.20):
    """Costado de la escalera en planta baja (29 set.).

    Arranca en el montante de acero de 0,16, a mitad del 5.o peldano; los
    peldanos de delante quedan vistos de lado. Su borde de arriba va en
    rampante: por debajo del plano de seccion se dibuja visto y, a partir de
    donde lo supera, cortado.
    """
    nm, x0, y0, x1, y1 = E.CAJA_ESC_PB
    mx0, my0, mx1, my1 = E.MONTANTE_ESC
    r = E.ESC_RAMPANTE
    yc = r['y0'] + (z_corte - r['z0']) / r['pend']          # 5,22
    L.rect('tabiques', x0, my1, x1, yc, '#ffffff', TINTA, 'fino')
    L.rect('tabiques', x0, yc, x1, y1, POCHE_TAB, TINTA, 'tabique')
    L.rect('pilares', mx0, my0, mx1, my1, POCHE_PIL, TINTA, 'corte')
    L.texto('rotulos', mx0 - 0.06, (my0 + my1) / 2, 'MONTANTE 0,16', 1.6, 'end',
            '#4a4a4a', dy=0.55)


def pizarra(L):
    """Pizarra con la carta sobre la trasbarra: por encima del corte."""
    p = E.PIZARRA
    L.rect('proyeccion', p['x'], p['y0'], p['x'] + 0.050, p['y1'], 'none',
           '#6a6a6a', 'fino', ' stroke-dasharray="2.4 1.4"')
    L.texto('rotulos', p['x'] + 0.15, (p['y0'] + p['y1']) / 2 - 0.30,
            'PIZARRA  +2,30', 1.7, 'middle', '#5f5f5f', rot=-90, dy=0.6)


def toldos(L):
    """Toldos desplegados (29 set.), azzurro con el logo: la lona en
    proyeccion, la capota contra la fachada, la barra de carga con su faldon,
    los postes y la cortina lateral del grande."""
    for t in E.TOLDOS:
        c0, c1, cy0, cy1 = t['capota']
        a0, a1, yb = t['a0'], t['a1'], t['y_barra']
        L.rect('proyeccion', a0, yb, a1, cy0, AZZ, AZZ, 'fino',
               ' fill-opacity="0.07" stroke-dasharray="2.2 1.2"')
        L.rect('proyeccion', c0, cy0, c1, cy1, 'none', AZZ, 'fino')
        L.rect('proyeccion', a0, yb - E.FALDON_TOLDO, a1, yb, AZZ, AZZ, 'auxiliar')
        for xp in t['postes']:
            L.circulo('proyeccion', xp, yb - 0.030, E.R_POSTE_TOLDO, '#ffffff', AZZ,
                      'medio')
        if t['cortina'] is not None:
            L.linea('proyeccion', t['cortina'], cy0, t['cortina'], yb, AZZ, 'medio')
    g, e = E.TOLDOS
    L.texto('rotulos', 3.80, -0.78, 'TOLDO GRANDE  ·  azzurro con el logo', 2.2,
            'middle', AZZ_T, 'bold')
    L.texto('rotulos', 3.80, -0.78,
            f"vuela {g['vuelo']:.2f}  ·  cae {g['caida']}°  ·  barra a +{g['z_barra']:.2f}"
            .replace('.', ','), 1.9, 'middle', AZZ_T, dy=3.2)
    L.texto('rotulos', 0.20, 0.10, 'CORTINA LATERAL', 1.7, 'middle', AZZ_T,
            rot=-90, dy=0.6)
    L.texto('rotulos', 8.67, -0.26, 'TOLDO DE LA ENTRADA', 2.0, 'middle', AZZ_T,
            'bold')
    L.texto('rotulos', 8.67, -0.26,
            f"vuela {e['vuelo']:.2f}  ·  cae {e['caida']}°  ·  barra +{e['z_barra']:.2f}"
            .replace('.', ','), 1.7, 'middle', AZZ_T, dy=2.8)


# ============================================================== PLANTA BAJA
def planta_baja():
    L = Lienzo(W, H, ESC, OX, OY_PB)
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
    # cerramiento de la escalera en planta baja (cara Oeste a 2,33 de P3),
    # desde el montante y con el borde en rampante
    cerramiento_escalera(L)
    pizarra(L)
    toldos(L)
    mobiliario(L, MB.MESAS_PB, luces=E.EMPOTRADOS)
    nevera_bebidas(L)
    accesibilidad(L)
    luces(L, numeros=True)        # proyecto original y, en sala, sobre las mesas
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
    L.texto('rotulos', 0.70, 7.30, 'techo de pladur a +2,31', 1.9, 'middle',
            '#3c5a68', rot=-90, dx=-3.4)
    L.texto('rotulos', 0.70, 3.10, 'BARRA', 2.4, 'middle', '#3c5a68', 'bold',
            rot=-90)
    # el vestibulo queda delante de la puerta: rotulo entre los dos barridos
    L.texto('rotulos', 8.67, 0.58, 'VESTÍBULO', 1.9, 'middle', '#3c5a68', 'bold')
    L.texto('rotulos', 8.67, 0.58, f'techo +{E.H_VESTIBULO:.2f}'.replace('.', ','),
            1.7, 'middle', '#3c5a68', dy=2.6)
    L.texto('rotulos', E.PARED_L_X, 7.00,
            f'PARED EN L  ·  {E.PARED_L_LARGO:.2f} + 0,74  ·  h=1,22'.replace('.', ','),
            2.0, 'middle', '#4a4a4a', rot=-90, dx=-4.6)
    nivel(L, 6.55, 0.62, '±0,00')

    L.texto('rotulos', 5.02, 8.967,
            f'MURO NORTE  e={E.MED_EXT - E.MURO_N:.2f}'.replace('.', ',')
            + f'  ·  {E.MED_EXT - E.MURO_N_COCINA:.2f}'.replace('.', ',')
            + ' en la cocina', 2.0, 'middle', '#ffffff')
    L.texto('rotulos', 0.125, 5.9, 'MURO OESTE  e=0,25', 2.0, 'middle', '#ffffff',
            rot=-90)
    L.texto('rotulos', 9.965, 5.9, 'MEDIANERA ESTE  e=0,15', 2.0, 'middle', '#ffffff',
            rot=-90)
    L.texto('rotulos', 3.60, 1.561,
            'VENTANAL SUR  ·  retorno de vidrio junto a P5  ·  travesaño ≈ +2,30',
            2.1, 'middle', '#26485a', dy=7.2)
    # por debajo de la capota del toldo de la entrada (0,165..0,365)
    L.texto('rotulos', 6.99, 0.370, 'ESCAPARATE  1,31', 2.1, 'middle', '#26485a',
            dy=7.4)
    L.texto('rotulos', 8.67, 0.370, 'PUERTA 2,06 AL FONDO  ·  barrido 1,00', 1.9,
            'middle', '#26485a', dy=7.4)
    L.texto('rotulos', 9.35, 6.30,
            f'ESCALERA  {E.ESC_N_HUELLAS} huellas × 0,26', 1.95, 'middle', TINTA,
            rot=-90)
    L.texto('rotulos', 9.35, 6.30,
            f'{E.ESC_N_TABICAS} tabicas × {E.ESC_TABICA:.3f}'.replace('.', ','),
            1.95, 'middle', TINTA, rot=-90, dx=3.0)

    # ---- cotas
    HU, PL = E.HUNDIMIENTO, E.PARED_L_LAR
    # por debajo de los toldos, que vuelan hasta 1,66 por delante de fachada.
    # Sin el muro del cuello, el pano Este del ventanal acaba en P5 (retorno).
    P5 = next(p for p in E.PILARES if p[0] == 'P5')
    y_toldos = min(t['y_barra'] for t in E.TOLDOS) - E.FALDON_TOLDO
    ys = L.py(y_toldos) + 5.0
    L.cota_h('cotas', [0.0, 0.510, 1.290, 1.870, P5[2], P5[4], 7.641,
                       9.701, 10.040], ys, 1.8, ext_desde=0.0)
    L.cota_h('cotas', [0.0, 10.040], ys + 7.5, 2.4)

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

    marco(L, 'PLANTA BAJA', '01 / 05', 'Estado actual · estructura',
          ['Cotas en metros: del cliente (19 set.) y, el resto, del levantamiento.',
           'Sección a 1,20 m. Muro Norte macizo: 0,20, y 0,15 en la cocina por el',
           'hundimiento de 0,05. La pared en L mide 3,60 y llega al muro.',
           'Mesas dobles de 0,70 × 0,70; sillón de 0,60 de fondo sin medir.',
           'A7 deja 0,45 hasta M2: a la barra, por el Norte (0,70). Baño no accesible.',
           '29 set.: luces de sala centradas en las mesas; puerta al fondo del',
           'vestíbulo; retorno de vidrio junto a P5; montante y cerramiento bajo en',
           'la escalera; techo de pladur en la cocina; toldos desplegados.'],
          [(POCHE, TINTA, 'Muro de carga / medianera'),
           (POCHE_PIL, TINTA, 'Pilar, machón o montante'),
           (POCHE_TAB, TINTA, 'Pared en L y tabiquería'),
           (VIDRIO, '#3d6b80', 'Carpintería acristalada'),
           ('url(#doble)', '#c3ced6', 'Espacio de doble altura'),
           ('linea', '#8a8a8a', 'Forjado, viga y pizarra sobre el corte'),
           ('linea', RESERVA, 'Reserva de espacio del cliente'),
           ('#f4efe6', MOB, 'Mesas dobles de 0,70 × 0,70 y sillas'),
           ('#eaeff2', APAR, 'Nevera A7 · 0,54 × 0,58 (cara Sur de P3)'),
           ('linea', ACC, 'Recorrido de sala · 0,70 por el Norte'),
           ('luces', LUZ, 'Luz empotrada y colgante (nº: lámina 05)'),
           ('linea', '#6f8a99', 'Aire acondicionado (cassette de techo)'),
           ('toldo', AZZ, 'Toldo desplegado: lona, barra y poste')],
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
    L.texto('rotulos', 1.33, 3.47, 'VACÍO', 2.3, 'middle', '#3c5a68', 'bold', rot=-90)
    # la cocina ya no es vacio: tiene techo de pladur 0,25 por debajo del forjado
    L.texto('rotulos', 1.33, 6.00, 'TECHO DE LA COCINA  ·  pladur a +2,31', 1.9,
            'middle', '#3c5a68', rot=-90)
    L.texto('rotulos', 8.67, 0.93, 'cubo de la entrada  ·  techo +2,24', 1.7,
            'middle', '#3c5a68')
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

    marco(L, 'PLANTA ALTA', '02 / 05', 'Altillo +2,56 · estructura',
          ['Cotas en metros, tomadas sobre el levantamiento.',
           'Nivel del forjado +2,56, medido en obra.',
           'El forjado no cubre todo el local: la franja Sur y la',
           'barra son doble altura; la cocina, techo a +2,31.',
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


# ======================================================= REPLANTEO DE LUCES
def _m(v):
    """Metros con dos decimales, redondeando las mitades hacia arriba: si no,
    dos medidas iguales (1,715) salian una en 1,71 y la otra en 1,72."""
    return f'{v + 1e-9:.2f}'.replace('.', ',')


def _ext(L, x0, y0, x1, y1):
    """Linea de referencia de una cota, de la luz o de la pared a la cota."""
    L.linea('cotas', x0, y0, x1, y1, COTA_COL, 'auxiliar')


def tabla_luces(L, y0=242.0, y1=287.0, x0=11.0, x1=W - 8.0 - 96.0 - 2.0):
    """Las dos medidas de cada luz, en dos columnas al pie de la lamina 05."""
    L.p_rect('cajetin', x0, y0, x1, y1, '#fbf6ee', NUM_LUZ, 'fino')
    L.p_texto('cajetin', x0 + 3.5, y0 + 4.6, 'REPLANTEO DE LOS HUECOS', 2.6, 'start',
              NUM_LUZ, 'bold', espaciado='0.6')
    L.p_texto('cajetin', x0 + 62.0, y0 + 4.6,
              'Metros, al centro de cada luz, desde la cara sin revestir de la pared, '
              'del pilar o del borde del forjado.  * ver aviso en las notas.',
              2.0, 'start', '#7a5a3a')
    L.p_linea('cajetin', x0 + 3.5, y0 + 6.4, x1 - 3.5, y0 + 6.4, '#d8c6ae', 'cota')
    porcol = (len(E.LUCES_PB) + 1) // 2
    ancho = (x1 - x0 - 7.0) / 2
    cols = ((0.0, 'Nº'), (8.0, 'Sitio'), (44.0, 'Este – Oeste'), (96.0, 'Norte – Sur'))
    for c in range(2):
        for dx, t in cols:
            L.p_texto('cajetin', x0 + 3.5 + c * ancho + dx, y0 + 10.4, t, 1.9, 'start',
                      '#7a5a3a', 'bold')
    for i, luz in enumerate(E.LUCES_PB):
        c, f = divmod(i, porcol)
        cx, cy = x0 + 3.5 + c * ancho, y0 + 14.2 + f * 3.1
        n, tipo, sitio = luz[0], luz[3], luz[4]
        (mx, tx, _ex), (my, ty, _ey) = E.replanteo_luz(luz)
        L.p_texto('cajetin', cx, cy, f"{n}{' *' if n in E.AVISOS_LUCES else ''}", 2.0,
                  'start', NUM_LUZ, 'bold')
        L.p_texto('cajetin', cx + 8.0, cy, f'{sitio} · {tipo}', 1.9, 'start', '#3a3a3a')
        L.p_texto('cajetin', cx + 44.0, cy, f'{_m(mx)} {tx}', 1.9, 'start', '#3a3a3a')
        L.p_texto('cajetin', cx + 96.0, cy, f'{_m(my)} {ty}', 1.9, 'start', '#3a3a3a')


def replanteo_luces():
    """Lamina 05: las luces de planta baja numeradas y acotadas desde las
    paredes, para marcar y abrir los huecos del techo en obra (29 set.).

    Las cotas van en cadena por filas de luces, desde la cara sin revestir de
    la pared, del pilar o del borde del forjado mas cercano; las mismas
    medidas estan en la tabla del pie, luz por luz.
    """
    L = Lienzo(W, H, ESC, OX, OY)
    L._fmt = _m
    for c in ('hoja', 'trama', 'proyeccion', 'muros', 'pilares', 'tabiques',
              'carpinteria', 'escalera', 'luces', 'cotas', 'rotulos', 'cajetin'):
        L.capa(c)

    # ---- la caja del local, solo lo que sirve de referencia
    L.poly('trama', zona_doble_altura(), 'url(#doble)', None)
    L.poly('proyeccion', E.FORJADO, 'none', '#8a8a8a', 'fino',
           ' stroke-dasharray="3.2 1.6"')
    muros(L)
    pared_l(L)
    pilares(L)
    for nm, x0, y0, x1, y1 in E.BANO_TABIQUES:
        L.rect('tabiques', x0, y0, x1, y1, POCHE_TAB, TINTA, 'tabique')
    ventanal_sur(L)
    escaparate(L)
    cerramiento_escalera(L)
    L.rect('escalera', E.ESC_X0, E.ESC_Y_PIE, E.ESC_X1, E.ESC_Y_ALTO, 'none',
           '#9a9a9a', 'fino')
    viga(L)
    q = Q.CAMPANA_POS
    L.rect('proyeccion', q['x0'], q['y0'], q['x1'], q['y1'], 'none', '#6a6a6a',
           'fino', ' stroke-dasharray="2.4 1.4"')
    L.texto('rotulos', 1.955, 8.75, 'CAMPANA', 1.8, 'middle', '#5f5f5f', dy=0.6)
    aire(L)
    L.poly('muros', interior_pb(), 'none', TINTA, 'fino')
    # eje de la fila de la cocina
    L.linea('cotas', 1.100, 4.45, 1.100, 8.70, COTA_COL, 'auxiliar',
            ' stroke-dasharray="3.0 1.0 0.6 1.0"')
    luces(L, numeros=True, tam=2.6, sitio_num={18: (-0.13, -0.24, 'end')})

    # ---- rotulos de zona, con el techo de cada una
    L.texto('rotulos', 0.70, 7.30, 'COCINA', 2.4, 'middle', '#3c5a68', 'bold', rot=-90)
    L.texto('rotulos', 0.70, 7.30, 'techo de pladur a +2,31', 1.8, 'middle',
            '#3c5a68', rot=-90, dx=-3.2)
    L.texto('rotulos', 0.70, 3.10, 'BARRA  ·  doble altura', 2.0, 'middle', '#3c5a68',
            'bold', rot=-90)
    L.texto('rotulos', 5.60, 7.00, 'SALA  ·  techo bajo el altillo', 2.1, 'middle',
            '#4a4a4a', 'bold')
    L.texto('rotulos', 6.00, 2.55, 'DOBLE ALTURA', 2.3, 'middle', '#3c5a68', 'bold')
    L.texto('rotulos', 8.20, 8.72, 'BAÑO', 2.0, 'middle', '#4a4a4a', 'bold')
    L.texto('rotulos', 8.67, 0.58, 'VESTÍBULO', 1.9, 'middle', '#3c5a68', 'bold')
    L.texto('rotulos', 8.67, 0.58, 'techo +2,10', 1.7, 'middle', '#3c5a68', dy=2.6)
    L.texto('rotulos', 9.35, 6.00, 'ESCALERA', 2.0, 'middle', '#6a6a6a', rot=-90)
    L.texto('rotulos', 6.80, 3.939, 'borde Sur del forjado', 1.7, 'middle',
            '#6a6a6a', dy=-0.9)

    # ---- cotas de replanteo, fila a fila
    Y = L.py
    X = L.px
    # fila del sillon (1, 2, 3): de la pared en L al tabique del baño
    L.cota_h('cotas', [2.530, 3.250, 4.965, 6.680, 7.400], Y(7.78), 1.9,
             ext_desde=8.007)
    # fila central (4, 5, 6): de la pared en L a P3
    L.cota_h('cotas', [2.530, 3.185, 4.190, 5.320, 5.670], Y(6.08), 1.9,
             ext_desde=5.780)
    # las dos filas desde el muro Norte, entre las luces 1 y 2 y entre 4 y 5
    L.cota_v('cotas', [5.780, 8.007, 8.957], X(3.90), 1.9)
    _ext(L, 3.250 + 0.085, 8.007, 3.90, 8.007)
    _ext(L, 4.190 - 0.085, 5.780, 3.90, 5.780)
    # fila de y 4,60 (7, 8): del borde Oeste del forjado a P3
    L.cota_h('cotas', [2.411, 2.600, 4.100, 5.670], Y(4.35), 1.9, ext_desde=4.600)
    # barra (14, 15) y fila de y 4,60 desde el borde Sur del forjado
    L.cota_v('cotas', [2.280, 3.580, 3.939, 4.600], X(2.30), 1.9)
    _ext(L, 2.040 + 0.10, 2.280, 2.30, 2.280)
    _ext(L, 2.040 + 0.10, 3.580, 2.30, 3.580)
    _ext(L, 2.411, 3.939, 2.30, 3.939)
    _ext(L, 2.600 - 0.085, 4.600, 2.30, 4.600)
    # colgantes de la doble altura (15, 16, 17), de muro a muro
    L.cota_h('cotas', [0.250, 2.040, 4.600, 7.600, 9.890], Y(2.05), 1.9)
    _ext(L, 2.040, 2.280 - 0.10, 2.040, 2.05)
    for x in (4.600, 7.600):
        _ext(L, x, 3.200 - 0.10, x, 2.05)
        # y su distancia al borde Sur del forjado
        L.cota_v('cotas', [3.200, 3.939], X(x - 0.25), 1.9)
        _ext(L, x - 0.10, 3.200, x - 0.25, 3.200)
    # baño (9)
    L.cota_h('cotas', [7.500, 8.600, 9.890], Y(8.22), 1.9, ext_desde=8.500)
    L.cota_v('cotas', [8.500, 8.957], X(9.05), 1.9, ext_desde=8.600)
    # cocina (10 a 13): desde el muro Norte, y desde P1 las del Sur
    L.cota_v('cotas', [7.200, 8.500, 9.008], X(1.60), 1.9, ext_desde=1.100)
    L.cota_v('cotas', [5.357, 5.900], X(1.60), 1.9)
    _ext(L, 0.550, 5.357, 1.60, 5.357)
    _ext(L, 1.100 + 0.085, 5.900, 1.60, 5.900)
    L.cota_v('cotas', [4.600, 4.759], X(1.60), 1.9)
    _ext(L, 0.550, 4.759, 1.60, 4.759)
    _ext(L, 1.100 + 0.085, 4.600, 1.60, 4.600)
    L.cota_h('cotas', [0.250, 1.100], Y(6.55), 1.9)
    # escaparate (18) y vestibulo (19)
    L.cota_h('cotas', [6.331, 7.300], Y(1.20), 1.9)
    _ext(L, 6.331, 1.000, 6.331, 1.20)
    _ext(L, 7.300, 0.950 + 0.10, 7.300, 1.20)
    L.cota_v('cotas', [0.419, 0.950], X(6.60), 1.9)
    _ext(L, 7.300 - 0.10, 0.950, 6.60, 0.950)
    L.cota_h('cotas', [8.900, 9.710], Y(0.72), 1.9)
    _ext(L, 8.900, 0.950 - 0.10, 8.900, 0.72)
    L.cota_v('cotas', [0.950, 1.429], X(8.65), 1.9)
    _ext(L, 8.900 - 0.10, 0.950, 8.65, 0.950)

    n_emp = sum(1 for l in E.LUCES_PB if l[3] == 'empotrado')
    avisos = [f'* {n}: {t}.' for n, t in sorted(E.AVISOS_LUCES.items())]
    marco(L, 'REPLANTEO DE LUCES', '05 / 05', 'Planta baja · huecos en el techo',
          ['Cada luz lleva su número, el mismo que en la lámina 01.',
           'Medidas en metros, al centro de cada luz, desde la cara',
           'sin revestir de la pared, del pilar o del borde del',
           'forjado; en el dibujo, en cadena por filas, y al pie,',
           'las dos de cada luz. El diámetro del hueco lo da la',
           'luminaria que se compre. Colgantes: punto de anclaje.',
           'La fila 4-5-6 va 2 cm al Norte de la cara Norte de P3.'] + avisos,
          [('luces', LUZ, 'Luz empotrada y colgante'),
           ('linea', '#8a8a8a', 'Borde del forjado del altillo'),
           ('linea', '#6a6a6a', 'Viga P1b y campana de la cocina'),
           ('linea', '#6f8a99', 'Cassette del aire acondicionado'),
           ('cota', COTA_COL, 'Cota de replanteo (m)'),
           (POCHE, TINTA, 'Muro de carga / medianera'),
           (POCHE_PIL, TINTA, 'Pilar, machón o montante'),
           (POCHE_TAB, TINTA, 'Pared en L y tabiquería'),
           (VIDRIO, '#3d6b80', 'Carpintería acristalada')],
          ('PUNTOS DE LUZ',
           [('Empotrados', f'{n_emp}'),
            ('Colgantes', f'{len(E.LUCES_PB) - n_emp}'),
            ('Total', f'{len(E.LUCES_PB)}')]),
          tabla=('TECHO DONDE VA CADA LUZ',
                 [('1 a 9 · bajo el altillo', '2,56 − canto'),
                  ('10 a 12 · cocina, pladur', '+2,31'),
                  ('13 a 18 · doble altura', '≈ +5,06'),
                  ('19 · vestíbulo, pladur', '+2,10')]))
    tabla_luces(L)
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
    exportar(replanteo_luces(), 'REPLANTEO_LUCES')
    import fitz
    doc = fitz.open()
    for f in (pb, pa):
        doc.insert_pdf(fitz.open(f))
    salida = os.path.join(AQUI, 'Planos_Estructura.pdf')
    doc.save(salida)
    print(f'  Planos_Estructura.pdf  ({doc.page_count} páginas)')
