# -*- coding: utf-8 -*-
"""
Genera MODELO_3D.rb: el local entero en 3D, listo para pegar o cargar en la
consola Ruby de SketchUp.

    python3 export_sketchup.py        ->  MODELO_3D.rb

Toda la geometria sale de estructura.py, mobiliario.py y equipamiento.py, que
son las mismas fuentes que dibujan las cuatro laminas: ninguna coordenada se
escribe a mano aqui. Las alturas que el levantamiento no recoge estan todas
juntas en ALTURAS, marcadas como supuestas, y viajan al encabezado del .rb.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estructura as E
import mobiliario as MB
import equipamiento as Q

AQUI = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- alturas
# En planta todo esta medido. En altura el levantamiento solo da el suelo a
# suelo (2,560). Lo demas se supone aqui, una sola vez, y se avisa en el .rb.
T_FORJADO   = 0.250     # SUPUESTO: canto del forjado (COMPROBAR)
Z_SOFITO    = E.H_PA - T_FORJADO           # 2,310 intrados del forjado
Z_PA        = E.H_PA                        # 2,560 suelo del altillo
Z_TECHO     = E.H_PA + E.H_LIBRE_PA         # 5,060 techo del altillo
H_SOLERA    = 0.150     # espesor de la solera dibujada bajo el pavimento
Z_VIGA_INF  = 2.100     # SUPUESTO: intrados de la viga P1b (COMPROBAR)
H_ZOC_VENT  = 0.450     # SUPUESTO: alto del zocalo del ventanal (COMPROBAR)
H_MESA      = 0.750     # tablero de las mesas
E_TABLERO   = 0.040
H_SILLA     = 0.450     # asiento
H_RESPALDO  = 0.880     # coronacion del respaldo
E_RESPALDO  = 0.050
H_SILLON    = 0.420     # asiento del sillon corrido
H_SILLON_R  = 1.050     # coronacion del respaldo del sillon
E_SILLON_R  = 0.100
H_BARRA_MAD = 0.040     # canto de la tabla de madera del mostrador
Z_ESTANTE   = 1.500     # SUPUESTO: altura del estante mural de la trasbarra
Z_AIRE      = 2.310     # cassettes de aire colgados al nivel del sofito
H_AIRE      = 0.250
H_REJILLA   = 0.060
D_EMPOTRADO = 0.090     # diametro de los empotrados
H_COLGANTE  = 0.220     # alto de la pantalla de los colgantes
Z_COLGANTE  = 2.200     # cota del borde inferior de los colgantes
H_APLIQUE   = 0.300

ALTURAS_DOC = [
    ('Suelo a suelo', E.H_PA, 'medido en obra'),
    ('Canto del forjado', T_FORJADO, 'SUPUESTO — COMPROBAR'),
    ('Intrados del forjado', Z_SOFITO, 'derivado'),
    ('Altura libre del altillo', E.H_LIBRE_PA, 'sin medir'),
    ('Techo del altillo', Z_TECHO, 'derivado'),
    ('Coronacion del acristalamiento', E.H_ESCAPARATE, 'aproximada — COMPROBAR'),
    ('Travesano del ventanal Sur', E.H_TRAVESANO, 'sin medir — COMPROBAR'),
    ('Zocalo de piedra de la carpinteria', E.H_ZOCALO, 'medido'),
    ('Alto del zocalo del ventanal', H_ZOC_VENT, 'SUPUESTO — COMPROBAR'),
    ('Intrados de la viga P1b', Z_VIGA_INF, 'SUPUESTO — COMPROBAR'),
    ('Pared en L', E.H_PARED_L, 'medida'),
    ('Vidrio sobre la pared en L', E.H_VIDRIO_L, 'medido'),
    ('Huecos de paso', E.H_PUERTA, 'estandar'),
    ('Antepechos de vidrio', E.H_BARANDA, 'estandar'),
    ('Encimeras', Q.H_ENCIMERA, 'estandar'),
    ('Borde inferior de la campana', Q.H_CAMPANA, 'estandar'),
    ('Estante mural de la trasbarra', Z_ESTANTE, 'SUPUESTO'),
    ('Sillon corrido: asiento / respaldo', H_SILLON, 'SUPUESTO — fondo sin medir'),
]

P1N = next(p for p in E.PILARES if p[0] == 'P1')[5]
_f = lambda v: f'{v:.3f}'.replace('.', ',')
CADENA_DOC = [
    ('Cara interior del zocalo del ventanal', _f(E.BARRA['y0'])),
    ('+ barra 2,79  -> cara Sur de P1', _f(E.BARRA['y1'])),
    (f"+ paso {_f(E.PASO_PERS['medido'])}  -> cara NORTE de P1 = base de la L",
     _f(E.PARED_L_LAR[2])),
    (f'+ pared en L {_f(E.PARED_L_LARGO)}  -> muro Norte', _f(E.PARED_L_LAR[4])),
    (f"+ hundimiento {_f(E.HUNDIMIENTO['p'])}  -> pared hundida de la cocina",
     _f(E.MURO_N_COCINA)),
    ('+ espesor del muro  -> borde del solar', _f(E.MED_EXT)),
    ('De la pared hundida a la cara Norte de P1',
     _f(E.MURO_N_COCINA - P1N) + '  (los 3,65 del cliente)'),
]
_fil = [m for m in MB.MESAS_PB if m[0] in ('M1', 'M3', 'M2')]
_fil.sort(key=lambda m: m[2])
PASOS_DOC = [
    ('Entre las mesas del ventanal',
     _f(_fil[1][2] - _fil[0][4]) + ' y ' + _f(_fil[2][2] - _fil[1][4])),
    ('Libre delante del mostrador', _f(_fil[0][2] - Q.MOSTRADOR_X[1])),
    ('Entre las dos filas de sillas (pasillo del ventanal)', '1,202'),
    ('Entre la silla de M2 y la nevera A7', '0,450'),
    ('Puerta -> barra, por el Norte de la fila central', '0,700'),
    ('Salida del personal de la barra a la sala', '1,310'),
    ('Pasillo de la cocina', _f(Q.PASILLO_COCINA_MIN) + ' a ' + _f(Q.PASILLO_COCINA)),
]

# --------------------------------------------------------------- materiales
MAT = {
    'muro':      ('Muro',            (196, 192, 186)),
    'pilar':     ('Pilar',           (120, 118, 114)),
    'tabique':   ('Tabique',         (214, 210, 202)),
    'forjado':   ('Forjado',         (176, 172, 165)),
    'solera':    ('Solera',          (150, 148, 145)),
    'vidrio':    ('Vidrio',          (150, 190, 205)),
    'carp':      ('Carpinteria',     ( 70,  90, 100)),
    'madera':    ('Madera',          (168, 124,  78)),
    'mesa':      ('Mesa',            (206, 190, 166)),
    'silla':     ('Silla',           (138, 111,  78)),
    'sillon':    ('Sillon',          (128,  96,  78)),
    'inox':      ('Inox',            (198, 202, 206)),
    'aparato':   ('Aparato',         (120, 138, 150)),
    'frio':      ('Equipo de frio',  (168, 198, 212)),
    'encimera':  ('Encimera',        (222, 214, 198)),
    'piedra':    ('Piedra',          (186, 182, 176)),
    'escalera':  ('Escalera',        (162, 158, 152)),
    'luz':       ('Luminaria',       (246, 232, 180)),
    'aire':      ('Aire acondicionado', (111, 138, 153)),
    'reserva':   ('Reserva',         (122, 106,  78)),
}

cajas, prismas, cilindros = [], [], []


def caja(tag, mat, nombre, x0, y0, x1, y1, z0, z1):
    if x1 - x0 <= 1e-6 or y1 - y0 <= 1e-6 or z1 - z0 <= 1e-6:
        raise ValueError(f'caja degenerada: {nombre}')
    cajas.append((tag, mat, nombre, x0, y0, x1, y1, z0, z1))


def prisma(tag, mat, nombre, pts, z0, z1):
    prismas.append((tag, mat, nombre, list(pts), z0, z1))


def cilindro(tag, mat, nombre, cx, cy, r, z0, z1):
    cilindros.append((tag, mat, nombre, cx, cy, r, z0, z1))


# ============================================================ PLANTA BAJA
# --- solera y muros -------------------------------------------------------
import build_planos as B

prisma('01 Solera', 'solera', 'Solera de planta baja',
       B.interior_pb(), -H_SOLERA, 0.0)

# El 'Muro Sur (con ventanal)' no es fabrica: en toda su longitud es el
# ventanal, con P2 y la jamba cerrando los extremos. Se salta igual que en
# el plano (B.SIN_POCHE) y su hueco lo cierra la carpinteria.
for nm, x0, y0, x1, y1, e in E.MUROS:
    if nm in B.SIN_POCHE:
        continue
    caja('02 Muros', 'muro', nm, x0, y0, x1, y1, 0.0, Z_TECHO)

# pilares: P1 muere en el forjado; los demas suben hasta el techo
for tag, nm, x0, y0, x1, y1 in E.PILARES:
    z1 = Z_PA if tag == 'P1' else Z_TECHO
    caja('03 Pilares', 'pilar', f'{tag} · {nm}', x0, y0, x1, y1, 0.0, z1)

# viga descolgada P1b
nm, x0, y0, x1, y1 = E.VIGA
caja('03 Pilares', 'pilar', nm, x0, y0, x1, y1, Z_VIGA_INF, Z_SOFITO)

# --- carpinteria del ventanal Sur ----------------------------------------
v = E.VENTANAL_SUR
for i, (a, b) in enumerate(v['panos'], 1):
    caja('04 Carpinteria', 'vidrio', f'Ventanal Sur · paño {i}',
         a, v['y'] + 0.012, b, v['y'] + v['e'] - 0.012,
         E.H_ZOCALO, E.H_ESCAPARATE)
    # travesaño corrido a media altura
    caja('04 Carpinteria', 'carp', f'Ventanal Sur · travesaño {i}',
         a, v['y'], b, v['y'] + v['e'],
         E.H_TRAVESANO - 0.030, E.H_TRAVESANO + 0.030)
    caja('04 Carpinteria', 'piedra', f'Ventanal Sur · zócalo de piedra {i}',
         a, v['y'], b, v['y'] + v['e'], 0.0, E.H_ZOCALO)
ja, jb = v['jamba']
caja('02 Muros', 'muro', 'Ventanal Sur · jamba', ja, v['y'], jb, v['y'] + 0.249,
     0.0, Z_TECHO)

# --- escaparate y puerta de acceso ---------------------------------------
es, pa = E.ESCAPARATE, E.PUERTA_ACCESO
caja('04 Carpinteria', 'vidrio', 'Escaparate · vidrio',
     es['x0'], es['y'] + 0.010, pa['x0'], es['y'] + es['e'] - 0.010,
     E.H_ZOCALO, E.H_ESCAPARATE)
caja('04 Carpinteria', 'piedra', 'Escaparate · zócalo de piedra',
     es['x0'], es['y'], es['x1'], es['y'] + es['e'], 0.0, E.H_ZOCALO)
# puerta de dos hojas, abierta 90 grados hacia el vestibulo
hoja = pa['ancho'] / 2
for i in range(pa['hojas']):
    xh = pa['x0'] + i * hoja
    caja('04 Carpinteria', 'vidrio', f'Puerta de acceso · hoja {i + 1}',
         xh, pa['y'], xh + hoja, pa['y'] + es['e'], E.H_ZOCALO, pa['alto'])
caja('04 Carpinteria', 'vidrio', 'Puerta de acceso · montante superior',
     pa['x0'], pa['y'] + 0.010, pa['x1'], pa['y'] + es['e'] - 0.010,
     pa['alto'], E.H_ESCAPARATE)

# --- pared en L y vidrio --------------------------------------------------
for nm, x0, y0, x1, y1 in (E.PARED_L_LAR, E.PARED_L_DOB):
    caja('05 Pared en L', 'tabique', nm, x0, y0, x1, y1, 0.0, E.H_PARED_L)
    caja('05 Pared en L', 'vidrio', nm + ' · vidrio',
         x0 + 0.030, y0 + 0.030, x1 - 0.030, y1 - 0.030,
         E.H_PARED_L, E.H_PARED_L + E.H_VIDRIO_L)

# --- zocalo del ventanal --------------------------------------------------
z = E.ZOCALO_SUR
for a, b in ((z['x0'], 1.290), (1.870, z['x1'])):      # partido por P2
    caja('06 Zocalo', 'piedra', 'Zócalo del ventanal',
         a, z['y0'], b, z['y1'], 0.0, H_ZOC_VENT)

# --- bano de planta baja --------------------------------------------------
for nm, x0, y0, x1, y1 in E.BANO_TABIQUES:
    caja('07 Bano', 'tabique', nm, x0, y0, x1, y1, 0.0, Z_PA)
bp = E.BANO_PUERTA
caja('07 Bano', 'tabique', 'Baño · dintel de la puerta',
     bp['x0'], bp['y'], bp['x1'], bp['y'] + E.BANO['e'], E.H_PUERTA, Z_PA)
caja('07 Bano', 'madera', 'Baño · hoja de la puerta',
     bp['x0'], bp['y'] + 0.020, bp['x1'], bp['y'] + 0.060, 0.0, E.H_PUERTA)

# --- caja de escalera y escalera -----------------------------------------
nm, x0, y0, x1, y1 = E.CAJA_ESC_PB
caja('08 Escalera', 'tabique', nm, x0, y0, x1, y1, 0.0, Z_PA)
for i in range(1, E.ESC_N_TABICAS + 1):
    ya = E.ESC_Y_PIE + (i - 1) * E.ESC_HUELLA
    yb = min(ya + E.ESC_HUELLA, E.ESC_Y_ALTO)
    if yb - ya < 1e-6:
        continue
    caja('08 Escalera', 'escalera', f'Peldaño {i}',
         E.ESC_X0, ya, E.ESC_X1, yb, 0.0, i * E.ESC_TABICA)

# --- forjado del altillo --------------------------------------------------
prisma('09 Forjado', 'forjado', 'Forjado de planta alta', E.FORJADO,
       Z_SOFITO, Z_PA)

# ============================================================ COCINA
c, n = Q.COCINA, Q.NICHO
b = Q.BANCADA_COCCION
caja('10 Cocina', 'inox', 'Bancada de cocción a medida',
     b['x0'], b['y0'], b['x1'], b['y1'], 0.0, Q.H_ENCIMERA)
x = Q.COCCION_X0
for p in Q.COCCION:
    caja('10 Cocina', 'aparato', f"{p['tag']} · {p['nombre']}",
         x, b['y1'] - p['f'], x + p['a'], b['y1'],
         Q.H_ENCIMERA, Q.H_ENCIMERA + p['h'])
    x += p['a']
cp = Q.CAMPANA_POS
caja('10 Cocina', 'inox', f"{Q.CAMPANA['tag']} · {Q.CAMPANA['nombre']}",
     cp['x0'], cp['y0'], cp['x1'], cp['y1'],
     Q.H_CAMPANA, Q.H_CAMPANA + Q.CAMPANA['h'])

y = Q.OESTE_Y0
for p in Q.OESTE:
    caja('10 Cocina', 'frio' if p['tag'] in ('K8', 'K9') else 'aparato',
         f"{p['tag']} · {p['nombre']}",
         Q.OESTE_X0, y - p['a'], Q.OESTE_X0 + p['f'], y, 0.0, p['h'])
    if p['tag'] == 'K7':                      # lavavajillas bajo el escurridor
        lv = Q.LAVAVAJILLAS
        ly1 = y - (Q.HUECO_LAV - lv['a']) / 2
        caja('10 Cocina', 'aparato', f"{lv['tag']} · {lv['nombre']}",
             Q.OESTE_X0 + 0.010, ly1 - lv['a'], Q.OESTE_X0 + lv['f'], ly1,
             0.0, lv['h'])
    y -= p['a']

y = Q.ESTE_Y0
for p in Q.ESTE:
    caja('10 Cocina', 'frio', f"{p['tag']} · {p['nombre']}",
         Q.ESTE_X1 - p['f'], y - p['a'], Q.ESTE_X1, y, 0.0, p['h'])
    y -= p['a']

# ============================================================ BARRA
tx0, tx1 = Q.TRASBARRA_X
ty0, ty1 = Q.TRASBARRA_Y
pos = dict((t, (a, b2)) for t, a, b2 in Q.trasbarra_pos())
fb = Q.FREGADERO_BARRA
# mesada corrida, salvo el tramo del fregadero de pie
caja('11 Barra', 'encimera', 'Mesada de la trasbarra a medida',
     tx0, pos[fb['tag']][1], tx1, ty1, Q.H_ENCIMERA - 0.040, Q.H_ENCIMERA)
caja('11 Barra', 'inox', f"{fb['tag']} · {fb['nombre']}",
     tx0, pos[fb['tag']][0], tx0 + fb['f'], pos[fb['tag']][1], 0.0, fb['h'])
for p in Q.TRASBARRA:
    ya, yb = pos[p['tag']]
    caja('11 Barra', 'aparato', f"{p['tag']} · {p['nombre']}",
         tx0, yb - p['a'], tx0 + p['f'], yb, Q.H_ENCIMERA, Q.H_ENCIMERA + p['h'])
nv, np_ = Q.NEVERA_BARRA, Q.NEVERA_POS
caja('11 Barra', 'frio', f"{nv['tag']} · {nv['nombre']}",
     tx0, np_['y0'], tx0 + nv['f'], np_['y1'], 0.0, nv['h'])
for i in range(Q.ESTANTE_N):
    ya = ty1 - (i + 1) * Q.ESTANTE['a']
    caja('11 Barra', 'inox', f"{Q.ESTANTE['tag']} · {Q.ESTANTE['nombre']} ({i + 1})",
         tx0, ya, tx0 + Q.ESTANTE['f'], ya + Q.ESTANTE['a'],
         Z_ESTANTE, Z_ESTANTE + Q.ESTANTE['h'])

# mostrador delantero
mx0, mx1 = Q.MOSTRADOR_X
my0, my1 = Q.MOSTRADOR_Y
bm = Q.BARRA_MADERA
caja('11 Barra', 'encimera', 'Mostrador delantero a medida',
     mx0, my0, mx1, my1, 0.0, Q.H_ENCIMERA)
caja('11 Barra', 'madera', 'Mostrador · tabla de madera',
     mx0, bm['y0'], mx1, bm['y1'], Q.H_ENCIMERA, Q.H_ENCIMERA + H_BARRA_MAD)
vy = my0
for p in Q.VITRINAS:
    vt = Q.VITRINA
    caja('11 Barra', 'aparato', f"{p['tag']} · motor",
         mx1 - vt['motor'][1], vy, mx1, vy + vt['motor'][0], 0.0, vt['motor'][1])
    caja('11 Barra', 'vidrio', f"{p['tag']} · {p['nombre']}",
         mx1 - p['f'], vy, mx1, vy + p['a'], vt['hueco_bajo'], p['h'])
    vy += p['a']
lv = Q.LAVAVASOS
caja('11 Barra', 'aparato', f"{lv['tag']} · {lv['nombre']}",
     mx1 - lv['f'], my0 + 0.030, mx1, my0 + 0.030 + lv['a'], 0.0, lv['h'])
tb = Q.TABLET
caja('11 Barra', 'aparato', f"{tb['tag']} · {tb['nombre']}",
     mx0 + 0.150, bm['y0'] + 0.200, mx0 + 0.150 + tb['f'],
     bm['y0'] + 0.200 + tb['a'], Q.H_ENCIMERA + H_BARRA_MAD,
     Q.H_ENCIMERA + H_BARRA_MAD + tb['h'])
# tabla de P2: chopera encima, barril debajo
tp = Q.TABLA_P2
caja('11 Barra', 'madera', 'Tabla de P2',
     tp['x0'], tp['y0'], tp['x1'], tp['y1'], Q.H_ENCIMERA, Q.H_ENCIMERA + H_BARRA_MAD)
ch = Q.CHOPERA
caja('11 Barra', 'inox', f"{ch['tag']} · {ch['nombre']}",
     tp['x1'] - 0.100 - ch['f'], tp['y0'] + 0.080,
     tp['x1'] - 0.100, tp['y0'] + 0.080 + ch['a'],
     Q.H_ENCIMERA + H_BARRA_MAD, Q.H_ENCIMERA + H_BARRA_MAD + ch['h'])
br = Q.BARRILES
cilindro('11 Barra', 'inox', f"{br['tag']} · {br['nombre']}",
         tp['x0'] + 0.400, (tp['y0'] + tp['y1']) / 2, br['a'] / 2, 0.0, br['h'])

# nevera de bebidas A7
nb, npos = Q.NEVERA_BEBIDAS, Q.NEVERA_BEBIDAS_POS
caja('12 Sala', 'frio', f"{nb['tag']} · {nb['nombre']}",
     npos['x0'], npos['y0'], npos['x1'], npos['y1'], 0.0, nb['h'])

# ============================================================ MOBILIARIO
def mesa(tag_capa, m, z0):
    tag, tipo, x0, y0, x1, y1, lados = m
    if tipo == 'redonda':
        cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2
        cilindro(tag_capa, 'mesa', f'{tag} · tablero', cx, cy, r,
                 z0 + H_MESA - E_TABLERO, z0 + H_MESA)
        cilindro(tag_capa, 'silla', f'{tag} · pie', cx, cy, 0.060,
                 z0, z0 + H_MESA - E_TABLERO)
        cilindro(tag_capa, 'silla', f'{tag} · base', cx, cy, 0.220, z0, z0 + 0.020)
    else:
        caja(tag_capa, 'mesa', f'{tag} · tablero', x0, y0, x1, y1,
             z0 + H_MESA - E_TABLERO, z0 + H_MESA)
        ancho = x1 - x0
        n_pies = max(1, int(round(ancho / 0.70)))
        for i in range(n_pies):
            cx = x0 + ancho * (i + 0.5) / n_pies
            cy = (y0 + y1) / 2
            caja(tag_capa, 'silla', f'{tag} · pie {i + 1}',
                 cx - 0.040, cy - 0.040, cx + 0.040, cy + 0.040,
                 z0, z0 + H_MESA - E_TABLERO)
            caja(tag_capa, 'silla', f'{tag} · base {i + 1}',
                 cx - 0.200, cy - 0.200, cx + 0.200, cy + 0.200, z0, z0 + 0.020)
    # sillas
    cx0, cy0 = (x0 + x1) / 2, (y0 + y1) / 2
    for i, (sx0, sy0, sx1, sy1) in enumerate(MB.sillas(m), 1):
        caja(tag_capa, 'silla', f'{tag} · silla {i} · asiento',
             sx0, sy0, sx1, sy1, z0 + H_SILLA - 0.040, z0 + H_SILLA)
        for px, py in ((sx0, sy0), (sx1 - 0.040, sy0),
                       (sx0, sy1 - 0.040), (sx1 - 0.040, sy1 - 0.040)):
            caja(tag_capa, 'silla', f'{tag} · silla {i} · pata',
                 px, py, px + 0.040, py + 0.040, z0, z0 + H_SILLA - 0.040)
        # respaldo en el lado opuesto a la mesa
        dx, dy = (sx0 + sx1) / 2 - cx0, (sy0 + sy1) / 2 - cy0
        if abs(dx) >= abs(dy):
            if dx > 0:
                rx0, rx1 = sx1 - E_RESPALDO, sx1
            else:
                rx0, rx1 = sx0, sx0 + E_RESPALDO
            ry0, ry1 = sy0, sy1
        else:
            if dy > 0:
                ry0, ry1 = sy1 - E_RESPALDO, sy1
            else:
                ry0, ry1 = sy0, sy0 + E_RESPALDO
            rx0, rx1 = sx0, sx1
        caja(tag_capa, 'silla', f'{tag} · silla {i} · respaldo',
             rx0, ry0, rx1, ry1, z0 + H_SILLA, z0 + H_RESPALDO)


for m in MB.MESAS_PB:
    mesa('12 Sala', m, 0.0)

s = E.SILLON
caja('12 Sala', 'sillon', 'Sillón corrido · asiento',
     s['x0'], s['y'] - s['fondo'], s['x1'], s['y'], 0.0, H_SILLON)
caja('12 Sala', 'sillon', 'Sillón corrido · respaldo',
     s['x0'], s['y'] - E_SILLON_R, s['x1'], s['y'], H_SILLON, H_SILLON_R)

# ============================================================ LUCES Y AIRE
for i, (cx, cy) in enumerate(E.EMPOTRADOS, 1):
    cilindro('13 Instalaciones', 'luz', f'Empotrado {i}', cx, cy,
             D_EMPOTRADO / 2, Z_SOFITO - 0.020, Z_SOFITO)
for i, (cx, cy) in enumerate(E.COLGANTES, 1):
    cilindro('13 Instalaciones', 'luz', f'Colgante {i}', cx, cy, 0.130,
             Z_COLGANTE, Z_COLGANTE + H_COLGANTE)
for i, (cx, cy) in enumerate(E.APLIQUES, 1):
    caja('13 Instalaciones', 'luz', f'Aplique {i}',
         cx - 0.060, cy - 0.100, cx + 0.060, cy + 0.100, 1.800, 1.800 + H_APLIQUE)
rw, rh = E.AIRE_REJILLA
for tag, nm, cx, cy, a, f in E.AIRE:
    caja('13 Instalaciones', 'aire', f'{tag} · {nm}',
         cx - a / 2, cy - f / 2, cx + a / 2, cy + f / 2,
         Z_AIRE - H_AIRE, Z_AIRE)
    caja('13 Instalaciones', 'aire', f'{tag} · rejilla de retorno',
         cx - rw / 2, cy + f / 2 + 0.060, cx + rw / 2, cy + f / 2 + 0.060 + rh,
         Z_AIRE - H_REJILLA, Z_AIRE)

# ============================================================ PLANTA ALTA
for nm, x0, y0, x1, y1 in E.TABIQUES_PA:
    caja('14 Planta alta', 'tabique', nm, x0, y0, x1, y1, Z_PA, Z_TECHO)
for nm, x0, y0, x1, y1, ancho, eje in E.HUECOS_PA:
    caja('14 Planta alta', 'tabique', f'{nm} · dintel',
         x0, y0, x1, y1, Z_PA + E.H_PUERTA, Z_TECHO)
    if eje == 'x':
        caja('14 Planta alta', 'madera', f'{nm} · hoja',
             x0, y0 + 0.020, x0 + ancho, y0 + 0.060, Z_PA, Z_PA + E.H_PUERTA)
    else:
        caja('14 Planta alta', 'madera', f'{nm} · hoja',
             x0 + 0.020, y0, x0 + 0.060, y0 + ancho, Z_PA, Z_PA + E.H_PUERTA)
for nm, x0, y0, x1, y1 in E.BARANDILLAS:
    caja('14 Planta alta', 'vidrio', nm, x0, y0, x1, y1,
         Z_PA, Z_PA + E.H_BARANDA)
for m in MB.MESAS_PA:
    mesa('14 Planta alta', m, Z_PA)

# ============================================================ TECHO (oculto)
prisma('15 Techo', 'forjado', 'Techo del altillo', E.PERIMETRO,
       Z_TECHO, Z_TECHO + 0.200)


# ------------------------------------------------------------------ salida
def rb_num(v):
    return f'{v:.4f}'


def rb_str(t):
    return '"' + str(t).replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    tags = []
    for t in [c[0] for c in cajas] + [p[0] for p in prismas] + [c[0] for c in cilindros]:
        if t not in tags:
            tags.append(t)
    tags.sort()

    L = []
    w = L.append
    w('# encoding: UTF-8')
    w('#' + '-' * 76)
    w('#  LOCAL DE HOSTELERIA — MODELO 3D PARA SKETCHUP')
    w('#')
    w('#  Generado por docs/planos/export_sketchup.py desde estructura.py,')
    w('#  mobiliario.py y equipamiento.py, que son las mismas fuentes que')
    w('#  dibujan las cuatro laminas. Ninguna coordenada esta escrita a mano.')
    w('#')
    w('#  USO — consola Ruby de SketchUp:')
    w('#      load "C:/ruta/MODELO_3D.rb"')
    w('#  o pegar el archivo entero. Se construye al cargarlo. Para rehacerlo:')
    w('#      Local3D.build')
    w('#  Para borrar lo construido:')
    w('#      Local3D.clear')
    w('#')
    w('#  UNIDADES: metros. Cada numero se convierte con .m, asi que el modelo')
    w('#  sale a milimetro exacto sobre las cotas del plano.')
    w('#')
    w('#  ORIGEN: esquina interior Suroeste del local (0,0,0), X al Este,')
    w('#  Y al Norte, Z hacia arriba. Es el mismo origen de obra del plano.')
    w('#')
    w('#  ALTURAS (en planta todo esta medido; en altura, solo el suelo a suelo)')
    for nm, v, fuente in ALTURAS_DOC:
        w(f'#      {nm:<38s} {v:6.3f} m   {fuente}')
    w('#')
    w('#  CADENA DE OBRA DEL LADO OESTE (la que fijo el cliente)')
    for nm, v in CADENA_DOC:
        w(f'#      {nm:<46s} {v}')
    w('#')
    w('#  PASOS LIBRES MEDIDOS SOBRE EL MODELO')
    for nm, v in PASOS_DOC:
        w(f'#      {nm:<46s} {v}')
    w('#' + '-' * 76)
    w('')
    w('module Local3D')
    w('')
    w('  NOMBRE_MODELO = "Local de hosteleria"')
    w('')
    w('  # --- materiales: [clave, nombre, r, g, b]')
    w('  MATERIALES = [')
    for k, (nm, (r, g, b)) in MAT.items():
        w(f'    [{rb_str(k)}, {rb_str(nm)}, {r}, {g}, {b}],')
    w('  ]')
    w('')
    w('  # --- capas')
    w('  CAPAS = [')
    for t in tags:
        w(f'    {rb_str(t)},')
    w('  ]')
    w('  CAPAS_OCULTAS = ["15 Techo"]')
    w('')
    w('  # --- cajas: [capa, material, nombre, x0, y0, x1, y1, z0, z1]')
    w('  CAJAS = [')
    for tg, mt, nm, x0, y0, x1, y1, z0, z1 in cajas:
        w(f'    [{rb_str(tg)}, {rb_str(mt)}, {rb_str(nm)}, '
          f'{rb_num(x0)}, {rb_num(y0)}, {rb_num(x1)}, {rb_num(y1)}, '
          f'{rb_num(z0)}, {rb_num(z1)}],')
    w('  ]')
    w('')
    w('  # --- prismas: [capa, material, nombre, [[x, y], ...], z0, z1]')
    w('  PRISMAS = [')
    for tg, mt, nm, pts, z0, z1 in prismas:
        cad = ', '.join(f'[{rb_num(a)}, {rb_num(b)}]' for a, b in pts)
        w(f'    [{rb_str(tg)}, {rb_str(mt)}, {rb_str(nm)}, [{cad}], '
          f'{rb_num(z0)}, {rb_num(z1)}],')
    w('  ]')
    w('')
    w('  # --- cilindros: [capa, material, nombre, cx, cy, r, z0, z1]')
    w('  CILINDROS = [')
    for tg, mt, nm, cx, cy, r, z0, z1 in cilindros:
        w(f'    [{rb_str(tg)}, {rb_str(mt)}, {rb_str(nm)}, '
          f'{rb_num(cx)}, {rb_num(cy)}, {rb_num(r)}, {rb_num(z0)}, {rb_num(z1)}],')
    w('  ]')
    w('')
    w(RUBY_BUILDER)
    w('end')
    w('')
    w('Local3D.build')
    w('')

    destino = os.path.join(AQUI, 'MODELO_3D.rb')
    with open(destino, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    print(f'MODELO_3D.rb  ·  {len(cajas)} cajas, {len(prismas)} prismas, '
          f'{len(cilindros)} cilindros, {len(tags)} capas')
    return destino


RUBY_BUILDER = r'''
  # ------------------------------------------------------------- utilidades
  def self.material(model, clave)
    @mats ||= {}
    return @mats[clave] if @mats[clave]
    fila = MATERIALES.find { |f| f[0] == clave }
    return nil unless fila
    nombre = fila[1]
    mat = model.materials[nombre] || model.materials.add(nombre)
    mat.color = Sketchup::Color.new(fila[2], fila[3], fila[4])
    @mats[clave] = mat
  end

  def self.capa(model, nombre)
    @capas ||= {}
    @capas[nombre] ||= (model.layers[nombre] || model.layers.add(nombre))
  end

  # Extruye una cara horizontal creada en z0 hasta z1. La cara se construye
  # en sentido antihorario visto desde arriba, asi que su normal apunta a +Z
  # y el pushpull positivo sube; aun asi se comprueba la normal, porque
  # SketchUp puede invertirla al fusionar geometria.
  def self.extruir(grupo, puntos_xy, z0, z1)
    pts = puntos_xy.map { |x, y| Geom::Point3d.new(x.m, y.m, z0.m) }
    cara = grupo.entities.add_face(pts)
    return nil if cara.nil?
    alto = (z1 - z0).m
    cara.reverse! if cara.normal.z < 0
    cara.pushpull(alto)
    cara
  end

  def self.poner(grupo, model, capa_nombre, mat_clave, nombre)
    grupo.name = nombre
    grupo.layer = capa(model, capa_nombre)
    m = material(model, mat_clave)
    grupo.material = m if m
    grupo
  end

  def self.caja(model, ents, capa_nombre, mat_clave, nombre, x0, y0, x1, y1, z0, z1)
    g = ents.add_group
    extruir(g, [[x0, y0], [x1, y0], [x1, y1], [x0, y1]], z0, z1)
    poner(g, model, capa_nombre, mat_clave, nombre)
  end

  def self.prisma(model, ents, capa_nombre, mat_clave, nombre, pts, z0, z1)
    g = ents.add_group
    extruir(g, pts, z0, z1)
    poner(g, model, capa_nombre, mat_clave, nombre)
  end

  def self.cilindro(model, ents, capa_nombre, mat_clave, nombre, cx, cy, r, z0, z1)
    g = ents.add_group
    centro = Geom::Point3d.new(cx.m, cy.m, z0.m)
    aristas = g.entities.add_circle(centro, Geom::Vector3d.new(0, 0, 1), r.m, 32)
    cara = g.entities.add_face(aristas)
    if cara
      cara.reverse! if cara.normal.z < 0
      cara.pushpull((z1 - z0).m)
    end
    poner(g, model, capa_nombre, mat_clave, nombre)
  end

  # --------------------------------------------------------------- limpieza
  def self.clear
    model = Sketchup.active_model
    model.start_operation("Borrar #{NOMBRE_MODELO}", true)
    raiz = model.entities.grep(Sketchup::Group).find { |g| g.name == NOMBRE_MODELO }
    raiz.erase! if raiz && raiz.valid?
    model.commit_operation
    Sketchup.active_model.active_view.invalidate
    "borrado"
  end

  # ---------------------------------------------------------------- montaje
  def self.build
    model = Sketchup.active_model
    @mats = {}
    @capas = {}

    # metros como unidad de trabajo del modelo
    begin
      model.options["UnitsOptions"]["LengthUnit"] = 4   # 4 = metros
      model.options["UnitsOptions"]["LengthFormat"] = 0
      model.options["UnitsOptions"]["LengthPrecision"] = 3
    rescue StandardError
      # si la version no acepta estas opciones, seguimos: la geometria no cambia
    end

    model.start_operation("Construir #{NOMBRE_MODELO}", true)
    begin
      anterior = model.entities.grep(Sketchup::Group).find { |g| g.name == NOMBRE_MODELO }
      anterior.erase! if anterior && anterior.valid?

      CAPAS.each { |c| capa(model, c) }

      raiz = model.entities.add_group
      raiz.name = NOMBRE_MODELO
      ents = raiz.entities

      n = 0
      CAJAS.each do |f|
        caja(model, ents, f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8])
        n += 1
      end
      PRISMAS.each do |f|
        prisma(model, ents, f[0], f[1], f[2], f[3], f[4], f[5])
        n += 1
      end
      CILINDROS.each do |f|
        cilindro(model, ents, f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7])
        n += 1
      end

      CAPAS_OCULTAS.each do |c|
        l = model.layers[c]
        l.visible = false if l
      end

      model.commit_operation
      model.active_view.zoom_extents
      puts "#{NOMBRE_MODELO}: #{n} solidos en #{CAPAS.length} capas."
      n
    rescue StandardError => e
      model.abort_operation
      puts "ERROR al construir: #{e.message}"
      puts e.backtrace.first(8)
      raise
    end
  end
'''

if __name__ == '__main__':
    main()
