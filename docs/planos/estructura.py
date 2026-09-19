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
# Cerramiento de la escalera en planta baja: su cara Oeste esta a 2,33 de P3
# (medida del cliente, 19 set.); en el altillo la barandilla queda en
# 8,759..8,811. El espesor de 0,161 es lo que cierra la cadena Este-Oeste.
CAJA_ESC_PB = ('Caja de escalera (planta baja)', 8.650, 3.939, 8.811, 7.738)

# ------------------------------------------------------- contorno del solar
PERIMETRO = [(0.000, 9.156), (10.040, 9.156), (10.040, 0.330),
             (6.230, 0.330), (6.230, 0.000), (5.731, 0.000),
             (5.731, 1.561), (0.000, 1.561)]

# ------------------------------------------------------------------- muros
# (nombre, x0, y0, x1, y1, espesor_nominal)
MUROS = [
    # El muro Norte es macizo hasta el borde del solar (9,156). Su cara
    # interior es 8,777 en casi todo y 8,927 en los 2,18 de la cocina: el
    # hundimiento es ese escalon, y el muro es mas grueso donde no lo hay.
    ('Medianera Norte',            2.430, 8.957, 10.040, 9.156, 0.199),
    ('Medianera Norte - cocina',   0.000, 9.008,  2.430, 9.156, 0.148),
    ('Muro Oeste',                 0.000, 2.009,  0.250, 9.008, 0.250),
    ('Muro Oeste - esquina SO',    0.000, 1.561,  0.510, 2.009, 0.448),
    ('Muro Sur (con ventanal)',    0.510, 1.561,  5.980, 1.810, 0.249),
    ('Muro Oeste del cuello',      5.731, 0.960,  5.980, 1.561, 0.249),
    ('Medianera Este',             9.890, 1.429, 10.040, 8.957, 0.150),
    ('Medianera Este - cuello',    9.710, 0.330, 10.040, 1.429, 0.330),
]

# MURO NORTE — cadena del cliente del 19 set. (noche), medida de Sur a Norte
# por la linea de la barra y de la pared en L:
#
#   1,968  cara interior del zocalo del ventanal
#   +2,79  barra                     -> 4,759  (cara Sur de P1)
#   +0,60  paso de personal          -> 5,357  (cara NORTE de P1 = base de la L)
#   +3,60  pared en L                -> 8,957  (cara interior del muro Norte)
#   +0,05  hundimiento               -> 9,008  (pared hundida de la cocina)
#
# Con la L en 3,60 el muro Norte queda en 0,199 de espesor en la sala y en
# 0,148 en la cocina, que es justo el espesor del levantamiento; y de la
# pared hundida a la cara Norte de P1 salen 3,651, o sea los 3,65 que el
# cliente midio en el muro Oeste "incluyendo el hundimiento".
#
# No hay trasdosado ni nada por delante: el muro es macizo hasta el borde
# del solar (9,156). Su espesor queda en COMPROBAR EN OBRA.
MED_EXT       = 9.156                   # cara exterior, borde del solar
MURO_N_COCINA = 9.008                   # cara interior en los 2,18 de la cocina
MURO_N        = 8.957                   # cara interior en el resto
HUNDIMIENTO = dict(x0=0.250, x1=2.430, y0=MURO_N, y1=MURO_N_COCINA,
                   p=round(MURO_N_COCINA - MURO_N, 3), largo=2.180)

