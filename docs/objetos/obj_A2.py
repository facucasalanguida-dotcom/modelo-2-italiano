# -*- coding: utf-8 -*-
"""
A2 · Molinillo de cafe Cunill TRANQUILO Automatico (on-demand), 170 x 340 x 410.

Referencia: foto del vendedor (ABC Hosteleria, la misma de Makro) y fotos
oficiales de Cunill de la misma carroceria (Tranquilo-Tron). Carroceria de
ABS negro brillante de una pieza: torre de seccion redondeada (125 de
ancho) que se ensancha en campana de planta casi semicircular (145 x 180,
esquinas r 70) hacia una base de 152 x 340 con bandeja oval integrada; aro
de regulacion negro dentado; garganta (tubo de 2 mm de pared) y tolva de
0,5 kg transparentes de pared fina con tapa plana (la tolva, o 170, es lo
mas ancho); cabezal dispensador negro en voladizo (cupula + embudo) con
badge plateado "Cunill"; horquilla portafiltros; interruptor basculante
verde en la esquina delantera izquierda de la campana, LED y pulsador en el
flanco izquierdo de la torre; rejillas de ranuras en los flancos bajos de
la campana y una pequena centrada en la trasera; cuatro tacos de goma.

Confirmado: 170 x 340 x 410, materiales, disposicion. Supuesto: medidas
parciales (torre, campana, tolva, cabezal, bandeja) por proporcion de foto;
sin panel tactil (version Automatico de la foto del vendedor).
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 0.170, 0.340, 0.410
Y_TRAS, Y_FRENTE = F / 2, -F / 2
Y_TORRE = 0.075                # centro de la torre
TORRE_W, TORRE_D = 0.125, 0.150
CAMP_W, CAMP_D, CAMP_R = TORRE_W + 0.020, TORRE_D + 0.030, 0.070   # campana 145 x 180, esquinas r 70
Y_CAMP = Y_TORRE + 0.005       # centro de la campana (frente en y = -0,010, trasera en y = +0,170)
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
    trans = L.mat_policarbonato('Copoliester', tinte=(0.95, 0.97, 0.98))
    verde = L.mat_plastico('Plastico verde', (0.05, 0.55, 0.15), rug=0.4, brillo=0.3)

    # --- base (152 de ancho, extremos semicirculares) con bandeja oval integrada, sobre 4 tacos de 6 mm
    base = L.caja('base', 0.152, F, Z_BASE - H_TACO, (0, 0, H_TACO), r_vert=0.080, r=0.004, segs=8, mat=abs_n)
    # rebaje oval de la bandeja (115 x 150); su borde trasero queda 1 mm por delante de la campana
    L.sustraer(base, L.caja('bandeja hueco', 0.115, 0.150, 0.02, (0, Y_FRENTE + 0.084, Z_BASE - 0.006), r_vert=0.056, segs=16))
    L.caja('bandeja fondo', 0.113, 0.148, 0.0015, (0, Y_FRENTE + 0.084, Z_BASE - 0.006), r_vert=0.055, segs=16, mat=mate)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        P.pie_goma(f'taco {i + 1}', (sx * 0.052, sy * 0.12, 0.0), d=0.015, h=H_TACO)

    # --- torre: prisma redondeado que se ensancha en campana hacia la base
    torre = L.caja('torre', TORRE_W, TORRE_D, Z_ARO - Z_BASE, (0, Y_TORRE, Z_BASE), r_vert=0.030, r=0.006, segs=8, mat=abs_n)
    # campana: nace 31 mm dentro de la base (su redondeo inferior de r 30 queda oculto), cara vertical plana en z 40-86;
    # con esquinas r 70 su planta cabe en el contorno semicircular de la base
    campana = L.caja('campana', CAMP_W, CAMP_D, 0.106, (0, Y_CAMP, Z_BASE - 0.031), r_vert=CAMP_R, r=0.030, segs=8, mat=abs_n)
    # rejillas: en los flancos bajos de la campana (zona plana, y 60-100) y una pequena centrada en la trasera
    # (0,3 mm hundida: sus bordes quedan a ras del redondeo de las esquinas)
    for sx, nm in ((-1, 'izquierda'), (1, 'derecha')):
        P.rejilla_ranuras(f'rejilla {nm}', (sx * CAMP_W / 2, Y_CAMP, Z_BASE + 0.022), 0.045, 0.040,
                          normal='+X' if sx > 0 else '-X', paso=0.006, ranura=0.003, orient='V', mat=abs_n, cuerpo=(torre, campana))
    P.rejilla_ranuras('rejilla trasera', (0, Y_CAMP + CAMP_D / 2 - 0.0003, Z_BASE + 0.022), 0.024, 0.040, normal='+Y',
                      paso=0.006, ranura=0.003, orient='V', mat=abs_n, cuerpo=(torre, campana))

    # --- aro de regulacion, garganta y tolva
    L.cilindro('aro regulacion', 0.0575, 0.012, (0, Y_TORRE, Z_ARO), segs=96, r=0.002, mat=mate)
    # garganta: tubo de vidrio de 2 mm de pared, 1 mm metido en el aro y 1 mm en el suelo de la tolva, con disco de fondo de 1,5 mm
    L.tubo('garganta', 0.048, 0.046, Z_TOLVA0 - Z_ARO - 0.010, (0, Y_TORRE, Z_ARO + 0.011), segs=64, mat=trans)
    L.cilindro('garganta fondo', 0.047, 0.0015, (0, Y_TORRE, Z_ARO + 0.0125), segs=64, mat=trans)
    L.caja('pestana tolva', 0.020, 0.014, 0.010, (-0.055, Y_TORRE, Z_ARO + 0.030), r=0.003, segs=2, mat=trans)
    # tolva: pared de 2 mm (perfil exterior + retorno interior) con suelo de 1,5 mm; r maximo 85 (= envolvente de 170)
    ext = [(0.048, Z_TOLVA0), (0.063, Z_TOLVA0 + 0.006), (0.074, Z_TOLVA0 + 0.018), (0.081, Z_TOLVA0 + 0.035),
           (0.085, Z_TOLVA0 + 0.050), (0.085, H - 0.010)]
    interior = [(r - 0.002, z) for r, z in reversed(ext)]
    interior[-1] = (0.046, Z_TOLVA0 + 0.0015)      # tapa interior 1,5 mm sobre la exterior: suelo de la tolva
    L.perfil_revolucion('tolva', ext + interior, (0, Y_TORRE, 0), segs=96, mat=trans, cerrar=True)
    # embudo interior: cono de 1,5 mm de pared con la punta 1 mm metida en el suelo de la tolva
    L.perfil_revolucion('tolva embudo', [(0.006, Z_TOLVA0 - 0.001), (0.040, Z_TOLVA0 + 0.045), (0.0385, Z_TOLVA0 + 0.045),
                                         (0.0045, Z_TOLVA0 + 0.0005)], (0, Y_TORRE, 0), segs=48, mat=trans, cerrar=True)
    L.cilindro('tapa tolva', 0.085, 0.008, (0, Y_TORRE, H - 0.010), segs=96, r=0.003, mat=trans)
    L.cilindro('tapa teton', 0.025, 0.002, (0, Y_TORRE, H - 0.002), segs=48, r=0.001, mat=trans)

    # --- cabezal dispensador en voladizo: cupula + embudo, badge Cunill
    yc = Y_TORRE - TORRE_D / 2 - 0.045
    L.perfil_revolucion('cabezal', [(0.012, 0.165), (0.022, 0.182), (0.046, 0.228), (0.046, 0.268), (0.039, 0.288), (0.021, 0.299), (0.0, 0.302)],
                        (0, yc, 0), segs=64, mat=abs_n)
    L.caja('cabezal puente', 0.060, 0.060, 0.050, (0, Y_TORRE - TORRE_D / 2 - 0.020, 0.232), r=0.010, segs=4, mat=abs_n)
    ruta = os.path.join(L.CALCAS_DIR, 'A2_badge.png')
    calca_badge(ruta)
    L.calca('A2 badge', ruta, 0.034, 0.015, (0, yc - 0.0455, 0.248), normal='-Y')   # 34 x 15: esquinas a ~3 mm de la cupula (r 46)
    # horquilla portafiltros
    for sx in (-1, 1):
        L.tubo_curva(f'horquilla {"i" if sx < 0 else "d"}', [(sx * 0.010, Y_TORRE - TORRE_D / 2, 0.125), (sx * 0.030, Y_TORRE - TORRE_D / 2 - 0.040, 0.125),
                                                            (sx * 0.032, Y_TORRE - TORRE_D / 2 - 0.085, 0.125)], 0.005, segs=16, mat=abs_n)
    L.caja('horquilla soporte', 0.040, 0.012, 0.030, (0, Y_TORRE - TORRE_D / 2 - 0.006, 0.110), r=0.004, segs=3, mat=abs_n)
    L.cilindro('microinterruptor', 0.006, 0.012, (0, Y_TORRE - TORRE_D / 2 - 0.010, 0.150), eje='Y', segs=24, mat=mate)   # 2 mm embebido en la torre

    # --- mandos: basculante verde en la esquina delantera izquierda de la campana (a 60-75 mm del suelo),
    #     apoyado tangente a su redondeo (marco 1 mm embebido); LED y pulsador en el flanco izquierdo de la torre
    xs = -0.040
    cx0, cy0 = -(CAMP_W / 2 - CAMP_R), Y_CAMP - CAMP_D / 2 + CAMP_R     # centro del redondeo delantero izquierdo
    ys = cy0 - math.sqrt(CAMP_R ** 2 - (xs - cx0) ** 2)                 # y de la superficie de la campana en x = xs
    giro = math.degrees(math.asin((xs - cx0) / CAMP_R))                 # angulo de la normal respecto a -Y (unos -32 grados)
    marco = L.caja('interruptor marco', 0.022, 0.004, 0.014, (xs, ys - 0.001, Z_BASE + 0.020), r=0.001, segs=2, mat=mate)
    tecla = L.caja('interruptor tecla', 0.018, 0.005, 0.011, (xs, ys - 0.0045, Z_BASE + 0.0215), r=0.001, segs=2, mat=verde)
    for ob in (marco, tecla):
        L.girar_malla(ob, (xs, ys, 0), 'Z', giro)
    P.piloto('led', (-TORRE_W / 2, Y_TORRE - 0.02, 0.245), d=0.006, color=(0.1, 1.0, 0.2), normal='-X')
    P.boton('pulsador', (-TORRE_W / 2, Y_TORRE - 0.02, 0.225), d=0.012, alto=0.004, normal='-X', mat=mate)

    # --- cable por la trasera baja (nace 4 mm dentro de la campana)
    P.cable('cable', (0.03, Y_CAMP + CAMP_D / 2 - 0.010, Z_BASE + 0.030), largo=0.20, d=0.007)

    return dict(ignorar=('cable', 'pulsador', 'led'))
