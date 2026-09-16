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
                          pilares, pared_l, ventanal_sur, viga)
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
    rotulo(L, c['x0'], c['y0'], c['x1'], c['y1'], 'COCINA',
           f"{_fmt(c['x1']-c['x0'])} × {_fmt(c['y1']-c['y0'])} m  ·  entrada bajo la viga P1b")
    muros(L); pared_l(L); pilares(L, solo=('P1',)); viga(L)

    # --- linea de coccion: bancada a medida y aparatos de Oeste a Este
    b = Q.BANCADA_COCCION
    L.rect('muebles', b['x0'], b['y0'], b['x1'], b['y1'], MUEBLE, TINTA, 'medio')
    x = Q.COCCION_X0
    cortes = [x]
    for p in Q.COCCION:
        caja(L, x, b['y1'] - p['f'], x + p['a'], b['y1'], p['tag'])
        x += p['a']; cortes.append(x)
    L.texto('rotulos', (b['x0'] + b['x1']) / 2, b['y0'] + 0.025,
            'bancada de apoyo a medida  ·  2,12 × 0,60', 1.5, 'middle', ENCIMERA,
            'bold', dy=0.5)
    cp = Q.CAMPANA_POS
    L.rect('proyeccion', cp['x0'], cp['y0'], cp['x1'], cp['y1'], 'none', APARATO,
           'fino', ' stroke-dasharray="2.4 1.4"')
    L.texto('rotulos', 1.28, 8.20, 'CAMPANA 2,00 × 1,20', 1.8, 'middle', APARATO,
            'bold')
    L.texto('rotulos', 1.28, 8.20, f'borde inferior +{_fmt(Q.H_CAMPANA)}', 1.6,
            'middle', APARATO, dy=2.2)

    # --- muro Oeste, de Norte a Sur
    y = Q.OESTE_Y0
    cortes_o = [y]
    for p in Q.OESTE:
        frio = p['tag'] in ('K8', 'K9')
        caja(L, Q.OESTE_X0, y - p['a'], Q.OESTE_X0 + p['f'], y, p['tag'],
             FRIO if frio else '#ffffff', APARATO if not frio else '#3d5c6e', rot=-90)
        y -= p['a']; cortes_o.append(y)
    # tabla sobre el lavavajillas, de la pileta al horno
    k5 = Q.OESTE[0]; k6 = Q.OESTE[1]; k7 = Q.OESTE[2]
    yt1 = Q.OESTE_Y0 - k5['a']
    yt0 = yt1 - k6['a']
    # la tabla se dibuja maciza: cubre el lavavajillas y enlaza pileta y horno
    L.rect('encimera', Q.OESTE_X0, yt0, Q.OESTE_X0 + 0.66, yt1, MADERA, '#6b4f2a',
           'medio')
    L.rect('encimera', Q.OESTE_X0, yt0 - k7['a'], Q.OESTE_X0 + 0.66, yt1 + k5['a'],
           'none', '#6b4f2a', 'fino', ' stroke-dasharray="1.6 1.0"')
    L.texto('rotulos', Q.OESTE_X0 + 0.56, (yt0 + yt1) / 2, 'TABLA', 2.0, 'middle',
            '#6b4f2a', 'bold', rot=-90, dy=0.7)
    L.texto('rotulos', Q.OESTE_X0 + 0.72, (yt0 + yt1) / 2, 'K6 debajo', 1.6, 'start',
            '#6b4f2a', 'bold', dy=0.6)

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
    L.texto('rotulos', 1.36, 5.42, 'ENTRADA  1,18', 1.9, 'middle', COTA_COL, 'bold',
            dy=0.7)

    # --- cotas
    L.cota_h('cotas', cortes + [c['x1']], L.py(c['y1']) - 13.5, 1.8, ext_desde=c['y1'])
    L.cota_v('cotas', cortes_o, L.px(c['x0']) - 7.0, 1.8, ext_desde=c['x0'])
    L.cota_v('cotas', [Q.BANCADA_COCCION['y0']] + cortes_e + [c['y0']],
             L.px(c['x1']) + 7.0, 1.8, ext_desde=c['x1'])
    L.cota_h('cotas', [c['x0'], 0.550, 1.730, c['x1']], L.py(c['y0']) + 9.0, 1.8,
             ext_desde=c['y0'])
    return L


