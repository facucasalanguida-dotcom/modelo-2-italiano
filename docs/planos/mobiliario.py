# -*- coding: utf-8 -*-
"""
MOBILIARIO DE SALA — medidas en metros.

Mesas de sala segun el encargo del cliente del 19 set.: TODAS dobles de
0,70 x 0,70 para dos comensales, porque el personal las junta cuando hace
falta una de cuatro. En planta alta se mantienen la mesa de cowork y la
redonda de seis que el cliente pidio antes.

    doble      0,70 x 0,70   2 comensales
    cowork     2,40 x 1,00   8 puestos (planta alta)
    redonda    diametro 1,20 6 puestos (planta alta)
Silla 0,42 x 0,42, a 0,05 del canto de la mesa.

Criterios de reparto: 1,00 m libre delante del mostrador; el paso de
personal y el camino puerta-barra sin mesas; mesas contra el sillon corrido
con las sillas solo por el lado Sur (el sillon hace de asiento por el Norte);
itinerario accesible de 1,20 continuo; nada en el barrido de la puerta ni en
el vestibulo; ninguna mesa suelta fuera de una fila.
"""

SILLA = 0.420
SEP = 0.050

# (rotulo, tipo, x0, y0, x1, y1, sillas)   sillas: cadena con N S E W
#
# Distribucion del 19 set., con la estructura ya corregida:
#   - Fila del ventanal Sur: las mesas arrancan en el zocalo (1,968). M1 y M2
#     van "en vertical" (sillas al Norte y al Sur) como pidio el cliente: M1
#     entre la barra y P5 y M2 en el hueco de 1,31 que queda entre P5 y el
#     vestibulo, con la plaza de silla de ruedas por su lado Norte. M3 va girada
#     (sillas al Este y al Oeste): en vertical su silla Norte se comeria el
#     itinerario accesible, que aqui solo tiene 2,72 entre el zocalo y P3.
#   - Fila central bajo el forjado: M5 y M4 al Oeste de P3 (M4 pegada a su
#     cara Oeste) y M6 al Este, entre P3 y el itinerario del bano. Al Oeste
#     de M5 no va ninguna mesa: ahi esta la unica salida del personal de la
#     barra a la sala (1,18 entre la linea del mostrador y M5), que es
#     tambien por donde se entra a la cocina por el paso de 0,95.
#   - Fila del sillon corrido: seis mesas de 0,70 a 0,10 entre si, con el
#     sillon de asiento por el Norte y una silla por el Sur. A 0,10 se juntan
#     de dos en dos sin mover nada y cada comensal tiene 0,80 de banco.
# La plaza de silla de ruedas ocupa el lado Norte de M1, al que se llega
# desde el ramal del itinerario que va a la barra.
MESAS_PB = [
    ('M1', 'doble', 3.660, 2.488, 4.360, 3.188, 'NS'),
    ('M3', 'doble', 5.000, 2.488, 5.700, 3.188, 'EW'),
    ('M2', 'doble', 6.520, 1.050, 7.220, 1.750, 'S'),
    ('M5', 'doble', 3.840, 5.330, 4.540, 6.030, 'NS'),
    ('M4', 'doble', 4.970, 5.330, 5.670, 6.030, 'NS'),
    ('M6', 'doble', 6.500, 5.330, 7.200, 6.030, 'NS'),
] + [(f'M{7 + i}', 'doble', round(2.680 + 0.800 * i, 3), 7.708,
      round(2.680 + 0.800 * i + 0.700, 3), 8.408, 'S') for i in range(6)]

