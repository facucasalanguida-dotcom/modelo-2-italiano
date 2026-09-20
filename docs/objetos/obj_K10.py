# -*- coding: utf-8 -*-
"""
K10 · Mesa refrigerada de 4 puertas 2542 x 600 x 850, 350 W, 530 L
(Clima Hosteleria CORDOBA MRCH-250 = Coreco MRS-250; el plano la llama
Infrico, pero los datos de Makro son exactamente los de la MRCH-250).

Referencia: fotos de distribuidores (4 puertas) y plano en seccion de la
tarifa Coreco. AISI-304 satinado: encimera de 600 con frente curvo que
vuela 50 sobre las puertas, peto sanitario trasero de 100 x 14; cuerpo de
532 de fondo y 706 de alto; cuatro puertas lisas de 470 x 610 con ranura
superior de tirador integrado y burlete gris; panel del grupo a la derecha
(340) con display digital, dos pilotos y rejilla pivotante de ranuras
cortas; segunda rejilla en el lateral derecho; seis patas de tubo O 50
regulables; trasera galvanizada.

MEDIDAS: 850 es la encimera; el peto sube a 950 (envolvente comprobada).
Supuesto: sentido de apertura (todas con bisagra a la izquierda), altura de
patas 144 y el reparto exacto del panel del grupo.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F = 2.542, 0.600
Z_TAB = 0.850
E_TAB = 0.040
PETO_H, PETO_E = 0.100, 0.014
F_CUERPO = 0.532
H_PATA = 0.144
Y_FRENTE_TAB, Y_TRAS = -F / 2, F / 2
Y_FRENTE = Y_FRENTE_TAB + 0.050        # frente del cuerpo y de las puertas
Y_TRAS_CUERPO = Y_FRENTE + F_CUERPO    # +0,282
GRUPO_W = 0.340
PUERTA_W, PUERTA_H, PUERTA_E = 0.470, 0.610, 0.045
Z_PUERTA0 = H_PATA + 0.026


def _f(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_display(ruta):
    W, Hh = 280, 80
    im = Image.new('RGBA', (W, Hh), (10, 10, 12, 255))
    dr = ImageDraw.Draw(im)
    dr.text((60, 10), '2.0', font=_f(56, True), fill=(255, 45, 25, 255))
    im.save(ruta)


def build():
    inox = L.mat_inox()
    inox_p = L.mat_inox_pulido()
    plast = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    galva = L.mat_aluminio('Galvanizado', rug=0.55, color=(0.50, 0.51, 0.52))
    goma = L.mat_goma('Burlete gris', (0.45, 0.45, 0.45))

    # --- encimera con frente curvo y peto
    tab = L.caja('encimera', A, F, E_TAB, (0, 0, Z_TAB - E_TAB), r=0.003, segs=3, mat=inox)
    # canto delantero redondeado: se redondea la arista frontal superior con
    # un cilindro sustraido y otro anadido (radio 20)
    L.sustraer(tab, L.caja('canto corte', A + 0.01, 0.020, 0.020, (0, Y_FRENTE_TAB + 0.010, Z_TAB - 0.020)))
    L.cilindro('canto curvo', 0.020, A, (-A / 2, Y_FRENTE_TAB + 0.020, Z_TAB - 0.020), eje='X', segs=32, mat=inox)
    L.prisma_yz('peto', [(Y_TRAS - PETO_E, Z_TAB - 0.001), (Y_TRAS, Z_TAB - 0.001), (Y_TRAS, Z_TAB + PETO_H - 0.008),
                         (Y_TRAS - PETO_E * 0.6, Z_TAB + PETO_H), (Y_TRAS - PETO_E, Z_TAB + PETO_H - 0.004)],
                -A / 2, A / 2, mat=inox, r=0.001)

    # --- cuerpo: caja de 532 de fondo bajo la encimera, con los huecos de las puertas
    cuerpo = L.caja('cuerpo', A, F_CUERPO, Z_TAB - E_TAB - H_PATA, (0, Y_FRENTE + F_CUERPO / 2, H_PATA), r=0.003, segs=3, mat=inox)
    modulo = (A - GRUPO_W) / 4
    for k in range(4):
        xc = -A / 2 + modulo * (k + 0.5)
        L.sustraer(cuerpo, L.caja(f'hueco {k + 1}', PUERTA_W + 0.004, PUERTA_E + 0.010, PUERTA_H + 0.030,
                                  (xc, Y_FRENTE + PUERTA_E / 2 - 0.003, Z_PUERTA0 - 0.002)))
        # puerta lisa con burlete y ranura oscura de tirador por arriba
        L.caja(f'puerta {k + 1}', PUERTA_W, PUERTA_E, PUERTA_H, (xc, Y_FRENTE + PUERTA_E / 2, Z_PUERTA0), r=0.003, segs=3, mat=inox)
        L.caja(f'puerta {k + 1} burlete', PUERTA_W + 0.003, 0.003, PUERTA_H + 0.003, (xc, Y_FRENTE + PUERTA_E + 0.0015, Z_PUERTA0 - 0.0015),
               mat=goma, suave=False)
        L.caja(f'puerta {k + 1} ranura', PUERTA_W, 0.004, 0.026, (xc, Y_FRENTE + 0.030, Z_PUERTA0 + PUERTA_H + 0.002),
               mat=L.mat_plastico('Interior oscuro', (0.01, 0.01, 0.01), rug=0.9), suave=False)
    L.caja('trasera', A - 0.006, 0.002, Z_TAB - E_TAB - H_PATA - 0.006, (0, Y_TRAS_CUERPO - 0.001, H_PATA + 0.003), mat=galva, suave=False)

    # --- panel del grupo (derecha): display, pilotos y rejilla pivotante de ranuras cortas
    xg = A / 2 - GRUPO_W / 2
    ruta = os.path.join(L.CALCAS_DIR, 'K10_display.png')
    calca_display(ruta)
    L.caja('display marco', 0.074, 0.003, 0.024, (xg - 0.060, Y_FRENTE - 0.0015, Z_TAB - 0.130), r=0.001, segs=2, mat=plast)
    L.calca('K10 display', ruta, 0.070, 0.020, (xg - 0.060, Y_FRENTE - 0.0034, Z_TAB - 0.118), normal='-Y', emision=1.5)
    P.piloto('piloto rojo', (xg + 0.010, Y_FRENTE, Z_TAB - 0.118), d=0.008, color=(1.0, 0.05, 0.02))
    P.piloto('piloto azul', (xg + 0.030, Y_FRENTE, Z_TAB - 0.118), d=0.008, color=(0.1, 0.4, 1.0))
    for k, x in enumerate((xg + 0.010, xg + 0.030)):
        L.cilindro(f'piloto aro {k + 1}', 0.006, 0.003, (x, Y_FRENTE - 0.003, Z_TAB - 0.118), eje='Y', segs=24, r=0.001, mat=plast)
    for col in range(6):
        x = xg - 0.125 + col * 0.050
        P.rejilla_ranuras(f'rejilla grupo col {col + 1}', (x, Y_FRENTE, Z_TAB - 0.350), 0.040, 0.300, normal='-Y',
                          paso=0.021, ranura=0.010, orient='H', mat=inox, cuerpo=cuerpo)
    # segunda rejilla en el lateral derecho, baja y trasera
    P.rejilla_ranuras('rejilla lateral', (A / 2, Y_TRAS_CUERPO - 0.170, Z_TAB - 0.390), 0.240, 0.140, normal='+X',
                      paso=0.010, ranura=0.005, orient='V', mat=inox, cuerpo=cuerpo)

    # --- seis patas de tubo O 50 regulables
    for i, (x, y) in enumerate(((-1.16, Y_FRENTE + 0.06), (0.0, Y_FRENTE + 0.06), (1.16, Y_FRENTE + 0.06),
                                (-1.16, Y_TRAS_CUERPO - 0.06), (0.0, Y_TRAS_CUERPO - 0.06), (1.16, Y_TRAS_CUERPO - 0.06))):
        P.pata_regulable(f'pata {i + 1}', (x, y, 0), H_PATA + 0.002, d_tubo=0.050, d_pie=0.050, h_pie=0.025, mat_tubo=inox)

    return dict(medidas=(A, F, Z_TAB + PETO_H), ignorar=('piloto',))
