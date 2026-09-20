# -*- coding: utf-8 -*-
"""
K3 · Freidora electrica de sobremesa 7 L con grifo, 1 cuba (Meral MERFRY 7 L
GRIFO o su OEM; el texto y las medidas de Makro son literales), 270 x 460 x 370.

Referencia: renders de catalogo Meral (csvalles). Cuerpo y cabezal de inox
pulido; cabezal desmontable trasero con panel inclinado (interruptor
basculante I/O con piloto verde, piloto ambar con icono de termometro,
ruleta de termostato con dial STOP / 100-190); en la cara vertical del
cabezal, guarda reposacestas de inox saliente con ranura y asa negra en D;
cuba con reborde perimetral; cesta de malla 195 x 215 x 120 con mango negro
plano que sale por el frente; logo MERAL gris arriba a la izquierda del
frontal; grifo cromado con maneta y tapon negros abajo a la derecha; cuatro
tacos negros.

La envolvente del plano (0,27 x 0,46 x 0,37) es el cuerpo: el mango de la
cesta (150) y el grifo (70) sobresalen por delante y se excluyen del control.
Supuesto: reparto de alturas cuerpo/cabezal (estimado del render), trasera,
cable, forma exacta de la resistencia.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 0.270, 0.460, 0.370
H_PIE = 0.012
Z_RIM = 0.230                        # borde de la cuba (reborde de 15)
Z_VERT = 0.315                       # fin de la cara vertical del cabezal
Y_CAB = 0.105                        # cara frontal del cabezal
Y_TRAS, Y_FRENTE = F / 2, -F / 2
INCL = 25.0
ALTO_PANEL = (H - Z_VERT) / math.cos(math.radians(INCL))
Y_TOP_FRONT = Y_CAB + (H - Z_VERT) * math.tan(math.radians(INCL))
CUBA_W, CUBA_D, CUBA_P = 0.240, 0.300, 0.160
CUBA_Y = Y_FRENTE + 0.0175 + CUBA_D / 2


def _f(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_panel(ruta):
    """Panel: 'I / O' junto al basculante, icono termometro, dial STOP y
    100-190 con barras rojas, a 4 px/mm sobre 270 x ALTO_PANEL mm."""
    W, Hh = int(A * 4000), int(ALTO_PANEL * 4000)
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    negro = (25, 25, 27, 255)
    rojo = (200, 30, 30, 255)

    def px(x, t):
        return (W / 2 + x * 4000, Hh - t * 4000)

    # icono termometro junto al piloto ambar
    cx, cy = px(0.005, 0.024)
    dr.rounded_rectangle((cx - 5, cy - 18, cx + 5, cy + 6), radius=5, outline=negro, width=3)
    dr.ellipse((cx - 9, cy + 3, cx + 9, cy + 21), outline=negro, width=3)
    # dial de la ruleta: STOP arriba; 100..150 por la derecha/abajo, 160..190 por la izquierda
    kx, ky = px(0.062, 0.030)
    R = 0.027 * 4000
    f = _f(22, True)
    bb = dr.textbbox((0, 0), 'STOP', font=f)
    dr.text((kx - (bb[2] - bb[0]) / 2 - bb[0], ky - R - 26 - bb[1]), 'STOP', font=f, fill=negro)
    f2 = _f(18)
    marcas = [(100, 20), (110, 50), (120, 80), (130, 110), (140, 140), (150, 170),
              (160, 200), (170, 225), (180, 250), (190, 275)]
    for v, ang in marcas:
        a = math.radians(ang - 90)
        x, y = kx + R * math.cos(a), ky + R * math.sin(a)
        t = f'{v}°'
        bb = dr.textbbox((0, 0), t, font=f2)
        dr.text((x - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), t, font=f2, fill=negro)
    # barras rojas de intensidad entre 160 y 190
    for i, ang in enumerate((205, 215, 230, 245, 260)):
        a = math.radians(ang - 90)
        r1, r2 = R - 30, R - 30 + 6 + i * 3
        dr.line((kx + r1 * math.cos(a), ky + r1 * math.sin(a), kx + r2 * math.cos(a), ky + r2 * math.sin(a)), fill=rojo, width=5)
    im.save(ruta)


def calca_logo(ruta):
    W, Hh = 720, 240
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    gris = (110, 112, 114, 255)
    # simbolo: aspa de cuatro puntas
    cx, cy = 70, 95
    for a in (45, 135, 225, 315):
        r = math.radians(a)
        dr.polygon([(cx, cy), (cx + 55 * math.cos(r - 0.35), cy + 55 * math.sin(r - 0.35)),
                    (cx + 55 * math.cos(r + 0.35), cy + 55 * math.sin(r + 0.35))], fill=gris)
    dr.text((150, 40), 'MERAL', font=_f(96), fill=gris)
    dr.text((152, 150), 'Equipamiento Hostelero', font=_f(28), fill=gris)
    im.save(ruta)


def _en_panel(objs):
    for ob in objs:
        L.girar_malla(ob, (0, Y_CAB, Z_VERT), 'X', -INCL)


def build():
    inox = L.mat_inox_pulido()
    negro = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    cromo = L.mat_cromo()
    malla = L.mat_chapa_perforada('Malla de cesta', d=0.0022, paso=0.0032)

    # --- tacos, cuerpo y cuba
    P.pies_goma('taco', A, F, inset=0.026, d=0.025, h=H_PIE)
    cuerpo = L.caja('cuerpo', A, F, Z_RIM - H_PIE - 0.003, (0, 0, H_PIE), r=0.002, r_vert=0.009, segs=3, mat=inox)
    # reborde perimetral elevado 3 mm alrededor de la boca
    reborde = L.caja('reborde', A, F, 0.003, (0, 0, Z_RIM - 0.003), r=0.0015, segs=2, mat=inox)
    L.sustraer(reborde, L.caja('reborde hueco', CUBA_W + 0.006, CUBA_D + 0.006, 0.02, (0, CUBA_Y, Z_RIM - 0.01), r_vert=0.02))
    P.cuba('cuba', cuerpo, (0, CUBA_Y, Z_RIM - 0.003), CUBA_W, CUBA_D, CUBA_P, r_esq=0.020, r_fondo=0.010, mat=inox, desague=False)
    z_fondo = Z_RIM - 0.003 - CUBA_P
    # resistencia en U doble sobre el fondo, saliendo del cabezal
    for i, x in enumerate((-0.075, -0.025, 0.025, 0.075)):
        L.tubo_curva(f'resistencia {i + 1}', [(x, Y_CAB - 0.005, z_fondo + 0.030), (x, CUBA_Y - 0.12, z_fondo + 0.030)],
                     0.0045, segs=16, mat=inox, suavizar=False)
    for i, (xa, xb) in enumerate(((-0.075, -0.025), (0.025, 0.075))):
        L.tubo_curva(f'resistencia codo {i + 1}', [(xa, CUBA_Y - 0.12, z_fondo + 0.030), ((xa + xb) / 2, CUBA_Y - 0.14, z_fondo + 0.030),
                                                     (xb, CUBA_Y - 0.12, z_fondo + 0.030)], 0.0045, segs=16, mat=inox)

    # --- cabezal desmontable: cara vertical + panel inclinado
    L.prisma_yz('cabezal', [(Y_CAB, Z_RIM - 0.004), (Y_TRAS, Z_RIM - 0.004), (Y_TRAS, H), (Y_TOP_FRONT, H), (Y_CAB, Z_VERT)],
                -A / 2, A / 2, mat=inox, r=0.002)
    ruta = os.path.join(L.CALCAS_DIR, 'K3_panel.png')
    calca_panel(ruta)
    piezas = [L.calca('K3 panel', ruta, A - 0.004, ALTO_PANEL - 0.004, (0, Y_CAB - 0.0003, Z_VERT + ALTO_PANEL / 2), normal='-Y')]
    # interruptor basculante negro con I/O, piloto verde a su derecha
    bas = L.caja('basculante marco', 0.032, 0.004, 0.024, (-0.085, Y_CAB - 0.004, Z_VERT + 0.018), r=0.001, segs=2, mat=negro)
    tecla = L.caja('basculante tecla', 0.026, 0.006, 0.018, (-0.085, Y_CAB - 0.010, Z_VERT + 0.021), r=0.0015, segs=2, mat=negro)
    L.girar_malla(tecla, (-0.085, Y_CAB - 0.007, Z_VERT + 0.030), 'X', 12)
    piezas += [bas, tecla]
    piezas.append(P.piloto('piloto verde', (-0.058, Y_CAB, Z_VERT + 0.030), d=0.008, color=(0.1, 1.0, 0.2)))
    piezas.append(P.piloto('piloto ambar', (-0.010, Y_CAB, Z_VERT + 0.030), d=0.008, color=(1.0, 0.45, 0.05)))
    piezas += P.mando_ruleta('mando', (0.062, Y_CAB, Z_VERT + 0.030), d=0.040, alto=0.020, mat=negro)
    _en_panel(piezas)
    # guarda reposacestas: caja inox saliente con ranura, en el centro de la cara vertical
    guarda = L.caja('guarda', 0.080, 0.045, 0.050, (0, Y_CAB - 0.0225, Z_RIM + 0.020), r=0.003, segs=3, mat=inox)
    L.sustraer(guarda, L.caja('guarda ranura', 0.060, 0.10, 0.010, (0, Y_CAB - 0.0225, Z_RIM + 0.045)))
    L.sustraer(guarda, L.caja('guarda hueco', 0.076, 0.10, 0.046, (0, Y_CAB - 0.06, Z_RIM + 0.022)))
    # asa negra en D a la derecha de la guarda
    L.tubo_curva('asa D', [(0.062, Y_CAB, Z_RIM + 0.020), (0.062, Y_CAB - 0.035, Z_RIM + 0.024),
                           (0.100, Y_CAB - 0.035, Z_RIM + 0.055), (0.100, Y_CAB, Z_RIM + 0.075)],
                 0.007, segs=20, mat=negro)

    # --- cesta de malla con mango negro hacia delante
    BW, BD, BH = 0.195, 0.215, 0.120
    zb = z_fondo + 0.045
    cesta = L.caja('cesta', BW, BD, BH, (0, CUBA_Y, zb), r_vert=0.008, r=0.003, segs=3, mat=malla)
    L.sustraer(cesta, L.caja('cesta hueco', BW - 0.0012, BD - 0.0012, BH, (0, CUBA_Y, zb + 0.0006), r_vert=0.0075, r=0.0025, segs=3))
    zr = zb + BH - 0.002
    for nm, w, d, pos, eje in (('aro 1', BW, 0, (-BW / 2, CUBA_Y - BD / 2 + 0.0015, zr), 'X'), ('aro 2', BW, 0, (-BW / 2, CUBA_Y + BD / 2 - 0.0015, zr), 'X'),
                               ('aro 3', 0, BD, (-BW / 2 + 0.0015, CUBA_Y - BD / 2, zr), 'Y'), ('aro 4', 0, BD, (BW / 2 - 0.0015, CUBA_Y - BD / 2, zr), 'Y')):
        L.cilindro(f'cesta {nm}', 0.0015, w or d, pos, eje=eje, segs=12, mat=inox)
    # horquilla: de las esquinas delanteras sube al borde y sigue horizontal hacia el frente
    yf = CUBA_Y - BD / 2
    for j, s in enumerate((-1, 1)):
        L.tubo_curva(f'cesta horquilla {j + 1}',
                     [(s * 0.06, yf, zr), (s * 0.035, yf - 0.05, Z_RIM + 0.012), (s * 0.012, Y_FRENTE - 0.02, Z_RIM + 0.012),
                      (s * 0.012, Y_FRENTE - 0.135, Z_RIM + 0.012)], 0.0022, segs=12, mat=inox)
    L.tubo_curva('cesta horquilla u', [(-0.012, Y_FRENTE - 0.135, Z_RIM + 0.012), (0, Y_FRENTE - 0.150, Z_RIM + 0.012),
                                       (0.012, Y_FRENTE - 0.135, Z_RIM + 0.012)], 0.0022, segs=12, mat=inox)
    mango = L.caja('cesta mango', 0.030, 0.120, 0.008, (0, Y_FRENTE - 0.075, Z_RIM + 0.012), r=0.003, segs=3, mat=negro)
    for k, y in enumerate((Y_FRENTE - 0.035, Y_FRENTE - 0.110)):
        L.cilindro(f'cesta mango tornillo {k + 1}', 0.003, 0.001, (0, y, Z_RIM + 0.020), segs=16, mat=cromo)

    # --- logo en el frontal, arriba a la izquierda
    ruta = os.path.join(L.CALCAS_DIR, 'K3_logo.png')
    calca_logo(ruta)
    L.calca('K3 logo', ruta, 0.072, 0.024, (-0.075, Y_FRENTE - 0.0003, Z_RIM - 0.040), normal='-Y')

    # --- grifo cromado con maneta y tapon negros, abajo a la derecha
    gx, gz = 0.048, 0.070
    L.cilindro('grifo tuerca', 0.011, 0.006, (gx, Y_FRENTE - 0.006, gz), eje='Y', segs=6, mat=cromo)
    L.cilindro('grifo tubo', 0.007, 0.040, (gx, Y_FRENTE - 0.042, gz), eje='Y', segs=32, mat=cromo)
    L.cilindro('grifo cuerpo', 0.014, 0.030, (gx, Y_FRENTE - 0.052, gz - 0.015), segs=40, r=0.004, mat=cromo)
    maneta = L.caja('grifo maneta', 0.012, 0.028, 0.016, (gx, Y_FRENTE - 0.052 - 0.006, gz + 0.015), r=0.004, segs=3, mat=negro)
    L.girar_malla(maneta, (gx, Y_FRENTE - 0.052, gz + 0.015), 'X', -25)
    L.cilindro('grifo salida', 0.007, 0.026, (gx, Y_FRENTE - 0.052, gz - 0.041), segs=32, mat=cromo)
    L.cilindro('grifo tapon', 0.009, 0.010, (gx, Y_FRENTE - 0.052, gz - 0.051), segs=32, r=0.002, mat=negro)

    # --- cable por la trasera del cabezal (supuesto)
    L.cilindro('prensaestopas', 0.008, 0.010, (-0.08, Y_TRAS, 0.300), eje='Y', segs=24, r=0.002, mat=negro)
    P.cable('cable', (-0.08, Y_TRAS + 0.010, 0.300), largo=0.25, d=0.009)

    return dict(ignorar=('grifo', 'cesta mango', 'cesta horquilla', 'cable', 'prensaestopas'))