# -------------------------------------------------- pilares y machones (PB)
# (rotulo, nombre, x0, y0, x1, y1)
# Secciones y posiciones MEDIDAS EN OBRA (revision del 14/09). El P2 se
# completa hasta la linea del ventanal: en obra llega hasta la fachada.
# P1b es el machon que sube desde P1 hasta el forjado del altillo.
# P3 (16/09): 0,65 x 1,07, colocado con las medidas del cliente: 3,20 desde
# la pared en L (medido en el altillo desde el borde del forjado), 3,25 de su
# cara Norte a la medianera Norte, 0,70 de su cara Sur a la barandilla del
# altillo (3,988). En planta baja midio 2,35 hasta la escalera y en el altillo
# 2,50: la caja de escalera de planta baja es mas gruesa (cara Oeste en 8,670,
# ver CAJA_ESC_PB) que la barandilla del altillo (8,759). El levantamiento daba
# el pilar en 5,62..6,22 y la correccion del 14/09 lo habia llevado a 5,41.
PILARES = [
    ('P1',  'Machón del muro Oeste',       0.250, 4.759, 0.550, 5.357),
    ('P2',  'Pilastra del muro Sur',       1.290, 1.561, 1.870, 2.011),
    ('P3',  'Pilar central',               5.670, 4.688, 6.320, 5.758),
    ('P4',  'Machón de la medianera Este', 9.689, 4.708, 9.890, 5.309),
    ('P5',  'Pilar de fachada',            5.731, 0.000, 6.331, 1.000),
]
# Pilares que atraviesan el forjado y siguen en planta alta. P5 es el machon
# de fachada entre el ventanal sur y el escaparate: en los videos se ve subir
# hasta el techo del altillo, por encima de la coronacion del vidrio.
PILARES_PA = ['P3', 'P4', 'P5']

# Viga P1b: el elemento de 1,83 x 0,25 que sale de P1 hasta la pared en L y
# sube al forjado. Al ser viga no corta el plano de seccion: por debajo de
# ella se entra a la cocina, entre P1 y el doblez de la pared en L.
VIGA = ('Viga P1b', 0.550, 4.933, 2.380, 5.183)

# ------------------------------------------- pared en L de apoyo del vidrio
# Estructura nueva. Medidas del cliente del 19 set.: la pared arranca en la
# muro Norte y baja hasta la cara Norte de P1, con el doblez de 0,74 hacia el
# Oeste en su extremo Sur. Largo resultante: 3,42.
# Su cara Oeste arranca donde termina el hundimiento (2,430).
# Sostiene el panel de vidrio de 1,35 m de alto. Espesor sin medir.
PARED_L_E   = 0.100                     # espesor supuesto, comprobar
# 19 set. (tarde): el cliente pide pegar la pared en L al final del
# hundimiento, sin dejar el paño de 0,13 que quedaba entre los dos. Su cara
# Oeste va a 2,430 y la Este a 2,530, con lo que hasta P3 quedan 3,14 en vez
# de los 3,01 que habia medido: P3 no se mueve, la pared si.
PARED_L_X   = 2.530                     # cara Este; cara Oeste en 2,430
PARED_L_LARGO = round(MURO_N - 5.357, 3)   # 3,60: la base cae en la cara Norte de P1
PARED_L_LAR = (f'Tramo largo {PARED_L_LARGO:.2f}'.replace('.', ','),
               PARED_L_X - PARED_L_E, MURO_N - PARED_L_LARGO, PARED_L_X, MURO_N)
PARED_L_DOB = ('Doblez 0,74',
               PARED_L_X - 0.740, MURO_N - PARED_L_LARGO, PARED_L_X,
               MURO_N - PARED_L_LARGO + PARED_L_E)
H_PARED_L   = 1.220                     # altura de la pared en L, medida
H_VIDRIO_L  = 1.350                     # panel de vidrio que sostiene

# ---------------------------------------------------- forjado de planta alta
FORJADO = [(2.461, MURO_N), (9.890, MURO_N), (9.890, 7.738), (8.811, 7.738),
           (8.811, 3.939), (2.411, 3.939), (2.411, 7.509), (2.461, 7.509)]

# Barandillas de vidrio del borde del vacio (e = 0,05 · h = 1,00)
BARANDILLAS = [
    ('Borde Oeste del vacio',   2.411, 3.988, 2.461, 7.509),
    ('Borde Sur del vacio',     2.411, 3.939, 8.759, 3.988),
    ('Caja de escalera',        8.759, 3.939, 8.811, 7.738),
]

