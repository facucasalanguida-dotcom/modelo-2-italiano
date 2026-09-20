# -*- coding: utf-8 -*-
"""
K2 · Cocedor de pasta METRO Professional GNC1008, 8 L, 4 cestos.

Referencia: fotos oficiales (Amazon/METRO) y titulo oficial de METRO DE.
MEDIDAS: el cuerpo real mide 0,267 x 0,461 x 0,357; el 0,47 x 0,55 x 0,38
de la ficha de Makro (y del plano) es la envolvente con los mangos de los
cestos hacia los lados y el grifo delante. Aqui se modela el cuerpo real y
los cestos con sus mangos (inclinados 25 grados hacia arriba, como en las
fotos) de forma que la envolvente sea 0,470 de ancho (punta de los punos)
x 0,550 de fondo (punta de la palanca del grifo) x 0,360 de alto.
NOTA: el plano dice 0,38 de alto y el modelo mide 0,360: el techo del
cabezal esta a 0,360 (cuerpo real 357) y los punos inclinados llegan a
~0,35; los 2 cm que faltan serian los mangos aun mas levantados.

Confirmado: cuerpo, cuba 237 x 297 x 194, 4 cestos 115 x 104 x 149 con
mangos de horquilla y puno negro (~Ø28 x 97) a 25 grados, panel inclinado
con logo, reset, dos pilotos y ruleta 40-110 C (40 a la derecha, 110 a la
izquierda, escala por abajo), pletina central colgada del gancho dentro de
la cuba con MAX/MIN, grifo cromado abajo a la derecha con la palanca negra
cerrada (colgando hacia delante y abajo), 4 tacos negros.
Supuesto: salida del cable por la trasera del cabezal.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, FB = 0.267, 0.461                  # cuerpo real
H_PIE = 0.012
Z_RIM = 0.270                         # borde de la cuba
Z_TOP = 0.360                         # techo del cabezal
GRIFO = 0.089                         # lo que sobresale el grifo del frontal
Y_OFF = GRIFO / 2                     # el origen es el centro de la envolvente (con grifo)
Y_CAB = 0.0995 + Y_OFF                # cara frontal del cabezal
Y_TRAS = FB / 2 + Y_OFF               # 0,275
Y_FRENTE = -FB / 2 + Y_OFF            # -0,186
CUBA_W, CUBA_D, CUBA_P = 0.237, 0.297, 0.194
CUBA_Y = Y_FRENTE + 0.015 + CUBA_D / 2   # -0,067
INCL = 30.0                           # inclinacion del panel (grados hacia atras)
Z_PANEL0 = 0.300                      # arranque del panel inclinado
ALTO_PANEL = (Z_TOP - Z_PANEL0) / math.cos(math.radians(INCL))   # 0,0693 a lo largo del panel
Y_TOP_FRONT = Y_CAB + (Z_TOP - Z_PANEL0) * math.tan(math.radians(INCL))


def _f(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_panel(ruta):
    """Serigrafia del panel inclinado (todo el ancho x el alto del panel):
    logo METRO Professional, simbolo de rearme, iconos de los pilotos,
    recuadro 'C' y escala 40-110 alrededor de la ruleta. 267 x 69 mm ->
    4 px/mm."""
    W, Hh = int(A * 4000), int(ALTO_PANEL * 4000)
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    negro = (20, 20, 22, 255)

    def px(x, t):
        # x en m desde el centro, t altura en m desde el borde inferior del panel
        return (W / 2 + x * 4000, Hh - t * 4000)

    # logo: escudo pentagonal con METRO / PROFESSIONAL
    cx, cy = px(-0.095, 0.036)
    dr.polygon([(cx - 40, cy - 60), (cx + 40, cy - 60), (cx + 40, cy + 25), (cx, cy + 60), (cx - 40, cy + 25)],
               outline=negro, width=4)
    f = _f(30, True)
    bb = dr.textbbox((0, 0), 'METRO', font=f)
    dr.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - 42 - bb[1]), 'METRO', font=f, fill=negro)
    f2 = _f(12)
    bb = dr.textbbox((0, 0), 'PROFESSIONAL', font=f2)
    dr.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - 2 - bb[1]), 'PROFESSIONAL', font=f2, fill=negro)
    # simbolo de rearme bajo el boton
    cx, cy = px(-0.052, 0.024)
    dr.arc((cx - 16, cy - 16, cx + 16, cy + 16), 300, 240, fill=negro, width=4)
    # iconos de los pilotos: encendido (verde, arriba) y termometro (rojo, abajo)
    cx, cy = px(-0.033, 0.048)
    dr.arc((cx - 14, cy - 14, cx + 14, cy + 14), 300, 240, fill=negro, width=4)
    dr.line((cx, cy - 18, cx, cy - 2), fill=negro, width=4)
    cx, cy = px(-0.033, 0.022)
    dr.rounded_rectangle((cx - 6, cy - 20, cx + 6, cy + 8), radius=6, outline=negro, width=3)
    dr.ellipse((cx - 11, cy + 4, cx + 11, cy + 26), outline=negro, width=3)
    # recuadro con termometro y C a la izquierda de la ruleta
    cx, cy = px(0.010, 0.058)
    dr.rectangle((cx - 22, cy - 22, cx + 22, cy + 22), outline=negro, width=3)
    dr.text((cx - 8, cy - 18), '°C', font=_f(22, True), fill=negro)
    # escala de la ruleta: 40 a la derecha casi a la altura del centro, la
    # escala corre por abajo y el 110 queda a la izquierda; OFF arriba
    kx, ky = px(0.050, 0.035)
    R = 0.026 * 4000
    f3 = _f(24, True)
    valores = [40, 50, 60, 70, 80, 90, 100, 110]
    # el 40 a -15 grados (derecha) y el 110 a 190 grados (izquierda) en sentido horario
    for i, v in enumerate(valores):
        ang = math.radians(-15 + i * (205 / 7))
        x, y = kx + R * math.cos(ang), ky + R * math.sin(ang)
        t = str(v)
        bb = dr.textbbox((0, 0), t, font=f3)
        dr.text((x - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), t, font=f3, fill=negro)
    # marca de apagado arriba
    dr.polygon([(kx, ky - R + 14), (kx - 7, ky - R + 30), (kx + 7, ky - R + 30)], fill=negro)
    im.save(ruta)


def calca_maxmin(ruta):
    W, Hh = 160, 400
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    f = _f(34, True)
    for t, y in (('MAX', 60), ('MIN', 300)):
        bb = dr.textbbox((0, 0), t, font=f)
        dr.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1]), t, font=f, fill=(60, 60, 62, 255))
        dr.line((20, y + 50, W - 20, y + 50), fill=(60, 60, 62, 255), width=5)
    im.save(ruta)


def _en_panel(objs):
    """Inclina hacia atras lo construido sobre la cara vertical y = Y_CAB
    para que quede sobre el panel inclinado."""
    for ob in objs:
        L.girar_malla(ob, (0, Y_CAB, Z_PANEL0), 'X', -INCL)


def build():
    inox = L.mat_inox()
    inox_p = L.mat_inox_pulido()
    negro = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    cromo = L.mat_cromo()
    goma = L.mat_goma()
    # base satinada (mas rugosa) para que los cestos no lean negros desde arriba
    perf = L.mat_chapa_perforada('Cesto perforado', d=0.003, paso=0.0052, base=L.mat_inox_satinado())

    # --- tacos de goma
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        P.pie_goma(f'taco {i + 1}', (sx * (A / 2 - 0.028), Y_OFF + sy * (FB / 2 - 0.028), 0), d=0.030, h=H_PIE)

    # --- cuerpo inferior con la cuba
    cuerpo = L.caja('cuerpo', A, FB, Z_RIM - H_PIE, (0, Y_OFF, H_PIE), r=0.002, r_vert=0.008, segs=3, mat=inox)
    P.cuba('cuba', cuerpo, (0, CUBA_Y, Z_RIM), CUBA_W, CUBA_D, CUBA_P, r_esq=0.025, r_fondo=0.012,
           mat=inox_p, desague=False)
    z_fondo = Z_RIM - CUBA_P
    # desague: rehundido circular delante a la derecha con rejilla de malla
    L.cilindro('desague rehundido', 0.040, 0.0008, (CUBA_W / 2 - 0.055, CUBA_Y - CUBA_D / 2 + 0.055, z_fondo + 0.0012),
               segs=64, mat=inox_p)
    L.cilindro('desague', 0.0125, 0.004, (CUBA_W / 2 - 0.055, CUBA_Y - CUBA_D / 2 + 0.055, z_fondo + 0.0012), segs=48,
               r=0.001, mat=cromo)
    L.cilindro('desague malla', 0.0095, 0.001, (CUBA_W / 2 - 0.055, CUBA_Y - CUBA_D / 2 + 0.055, z_fondo + 0.0052),
               segs=32, mat=L.mat_chapa_perforada('Malla fina', d=0.0008, paso=0.0013))
    # resistencia tubular en 3 lazos sobre el fondo
    for i, y in enumerate((-0.09, -0.03, 0.03)):
        L.tubo_curva(f'resistencia {i + 1}',
                     [(-0.095, CUBA_Y + y, z_fondo + 0.012), (0.095, CUBA_Y + y, z_fondo + 0.012)],
                     0.004, segs=16, mat=inox_p, suavizar=False)
    # serpentin: el codo 1 (izquierda) une los tubos 1-2 y el codo 2 (derecha) los tubos 2-3
    for i, pts in enumerate(([(-0.095, CUBA_Y - 0.09), (-0.115, CUBA_Y - 0.06), (-0.095, CUBA_Y - 0.03)],
                             [(0.095, CUBA_Y - 0.03), (0.115, CUBA_Y), (0.095, CUBA_Y + 0.03)])):
        L.tubo_curva(f'resistencia codo {i + 1}', [(x, y, z_fondo + 0.012) for x, y in pts],
                     0.004, segs=16, mat=inox_p)
    # bandeja perforada (falso fondo)
    L.caja('falso fondo', CUBA_W - 0.006, CUBA_D - 0.006, 0.0012, (0, CUBA_Y, z_fondo + 0.022), mat=perf, suave=False)

    # --- cabezal trasero con panel inclinado
    L.prisma_yz('cabezal', [(Y_CAB, Z_RIM - 0.001), (Y_TRAS, Z_RIM - 0.001), (Y_TRAS, Z_TOP),
                            (Y_TOP_FRONT, Z_TOP), (Y_CAB, Z_PANEL0)], -A / 2, A / 2, mat=inox, r=0.002)
    # serigrafia del panel
    ruta = os.path.join(L.CALCAS_DIR, 'K2_panel.png')
    calca_panel(ruta)
    cal = L.calca('K2 panel', ruta, A - 0.004, ALTO_PANEL - 0.004, (0, Y_CAB - 0.0003, Z_PANEL0 + ALTO_PANEL / 2), normal='-Y')
    piezas = [cal]
    # boton de rearme, pilotos y ruleta, construidos en vertical y luego inclinados
    piezas.append(P.boton('reset', (-0.052, Y_CAB, Z_PANEL0 + 0.040), d=0.012, alto=0.005, mat=negro))
    piezas.append(P.piloto('piloto verde', (-0.018, Y_CAB, Z_PANEL0 + 0.048), d=0.010, color=(0.1, 1.0, 0.2)))
    piezas.append(P.piloto('piloto rojo', (-0.018, Y_CAB, Z_PANEL0 + 0.022), d=0.010, color=(1.0, 0.05, 0.02)))
    piezas += P.mando_ruleta('mando', (0.050, Y_CAB, Z_PANEL0 + 0.035), d=0.035, alto=0.018, mat=negro)
    _en_panel(piezas)

    # --- pletina central con gancho reposacestos y MAX/MIN: cuelga del
    # gancho dentro de la cuba, pegada a su pared trasera (y ~ 0,122); su
    # parte alta (0,270-0,298) asoma delante de la franja del borde
    Y_PLET = CUBA_Y + CUBA_D / 2 - 0.0012 - 0.002      # centro de la pletina (2 mm de chapa)
    L.caja('pletina', 0.040, 0.002, Z_RIM - 0.100 + 0.028, (0, Y_PLET, 0.100), mat=inox)
    L.caja('gancho', 0.060, 0.040, 0.002, (0, Y_CAB - 0.020, Z_RIM + 0.026), r=0.0008, segs=2, mat=inox)
    L.caja('gancho labio', 0.060, 0.002, 0.018, (0, Y_CAB - 0.040, Z_RIM + 0.008), r=0.0008, segs=2, mat=inox)
    ruta = os.path.join(L.CALCAS_DIR, 'K2_maxmin.png')
    calca_maxmin(ruta)
    L.calca('K2 maxmin', ruta, 0.016, 0.040, (0, Y_PLET - 0.001 - 0.0003, 0.235), normal='-Y')

    # --- 4 cestos perforados con mangos a los lados
    BW, BD, BH = 0.115, 0.104, 0.149
    z_b = z_fondo + 0.024
    ANG = 25.0                                # inclinacion de los mangos hacia arriba (fotos)
    ca, sa = math.cos(math.radians(ANG)), math.sin(math.radians(ANG))
    R_PUNO, RB_PUNO = 0.014, 0.004            # radio del puno y redondeo de sus tapas
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        xc, yc = sx * (BW / 2 + 0.002), CUBA_Y + sy * (BD / 2 + 0.003)
        cesto = L.caja(f'cesto {i + 1}', BW, BD, BH, (xc, yc, z_b), r_vert=0.006, r=0.002, segs=3, mat=perf)
        hueco = L.caja(f'cesto {i + 1} hueco', BW - 0.0012, BD - 0.0012, BH, (xc, yc, z_b + 0.0006), r_vert=0.0055, r=0.0015, segs=3)
        L.sustraer(cesto, hueco)
        # aro superior de varilla
        zr = z_b + BH - 0.002
        L.cilindro(f'cesto {i + 1} aro 1', 0.0015, BW, (xc - BW / 2, yc - BD / 2 + 0.0015, zr), eje='X', segs=12, mat=inox_p)
        L.cilindro(f'cesto {i + 1} aro 2', 0.0015, BW, (xc - BW / 2, yc + BD / 2 - 0.0015, zr), eje='X', segs=12, mat=inox_p)
        L.cilindro(f'cesto {i + 1} aro 3', 0.0015, BD, (xc - BW / 2 + 0.0015, yc - BD / 2, zr), eje='Y', segs=12, mat=inox_p)
        L.cilindro(f'cesto {i + 1} aro 4', 0.0015, BD, (xc + BW / 2 - 0.0015, yc - BD / 2, zr), eje='Y', segs=12, mat=inox_p)
        # mango: horquilla de varilla que sube pegada al cesto, pasa por
        # encima del borde y converge en la varilla; varilla y puno negro se
        # construyen horizontales y se inclinan ANG grados hacia arriba
        # girando sobre el arranque de la varilla S
        xo = xc + sx * BW / 2
        S = (xo + sx * 0.018, yc, zr + 0.047)
        for j, s in enumerate((-1, 1)):
            L.tubo_curva(f'cesto {i + 1} horquilla {j + 1}',
                         [(xo, yc + s * 0.035, zr), (xo, yc + s * 0.028, zr + 0.030), S,
                          (S[0] + sx * 0.006 * ca, yc, S[2] + 0.006 * sa)], 0.002, segs=12, mat=inox_p)
        mango = [L.cilindro(f'cesto {i + 1} varilla', 0.002, 0.014, (S[0] - (0.014 if sx < 0 else 0), yc, S[2]),
                            eje='X', segs=12, mat=inox_p)]
        # distancia de S a la tapa del puno para que su punto mas alejado
        # (tapa inclinada con el canto redondeado) quede en +-0,235
        l_tapa = (A / 2 + 0.1015 - abs(S[0]) - R_PUNO * sa - RB_PUNO * (1 - ca - sa)) / ca
        largo = l_tapa - 0.008                    # el puno empieza 8 mm mas alla de S
        x_ini = S[0] + sx * 0.008
        mango.append(L.cilindro(f'cesto {i + 1} puno', R_PUNO, largo, (x_ini - (largo if sx < 0 else 0), yc, S[2]),
                                eje='X', segs=32, r=RB_PUNO, mat=negro))
        for ob in mango:
            L.girar_malla(ob, S, 'Y', -sx * ANG)

    # --- grifo de vaciado cromado, abajo a la derecha del frontal
    gx, gz = 0.045, 0.060
    GY = Y_FRENTE - 0.0645                # eje vertical del grifo
    L.cilindro('grifo tuerca', 0.012, 0.007, (gx, Y_FRENTE - 0.007, gz), eje='Y', segs=6, mat=cromo)
    L.cilindro('grifo tubo', 0.0075, 0.0605, (gx, GY, gz), eje='Y', segs=32, mat=cromo)
    L.cilindro('grifo cuerpo', 0.015, 0.034, (gx, GY, gz - 0.017), segs=40, r=0.005, mat=cromo)
    L.cilindro('grifo eje', 0.005, 0.010, (gx, GY, gz + 0.017), segs=24, mat=cromo)
    L.caja('grifo cabeza', 0.012, 0.020, 0.010, (gx, GY - 0.005, gz + 0.027), r=0.002, segs=2, mat=cromo)
    # palanca negra (grifo cerrado): pivota en la cabeza y cuelga hacia
    # delante y abajo (65 grados) por delante del cuerpo; su punta es el
    # punto mas adelantado del aparato (GRIFO = 0,089)
    piv = (gx, GY - 0.0087, gz + 0.032)
    palanca = L.cilindro('grifo palanca', 0.0035, 0.032, (gx, piv[1] - 0.032, piv[2]), eje='Y', segs=24,
                         r=0.0025, mat=negro)
    L.girar_malla(palanca, piv, 'X', 65)
    L.cilindro('grifo salida', 0.0075, 0.030, (gx, GY, gz - 0.047), segs=32, mat=cromo)
    L.cilindro('grifo boca', 0.009, 0.006, (gx, GY, gz - 0.053), segs=32, r=0.001, mat=cromo)

    # --- cable por la trasera del cabezal (supuesto)
    L.cilindro('prensaestopas', 0.008, 0.010, (-0.080, Y_TRAS, 0.315), eje='Y', segs=24, r=0.002, mat=negro)
    P.cable('cable', (-0.080, Y_TRAS + 0.010, 0.315), largo=0.25, d=0.009)

    return dict(medidas=(0.470, 0.550, 0.360), ignorar=('cable', 'prensaestopas'))