# ================================================================ BARRA
def detalle_barra(ox, oy):
    L = Lienzo(W, H, ESC25, ox, oy)
    for c in ('fondo', 'trama', 'muros', 'pilares', 'proyeccion', 'carpinteria',
              'muebles', 'encimera', 'aparatos', 'cotas', 'rotulos'):
        L.capa(c)
    b = Q.BARRA
    rotulo(L, b['x0'], b['y0'], b['x1'], b['y1'], 'BARRA',
           'trasbarra 2,75 · mostrador 3,19 hasta el paso de 0,60')
    muros(L); pared_l(L); pilares(L, solo=('P1', 'P2')); viga(L); ventanal_sur(L)

    # --- trasbarra: un mueble corrido bajo una sola encimera
    tx0, tx1 = Q.TRASBARRA_X
    ty0, ty1 = Q.TRASBARRA_Y
    L.rect('muebles', tx0, ty0, tx1, ty1, MUEBLE, TINTA, 'medio')
    L.rect('encimera', tx0, ty0, tx1, ty1, 'none', ENCIMERA, 'corte')
    y = ty1
    cortes_t = [y]
    for p in Q.TRASBARRA:
        if p['tag'] == 'A3':          # la licuadora va encima: rotulo en la franja Norte
            caja(L, tx0, y - p['a'], tx0 + p['f'], y, p['tag'], dash=True, tam=2.0,
                 tx=tx0 + p['f'] / 2, ty=y - 0.075)
        else:
            caja(L, tx0, y - p['a'], tx0 + p['f'], y, p['tag'], rot=-90)
        y -= p['a']; cortes_t.append(y)
    # modulo tecnico bajo la cafetera y licuadora sobre la hielera
    L.rect('muebles', tx0, ty1 - Q.MODULO_TECNICO, tx1, ty1, 'none', ENCIMERA,
           'fino', ' stroke-dasharray="1.2 0.9"')
    L.texto('rotulos', tx1 - 0.10, ty1 - Q.MODULO_TECNICO / 2, 'T1 técnico', 1.6,
            'middle', ENCIMERA, 'bold', rot=-90)
    a3 = Q.TRASBARRA[2]; ya3 = cortes_t[3]
    li = Q.LICUADORA
    caja(L, tx0 + 0.05, ya3 + 0.05, tx0 + 0.05 + li['f'], ya3 + 0.05 + li['a'],
         li['tag'], tam=1.7)
    L.texto('rotulos', tx1 + 0.06, (ty0 + ty1) / 2 + 0.55, 'ENCIMERA ÚNICA  2,75', 1.9,
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
        # motor abajo, a la izquierda (Sur) del lado de cliente
        mw, md = v['motor']
        L.rect('aparatos', mx0 + v['fondo_cristal'] - md, y, mx0 + v['fondo_cristal'],
               y + mw, 'none', '#3d5c6e', 'fino', ' stroke-dasharray="1.2 0.9"')
        L.texto('rotulos', mx0 + v['fondo_cristal'] - md / 2, y + mw / 2, 'motor', 1.4,
                'middle', '#3d5c6e', rot=-90, dy=0.5)
        y += p['a']; cortes_m.append(y)
    # bajo V2: lavavasos · bajo V1: barriles
    lv = Q.LAVAVASOS
    caja(L, mx0 + 0.05, my0 + 0.34, mx0 + 0.05 + lv['f'], my0 + 0.34 + lv['a'],
         lv['tag'], '#ffffff', APARATO, dash=True, tam=1.8, rot=-90)
    for k in range(2):
        cy = my0 + 1.000 + 0.31 + 0.16 + k * 0.34
        L.circulo('aparatos', mx0 + 0.30, cy, 0.16, 'none', APARATO, 'fino',
                  ' stroke-dasharray="1.2 0.9"')
    L.texto('rotulos', mx0 + 0.30, my0 + 1.000 + 0.31 + 0.16, 'B2', 1.8, 'middle',
            APARATO, 'bold', dy=0.6)
    bm = Q.BARRA_MADERA
    L.rect('muebles', mx0, bm['y0'], mx1, bm['y1'], MADERA, '#6b4f2a', 'medio')
    L.texto('rotulos', mx0 + 0.05, (bm['y0'] + bm['y1']) / 2,
            f"BARRA DE MADERA  {_fmt(bm['y1'] - bm['y0'])}", 1.7, 'middle', '#6b4f2a',
            'bold', rot=-90, dy=0.6)
    ch = Q.CHOPERA; tb = Q.TABLET
    caja(L, mx0 + 0.10, bm['y0'] + 0.03, mx0 + 0.10 + ch['f'], bm['y0'] + 0.03 + ch['a'],
         'B4', tam=1.8)
    caja(L, mx0 + 0.18, bm['y1'] - 0.03 - tb['a'], mx0 + 0.18 + tb['f'], bm['y1'] - 0.03,
         'B3', tam=1.6)
    # tabla de P2 al muro
    t = Q.TABLA_P2
    caja(L, t['x0'], t['y0'], t['x1'], t['y1'], 'TABLA', MADERA, '#6b4f2a', tam=1.8)

    # --- paso de servicio
    ym = (ty0 + ty1) / 2
    L.linea('cotas', tx1, ym, mx0, ym, COTA_COL, 'cota')
    L.texto('rotulos', (tx1 + mx0) / 2, ym, f'PASO DE SERVICIO  {_fmt(Q.PASILLO_BARRA)}',
            2.0, 'middle', COTA_COL, 'bold', rot=-90, dx=-1.4)

    L.cota_v('cotas', cortes_t + [ty0], L.px(b['x0']) - 7.0, 1.8, ext_desde=b['x0'])
    L.cota_v('cotas', cortes_m + [bm['y1'], E.PARED_L_LAR[2]], L.px(b['x1']) + 7.0, 1.8,
             ext_desde=b['x1'])
    L.cota_h('cotas', [b['x0'], tx1, mx0, mx1, mx0 + v['fondo_cristal']],
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
    K = detalle_cocina(ox=24.0, oy=52.0 + 9.008 * ESC25)
    B = detalle_barra(ox=170.0, oy=52.0 + 5.350 * ESC25)
    L.absorber(K, clip=(13.0, 26.0, 142.0, 232.0))
    L.absorber(B, clip=(160.0, 26.0, 292.0, 232.0))
    cuadro_equipos(L)

    marco(L, 'EQUIPAMIENTO', '03 / 04', 'Barra y cocina · productos Makro',
          ['Cada máquina es un producto real de makro.es con',
           'sus medidas de ficha; la web bloquea el acceso',
           'directo, así que las medidas vienen de su buscador.',
           'Confirmar en la ficha antes de comprar.',
           'Cocción corrida en la medianera Norte bajo campana',
           'de 2,00 sobre K1 a K4. Mesada refrigerada de una',
           'sola pieza (2,54, la más larga de Makro) pegada al',
           'doblez de la L; 0,42 libres junto a la cocción.',
           'La tabla cubre K6.',
           f'Pasillo de cocina de {_fmt(Q.PASILLO_COCINA_MIN)} a {_fmt(Q.PASILLO_COCINA)}: por debajo de 0,90',
           'con permiso del cliente. Muro Oeste: 3,01 de',
           'aparatos en los 3,05 que hay hasta P1.'],
          [(MUEBLE, TINTA, 'Bancada o mueble bajo'),
           (FRIO, '#3d5c6e', 'Equipo refrigerado'),
           ('none', ENCIMERA, 'Encimera o tabla corrida'),
           ('none', APARATO, 'Aparato (trazos: bajo encimera)'),
           (MADERA, '#6b4f2a', 'Tabla de madera'),
           (POCHE, TINTA, 'Muro de carga / medianera')],
          ('HOLGURAS Y ALTURAS',
           [('Pasillo de cocina, mínimo', f'{_fmt(Q.PASILLO_COCINA_MIN)} m'),
            ('Paso de servicio en barra', f'{_fmt(Q.PASILLO_BARRA)} m'),
            ('Entrada a la cocina, bajo la viga', '1,18 m'),
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
    paso = 4.9

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

    y = seccion(52.0, 'EQUIPOS DIBUJADOS EN LAS LÁMINAS 01 Y 03')
    y = cabecera(y)
    for i, p in enumerate(Q.todos()):
        y = fila(y, i, p)

    y = seccion(y + 5.0, 'ALTERNATIVAS CON LA MISMA FUNCIÓN  ·  no dibujadas')
    y = cabecera(y, 'SUSTITUYE')
    for i, p in enumerate(Q.ESTE_ALT + Q.OESTE_ALT):
        y = fila(y, i, p, tag=p['tag'].replace(' alt', ''))

    y = seccion(y + 5.0, 'A MEDIDA  ·  no se compran en Makro')
    for t in LM.A_MEDIDA:
        L.p_texto('rotulos', c_nom, y, '·  ' + t, 2.0, 'start', '#222222')
        y += 4.0

    y = seccion(y + 4.0, 'VERIFICACIÓN DE LOS ENLACES')
    for t in ('makro.es responde 403 a cualquier acceso desde un servidor (curl, Playwright o un '
              'navegador en la nube), así que las fichas no se pueden abrir desde el entorno de trabajo.',
              'Cada enlace se verificó buscando su identificador con el buscador restringido a makro.es: '
              'los 21 devuelven exactamente su URL con el título del producto (LISTA_MAKRO.md).',
              'Precios y stock no se han podido leer con fiabilidad: confirmar en la ficha antes de '
              'comprar. Si un enlace dejara de funcionar, buscar el título literal de la ficha en makro.es.'):
        L.p_texto('rotulos', c_nom, y, t, 2.0, 'start', '#444444')
        y += 4.0

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