# -------------------------------------------- particiones de planta alta
TABIQUES_PA = [
    ('Tabique Oeste del aseo',        2.461, 7.509, 2.560, MURO_N),
    ('Tabique Sur - tramo Oeste',     2.560, 7.509, 3.089, 7.607),
    ('Tabique Sur - tramo Este',      3.849, 7.509, 7.511, 7.607),
    ('Tabique del inodoro',           4.461, 7.607, 4.560, 8.208),
    ('Tabique aseo / almacen',        5.459, 7.607, 5.558, MURO_N),
    ('Tabique Este del almacen',      7.408, 7.607, 7.511, 8.072),
]
# (nombre, x0, y0, x1, y1, ancho, eje) — eje 'x' = hoja barre en X
# El ancho es el del hueco que dejan los tabiques, calculado y no escrito:
# al bajar el muro Norte a 8,957 las dos puertas que dan a el se quedaron
# mas estrechas que los 0,80 y 0,94 que tenian cuando el muro estaba en
# 9,008 (0,749 y 0,885). El hueco manda, y asi la hoja no se mete en el muro.
_HUECOS_PA = [
    ('Puerta aseo',    3.089, 7.509, 3.849, 7.607, 'x'),
    ('Puerta inodoro', 4.461, 8.208, 4.560, MURO_N, 'y'),
    ('Puerta almacen', 7.408, 8.072, 7.511, MURO_N, 'y'),
]
HUECOS_PA = [(nm, x0, y0, x1, y1,
              round(x1 - x0 if eje == 'x' else y1 - y0, 3), eje)
             for nm, x0, y0, x1, y1, eje in _HUECOS_PA]

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
# La puerta va a la DERECHA (contra la medianera Este) y el escaparate a la
# izquierda, pegado a P5. Medidas del cliente del 19 set.: 1,31 de P5 a la
# jamba del vestibulo, 2,06 de ancho de puerta y 1,00 de fondo de vestibulo.
PUERTA_ACCESO = dict(x0=7.641, x1=9.701, y=0.370, ancho=2.060, barrido=1.000,
                     alto=2.100, hojas=2)
VESTIBULO = dict(x0=7.641, x1=9.890, y0=0.370, y1=1.429, fondo=1.059)

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
# Medidas del cliente del 19 set.: del muro Oeste al arranque de la barra hay
# 1,65, la barra mide 2,79 de largo y arranca en el zocalo del ventanal. Con
# eso termina justo en la cara Sur de P1 y su frente cae en la linea de la
# pared en L, de donde sale el fondo de 0,76. El paso de personal que queda
# entre el final de la barra y la base de la pared en L es de 0,95.
BARRA      = dict(x0=1.900, x1=PARED_L_X, y0=1.968, y1=4.759,
                  largo=4.759 - 1.968, fondo=PARED_L_X - 1.900, medido=2.790)
PASO_PERS  = dict(x0=BARRA['x0'], x1=PARED_L_X, y0=4.759,
                  y1=MURO_N - PARED_L_LARGO, medido=0.598)
SILLON     = dict(x0=PARED_L_X, x1=7.400, y=MURO_N, fondo=0.600,
                  largo=7.400 - PARED_L_X)

# Zocalo de piedra del ventanal Sur: el cliente mide 2,72 de la cara Sur de P3
# a su cara interior, lo que le da 0,347 de fondo desde el vidrio (0,10 por
# delante de la cara interior del muro del ventanal). Alto H_ZOCALO.
ZOCALO_SUR = dict(x0=0.510, x1=5.870, y0=1.621, y1=1.968, fondo=0.347)

# ------------------------------------------------- aire acondicionado (techo)
# UNA sola maquina, un cassette de techo de 4 vias. El cliente lo corrige el
# 20 set.: antes se habian dibujado dos y solo hay uno. En sus fotos aparece
# empotrado en el techo bajo (el intrados del forjado del altillo), a la
# izquierda del pilar mirando al Norte, es decir al OESTE de P3 y pegado a el.
# Se coloca centrado con P3 y a 0,10 de su cara Oeste. El panel estandar es de
# 0,95 x 0,95. Posicion tomada de las fotos: falta medirla en obra.
AIRE = [
    ('AC1', 'Cassette de techo 4 vías, bajo el forjado',
     5.070, 5.223, 0.95, 0.95),
]
AIRE_REJILLA = None          # el cassette de 4 vias retorna por su centro

