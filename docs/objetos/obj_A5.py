# -*- coding: utf-8 -*-
"""
A5 · Botellero frigorifico BTL1000, 1040 x 580 x 850, 240 L (vendedor
Arsent, misma ficha y fotos que Makro).

Referencia: fotos del vendedor y detalles de El Hostelero (mismo casco).
Es un ARCON: acero inoxidable satinado interior y exterior, cornisa
superior de 70 que vuela 10 y aloja, en un cerco de 12, DOS TAPAS CORREDERAS
CIEGAS de inox (no cristal) a ras, con borde delantero doblado y carril central; frontal liso
con un rebaje negro de mandos (interruptor verde luminoso + display rojo)
abajo a la izquierda (display a la izquierda, tecla verde a la derecha),
rejilla de ranuras cortas al tresbolillo en la esquina inferior izquierda,
abrebotellas de inox con caja recogechapas contigua a la derecha, justo
bajo la cornisa (version El Hostelero; la foto de Makro no lo lleva), tapon negro de desague abajo a la derecha, zocalo
retranqueado 20 sobre pies ocultos. Interior con separadores de rejilla
negra (no visible con las tapas cerradas).

Confirmado: medidas, todo inox, tapas ciegas correderas, disposicion.
Supuesto: display digital (Arsent dice termostato manual), alto de cornisa
y de zocalo, pegatina del vendedor omitida.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 1.040, 0.580, 0.850
H_ZOC = 0.020                     # zocalo retranqueado
CORNISA_H, CORNISA_V = 0.070, 0.010
Y_FRENTE, Y_TRAS = -F / 2, F / 2
Y_CASCO = Y_FRENTE + CORNISA_V    # el casco queda 10 mm por detras de la cornisa
Z_CASCO1 = H - CORNISA_H


def calca_mandos(ruta):
    W, Hh = 440, 180
    im = Image.new('RGBA', (W, Hh), (14, 14, 16, 255))
    dr = ImageDraw.Draw(im)
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 96)
    dr.rounded_rectangle((40, 30, 240, 150), radius=10, fill=(30, 8, 6, 255))
    dr.text((90, 34), '4', font=f, fill=(255, 40, 20, 255))
    im.save(ruta)


def build():
    inox = L.mat_inox()
    inox_p = L.mat_inox_pulido()
    plast = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    zoc = L.mat_chapa('Zocalo gris oscuro', (0.06, 0.06, 0.06), rug=0.6, brillo=0.0)

    # --- zocalo retranqueado y casco
    L.caja('zocalo', A - 2 * CORNISA_V - 0.040, F - CORNISA_V - 0.040, H_ZOC + 0.002, (0, Y_CASCO + 0.020 + (F - CORNISA_V - 0.040) / 2, 0), mat=zoc, suave=False)
    L.caja('casco', A - 2 * CORNISA_V, F - CORNISA_V, Z_CASCO1 - H_ZOC + 0.002, (0, Y_CASCO + (F - CORNISA_V) / 2, H_ZOC), r=0.003, segs=3, mat=inox)
    # --- cornisa: marco de 70 que vuela 10 al frente y laterales; dentro, las dos tapas y la franja fija trasera
    cor = L.caja('cornisa', A, F, CORNISA_H, (0, 0, Z_CASCO1), r=0.003, segs=3, mat=inox)
    L.sustraer(cor, L.caja('cornisa hueco', A - 0.024, F - 0.024, 0.10, (0, 0.0, Z_CASCO1 + 0.036), r_vert=0.006))
    L.caja('cornisa fondo', A - 0.024 - 0.001, F - 0.024 - 0.001, 0.002, (0, 0, Z_CASCO1 + 0.036), mat=L.mat_plastico('Interior oscuro', (0.01, 0.01, 0.01), rug=0.9), suave=False)
    L.caja('franja trasera', A - 0.024, 0.080, 0.018, (0, F / 2 - 0.012 - 0.040, Z_CASCO1 + 0.050), r=0.002, segs=2, mat=inox)
    L.caja('carril central', 0.030, F - 0.024 - 0.080, 0.006, (0, -0.040, Z_CASCO1 + 0.064), r=0.001, segs=2, mat=inox_p)
    tw = (A - 0.024 - 0.030) / 2 - 0.004
    for k, x in enumerate((-(A - 0.024) / 4 - 0.0075, (A - 0.024) / 4 + 0.0075)):
        tapa = L.caja(f'tapa {k + 1}', tw, F - 0.024 - 0.080 - 0.006, 0.015, (x, -0.040, Z_CASCO1 + CORNISA_H - 0.015), r=0.002, segs=3, mat=inox_p)
        L.caja(f'tapa {k + 1} borde', tw, 0.002, 0.012, (x, -0.040 - (F - 0.024 - 0.080 - 0.006) / 2 + 0.001, Z_CASCO1 + CORNISA_H - 0.027), r=0.0006, segs=2, mat=inox_p)

    # --- frontal: mandos, rejilla, abrebotellas, tapon
    ruta = os.path.join(L.CALCAS_DIR, 'A5_mandos.png')
    calca_mandos(ruta)
    L.sustraer(L.bpy.data.objects['casco'], L.caja('mandos rebaje', 0.110, 0.030, 0.045, (-A / 2 + 0.060 + 0.055, Y_CASCO - 0.005, 0.330)))
    L.caja('mandos fondo', 0.108, 0.002, 0.043, (-A / 2 + 0.115, Y_CASCO + 0.009, 0.331), mat=plast, suave=False)
    L.calca('A5 mandos', ruta, 0.100, 0.040, (-A / 2 + 0.115, Y_CASCO + 0.0077, 0.3525), normal='-Y', emision=1.2)
    P.boton('interruptor verde', (-A / 2 + 0.150, Y_CASCO + 0.008, 0.3525), d=0.014, alto=0.005,
            mat=L.mat_led('LED verde tecla', (0.2, 1.0, 0.3), 2.0))
    for c in range(8):
        P.rejilla_ranuras(f'rejilla col {c + 1}', (-A / 2 + 0.062 + c * 0.014, Y_CASCO, 0.095 + (0.006 if c % 2 else 0.0)), 0.010, 0.070,
                          normal='-Y', paso=0.012, ranura=0.004, orient='H', mat=inox, cuerpo=L.bpy.data.objects['casco'])
    # abrebotellas con caja recogechapas
    xa, za = A / 2 - 0.100, Z_CASCO1 - 0.020          # eje del abrebotellas y su cara superior (20 bajo la cornisa)
    ab = L.caja('abrebotellas', 0.080, 0.030, 0.120, (xa, Y_CASCO - 0.015, za - 0.120), r=0.003, segs=3, mat=inox)
    L.sustraer(ab, L.caja('abrebotellas garra', 0.034, 0.026, 0.025, (xa, Y_CASCO - 0.023, za - 0.040)))
    L.cilindro('abrebotellas tornillo', 0.004, 0.001, (xa, Y_CASCO - 0.031, za - 0.010), eje='Y', segs=16, mat=inox_p)
    L.caja('recogechapas', 0.090, 0.060, 0.090, (xa, Y_CASCO - 0.030, za - 0.120 - 0.090), r=0.003, segs=3, mat=inox)
    L.cilindro('tapon desague', 0.0075, 0.003, (A / 2 - 0.045, Y_CASCO - 0.003, 0.040), eje='Y', segs=24, r=0.001, mat=plast)

    P.cable('cable', (-0.35, Y_TRAS, 0.20), largo=0.30, d=0.009)
    return dict(ignorar=('cable', 'abrebotellas', 'recogechapas', 'interruptor', 'tapon'))
