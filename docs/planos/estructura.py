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
# MEDIDA EN OBRA: del pavimento de planta baja al suelo del altillo hay
# 2,560 m, no los 3,000 que suponia el levantamiento. El canto del forjado
# sigue sin medir, asi que la altura libre de planta baja es 2,560 menos ese
# canto y no puede darse por buena hasta comprobarla.
H_PA          = 2.560     # suelo a suelo, medido en obra
T_FORJADO     = None      # canto del forjado: sin medir
Z_FORJ_INF    = None      # altura libre de planta baja = H_PA - T_FORJADO
H_LIBRE_PA    = 2.500     # altura libre en planta alta (sin medir)
H_TOT         = None      # altura total de la doble altura: sin medir
# El acristalamiento de fachada NO termina en +3,00 como suponia el modelo:
# los videos de obra lo muestran de DOBLE ALTURA, con la cabeza del vidrio a
# 0,4-0,8 m del techo del altillo. Cota pendiente de medir en obra.
H_ESCAPARATE  = 4.700     # coronacion aproximada del acristalamiento (comprobar)
# El ventanal sur, en cambio, tiene un travesaño corrido a media altura: en los
# videos se ve un montante horizontal continuo por encima del cual el hueco
# sigue subiendo. Altura del travesaño pendiente de medir.
H_TRAVESANO   = 2.300     # travesaño del ventanal sur (comprobar)
H_ZOCALO      = 0.130     # zocalo de piedra oscura bajo toda la carpinteria
H_BANDA       = 0.550     # banda de rotulo, a la altura de los ojos del altillo
Z_VIGA_INF    = 2.600     # intrados de la viga descolgada
H_PUERTA      = 2.100     # huecos de paso
H_BARANDA     = 1.000     # antepechos de vidrio

# escalera: la huella y el desarrollo en planta salen del levantamiento;
# la tabica se recalcula sobre la altura medida (2,560 / 17 = 0,1506).
ESC_Y_PIE, ESC_Y_ALTO = 3.579, 7.738
ESC_N_HUELLAS, ESC_N_TABICAS = 16, 17
ESC_HUELLA = (ESC_Y_ALTO - ESC_Y_PIE) / ESC_N_HUELLAS      # 0,2599
ESC_TABICA = H_PA / ESC_N_TABICAS                          # 0,1506
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
# Secciones y posiciones MEDIDAS EN OBRA (revision del 14/09). El P2 se
# completa hasta la linea del ventanal: en obra llega hasta la fachada.
# P1b es el machon que sube desde P1 hasta el forjado del altillo.
PILARES = [
    ('P1',  'Machón del muro Oeste',       0.250, 4.759, 0.550, 5.357),
    ('P1b', 'Machón sobre P1, al forjado', 0.550, 4.933, 2.380, 5.183),
    ('P2',  'Pilastra del muro Sur',       1.290, 1.561, 1.870, 2.011),
    ('P3',  'Pilar central',               5.410, 4.788, 6.060, 5.858),
    ('P4',  'Machón de la medianera Este', 9.689, 4.708, 9.890, 5.309),
    ('P5',  'Pilar de fachada',            5.731, 0.000, 6.331, 1.000),
]
# Pilares que atraviesan el forjado y siguen en planta alta. P5 es el machon
# de fachada entre el ventanal sur y el escaparate: en los videos se ve subir
# hasta el techo del altillo, por encima de la coronacion del vidrio.
PILARES_PA = ['P3', 'P4', 'P5']

# La antigua "viga descolgada" resulta ser el machon P1b, medido en obra
# (1,83 x 0,25), que sube de P1 al forjado. Se dibuja ya como pilar.
VIGA = None

# ------------------------------------------- pared en L de apoyo del vidrio
# Estructura nueva: tramo largo de 3,60 paralelo al muro Oeste, a 2,22 m de
# su cara interior, y doblez de 0,74 hacia el Oeste en su extremo Sur.
# Sostiene el panel de vidrio de 1,35 m de alto. Espesor sin medir.
PARED_L_E   = 0.100                     # espesor supuesto, comprobar
PARED_L_X   = 0.250 + 2.220             # cara Este del tramo largo = 2,470
PARED_L_LAR = ('Tramo largo 3,60',
               PARED_L_X - PARED_L_E, 9.008 - 3.600, PARED_L_X, 9.008)
