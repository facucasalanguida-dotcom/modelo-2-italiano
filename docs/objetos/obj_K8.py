# -*- coding: utf-8 -*-
"""
K8 · Armario refrigerado Edenox APS-451 I (Fagor Professional / Onnera),
626 x 740 x 1865. K9 es la segunda unidad, identica (obj_K9 importa esto).

Referencia: plano acotado oficial de Edenox y fotos de distribuidores.
Exterior inox satinado de grano fino ("epoxi inox"); banda superior de
mandos de plastico AZUL a haces del frente (60 de fondo, la misma que la
puerta, y 13 mm mas alta que el techo inox del cuerpo) con display digital
rojo, mando pequeno, cerradura cromada y logo "edenox" en blanco; puerta
opaca lisa (600 x 1690, 60 de grueso) con bisagras a la derecha (dos
pletinas que unen cuerpo y puerta, y la placa de la bisagra inferior sobre
la cara de la puerta) y perfil-tirador vertical de aluminio en el canto
izquierdo, a toda la altura, que sobresale 48 mm (los 740 de fondo son con
el tirador; el cuerpo tiene 692); zocalo de 45 de todo el ancho,
retranqueado 8 mm respecto a la puerta, con cuatro grupos de 6 ranuras
verticales; compartimento del compresor en la parte baja trasera (246 alto
x 150 fondo) ENTRE las paredes laterales (62 mm), abierto solo por detras,
con bandeja, compresor y condensador; trasera galvanizada de 2 mm sobre el
cuerpo; cuatro pies pequenos.

Confirmado: todas las cotas (plano oficial), disposicion. Supuesto: estetica
"clasica" de la banda azul (display a la izquierda, logo a la derecha) y
bisagras a la derecha (puerta reversible).
"""
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 0.626, 0.740, 1.865
F_CUERPO = 0.692
TIR = F - F_CUERPO                     # 0,048: perfil-tirador por delante
Y_FRENTE = -F / 2 + TIR                # cara de la puerta
Y_TRAS = F / 2
H_PIE = 0.030
Z_BANDA0 = H - 0.100                   # banda de mandos 100 mm
Z_TOP_CUERPO = H - 0.013               # el cuerpo queda 13 mm bajo la banda
PUERTA_W, PUERTA_E = 0.600, 0.060
Z_ZOCALO = 0.045                       # zocalo bajo la puerta
Z_PUERTA0 = H_PIE + Z_ZOCALO
PUERTA_H = Z_BANDA0 - Z_PUERTA0        # ~1,690
D_CUERPO = F_CUERPO - PUERTA_E - 0.002  # el cuerpo acaba 2 mm antes del plano trasero (trasera galvanizada)
H_COMPRESOR, F_COMPRESOR = 0.246, 0.150  # compartimento del compresor (plano oficial)


