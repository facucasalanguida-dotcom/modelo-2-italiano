# -*- coding: utf-8 -*-
"""
LA CALLE — el contexto urbano que se ve por el escaparate.

El HDRI de Poly Haven pone el cielo y la luz, pero esta a distancia infinita:
todo lo que se ve de cerca por un escaparate de doble altura tiene que estar
construido. Esto levanta la acera, la calzada, la acera de enfrente, los
edificios de la manzana de enfrente con sus balcones y persianas, el arbolado
en alcorques, el mobiliario urbano y los coches aparcados.

Estilo de calle de Malaga: fachadas enlucidas en ocres y blancos, cinco
plantas, balcones de forja, bajos comerciales con toldo, cubierta de teja.

Sistema de coordenadas: el del local. La fachada del local esta en y = 1,5 y
la calle va hacia -Y.
"""
import math
import random

import bpy

# ------------------------------------------------------- seccion de la calle
Y_FACHADA = 1.500          # linea de fachada del local
Y_ACERA = -2.700           # bordillo de nuestra acera
Y_APARCA = -4.900          # banda de aparcamiento
Y_EJE = -6.900             # eje de la calzada
Y_ACERA_OP = -10.900       # bordillo de la acera de enfrente
Y_FACHADA_OP = -13.900     # fachada de enfrente
H_BORDILLO = 0.140
X0, X1 = -26.0, 34.0       # cuanto de calle se construye


def _c(escena, nombre, x0, y0, x1, y1, z0, z1, mat, col='Ciudad'):
    return escena.caja(nombre, x0, y0, x1, y1, z0, z1, mat, col)


def suelo_urbano(E, M):
    """Acera, bordillo, calzada, marcas viales y alcorques."""
    # acera del local y de enfrente
    _c(E, 'Acera', X0, Y_ACERA, X1, Y_FACHADA + 0.4, 0.0, H_BORDILLO, M['_acera'])
    _c(E, 'Acera enfrente', X0, Y_FACHADA_OP, X1, Y_ACERA_OP, 0.0, H_BORDILLO, M['_acera'])
    # bordillos de granito
    _c(E, 'Bordillo', X0, Y_ACERA - 0.180, X1, Y_ACERA, -0.120, H_BORDILLO, M['piedra'])
    _c(E, 'Bordillo enfrente', X0, Y_ACERA_OP, X1, Y_ACERA_OP + 0.180, -0.120,
       H_BORDILLO, M['piedra'])
    # calzada, un poco por debajo del bordillo
    _c(E, 'Calzada', X0, Y_ACERA_OP + 0.18, X1, Y_ACERA - 0.18, -0.130, -0.002,
       M['_asfalto'])
    # marcas viales: eje discontinuo y linea de aparcamiento
    for x in range(int(X0), int(X1), 4):
        _c(E, f'Eje {x}', x, Y_EJE - 0.06, x + 2.2, Y_EJE + 0.06, -0.001, 0.0015,
           M['_pintura_vial'])
    _c(E, 'Linea aparcamiento', X0, Y_APARCA - 0.05, X1, Y_APARCA + 0.05,
       -0.001, 0.0015, M['_pintura_vial'])
    # paso de cebra a la altura de la esquina
    for i in range(7):
        x = 12.4 + i * 0.90
        _c(E, f'Cebra {i + 1}', x, Y_ACERA_OP + 0.2, x + 0.50, Y_ACERA - 0.2,
           -0.001, 0.0015, M['_pintura_vial'])
    # alcorques de los arboles
    for x in ALCORQUES:
        _c(E, f'Alcorque {x:.0f}', x - 0.55, Y_ACERA + 0.35, x + 0.55,
           Y_ACERA + 1.45, 0.0, H_BORDILLO - 0.02, M['_tierra'])
        for s, (ax0, ay0, ax1, ay1) in enumerate((
                (x - 0.60, Y_ACERA + 0.30, x + 0.60, Y_ACERA + 0.35),
                (x - 0.60, Y_ACERA + 1.45, x + 0.60, Y_ACERA + 1.50),
                (x - 0.60, Y_ACERA + 0.30, x - 0.55, Y_ACERA + 1.50),
                (x + 0.55, Y_ACERA + 0.30, x + 0.60, Y_ACERA + 1.50))):
            _c(E, f'Alcorque {x:.0f} canto {s}', ax0, ay0, ax1, ay1, 0.0,
               H_BORDILLO + 0.01, M['piedra'])


