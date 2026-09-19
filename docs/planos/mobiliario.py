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
#   - Fila del ventanal Sur (19 set., tarde): las tres mesas arrancan en el
#     zocalo (1,968) y van "en vertical", con las sillas al Norte y al Sur.
#     M2 se trae aqui desde el hueco del escaparate, al lado de M3.
#     Separacion: 0,40 entre mesas, que son 0,68 entre sillas, con lo que
#     se pasa entre ellas. La fila mide 2,90 y se corre al Este, que es de
#     donde sale el sitio sin tocar nada: la silla Norte de M2 arranca en
#     6,265, justo donde acaba la nevera A7, asi que no entra en el
#     barrido de su puerta; y delante del mostrador quedan 1,395 en vez
#     de 1,00. M2 pasa del zocalo (que acaba en 5,870) al hueco de P5, el
#     sitio que el cliente pidio aprovechar, a 0,82 de la jamba del
#     vestibulo: ni en la puerta ni suelta, va al lado de M3.
#   - Fila central bajo el forjado: M5 y M4, las dos al Oeste de P3 y M4
#     pegada a su cara Oeste. M6 se quita. Al Oeste
#     de M5 no va ninguna mesa: ahi esta la unica salida del personal de la
#     barra a la sala (1,18 entre la linea del mostrador y M5), que es
#     tambien por donde se entra a la cocina por el paso de 0,95.
#   - Fila del sillon corrido: dos cuadruples de 1,40 (dos mesas de 0,70
#     juntas) pegadas a los extremos, contra la pared en L y contra el
#     tabique del bano, y una doble centrada entre las dos. Con la
#     correccion del muro Norte del 19 set. (noche) la fila baja 0,231,
#     igual que el sillon.
# La plaza de silla de ruedas ocupa el lado Norte de M1, al que se llega
# desde el ramal del itinerario que va a la barra.
MESAS_PB = [
    ('M1', 'doble',     3.925, 2.488, 4.625, 3.188, 'NS'),
    ('M3', 'doble',     5.025, 2.488, 5.725, 3.188, 'NS'),
    ('M2', 'doble',     6.125, 2.488, 6.825, 3.188, 'NS'),
    ('M5', 'doble',     3.840, 5.330, 4.540, 6.030, 'NS'),
    ('M4', 'doble',     4.970, 5.330, 5.670, 6.030, 'NS'),
    ('M7', 'cuadruple', 2.550, 7.657, 3.950, 8.357, 'S'),
    ('M10', 'doble',    4.615, 7.657, 5.315, 8.357, 'S'),
    ('M11', 'cuadruple', 5.980, 7.657, 7.380, 8.357, 'S'),
]

# Itinerario: tramos (metros), espacios de giro de 1,50 y anchos que se
# acotan. Trazado con el mayor circulo que pasa de la puerta a cada sitio,
# medido sobre la planta con todo el mobiliario puesto (1 cm de malla).
#
# La nevera A7 sale 0,58 de la cara Sur de P3 y deja 0,45 hasta las sillas
# de M2: por delante del pilar ya no se pasa. El camino de la puerta a la
# barra tiene que dar la vuelta por el Norte de la fila central, donde el
# hueco entre las sillas de esa fila (6,500) y las del sillon (7,238) es
# de 0,74. Sin la nevera el paso por el Sur era de 1,04.
#
# El pasillo del ventanal (1,20 entre las dos filas de sillas) se queda
# comunicado solo por su extremo Oeste: se dibuja como ramal sin salida.
ACC_ITINERARIO = [
    [(8.300, 0.600), (8.300, 2.400), (7.870, 3.200), (7.870, 7.000),
     (8.007, 7.250), (8.007, 7.730)],
    [(7.870, 6.844), (3.400, 6.844), (3.185, 6.300), (3.185, 4.173)],
    [(3.185, 4.173), (5.200, 4.173)],
]
# giros: centro y posicion del rotulo (fuera del trazo del itinerario)
ACC_GIROS = [((8.550, 2.120), (9.220, 2.860)), ((7.870, 6.600), (7.870, 6.960))]
ACC_PMR = None
# anchos que se acotan: tipo, posicion de la linea, extremos y sitio del texto
ACC_ANCHOS = [
    ('v', 4.230, 3.658, 4.860, 4.370, 4.100),    # sillas del ventanal - fila central
    ('v', 6.262, 3.658, 4.108, 6.085, 3.885),    # sillas de M2 - nevera A7: 0,45
    ('h', 5.679, 7.380, 8.650, 7.980, 5.789),    # M11 - caja de escalera
    ('v', 6.850, 6.500, 7.187, 6.680, 6.900),    # sillas: fila central - sillon
    ('h', 5.600, 2.530, 3.840, 3.180, 5.710),    # salida del personal a la sala
    ('h', 2.838, 4.625, 5.025, 4.825, 2.960),    # entre M1 y M3: 0,40
    ('h', 2.838, 5.725, 6.125, 5.925, 2.960),    # entre M3 y M2: 0,40
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
