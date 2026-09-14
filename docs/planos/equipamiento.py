# -*- coding: utf-8 -*-
"""
EQUIPAMIENTO DE BARRA Y COCINA — medidas en metros.

Anchos y fondos de serie de hosteleria. Ninguno esta medido sobre un aparato
concreto: son los modulos normalizados del sector, pensados para que el
cliente sustituya encima los de los aparatos que ya tenga elegidos.

Los recintos salen del plano de estructura revisado el 14/09:

    COCINA   x 0,250 .. 2,370   y 5,183 .. 9,008    2,12 x 3,83 = 8,11 m2
             muro Oeste + medianera Norte + pared en L; al sur, P1b
    BARRA    x 0,250 .. 2,470   y 1,561 .. 5,183    trasbarra contra el muro
             Oeste y mostrador delantero en la linea de la pared en L

Toda la linea de coccion va en serie 600 y no en la habitual de 700: con
2,12 m de ancho libre, un fondo de 700 dejaria el pasillo de trabajo en
0,82 m, por debajo del minimo recomendado.
"""

# ------------------------------------------------------------------ recintos
COCINA = dict(x0=0.250, x1=2.370, y0=5.183, y1=9.008)
BARRA  = dict(x0=0.250, x1=2.470, y0=1.561, y1=5.183)

FONDO_COCINA = 0.600      # todas las lineas de la cocina
FONDO_BARRA  = 0.600      # trasbarra y mostrador delantero
H_ENCIMERA   = 0.900
H_CAMPANA    = 2.000      # borde inferior de la campana

# ------------------------------------------------- BARRA · mostrador delantero
# Cara Este de la barra, la que ve el cliente. (rotulo, nombre, largo)
MOSTRADOR = [
    ('V1', 'Vitrina expositora refrigerada', 1.200),
    ('C1', 'Caja y TPV',                     0.600),
    ('M1', 'Mostrador de servicio',          1.600),
]
MOSTRADOR_X = (1.870, 2.470)      # franja que ocupa, de Oeste a Este
MOSTRADOR_Y = 1.561               # arranca en la linea del ventanal

# ----------------------------------------------------- BARRA · trasbarra
# Un unico mueble corrido contra el muro Oeste, con UNA sola encimera.
TRASBARRA_X = (0.250, 0.850)
TRASBARRA_Y = (2.009, 4.759)      # de la esquina SO al machon P1 · 2,75 m

# Modulos bajo la encimera (rotulo, nombre, largo)
TRASBARRA_BAJO = [
    ('T1', 'Módulo técnico: descalcificador, conexiones y cajón de posos', 0.600),
    ('T2', 'Lavavajillas de barra, cesta 400 × 400',                       0.600),
    ('T3', 'Mueble del fregadero',                                         0.500),
    ('T4', 'Frigorífico bajo mostrador',                                   0.600),
    ('T5', 'Cajonera',                                                     0.450),
]
# Aparatos sobre la encimera (rotulo, nombre, largo, fondo, offset desde el sur)
TRASBARRA_SOBRE = [
    ('A1', 'Cafetera de 2 grupos', 1.200, 0.580, 0.000),
    ('A2', 'Fregadero pequeño',    0.500, 0.500, 1.200),
    ('A3', 'Exprimidor de naranjas', 0.350, 0.450, 1.700),
    ('A4', 'Tirador de cerveza',   0.350, 0.350, 2.050),
]

# ------------------------------------------------ COCINA · linea de coccion
# Contra el muro Oeste, bajo la campana. De Norte a Sur.
COCCION_X = (0.250, 0.850)
COCCION_Y0 = 9.008
COCCION = [
    ('K1', 'Cocina de 4 fuegos',        0.800),
    ('K2', 'Cocedor de pasta',          0.400),
    ('K3', 'Plancha',                   0.600),
    ('K4', 'Freidora',                  0.400),
    ('K5', 'Mesa de trabajo',           1.625),
]
CAMPANA = dict(x0=0.250, x1=0.950, y0=6.708, y1=9.008)   # 2,30 de largo

# ------------------------------------------------- COCINA · medianera Norte
NORTE_Y = (8.408, 9.008)
NORTE_X0 = 0.850
NORTE = [
    ('K6', 'Fregadero de cocina, 2 cubetas con escurridor', 1.200),
    ('K7', 'Módulo de apoyo',                               0.320),
]

# ---------------------------------------------------- COCINA · pared en L
# Muebles frigorificos abajo y encimera corrida de acero inoxidable encima.
ESTE_X = (1.770, 2.370)
ESTE_Y0 = 8.408
ESTE = [
    ('K8',  'Lavavajillas de cocina',              0.600),
    ('K9',  'Horno bajo encimera',                 0.600),
    ('K10', 'Mesa refrigerada de 2 puertas',       1.200),
    ('K11', 'Módulo de apoyo con estante',         0.600),
]
# Sobre la encimera de acero, con su offset desde el Norte
ESTE_SOBRE = [
    ('A5', 'Cortadora de fiambre', 0.550, 0.500, 1.250),
]

# --------------------------------------------------------------- holguras
PASILLO_COCINA = COCINA['x1'] - COCINA['x0'] - 2 * FONDO_COCINA     # 0,92
PASILLO_BARRA  = MOSTRADOR_X[0] - TRASBARRA_X[1]                    # 1,02
