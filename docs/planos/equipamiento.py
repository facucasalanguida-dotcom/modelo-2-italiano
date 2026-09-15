# -*- coding: utf-8 -*-
"""
EQUIPAMIENTO DE BARRA Y COCINA — medidas en metros.

Revision del 15/09 sobre el croquis del cliente. Cada maquina es un producto
real del marketplace de makro.es, con el ancho, fondo y alto de su ficha.
Las dos vitrinas y la cafetera no se buscaron: ya estan compradas y el
cliente dio sus medidas. Las mesas de sala llevan medidas promedio.

La web de Makro bloquea el acceso directo desde servidores: las medidas
salen de las fichas tal y como las indexa su buscador. Comprobar la ficha
antes de comprar.

Recintos (plano de estructura revisado el 15/09):

    COCINA   x 0,250 .. 2,370   y 4,888 .. 9,008   muro Oeste, medianera
             Norte y pared en L (4,22); entrada bajo la viga P1b, entre P1
             y el doblez de la pared en L.
    BARRA    x 0,250 .. 2,470   y 1,561 .. 4,788   trasbarra contra el muro
             Oeste; mostrador delantero en la linea de la pared en L.
"""

MAKRO = 'https://www.makro.es/marketplace/product/'

# ------------------------------------------------------------------ recintos
COCINA = dict(x0=0.250, x1=2.370, y0=4.888, y1=9.008)
BARRA  = dict(x0=0.250, x1=2.470, y0=1.561, y1=4.788)
H_ENCIMERA = 0.900
H_CAMPANA  = 2.000                       # borde inferior de la campana

# Un producto: (rotulo, nombre, ancho, fondo, alto, id de makro o None)
P = lambda t, n, a, f, h, u=None: dict(tag=t, nombre=n, a=a, f=f, h=h, url=(MAKRO + u) if u else None)

# ============================================================== COCINA
# --- Linea de coccion en la medianera Norte, bajo la campana corrida.
#     De Oeste a Este, sobre una bancada de apoyo a medida de 0,60 de fondo.
COCCION_Y = (8.408, 9.008)
COCCION_X0 = 0.250
COCCION = [
    P('K1', 'Placa de inducción Bartscher, 2 zonas Ø230, 6 kW, 400 V',
      0.700, 0.455, 0.120, '623ef78b-af50-4e27-a2c5-b3a45089ba59'),
    P('K2', 'Cocedor de pasta eléctrico METRO Professional GNC1008, 8 L, 4 cestos',
      0.470, 0.550, 0.380, '85f3fb44-3f09-463c-ab29-53822c8c1ce7'),
    P('K3', 'Freidora profesional 1 cuba de 7 L, eléctrica',
      0.270, 0.460, 0.370, '57e9d9ed-d483-4f88-a049-5597b3a7ad18'),
    P('K4', 'Plancha eléctrica Cleiton 50 cm, placa de 8 mm, sobremesa',
      0.550, 0.500, 0.330, 'acd212b2-73a4-42bc-bea7-329d5ab4771d'),
]
BANCADA_COCCION = dict(x0=0.250, x1=2.370, y0=8.408, y1=9.008)   # a medida
CAMPANA = P('KC', 'Campana extractora industrial recta, sin turbina, AISI-304 satinado, 2000 × 1200 × 500',
            2.000, 1.200, 0.500, 'a8240770-cb5f-491b-926d-83b1e1e00a22')
CAMPANA_POS = dict(x0=0.310, x1=2.310, y0=9.008 - 1.200, y1=9.008)

# --- Muro Oeste, de Norte a Sur, a partir de la esquina de la coccion.
#     La tabla cubre el lavavajillas y enlaza la pileta con el horno.
OESTE_X0 = 0.250
OESTE_Y0 = 8.408
OESTE = [
    P('K5', 'Horno de convección eléctrico industrial, 4 bandejas 45 × 33',
      0.590, 0.595, 0.575, 'e3c35b3b-14d3-4e2b-a109-373a863ddff9'),
    P('K6', 'Lavavajillas industrial ST500, cesta 50 × 50, bajo la tabla',
      0.565, 0.651, 0.833, 'b6893f6e-6c55-499e-8e8b-4e246d107961'),
    P('K7', 'Fregadero industrial Royal Catering, 1 cubeta 50 × 50, 70 × 70',
      0.700, 0.700, 0.850, '987fd316-3c44-48e2-a628-d88809ed245c'),
    P('K8', 'Armario refrigerado vertical AR400L Clima Hostelería, inox, 360 L',
      0.600, 0.615, 1.870, 'd48c3c0c-7975-4c22-89c7-64676c23681f'),
    P('K9', 'Armario refrigerado vertical AR400L Clima Hostelería, inox, 360 L',
      0.600, 0.615, 1.870, 'd48c3c0c-7975-4c22-89c7-64676c23681f'),
]
TABLA_OESTE = ('K6',)                    # modulos cubiertos por la tabla

