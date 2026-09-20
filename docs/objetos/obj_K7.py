# -*- coding: utf-8 -*-
"""
K7 · Fregadero inox 1200 x 600 x 850 con bastidor, cuba a la izquierda y
hueco para lavavajillas bajo el escurridor (Makro ref. AAA0045913963;
producto generico espanol, mismo render en Osteleria).

Referencia: render de Osteleria (K7_04) y foto real de un equivalente.
Todo AISI-304 satinado: tablero de 1200 x 600 con faldon sanitario de 40;
peto trasero de 100 con remate inclinado; cuba embutida 500 x 400 x 250 a
la izquierda (eje a 300 del lateral y del frente) con valvula O 90 y
rebosadero; escurridor a la derecha con estrias frente-trasera; caja
envolvente bajo la cuba (240 bajo el faldon sanitario); cuatro patas de tubo 40 x 40
con pie regulable, adelantadas 50, solo bajo la cuba; el escurridor vuela y
deja el hueco de 600 para el lavavajillas. Sin estante ni grifo.

MEDIDAS: 850 es la altura del tablero; el peto sube a 950, que es la
envolvente que se comprueba. Supuesto: alto del peto (100) y del faldon
envolvente de la cuba (200).
"""
import lib as L
import partes as P

A, F = 1.200, 0.600
Z_TAB = 0.850                 # cara del tablero
E_TAB = 0.040                 # faldon sanitario
PETO_H, PETO_E = 0.100, 0.015
CUBA_W, CUBA_D, CUBA_P = 0.500, 0.400, 0.250
CUBA_X, CUBA_Y = -A / 2 + 0.300, 0.0
Y_FRENTE, Y_TRAS = -F / 2, F / 2


def build():
    inox = L.mat_inox()
    inox_p = L.mat_inox_pulido()
    cromo = L.mat_cromo()

    # --- tablero con faldon y peto
    tab = L.caja('tablero', A, F, E_TAB, (0, 0, Z_TAB - E_TAB), r=0.004, r_vert=0.010, segs=4, mat=inox)
    L.prisma_yz('peto', [(Y_TRAS - PETO_E, Z_TAB - 0.001), (Y_TRAS, Z_TAB - 0.001), (Y_TRAS, Z_TAB + PETO_H - 0.008),
                         (Y_TRAS - PETO_E * 0.6, Z_TAB + PETO_H), (Y_TRAS - PETO_E, Z_TAB + PETO_H - 0.004)],
                -A / 2, A / 2, mat=inox, r=0.001)
    # --- cuba embutida con valvula y rebosadero
    P.cuba('cuba', tab, (CUBA_X, CUBA_Y, Z_TAB), CUBA_W, CUBA_D, CUBA_P, r_esq=0.045, r_fondo=0.030, mat=inox_p, desague=False)
    zf = Z_TAB - CUBA_P
    L.cilindro('valvula', 0.045, 0.0015, (CUBA_X, CUBA_Y, zf + 0.0012), segs=64, r=0.001, mat=inox_p)
    L.cilindro('valvula tapon', 0.030, 0.004, (CUBA_X, CUBA_Y, zf + 0.0027), segs=48, r=0.0015, mat=cromo)
    L.cilindro('rebosadero', 0.018, 0.002, (CUBA_X + CUBA_W / 2 - 0.0030, CUBA_Y, Z_TAB - 0.06), eje='X', segs=32, r=0.001,
               mat=L.mat_chapa_perforada('Rejilla rebosadero', d=0.003, paso=0.005))
    # --- escurridor: estrias frente-trasera (varillas embutidas medio hundidas)
    x0, x1 = 0.060, A / 2 - 0.045
    n = 13
    paso = (x1 - x0) / (n - 1)
    for i in range(n):
        L.cilindro(f'estria {i + 1}', 0.0025, F - 0.110, (x0 + i * paso, -F / 2 + 0.050, Z_TAB - 0.0015), eje='Y', segs=16, mat=inox)
    # --- caja envolvente de la cuba bajo el tablero
    L.caja('faldon cuba', 0.600, 0.580, 0.240, (-A / 2 + 0.300, 0.000, Z_TAB - E_TAB - 0.240), r=0.003, segs=3, mat=inox)
    # --- cuatro patas de tubo 40 x 40 con pie regulable, adelantadas 50
    for i, (x, y) in enumerate(((-A / 2 + 0.040, Y_FRENTE + 0.050 + 0.020), (-0.020, Y_FRENTE + 0.050 + 0.020),
                                (-A / 2 + 0.040, Y_TRAS - 0.040), (-0.020, Y_TRAS - 0.040))):
        L.cilindro(f'pata {i + 1} pie', 0.020, 0.030, (x, y, 0), r=0.004, segs=40, mat=L.mat_plastico('Plastico gris', (0.30, 0.30, 0.30)))
        L.cilindro(f'pata {i + 1} rosca', 0.010, 0.020, (x, y, 0.030), segs=24, mat=inox_p)
        L.caja(f'pata {i + 1}', 0.040, 0.040, Z_TAB - E_TAB - 0.240 - 0.050 + 0.002, (x, y, 0.050), r=0.003, segs=3, mat=inox)

    return dict(medidas=(A, F, Z_TAB + PETO_H))
