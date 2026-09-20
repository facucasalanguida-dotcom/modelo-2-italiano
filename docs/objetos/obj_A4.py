# -*- coding: utf-8 -*-
"""
A4 · Fregadero Cleiton de pie, 1 seno con estante, 600 x 600 x 850 (+ peto
de 100), desmontable, AISI 201 satinado.

Referencia: 9 fotos y 3 planos acotados del fabricante (Gastroten, mismo
EAN que Makro). Encimera 600 x 600 con canto perimetral de 40; seno
embutido 400 x 400 x 250 (a 40 del canto izquierdo, 73 del derecho y del
trasero) con desague O 52; taladro O 33 para grifo en la repisa trasera
derecha; peto trasero 600 x 100 x 15; faldon de 80 bajo la encimera; cuatro
patas de tubo 40 x 40 con pies regulables de plastico gris; estante inferior
con canto de 40 a 150 del suelo. Sin grifo de serie, sin logos.

MEDIDAS: 850 es la encimera; el peto sube a 950 (envolvente comprobada).
Supuesto: radios de canto (6) y del seno (40 / 30).
"""
import lib as L
import partes as P

A, F = 0.600, 0.600
Z_TAB = 0.850
E_TAB = 0.040
PETO_H, PETO_E = 0.100, 0.015
Y_FRENTE, Y_TRAS = -F / 2, F / 2
SENO = 0.400
SENO_X = -A / 2 + 0.040 + SENO / 2        # a 40 del canto izquierdo
SENO_Y = Y_FRENTE + 0.073 + SENO / 2      # a 73 del canto trasero... (73 del trasero y 127 del frente)
SENO_Y = Y_TRAS - 0.073 - SENO / 2
Z_FALDON = 0.080
Z_EST = 0.150                             # cara inferior del estante
PATA = 0.040


def build():
    inox = L.mat_inox()
    inox_p = L.mat_inox_pulido()
    pie_m = L.mat_plastico('Plastico gris azulado', (0.32, 0.34, 0.38))

    # --- encimera con canto de 40 y peto
    tab = L.caja('encimera', A, F, E_TAB, (0, 0, Z_TAB - E_TAB), r=0.006, segs=4, mat=inox)
    L.prisma_yz('peto', [(Y_TRAS - PETO_E, Z_TAB - 0.001), (Y_TRAS, Z_TAB - 0.001), (Y_TRAS, Z_TAB + PETO_H - 0.002),
                         (Y_TRAS - PETO_E, Z_TAB + PETO_H)], -A / 2, A / 2, mat=inox, r=0.0015)
    # ceja perimetral tipo bandeja: rebaje de 1,5 mm alrededor del seno
    L.sustraer(tab, L.caja('ceja', A - 0.050, F - 0.050, 0.01, (0, 0, Z_TAB - 0.0015), r_vert=0.010))
    L.caja('ceja fondo', A - 0.050 - 0.001, F - 0.050 - 0.001, 0.0005, (0, 0, Z_TAB - 0.002), mat=inox, suave=False)
    # seno embutido, desague y taladro del grifo
    P.cuba('seno', tab, (SENO_X, SENO_Y, Z_TAB - 0.0015), SENO, SENO, 0.250, r_esq=0.040, r_fondo=0.030, mat=inox_p, desague=False)
    zf = Z_TAB - 0.0015 - 0.250
    L.cilindro('desague', 0.026, 0.0015, (SENO_X, SENO_Y + 0.05, zf + 0.0012), segs=48, r=0.001, mat=inox_p)
    L.cilindro('desague tapon', 0.018, 0.003, (SENO_X, SENO_Y + 0.05, zf + 0.0027), segs=48, r=0.001, mat=L.mat_cromo())
    L.cilindro('racor desague', 0.020, 0.060, (SENO_X, SENO_Y + 0.05, zf - 0.060), segs=32, mat=L.mat_plastico('PVC gris', (0.55, 0.55, 0.52)))
    L.sustraer(tab, L.cilindro('taladro grifo', 0.0165, 0.06, (0.180, Y_TRAS - 0.033, Z_TAB - 0.05), segs=32))

    # --- faldon de 80 bajo la encimera (frente y laterales), con remaches
    zf0 = Z_TAB - E_TAB - Z_FALDON
    L.caja('faldon frente', A - 0.080, 0.0015, Z_FALDON, (0, Y_FRENTE + 0.040 + 0.00075, zf0), mat=inox, suave=False)
    for sx, nm in ((-1, 'izquierdo'), (1, 'derecho')):
        if sx < 0:
            # a la izquierda la pared exterior del seno (a 40 del canto) hace de faldon:
            # solo se ponen los dos tramos cortos delante y detras del seno (evita caras coplanarias)
            for j, (y0, y1) in enumerate(((-(F / 2 - 0.040), SENO_Y - SENO / 2 - 0.0015), (SENO_Y + SENO / 2 + 0.0015, F / 2 - 0.040))):
                L.caja(f'faldon {nm} {j + 1}', 0.0015, y1 - y0, Z_FALDON, (sx * (A / 2 - 0.040 - 0.00075), (y0 + y1) / 2, zf0), mat=inox, suave=False)
        else:
            L.caja(f'faldon {nm}', 0.0015, F - 0.080, Z_FALDON, (sx * (A / 2 - 0.040 - 0.00075), 0, zf0), mat=inox, suave=False)
        for k, y in enumerate((-0.15, 0.15)):
            L.cilindro(f'remache {nm} {k + 1}', 0.004, 0.001, (sx * (A / 2 - 0.040), y, zf0 + 0.040), eje='X', segs=16, mat=inox_p)
    # --- patas 40 x 40 con pie regulable, y estante inferior
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        x, y = sx * (A / 2 - 0.040 - PATA / 2), sy * (F / 2 - 0.040 - PATA / 2)
        L.cilindro(f'pata {i + 1} pie', 0.020, 0.030, (x, y, 0), r=0.004, segs=40, mat=pie_m)
        L.caja(f'pata {i + 1}', PATA, PATA, zf0 - 0.030 + 0.002, (x, y, 0.030), r=0.003, segs=3, mat=inox)
    est = L.caja('estante', A - 0.080, F - 0.080, 0.040, (0, 0, Z_EST), r=0.004, segs=3, mat=inox)
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        L.sustraer(est, L.caja('estante recorte', PATA + 0.002, PATA + 0.002, 0.10, (sx * (A / 2 - 0.040 - PATA / 2), sy * (F / 2 - 0.040 - PATA / 2), Z_EST - 0.03)))

    return dict(medidas=(A, F, Z_TAB + PETO_H))