PARED_L_DOB = ('Doblez 0,74',
               PARED_L_X - 0.740, 9.008 - 3.600, PARED_L_X, 9.008 - 3.600 + PARED_L_E)
H_VIDRIO_L  = 1.350                     # panel de vidrio que sostiene

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
# MEDIDO EN OBRA: el ventanal sur no es un solo pano corrido de 5,47. El P2
# llega hasta la fachada y lo parte en dos: un pano corto al Oeste (0,78, que
# es justo la distancia medida del muro al P2) y el pano largo de 4,00 al Este,
# mas una jamba de 0,11 contra el muro del cuello.
VENTANAL_SUR = dict(y=1.561, e=0.060, panos=[(0.510, 1.290), (1.870, 5.870)],
                    jamba=(5.870, 5.980))
# Escaparate: arranca en la cara Este de P5. La puerta de entrada mide 2,10 de
# ancho y barre 1,00 hacia el vestibulo; va pegada a P5.
ESCAPARATE = dict(x0=6.331, x1=9.710, y=0.370, e=0.049)
PUERTA_ACCESO = dict(x0=6.331, x1=8.431, y=0.370, ancho=2.100, barrido=1.000,
                     alto=2.100, hojas=2)

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

# ------------------------------------------- reservas de espacio (no estructura)
# El cliente marca donde van tres cosas. No son estructura: se grafian como
# reserva, con linea de trazos, para que el plano siga siendo estructural.
BARRA      = dict(x=2.470, y0=1.561, y1=1.561 + 3.400, largo=3.400)
PASO_PERS  = dict(x=2.470, y0=1.561 + 3.400, y1=9.008 - 3.600, medido=0.600)
SILLON     = dict(x0=2.470, x1=2.470 + 4.890, y=9.008, fondo=0.600, largo=4.890)

# --------------------------------------------------------------- superficies
SUP_PB_UTIL   = 75.63     # m2 dentro de muros, planta baja
SUP_FORJADO   = 33.74     # m2 de forjado de planta alta
SUP_DOBLE_ALT = 37.80     # m2 de vacio a doble altura
SUP_SOLAR     = 81.72     # m2 dentro del contorno exterior
RECINTOS_PA = [('Aseo (lavabo + inodoro)', 3.92), ('Almacen', 2.59),
               ('Paso / rellano', 3.33), ('Altillo diafano', 26.17)]

# ------------------------------------------------- discrepancias por resolver
# Puntos en los que los videos del local en obra no cuadran con el
# levantamiento, o que el levantamiento no recoge. Se dibuja el levantamiento
# (es la unica fuente acotada) y se listan aqui para medir en obra.
COMPROBAR = [
    'La cota de 2,70 anotada contra la medianera norte no cuadra: mide la '
    'misma distancia que el 2,22 aplicado (muro Oeste a pared en L). '
    'Aclarar qué mide ese 2,70.',
    'Canto del forjado del altillo. Con 2,56 m de suelo a suelo, la altura '
    'libre de planta baja es 2,56 menos ese canto, no los 2,70 supuestos.',
    'Espesor de la pared en L y del panel de vidrio de 1,35 m que sostiene.',
    'Posición de P3: el 3,15 de la planta baja y el 1,90 de la planta alta se '
    'llevan 0,15; el 2,94 y el 3,20 se llevan 0,26. Se dibuja con la cadena '
    'de planta baja.',
    'Del P3 a la escalera se midió 2,35 y en el plano salen 2,75. Los 0,40 de '
    'diferencia no cierran contra la medianera Este.',
    'P5: se dibuja 0,60 x 1,00 con la cara Oeste a plomo con el muro del '
    'cuello. El resalto de 0,20 al Este anotado da 0,35 en esa posición.',
    'Escaparate: bajo él aparece un 2,70 sin aclarar. Se dibuja el hueco '
    'completo con la puerta de 2,10 pegada a P5.',
    'Tabica de la escalera: 2,56/17 = 0,151 m. Contar los peldaños en obra '
    'para confirmar que son 17.',
    'Machones trasdosados con placa de yeso nueva: la sección de hormigón '
    'no es verificable a la vista.',
]