# --- Pared en L: nevera corrida de acero inoxidable usada como mesada,
#     con las puertas debajo. Dos mesas refrigeradas de 0,70 de fondo.
ESTE_X1 = 2.370
ESTE_Y0 = 8.408
ESTE = [
    P('K10', 'Mesa refrigerada METRO Professional GCC3100, inox, 3 puertas, 334 L',
      1.795, 0.700, 0.850, '176b30f1-81b0-4a52-916e-80722d9a9240'),
    P('K11', 'Mesa refrigerada bajo mostrador, 2 puertas, ventilada, mural',
      1.360, 0.700, 0.850, '4a434762-a949-4461-ab52-6b1e3e4319cc'),
]
ESTE_SOBRE = [
    P('A5', 'Cortadora de fiambre (medida promedio)', 0.550, 0.500, 0.450),
]

# ================================================================ BARRA
# --- Trasbarra contra el muro Oeste, de Norte (P1) a Sur, 2,75 m.
TRASBARRA_X = (0.250, 0.850)
TRASBARRA_Y = (2.009, 4.759)
TRASBARRA = [
    P('A1', 'Cafetera (comprada), 2 grupos', 1.200, 0.600, 0.500),
    P('A2', 'Lavamanos inox con grifo y pulsador de pedal, cuba Ø340',
      0.400, 0.400, 0.850, '6105678f-3159-4172-a17a-f400760f0b35'),
    P('A3', 'Fabricador de hielo Gastro M CT694, 28 kg/24 h (bajo encimera)',
      0.400, 0.460, 0.670, 'e3db53e1-8f64-4495-bb2c-59fe355a32e2'),
    P('A4', 'Exprimidor de naranjas Mizumo Next Gen',
      0.480, 0.350, 0.735, 'a7c3e878-0cdd-4f7e-b013-897ae4f6120d'),
]
# Sobre la hielera, encima de la encimera:
LICUADORA = P('A3b', 'Licuadora industrial Sammic Li-240', 0.205, 0.310, 0.360,
              '2b8d9850-b422-4738-b716-c30da9857300')
MODULO_TECNICO = 0.600                   # bajo la cafetera, extremo Norte

# --- Mostrador delantero en la linea de la pared en L, del ventanal al paso.
#     Medido 2,80; en el plano quedan 2,63 hasta el paso de personal.
MOSTRADOR_X = (1.870, 2.470)
MOSTRADOR_Y = (1.561, 4.188)
VITRINA = dict(largo=1.000, fondo_cristal=0.700, hueco_bajo=0.600,
               motor=(0.300, 0.300))    # motor abajo, a la izquierda (Sur)
VITRINAS = [
    P('V2', 'Vitrina refrigerada (comprada), 1,00 × 0,70; debajo, lavavasos',
      1.000, 0.700, 1.250),
    P('V1', 'Vitrina refrigerada (comprada), 1,00 × 0,70; debajo, barriles',
      1.000, 0.700, 1.250),
]
LAVAVASOS = P('B1', 'Lavavasos Elettrobar FAST 40, cesta 40 × 40 (bajo la vitrina V2)',
              0.440, 0.540, 0.670, 'e858e346-8373-4e64-aa03-6f9a559e168e')
BARRILES = P('B2', 'Barriles de cerveza de 30 L, Ø 0,32 (bajo la vitrina V1)',
             0.320, 0.320, 0.600)
BARRA_MADERA = dict(y0=3.561, y1=4.188)   # tabla de madera, 0,63
TABLET = P('B3', 'Caja: tablet sobre soporte', 0.250, 0.200, 0.250)
CHOPERA = P('B4', 'Columna de cerveza de 2 grifos (Makro sólo lista la de 3, bandeja 40 × 40)',
            0.400, 0.400, 0.550, 'f2d9d7ba-6f4f-4feb-b032-641cc4d828fe')
TABLA_P2 = dict(x0=0.510, x1=1.290, y0=1.561, y1=2.011)   # tabla de P2 al muro

# --------------------------------------------------------------- holguras
PASILLO_COCINA_MIN = COCINA['x1'] - COCINA['x0'] - 0.651 - 0.700   # 0,77
PASILLO_COCINA = COCINA['x1'] - COCINA['x0'] - 0.600 - 0.700       # 0,82
PASILLO_BARRA  = MOSTRADOR_X[0] - TRASBARRA_X[1]                   # 1,02


def todos():
    """Lista plana de todo lo que hay que comprar, en orden de lamina."""
    return (COCCION + [CAMPANA] + OESTE + ESTE + ESTE_SOBRE + TRASBARRA +
            [LICUADORA] + VITRINAS + [LAVAVASOS, BARRILES, TABLET, CHOPERA])
