# -*- coding: utf-8 -*-
"""
A3 · Maquina de helado y crema fria Bras B-Cream HD 1 (B-CREAM1HD), 1 cuba
de 6 L, 200 x 490 x 620.

Referencia: fotos oficiales (hosteleria10, Bertoni). Cuerpo de acero lacado
blanco con cantos redondeados; paneles laterales y trasero marron chocolate
oscuro embutidos 2 mm en el cuerpo, de lamas horizontales (persiana del
condensador) con tira plateada "made in Italy" y tornillos en relieve;
capota blanca en arco (L invertida de esquina muy redondeada) que cubre la
cuba, con placa marron "BRAS" sobre su cara inclinada; cuba cilindrica
horizontal transparente (tubo de 4 mm de pared) adelantada hasta el frente
del cuerpo, con cupula frontal, cuatro anillos blancos y grifo con palanca
blanca; panel de control con LCD pequeno y cinco botones redondos; logo
BRAS dorado; bandeja de goteo blanca extraible con rejilla y punto rojo;
cuatro pies negros.

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
Y_CUBA0, Y_CUBA1 = -0.150, 0.115     # cilindro de la cuba: del frente del cuerpo a la cara del pilar del capo
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
    """Panel de control (170 x 90 mm a 4 px/mm, centrado en x = 340 px): LCD
    gris verdoso pequeno (47 x 16 mm) con temperatura y barra, ventana negra
    del sensor y textos bajo los botones (a -50, -17,5, +17,5 y +45 mm)."""
    W, Hh = 680, 360
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((250, 50, 440, 115), radius=6, fill=(150, 165, 140, 255), outline=(60, 60, 60, 255), width=2)
    dr.text((262, 56), '-12.3°C', font=_f(36, True), fill=(30, 40, 30, 255))
    for i in range(10):
        dr.rectangle((262 + i * 17, 93, 274 + i * 17, 105), fill=(30, 40, 30, 255) if i < 6 else (120, 135, 110, 255))
    gris = (110, 110, 112, 255)
    f = _f(16)
    for t, x in (('alarm reset', 140), ('cleaning', 270), ('-', 410), ('+', 520)):
        bb = dr.textbbox((0, 0), t, font=f)
        dr.text((x - (bb[2] - bb[0]) / 2 - bb[0], 300), t, font=f, fill=gris)
    dr.rectangle((335, 215, 365, 275), fill=(15, 15, 15, 255))
    im.save(ruta)


def build():
    blanco = L.mat_chapa('Lacado blanco', (0.86, 0.86, 0.84), rug=0.30, brillo=0.5, piel=0.08)
    marron = L.mat_chapa('Lacado marron chocolate', (0.065, 0.040, 0.032), rug=0.42, brillo=0.2)
    trans = L.mat_policarbonato('Copoliester', tinte=(0.95, 0.97, 0.985))
    bl_pl = L.mat_plastico('Plastico blanco', (0.85, 0.85, 0.82), rug=0.35)
    negro = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    plata = L.mat_cromo()

    # --- pies y cuerpo lacado blanco
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        L.cilindro(f'pie {i + 1}', 0.015, H_PIE, (sx * (A / 2 - 0.030), (Y_FRENTE + 0.035) if sy < 0 else (Y_TRAS - 0.035), 0),
                   r=0.003, segs=32, mat=negro)
    cuerpo = L.caja('cuerpo', A, Y_TRAS - Y_FRENTE, Z_CUERPO - H_PIE, (0, (Y_FRENTE + Y_TRAS) / 2, H_PIE), r_vert=0.015, r=0.006, segs=6, mat=blanco)
    # paneles laterales marrones embutidos en un rebaje de 4 mm del cuerpo: marco de 3 mm (1 mm embebido en el fondo
    # del rebaje, cara 2 mm dentro del flanco), lamas a haces con el marco, tira plateada y tornillos 1 mm en relieve
    for sx, nm in ((-1, 'izquierdo'), (1, 'derecho')):
        normal = '-X' if sx < 0 else '+X'
        L.sustraer(cuerpo, L.caja(f'panel {nm} rebaje', 0.008, 0.330, 0.250, (sx * A / 2, 0.045, H_PIE + 0.045)))
        xp = sx * (A / 2 - 0.002)                                        # cara del panel
        marco = L.caja(f'panel {nm} marco', 0.003, 0.330, 0.250, (sx * (A / 2 - 0.0035), 0.045, H_PIE + 0.045), mat=marron, suave=False)
        P.rejilla_ranuras(f'panel {nm} lamas', (xp, 0.045, H_PIE + 0.045 + 0.125), 0.300, 0.220, normal=normal,
                          paso=0.010, ranura=0.005, orient='H', mat=marron, fondo=0.003, cuerpo=(cuerpo, marco))
        L.caja(f'panel {nm} tira', 0.002, 0.060, 0.006, (xp, 0.045, H_PIE + 0.090), mat=plata, suave=False)
        for k, (yy, zz) in enumerate(((-0.105, H_PIE + 0.055), (0.195, H_PIE + 0.055), (-0.105, H_PIE + 0.285), (0.195, H_PIE + 0.285))):
            # el cilindro en X crece hacia +X: a la izquierda nace 1 mm mas adentro para asomar 1 mm de la cara
            L.cilindro(f'panel {nm} tornillo {k + 1}', 0.004, 0.001, (xp - (0.001 if sx < 0 else 0), yy, zz), eje='X', segs=16, mat=plata)
    # panel trasero: marco marron en un rebaje igual (2 mm dentro de la cara trasera), lamas en su mitad baja
    L.sustraer(cuerpo, L.caja('panel trasero rebaje', 0.180, 0.008, 0.300, (0, Y_TRAS, H_PIE + 0.030)))
    marco_t = L.caja('panel trasero marco', 0.180, 0.003, 0.300, (0, Y_TRAS - 0.0035, H_PIE + 0.030), mat=marron, suave=False)
    P.rejilla_ranuras('panel trasero', (0, Y_TRAS - 0.002, H_PIE + 0.130), 0.160, 0.180, normal='+Y', paso=0.010, ranura=0.005, orient='H',
                      mat=marron, fondo=0.003, cuerpo=(cuerpo, marco_t))

    # --- capota en arco: pilar trasero + techo sobre la cuba (L de esquina redondeada)
    pts = [(0.115, Z_CUERPO - 0.001), (Y_TRAS, Z_CUERPO - 0.001), (Y_TRAS, H - 0.130)]
    for i in range(1, 9):
        t = math.radians(90 * i / 8)
        pts.append((Y_TRAS - 0.130 + 0.130 * math.cos(t), H - 0.130 + 0.130 * math.sin(t)))
    pts += [(-0.020, H), (-0.062, H - 0.040), (-0.062, H - 0.062), (0.115, H - 0.062)]
    L.prisma_yz('capota', pts, -A / 2, A / 2, mat=blanco, r=0.004)
    ruta = os.path.join(L.CALCAS_DIR, 'A3_bras.png')
    calca_bras(ruta)
    # placa BRAS sobre la cara inclinada del capo, de (-0.020, H) a (-0.062, H - 0.040): normal (0, -0,69, +0,72).
    # La calca (normal -Y) se gira sobre X unos -46 grados hasta esa normal y se separa 0,3 mm hacia fuera
    ny, nz = 0.040, 0.042
    ny, nz = -ny / math.hypot(ny, nz), nz / math.hypot(ny, nz)
    cp = (0, -0.041 + 0.0003 * ny, H - 0.020 + 0.0003 * nz)
    placa = L.calca('A3 placa BRAS', ruta, 0.100, 0.035, cp, normal='-Y')
    L.girar_malla(placa, cp, 'X', math.degrees(math.atan2(-nz, -ny)))

    # --- cuba: tubo de vidrio horizontal de 4 mm de pared, adelantado hasta el frente del cuerpo y metido 3 mm en el
    #     pilar del capo, cerrado atras por un disco fino; cupula frontal, anillos, tapa trasera, grifo
    L.tubo('cuba', R_CUBA, R_CUBA - 0.004, Y_CUBA1 - Y_CUBA0 + 0.003, (0, Y_CUBA0, Z_CUBA), eje='Y', segs=96, mat=trans)
    L.cilindro('cuba fondo', R_CUBA - 0.002, 0.005, (0, Y_CUBA1 - 0.003, Z_CUBA), eje='Y', segs=96, mat=trans)
    # cupula: casquete de revolucion de 4 mm de pared (se construye sobre Z y se gira sobre Y): perfil exterior del
    # vertice a la base y retorno interior de la base al vertice, que cierra el solido sin tapas planas
    ts = [math.radians(90 * i / 12) for i in range(13)]
    perfil = [(R_CUBA * math.sin(t), 0.066 * math.cos(t)) for t in ts]
    perfil += [((R_CUBA - 0.004) * math.sin(t), 0.062 * math.cos(t)) for t in reversed(ts)]
    cupula = L.perfil_revolucion('cupula', perfil, (0, 0, 0), segs=96, mat=trans, cerrar=True)
    L.girar_malla(cupula, (0, 0, 0), 'X', 90)
    for v in cupula.data.vertices:
        v.co.y += Y_CUBA0
        v.co.z += Z_CUBA
    L.toro('aro cupula', R_CUBA + 0.002, 0.006, (0, Y_CUBA0, Z_CUBA), segs=96, segs_r=16, mat=bl_pl)
    L.girar_malla(L.bpy.data.objects['aro cupula'], (0, Y_CUBA0, Z_CUBA), 'X', 90)
    for k, y in enumerate((-0.095, -0.040, 0.015, 0.070)):
        an = L.toro(f'anillo {k + 1}', R_CUBA - 0.010, 0.008, (0, y, Z_CUBA), segs=64, segs_r=12, mat=bl_pl)
        L.girar_malla(an, (0, y, Z_CUBA), 'X', 90)
    # eje del agitador: del vertice de la cupula (embebido en su pared) hasta 20 mm dentro del pilar del capo
    L.cilindro('eje agitador', 0.006, Y_CUBA1 - Y_CUBA0 + 0.086, (0, Y_CUBA0 - 0.066, Z_CUBA), eje='Y', segs=24, mat=L.mat_inox_pulido())
    L.cilindro('tapa trasera cuba', 0.030, 0.016, (0, 0.060, Z_CUBA + R_CUBA - 0.008), segs=48, r=0.002, mat=bl_pl)
    L.cilindro('pomo tapa', 0.008, 0.010, (0, 0.060, Z_CUBA + R_CUBA + 0.008), segs=24, r=0.002, mat=bl_pl)
    # grifo: cuerpo bajo la cupula, palanca vertical blanca a la izquierda
    L.cilindro('grifo cuerpo', 0.014, 0.030, (0, Y_CUBA0 - 0.040, Z_CUBA - R_CUBA + 0.010), segs=32, r=0.003, mat=trans)
    L.cilindro('grifo boca', 0.008, 0.012, (0, Y_CUBA0 - 0.040, Z_CUBA - R_CUBA - 0.002), segs=24, mat=trans)
    pal = L.caja('grifo palanca', 0.018, 0.008, 0.090, (-0.030, Y_CUBA0 - 0.058, Z_CUBA - 0.070), r=0.004, segs=4, mat=bl_pl)
    L.girar_malla(pal, (-0.030, Y_CUBA0 - 0.058, Z_CUBA - 0.070), 'X', -12)
    # asiento blanco de la cuba sobre el cuerpo (vuela 10 mm por delante del frente)
    L.caja('asiento cuba', 0.190, 0.300, 0.012, (0, -0.015, Z_CUERPO - 0.001), r=0.004, segs=3, mat=blanco)

    # --- frontal: panel de control (170 de ancho, dentro de la zona plana del frente), botones, logo dorado
    ruta = os.path.join(L.CALCAS_DIR, 'A3_panel.png')
    calca_panel(ruta)
    L.calca('A3 panel', ruta, 0.170, 0.090, (0, Y_FRENTE - 0.0003, 0.255), normal='-Y', emision=0.4)
    P.boton('boton encendido', (0.070, Y_FRENTE, 0.275), d=0.012, alto=0.003, mat=L.mat_plastico('Plastico rojo', (0.7, 0.05, 0.03)))
    for nm, x in (('boton alarma', -0.050), ('boton limpieza', -0.017), ('boton menos', 0.017), ('boton mas', 0.045)):
        P.boton(nm, (x, Y_FRENTE, 0.240), d=0.012, alto=0.003, mat=L.mat_plastico('Plastico gris', (0.30, 0.30, 0.30)))
    ruta2 = os.path.join(L.CALCAS_DIR, 'A3_logo.png')
    calca_bras(ruta2, oro=False)
    L.calca('A3 logo', ruta2, 0.040, 0.014, (-0.045, Y_FRENTE - 0.0003, 0.100), normal='-Y')

    # --- bandeja de goteo blanca (60 de alto, metida 2 mm en el frente) con rejilla y punto rojo
    L.caja('bandeja', A, 0.092, 0.060, (0, Y_FRENTE - 0.044, H_PIE + 0.010), r_vert=0.025, r=0.006, segs=6, mat=bl_pl)
    rej = L.caja('bandeja rejilla', A - 0.024, 0.066, 0.003, (0, Y_FRENTE - 0.044, H_PIE + 0.070), r=0.001, segs=2, mat=bl_pl)
    for i in range(9):
        L.sustraer(rej, L.caja(f'rejilla ranura {i + 1}', 0.004, 0.050, 0.02, (-0.070 + i * 0.0175, Y_FRENTE - 0.044, H_PIE + 0.060)))
    P.piloto('punto rojo', (0, Y_FRENTE - 0.012, H_PIE + 0.073), d=0.006, color=(1.0, 0.05, 0.02), normal='+Y', fuerza=0.5)
    L.girar_malla(L.bpy.data.objects['punto rojo'], (0, Y_FRENTE - 0.012, H_PIE + 0.073), 'X', 90)

    # cable: nace 3 mm dentro de la trasera, bajo el panel marron
    P.cable('cable', (0.05, Y_TRAS - 0.003, 0.045), largo=0.25, d=0.008)
    return dict(ignorar=('cable', 'boton', 'pomo tapa', 'panel izquierdo tira', 'panel derecho tira',
                         'panel izquierdo tornillo', 'panel derecho tornillo'))
