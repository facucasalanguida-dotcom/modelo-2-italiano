# -*- coding: utf-8 -*-
"""
A7 · Armario expositor refrigerado de bebidas Gasfrit, 1 puerta, 400 L,
540 x 580 x 1920 (foto acotada del fabricante).

Referencia: 9 fotos de gasfrit.com. Cuerpo de acero galvanizado lacado en
NEGRO satinado; puerta de doble cristal (480 x 1430, de 250 a 1680 del
suelo) con marco de aluminio y cenefa negra serigrafiada, banda negra opaca
superior de 70 que oculta el ventilador, montante derecho redondeado
(bisagra), cerradura en el canto izquierdo y asa integrada en el montante
izquierdo; la puerta sobresale 15 del frente. Sin cabecera luminosa: dos
tiras LED verticales interiores (azul / blanco / amarillo; aqui blanco).
Interior de PVC negro con pared del fondo ranurada, cremalleras, rejilla
redonda del ventilador en el techo y 5 parrillas de varilla gris claro con
tope frontal. Zocalo negro de 190 con rejilla de ranuras cortas a la
izquierda y etiqueta de mandos (degradado azul-morado-rojo, interruptor
verde, termostato de digitos rojos, interruptor rojo) a la derecha; cuatro
ruedas negras con freno.

Confirmado: medidas, colores, 5 estantes, mandos, ruedas. Supuesto: cotas
del marco y del asa integrada (por proporcion), trasera con compresor.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 0.540, 0.580, 1.920
PUERTA_SAL = 0.015
Y_FRENTE = -F / 2 + PUERTA_SAL          # frente del cuerpo
Y_TRAS = F / 2
Y_PUERTA = -F / 2                       # cara exterior del cristal
H_RUEDA = 0.065
Z_PUERTA0, Z_PUERTA1 = 0.250, 1.680
PUERTA_W, PUERTA_E = 0.480, 0.030
MARCO = 0.025
BANDA = 0.070
INT_W, INT_D, INT_H = 0.460, 0.470, 1.400
Z_INT0 = 0.270


def _f(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_mandos(ruta):
    """Etiqueta de mandos 180 x 45 mm (4 px/mm): degradado azul -> morado ->
    rojo, ventana negra del termostato con digitos rojos, logo Gasfrit."""
    W, Hh = 720, 180
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    for x in range(W):
        t = x / (W - 1)
        if t < 0.5:
            c = (int(20 + (110 - 20) * t * 2), int(90 - 60 * t * 2), int(200 - 60 * t * 2))
        else:
            c = (int(110 + (200 - 110) * (t - 0.5) * 2), int(30 - 10 * (t - 0.5) * 2), int(140 - 120 * (t - 0.5) * 2))
        dr.line((x, 0, x, Hh), fill=(*c, 255))
    dr.rounded_rectangle((250, 45, 470, 135), radius=8, fill=(12, 12, 14, 255))
    dr.text((300, 52), '30', font=_f(64, True), fill=(255, 40, 20, 255))
    f = _f(26, True)
    dr.text((510, 60), 'Gasfrit', font=f, fill=(255, 255, 255, 255))
    dr.polygon([(490, 100), (500, 70), (512, 95), (505, 110)], fill=(255, 140, 20, 255))
    im.save(ruta)


def calca_cenefa(ruta):
    """Cenefa negra perimetral del cristal (25 mm) y banda superior opaca
    (70 mm): PNG del tamano de la puerta con el centro transparente."""
    W, Hh = int(PUERTA_W * 2000), int((Z_PUERTA1 - Z_PUERTA0) * 2000)
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    m = int(MARCO * 2000)
    dr.rectangle((0, 0, W, Hh), fill=(8, 8, 9, 255))
    dr.rectangle((m, int(BANDA * 2000), W - m, Hh - m), fill=(0, 0, 0, 0))
    im.save(ruta)


def build():
    negro = L.mat_chapa('Lacado negro satinado', (0.018, 0.018, 0.019), rug=0.42, brillo=0.2, piel=0.1)
    pvc = L.mat_plastico('PVC negro interior', (0.02, 0.02, 0.02), rug=0.55)
    alu = L.mat_aluminio()
    vidrio = L.mat_vidrio('Vidrio de puerta', tinte=(0.93, 0.97, 0.96))
    gris = L.mat_plastico('Varilla plastificada gris', (0.62, 0.63, 0.64), rug=0.35)
    plast = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    cromo = L.mat_cromo()
    led = L.mat_led('LED blanco frio', (0.80, 0.90, 1.0), 12.0)

    # --- ruedas y cuerpo
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        x, y = sx * (A / 2 - 0.045), (Y_FRENTE + 0.050) if sy < 0 else (Y_TRAS - 0.050)
        L.cilindro(f'rueda {i + 1}', 0.025, 0.020, (x - 0.010, y, 0.025), eje='X', segs=40, r=0.003, mat=plast)
        L.caja(f'rueda {i + 1} horquilla', 0.030, 0.036, 0.040, (x, y, 0.025), r=0.003, segs=3, mat=cromo)
    cuerpo = L.caja('cuerpo', A, F - PUERTA_SAL, H - H_RUEDA, (0, Y_FRENTE + (F - PUERTA_SAL) / 2, H_RUEDA), r=0.003, segs=3, mat=negro)
    # hueco interior (detras de la puerta) y pared del fondo ranurada
    L.sustraer(cuerpo, L.caja('interior', INT_W, INT_D + 0.02, INT_H, (0, Y_FRENTE + INT_D / 2 - 0.01, Z_INT0), r_vert=0.006, r=0.006, segs=3))
    y_fondo = Y_FRENTE + INT_D
    for k in range(7):
        P.rejilla_ranuras(f'fondo ranuras {k + 1}', (0, y_fondo, Z_INT0 + 0.10 + k * 0.19), 0.30, 0.030, normal='-Y', paso=0.010, ranura=0.005, orient='V', mat=pvc, cuerpo=cuerpo)
    # cremalleras en las cuatro esquinas del hueco
    for sx in (-1, 1):
        for y in (Y_FRENTE + 0.040, y_fondo - 0.040):
            L.caja(f'cremallera {sx}{y:+.2f}', 0.012, 0.012, INT_H - 0.04, (sx * (INT_W / 2 - 0.006), y, Z_INT0 + 0.02), mat=alu, suave=False)
    # rejilla redonda del ventilador en el techo interior y deflector
    L.cilindro('ventilador rejilla', 0.075, 0.003, (0.06, y_fondo - 0.120, Z_INT0 + INT_H - 0.004), segs=64,
               mat=L.mat_chapa_perforada('Rejilla ventilador', d=0.005, paso=0.009))
    # 5 parrillas con tope frontal
    for k in range(5):
        z = Z_INT0 + 0.130 + k * 0.250
        P.estante_rejilla(f'parrilla {k + 1}', (0, y_fondo - 0.015 - 0.220, z), INT_W - 0.020, 0.440, paso=0.025, d_barra=0.005, mat=gris)
        L.cilindro(f'parrilla {k + 1} tope', 0.0025, INT_W - 0.020, (-(INT_W - 0.020) / 2, y_fondo - 0.015 - 0.440, z + 0.020), eje='X', segs=12, mat=gris)
        for sx in (-1, 1):
            L.cilindro(f'parrilla {k + 1} tope pie {sx}', 0.0025, 0.020, (sx * (INT_W / 2 - 0.020), y_fondo - 0.015 - 0.440, z), segs=12, mat=gris)
    # tiras LED verticales en los montantes interiores
    for sx in (-1, 1):
        L.caja(f'led {sx}', 0.010, 0.006, INT_H - 0.06, (sx * (INT_W / 2 - 0.006), Y_FRENTE + 0.006, Z_INT0 + 0.03), mat=led, suave=False)

    # --- puerta de cristal con marco, cenefa, montantes, cerradura y bisagra
    zc = (Z_PUERTA0 + Z_PUERTA1) / 2
    ph = Z_PUERTA1 - Z_PUERTA0
    for nm, y in (('cristal exterior', Y_PUERTA + 0.004), ('cristal interior', Y_PUERTA + PUERTA_E - 0.008)):
        L.caja(nm, PUERTA_W - 2 * MARCO + 0.010, 0.004, ph - 2 * MARCO + 0.010, (0, y, Z_PUERTA0 + MARCO - 0.005), mat=vidrio, suave=False)
    ruta = os.path.join(L.CALCAS_DIR, 'A7_cenefa.png')
    calca_cenefa(ruta)
    L.calca('A7 cenefa', ruta, PUERTA_W, ph, (0, Y_PUERTA + 0.0065, zc), normal='-Y')
    # marco: montante izquierdo con asa integrada (canal), derecho redondeado (bisagra), travesanos
    izq = L.caja('montante izquierdo', 0.030, PUERTA_E, ph, (-PUERTA_W / 2 + 0.015, Y_PUERTA + PUERTA_E / 2, Z_PUERTA0), r=0.003, segs=3, mat=alu)
    L.sustraer(izq, L.caja('asa canal', 0.016, 0.014, ph - 0.10, (-PUERTA_W / 2 + 0.008, Y_PUERTA + 0.012, Z_PUERTA0 + 0.05), r=0.003))
    L.caja('montante derecho', 0.035, PUERTA_E, ph, (PUERTA_W / 2 - 0.0175, Y_PUERTA + PUERTA_E / 2, Z_PUERTA0), r_vert=0.014, r=0.003, segs=8, mat=negro)
    L.caja('travesano superior', PUERTA_W, PUERTA_E, BANDA, (0, Y_PUERTA + PUERTA_E / 2, Z_PUERTA1 - BANDA), r=0.003, segs=3, mat=negro)
    L.caja('travesano inferior', PUERTA_W, PUERTA_E, MARCO, (0, Y_PUERTA + PUERTA_E / 2, Z_PUERTA0), r=0.003, segs=3, mat=alu)
    L.cilindro('cerradura', 0.007, 0.003, (-PUERTA_W / 2 + 0.015, Y_PUERTA - 0.003 + 0.0, 0.900), eje='Y', segs=32, r=0.001, mat=cromo)
    L.caja('bisagra superior', 0.040, 0.040, 0.010, (PUERTA_W / 2 - 0.020, Y_PUERTA + 0.020, Z_PUERTA1), r=0.003, segs=2, mat=cromo)

    # --- zocalo: rejilla de ranuras cortas a la izquierda, etiqueta de mandos e interruptores a la derecha
    zz = H_RUEDA + 0.095
    for col in range(8):
        P.rejilla_ranuras(f'zocalo rejilla col {col + 1}', (-A / 2 + 0.060 + col * 0.027, Y_FRENTE, zz), 0.022, 0.110, normal='-Y',
                          paso=0.018, ranura=0.006, orient='H', mat=negro, cuerpo=cuerpo)
    ruta = os.path.join(L.CALCAS_DIR, 'A7_mandos.png')
    calca_mandos(ruta)
    L.calca('A7 mandos', ruta, 0.180, 0.045, (A / 2 - 0.150, Y_FRENTE - 0.0003, zz), normal='-Y', emision=0.8)
    L.caja('interruptor verde', 0.020, 0.005, 0.012, (A / 2 - 0.215, Y_FRENTE - 0.005, zz - 0.006), r=0.001, segs=2,
           mat=L.mat_led('LED verde tecla', (0.2, 1.0, 0.3), 2.0))
    L.caja('interruptor rojo', 0.020, 0.005, 0.012, (A / 2 - 0.085, Y_FRENTE - 0.005, zz - 0.006), r=0.001, segs=2,
           mat=L.mat_plastico('Plastico rojo', (0.7, 0.05, 0.03)))
    L.cilindro('taladro evacuacion', 0.005, 0.002, (A / 2 - 0.040, Y_FRENTE - 0.001, zz), eje='Y', segs=24, mat=pvc)

    P.cable('cable', (0.10, Y_TRAS, 0.20), largo=0.30, d=0.009)
    return dict(ignorar=('cable', 'interruptor', 'cerradura'))
