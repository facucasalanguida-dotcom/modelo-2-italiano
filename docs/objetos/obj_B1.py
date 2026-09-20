# -*- coding: utf-8 -*-
"""
B1 · Lavavasos Elettrobar FAST 40 (cesta 40 x 40), 440 x 540 x 670.

Referencia: foto oficial en alta resolucion (hosteleria10 / Eurofred) y
fotos de la misma carroceria (Fast 30). Carroceria entera de inox AISI 304
satinado con cantos verticales redondeados: franja de mandos superior de 52
serigrafiada en AZUL degradado con marco blanco fino (logo "fast" blanco, boton ON/OFF blanco con
icono de encendido, boton central mayor con aro azul claro y silueta de pez,
boton START con aro rosa y display rojo de dos digitos con dos LED); liston
inox fino con dos tornillos y cierre central bajo la franja; puerta abatible
de doble pared 400 x 345, lisa, a ras del frente, enmarcada por una ranura
de 2 mm; bajo la puerta el panel fijo lleva el tirador en arco ("sonrisa",
R 276) que va del centro al canto derecho; en los laterales dos recuadros
embutidos de 3 mm (doble pared parcial) con barra intermedia y una costura
a 165 del suelo; cuatro pies negros bajos retranqueados.

Confirmado: medidas (436 x 535 x 670 Eurofred; 0,44 x 0,54 x 0,67 Makro),
panel azul, botones, display, puerta lisa con arco, recuadros laterales.
Alturas medidas sobre la foto oficial (puerta 255-600, franja 617-669).
Supuesto: trasera (toma de agua, desague y cable, no fotografiada), radio
de cantos 8.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 0.440, 0.540, 0.670
F_CUERPO = F - 0.004                  # el liston y los botones asoman 4 mm por delante
H_PIE = 0.012
Y_TRAS = F / 2
Y_FRENTE = Y_TRAS - F_CUERPO          # cara del frente: -0,266
Z_BANDA0, BANDA_H = 0.617, 0.052      # franja de mandos azul (foto: 52 de alto)
Z_LISTON0, LISTON_H = 0.610, 0.006    # liston inox bajo la franja
PUERTA_W, PUERTA_H = 0.400, 0.345
Z_PUERTA0 = 0.255
X_BOT = {'onoff': -0.090, 'programa': -0.027, 'start': 0.030}
X_DISPLAY = 0.105
Z_BOT = Z_BANDA0 + BANDA_H / 2


def _f(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_banda(ruta):
    """Serigrafia de la franja azul (432 x 83 mm a 4 px/mm): degradado
    cian -> azul, logo 'fast', icono de encendido, pez azul claro, START,
    marco del display y dos iconos de LED."""
    W, Hh = int((A - 0.008) * 4000), int((BANDA_H - 0.002) * 4000)
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 255))
    dr = ImageDraw.Draw(im)
    arriba, abajo = (105, 200, 240), (20, 105, 200)
    for y in range(Hh):
        t = y / (Hh - 1)
        c = tuple(int(arriba[i] * (1 - t) + abajo[i] * t) for i in range(3)) + (255,)
        dr.line((0, y, W, y), fill=c)
    blanco = (255, 255, 255, 255)

    def px(x, z):
        return (W / 2 + x * 4000, Hh - (z - Z_BANDA0 - 0.001) * 4000)

    # marco blanco fino interior de la franja
    dr.rounded_rectangle((10, 10, W - 11, Hh - 11), radius=14, outline=blanco, width=3)
    # logo "fast" en minusculas, ligero, a la izquierda y centrado en la franja
    f = _f(44)
    bb = dr.textbbox((0, 0), 'fast', font=f)
    x0, y0 = px(-0.176, Z_BOT)
    dr.text((x0 - bb[0], y0 - (bb[3] - bb[1]) / 2 - bb[1]), 'fast', font=f, fill=blanco)
    # icono de encendido bajo el boton ON/OFF, junto al borde inferior
    cx, cy = px(X_BOT['onoff'], Z_BANDA0 + 0.006)
    dr.arc((cx - 9, cy - 9, cx + 9, cy + 9), 300, 240, fill=blanco, width=3)
    dr.line((cx, cy - 12, cx, cy - 2), fill=blanco, width=3)
    # gota azul claro con la punta arriba alrededor del boton central, con dos "ojos"
    cx, cy = px(X_BOT['programa'], Z_BOT)
    claro = (150, 215, 245, 255)
    dr.ellipse((cx - 64, cy - 62, cx + 64, cy + 86), fill=claro)
    dr.polygon(((cx - 40, cy - 40), (cx + 40, cy - 40), (cx, cy - 94)), fill=claro)
    for ex in (-16, 16):
        dr.ellipse((cx + ex - 6, cy - 66, cx + ex + 6, cy - 54), fill=blanco)
    # START bajo el tercer boton
    cx, cy = px(X_BOT['start'], Z_BANDA0 + 0.006)
    bb = dr.textbbox((0, 0), 'START', font=_f(18, True))
    dr.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), 'START', font=_f(18, True), fill=blanco)
    # marco negro del display y dos iconos de LED (lavado / aclarado)
    cx, cy = px(X_DISPLAY, Z_BOT)
    dr.rounded_rectangle((cx - 50, cy - 30, cx + 50, cy + 30), radius=6, fill=(12, 12, 14, 255))
    for k, dz in enumerate((0.005, -0.005)):
        lx, ly = px(X_DISPLAY - 0.022, Z_BOT + dz)
        dr.ellipse((lx - 5, ly - 5, lx + 5, ly + 5), fill=blanco if k else (255, 90, 40, 255))
        dr.line((lx + 8, ly, lx + 18, ly), fill=blanco, width=3)
    im.save(ruta)


def calca_display(ruta):
    im = Image.new('RGBA', (140, 72), (12, 12, 14, 255))
    dr = ImageDraw.Draw(im)
    dr.text((28, 4), '65', font=_f(60, True), fill=(255, 45, 25, 255))
    im.save(ruta)


def build():
    inox = L.mat_inox()
    inox_p = L.mat_inox_pulido()
    plast = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    blanco = L.mat_plastico('Plastico blanco', (0.85, 0.85, 0.83), rug=0.30, brillo=0.3)
    azul_c = L.mat_plastico('Plastico azul claro', (0.35, 0.72, 0.95), rug=0.30, brillo=0.3)
    rosa = L.mat_plastico('Plastico rosa', (0.90, 0.40, 0.70), rug=0.30, brillo=0.3)
    cromo = L.mat_cromo()

    # --- pies regulables y cuerpo con cantos verticales redondeados
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        L.cilindro(f'pie {i + 1}', 0.013, 0.010, (sx * (A / 2 - 0.040), sy * (F_CUERPO / 2 - 0.040) + 0.002, 0), r=0.003, segs=32, mat=plast)
        L.cilindro(f'pie {i + 1} rosca', 0.006, 0.004, (sx * (A / 2 - 0.040), sy * (F_CUERPO / 2 - 0.040) + 0.002, 0.010), segs=24, mat=inox_p)
    cuerpo = L.caja('cuerpo', A, F_CUERPO, H - H_PIE, (0, Y_TRAS - F_CUERPO / 2, H_PIE), r=0.003, r_vert=0.008, segs=4, mat=inox)
    # costura de la tapa (a 15 del borde superior) y del cabezal (bajo el liston)
    for nm, z in (('costura cabezal', Z_LISTON0),):
        L.sustraer(cuerpo, L.caja(nm, A + 0.01, F_CUERPO + 0.01, 0.0008, (0, Y_TRAS - F_CUERPO / 2, z - 0.0004)))
        L.caja(nm + ' fondo', A - 0.0016, F_CUERPO - 0.0016, 0.0012, (0, Y_TRAS - F_CUERPO / 2, z - 0.0006), r_vert=0.007, mat=inox, suave=False)
    # recuadro embutido en los laterales (3 mm, marco de 30) y costura a 100 del suelo
    for nm, sx in (('derecho', 1), ('izquierdo', -1)):
        x = sx * A / 2
        L.sustraer(cuerpo, L.caja(f'embutido {nm} superior', 0.006, F_CUERPO - 0.040, 0.219, (x, Y_TRAS - F_CUERPO / 2, 0.366), r_vert=0.004))
        L.sustraer(cuerpo, L.caja(f'embutido {nm} inferior', 0.006, F_CUERPO - 0.040, 0.108, (x, Y_TRAS - F_CUERPO / 2, 0.227), r_vert=0.004))
        L.sustraer(cuerpo, L.caja(f'costura baja {nm}', 0.002, F_CUERPO + 0.01, 0.0008, (x, Y_TRAS - F_CUERPO / 2, 0.165)))

    # --- franja de mandos: rebaje de 1,5 mm con la calca azul, botones y display
    ruta = os.path.join(L.CALCAS_DIR, 'B1_banda.png')
    calca_banda(ruta)
    L.sustraer(cuerpo, L.caja('banda rebaje', A - 0.008, 0.010, BANDA_H - 0.002, (0, Y_FRENTE - 0.0035, Z_BANDA0 + 0.001)))  # de -8,5 a +1,5
    yb = Y_FRENTE + 0.0015
    L.calca('B1 banda', ruta, A - 0.008 - 0.002, BANDA_H - 0.004, (0, yb - 0.0003, Z_BANDA0 + BANDA_H / 2), normal='-Y')
    for nm, d, aro in (('onoff', 0.019, cromo), ('programa', 0.019, azul_c), ('start', 0.019, rosa)):
        x = X_BOT[nm]
        r_ext = 0.016 if nm == 'start' else d / 2 + 0.0025
        L.tubo(f'boton {nm} aro', r_ext, d / 2 - 0.0003, 0.0035 if nm != 'start' else 0.0015, (x, yb - (0.0035 if nm != 'start' else 0.0015), Z_BOT), eje='Y', segs=48, mat=aro)
        P.boton(f'boton {nm}', (x, yb, Z_BOT), d=d - 0.001, alto=0.0055, mat=blanco)
    rutad = os.path.join(L.CALCAS_DIR, 'B1_display.png')
    calca_display(rutad)
    L.calca('B1 display', rutad, 0.022, 0.0126, (X_DISPLAY, yb - 0.0006, Z_BOT), normal='-Y', emision=2.0)

    # --- liston inox con dos tornillos bajo la franja
    L.caja('liston', A - 0.006, 0.004, LISTON_H, (0, Y_FRENTE - 0.002, Z_LISTON0), r=0.0012, segs=2, mat=inox)
    L.sustraer(cuerpo, L.caja('liston hueco', A - 0.008, 0.006, 0.002, (0, Y_FRENTE, Z_LISTON0 + LISTON_H)))
    L.caja('cierre', 0.010, 0.004, 0.005, (0, Y_FRENTE - 0.002, Z_LISTON0 - 0.005), r=0.0008, segs=2, mat=L.mat_plastico('Plastico gris', (0.30, 0.30, 0.31)))
    for k, x in enumerate((-0.190, 0.190)):
        L.cilindro(f'liston tornillo {k + 1}', 0.003, 0.0012, (x, Y_FRENTE - 0.0048, Z_LISTON0 + LISTON_H / 2), eje='Y', segs=24, r=0.0004, mat=inox_p)

    # --- puerta abatible lisa, a ras, en un bolsillo con ranura de 2 mm
    L.sustraer(cuerpo, L.caja('puerta bolsillo', PUERTA_W + 0.004, 0.026, PUERTA_H + 0.004, (0, Y_FRENTE + 0.007, Z_PUERTA0 - 0.002)))  # de -6 a +20
    L.caja('puerta bolsillo fondo', PUERTA_W + 0.003, 0.0013, PUERTA_H + 0.003, (0, Y_FRENTE + 0.0185, Z_PUERTA0 - 0.0015), mat=plast, suave=False)
    L.caja('puerta', PUERTA_W, 0.016, PUERTA_H, (0, Y_FRENTE + 0.0085, Z_PUERTA0), r=0.002, segs=3, mat=inox)
    L.caja('puerta junta', PUERTA_W - 0.006, 0.002, PUERTA_H - 0.006, (0, Y_FRENTE + 0.0175, Z_PUERTA0 + 0.003), mat=L.mat_goma(), suave=False)
    # tirador embutido en arco ("sonrisa") en el panel fijo, bajo la puerta
    son = L.cilindro('sonrisa', 0.276, 0.0015, (0.108, Y_FRENTE - 0.0005, Z_PUERTA0 + 0.254), eje='Y', segs=256, r=0.0006)
    L.sustraer(son, L.caja('sonrisa clip', 0.7, 0.02, 0.7, (0.108, Y_FRENTE, Z_PUERTA0 - 0.0005)))
    L.sustraer(cuerpo, son)

    # --- trasera (supuesta): toma de agua 3/4", desague y cable
    L.cilindro('toma agua', 0.013, 0.018, (-0.12, Y_TRAS - 0.001, 0.14), eje='Y', segs=32, r=0.002, mat=cromo)
    L.cilindro('desague', 0.014, 0.020, (0.05, Y_TRAS - 0.001, 0.09), eje='Y', segs=32, r=0.002, mat=plast)
    P.cable('cable', (0.15, Y_TRAS, 0.12), largo=0.28, d=0.009)
    return dict(ignorar=('boton', 'liston tornillo', 'cierre', 'toma agua', 'desague', 'cable'))