def _f(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_banda(ruta):
    """Banda azul (626 x 100 mm a 4 px/mm): ventana negra del display con
    digitos rojos, y logo 'edenox' blanco a la derecha."""
    W, Hh = int(A * 4000), 400
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    # ventana del display
    x0 = W / 2 - 0.160 * 4000
    dr.rounded_rectangle((x0 - 110, 155, x0 + 110, 245), radius=10, fill=(12, 12, 14, 255))
    dr.text((x0 - 70, 162), '3.5', font=_f(70, True), fill=(255, 40, 20, 255))
    # logo
    t = 'edenox'
    f = _f(84, True)
    bb = dr.textbbox((0, 0), t, font=f)
    dr.text((W / 2 + 0.200 * 4000 - (bb[2] - bb[0]) / 2 - bb[0], 200 - (bb[3] - bb[1]) / 2 - bb[1]), t, font=f, fill=(250, 250, 250, 255))
    # simbolo del logo: circulo con estrella
    cx = W / 2 + 0.135 * 4000
    dr.ellipse((cx - 32, 168, cx + 32, 232), outline=(250, 250, 250, 255), width=6)
    im.save(ruta)


def build():
    inox = L.mat_inox('INOX epoxi', rug=0.36, aniso=0.6, huellas=0.05)
    inox_p = L.mat_inox_pulido()
    azul = L.mat_plastico('Plastico azul Edenox', (0.08, 0.30, 0.75), rug=0.5)
    plast = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    alu = L.mat_aluminio()
    cromo = L.mat_cromo()
    galva = L.mat_aluminio('Galvanizado', rug=0.55, color=(0.50, 0.51, 0.52))

    # --- pies y cuerpo (los delanteros bajo el zocalo, los traseros bajo las paredes laterales)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        x = sx * (A / 2 - 0.045)
        y = Y_FRENTE + 0.045 if sy < 0 else Y_TRAS - 0.045
        L.cilindro(f'pie {i + 1}', 0.016, H_PIE, (x, y, 0), r=0.003, segs=32, mat=plast)
    cuerpo = L.caja('cuerpo', A, D_CUERPO, Z_TOP_CUERPO - H_PIE, (0, Y_FRENTE + PUERTA_E + D_CUERPO / 2, H_PIE),
                    r=0.003, segs=3, mat=inox)
    # compartimento del compresor: 246 de alto x 150 de fondo, ENTRE las paredes laterales (62 mm)
    # y abierto solo por detras (los laterales llegan rectos hasta el suelo)
    L.sustraer(cuerpo, L.caja('escalon', A - 0.124, F_COMPRESOR + 0.010, H_COMPRESOR + 0.001,
                              (0, Y_TRAS - F_COMPRESOR / 2 + 0.005, H_PIE - 0.001)))
    # trasera galvanizada: ocupa los 2 mm entre el cuerpo (y 368) y el plano trasero (y 370)
    L.caja('trasera', A - 0.006, 0.002, Z_TOP_CUERPO - H_PIE - H_COMPRESOR - 0.004,
           (0, Y_TRAS - 0.001, H_PIE + H_COMPRESOR + 0.002), mat=galva, suave=False)
    # bandeja sobre la que descansan compresor y condensador
    L.caja('bandeja compresor', A - 0.130, F_COMPRESOR, 0.003, (0, Y_TRAS - F_COMPRESOR / 2, H_PIE + 0.0005), mat=galva, suave=False)
    L.cilindro('compresor', 0.072, 0.16, (0.10, Y_TRAS - F_COMPRESOR / 2, H_PIE + 0.003), segs=48, r=0.02, mat=plast)
    L.caja('condensador', 0.25, 0.02, 0.20, (-0.12, Y_TRAS - 0.03, H_PIE + 0.003),
           mat=L.mat_chapa('Condensador negro', (0.02, 0.02, 0.02), rug=0.8, brillo=0.0), suave=False)

    # --- zocalo de todo el ancho, retranqueado 8 mm respecto a la puerta, con 4 grupos de 6 ranuras verticales
    zocalo = L.caja('zocalo', A, PUERTA_E - 0.008, Z_ZOCALO, (0, Y_FRENTE + 0.008 + (PUERTA_E - 0.008) / 2, H_PIE),
                    r=0.002, segs=2, mat=inox)
    for k in range(4):
        P.rejilla_ranuras(f'rejilla zocalo {k + 1}', (-0.20 + k * 0.105, Y_FRENTE + 0.008, H_PIE + 0.0225), 0.085, 0.028,
                          normal='-Y', n=6, paso=0.014, ranura=0.005, orient='V', mat=inox, cuerpo=zocalo)

    # --- puerta lisa, perfil-tirador y bisagras
    L.caja('puerta', PUERTA_W, PUERTA_E, PUERTA_H, (0, Y_FRENTE + PUERTA_E / 2, Z_PUERTA0), r=0.003, segs=3, mat=inox)
    perfil = L.caja('tirador perfil', 0.025, TIR, PUERTA_H - 0.004, (-PUERTA_W / 2 + 0.0125, Y_FRENTE - TIR / 2, Z_PUERTA0 + 0.002),
                    r=0.003, segs=3, mat=alu)
    L.sustraer(perfil, L.caja('tirador canal', 0.016, 0.030, PUERTA_H, (-PUERTA_W / 2 + 0.0125 + 0.008, Y_FRENTE - 0.018, Z_PUERTA0), r=0.002))
    # pletinas que unen cuerpo y puerta por el canto derecho: sobresalen 4 mm del frente y entran 1 mm en el
    # cuerpo (asi su cara trasera no queda coplanaria con la trasera de la puerta)
    for i, z in enumerate((Z_PUERTA0 + 0.010, Z_BANDA0 - 0.040)):
        L.caja(f'bisagra {i + 1}', 0.030, PUERTA_E + 0.005, 0.030, (A / 2 - 0.015, Y_FRENTE - 0.004 + (PUERTA_E + 0.005) / 2, z),
               r=0.002, segs=2, mat=inox_p)
    # placa de la bisagra inferior sobre la cara de la puerta, pegada a la pletina 1 (foto K8_26)
    L.caja('bisagra inferior', 0.035, 0.006, 0.026, (A / 2 - 0.0475, Y_FRENTE - 0.003, Z_PUERTA0 + 0.012), r=0.002, segs=2, mat=inox_p)

    # --- banda de mandos azul, a haces de la puerta (60 de fondo) y 13 mm por encima del techo del cuerpo
    L.caja('banda mandos', A, PUERTA_E, 0.100, (0, Y_FRENTE + PUERTA_E / 2, Z_BANDA0), r=0.003, segs=3, mat=azul)
    ruta = os.path.join(L.CALCAS_DIR, 'K8_banda.png')
    calca_banda(ruta)
    L.calca('K8 banda', ruta, A - 0.004, 0.098, (0, Y_FRENTE - 0.0003, Z_BANDA0 + 0.050), normal='-Y', emision=0.6)
    P.mando_ruleta('mando termostato', (-0.060, Y_FRENTE, Z_BANDA0 + 0.050), d=0.020, alto=0.010, mat=azul, faldon=False, marca=True)
    L.cilindro('cerradura', 0.009, 0.004, (0.070, Y_FRENTE - 0.004, Z_BANDA0 + 0.050), eje='Y', segs=32, r=0.001, mat=cromo)
    L.caja('cerradura ranura', 0.002, 0.003, 0.010, (0.070, Y_FRENTE - 0.0045, Z_BANDA0 + 0.045), mat=plast, suave=False)

    return dict(ignorar=('mando',))
