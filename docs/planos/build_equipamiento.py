# -*- coding: utf-8 -*-
"""
Laminas 03 y 04: equipamiento de barra y cocina con productos reales de
Makro, y la lista de compra con enlaces clicables.

Dos detalles a 1:25 sobre la misma hoja A3, cada uno con su propio origen de
coordenadas de obra y recortado a su caja de papel. La geometria de los
muros sale de `estructura.py` y los aparatos de `equipamiento.py`.

    python3 build_equipamiento.py      # genera las cuatro laminas y los PDF
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estructura as E
import equipamiento as Q
from dibujo import (Lienzo, TRAZO, TINTA, POCHE, POCHE_PIL, POCHE_TAB,
                    VIDRIO, COTA_COL)
from build_planos import (W, H, MARGEN, CAJ_X, DEFS, marco, exportar, muros,
                          pilares, pared_l, ventanal_sur, viga, hundimiento,
                          zocalo_sur)
import lista_makro as LM

AQUI = os.path.dirname(os.path.abspath(__file__))

ESC25 = 40.0                      # mm de papel por metro · 1:25
MUEBLE = '#e7dfd2'                # bancada o mueble bajo
ENCIMERA = '#8d7f66'              # canto de la encimera corrida
APARATO = '#4a5a68'               # aparato
FRIO = '#cfe0e8'                  # equipos refrigerados
MADERA = '#c9a674'                # tabla de madera


def _fmt(v):
    return f'{v:.2f}'.replace('.', ',')


def rotulo(L, x0, y0, x1, y1, titulo, sub):
    L.rect('fondo', x0, y0, x1, y1, '#ffffff', None)
    L.p_texto('rotulos', L.px((x0 + x1) / 2), L.py(y1) - 22.0, titulo, 4.0,
              'middle', TINTA, 'bold', espaciado='0.8')
    L.p_texto('rotulos', L.px((x0 + x1) / 2), L.py(y1) - 17.5, sub, 2.4,
              'middle', '#666666')


def caja(L, x0, y0, x1, y1, tag, relleno='#ffffff', color=APARATO, capa='aparatos',
         rot=0, dash=False, tam=2.4, tx=None, ty=None):
    """Un aparato o mueble como rectangulo con su rotulo centrado (o en tx, ty)."""
    ex = ' stroke-dasharray="1.6 1.0"' if dash else ''
    L.rect(capa, x0, y0, x1, y1, relleno, color, 'medio', ex)
    L.texto('rotulos', (x0 + x1) / 2 if tx is None else tx,
            (y0 + y1) / 2 if ty is None else ty, tag, tam, 'middle', color,
            'bold', dy=0.8, rot=rot)


# =============================================================== COCINA
def detalle_cocina(ox, oy):
    L = Lienzo(W, H, ESC25, ox, oy)
    for c in ('fondo', 'trama', 'muros', 'pilares', 'proyeccion', 'muebles',
              'encimera', 'aparatos', 'cotas', 'rotulos'):
        L.capa(c)
    c = Q.COCINA
    rotulo(L, c['x0'], c['y0'], c['x1'], Q.NICHO['y1'], 'COCINA',
           f"{_fmt(c['x1']-c['x0'])} × {_fmt(c['y1']-c['y0'])} m  ·  hundimiento de "
           f"0,275 al Norte  ·  entrada bajo la viga P1b")
    muros(L); hundimiento(L); pared_l(L); pilares(L, solo=('P1',)); viga(L)

    # --- linea de coccion: bancada a medida y aparatos de Oeste a Este
    b = Q.BANCADA_COCCION
    L.rect('muebles', b['x0'], b['y0'], b['x1'], b['y1'], MUEBLE, TINTA, 'medio')
    x = Q.COCCION_X0
    cortes = [x]
    for p in Q.COCCION:
        caja(L, x, b['y1'] - p['f'], x + p['a'], b['y1'], p['tag'])
        x += p['a']; cortes.append(x)
    L.texto('rotulos', (b['x0'] + b['x1']) / 2, b['y0'] + 0.025,
            'bancada de apoyo a medida  ·  '
            f"{_fmt(b['x1'] - b['x0'])} × {_fmt(b['y1'] - b['y0'])}  ·  en el hundimiento",
            1.5, 'middle', ENCIMERA, 'bold', dy=0.5)
    cp = Q.CAMPANA_POS
    L.rect('proyeccion', cp['x0'], cp['y0'], cp['x1'], cp['y1'], 'none', APARATO,
           'fino', ' stroke-dasharray="2.4 1.4"')
    L.texto('rotulos', 1.35, 8.35, 'CAMPANA 2,00 × 1,20', 1.8, 'middle', APARATO,
            'bold')
    L.texto('rotulos', 1.35, 8.35, f'borde inferior +{_fmt(Q.H_CAMPANA)}', 1.6,
            'middle', APARATO, dy=2.2)

    # --- muro Oeste, de Norte a Sur
    y = Q.OESTE_Y0
    cortes_o = [y]
    for p in Q.OESTE:
        frio = p['tag'] in ('K8', 'K9')
        if p['tag'] == 'K7':
            # fregadero con hueco: cuba al Sur (rotulo dentro de la cuba) y
            # escurridor al Norte con el lavavajillas debajo
            caja(L, Q.OESTE_X0, y - p['a'], Q.OESTE_X0 + p['f'], y, p['tag'],
                 rot=-90, tx=Q.OESTE_X0 + p['f'] / 2,
                 ty=y - Q.HUECO_LAV - (p['a'] - Q.HUECO_LAV) / 2)
            cu = Q.CUBA
            cy0 = y - Q.HUECO_LAV - (p['a'] - Q.HUECO_LAV + cu['largo']) / 2
            cx0 = Q.OESTE_X0 + (p['f'] - cu['fondo']) / 2
            L.rect('aparatos', cx0, cy0, cx0 + cu['fondo'], cy0 + cu['largo'], 'none',
                   APARATO, 'fino', ' rx="0.8"')
            L.linea('aparatos', Q.OESTE_X0, y - Q.HUECO_LAV, Q.OESTE_X0 + p['f'],
                    y - Q.HUECO_LAV, APARATO, 'fino', ' stroke-dasharray="1.2 0.9"')
            lv = Q.LAVAVAJILLAS
            ly1 = y - (Q.HUECO_LAV - lv['a']) / 2
            caja(L, Q.OESTE_X0, ly1 - lv['a'], Q.OESTE_X0 + lv['f'], ly1, lv['tag'],
                 dash=True, tam=2.0, rot=-90)
            L.texto('rotulos', Q.OESTE_X0 + lv['f'] + 0.05, y - Q.HUECO_LAV / 2,
                    'mesada del fregadero · K6 debajo', 1.5, 'start', APARATO, 'bold', dy=0.5)
            L.texto('rotulos', Q.OESTE_X0 + p['f'] + 0.05, cy0 + cu['largo'] / 2,
                    'cuba', 1.5, 'start', APARATO, dy=0.5)
        else:
            caja(L, Q.OESTE_X0, y - p['a'], Q.OESTE_X0 + p['f'], y, p['tag'],
                 FRIO if frio else '#ffffff', APARATO if not frio else '#3d5c6e', rot=-90)
        y -= p['a']; cortes_o.append(y)

    # --- pared en L: nevera corrida de acero como mesada, de una sola pieza
    y = Q.ESTE_Y0
    cortes_e = [y]
    fondo_e = Q.ESTE[0]['f']
    for p in Q.ESTE:
        caja(L, Q.ESTE_X1 - p['f'], y - p['a'], Q.ESTE_X1, y, p['tag'], FRIO,
             '#3d5c6e', rot=-90)
        y -= p['a']; cortes_e.append(y)
    L.rect('encimera', Q.ESTE_X1 - fondo_e, y, Q.ESTE_X1, Q.ESTE_Y0, 'none', ENCIMERA,
           'corte')
    L.texto('rotulos', Q.ESTE_X1 - fondo_e + 0.07, (y + Q.ESTE_Y0) / 2,
            f'MESA REFRIGERADA DE UNA PIEZA  {_fmt(Q.ESTE_Y0 - y)} × {_fmt(fondo_e)}  ·  '
            'MESADA · puertas debajo', 1.7, 'middle', ENCIMERA, 'bold', rot=-90)
    # hueco libre entre la mesada y la bancada de coccion
    L.texto('rotulos', Q.ESTE_X1 - fondo_e / 2, (Q.ESTE_Y0 + Q.BANCADA_COCCION['y0']) / 2,
            f'libre {_fmt(Q.LIBRE_ESTE)}', 1.5, 'middle', ENCIMERA, rot=-90, dy=0.5)

    # --- pasillo (acotado en el punto mas estrecho: frente a los frigorificos)
    #     y entrada
    y_p = 6.20
    yy = Q.OESTE_Y0
    fondo_o = Q.OESTE[0]['f']
    for p in Q.OESTE:
        if yy - p['a'] <= y_p <= yy:
            fondo_o = p['f']
        yy -= p['a']
    L.linea('cotas', Q.OESTE_X0 + fondo_o, y_p, Q.ESTE_X1 - fondo_e, y_p, COTA_COL,
            'cota')
    L.texto('rotulos', (Q.OESTE_X0 + fondo_o + Q.ESTE_X1 - fondo_e) / 2, y_p,
            f'PASILLO  {_fmt(Q.PASILLO_COCINA_MIN)} – {_fmt(Q.PASILLO_COCINA)}',
            2.0, 'middle', COTA_COL, 'bold', dy=-1.4)

    # --- cotas
    L.cota_h('cotas', cortes + [Q.NICHO['x1']], L.py(Q.NICHO['y1']) - 13.5, 1.8,
             ext_desde=Q.NICHO['y1'])
    L.cota_v('cotas', cortes_o, L.px(c['x0']) - 7.0, 1.8, ext_desde=c['x0'])
    L.cota_v('cotas', [Q.BANCADA_COCCION['y0']] + cortes_e + [c['y0']],
             L.px(c['x1']) + 7.0, 1.8, ext_desde=c['x1'])
    L.cota_h('cotas', [0.550, E.PARED_L_DOB[1], c['x1']],
             L.py(c['y0']) + 37.0, 1.8, ext_desde=c['y0'])
    return L


# ================================================================ BARRA
def detalle_barra(ox, oy):
    L = Lienzo(W, H, ESC25, ox, oy)
    for c in ('fondo', 'trama', 'muros', 'pilares', 'proyeccion', 'carpinteria',
              'muebles', 'encimera', 'aparatos', 'cotas', 'rotulos'):
        L.capa(c)
    b = Q.BARRA
    rotulo(L, b['x0'], b['y0'], b['x1'], b['y1'], 'BARRA',
           f"trasbarra {_fmt(Q.TRASBARRA_Y[1] - Q.TRASBARRA_Y[0])} entre P1 y P2  ·  "
           f"mostrador {_fmt(Q.MOSTRADOR_Y[1] - Q.MOSTRADOR_Y[0])}  ·  paso de personal 0,95")
    muros(L); pared_l(L); pilares(L, solo=('P1', 'P2')); viga(L); ventanal_sur(L)
    zocalo_sur(L)

    # --- trasbarra: mesada corrida de 0,60 entre P1 y P2 (encargo 19 set.)
    tx0, tx1 = Q.TRASBARRA_X
    ty0, ty1 = Q.TRASBARRA_Y
    L.rect('muebles', tx0, ty0, tx1, ty1, MUEBLE, TINTA, 'medio')
    pos = dict((t, (y0, y1)) for t, y0, y1 in Q.trasbarra_pos())
    for p in Q.TRASBARRA + [Q.FREGADERO_BARRA]:
        y0, y1 = pos[p['tag']]
        fuera = (y1 - y0) < 0.30      # los huecos estrechos no admiten rotulo dentro
        caja(L, tx0, y0, tx0 + min(p['f'], Q.MESADA_FONDO), y1, p['tag'], rot=-90,
             tam=1.9 if fuera else 2.2,
             tx=tx1 + 0.09 if fuera else None, ty=(y0 + y1) / 2 if fuera else None)
    # nevera inox bajo el hueco libre de mesada
    nv, np_ = Q.NEVERA_BARRA, Q.NEVERA_POS
    caja(L, tx0, np_['y0'], tx0 + nv['f'], np_['y1'], nv['tag'], 'none', '#3d5c6e',
         dash=True, tam=2.2, rot=-90, tx=tx0 + nv['f'] - 0.12)
    # hueco libre de mesada entre la granizadora y el fregadero
    hy0, hy1 = pos['A4'][1], pos['A3'][0]
    L.texto('rotulos', tx1 - 0.14, (hy0 + hy1) / 2,
            f'libre {_fmt(hy1 - hy0)}', 1.6, 'middle', ENCIMERA, 'bold', rot=-90)
    # encimera corrida: llega hasta el fregadero A4, que es de pie y
    # sustituye ese tramo de mesada
    y_enc0 = pos['A4'][1]
    L.rect('encimera', tx0, y_enc0, tx1, ty1, 'none', ENCIMERA, 'corte')
    es = Q.ESTANTE
    ey1 = ty1 - (ty1 - ty0 - Q.ESTANTE_LARGO) / 2
    L.rect('proyeccion', tx0, ey1 - Q.ESTANTE_LARGO, tx0 + es['f'], ey1, 'none',
           ENCIMERA, 'fino', ' stroke-dasharray="2.4 1.4"')
    for k in range(1, Q.ESTANTE_N):
        yk = ey1 - es['a'] * k
        L.linea('proyeccion', tx0, yk, tx0 + es['f'], yk, ENCIMERA, 'fino',
                ' stroke-dasharray="1.2 0.9"')
    L.texto('rotulos', tx0 + 0.08, ty1 - 0.50,
            f"A6 ESTANTE  {Q.ESTANTE_N} × {_fmt(es['a'])} × {_fmt(es['f'])}", 1.6,
            'middle', ENCIMERA, 'bold', rot=-90)
    L.texto('rotulos', tx1 + 0.06, ty1 - 0.52,
            f"MESADA A MEDIDA  {_fmt(ty1 - y_enc0)} × {_fmt(Q.MESADA_FONDO)}", 1.9,
            'middle', ENCIMERA, 'bold', rot=-90)

    # --- mostrador delantero: vitrinas y tabla de madera
    mx0, mx1 = Q.MOSTRADOR_X
    my0, my1 = Q.MOSTRADOR_Y
    v = Q.VITRINA
    y = my0
    cortes_m = [y]
    for p in Q.VITRINAS:
        caja(L, mx0, y, mx0 + v['fondo_cristal'], y + p['a'], p['tag'], FRIO,
             '#3d5c6e', tam=2.2, tx=mx0 + 0.20, ty=y + 0.16)
        mw, md = v['motor']
        L.rect('aparatos', mx0 + v['fondo_cristal'] - md, y, mx0 + v['fondo_cristal'],
               y + mw, 'none', '#3d5c6e', 'fino', ' stroke-dasharray="1.2 0.9"')
        L.texto('rotulos', mx0 + v['fondo_cristal'] - md / 2, y + mw / 2, 'motor', 1.4,
                'middle', '#3d5c6e', rot=-90, dy=0.5)
        y += p['a']; cortes_m.append(y)
    # bajo V2 sigue el lavavasos; los barriles se van a la tabla de P2
    lv = Q.LAVAVASOS
    caja(L, mx0 + 0.05, my0 + 0.34, mx0 + 0.05 + lv['f'], my0 + 0.34 + lv['a'],
         lv['tag'], '#ffffff', APARATO, dash=True, tam=1.8, rot=-90)
    bm = Q.BARRA_MADERA
    L.rect('muebles', mx0, bm['y0'], mx1, bm['y1'], MADERA, '#6b4f2a', 'medio')
    L.texto('rotulos', mx0 + 0.05, (bm['y0'] + bm['y1']) / 2,
            f"BARRA DE MADERA  {_fmt(bm['y1'] - bm['y0'])}", 1.7, 'middle', '#6b4f2a',
            'bold', rot=-90, dy=0.6)
    # en el mostrador solo queda la tablet de cobro (encargo 19 set.)
    tb = Q.TABLET
    caja(L, mx0 + 0.18, bm['y1'] - 0.06 - tb['a'], mx0 + 0.18 + tb['f'],
         bm['y1'] - 0.06, 'B3', tam=1.6)
    # tabla de P2: chopera encima y barril debajo
    t = Q.TABLA_P2
    ch = Q.CHOPERA
    L.rect('muebles', t['x0'], t['y0'], t['x1'], t['y1'], MADERA, '#6b4f2a', 'medio')
    L.texto('rotulos', 1.30, t['y1'] + 0.13,
            f"TABLA DE P2  {_fmt(t['x1'] - t['x0'])} × {_fmt(t['y1'] - t['y0'])}",
            1.6, 'middle', '#6b4f2a', 'bold')
    L.texto('rotulos', 1.30, t['y1'] + 0.13, 'chopera B4 encima · barril B2 debajo',
            1.5, 'middle', '#6b4f2a', dy=2.4)
    caja(L, t['x1'] - 0.03 - ch['a'], t['y0'] + 0.005, t['x1'] - 0.03,
         t['y0'] + 0.005 + ch['f'], 'B4', tam=1.8)
    L.circulo('aparatos', t['x0'] + 0.20, (t['y0'] + t['y1']) / 2, 0.16, 'none',
              APARATO, 'fino', ' stroke-dasharray="1.2 0.9"')
    L.texto('rotulos', t['x0'] + 0.20, (t['y0'] + t['y1']) / 2, 'B2', 1.8, 'middle',
            APARATO, 'bold', dy=0.6)

    # --- paso de servicio
    ym = (ty0 + ty1) / 2
    L.linea('cotas', tx1, ym, mx0, ym, COTA_COL, 'cota')
    L.texto('rotulos', (tx1 + mx0) / 2, ym, f'PASO DE SERVICIO  {_fmt(Q.PASILLO_BARRA)}',
            2.0, 'middle', COTA_COL, 'bold', rot=-90, dx=-1.4)

    cortes_t = [ty1, pos['A4'][1]] + [y0 for _t, y0, _y1 in Q.trasbarra_pos()]
    L.cota_v('cotas', sorted(set(cortes_t + [ty0])), L.px(b['x0']) - 7.0, 1.8,
             ext_desde=b['x0'])
    L.cota_v('cotas', cortes_m + [bm['y1'], E.PARED_L_LAR[2]], L.px(b['x1']) + 7.0, 1.8,
             ext_desde=b['x1'])
    L.cota_h('cotas', [b['x0'], tx1, mx0, mx0 + v['fondo_cristal'], mx1],
             L.py(b['y0']) + 9.0, 1.8, ext_desde=b['y0'])
    return L


# ================================================================ hoja
def cuadro_equipos(L, x0=14.0, x1=W - 8.0 - 96.0 - 4.0, y0=235.0):
    filas = Q.todos()
    L.p_rect('rotulos', x0, y0, x1, 287.0, '#fbfaf7', '#cfc6b6', 'fino')
    L.p_texto('rotulos', x0 + 4, y0 + 5.2, 'EQUIPAMIENTO  ·  MAKRO', 2.6, 'start',
              TINTA, 'bold', espaciado='0.6')
    L.p_texto('rotulos', x0 + 52, y0 + 5.2,
              'Ancho × fondo × alto en metros, de la ficha de makro.es. Vitrinas y '
              'cafetera ya compradas. Tablet y barriles con medida promedio. Enlaces en la lámina 04.',
              1.9, 'start', '#7a6a4a')
    L.p_linea('rotulos', x0 + 4, y0 + 7.0, x1 - 4, y0 + 7.0, '#cfc6b6', 'cota')
    ncol = 2
    porcol = -(-len(filas) // ncol)
    ancho = (x1 - x0 - 8.0) / ncol
    for i, p in enumerate(filas):
        col, fila = divmod(i, porcol)
        cx = x0 + 4 + col * ancho
        cy = y0 + 11.0 + fila * 3.5
        L.p_texto('rotulos', cx, cy, p['tag'], 2.0, 'start', APARATO, 'bold')
        L.p_texto('rotulos', cx + 8.5, cy, p['nombre'][:78], 1.9, 'start', '#333333')
        L.p_texto('rotulos', cx + ancho - 6.0, cy,
                  f"{_fmt(p['a'])} × {_fmt(p['f'])} × {_fmt(p['h'])}", 1.9, 'end',
                  TINTA, 'bold')


def lamina():
    L = Lienzo(W, H, 1.0, 0.0, 0.0)
    for c in ('hoja', 'fondo', 'trama', 'muros', 'pilares', 'proyeccion',
              'carpinteria', 'muebles', 'encimera', 'aparatos', 'cotas', 'rotulos',
              'cajetin'):
        L.capa(c)
    K = detalle_cocina(ox=24.0, oy=52.0 + Q.NICHO['y1'] * ESC25)
    B = detalle_barra(ox=170.0, oy=52.0 + Q.BARRA['y1'] * ESC25)
    L.absorber(K, clip=(13.0, 26.0, 142.0, 232.0))
    L.absorber(B, clip=(160.0, 26.0, 292.0, 232.0))
    cuadro_equipos(L)

    marco(L, 'EQUIPAMIENTO', '03 / 04', 'Barra y cocina · productos Makro',
          ['Cada máquina es un producto real de makro.es con',
           'sus medidas de ficha; la web bloquea el acceso',
           'directo, así que las medidas vienen de su buscador.',
           'Confirmar en la ficha antes de comprar.',
           'Cocción y campana metidas en el hundimiento de 0,275',
           'de la medianera Norte, como pidió el cliente.',
           'Mesada refrigerada de una sola pieza (2,54, la más',
           f"larga de Makro) pegada al doblez de la L; {_fmt(Q.LIBRE_ESTE)} libres",
           'junto a la cocción. K6 bajo el escurridor de K7.',
           f'Pasillo de cocina de {_fmt(Q.PASILLO_COCINA_MIN)} a {_fmt(Q.PASILLO_COCINA)}. Muro Oeste:',
           f"{_fmt(Q.SUMA_OESTE)} de aparatos en los {_fmt(Q.LARGO_OESTE)} que hay hasta P1.",
           'Trasbarra nueva del 19 set.: mesada corrida de 0,60',
           'entre P1 y P2, con estante encima; la nevera A5 va',
           'bajo el hueco libre y nada bajo el fregadero A4.',
           'Alturas por confirmar: A4 y A5 miden 0,85 y la',
           'encimera va a 0,90, con 5 cm de desnivel en A4 y 1-2',
           'de holgura sobre A5. La altura libre que pide A3 para',
           'llenar la cuba no consta: medirla antes de colgar A6.'],
          [(MUEBLE, TINTA, 'Bancada o mueble bajo'),
           (FRIO, '#3d5c6e', 'Equipo refrigerado'),
           ('none', ENCIMERA, 'Encimera o tabla corrida'),
           ('none', APARATO, 'Aparato (trazos: bajo encimera)'),
           (MADERA, '#6b4f2a', 'Tabla de madera'),
           (POCHE, TINTA, 'Muro de carga / medianera')],
          ('HOLGURAS Y ALTURAS',
           [('Pasillo de cocina, mínimo', f'{_fmt(Q.PASILLO_COCINA_MIN)} m'),
            ('Paso de servicio en barra', f'{_fmt(Q.PASILLO_BARRA)} m'),
            ('Entrada a la cocina, bajo la viga',
             f"{_fmt(E.PARED_L_DOB[1] - 0.550)} m"),
            ('Hueco libre de mesada en barra', f'{_fmt(Q.libre_trasbarra())} m'),
            ('Altura de encimera', '0,90 m'),
            ('Borde inferior de la campana', '2,00 m')]),
          tabla=('', []), esc_dibujo=ESC25, esc_txt='1:25  (A3)')
    return L


# ======================================================= LAMINA 04: LISTA
ENLACE = '#1f4e79'                # color de los enlaces clicables


def lamina_lista():
    """Lamina 04: toda la maquinaria con su ficha de makro.es. Devuelve el
    lienzo y la lista de zonas de enlace (mm de papel + url) para el PDF."""
    L = Lienzo(W, H, 1.0, 0.0, 0.0)
    for c in ('hoja', 'fondo', 'rotulos', 'cajetin'):
        L.capa(c)
    enlaces = []
    x0, x1 = 14.0, CAJ_X - 6.0
    c_tag, c_nom, c_med, c_ubi, c_url = x0, x0 + 14.0, x0 + 98.0, x0 + 118.0, x0 + 206.0
    paso = 3.70

    L.p_texto('rotulos', x0, 36.0, 'LISTA DE EQUIPAMIENTO  ·  MAKRO', 4.2, 'start',
              TINTA, 'bold', espaciado='0.8')
    L.p_texto('rotulos', x0, 41.8,
              'Todo lo que hay que comprar para la barra y la cocina, con la ficha de '
              'makro.es de cada producto. Medidas en metros, ancho × fondo × alto. '
              'Los enlaces de la última columna son clicables en el PDF.',
              2.3, 'start', '#666666')

    def seccion(y, titulo):
        L.p_texto('rotulos', x0, y, titulo, 2.7, 'start', TINTA, 'bold', espaciado='0.5')
        return y + 5.6

    def cabecera(y, primera='RÓTULO'):
        for cx, t in ((c_tag, primera), (c_nom, 'PRODUCTO'), (c_med, 'MEDIDAS'),
                      (c_ubi, 'DÓNDE VA'), (c_url, 'FICHA EN MAKRO.ES')):
            L.p_texto('rotulos', cx, y, t, 1.9, 'start', '#7a6a4a', 'bold')
        L.p_linea('rotulos', x0, y + 1.4, x1, y + 1.4, '#cfc6b6', 'cota')
        return y + paso + 0.6

    def fila(y, i, p, tag=None):
        if i % 2 == 0:
            L.p_rect('fondo', x0 - 1.5, y - 3.4, x1, y + 1.3, '#f7f4ee', None)
        L.p_texto('rotulos', c_tag, y, tag or p['tag'], 2.1, 'start', APARATO, 'bold')
        L.p_texto('rotulos', c_nom, y, p['nombre'], 2.1, 'start', '#222222')
        L.p_texto('rotulos', c_med, y, f"{_fmt(p['a'])} × {_fmt(p['f'])} × {_fmt(p['h'])}",
                  2.1, 'start', TINTA, 'bold')
        L.p_texto('rotulos', c_ubi, y, LM.donde(p), 2.1, 'start', '#444444')
        if p.get('url'):
            L.p_texto('rotulos', c_url, y, p['url'], 2.0, 'start', ENLACE)
            enlaces.append((c_url - 1.0, y - 2.8, x1, y + 1.1, p['url']))
        else:
            L.p_texto('rotulos', c_url, y, 'ya comprado / medida promedio, sin ficha', 2.0,
                      'start', '#8a8a8a')
        return y + paso

    y = seccion(48.0, 'EQUIPOS DIBUJADOS EN LAS LÁMINAS 01 Y 03')
    y = cabecera(y)
    for i, p in enumerate(Q.todos()):
        y = fila(y, i, p)

    y = seccion(y + 4.0, 'ALTERNATIVAS CON LA MISMA FUNCIÓN  ·  no dibujadas')
    y = cabecera(y, 'SUSTITUYE')
    for i, p in enumerate(Q.ESTE_ALT + Q.OESTE_ALT + Q.ALT_BARRA):
        y = fila(y, i, p, tag=p['tag'].replace(' alt', ''))

    y = seccion(y + 4.0, 'SIN SITIO EN LA TRASBARRA NUEVA  ·  decidir dónde van')
    y = cabecera(y, 'ERA')
    for i, p in enumerate(Q.SIN_SITIO):
        y = fila(y, i, p, tag=p['tag'].replace(' ant.', ''))

    y = seccion(y + 4.0, 'A MEDIDA  ·  no se compran en Makro')
    for t in LM.A_MEDIDA:
        L.p_texto('rotulos', c_nom, y, '·  ' + t, 2.0, 'start', '#222222')
        y += 3.5

    y = seccion(y + 3.0, 'VERIFICACIÓN DE LOS ENLACES')
    for t in ('makro.es responde 403 a cualquier acceso desde un servidor, así que las fichas no se pueden '
              'abrir desde el entorno de trabajo. Cada enlace se verificó buscando su identificador con el',
              'buscador restringido a makro.es: todos devuelven su URL con el título del producto '
              '(LISTA_MAKRO.md). La del fregadero K7 la facilitó el cliente. Confirmar precio y stock.'):
        L.p_texto('rotulos', c_nom, y, t, 2.0, 'start', '#444444')
        y += 3.7

    n_fichas = len({p['url'] for p in Q.todos() if p.get('url')})
    n_unid = len([p for p in Q.todos() if p.get('url')])
    marco(L, 'EQUIPAMIENTO', '04 / 04', 'Lista de compra · enlaces a makro.es',
          ['Medidas ancho × fondo × alto en metros,',
           'tomadas de la ficha de makro.es.',
           'Los enlaces de la última columna son',
           'clicables en el PDF; en papel, copiar la',
           'dirección o buscar el título en makro.es.',
           'Vitrinas y cafetera ya compradas, con las',
           'medidas del cliente. Barriles y tablet con',
           'medida promedio.',
           'Confirmar precio y stock antes de comprar.'],
          [], ('RESUMEN',
               [('Fichas distintas de Makro', f'{n_fichas}'),
                ('Unidades a comprar en Makro', f'{n_unid}'),
                ('Ya comprado', 'cafetera y 2 vitrinas'),
                ('Medida promedio', 'barriles y tablet'),
                ('A medida', f'{len(LM.A_MEDIDA)} elementos')]),
          tabla=('', []), esc_txt='sin escala', escala=False)
    return L, enlaces


def exportar_lista(nombre='LISTA_EQUIPAMIENTO'):
    L, enlaces = lamina_lista()
    pdf = exportar(L, nombre)
    import pymupdf
    k = 72.0 / 25.4
    doc = pymupdf.open(pdf)
    pg = doc[0]
    for a, b, c, d, url in enlaces:
        pg.insert_link({'kind': pymupdf.LINK_URI,
                        'from': pymupdf.Rect(a * k, b * k, c * k, d * k), 'uri': url})
    tmp = pdf + '.tmp'
    doc.save(tmp); doc.close()
    os.replace(tmp, pdf)
    print(f'  {nombre}.pdf  ·  {len(enlaces)} enlaces clicables')
    return pdf


if __name__ == '__main__':
    import build_planos
    print('Generando las cuatro láminas...')
    pb = exportar(build_planos.planta_baja(), 'PLANTA_BAJA')
    pa = exportar(build_planos.planta_alta(), 'PLANTA_ALTA')
    eq = exportar(lamina(), 'EQUIPAMIENTO')
    li = exportar_lista()
    import pymupdf
    for nombre, hojas in (('Planos_Estructura.pdf', (pb, pa)),
                          ('Planos_Completos.pdf', (pb, pa, eq, li))):
        doc = pymupdf.open()
        for f in hojas:
            doc.insert_pdf(pymupdf.open(f))
        doc.save(os.path.join(AQUI, nombre))
        print(f'  {nombre}  ({doc.page_count} páginas)')
