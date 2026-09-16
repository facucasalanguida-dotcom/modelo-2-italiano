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

    COCINA   x 0,250 .. 2,370   y 5,450 .. 9,008   muro Oeste, medianera
             Norte y pared en L (3,66 + doblez 0,74); entrada bajo la viga
             P1b, entre P1 y el doblez de la pared en L (1,18).
    BARRA    x 0,250 .. 2,470   y 1,561 .. 5,350   trasbarra contra el muro
             Oeste; mostrador delantero en la linea de la pared en L hasta
             4,75; paso de personal de 0,60 hasta la pared en L.
"""

MAKRO = 'https://www.makro.es/marketplace/product/'

# ------------------------------------------------------------------ recintos
COCINA = dict(x0=0.250, x1=2.370, y0=5.450, y1=9.008)
BARRA  = dict(x0=0.250, x1=2.470, y0=1.561, y1=5.350)
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
CAMPANA = P('KC', 'Campana extractora industrial recta, sin turbina, AISI-304 satinado, 2 × 1,2 m',
            2.000, 1.200, 0.500, 'a8240770-cb5f-491b-926d-83b1e1e00a22')
CAMPANA_POS = dict(x0=0.310, x1=2.310, y0=9.008 - 1.200, y1=9.008)

# --- Muro Oeste, de Norte a Sur, a partir de la esquina de la coccion.
#     La tabla cubre el lavavajillas y enlaza la pileta con el horno.
#     Largo disponible hasta P1: 8,408 - 5,357 = 3,051. Suma: 3,007 (44 mm).
#     En makro.es no hay armario refrigerado inox de puerta ciega de menos
#     de 0,626 de ancho; el fregadero baja a 0,60 para que entren los dos.
OESTE_X0 = 0.250
OESTE_Y0 = 8.408
OESTE = [
    P('K5', 'Horno de convección eléctrico industrial, 4 bandejas 45 × 33',
      0.590, 0.595, 0.575, 'e3c35b3b-14d3-4e2b-a109-373a863ddff9'),
    P('K6', 'Lavavajillas industrial ST500, cesta 50 × 50, bajo la tabla',
      0.565, 0.651, 0.863, 'b6893f6e-6c55-499e-8e8b-4e246d107961'),
    P('K7', 'Fregadero industrial Distform gama 600, 1 cubeta 50 × 40, con puerta, peto 105',
      0.600, 0.600, 0.850, '3efac5b4-e702-4af6-9dd9-533709488190'),
    P('K8', 'Armario refrigerado vertical Edenox APS-451 I, inox, 1 puerta, 395 L',
      0.626, 0.740, 1.865, '2e636462-1801-45f6-a3d8-15413909cb8c'),
    P('K9', 'Armario refrigerado vertical Edenox APS-451 I, inox, 1 puerta, 395 L',
      0.626, 0.740, 1.865, '2e636462-1801-45f6-a3d8-15413909cb8c'),
]
TABLA_OESTE = ('K6',)                    # modulos cubiertos por la tabla

# --- Pared en L: nevera corrida de acero inoxidable usada como mesada,
#     con las puertas debajo. UNA sola mesa refrigerada, la mas larga que
#     lista makro.es (ninguna pasa de 2,545) para los 2,96 m que hay entre
#     la bancada de coccion y el doblez de la pared en L. Va pegada al
#     doblez (base de la L, extremo Sur) y los 0,42 libres quedan junto a la
#     bancada de coccion. Foto de referencia del cliente: METRO GCF3100BS
#     179,5 x 70 x 85, 3 puertas (esa es de congelacion).
ESTE_X1 = 2.370
ESTE_LARGO = 2.542                         # largo de la mesa (ficha)
ESTE_Y0 = COCINA['y0'] + ESTE_LARGO        # 7,992: borde Norte de la mesa
ESTE = [
    P('K10', 'Mesa refrigerada Infrico 4 puertas, AISI-304, peto 100 mm, -2/+8 ºC, 530 L',
      2.542, 0.600, 0.850, '764bc52f-1287-4e08-89dc-c2e453dfea49'),
]
# Alternativas con la misma funcion, por si se prefiere el fondo de 0,70 de
# la foto de referencia (no se dibujan):
ESTE_ALT = [
    P('K10 alt', 'Mesa refrigerada Vaiotec EASYLINE, inox, 4 puertas, GN 1/1, 553 L',
      2.230, 0.700, 0.850, '230e627d-7291-43e0-a2b4-ebbf6e783f27'),
    P('K10 alt', 'METRO Professional GCC3100, inox, 3 puertas, 334 L (la de la foto, refrigerada)',
      1.795, 0.700, 0.850, '176b30f1-81b0-4a52-916e-80722d9a9240'),
]
OESTE_ALT = [
    P('K8/K9 alt', 'Armario frigorífico ventilado 400 L, acero inoxidable (Diamond)',
      0.626, 0.740, 1.925, '8969b667-b5cb-4e83-b599-3dd45c112547'),
    P('K8/K9 alt', 'Armario refrigerado AR400L Clima Hostelería, lacado blanco (no inox), 360 L',
      0.600, 0.615, 1.870, 'd48c3c0c-7975-4c22-89c7-64676c23681f'),
    P('K7 alt', 'Fregadero Royal Catering, 1 cubeta 50 × 50, 70 × 70 (alto sin dato en ficha)',
      0.700, 0.700, 0.850, '987fd316-3c44-48e2-a628-d88809ed245c'),
]
ESTE_SOBRE = []

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
#     Croquis del 15/09: llega hasta y=4,75, justo antes del paso de 0,60.
MOSTRADOR_X = (1.870, 2.470)
MOSTRADOR_Y = (1.561, 4.750)
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
BARRA_MADERA = dict(y0=3.561, y1=4.750)   # tabla de madera, 1,19
TABLET = P('B3', 'Caja: tablet sobre soporte', 0.250, 0.200, 0.250)
CHOPERA = P('B4', 'Columna de cerveza en T de 3 grifos, bandeja 40 × 40 (no la hay de 2 en Makro)',
            0.400, 0.400, 0.550, 'f2d9d7ba-6f4f-4feb-b032-641cc4d828fe')
TABLA_P2 = dict(x0=0.510, x1=1.290, y0=1.561, y1=2.011)   # tabla de P2 al muro

# --------------------------------------------------------------- holguras
def _oeste_frente_a_mesada():
    """Fondos de los modulos del muro Oeste que quedan frente a la mesada."""
    y_fin = ESTE_Y0 - sum(p['a'] for p in ESTE)
    y, fondos = OESTE_Y0, []
    for p in OESTE:
        if y > y_fin:                       # el modulo empieza frente a la mesada
            fondos.append(p['f'])
        y -= p['a']
    return fondos

_F = _oeste_frente_a_mesada()
ANCHO_COCINA = COCINA['x1'] - COCINA['x0']                          # 2,12
PASILLO_COCINA_MIN = ANCHO_COCINA - max(_F) - ESTE[0]['f']         # 0,78
PASILLO_COCINA = ANCHO_COCINA - 0.600 - ESTE[0]['f']               # 0,92 frente al fregadero
PASILLO_BARRA  = MOSTRADOR_X[0] - TRASBARRA_X[1]                   # 1,02
LIBRE_ESTE = BANCADA_COCCION['y0'] - ESTE_Y0                         # 0,42 junto a la coccion
LARGO_OESTE = OESTE_Y0 - 5.357                                      # 3,051 hasta P1
SUMA_OESTE = sum(p['a'] for p in OESTE)                             # 3,007


def todos():
    """Lista plana de todo lo que hay que comprar, en orden de lamina."""
    return (COCCION + [CAMPANA] + OESTE + ESTE + ESTE_SOBRE + TRASBARRA +
            [LICUADORA] + VITRINAS + [LAVAVASOS, BARRILES, TABLET, CHOPERA])
