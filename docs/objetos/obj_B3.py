# -*- coding: utf-8 -*-
"""
B3 · Tablet de TPV sobre soporte giratorio de sobremesa, huella 250 x 200,
alto 250. No es de Makro: diseno propio tipo Square Stand: base blanca
brillante de esquinas muy redondeadas 250 x 200 x 12 sobre disco giratorio
gris con goma, columna trasera blanca de 100 x 30 x 140 con perfil en L
redondeado, bisagra O 20, marco negro mate de 245 x 185 x 14 con oreja de
lector (simbolo NFC y ranura de chip) inclinado 60 grados, tablet de 10,2"
con pantalla emisiva de TPV (cuadricula de productos + ticket) y cable
USB-C negro por detras. Origen: centro de la huella, pantalla hacia -Y.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 0.250, 0.200, 0.250
Y_FRENTE, Y_TRAS = -F / 2, F / 2
E_BASE = 0.012
COL_E, COL_W = 0.030, 0.100
Y_COL = 0.015                        # centro de la columna en Y
MARCO_W, MARCO_H, MARCO_E = 0.245, 0.185, 0.014
INCL = 60.0                          # inclinacion de la pantalla sobre la horizontal
H_BIS = 0.065                        # altura de la bisagra sobre el borde inferior del marco


def _f(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_pantalla(ruta):
    """Interfaz de TPV: cuadricula de productos a la izquierda y ticket a la derecha. 215 x 150 mm -> 1720 x 1200."""
    W, Hh = 1720, 1200
    im = Image.new('RGBA', (W, Hh), (238, 240, 243, 255))
    dr = ImageDraw.Draw(im)
    dr.rectangle((0, 0, W, 90), fill=(28, 30, 34, 255))
    dr.text((30, 22), 'Caffe & Gelato  ·  Mesa 4', font=_f(40, True), fill=(245, 245, 245, 255))
    colores = [(214, 90, 60), (72, 150, 200), (110, 170, 90), (230, 170, 50), (150, 110, 190), (60, 160, 160)]
    nombres = ['Espresso', 'Cappuccino', 'Gelato 2', 'Gelato 3', 'Tiramisu', 'Cerveza', 'Agua', 'Cornetto', 'Latte', 'Panino', 'Spritz', 'Vino']
    for i, nm in enumerate(nombres):
        cx, cy = 30 + (i % 4) * 300, 120 + (i // 4) * 330
        dr.rounded_rectangle((cx, cy, cx + 280, cy + 300), radius=18, fill=colores[i % 6] + (255,))
        dr.text((cx + 20, cy + 230), nm, font=_f(34, True), fill=(255, 255, 255, 255))
    dr.rounded_rectangle((1250, 120, 1690, 1170), radius=18, fill=(255, 255, 255, 255), outline=(200, 200, 205, 255), width=3)
    dr.text((1280, 150), 'Ticket', font=_f(38, True), fill=(40, 40, 44, 255))
    for i, (t, p) in enumerate((('2 x Espresso', '2,60'), ('1 x Cappuccino', '1,80'), ('1 x Gelato 2', '3,50'), ('1 x Tiramisu', '4,50'))):
        dr.text((1280, 230 + i * 70), t, font=_f(30), fill=(60, 60, 64, 255))
        dr.text((1560, 230 + i * 70), p, font=_f(30), fill=(60, 60, 64, 255))
    dr.line((1280, 560, 1660, 560), fill=(200, 200, 205, 255), width=3)
    dr.text((1280, 590), 'TOTAL', font=_f(40, True), fill=(40, 40, 44, 255))
    dr.text((1500, 590), '12,40 €', font=_f(40, True), fill=(40, 40, 44, 255))
    dr.rounded_rectangle((1280, 1040, 1660, 1140), radius=14, fill=(40, 160, 90, 255))
    dr.text((1400, 1068), 'Cobrar', font=_f(40, True), fill=(255, 255, 255, 255))
    im.save(ruta)


def calca_nfc(ruta):
    S = 200
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    for r in (30, 55, 80):
        dr.arc((S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r), 300, 60, fill=(235, 235, 235, 255), width=9)
    dr.ellipse((S / 2 - 12, S / 2 - 12, S / 2 + 12, S / 2 + 12), fill=(235, 235, 235, 255))
    im.save(ruta)


def build():
    blanco = L.mat_plastico('Plastico blanco brillante', (0.90, 0.90, 0.89), rug=0.15, brillo=0.6)
    negro = L.mat_plastico('Plastico negro mate', (0.02, 0.02, 0.022), rug=0.55)
    gris = L.mat_plastico('Plastico gris', (0.30, 0.30, 0.31), rug=0.5)
    goma = L.mat_goma()
    vidrio_n = L.mat_vitroceramica('Cristal pantalla', color=(0.004, 0.004, 0.005), rug=0.02)

    # --- disco giratorio, base y columna con la trasera curva (perfil en L redondeado)
    L.cilindro('disco giratorio', 0.060, 0.006, (0, 0.010, 0), segs=96, r=0.002, mat=gris)
    L.toro('disco goma', 0.052, 0.0025, (0, 0.010, 0.0025), segs=96, segs_r=10, mat=goma)
    L.caja('base', A, F, E_BASE, (0, 0, 0.006), r=0.004, r_vert=0.030, segs=6, mat=blanco)
    inc = math.radians(INCL)
    # la bisagra se situa para que la esquina alta del marco inclinado quede exactamente en H
    z_bis = H - (MARCO_H - H_BIS) * math.sin(inc) - MARCO_E * math.cos(inc) + 0.0019   # +1,9: radio de 5 de las aristas del marco
    col_h = z_bis - (E_BASE + 0.006)
    L.caja('columna', COL_W, COL_E, col_h, (0, Y_COL, E_BASE + 0.006 - 0.001), r=0.006, segs=4, mat=blanco)
    z0 = E_BASE + 0.005
    L.prisma_yz('columna curva', [(Y_COL - COL_E / 2, z0), (Y_COL + COL_E / 2 + 0.030, z0)] +
                [(Y_COL + COL_E / 2 + 0.030 - 0.030 * math.sin(math.radians(90 * i / 8)), z0 + 0.030 - 0.030 * math.cos(math.radians(90 * i / 8))) for i in range(1, 9)] +
                [(Y_COL + COL_E / 2, z0 + 0.035), (Y_COL - COL_E / 2, z0 + 0.035)],
                -COL_W / 2, COL_W / 2, mat=blanco, r=0.0, suave=True)
    L.cilindro('bisagra', 0.010, COL_W + 0.004, (-(COL_W + 0.004) / 2, Y_COL, z_bis), eje='X', segs=48, r=0.002, mat=blanco)

    # --- marco negro con la tablet y la pantalla: se construye vertical (cara trasera en yb) y se gira sobre la bisagra
    yb = Y_COL - 0.010
    zb = z_bis - H_BIS
    piezas = []
    marco = L.caja('marco', MARCO_W, MARCO_E, MARCO_H, (0, yb - MARCO_E / 2, zb), r=0.005, segs=4, mat=negro)
    L.sustraer(marco, L.caja('marco ventana', 0.216, 0.010, 0.152, (-0.010, yb - MARCO_E - 0.003, zb + 0.016), r_vert=0.004))
    piezas.append(marco)
    piezas.append(L.caja('tablet', 0.215, 0.007, 0.151, (-0.010, yb - MARCO_E + 0.004, zb + 0.0165), r=0.001, segs=2, mat=L.mat_aluminio('Aluminio tablet', rug=0.3)))
    piezas.append(L.caja('pantalla cristal', 0.214, 0.001, 0.150, (-0.010, yb - MARCO_E + 0.0005, zb + 0.017), mat=vidrio_n, suave=False))
    ruta = os.path.join(L.CALCAS_DIR, 'B3_pantalla.png')
    calca_pantalla(ruta)
    piezas.append(L.calca('B3 pantalla', ruta, 0.208, 0.145, (-0.010, yb - MARCO_E - 0.0003, zb + 0.092), normal='-Y', emision=1.4))
    rutan = os.path.join(L.CALCAS_DIR, 'B3_nfc.png')
    calca_nfc(rutan)
    piezas.append(L.calca('B3 nfc', rutan, 0.016, 0.016, (0.111, yb - MARCO_E - 0.0003, zb + 0.140), normal='-Y'))
    piezas.append(L.caja('ranura chip', 0.004, 0.003, 0.050, (0.111, yb - MARCO_E - 0.0015, zb + 0.025), mat=L.mat_plastico('Ranura oscura', (0.005, 0.005, 0.005), rug=0.9), suave=False))
    piezas.append(L.caja('pestillo', 0.006, 0.004, 0.020, (-MARCO_W / 2, yb - 0.008, zb + 0.070), r=0.001, segs=2, mat=negro))
    piezas.append(L.caja('marco trasera', MARCO_W - 0.010, 0.0015, MARCO_H - 0.010, (0, yb + 0.0005, zb + 0.005), mat=blanco, suave=False))
    for ob in piezas:
        L.girar_malla(ob, (0, yb, z_bis), 'X', -(90.0 - INCL))
    P.cable('cable', (0.0, Y_COL + COL_E / 2, E_BASE + 0.010), largo=0.15, d=0.004)
    return dict(ignorar=('cable',))