# menos alcorques: cada arbol es follaje con alfa, lo mas caro de la escena
ALCORQUES = [-6.8, 8.6, 17.5]


# ------------------------------------------------------------- los edificios
# (x0, ancho, plantas, color de fachada, color del bajo, huecos por planta)
MANZANA = [
    (-26.0, 8.4, 5, 'D9C9A8', 'B08A63', 3),
    (-17.6, 7.2, 4, 'E6DCC8', '7C6A58', 3),
    (-10.4, 9.0, 5, 'C9A882', '3E4A52', 4),
    (-1.4, 7.8, 4, 'EFE7D6', '8C5C48', 3),
    (6.4, 8.6, 5, 'D2B896', '445048', 3),
    (15.0, 7.4, 4, 'E3D6BC', '9A6A4A', 3),
    (22.4, 9.2, 5, 'CDBEA4', '5A4438', 4),
]
H_PLANTA = 3.05
H_BAJO = 4.10


def edificios(E, M, rnd):
    """La manzana de enfrente: es lo que de verdad hace que sea una ciudad."""
    for k, (x0, ancho, plantas, col_f, col_b, huecos) in enumerate(MANZANA):
        x1 = x0 + ancho
        yf = Y_FACHADA_OP
        yb = yf - 9.0                       # fondo del edificio
        alto = H_BAJO + plantas * H_PLANTA
        mat_f = M['_fachada'][k % len(M['_fachada'])]
        # cuerpo
        _c(E, f'Edificio {k + 1}', x0, yb, x1, yf, 0.0, alto, mat_f)
        # zocalo del bajo comercial, en otro color
        _c(E, f'Edificio {k + 1} zocalo', x0 - 0.04, yf - 0.10, x1 + 0.04, yf + 0.06,
           0.0, H_BAJO - 0.55, M['_bajo'][k % len(M['_bajo'])])
        # escaparate del bajo
        _c(E, f'Edificio {k + 1} escaparate', x0 + 0.55, yf + 0.02, x1 - 0.55,
           yf + 0.05, 0.55, H_BAJO - 0.95, M['_vidrio_calle'])
        # toldo del bajo
        if k % 2 == 0:
            _c(E, f'Edificio {k + 1} toldo', x0 + 0.45, yf + 0.06, x1 - 0.45,
               yf + 1.45, H_BAJO - 0.90, H_BAJO - 0.72,
               M['_toldo'][k % len(M['_toldo'])])
            for xt in (x0 + 0.50, x1 - 0.50):
                _c(E, f'Edificio {k + 1} varilla {xt:.1f}', xt - 0.02, yf + 1.40,
                   xt + 0.02, yf + 1.45, H_BAJO - 1.55, H_BAJO - 0.72, M['carp'])
        # imposta sobre el bajo
        _c(E, f'Edificio {k + 1} imposta', x0 - 0.08, yf, x1 + 0.08, yf + 0.14,
           H_BAJO - 0.55, H_BAJO - 0.38, M['_cornisa'])
        # huecos de las plantas
        paso = ancho / huecos
        for p in range(plantas):
            z0 = H_BAJO + p * H_PLANTA
            for h in range(huecos):
                cx = x0 + paso * (h + 0.5)
                w, hh = 0.95, 1.95
                # hueco oscuro embebido (el interior de la casa)
                _c(E, f'Ed{k + 1} hueco {p}{h}', cx - w / 2, yf - 0.22,
                   cx + w / 2, yf + 0.02, z0 + 0.62, z0 + 0.62 + hh, M['_interior_calle'])
                # jambas y dintel
                for nm, a, b in (('jamba i', cx - w / 2 - 0.09, cx - w / 2),
                                 ('jamba d', cx + w / 2, cx + w / 2 + 0.09)):
                    _c(E, f'Ed{k + 1} {nm} {p}{h}', a, yf, b, yf + 0.07,
                       z0 + 0.55, z0 + 0.62 + hh + 0.09, M['_cornisa'])
                _c(E, f'Ed{k + 1} dintel {p}{h}', cx - w / 2 - 0.09, yf,
                   cx + w / 2 + 0.09, yf + 0.09, z0 + 0.62 + hh, z0 + 0.62 + hh + 0.09,
                   M['_cornisa'])
                # carpinteria y vidrio
                _c(E, f'Ed{k + 1} carp {p}{h}', cx - w / 2, yf - 0.02,
                   cx + w / 2, yf + 0.01, z0 + 0.62, z0 + 0.62 + hh, M['carp'])
                _c(E, f'Ed{k + 1} vidrio {p}{h}', cx - w / 2 + 0.05, yf - 0.03,
                   cx + w / 2 - 0.05, yf - 0.015, z0 + 0.70, z0 + 0.62 + hh - 0.08,
                   M['_vidrio_calle'])
                # persiana enrollable a media altura, cada una a su aire
                pr = rnd.choice((0.0, 0.0, 0.35, 0.6, 0.85))
                if pr > 0:
                    _c(E, f'Ed{k + 1} persiana {p}{h}', cx - w / 2 + 0.03, yf - 0.05,
                       cx + w / 2 - 0.03, yf - 0.03,
                       z0 + 0.62 + hh - pr * hh, z0 + 0.62 + hh, M['_persiana'])
                # balcon en las plantas bajas
                if p < 2 and (h + k) % 2 == 0:
                    _c(E, f'Ed{k + 1} losa {p}{h}', cx - 0.82, yf, cx + 0.82,
                       yf + 0.55, z0 + 0.50, z0 + 0.60, M['_cornisa'])
                    baranda(E, M, cx - 0.82, yf + 0.52, cx + 0.82, yf + 0.55,
                            z0 + 0.60, z0 + 1.62, f'Ed{k + 1} {p}{h}')
                else:
                    _c(E, f'Ed{k + 1} vierte {p}{h}', cx - w / 2 - 0.11, yf,
                       cx + w / 2 + 0.11, yf + 0.13, z0 + 0.55, z0 + 0.62,
                       M['_cornisa'])
        # cornisa de coronacion y peto
        _c(E, f'Edificio {k + 1} cornisa', x0 - 0.22, yf, x1 + 0.22, yf + 0.34,
           alto - 0.30, alto, M['_cornisa'])
        _c(E, f'Edificio {k + 1} peto', x0, yb, x1, yf + 0.06, alto, alto + 0.85,
           mat_f)
        # cubierta de teja, un faldon hacia la calle
        _c(E, f'Edificio {k + 1} teja', x0, yf - 2.6, x1, yf + 0.20,
           alto + 0.85, alto + 1.05, M['_teja'])


