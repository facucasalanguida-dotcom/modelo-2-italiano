# -*- coding: utf-8 -*-
"""
K4 · Plancha electrica Cleiton 50 cm sobremesa Top (SKU CC-31-CL), 550 x 500 x 330.

Referencia: fotos e infografia acotada del fabricante (Gastroten). Carcasa
de inox cepillado; placa pulida de 500 x 425 (12 mm; Makro dice 8, solo
asoma el canto) que llega hasta el plano frontal, con el canto visto sobre
una banda negra de 15 mm; peto trasero de 125 sobre la placa con pestana
superior ranurada; petos laterales en cuna apoyados en el marco; cuerpo de
mandos retranqueado 20 mm entre dos laterales de 15 que llegan al frente,
con ruleta ON/OFF sobre dial blanco, piloto verde, ruleta de temperatura
sobre dial blanco (50-300), piloto ambar, logo Cleiton y sello TOP QUALITY;
tira de pictogramas y CE a la izquierda; cajon de grasa abajo a la
izquierda; cuatro tacos negros de 30.

Confirmado: medidas exteriores, placa 500 x 425, mandos y pegatinas.
Supuesto: reparto de alturas (patas 30, frontal 150, banda 15 + canto 12,
peto 125), trasera y salida del cable. Las ruletas (25 mm de alto) asoman
5 mm del plano frontal y se excluyen del control de medidas.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 0.550, 0.500, 0.330
H_PATA = 0.030
Z_CAJA = 0.180                 # techo de la caja de mandos
E_PLACA = 0.012
Z_PLACA = Z_CAJA + 0.015 + E_PLACA  # cara de la placa (0,207): banda 15 + canto 12
PLACA_W, PLACA_D = 0.500, 0.425
Y_FRENTE, Y_TRAS = -F / 2, F / 2
Y_PANEL = Y_FRENTE + 0.020     # frontal de mandos, retranqueado
Y_PLACA0 = Y_FRENTE + 0.002    # la placa llega hasta el plano frontal
E_PETO = 0.015


def _f(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def dial_onoff(ruta):
    S = 650
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse((4, 4, S - 4, S - 4), fill=(240, 240, 238, 255), outline=(180, 180, 180, 255), width=3)
    f = _f(64, True)
    dr.text((60, S / 2 - 40), 'ON', font=f, fill=(20, 20, 20, 255))
    dr.text((S - 200, S / 2 - 40), 'OFF', font=f, fill=(20, 20, 20, 255))
    dr.arc((110, 110, S - 110, S - 110), 30, 150, fill=(210, 30, 30, 255), width=14)
    dr.polygon([(S - 130, S / 2 + 120), (S - 175, S / 2 + 160), (S - 120, S / 2 + 175)], fill=(210, 30, 30, 255))
    im.save(ruta)


def dial_temp(ruta):
    S = 650
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse((4, 4, S - 4, S - 4), fill=(240, 240, 238, 255), outline=(180, 180, 180, 255), width=3)
    f = _f(38, True)
    R = 255
    for i, v in enumerate((50, 100, 150, 200, 250, 300)):
        a = math.radians(140 + i * 52)
        x, y = S / 2 + R * math.cos(a), S / 2 + R * math.sin(a)
        t = str(v)
        bb = dr.textbbox((0, 0), t, font=f)
        dr.text((x - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), t, font=f, fill=(20, 20, 20, 255))
    dr.arc((95, 95, S - 95, S - 95), 140, 400, fill=(210, 30, 30, 255), width=12)
    im.save(ruta)


def logo_cleiton(ruta):
    W, Hh = 550, 300
    im = Image.new('RGBA', (W, Hh), (255, 255, 255, 255))
    dr = ImageDraw.Draw(im)
    dr.rectangle((0, 0, W - 1, Hh - 1), outline=(200, 200, 200, 255), width=4)
    # C estilizada azul marino
    dr.arc((30, 40, 250, 260), 40, 320, fill=(20, 45, 110, 255), width=48)
    dr.text((250, 95), 'LEITON', font=_f(92, True), fill=(235, 140, 20, 255))
    im.save(ruta)


def sello_top(ruta):
    S = 300
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.regular_polygon((S / 2, S / 2, 140), 8, fill=(240, 240, 240, 255), outline=(140, 140, 140, 255))
    dr.polygon([(105, 120), (125, 80), (150, 110), (175, 80), (195, 120)], fill=(200, 30, 30, 255))
    f = _f(42, True)
    for t, y in (('TOP', 130), ('QUALITY', 185)):
        bb = dr.textbbox((0, 0), t, font=f if t == 'TOP' else _f(30, True))
        dr.text(((S - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1]), t, font=f if t == 'TOP' else _f(30, True), fill=(40, 40, 40, 255))
    im.save(ruta)


def pictogramas(ruta):
    W, Hh = 600, 100
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    for i in range(6):
        x = 10 + i * 98
        dr.rounded_rectangle((x, 10, x + 80, 90), radius=12, fill=(30, 30, 30, 255))
        dr.ellipse((x + 22, 30, x + 58, 66), outline=(230, 230, 230, 255), width=6)
    im.save(ruta)


def sello_ce(ruta):
    S = 300
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse((4, 4, S - 4, S - 4), fill=(245, 245, 245, 255), outline=(200, 200, 200, 255), width=3)
    for i in range(12):
        a = math.radians(i * 30)
        dr.ellipse((S / 2 + 115 * math.cos(a) - 9, S / 2 + 115 * math.sin(a) - 9, S / 2 + 115 * math.cos(a) + 9, S / 2 + 115 * math.sin(a) + 9),
                   fill=(210, 30, 30, 255))
    f = _f(90, True)
    bb = dr.textbbox((0, 0), 'CE', font=f)
    dr.text(((S - (bb[2] - bb[0])) / 2 - bb[0], (S - (bb[3] - bb[1])) / 2 - bb[1]), 'CE', font=f, fill=(30, 30, 30, 255))
    im.save(ruta)


def build():
    inox = L.mat_inox()
    placa_m = L.mat_inox_pulido()
    negro = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    banda = L.mat_plastico('Banda negra', (0.015, 0.015, 0.015), rug=0.5)

    # --- patas y caja: el cuerpo de mandos va retranqueado 20 mm entre dos
    # laterales de 15 mm que llegan al plano frontal (queda un suelo de 4 mm)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        L.cilindro(f'pata {i + 1}', 0.0175, H_PATA, (sx * (A / 2 - 0.045), sy * (F / 2 - 0.050), 0), r=0.004, segs=40, mat=negro)
    caja = L.caja('caja', A, F, Z_CAJA - H_PATA, (0, 0, H_PATA), r=0.002, segs=3, mat=inox)
    L.sustraer(caja, L.caja('retranqueo', A - 0.030, 0.021, Z_CAJA - H_PATA - 0.004 + 0.001,
                            (0, Y_FRENTE + 0.010 - 0.0005, H_PATA + 0.004)))
    # --- labio delantero de 15 mm bajo la placa, cubierto por la banda negra;
    # marco de la placa (4 mm bajo su cara) del que cuelgan los petos
    L.caja('labio', A, 0.040, Z_PLACA - E_PLACA - Z_CAJA, (0, Y_FRENTE + 0.020, Z_CAJA), r=0.002, segs=3, mat=inox)
    L.caja('banda negra', A + 0.0004, 0.0008, Z_PLACA - E_PLACA - Z_CAJA, (0, Y_FRENTE - 0.0002, Z_CAJA), mat=banda, suave=False)
    marco = L.caja('marco placa', A, Y_TRAS - Y_PLACA0, Z_PLACA - Z_CAJA - 0.004, (0, (Y_PLACA0 + Y_TRAS) / 2, Z_CAJA), r=0.001, segs=2, mat=inox)
    L.sustraer(marco, L.caja('marco hueco', PLACA_W + 0.002, PLACA_D + 0.002, 0.05, (0, Y_PLACA0 + PLACA_D / 2 + 0.001, Z_PLACA - 0.03)))
    # --- placa pulida 500 x 425 x 12, canto delantero visto
    L.caja('placa', PLACA_W, PLACA_D, E_PLACA, (0, Y_PLACA0 + PLACA_D / 2, Z_PLACA - E_PLACA), r=0.0015, segs=2, mat=placa_m)
    # --- peto trasero con pestana ranurada, y petos laterales en cuna
    L.caja('peto trasero', A, E_PETO, H - (Z_PLACA - 0.004), (0, Y_TRAS - E_PETO / 2, Z_PLACA - 0.004), r=0.0015, segs=2, mat=inox)
    pest = L.caja('peto pestana', A - 0.030, 0.032, 0.004, (0, Y_TRAS - E_PETO - 0.016, H - 0.004), r=0.0008, segs=2, mat=inox)
    paso = (A - 0.030 - 0.040 - 0.020) / 19     # 20 ranuras centradas, margen 20 mm
    for i in range(20):
        x = -(A - 0.030) / 2 + 0.020 + i * paso
        L.sustraer(pest, L.caja(f'ranura {i + 1}', 0.020, 0.008, 0.02, (x + 0.010, Y_TRAS - E_PETO - 0.016, H - 0.012), r=0.002))
    for nm, sx in (('izquierdo', -1), ('derecho', 1)):
        x = sx * (A / 2 - E_PETO / 2)
        L.prisma_yz(f'peto lateral {nm}', [(Y_PLACA0, Z_PLACA - 0.0045), (Y_TRAS - E_PETO, Z_PLACA - 0.0045), (Y_TRAS - E_PETO, H),
                                            (Y_PLACA0, Z_PLACA + 0.035)], x - E_PETO / 2, x + E_PETO / 2, mat=inox, r=0.001)

    # --- frontal de mandos
    zc = H_PATA + 0.095
    calcas = L.CALCAS_DIR
    dial_onoff(os.path.join(calcas, 'K4_dial_onoff.png'))
    dial_temp(os.path.join(calcas, 'K4_dial_temp.png'))
    logo_cleiton(os.path.join(calcas, 'K4_logo.png'))
    sello_top(os.path.join(calcas, 'K4_top.png'))
    pictogramas(os.path.join(calcas, 'K4_picto.png'))
    sello_ce(os.path.join(calcas, 'K4_ce.png'))
    L.calca('K4 dial onoff', os.path.join(calcas, 'K4_dial_onoff.png'), 0.065, 0.065, (-0.075, Y_PANEL - 0.0003, zc), normal='-Y')
    L.calca('K4 dial temp', os.path.join(calcas, 'K4_dial_temp.png'), 0.065, 0.065, (0.040, Y_PANEL - 0.0003, zc), normal='-Y')
    P.mando_ruleta('mando onoff', (-0.075, Y_PANEL, zc), d=0.045, alto=0.025, mat=negro, faldon=False)
    P.mando_ruleta('mando temperatura', (0.040, Y_PANEL, zc), d=0.045, alto=0.025, mat=negro, faldon=False)
    # pilotos apoyados en la cara del aro (3 mm por delante del panel)
    P.piloto('piloto verde', (-0.020, Y_PANEL - 0.003, zc + 0.012), d=0.010, color=(0.1, 1.0, 0.2))
    P.piloto('piloto ambar', (0.098, Y_PANEL - 0.003, zc + 0.012), d=0.010, color=(1.0, 0.45, 0.05))
    for nm, x, z in (('aro verde', -0.020, zc + 0.012), ('aro ambar', 0.098, zc + 0.012)):
        L.cilindro(nm, 0.0075, 0.003, (x, Y_PANEL - 0.003, z), eje='Y', segs=32, r=0.001, mat=negro)
    L.calca('K4 logo', os.path.join(calcas, 'K4_logo.png'), 0.055, 0.030, (0.180, Y_PANEL - 0.0003, zc + 0.012), normal='-Y')
    L.calca('K4 top', os.path.join(calcas, 'K4_top.png'), 0.030, 0.030, (0.180, Y_PANEL - 0.0003, zc - 0.035), normal='-Y')
    L.calca('K4 picto', os.path.join(calcas, 'K4_picto.png'), 0.060, 0.010, (-0.205, Y_PANEL - 0.0003, Z_CAJA - 0.012), normal='-Y')
    L.calca('K4 ce', os.path.join(calcas, 'K4_ce.png'), 0.018, 0.018, (-0.225, Y_PANEL - 0.0003, zc - 0.010), normal='-Y')
    # cajon de grasa abajo a la izquierda, con pestana-tirador
    L.caja('cajon frente', 0.120, 0.016, 0.060, (-0.190, Y_PANEL - 0.008, H_PATA + 0.006), r=0.002, segs=3, mat=inox)
    L.caja('cajon tirador', 0.120, 0.008, 0.003, (-0.190, Y_PANEL - 0.016, H_PATA + 0.063), r=0.001, segs=2, mat=inox)

    # --- cable por la trasera (supuesto)
    L.cilindro('prensaestopas', 0.008, 0.010, (0.15, Y_TRAS, 0.070), eje='Y', segs=24, r=0.002, mat=negro)
    P.cable('cable', (0.15, Y_TRAS + 0.010, 0.070), largo=0.25, d=0.009)

    return dict(ignorar=('cable', 'prensaestopas', 'mando'))
