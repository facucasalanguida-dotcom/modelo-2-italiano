# -*- coding: utf-8 -*-
"""
ESTRUCTURA DEL LOCAL — cotas en metros.

Sistema de coordenadas del levantamiento (el mismo del modelo 3D):

    X = 0,000   cara exterior del muro OESTE
    X = 10,040  cara exterior de la medianera ESTE
    Y = 0,000   punto mas al sur del solar (cara sur del pilar de fachada)
    Y = 9,156   cara exterior de la medianera NORTE
    Z = 0,000   pavimento de planta baja     Z = +3,000  pavimento de planta alta

Cada cota procede de los PDF del levantamiento (planimetria 1:50 y propuesta
1:30), convertida a metros con las escalas validadas contra las cotas
rotuladas de los propios planos. No hay ninguna medida inventada.
"""

# ---------------------------------------------------------------- alturas (m)
H_PA          = 3.000     # cara superior del forjado de planta alta
T_FORJADO     = 0.300     # canto del forjado
Z_FORJ_INF    = 2.700     # intrados del forjado = altura libre en planta baja
H_LIBRE_PA    = 2.500     # altura libre en planta alta
H_TOT         = 5.500     # cara inferior del forjado de cubierta
H_ESCAPARATE  = 3.000     # coronacion del acristalamiento de fachada
H_BANDA       = 0.550     # banda de rotulo sobre el acristalamiento
Z_VIGA_INF    = 2.600     # intrados de la viga descolgada
H_PUERTA      = 2.100     # huecos de paso
H_BARANDA     = 1.000     # antepechos de vidrio

# escalera: 16 huellas de 0,260 · 17 tabicas de 3,000/17 = 0,1765
ESC_Y_PIE, ESC_Y_ALTO = 3.579, 7.738
ESC_N_HUELLAS, ESC_N_TABICAS = 16, 17
ESC_HUELLA = (ESC_Y_ALTO - ESC_Y_PIE) / ESC_N_HUELLAS      # 0,2599
ESC_TABICA = H_PA / ESC_N_TABICAS                          # 0,1765
ESC_X0, ESC_X1 = 8.811, 9.890                              # ancho 1,079

# ------------------------------------------------------- contorno del solar
PERIMETRO = [(0.000, 9.156), (10.040, 9.156), (10.040, 0.330),
             (6.230, 0.330), (6.230, 0.000), (5.731, 0.000),
             (5.731, 1.561), (0.000, 1.561)]

# ------------------------------------------------------------------- muros
# (nombre, x0, y0, x1, y1, espesor_nominal)
MUROS = [
    ('Medianera Norte',            0.000, 9.008, 10.040, 9.156, 0.148),
    ('Muro Oeste',                 0.000, 2.009,  0.250, 9.008, 0.250),
    ('Muro Oeste - esquina SO',    0.000, 1.561,  0.510, 2.009, 0.448),
    ('Muro Sur (con ventanal)',    0.510, 1.561,  5.980, 1.810, 0.249),
    ('Muro Oeste del cuello',      5.731, 0.960,  5.980, 1.561, 0.249),
    ('Medianera Este',             9.890, 1.429, 10.040, 9.008, 0.150),
    ('Medianera Este - cuello',    9.710, 0.330, 10.040, 1.429, 0.330),
]

# Trasdosado de 0,10 m bajo el forjado (solo planta baja, no llega a cubierta)
TRASDOSADO = ('Trasdosado Norte', 2.459, 8.907, 9.890, 9.008)

# -------------------------------------------------- pilares y machones (PB)
# (rotulo, nombre, x0, y0, x1, y1)
PILARES = [
    ('P1', 'Machón del muro Oeste',       0.250, 4.759, 0.621, 5.357),
    ('P2', 'Pilastra del muro Sur',       1.300, 1.810, 1.901, 2.108),
    ('P3', 'Pilar central',                5.620, 4.708, 6.219, 5.609),
    ('P4', 'Machón de la medianera Este', 9.689, 4.708, 9.890, 5.309),
    ('P5', 'Pilar de fachada',             5.731, 0.000, 6.230, 0.960),
]
# P3 llega solo al intrados del forjado y reaparece en planta alta.
PILARES_PA = ['P3', 'P4']