def baranda(E, M, x0, y0, x1, y1, z0, z1, nombre):
    """Barandilla de forja: pasamanos, zocalo y balaustres."""
    _c(E, f'{nombre} pasamanos', x0, y0 - 0.02, x1, y1 + 0.02, z1 - 0.045, z1, M['carp'])
    _c(E, f'{nombre} zocalo', x0, y0 - 0.01, x1, y1 + 0.01, z0, z0 + 0.035, M['carp'])
    n = max(3, int((x1 - x0) / 0.115))
    for i in range(n):
        cx = x0 + (x1 - x0) * (i + 0.5) / n
        _c(E, f'{nombre} balaustre {i}', cx - 0.008, y0, cx + 0.008, y1,
           z0 + 0.03, z1 - 0.04, M['carp'])


# ------------------------------------------------------- mobiliario y coches
def farola(E, M, x, y, alto=5.2, nombre='Farola'):
    E.cilindro(f'{nombre} base', x, y, 0.115, 0.0, 0.42, M['carp'], 'Ciudad', 20)
    E.cilindro(f'{nombre} fuste', x, y, 0.062, 0.40, alto, M['carp'], 'Ciudad', 20)
    E.cilindro(f'{nombre} brazo', x, y, 0.045, alto, alto + 0.22, M['carp'], 'Ciudad', 16)
    lum = E.caja(f'{nombre} luminaria', x - 0.28, y - 0.17, x + 0.28, y + 0.17,
                 alto + 0.16, alto + 0.30, M['carp'], 'Ciudad')
    E.caja(f'{nombre} vidrio', x - 0.25, y - 0.14, x + 0.25, y + 0.14,
           alto + 0.13, alto + 0.17, M['_luz_farola'], 'Ciudad')
    return lum


