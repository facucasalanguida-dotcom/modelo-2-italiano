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

Recintos (plano de estructura revisado el 19/09 con las medidas del cliente):

    COCINA   x 0,250 .. 2,560   y 5,808 .. 9,008 (9,283 en el hundimiento de
             2,18 de la medianera Norte); entrada bajo la viga P1b, entre P1
             y el doblez de la pared en L (1,36).
    BARRA    x 0,250 .. 2,660   y 1,968 .. 5,708   trasbarra contra el muro
             Oeste entre P1 y P2; mostrador delantero en la linea de la pared
             en L, del zocalo del ventanal a P1; paso de personal de 0,95.
"""

MAKRO = 'https://www.makro.es/marketplace/product/'

# ------------------------------------------------------------------ recintos
COCINA = dict(x0=0.250, x1=2.560, y0=5.808, y1=9.008)
NICHO  = dict(x0=0.250, x1=2.430, y0=9.008, y1=9.283)   # hundimiento medido
BARRA  = dict(x0=0.250, x1=2.660, y0=1.968, y1=5.708)
H_ENCIMERA = 0.900
H_CAMPANA  = 2.000                       # borde inferior de la campana

# Un producto: (rotulo, nombre, ancho, fondo, alto, id de makro o None)
P = lambda t, n, a, f, h, u=None: dict(tag=t, nombre=n, a=a, f=f, h=h, url=(MAKRO + u) if u else None)

# ============================================================== COCINA
# --- Linea de coccion en la medianera Norte, bajo la campana corrida.
#     De Oeste a Este, sobre una bancada de apoyo a medida de 0,60 de fondo.
# La bancada de coccion y la campana se meten en el hundimiento de 0,275,
# como pidio el cliente: ocupan justo los 2,18 del nicho.
COCCION_Y = (NICHO['y1'] - 0.600, NICHO['y1'])
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
BANCADA_COCCION = dict(x0=NICHO['x0'], x1=NICHO['x1'], y0=COCCION_Y[0],
                       y1=COCCION_Y[1])                          # a medida
CAMPANA = P('KC', 'Campana extractora industrial recta, sin turbina, AISI-304 satinado, 2 × 1,2 m',
            2.000, 1.200, 0.500, 'a8240770-cb5f-491b-926d-83b1e1e00a22')
CAMPANA_POS = dict(x0=0.310, x1=2.310, y0=NICHO['y1'] - 1.200, y1=NICHO['y1'])

# --- Muro Oeste, de Norte a Sur, a partir de la esquina de la coccion.
#     Fregadero con bastidor y hueco de lavavajillas (croquis del cliente,
#     16/09): cuba a la izquierda mirando al muro, es decir al Sur, y el
#     escurridor al Norte con el lavavajillas K6 debajo. Ya no hay tabla.
#     Largo disponible hasta P1: 8,408 - 5,357 = 3,051. Suma: 3,042 (9 mm).
#     En makro.es no hay armario refrigerado inox de puerta ciega de menos
#     de 0,626 de ancho.
#     Ficha facilitada por el cliente (el buscador de Makro no la indexa):
#     "Fregadero con bastidor con hueco lavavajillas cuba izquierda
#     1200x600x850 mm", Ref. AAA0045913963, 395 EUR (477,95 IVA incl.).
OESTE_X0 = 0.250
OESTE_Y0 = COCCION_Y[0]
FREGADERO = P('K7', 'Fregadero con bastidor con hueco lavavajillas, cuba izquierda, 1200 × 600',
              1.200, 0.600, 0.850, 'c0cd57f0-35a2-485a-98f4-5dffc628d84e')
FREGADERO['ref'] = 'AAA0045913963'
FREGADERO['precio'] = '395,00 € (477,95 € IVA incl.)'
CUBA = dict(largo=0.500, fondo=0.400)    # cuba embutida, medida habitual
HUECO_LAV = 0.600                        # mitad Norte del fregadero, bajo el escurridor
LAVAVAJILLAS = P('K6', 'Lavavajillas industrial ST500, cesta 50 × 50, bajo el escurridor de K7',
                 0.565, 0.651, 0.863, 'b6893f6e-6c55-499e-8e8b-4e246d107961')
OESTE = [
    P('K5', 'Horno de convección eléctrico industrial, 4 bandejas 45 × 33',
      0.590, 0.595, 0.575, 'e3c35b3b-14d3-4e2b-a109-373a863ddff9'),
    FREGADERO,
    P('K8', 'Armario refrigerado vertical Edenox APS-451 I, inox, 1 puerta, 395 L',
      0.626, 0.740, 1.865, '2e636462-1801-45f6-a3d8-15413909cb8c'),
    P('K9', 'Armario refrigerado vertical Edenox APS-451 I, inox, 1 puerta, 395 L',
      0.626, 0.740, 1.865, '2e636462-1801-45f6-a3d8-15413909cb8c'),
]

# --- Pared en L: nevera corrida de acero inoxidable usada como mesada,
#     con las puertas debajo. UNA sola mesa refrigerada, la mas larga que
#     lista makro.es (ninguna pasa de 2,545) para los 2,96 m que hay entre
#     la bancada de coccion y el doblez de la pared en L. Va pegada al
#     doblez (base de la L, extremo Sur) y los 0,42 libres quedan junto a la
#     bancada de coccion. Foto de referencia del cliente: METRO GCF3100BS
#     179,5 x 70 x 85, 3 puertas (esa es de congelacion).
ESTE_X1 = COCINA['x1']
ESTE_LARGO = 2.542                         # largo de la mesa (ficha)
ESTE_Y0 = COCINA['y0'] + ESTE_LARGO        # 8,350: borde Norte de la mesa
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
    P('K6 alt', 'Lavavajillas Eurast 50 × 50, 575 × 600 × 820: cabe seguro bajo el escurridor',
      0.575, 0.600, 0.820, '1acedc0e-199c-449c-b390-a8626c771613'),
    P('K8/K9 alt', 'Armario frigorífico ventilado 400 L, acero inoxidable (Diamond)',
      0.626, 0.740, 1.925, '8969b667-b5cb-4e83-b599-3dd45c112547'),
    P('K8/K9 alt', 'Armario refrigerado AR400L Clima Hostelería, lacado blanco (no inox), 360 L',
      0.600, 0.615, 1.870, 'd48c3c0c-7975-4c22-89c7-64676c23681f'),
]
ESTE_SOBRE = []

# ================================================================ BARRA
# --- Trasbarra contra el muro Oeste, entre P1 (Norte) y P2 (Sur): 2,748 m.
#     Encargo del cliente del 19 set.: una mesada corrida de 0,60 de fondo en
#     toda la pared entre pilares. Encima, de izquierda a derecha (de P1
#     hacia P2): cafetera de 1,00, 0,20 de molinillos y utensilios, la
#     granizadora de crema de cafe, un espacio libre y, pegado a P2, un
#     fregadero pequeno. Debajo: nada bajo el fregadero y una nevera inox de
#     1 m bajo el espacio libre. Sobre los aparatos, un estante corrido.
TRASBARRA_X = (0.250, 0.850)
TRASBARRA_Y = (2.011, 4.759)               # de P2 (Sur) a P1 (Norte)
MESADA_FONDO = TRASBARRA_X[1] - TRASBARRA_X[0]
# 'hueco' es lo que cada cosa ocupa a lo largo de la mesada; el molinillo es
# mas estrecho que el hueco de 0,20 que pidio el cliente para molinillos y
# utensilios, asi que se dibuja dentro de el.
TRASBARRA = [
    P('A1', 'Cafetera (comprada), 2 grupos', 1.000, 0.600, 0.500),
    P('A2', 'Molinillo de café Cunil TRANQUILO de ABC, 275 W, tolva 0,5 kg',
      0.170, 0.340, 0.410, 'f2df0f65-b185-40b2-b2e2-2cd42fb2eefd'),
    P('A3', 'Máquina de helado y crema fría Bras B-CREAM1HD, 6 L, italiana',
      0.200, 0.490, 0.620, 'e4ddc7ec-739d-4b14-968b-1d230076b476'),
]
HUECO_MOLINILLOS = 0.200                   # hueco pedido por el cliente
TRASBARRA[1]['hueco'] = HUECO_MOLINILLOS
# El A4 no apoya sobre la mesada: es un fregadero de pie con bastidor y
# estante que sustituye ese tramo de mesada. Su alto de 0,85 es del suelo.
FREGADERO_BARRA = P('A4', 'Fregadero de pie 1 seno con estante y bastidor, 600 × 600 × 850',
                    0.600, 0.600, 0.850,
                    '31bf0e3c-d322-4e34-a968-9bd9ace2024d')
NEVERA_BARRA = P('A5', 'Botellero frigorífico BTL1000, 2 puertas correderas, 240 L',
                 1.040, 0.580, 0.850,
                 '77c7b69b-09e0-4c28-878e-9454ffff60ec')
# Dos piezas iguales hacen el estante corrido de 2,50 sobre la mesada.
ESTANTE = P('A6', 'Estante mural cartelas compacto Fricosmos 011410, 1250 × 400 × '
                  '245 (2 piezas hacen 2,50)', 1.250, 0.400, 0.245,
            '8af91e42-ebf3-4239-8e01-9b6b82b73120')
ESTANTE_N = 2
ESTANTE_LARGO = ESTANTE['a'] * ESTANTE_N


def trasbarra_pos():
    """(tag, y0, y1) de lo que va SOBRE la mesada, de P1 (Norte) a P2 (Sur)."""
    y, out = TRASBARRA_Y[1], []
    for p in TRASBARRA:
        h = p.get('hueco', p['a'])
        out.append((p['tag'], y - h, y))
        y -= h
    f = FREGADERO_BARRA
    out.append((f['tag'], TRASBARRA_Y[0], TRASBARRA_Y[0] + f['a']))
    return out


def libre_trasbarra():
    """Hueco libre de mesada entre la granizadora y el fregadero."""
    ocupado = sum(p.get('hueco', p['a']) for p in TRASBARRA) + FREGADERO_BARRA['a']
    return (TRASBARRA_Y[1] - TRASBARRA_Y[0]) - ocupado


NEVERA_POS = dict(y0=TRASBARRA_Y[0] + FREGADERO_BARRA['a'],
                  y1=TRASBARRA_Y[0] + FREGADERO_BARRA['a'] + NEVERA_BARRA['a'])

# Alternativas de la trasbarra con la misma funcion (no se dibujan)
ALT_BARRA = [
    P('A3 alt', 'Granizadora GRANICREAM 1S Eurofred, 1 cuba de 10 L, cremas de café',
      0.200, 0.500, 0.790, 'e826e334-3cba-44fc-a530-627af1dabaf6'),
    P('A3 alt', 'Granizadora GRANISMART 5x1 Eurofred, 1 cuba de 5 L (la más baja)',
      0.260, 0.400, 0.630, '635e0924-0d3e-42ca-965e-e66eb41cdee1'),
    P('A6 alt', 'Estante en inox de pared, 2000 × 400 × 250, de una sola pieza',
      2.000, 0.400, 0.250, '15f4f100-83b5-4f51-a383-11acf9989372'),
    P('A4 alt', 'Fregadero 1 cubeta con puerta, Gama 600 Distform, 600 × 600 × 850',
      0.600, 0.600, 0.850, '3efac5b4-e702-4af6-9dd9-533709488190'),
    P('A4 alt', 'Fregadero industrial 1 cuba AISI-304, 700 × 600 × 850',
      0.700, 0.600, 0.850, '95121b55-b486-4a76-a3de-ed7874e75876'),
    P('A5 alt', 'Botellero inox interior y exterior, 2 puertas, 200 L, Eurast',
      1.020, 0.550, 0.850, 'a046bf7e-9d25-4304-9593-1cd32668e47f'),
    P('A5 alt', 'Botellero refrigerado de bar Yostin, 2 puertas, 100 cm, AISI-304',
      1.000, 0.550, 0.840, '6589602e-de66-484c-871f-68f83b182638'),
]

# Aparatos que la trasbarra nueva deja sin sitio: el encargo del 19 set. no
# los incluye. Se mantienen listados para que el cliente decida.
SIN_SITIO = [
    P('A3 ant.', 'Fabricador de hielo Gastro M CT694, 28 kg/24 h (bajo encimera)',
      0.400, 0.460, 0.670, 'e3db53e1-8f64-4495-bb2c-59fe355a32e2'),
    P('A4 ant.', 'Exprimidor de naranjas Mizumo Next Gen', 0.480, 0.350, 0.735,
      'a7c3e878-0cdd-4f7e-b013-897ae4f6120d'),
    P('A2 ant.', 'Lavamanos inox con grifo y pulsador de pedal, cuba Ø340',
      0.400, 0.400, 0.850, '6105678f-3159-4172-a17a-f400760f0b35'),
    P('A3b ant.', 'Licuadora industrial Sammic Li-240', 0.205, 0.310, 0.360,
      '2b8d9850-b422-4738-b716-c30da9857300'),
]

# --- Mostrador delantero en la linea de la pared en L, del ventanal al paso.
#     Croquis del 15/09: llega hasta y=4,75, justo antes del paso de 0,60.
MOSTRADOR_X = (BARRA_FRENTE_X0 := 1.900, 2.660)
MOSTRADOR_Y = (1.968, 4.759)              # del zocalo del ventanal a P1
VITRINA = dict(largo=1.000, fondo_cristal=0.700, hueco_bajo=0.600,
               motor=(0.300, 0.300))    # motor abajo, a la izquierda (Sur)
VITRINAS = [
    P('V2', 'Vitrina refrigerada (comprada), 1,00 × 0,70; debajo, lavavasos',
      1.000, 0.700, 1.250),
    P('V1', 'Vitrina refrigerada (comprada), 1,00 × 0,70; hueco libre debajo',
      1.000, 0.700, 1.250),
]
LAVAVASOS = P('B1', 'Lavavasos Elettrobar FAST 40, cesta 40 × 40 (bajo la vitrina V2)',
              0.440, 0.540, 0.670, 'e858e346-8373-4e64-aa03-6f9a559e168e')
BARRILES = P('B2', 'Barriles de cerveza de 30 L, Ø 0,32 (debajo de la tabla de P2)',
             0.320, 0.320, 0.600)
BARRA_MADERA = dict(y0=MOSTRADOR_Y[0] + 2.000, y1=MOSTRADOR_Y[1])  # tabla de madera
TABLET = P('B3', 'Caja: tablet sobre soporte (lo único que queda en el mostrador)',
           0.250, 0.200, 0.250)
CHOPERA = P('B4', 'Columna de cerveza en T de 3 grifos, bandeja 40 × 40, sobre la tabla de P2',
            0.400, 0.400, 0.550, 'f2d9d7ba-6f4f-4feb-b032-641cc4d828fe')
TABLA_P2 = dict(x0=0.510, x1=1.290, y0=1.621, y1=2.011)   # tabla de P2 al muro

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
ANCHO_COCINA = COCINA['x1'] - COCINA['x0']                          # 2,31
PASILLO_COCINA_MIN = ANCHO_COCINA - max(_F) - ESTE[0]['f']         # 0,97
PASILLO_COCINA = ANCHO_COCINA - 0.600 - ESTE[0]['f']               # 1,11 frente al fregadero
PASILLO_BARRA  = MOSTRADOR_X[0] - TRASBARRA_X[1]                   # 1,05
LIBRE_ESTE = BANCADA_COCCION['y0'] - ESTE_Y0                         # 0,33 junto a la coccion
LARGO_OESTE = OESTE_Y0 - 5.357                                      # 3,326 hasta P1
SUMA_OESTE = sum(p['a'] for p in OESTE)                             # 3,042


def todos():
    """Lista plana de todo lo que hay que comprar, en orden de lamina."""
    return (COCCION + [CAMPANA] + OESTE[:2] + [LAVAVAJILLAS] + OESTE[2:] + ESTE +
            ESTE_SOBRE + TRASBARRA + [FREGADERO_BARRA, NEVERA_BARRA, ESTANTE] +
            VITRINAS + [LAVAVASOS, BARRILES, TABLET, CHOPERA])
