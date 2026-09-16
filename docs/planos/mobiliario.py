# -*- coding: utf-8 -*-
"""
MOBILIARIO DE SALA — medidas en metros.

Mesas con medidas promedio de hosteleria (el cliente no pidio buscarlas):
    doble      0,70 x 0,70   2 comensales
    cuadruple  1,20 x 0,70   4 comensales
    cowork     2,40 x 1,00   8 puestos
    redonda    diametro 0,80 4 puestos
Silla 0,42 x 0,42, a 0,05 del canto de la mesa.

Criterios de reparto: 1,00 m libre delante del mostrador; el paso de
personal y el camino puerta-barra sin mesas; mesas contra el sillon corrido
con las sillas solo por el lado Sur (el sillon hace de asiento por el Norte);
1,30 entre cantos de mesas enfrentadas con sillas en medio; nada en el
pasillo de acceso al bano.
"""

SILLA = 0.420
SEP = 0.050

# (rotulo, tipo, x0, y0, x1, y1, sillas)   sillas: cadena con N S E W
#
# Accesibilidad (CTE DB-SUA): itinerario de 1,20 de ancho libre desde la puerta
# a la barra, al bano y a una plaza de silla de ruedas, con giros de 1,50 en la
# entrada y ante el bano. Para conseguirlo se retiran las dos mesas dobles (la
# del ventanal, junto a la entrada, y la de junto a la caja de escalera), la
# fila del ventanal baja 0,15 (1,26 entre sus sillas y las de la fila central),
# la plaza de silla de ruedas va entre M1 y M2 (extremo Oeste de M2) y la mesa
# central Este se corre 0,10 al Oeste (1,36 hasta la caja de escalera).
MESAS_PB = [
    # fila del ventanal sur: 0,28 libres junto al vidrio, para dejar 1,21 entre
    # sus sillas y el pilar P3 (itinerario accesible)
    ('M1', 'cuadruple', 3.700, 2.310, 4.900, 3.010, 'NS'),
    ('M2', 'cuadruple', 6.100, 2.310, 7.300, 3.010, 'NS'),   # 1,20 entre ambas: plaza PMR
    # fila central bajo el forjado: las dos al Oeste de P3 (con el pilar a
    # 2,35 de la caja de escalera no cabe mesa mas itinerario de 1,20 al Este)
    ('M3', 'cuadruple', 2.770, 5.300, 3.970, 6.000, 'NS'),
    ('M4', 'cuadruple', 4.270, 5.300, 5.470, 6.000, 'NS'),
    # fila del sillon corrido: tres cuadruples, el sillon es el asiento del
    # lado Norte; las de los extremos pegadas a la pared en L (0,03) y al
    # tabique del bano (0,03), la central centrada entre ambas
    ('M5', 'cuadruple', 2.500, 7.680, 3.700, 8.380, 'S'),
    ('M6', 'cuadruple', 4.335, 7.680, 5.535, 8.380, 'S'),
    ('M7', 'cuadruple', 6.170, 7.680, 7.370, 8.380, 'S'),
]

# Itinerario accesible: tramos (metros), espacios de giro de 1,50, plaza de
# silla de ruedas (extremo Oeste de M2, entre M1 y M2) y anchos que se acotan.
ACC_ITINERARIO = [
    [(8.660, 0.550), (8.660, 2.120), (8.030, 3.000), (8.030, 7.100)],   # puerta - bano
    [(8.030, 4.080), (3.100, 4.080)],                                    # ramal a la barra
]
# giros: centro y posicion del rotulo (fuera del trazo del itinerario)
ACC_GIROS = [((8.660, 2.120), (9.080, 2.360)), ((8.000, 6.930), (8.000, 6.470))]
ACC_PMR = (4.900, 2.310, 6.100, 3.010)
# anchos que se acotan: tipo, posicion de la linea, extremos y sitio del texto
ACC_ANCHOS = [('v', 6.300, 3.480, 4.688, 6.450, 4.360)]   # sillas de M2 - pilar P3 (punto mas estrecho)