def bolardo(E, M, x, y, nombre):
    E.cilindro(f'{nombre}', x, y, 0.055, 0.0, 0.78, M['carp'], 'Ciudad', 20)
    E.cilindro(f'{nombre} cabeza', x, y, 0.070, 0.78, 0.83, M['carp'], 'Ciudad', 20)


def coche(E, M, x, y, giro, color, nombre, largo=4.35, ancho=1.78):
    """Coche aparcado: carroceria, lunas y ruedas. A la distancia a la que se
    ve por el escaparate, la silueta y el reflejo son lo que cuenta."""
    L, A = largo, ancho
    h0, h1, h2 = 0.28, 0.76, 1.42          # bajos, cintura, techo
    obs = []
    # cuerpo bajo
    c = E.caja(f'{nombre} cuerpo', x - L / 2, y - A / 2, x + L / 2, y + A / 2,
               h0, h1, color, 'Ciudad')
    E.bisel(c, 0.055, 4, 70)
    obs.append(c)
    # habitaculo, mas corto y estrecho
    hx0, hx1 = x - L * 0.30, x + L * 0.22
    t = E.caja(f'{nombre} techo', hx0, y - A / 2 + 0.09, hx1, y + A / 2 - 0.09,
               h1 - 0.03, h2, color, 'Ciudad')
    E.bisel(t, 0.085, 4, 70)
    obs.append(t)
    # lunas
    for nm, a, b, c0, c1 in (('parabrisas', hx1 - 0.06, hx1 + 0.02, h1 + 0.04, h2 - 0.06),
                             ('luneta', hx0 - 0.02, hx0 + 0.06, h1 + 0.04, h2 - 0.06)):
        E.caja(f'{nombre} {nm}', a, y - A / 2 + 0.12, b, y + A / 2 - 0.12,
               c0, c1, M['_luna'], 'Ciudad')
    for s in (-1, 1):
        E.caja(f'{nombre} ventanilla {s}', hx0 + 0.10, y + s * (A / 2 - 0.10),
               hx1 - 0.10, y + s * (A / 2 - 0.075), h1 + 0.05, h2 - 0.09,
               M['_luna'], 'Ciudad')
    # faros y pilotos
    E.caja(f'{nombre} faro i', x + L / 2 - 0.06, y - A / 2 + 0.18, x + L / 2 + 0.01,
           y - A / 2 + 0.58, h1 - 0.28, h1 - 0.08, M['_faro'], 'Ciudad')
    E.caja(f'{nombre} faro d', x + L / 2 - 0.06, y + A / 2 - 0.58, x + L / 2 + 0.01,
           y + A / 2 - 0.18, h1 - 0.28, h1 - 0.08, M['_faro'], 'Ciudad')
    for s in (-1, 1):
        E.caja(f'{nombre} piloto {s}', x - L / 2 - 0.01, y + s * (A / 2 - 0.55),
               x - L / 2 + 0.06, y + s * (A / 2 - 0.16), h1 - 0.26, h1 - 0.06,
               M['_piloto'], 'Ciudad')
    # ruedas
    for sx in (-1, 1):
        for sy in (-1, 1):
            rx, ry = x + sx * L * 0.30, y + sy * (A / 2 - 0.09)
            r = E.cilindro(f'{nombre} rueda {sx}{sy}', 0, 0, 0.325, -0.105, 0.105,
                           M['_neumatico'], 'Ciudad', 28)
            E.girar(r, (0, 0, 0), 90, 'X')
            for v in r.data.vertices:
                v.co.x += rx
                v.co.y += ry
                v.co.z += 0.325
            ll = E.cilindro(f'{nombre} llanta {sx}{sy}', 0, 0, 0.205, -0.112, 0.112,
                            M['_llanta'], 'Ciudad', 24)
            E.girar(ll, (0, 0, 0), 90, 'X')
            for v in ll.data.vertices:
                v.co.x += rx
                v.co.y += ry
                v.co.z += 0.325
            obs += [r, ll]
    for o in obs:
        E.girar(o, (x, y, 0), giro)
    return obs
