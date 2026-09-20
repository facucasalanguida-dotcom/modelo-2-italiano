# -*- coding: utf-8 -*-
"""
A2 · Molinillo de cafe Cunill TRANQUILO Automatico (on-demand), 170 x 340 x 410.

Referencia: foto del vendedor (ABC Hosteleria, la misma de Makro) y fotos
oficiales de Cunill de la misma carroceria (Tranquilo-Tron). Carroceria de
ABS negro brillante de una pieza: torre de seccion redondeada que se
ensancha en campana hacia una base con bandeja oval integrada; aro de
regulacion negro dentado; garganta y tolva de 0,5 kg transparentes con tapa
plana; cabezal dispensador negro en voladizo (cupula + embudo) con badge
plateado "Cunill"; horquilla portafiltros; interruptor basculante verde
abajo a la izquierda, LED y pulsador en el flanco izquierdo; rejillas de
ranuras en abanico en los flancos traseros bajos; cuatro tacos de goma.

Confirmado: 170 x 340 x 410, materiales, disposicion. Supuesto: medidas
parciales (tolva, cabezal, bandeja) por proporcion de foto; sin panel
tactil (version Automatico de la foto del vendedor).
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 0.170, 0.340, 0.410
Y_TRAS, Y_FRENTE = F / 2, -F / 2
Y_TORRE = 0.075                # centro de la torre
TORRE_W, TORRE_D = 0.150, 0.150
H_TACO = 0.006
Z_BASE = 0.041                 # cara superior de la base
Z_ARO = 0.285
Z_TOLVA0 = 0.342


def calca_badge(ruta):
    W, Hh = 440, 200
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse((4, 4, W - 4, Hh - 4), fill=(200, 202, 206, 255), outline=(120, 122, 126, 255), width=4)
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 88)
    bb = dr.textbbox((0, 0), 'Cunill', font=f)
    dr.text(((W - (bb[2] - bb[0])) / 2 - bb[0], (Hh - (bb[3] - bb[1])) / 2 - bb[1]), 'Cunill', font=f, fill=(25, 25, 28, 255))
    im.save(ruta)


def build():
    abs_n = L.mat_chapa('ABS negro brillante', (0.012, 0.012, 0.013), rug=0.22, brillo=0.7, piel=0.05)
    mate = L.mat_plastico('Plastico negro mate', (0.02, 0.02, 0.02), rug=0.6)
    trans = L.mat_policarbonato('Copoliester', tinte=(0.96, 0.97, 0.97))
    verde = L.mat_plastico('Plastico verde', (0.05, 0.55, 0.15), rug=0.4, brillo=0.3)

    # --- base con bandeja oval integrada (frente semicircular), sobre 4 tacos de 6 mm
    base = L.caja('base', A, F, Z_BASE - H_TACO, (0, 0, H_TACO), r_vert=0.080, r=0.004, segs=8, mat=abs_n)
    L.sustraer(base, L.cilindro('bandeja hueco', 0.062, 0.02, (0, Y_FRENTE + 0.085, Z_BASE - 0.006), segs=48))
    L.cilindro('bandeja fondo', 0.061, 0.0015, (0, Y_FRENTE + 0.085, Z_BASE - 0.006), segs=48, mat=mate)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        P.pie_goma(f'taco {i + 1}', (sx * 0.060, sy * 0.12, 0.0), d=0.015, h=H_TACO)

    # --- torre: prisma redondeado que se ensancha en campana hacia la base
    torre = L.caja('torre', TORRE_W, TORRE_D, Z_ARO - Z_BASE, (0, Y_TORRE, Z_BASE), r_vert=0.030, r=0.006, segs=8, mat=abs_n)
    L.caja('campana', TORRE_W + 0.018, TORRE_D + 0.030, 0.075, (0, Y_TORRE + 0.005, Z_BASE - 0.001), r_vert=0.040, r=0.030, segs=8, mat=abs_n)
    # rejillas en abanico en los flancos traseros bajos
    for sx, nm in ((-1, 'izquierda'), (1, 'derecha')):
        P.rejilla_ranuras(f'rejilla {nm}', (sx * (TORRE_W / 2 + 0.009), Y_TORRE + 0.045, Z_BASE + 0.040), 0.045, 0.040,
                          normal='+X' if sx > 0 else '-X', paso=0.006, ranura=0.003, orient='V', mat=abs_n, cuerpo=torre)
    P.rejilla_ranuras('rejilla trasera', (0, Y_TORRE + TORRE_D / 2 + 0.015, Z_BASE + 0.040), 0.080, 0.040, normal='+Y',
                      paso=0.006, ranura=0.003, orient='V', mat=abs_n, cuerpo=torre)

    # --- aro de regulacion, garganta y tolva
    L.cilindro('aro regulacion', 0.0575, 0.012, (0, Y_TORRE, Z_ARO), segs=96, r=0.002, mat=mate)
    L.cilindro('garganta', 0.048, Z_TOLVA0 - Z_ARO - 0.012, (0, Y_TORRE, Z_ARO + 0.012), segs=64, mat=trans)
    L.caja('pestana tolva', 0.020, 0.014, 0.010, (-0.058, Y_TORRE, Z_ARO + 0.030), r=0.003, segs=2, mat=trans)
    perfil = [(0.048, Z_TOLVA0), (0.052, Z_TOLVA0 + 0.008), (0.066, Z_TOLVA0 + 0.025), (0.078, Z_TOLVA0 + 0.045),
              (0.083, Z_TOLVA0 + 0.060), (0.083, H - 0.010)]
    L.perfil_revolucion('tolva', perfil, (0, Y_TORRE, 0), segs=96, mat=trans, cerrar=False)
    L.perfil_revolucion('tolva embudo', [(0.006, Z_TOLVA0 + 0.005), (0.040, Z_TOLVA0 + 0.045)], (0, Y_TORRE, 0), segs=48, mat=trans, cerrar=False)
    L.cilindro('tapa tolva', 0.083, 0.008, (0, Y_TORRE, H - 0.010), segs=96, r=0.003, mat=trans)
    L.cilindro('tapa teton', 0.025, 0.002, (0, Y_TORRE, H - 0.002), segs=48, r=0.001, mat=trans)

    # --- cabezal dispensador en voladizo: cupula + embudo, badge Cunill
    yc = Y_TORRE - TORRE_D / 2 - 0.045
    L.perfil_revolucion('cabezal', [(0.012, 0.185), (0.020, 0.200), (0.045, 0.245), (0.046, 0.275), (0.038, 0.292), (0.020, 0.300), (0.0, 0.302)],
                        (0, yc, 0), segs=64, mat=abs_n)
    L.caja('cabezal puente', 0.060, 0.060, 0.050, (0, Y_TORRE - TORRE_D / 2 - 0.020, 0.240), r=0.010, segs=4, mat=abs_n)
    ruta = os.path.join(L.CALCAS_DIR, 'A2_badge.png')
    calca_badge(ruta)
    L.calca('A2 badge', ruta, 0.050, 0.022, (0, yc - 0.0455, 0.262), normal='-Y')
    # horquilla portafiltros
    for sx in (-1, 1):
        L.tubo_curva(f'horquilla {"i" if sx < 0 else "d"}', [(sx * 0.010, Y_TORRE - TORRE_D / 2, 0.125), (sx * 0.030, Y_TORRE - TORRE_D / 2 - 0.040, 0.125),
                                                            (sx * 0.032, Y_TORRE - TORRE_D / 2 - 0.085, 0.125)], 0.005, segs=16, mat=abs_n)
    L.caja('horquilla soporte', 0.040, 0.012, 0.030, (0, Y_TORRE - TORRE_D / 2 - 0.006, 0.110), r=0.004, segs=3, mat=abs_n)
    L.cilindro('microinterruptor', 0.006, 0.006, (0, Y_TORRE - TORRE_D / 2 - 0.012, 0.150), eje='Y', segs=24, mat=mate)

    # --- mandos: basculante verde abajo a la izquierda del frente, LED y pulsador en el flanco
    L.caja('interruptor marco', 0.022, 0.004, 0.014, (-0.050, Y_TORRE - TORRE_D / 2 - 0.004 + 0.0, Z_BASE + 0.045), r=0.001, segs=2, mat=mate)
    L.caja('interruptor tecla', 0.018, 0.005, 0.011, (-0.050, Y_TORRE - TORRE_D / 2 - 0.008, Z_BASE + 0.0465), r=0.001, segs=2, mat=verde)
    P.piloto('led', (-TORRE_W / 2, Y_TORRE - 0.02, 0.245), d=0.006, color=(0.1, 1.0, 0.2), normal='-X')
    P.boton('pulsador', (-TORRE_W / 2, Y_TORRE - 0.02, 0.225), d=0.012, alto=0.004, normal='-X', mat=mate)

    # --- cable por la trasera baja
    P.cable('cable', (0.03, Y_TORRE + TORRE_D / 2 + 0.015, Z_BASE + 0.030), largo=0.20, d=0.007)

    return dict(ignorar=('cable', 'pulsador', 'led'))