# Planta alta: mesa grande de cowork y una redonda grande. La redonda que
# quedaba al desembarco de la escalera se quita; la otra pasa a diametro
# 1,20 con seis sillas a 60 grados (N, S y cuatro a 30 grados del eje
# Este-Oeste: e=NE f=NO g=SO h=SE), la orientacion que menos ocupa a lo
# ancho. Centrada entre P3 y la caja de escalera y colocada de forma que el
# paso Norte hacia el aseo y el almacen quede en 1,01; a los lados quedan
# 0,40 hasta P3 y 0,39 hasta la caja de escalera (accesos a sillas, no
# recorridos), y 0,37 de la silla Sur a la barandilla.
# La mesa de cowork baja 0,20 y se corre 0,10 al Oeste: 1,01 de paso al
# Norte y 0,59 hasta P3.
MESAS_PA = [
    ('C1', 'cowork',  3.350, 4.100, 4.350, 6.500, 'EW4'),
    ('R1', 'redonda', 6.984, 4.830, 8.184, 6.030, 'NSefgh'),   # centrada entre P3 y la caja
]

# Pasos libres de planta alta que se acotan: tipo, posicion de la linea,
# extremos y sitio del texto
PASOS_PA = [
    ('v', 4.100, 6.500, 7.509, 4.250, 7.000),    # sobre la mesa de cowork
    ('v', 7.584, 6.500, 7.509, 7.734, 7.000),    # sobre la redonda (silla Norte)
    ('h', 5.300, 4.820, 5.759, 5.290, 5.420),    # sillas Este de C1 - P3
    ('h', 5.010, 6.409, 6.629, 6.519, 5.130),    # P3 - silla SO de la redonda
    ('h', 5.870, 8.539, 8.759, 8.649, 5.990),    # silla NE - caja de escalera
    ('v', 7.584, 3.988, 4.360, 7.734, 4.170),    # silla Sur - barandilla Sur
    ('h', 4.600, 2.461, 2.880, 2.670, 4.720),    # barandilla Oeste - sillas de C1
    ('v', 6.084, 3.988, 4.688, 6.234, 4.340),    # barandilla Sur - P3 (0,70 medido en obra)
    ('h', 8.150, 7.511, 8.811, 8.160, 8.270),    # desembarco de la escalera
]

def sillas(m):
    """Rectangulos de las sillas de una mesa."""
    tag, tipo, x0, y0, x1, y1, lados = m
    out = []
    if tipo == 'redonda':
        # N E S W y diagonales a=NE b=NO c=SO d=SE; sillas como cuadrados
        # centrados a r + 0,05 + 0,21 del centro de la mesa
        import math
        ang = dict(E=0, e=30, a=45, N=90, b=135, f=150, W=180, g=210, c=225,
                   S=270, d=315, h=330)
        cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2
        rc = r + SEP + SILLA / 2
        for l in lados:
            t = math.radians(ang[l])
            sx, sy = cx + rc * math.cos(t), cy + rc * math.sin(t)
            out.append((sx - SILLA/2, sy - SILLA/2, sx + SILLA/2, sy + SILLA/2))
        return out
    n = 4 if 'EW4' in lados else 2 if tipo != 'doble' else 1
    if tipo == 'cowork':
        n = 4
    largo_x = (x1 - x0)
    for l in lados.replace('4', ''):
        if l in 'NS':
            paso = largo_x / n
            for i in range(n):
                cx = x0 + paso * (i + 0.5)
                if l == 'N':
                    out.append((cx - SILLA/2, y1 + SEP, cx + SILLA/2, y1 + SEP + SILLA))
                else:
                    out.append((cx - SILLA/2, y0 - SEP - SILLA, cx + SILLA/2, y0 - SEP))
        else:
            paso = (y1 - y0) / n
            for i in range(n):
                cy = y0 + paso * (i + 0.5)
                if l == 'E':
                    out.append((x1 + SEP, cy - SILLA/2, x1 + SEP + SILLA, cy + SILLA/2))
                else:
                    out.append((x0 - SEP - SILLA, cy - SILLA/2, x0 - SEP, cy + SILLA/2))
    return out


# contra el sillon, el propio sillon aporta los asientos del lado Norte
PLAZAS_PB = sum(len(sillas(m)) + ((2 if m[1] == 'cuadruple' else 1) if m[6] == 'S' else 0)
                for m in MESAS_PB)
PLAZAS_PA = sum(len(sillas(m)) for m in MESAS_PA)
