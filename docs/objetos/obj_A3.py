# -*- coding: utf-8 -*-
"""
A3 · Maquina de helado y crema fria Bras B-Cream HD 1 (B-CREAM1HD), 1 cuba
de 6 L, 200 x 490 x 620.

Referencia: fotos oficiales (hosteleria10, Bertoni). Cuerpo de acero lacado
blanco con cantos redondeados; paneles laterales y trasero marron chocolate
de lamas horizontales (persiana del condensador) con tira plateada "made in
Italy"; capota blanca en arco (L invertida de esquina muy redondeada) que
cubre la cuba, con placa marron "BRAS" en su frente; cuba cilindrica
horizontal transparente de doble pared con cupula frontal, anillos blancos
y grifo con palanca blanca; panel de control con LCD y cinco botones
redondos; logo BRAS dorado; bandeja de goteo blanca extraible con rejilla
y punto rojo; cuatro pies negros.

Confirmado: medidas, materiales, disposicion. Supuesto: color marron de
los paneles (la version antigua era gris), radios y diametro de la cuba
(por proporcion de foto).
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 0.200, 0.490, 0.620
Y_TRAS = F / 2                       # +0,245
Y_FRENTE = Y_TRAS - 0.400            # frente del cuerpo: -0,155
H_PIE = 0.020
Z_CUERPO = 0.350                     # techo del cuerpo (asiento de la cuba)
R_CUBA = 0.088
Y_CUBA0, Y_CUBA1 = -0.100, 0.120     # cilindro de la cuba
Z_CUBA = Z_CUERPO + R_CUBA + 0.004


def _f(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_bras(ruta, oro=True):
    W, Hh = 400, 140
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    if oro:
        dr.rounded_rectangle((2, 2, W - 2, Hh - 2), radius=24, fill=(78, 62, 54, 255))
    f = _f(84, True)
    bb = dr.textbbox((0, 0), 'BRAS', font=f)
    dr.text(((W - (bb[2] - bb[0])) / 2 - bb[0], (Hh - (bb[3] - bb[1])) / 2 - bb[1] - 8), 'BRAS', font=f, fill=(205, 175, 110, 255))
    f2 = _f(18)
    bb = dr.textbbox((0, 0), 'made in Italy', font=f2)
    dr.text(((W - (bb[2] - bb[0])) / 2 - bb[0], Hh - 34), 'made in Italy', font=f2, fill=(205, 175, 110, 255))
    im.save(ruta)


def calca_panel(ruta):
    """Panel de control (200 x 90 mm a 4 px/mm): LCD gris verdoso con
    temperatura y barra, boton de encendido, y textos bajo los botones."""
    W, Hh = 800, 360
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((250, 40, 560, 150), radius=8, fill=(150, 165, 140, 255), outline=(60, 60, 60, 255), width=3)
    dr.text((275, 60), '-12.3°C', font=_f(52, True), fill=(30, 40, 30, 255))
    for i in range(10):
        dr.rectangle((275 + i * 27, 122, 295 + i * 27, 138), fill=(30, 40, 30, 255) if i < 6 else (120, 135, 110, 255))
    gris = (110, 110, 112, 255)
    f = _f(16)
    for t, x in (('alarm reset', 200), ('cleaning', 330), ('', 400), ('-', 470), ('+', 580)):
        if t:
            bb = dr.textbbox((0, 0), t, font=f)
            dr.text((x - (bb[2] - bb[0]) / 2 - bb[0], 300), t, font=f, fill=gris)
    dr.rectangle((395, 215, 425, 275), fill=(15, 15, 15, 255))
    im.save(ruta)


def build():
    blanco = L.mat_chapa('Lacado blanco', (0.86, 0.86, 0.84), rug=0.30, brillo=0.5, piel=0.08)
    marron = L.mat_chapa('Lacado marron chocolate', (0.16, 0.10, 0.075), rug=0.42, brillo=0.2)
    trans = L.mat_policarbonato('Copoliester', tinte=(0.95, 0.97, 0.985))
    bl_pl = L.mat_plastico('Plastico blanco', (0.85, 0.85, 0.82), rug=0.35)
    negro = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    plata = L.mat_cromo()

    # --- pies y cuerpo lacado blanco
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        L.cilindro(f'pie {i + 1}', 0.015, H_PIE, (sx * (A / 2 - 0.030), (Y_FRENTE + 0.035) if sy < 0 else (Y_TRAS - 0.035), 0),
                   r=0.003, segs=32, mat=negro)
    cuerpo = L.caja('cuerpo', A, Y_TRAS - Y_FRENTE, Z_CUERPO - H_PIE, (0, (Y_FRENTE + Y_TRAS) / 2, H_PIE), r_vert=0.015, r=0.006, segs=6, mat=blanco)
    # paneles laterales marrones con lamas (persiana), tira plateada y tornillos
    for sx, nm in ((-1, 'izquierdo'), (1, 'derecho')):
        normal = '-X' if sx < 0 else '+X'
        marco = L.caja(f'panel {nm} marco', 0.003, 0.330, 0.250, (sx * (A / 2 - 0.0015), 0.045, H_PIE + 0.045), mat=marron, suave=False)
        P.rejilla_ranuras(f'panel {nm} lamas', (sx * A / 2, 0.045, H_PIE + 0.045 + 0.125), 0.300, 0.220, normal=normal,
                          paso=0.010, ranura=0.005, orient='H', mat=marron, fondo=0.003, cuerpo=(cuerpo, marco))
        L.caja(f'panel {nm} tira', 0.001, 0.060, 0.006, (sx * (A / 2 - 0.0005), 0.045, H_PIE + 0.090), mat=plata, suave=False)
        for k, (yy, zz) in enumerate(((-0.105, H_PIE + 0.055), (0.195, H_PIE + 0.055), (-0.105, H_PIE + 0.285), (0.195, H_PIE + 0.285))):
            L.cilindro(f'panel {nm} tornillo {k + 1}', 0.004, 0.001, (sx * (A / 2), yy, zz), eje='X', segs=16, mat=plata)
    P.rejilla_ranuras('panel trasero', (0, Y_TRAS, H_PIE + 0.100), 0.160, 0.140, normal='+Y', paso=0.010, ranura=0.005, orient='H',
                      mat=marron, fondo=0.003, cuerpo=cuerpo)

    # --- capota en arco: pilar trasero + techo sobre la cuba (L de esquina redondeada)
    pts = [(0.115, Z_CUERPO - 0.001), (Y_TRAS, Z_CUERPO - 0.001), (Y_TRAS, H - 0.130)]
    for i in range(1, 9):
        t = math.radians(90 * i / 8)
        pts.append((Y_TRAS - 0.130 + 0.130 * math.cos(t), H - 0.130 + 0.130 * math.sin(t)))
    pts += [(-0.020, H), (-0.062, H - 0.040), (-0.062, H - 0.062), (0.115, H - 0.062)]
    L.prisma_yz('capota', pts, -A / 2, A / 2, mat=blanco, r=0.004)
    ruta = os.path.join(L.CALCAS_DIR, 'A3_bras.png')
    calca_bras(ruta)
    placa = L.calca('A3 placa BRAS', ruta, 0.100, 0.035, (0, -0.041 - 0.0004, H - 0.020), normal='-Y')
    L.girar_malla(placa, (0, -0.041, H - 0.020), 'X', 46)

    # --- cuba: cilindro horizontal transparente, cupula frontal, anillos, tapa trasera, grifo
    L.cilindro('cuba', R_CUBA, Y_CUBA1 - Y_CUBA0, (0, Y_CUBA0, Z_CUBA), eje='Y', segs=96, mat=trans)
    cup = [(0.0, 0.0)]
    for i in range(1, 13):
        t = math.radians(90 * i / 12)
        cup.append((R_CUBA * math.sin(t), -R_CUBA * (1 - math.cos(t)) * 0.75 + 0.0))
    # cupula: casquete de revolucion sobre el eje Y (se construye sobre Z y se gira)
    perfil = [(R_CUBA * math.sin(math.radians(90 * i / 12)), 0.066 * math.cos(math.radians(90 * i / 12))) for i in range(12, -1, -1)]
    cupula = L.perfil_revolucion('cupula', perfil, (0, 0, 0), segs=96, mat=trans, cerrar=False)
    L.girar_malla(cupula, (0, 0, 0), 'X', 90)
    for v in cupula.data.vertices:
        v.co.y += Y_CUBA0
        v.co.z += Z_CUBA
    L.toro('aro cupula', R_CUBA + 0.002, 0.006, (0, Y_CUBA0, Z_CUBA), segs=96, segs_r=16, mat=bl_pl)
    L.girar_malla(L.bpy.data.objects['aro cupula'], (0, Y_CUBA0, Z_CUBA), 'X', 90)
    for k, y in enumerate((-0.045, 0.010, 0.065)):
        an = L.toro(f'anillo {k + 1}', R_CUBA - 0.010, 0.008, (0, y, Z_CUBA), segs=64, segs_r=12, mat=bl_pl)
        L.girar_malla(an, (0, y, Z_CUBA), 'X', 90)
    L.cilindro('eje agitador', 0.006, Y_CUBA1 - Y_CUBA0 - 0.02, (0, Y_CUBA0 + 0.01, Z_CUBA), eje='Y', segs=24, mat=L.mat_inox_pulido())
    L.cilindro('tapa trasera cuba', 0.030, 0.010, (0, 0.060, Z_CUBA + R_CUBA - 0.002), segs=48, r=0.002, mat=bl_pl)
    L.cilindro('pomo tapa', 0.008, 0.010, (0, 0.060, Z_CUBA + R_CUBA + 0.008), segs=24, r=0.002, mat=bl_pl)
    # grifo: cuerpo bajo la cupula, palanca vertical blanca a la izquierda
    L.cilindro('grifo cuerpo', 0.014, 0.030, (0, Y_CUBA0 - 0.040, Z_CUBA - R_CUBA + 0.010), segs=32, r=0.003, mat=trans)
    L.cilindro('grifo boca', 0.008, 0.012, (0, Y_CUBA0 - 0.040, Z_CUBA - R_CUBA - 0.002), segs=24, mat=trans)
    pal = L.caja('grifo palanca', 0.018, 0.008, 0.090, (-0.030, Y_CUBA0 - 0.058, Z_CUBA - 0.070), r=0.004, segs=4, mat=bl_pl)
    L.girar_malla(pal, (-0.030, Y_CUBA0 - 0.058, Z_CUBA - 0.070), 'X', -12)
    # asiento blanco de la cuba sobre el cuerpo
    L.caja('asiento cuba', 0.190, 0.240, 0.012, (0, 0.010, Z_CUERPO - 0.001), r=0.004, segs=3, mat=blanco)

    # --- frontal: panel de control, botones, logo dorado
    ruta = os.path.join(L.CALCAS_DIR, 'A3_panel.png')
    calca_panel(ruta)
    L.calca('A3 panel', ruta, 0.200, 0.090, (0, Y_FRENTE - 0.0003, 0.255), normal='-Y', emision=0.4)
    P.boton('boton encendido', (0.070, Y_FRENTE, 0.275), d=0.012, alto=0.003, mat=L.mat_plastico('Plastico rojo', (0.7, 0.05, 0.03)))
    for nm, x in (('boton alarma', -0.050), ('boton limpieza', -0.017), ('boton menos', 0.017), ('boton mas', 0.045)):
        P.boton(nm, (x, Y_FRENTE, 0.240), d=0.012, alto=0.003, mat=L.mat_plastico('Plastico gris', (0.30, 0.30, 0.30)))
    ruta2 = os.path.join(L.CALCAS_DIR, 'A3_logo.png')
    calca_bras(ruta2, oro=False)
    L.calca('A3 logo', ruta2, 0.040, 0.014, (-0.045, Y_FRENTE - 0.0003, 0.100), normal='-Y')

    # --- bandeja de goteo blanca con rejilla y punto rojo
    band = L.caja('bandeja', A, 0.090, 0.045, (0, Y_FRENTE - 0.045, H_PIE + 0.010), r_vert=0.025, r=0.006, segs=6, mat=bl_pl)
    rej = L.caja('bandeja rejilla', A - 0.024, 0.066, 0.003, (0, Y_FRENTE - 0.045, H_PIE + 0.055), r=0.001, segs=2, mat=bl_pl)
    for i in range(9):
        L.sustraer(rej, L.caja(f'rejilla ranura {i + 1}', 0.004, 0.050, 0.02, (-0.070 + i * 0.0175, Y_FRENTE - 0.045, H_PIE + 0.045)))
    P.piloto('punto rojo', (0, Y_FRENTE - 0.012, H_PIE + 0.058), d=0.006, color=(1.0, 0.05, 0.02), normal='+Y', fuerza=0.5)
    L.girar_malla(L.bpy.data.objects['punto rojo'], (0, Y_FRENTE - 0.012, H_PIE + 0.058), 'X', 90)

    P.cable('cable', (0.05, Y_TRAS, 0.06), largo=0.25, d=0.008)
    return dict(ignorar=('cable', 'boton', 'pomo tapa'))
