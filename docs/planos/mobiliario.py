# -*- coding: utf-8 -*-
"""
MOBILIARIO DE SALA Y PUNTOS DE LUZ — medidas en metros.

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
MESAS_PB = [
    # fila del ventanal sur
    # despegadas del ventanal (croquis del 15/09): 0,52 libres junto al vidrio
    ('M1', 'cuadruple', 3.700, 2.550, 4.900, 3.250, 'NS'),
    ('M2', 'cuadruple', 5.400, 2.550, 6.600, 3.250, 'NS'),
    # la doble va junto a M2 (0,30 entre cantos): delante del arranque de la
    # escalera no estorba el paso desde la puerta
    ('M3', 'doble',     6.900, 2.550, 7.600, 3.250, 'NS'),
    # fila central bajo el forjado
    ('M4', 'cuadruple', 3.550, 5.300, 4.750, 6.000, 'NS'),
    ('M5', 'cuadruple', 6.300, 5.300, 7.500, 6.000, 'NS'),
    ('M6', 'doble',     7.900, 5.300, 8.600, 6.000, 'NS'),
    # fila del sillon corrido: el sillon es el asiento del lado Norte
    ('M7', 'cuadruple', 2.850, 7.680, 4.050, 8.380, 'S'),
    ('M8', 'cuadruple', 4.450, 7.680, 5.650, 8.380, 'S'),
    ('M9', 'cuadruple', 6.050, 7.680, 7.250, 8.380, 'S'),
]

# Planta alta: mesa grande de cowork y dos redondas
MESAS_PA = [
    ('C1', 'cowork',  3.450, 4.300, 4.450, 6.700, 'EW4'),
    ('R1', 'redonda', 7.000, 4.550, 7.800, 5.350, 'SEW'),
    ('R2', 'redonda', 7.000, 6.100, 7.800, 6.900, 'NEW'),
]

# ------------------------------------------------------------------ luces
# Colgantes: uno centrado sobre cada mesa, tres sobre el borde de cliente de
# la barra y dos en el vestibulo. Empotrados: pasillos, cocina, trasbarra,
# bano y escalera. Todo replanteado sobre el mobiliario, no sobre el
# proyecto anterior.
def _centro(m):
    return ((m[2] + m[4]) / 2, (m[3] + m[5]) / 2)

COLGANTES_PB = [_centro(m) for m in MESAS_PB] + [
    (2.750, 2.100), (2.750, 3.100), (2.750, 4.100),      # barra, lado cliente
    (7.300, 0.950), (8.900, 0.950),                      # vestibulo
]
EMPOTRADOS_PB = [
    (0.550, 2.500), (0.550, 3.400), (0.550, 4.300),      # trasbarra
    (1.050, 5.950), (1.750, 5.950), (0.850, 7.150),      # cocina: el del SO delante
    (1.750, 7.150), (1.150, 5.250),                      # de los frigorificos (0,74 de
                                                         # fondo); entrada bajo la viga
    (3.100, 4.450), (4.950, 4.450), (7.000, 4.450),      # pasillo barra-sala
    (8.250, 4.450),
    (3.100, 6.900), (5.450, 6.900), (8.050, 6.950),      # pasillo del sillon
    (4.400, 1.950), (8.300, 2.250), (8.300, 3.450),      # paso del ventanal y camino
                                                         # puerta - escalera
    (8.600, 8.400),                                      # bano
    (9.350, 6.500),                                      # escalera
]
APLIQUES_PB = [(9.850, 2.450), (9.850, 3.250)]           # muro este, vestibulo

COLGANTES_PA = [_centro(m) for m in MESAS_PA]
EMPOTRADOS_PA = [
    (3.000, 4.700), (3.000, 6.300), (5.000, 4.500), (5.000, 6.900),
    (8.400, 4.700), (8.400, 6.500), (6.500, 7.050),
    (3.500, 8.300), (5.000, 8.500), (6.500, 8.300), (8.600, 8.400),
]


def sillas(m):
    """Rectangulos de las sillas de una mesa."""
    tag, tipo, x0, y0, x1, y1, lados = m
    out = []
    if tipo == 'redonda':
        cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2
        for l in lados:
            if l == 'N': out.append((cx - SILLA/2, cy + r + SEP, cx + SILLA/2, cy + r + SEP + SILLA))
            if l == 'S': out.append((cx - SILLA/2, cy - r - SEP - SILLA, cx + SILLA/2, cy - r - SEP))
            if l == 'E': out.append((cx + r + SEP, cy - SILLA/2, cx + r + SEP + SILLA, cy + SILLA/2))
            if l == 'W': out.append((cx - r - SEP - SILLA, cy - SILLA/2, cx - r - SEP, cy + SILLA/2))
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


PLAZAS_PB = sum(len(sillas(m)) + (2 if m[1] == 'cuadruple' and m[6] == 'S' else 0)
                for m in MESAS_PB)
PLAZAS_PA = sum(len(sillas(m)) for m in MESAS_PA)