# Itinerario accesible: tramos (metros), espacios de giro de 1,50, plaza de
# silla de ruedas y anchos que se acotan.
#   - El ramal a la barra pasa a 0,60 de la cara Sur de P3 y sube a 4,26 al
#     Oeste del pilar, que es donde manda la fila del ventanal: entre la silla
#     Norte de M1 (3,658) y la silla Sur de la fila central (4,860) hay
#     justo 1,20.
#   - El tronco llega hasta la hoja de la puerta del bano, corrido a 8,007
#     para dejar 0,64 a la ultima mesa del sillon y a la caja de escalera.
#   - La plaza PMR va al lado Norte de M2, en el hueco entre P5 y el
#     vestibulo: su borde Este coincide con el borde Oeste del itinerario, de
#     modo que la silla de ruedas entra desde el sin invadirlo.
ACC_ITINERARIO = [
    [(8.300, 0.600), (8.300, 2.400), (7.870, 3.200), (7.870, 7.000),
     (8.007, 7.250), (8.007, 7.730)],
    [(7.870, 4.088), (5.500, 4.088), (5.000, 4.260), (3.260, 4.260)],
]
# giros: centro y posicion del rotulo (fuera del trazo del itinerario)
ACC_GIROS = [((8.550, 2.120), (9.220, 2.860)), ((7.870, 6.600), (7.870, 6.960))]
ACC_PMR = (6.470, 1.800, 7.270, 3.000)
# anchos que se acotan: tipo, posicion de la linea, extremos y sitio del texto
ACC_ANCHOS = [
    ('v', 4.190, 3.658, 4.860, 4.330, 4.100),    # itinerario: sillas del ventanal - fila central
    ('h', 5.730, 7.200, 8.650, 7.930, 5.840),    # M6 - caja de escalera
    ('v', 6.850, 6.550, 7.238, 6.680, 6.900),    # sillas: fila central - sillon
    ('h', 5.600, 2.660, 3.840, 3.250, 5.710),    # salida del personal a la sala
]

# Planta alta: mesa grande de cowork y una redonda grande. La redonda que
# quedaba al desembarco de la escalera se quita; la otra pasa a diametro
# 1,20 con seis sillas a 60 grados (N, S y cuatro a 30 grados del eje
# Este-Oeste: e=NE f=NO g=SO h=SE), la orientacion que menos ocupa a lo
# ancho. Centrada entre P3 y la caja de escalera y colocada de forma que el
# paso Norte hacia el aseo y el almacen quede en 1,01; a los lados quedan
# 0,40 hasta P3 y 0,39 hasta la caja de escalera (accesos a sillas, no
# recorridos), y 0,37 de la silla Sur a la barandilla.
# La mesa de cowork baja 0,20 y se corre 0,10 al Oeste: 1,01 de paso al
# Norte y 0,85 hasta P3.
MESAS_PA = [
    ('C1', 'cowork',  3.350, 4.100, 4.350, 6.500, 'EW4'),
    ('R1', 'redonda', 6.940, 4.830, 8.140, 6.030, 'NSefgh'),   # centrada entre P3 (6,32) y la caja (8,759)
]

# Pasos libres de planta alta que se acotan: tipo, posicion de la linea,
# extremos y sitio del texto
PASOS_PA = [
    ('v', 4.100, 6.500, 7.509, 4.250, 7.000),    # sobre la mesa de cowork
    ('v', 7.540, 6.500, 7.509, 7.690, 7.000),    # sobre la redonda (silla Norte)
    ('h', 5.300, 4.820, 5.670, 5.245, 5.420),    # sillas Este de C1 - P3
    ('h', 5.010, 6.320, 6.585, 6.452, 5.130),    # P3 - silla SO de la redonda
    ('h', 5.870, 8.495, 8.759, 8.627, 5.990),    # silla NE - caja de escalera
    ('v', 7.540, 3.988, 4.360, 7.690, 4.170),    # silla Sur - barandilla Sur
    ('h', 4.600, 2.461, 2.880, 2.670, 4.720),    # barandilla Oeste - sillas de C1
    ('v', 5.995, 3.988, 4.688, 6.145, 4.340),    # barandilla Sur - P3 (0,70 medido en obra)
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