# ------------------------------------------------------ bano de planta baja
# Nuevo, croquis del cliente del 15/09: rincon NE, entre la medianera Norte,
# la medianera Este y el desembarco de la escalera. Puerta de 0,70 abriendo
# hacia dentro, bisagra en la jamba Este.
BANO = dict(x0=7.400, x1=9.890, y0=7.730, y1=MURO_N, e=0.100)
BANO_TABIQUES = [
    ('Tabique Oeste del baño', 7.400, 7.730, 7.500, MURO_N),
    ('Tabique Sur - tramo Oeste', 7.400, 7.730, 7.770, 7.830),
    ('Tabique Sur - tramo Este', 8.470, 7.730, 9.890, 7.830),
]
BANO_PUERTA = dict(x0=7.770, x1=8.470, y=7.730, ancho=0.700, bisagra='E')

# --------------------------------------------------------------- superficies
SUP_PB_UTIL   = 75.25     # m2 dentro de muros, planta baja (con el hundimiento)
SUP_FORJADO   = 33.36     # m2 de forjado de planta alta
SUP_DOBLE_ALT = 37.79     # m2 de vacio a doble altura
SUP_SOLAR     = 81.72     # m2 dentro del contorno exterior
RECINTOS_PA = [('Aseo (lavabo + inodoro)', 3.77), ('Almacen', 2.50),
               ('Paso / rellano', 3.33), ('Altillo diafano', 26.04)]

# ------------------------------------------------- discrepancias por resolver
# Puntos en los que los videos del local en obra no cuadran con el
# levantamiento, o que el levantamiento no recoge. Se dibuja el levantamiento
# (es la unica fuente acotada) y se listan aqui para medir en obra.
COMPROBAR = [
    'Muro Norte: macizo hasta el solar, 0,148 en la cocina (el del levantamiento) y 0,199 '
    'en el resto. Medir ese espesor y el hundimiento de 0,05 entre los dos.',
    'Canto del forjado del altillo. Con 2,56 m de suelo a suelo, la altura '
    'libre de planta baja es 2,56 menos ese canto, no los 2,70 supuestos.',
    'P1b se dibuja como viga (1,83 × 0,25) y no como pilar: si fuera macizo '
    'hasta el suelo, la cocina no tendría entrada. Medir su intradós.',
    'Zócalo del ventanal: 0,347 desde el vidrio, deducido de los 2,72 de P3 a su cara '
    'interior; sobresale 0,16 del muro del ventanal (0,25). Medirlo directamente.',
    'Muro Oeste de la cocina: los cuatro aparatos suman 3,04 y entre P1 y la bancada hay '
    '3,05. Entran con 1 cm de holgura: confirmar los anchos reales antes de comprar.',
    'La pared en L queda 0,10 al Este del borde del forjado del levantamiento: el '
    'vidrio de 1,35 sobre ella (2,57 en total) no pasa bajo el altillo. Medir ese borde.',
    'Vestíbulo: los 1,31 y 2,23 del cliente suman 3,54 y de P5 al muro Este hay 3,559. '
    'Se dibuja el 1,31 medido y el resto queda en 2,25, 2 cm más que su medida.',
    'P3 no se mueve: los 3,23 a la medianera dan 3,25 medidos al muro desnudo (2,98 al '
    'trasdosado) y los 3,65 a P5 se dibujan 3,69. Confirmar a qué cara se midió.',
    'Aire acondicionado: un cassette situado con las fotos del cliente, con panel '
    'estándar de 0,95 y rejilla de 0,90 × 0,50. Medir posición y tamaño reales.',
]