# Viga descolgada (intrados 2,60 · pasa a 3,00)
VIGA = ('Viga descolgada', 0.659, 4.828, 2.411, 5.078)

# ---------------------------------------------------- forjado de planta alta
FORJADO = [(2.461, 9.008), (9.890, 9.008), (9.890, 7.738), (8.811, 7.738),
           (8.811, 3.939), (2.411, 3.939), (2.411, 7.509), (2.461, 7.509)]

# Barandillas de vidrio del borde del vacio (e = 0,05 · h = 1,00)
BARANDILLAS = [
    ('Borde Oeste del vacio',   2.411, 3.988, 2.461, 7.509),
    ('Borde Sur del vacio',     2.411, 3.939, 8.759, 3.988),
    ('Caja de escalera',        8.759, 3.939, 8.811, 7.738),
]

# -------------------------------------------- particiones de planta alta
TABIQUES_PA = [
    ('Tabique Oeste del aseo',        2.461, 7.509, 2.560, 9.008),
    ('Tabique Sur - tramo Oeste',     2.560, 7.509, 3.089, 7.607),
    ('Tabique Sur - tramo Este',      3.849, 7.509, 7.511, 7.607),
    ('Tabique del inodoro',           4.461, 7.607, 4.560, 8.208),
    ('Tabique aseo / almacen',        5.459, 7.607, 5.558, 9.008),
    ('Tabique Este del almacen',      7.408, 7.607, 7.511, 8.072),
]
# (nombre, x0, y0, x1, y1, ancho, eje) — eje 'x' = hoja barre en X
HUECOS_PA = [
    ('Puerta aseo',    3.089, 7.509, 3.849, 7.607, 0.760, 'x'),
    ('Puerta inodoro', 4.461, 8.208, 4.560, 9.008, 0.800, 'y'),
    ('Puerta almacen', 7.408, 8.072, 7.511, 9.008, 0.940, 'y'),
]

# ------------------------------------------------------------ acristalamientos
# Ventanal sur del cuerpo principal: 4 panos iguales + 3 montantes de 0,05
VENTANAL_SUR = dict(x0=0.510, x1=5.980, y=1.561, e=0.060, panos=4, montante=0.050)
# Escaparate de la fachada principal: 2 panos + 1 montante en x = 7,639
ESCAPARATE = dict(x0=6.230, x1=9.710, y=0.330, e=0.049, montante_x=(7.639, 7.690))

# ------------------------------------------------ puntos de luz en el techo
# Empotrados del techo bajo (intrados 2,70) tomados del proyecto de reforma.
EMPOTRADOS = [(1.10, 4.60), (2.60, 4.60), (4.10, 4.60),
              (1.10, 5.90), (2.60, 5.90), (4.10, 5.90),
              (1.10, 7.20), (2.60, 7.20), (4.10, 7.20),
              (1.10, 8.50), (2.60, 8.50), (4.10, 8.50), (8.60, 8.50)]
# Colgantes / focos suspendidos de la zona de doble altura y del cuello
COLGANTES = [(2.04, 2.28), (2.04, 3.58), (4.60, 3.20), (7.60, 3.20),
             (7.30, 0.95), (8.90, 0.95)]
APLIQUES = [(0.31, 5.75), (0.31, 6.45)]

# --------------------------------------------------------------- superficies
SUP_PB_UTIL   = 75.63     # m2 dentro de muros, planta baja
SUP_FORJADO   = 33.74     # m2 de forjado de planta alta
SUP_DOBLE_ALT = 37.80     # m2 de vacio a doble altura
SUP_SOLAR     = 81.72     # m2 dentro del contorno exterior
RECINTOS_PA = [('Aseo (lavabo + inodoro)', 3.92), ('Almacen', 2.59),
               ('Paso / rellano', 3.33), ('Altillo diafano', 26.17)]
