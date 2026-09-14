# -*- coding: utf-8 -*-
"""
Lamina 03: equipamiento de barra y cocina.

Dos detalles a 1:25 sobre la misma hoja A3, cada uno con su propio origen de
coordenadas de obra pero dibujados en el mismo papel. La geometria de los
muros sale de `estructura.py` y los muebles de `equipamiento.py`.

    python3 build_equipamiento.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estructura as E
import equipamiento as Q
from dibujo import (Lienzo, TRAZO, TINTA, POCHE, POCHE_PIL, POCHE_TAB,
                    VIDRIO, COTA_COL)
from build_planos import (W, H, MARGEN, DEFS, marco, exportar, muros, pilares,
                          pared_l, ventanal_sur)

AQUI = os.path.dirname(os.path.abspath(__file__))

ESC25 = 40.0                      # mm de papel por metro · 1:25
MUEBLE = '#e7dfd2'                # mueble bajo
ENCIMERA = '#8d7f66'              # canto de la encimera corrida
APARATO = '#4a5a68'               # aparato sobre la encimera
FRIO = '#cfe0e8'                  # equipos refrigerados


# ------------------------------------------------------------- utilidades
def _fmt(v):
    return f'{v:.2f}'.replace('.', ',')


def recinto(L, x0, y0, x1, y1, titulo, sup):
    """Muros del recinto recortados del plano general, y su rotulo."""
    L.rect('fondo', x0, y0, x1, y1, '#ffffff', None)
    L.p_texto('rotulos', L.px((x0 + x1) / 2), L.py(y1) - 22.0, titulo, 4.0,
              'middle', TINTA, 'bold', espaciado='0.8')
    L.p_texto('rotulos', L.px((x0 + x1) / 2), L.py(y1) - 17.5,
              f'{_fmt(x1 - x0)} × {_fmt(y1 - y0)} m  ·  {sup}', 2.4, 'middle',
              '#666666')


def modulos(L, eje, fijo0, fijo1, arranque, lista, sentido=-1, relleno=MUEBLE,
            capa='muebles', tag_off=0.10):
    """Reparte modulos consecutivos a lo largo de un eje.

    eje 'y': los modulos se suceden en Y y ocupan de fijo0 a fijo1 en X.
    sentido -1 = hacia el Sur (o hacia el Oeste en el eje 'x').
    Devuelve la lista de (rotulo, nombre, largo, inicio, fin).
    """
    out, p = [], arranque
    for tag, nm, largo in lista:
        q = p + sentido * largo
        a, b = min(p, q), max(p, q)
        if eje == 'y':
            L.rect(capa, fijo0, a, fijo1, b, relleno, TINTA, 'medio')
            cx, cy, rot = fijo0 + tag_off, (a + b) / 2, -90
        else:
            L.rect(capa, a, fijo0, b, fijo1, relleno, TINTA, 'medio')
            cx, cy, rot = (a + b) / 2, fijo0 + tag_off, 0
        L.texto('rotulos', cx, cy, tag, 2.6, 'middle', TINTA, 'bold', dy=0.9,
                rot=rot)
        out.append((tag, nm, largo, a, b))
        p = q
    return out


def encimera(L, x0, y0, x1, y1, texto=None):
    """Canto de la encimera corrida, por encima de los modulos."""
    L.rect('encimera', x0, y0, x1, y1, 'none', ENCIMERA, 'corte')
    if texto:
        vert = (y1 - y0) > (x1 - x0)
        L.texto('rotulos', x1 - 0.30 if vert else (x0 + x1) / 2,
                y1 - 0.55 if vert else (y0 + y1) / 2, texto, 2.2, 'middle',
                ENCIMERA, 'bold', rot=-90 if vert else 0, dy=0.8)


def aparatos(L, eje, borde, arranque, lista, sentido=-1):
    """Aparatos sobre la encimera, con su propio fondo desde el borde."""
    for tag, nm, largo, fondo, off in lista:
        a = arranque + sentido * off
        b = a + sentido * largo
        lo, hi = min(a, b), max(a, b)
        if eje == 'y':
            L.rect('aparatos', borde, lo, borde + fondo, hi, '#ffffff', APARATO,
                   'medio')
            L.texto('rotulos', borde + fondo - 0.08, (lo + hi) / 2, tag, 2.4,
                    'middle', APARATO, 'bold', rot=-90, dy=0.8)
        else:
            L.rect('aparatos', lo, borde, hi, borde + fondo, '#ffffff', APARATO,
                   'medio')
            L.texto('rotulos', (lo + hi) / 2, borde + fondo - 0.08, tag, 2.4,
                    'middle', APARATO, 'bold', dy=0.8)


# =============================================================== detalles
def detalle_cocina(ox, oy):
    L = Lienzo(W, H, ESC25, ox, oy)
    for c in ('fondo', 'trama', 'muros', 'pilares', 'muebles', 'encimera',
              'aparatos', 'cotas', 'rotulos'):
        L.capa(c)
    c = Q.COCINA
    recinto(L, c['x0'], c['y0'], c['x1'], c['y1'], 'COCINA', '8,11 m²')

    muros(L)
    pared_l(L)
    pilares(L, solo=('P1', 'P1b'))

    # linea de coccion contra el muro Oeste
    cx0, cx1 = Q.COCCION_X
    cocc = modulos(L, 'y', cx0, cx1, Q.COCCION_Y0, Q.COCCION)
    encimera(L, cx0, c['y0'], cx1, c['y1'])
    ca = Q.CAMPANA
    L.rect('aparatos', ca['x0'], ca['y0'], ca['x1'], ca['y1'], 'none', APARATO,
           'fino', ' stroke-dasharray="2.4 1.4"')
    L.texto('rotulos', ca['x1'] - 0.10, (ca['y0'] + ca['y1']) / 2,
            f"CAMPANA  2,30  ·  bajo borde +{_fmt(Q.H_CAMPANA)}", 2.2, 'middle',
            APARATO, 'bold', rot=-90)

    # medianera Norte
    ny0, ny1 = Q.NORTE_Y
    nor = modulos(L, 'x', ny0, ny1, Q.NORTE_X0, Q.NORTE, sentido=+1)
    encimera(L, Q.NORTE_X0, ny0, c['x1'], ny1)

    # pared en L
    ex0, ex1 = Q.ESTE_X
    est = modulos(L, 'y', ex0, ex1, Q.ESTE_Y0, Q.ESTE, relleno=FRIO)
    encimera(L, ex0, c['y0'], ex1, Q.ESTE_Y0, 'ACERO INOX.')
    aparatos(L, 'y', ex0, Q.ESTE_Y0, Q.ESTE_SOBRE)

    # pasillo de trabajo
    px0, px1 = cx1, ex0
    ym = (c['y0'] + Q.ESTE_Y0) / 2
    L.linea('cotas', px0, ym, px1, ym, COTA_COL, 'cota')
    L.texto('rotulos', (px0 + px1) / 2, ym,
            f'PASILLO DE TRABAJO  {_fmt(Q.PASILLO_COCINA)}', 2.2, 'middle',
            COTA_COL, 'bold', dy=-1.6)

    # cotas
    L.cota_v('cotas', [c['y0']] + [b for *_, a, b in cocc][::-1] + [c['y1']],
             L.px(c['x0']) - 7.0, 1.9, ext_desde=c['x0'])
    L.cota_h('cotas', [Q.NORTE_X0] + [b for *_, a, b in nor] + [c['x1']],
             L.py(c['y1']) - 13.5, 1.9, ext_desde=c['y1'])
    L.cota_v('cotas', [Q.ESTE_Y0] + [a for *_, a, b in est] + [c['y0']],
             L.px(c['x1']) + 7.0, 1.9, ext_desde=c['x1'])
    L.cota_h('cotas', [c['x0'], cx1, ex0, c['x1']], L.py(c['y0']) + 8.0, 1.9,
             ext_desde=c['y0'])
    return L, cocc + nor + est


def detalle_barra(ox, oy):
    L = Lienzo(W, H, ESC25, ox, oy)
    for c in ('fondo', 'trama', 'muros', 'pilares', 'carpinteria', 'muebles',
              'encimera', 'aparatos', 'cotas', 'rotulos'):
        L.capa(c)
    b = Q.BARRA
    recinto(L, b['x0'], b['y0'], b['x1'], b['y1'], 'BARRA', '2,75 + 3,40 m de mueble')

    muros(L)
    pared_l(L)
    pilares(L, solo=('P1', 'P1b', 'P2'))
    ventanal_sur(L)

    # trasbarra: un solo mueble con una sola encimera
    tx0, tx1 = Q.TRASBARRA_X
    ty0, ty1 = Q.TRASBARRA_Y
    tras = modulos(L, 'y', tx0, tx1, ty1, Q.TRASBARRA_BAJO)
    encimera(L, tx0, ty0, tx1, ty1, 'ENCIMERA ÚNICA')
    aparatos(L, 'y', tx0, ty1, Q.TRASBARRA_SOBRE)

    # mostrador delantero
    mx0, mx1 = Q.MOSTRADOR_X
    most = modulos(L, 'y', mx0, mx1, Q.MOSTRADOR_Y, Q.MOSTRADOR, sentido=+1)
    encimera(L, mx0, Q.MOSTRADOR_Y, mx1, Q.MOSTRADOR_Y + 3.400)

    ym = (ty0 + ty1) / 2
    L.linea('cotas', tx1, ym, mx0, ym, COTA_COL, 'cota')
    L.texto('rotulos', (tx1 + mx0) / 2, ym,
            f'PASO DE SERVICIO  {_fmt(Q.PASILLO_BARRA)}', 2.2, 'middle',
            COTA_COL, 'bold', rot=-90, dx=-1.4)

    L.cota_v('cotas', [ty0] + [a for *_, a, bb in tras] + [ty1],
             L.px(b['x0']) - 7.0, 1.9, ext_desde=b['x0'])
    L.cota_v('cotas', [Q.MOSTRADOR_Y] + [bb for *_, a, bb in most],
             L.px(b['x1']) + 7.0, 1.9, ext_desde=b['x1'])
    L.cota_h('cotas', [b['x0'], tx1, mx0, mx1], L.py(b['y0']) + 8.0, 1.9,
             ext_desde=b['y0'])
    return L, tras + most


def cuadro_equipos(L, lista, x0=14.0, x1=W - 8.0 - 96.0 - 4.0, y0=222.0):
    """Cuadro de equipamiento al pie del area de dibujo, en tres columnas."""
    filas = [(t, n, la) for t, n, la, *_ in lista] + \
            [(t, n, la) for t, n, la, f, o in Q.TRASBARRA_SOBRE + Q.ESTE_SOBRE]
    L.p_rect('rotulos', x0, y0, x1, 287.0, '#fbfaf7', '#cfc6b6', 'fino')
    L.p_texto('rotulos', x0 + 4, y0 + 5.2, 'EQUIPAMIENTO', 2.6, 'start', TINTA,
              'bold', espaciado='0.6')
    L.p_texto('rotulos', x0 + 38, y0 + 5.2,
              'Ancho en metros. Serie de hostelería, pendiente de sustituir '
              'por el del equipo que se elija.', 2.0, 'start', '#7a6a4a')
    L.p_linea('rotulos', x0 + 4, y0 + 7.0, x1 - 4, y0 + 7.0, '#cfc6b6', 'cota')

    ncol = 3
    porcol = -(-len(filas) // ncol)
    ancho = (x1 - x0 - 8.0) / ncol
    for i, (t, n, la) in enumerate(filas):
        col, fila = divmod(i, porcol)
        cx = x0 + 4 + col * ancho
        cy = y0 + 11.6 + fila * 4.0
        L.p_texto('rotulos', cx, cy, t, 2.1, 'start', APARATO, 'bold')
        L.p_texto('rotulos', cx + 9.5, cy, n[:52], 2.1, 'start', '#333333')
        L.p_texto('rotulos', cx + ancho - 6.0, cy, _fmt(la), 2.1, 'end', TINTA,
                  'bold')


# ================================================================== hoja
def lamina():
    L = Lienzo(W, H, 1.0, 0.0, 0.0)
    for c in ('hoja', 'fondo', 'trama', 'muros', 'pilares', 'carpinteria',
              'muebles', 'encimera', 'aparatos', 'cotas', 'rotulos', 'cajetin'):
        L.capa(c)

    # Cada detalle lleva su propio origen de obra y se recorta a su caja de
    # papel: si no, los muros del resto del local se salen por toda la hoja.
    K, lk = detalle_cocina(ox=24.0, oy=52.0 + 9.008 * ESC25)
    B, lb = detalle_barra(ox=170.0, oy=52.0 + 5.183 * ESC25)
    L.absorber(K, clip=(13.0, 26.0, 142.0, 217.0))
    L.absorber(B, clip=(160.0, 26.0, 292.0, 210.0))
    cuadro_equipos(L, lk + lb)

    marco(L, 'EQUIPAMIENTO', '03 / 03', 'Barra y cocina · distribución',
          ['Anchos de serie de hostelería, no medidos sobre',
           'aparato. Sustituir por los del equipo que se elija.',
           'La línea de cocción va en serie 600 y no en 700:',
           'con 2,12 m libres, un fondo de 700 dejaría el',
           'pasillo en 0,82 m, bajo el mínimo recomendado.',
           'La trasbarra es un solo mueble con una sola',
           'encimera corrida; el módulo técnico T1 queda',
           'bajo la cafetera.',
           'No hace falta cerrar la zona del ventanal: todo',
           'entra en los 2,75 m de trasbarra.'],
          [(MUEBLE, TINTA, 'Mueble bajo encimera'),
           (FRIO, TINTA, 'Equipo refrigerado'),
           ('none', ENCIMERA, 'Encimera corrida'),
           ('none', APARATO, 'Aparato sobre encimera'),
           (POCHE, TINTA, 'Muro de carga / medianera'),
           (POCHE_PIL, TINTA, 'Pilar o machón')],
          ('HOLGURAS Y ALTURAS',
           [('Pasillo de trabajo en cocina', f'{_fmt(Q.PASILLO_COCINA)} m'),
            ('Paso de servicio en barra', f'{_fmt(Q.PASILLO_BARRA)} m'),
            ('Fondo de todos los muebles', '0,60 m'),
            ('Altura de encimera', '0,90 m'),
            ('Borde inferior de la campana', '2,00 m')]),
          tabla=('', []), esc_dibujo=ESC25, esc_txt='1:25  (A3)')
    return L


if __name__ == '__main__':
    import build_planos
    print('Generando las tres láminas...')
    pb = exportar(build_planos.planta_baja(), 'PLANTA_BAJA')
    pa = exportar(build_planos.planta_alta(), 'PLANTA_ALTA')
    eq = exportar(lamina(), 'EQUIPAMIENTO')
    import pymupdf
    for nombre, hojas in (('Planos_Estructura.pdf', (pb, pa)),
                          ('Planos_Completos.pdf', (pb, pa, eq))):
        doc = pymupdf.open()
        for f in hojas:
            doc.insert_pdf(pymupdf.open(f))
        doc.save(os.path.join(AQUI, nombre))
        print(f'  {nombre}  ({doc.page_count} páginas)')
