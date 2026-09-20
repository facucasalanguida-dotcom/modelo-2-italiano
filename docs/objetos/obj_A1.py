# -*- coding: utf-8 -*-
"""
A1 · Cafetera espresso profesional de 2 grupos (barra), 1000 x 600 x 500.
No es de Makro: diseno propio con la tipologia italiana clasica (referencia
La Marzocco Linea Classic 2GR y Rancilio Classe 9), respetando las medidas
del plano: el ancho de 1,00 (mas que una 2 grupos real, 0,69-0,85) se
absorbe en los paneles laterales y en las zonas de mandos, sin estirar los
grupos.

Alzado (de abajo arriba): pies de goma negros O 50 x 25; zocalo negro
retranqueado 20 (55 de alto); bandeja de goteo inox de 980 x 230 x 90
delante con rejilla de varilla; cuerpo inferior de inox pulido espejo
retranqueado; panel de mandos de 115 de alto que vuela 120 sobre el cuerpo
(rasgo de la Linea / Classe 9) de modo que los grupos cuelgan enteros a la
vista, con por grupo
3 teclas negras con aro rojo + tecla de icono y display rojo de 3 digitos,
manometro central O 60 de esfera blanca con aro cromado, ruedas de vapor
negras estriadas O 50 en los extremos; 2 grupos cromados O 100 con cabeza
de portafiltro O 75 y mango negro apuntando 10 grados abajo, 2 pitorros;
interruptor general 0/1 negro a la izquierda; grifo de agua caliente con
boquilla de bulbo a la derecha; 2 lanzas de vapor cromadas O 12 con
articulacion esferica y empunadura de goma negra; calientatazas superior
con marco inox de 20 y chapa perforada, retranqueado 110 respecto al panel.
Rotulo rojo generico "ESPRESSO" en el frente de la bandeja (sin marca).

Origen: centro de la huella (bandeja incluida), frente en -Y.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 1.000, 0.600, 0.500
Y_FRENTE, Y_TRAS = -F / 2, F / 2
H_PIE, H_ZOC = 0.025, 0.055
Z_CUERPO0 = H_PIE + H_ZOC                    # 0,080
BANDEJA_W, BANDEJA_D, BANDEJA_H = 0.980, 0.230, 0.090
Y_CUERPO = Y_FRENTE + BANDEJA_D              # frente del cuerpo inferior: -0,07
Z_PANEL0, PANEL_H = 0.280, 0.115
Y_PANEL = Y_CUERPO - 0.120                   # frente del panel de mandos: vuela 120 (Linea / Classe 9)
Z_TAPA0 = Z_PANEL0 + PANEL_H                 # 0,395
Y_TAPA = Y_CUERPO - 0.010                    # frente del calientatazas, casi a ras del cuerpo
X_GRUPOS = (-0.185, 0.185)
Y_GRUPO = Y_PANEL + 0.070                    # eje de los grupos: cuelgan enteros delante del cuerpo


def _f(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_display(ruta):
    im = Image.new('RGBA', (180, 72), (10, 10, 12, 255))
    ImageDraw.Draw(im).text((22, 4), '0 1', font=_f(58, True), fill=(255, 45, 25, 255))
    im.save(ruta)


def calca_manometro(ruta):
    """Esfera blanca O 56 con escala 0-16 bar, aguja negra. 560 px."""
    S = 560
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.ellipse((0, 0, S - 1, S - 1), fill=(246, 246, 242, 255))
    negro = (25, 25, 28, 255)
    for i in range(17):
        a = math.radians(135 + 270 * i / 16)
        r1, r2 = 230, 250 if i % 4 == 0 else 242
        dr.line((S / 2 + r1 * math.cos(a), S / 2 + r1 * math.sin(a), S / 2 + r2 * math.cos(a), S / 2 + r2 * math.sin(a)),
                fill=negro, width=6 if i % 4 == 0 else 3)
        if i % 4 == 0:
            t = str(i)
            bb = dr.textbbox((0, 0), t, font=_f(40, True))
            x, y = S / 2 + 195 * math.cos(a), S / 2 + 195 * math.sin(a)
            dr.text((x - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), t, font=_f(40, True), fill=negro)
    dr.text((S / 2 - 30, S / 2 + 90), 'bar', font=_f(30), fill=negro)
    a = math.radians(135 + 270 * 9 / 16)
    dr.line((S / 2 - 40 * math.cos(a), S / 2 - 40 * math.sin(a), S / 2 + 215 * math.cos(a), S / 2 + 215 * math.sin(a)), fill=negro, width=8)
    dr.ellipse((S / 2 - 16, S / 2 - 16, S / 2 + 16, S / 2 + 16), fill=negro)
    im.save(ruta)


def calca_rotulo(ruta):
    W, Hh = 1200, 200
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    t = 'ESPRESSO'
    f = _f(120, True)
    bb = dr.textbbox((0, 0), t, font=f)
    dr.text(((W - (bb[2] - bb[0])) / 2 - bb[0], (Hh - (bb[3] - bb[1])) / 2 - bb[1]), t, font=f, fill=(200, 20, 25, 255))
    im.save(ruta)


def calca_interruptor(ruta):
    S = 320
    im = Image.new('RGBA', (S, S), (12, 12, 14, 255))
    dr = ImageDraw.Draw(im)
    dr.text((40, 30), '0', font=_f(60, True), fill=(240, 240, 240, 255))
    dr.text((230, 30), '1', font=_f(60, True), fill=(240, 240, 240, 255))
    im.save(ruta)


def esfera(nombre, r, centro, mat=None, segs=48):
    perfil = [(r * math.sin(math.pi * i / 16), -r * math.cos(math.pi * i / 16)) for i in range(17)]
    return L.perfil_revolucion(nombre, perfil, centro, segs=segs, mat=mat)


def build():
    espejo = L.mat_inox_pulido()
    inox = L.mat_inox()
    cromo = L.mat_cromo()
    negro = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    negro_b = L.mat_plastico('Plastico negro brillante', (0.01, 0.01, 0.011), rug=0.18, brillo=0.5)
    goma = L.mat_goma()
    lacado = L.mat_chapa('Zocalo negro lacado', (0.02, 0.02, 0.022), rug=0.3, brillo=0.4)
    rojo_led = L.mat_led('LED rojo aro', (1.0, 0.08, 0.03), 1.0)
    rutad = os.path.join(L.CALCAS_DIR, 'A1_display.png')
    calca_display(rutad)
    mat_display = L.mat_calca('Calca A1 display', rutad, 1.2)
    oscuro = L.mat_plastico('Interior oscuro', (0.01, 0.01, 0.01), rug=0.9)

    # --- pies, zocalo negro retranqueado y cuerpo inferior
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        L.cilindro(f'pie {i + 1}', 0.025, H_PIE, (sx * (A / 2 - 0.080), Y_FRENTE + 0.060 if sy < 0 else Y_TRAS - 0.060, 0), r=0.005, segs=40, mat=goma)
    L.caja('zocalo', A - 0.040, Y_TRAS - Y_CUERPO - 0.020, H_ZOC + 0.002, (0, (Y_CUERPO + Y_TRAS) / 2, H_PIE), r=0.004, segs=3, mat=lacado)
    cuerpo = L.caja('cuerpo', A, Y_TRAS - Y_CUERPO, Z_PANEL0 - Z_CUERPO0 + 0.002, (0, (Y_CUERPO + Y_TRAS) / 2, Z_CUERPO0), r=0.004, segs=4, mat=espejo)
    # --- bandeja de goteo delante: cubeta inox con rejilla de varilla y rotulo
    ban = L.caja('bandeja', BANDEJA_W, BANDEJA_D, BANDEJA_H, (0, Y_FRENTE + BANDEJA_D / 2, H_PIE), r=0.003, segs=3, mat=espejo)
    L.sustraer(ban, L.caja('bandeja hueco', BANDEJA_W - 0.016, BANDEJA_D - 0.012, 0.070, (0, Y_FRENTE + BANDEJA_D / 2 + 0.002, H_PIE + BANDEJA_H - 0.060), r_vert=0.006))
    L.caja('bandeja fondo', BANDEJA_W - 0.018, BANDEJA_D - 0.014, 0.002, (0, Y_FRENTE + BANDEJA_D / 2 + 0.002, H_PIE + BANDEJA_H - 0.058), mat=oscuro, suave=False)
    z_rej = H_PIE + BANDEJA_H - 0.006
    for k, xc in enumerate((-0.327, 0.0, 0.327)):
        P.estante_rejilla(f'rejilla goteo {k + 1}', (xc, Y_FRENTE + BANDEJA_D / 2 + 0.002, z_rej), 0.316, BANDEJA_D - 0.030, paso=0.008, d_barra=0.004, mat=espejo)
    ruta = os.path.join(L.CALCAS_DIR, 'A1_rotulo.png')
    calca_rotulo(ruta)
    L.calca('A1 rotulo', ruta, 0.180, 0.030, (-0.30, Y_FRENTE - 0.0003, H_PIE + 0.045), normal='-Y')

    # --- panel de mandos (vuela 35) y calientatazas (retranqueado 55)
    panel = L.caja('panel mandos', A, Y_TRAS - Y_PANEL, PANEL_H, (0, (Y_PANEL + Y_TRAS) / 2, Z_PANEL0), r=0.003, segs=3, mat=espejo)
    tapa = L.caja('calientatazas', A, Y_TRAS - Y_TAPA, H - Z_TAPA0, (0, (Y_TAPA + Y_TRAS) / 2, Z_TAPA0), r=0.003, segs=3, mat=inox)
    L.sustraer(tapa, L.caja('calientatazas hueco', A - 0.040, Y_TRAS - Y_TAPA - 0.040, 0.030, (0, (Y_TAPA + Y_TRAS) / 2, H - 0.012), r_vert=0.004))
    L.caja('calientatazas fondo', A - 0.042, Y_TRAS - Y_TAPA - 0.042, 0.002, (0, (Y_TAPA + Y_TRAS) / 2, H - 0.012), mat=oscuro, suave=False)
    for k, xc in enumerate((-(A - 0.044) / 4, (A - 0.044) / 4)):
        L.caja(f'calientatazas chapa {k + 1}', (A - 0.044) / 2 - 0.002, Y_TRAS - Y_TAPA - 0.044, 0.0015, (xc, (Y_TAPA + Y_TRAS) / 2, H - 0.008),
               mat=L.mat_chapa_perforada('Chapa perforada calientatazas', d=0.004, paso=0.008), suave=False)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        for j, (dx, dy) in enumerate(((0.010, 0.010), (0.030, 0.010), (0.010, 0.030))):
            L.cilindro(f'tornillo tapa {i + 1}.{j + 1}', 0.0025, 0.0008, (sx * (A / 2 - dx), (Y_TAPA + 0.0 if sy < 0 else Y_TRAS) - sy * dy, H), segs=16, mat=cromo)

    # --- grupos: cuerpo cromado, cabeza de portafiltro, mango negro y pitorros
    for k, x in enumerate(X_GRUPOS):
        n = f'grupo {k + 1}'
        L.cilindro(n, 0.050, 0.035, (x, Y_GRUPO, Z_PANEL0 - 0.033), segs=64, r=0.004, mat=cromo)
        L.cilindro(n + ' cabeza', 0.0375, 0.018, (x, Y_GRUPO, Z_PANEL0 - 0.051), segs=64, r=0.003, mat=cromo)
        L.cilindro(n + ' tuerca', 0.030, 0.010, (x, Y_GRUPO, Z_PANEL0 - 0.061), segs=48, r=0.002, mat=cromo)
        # orejas del portafiltro y mango apuntando 10 grados hacia abajo
        L.caja(n + ' oreja', 0.024, 0.030, 0.014, (x, Y_GRUPO - 0.045, Z_PANEL0 - 0.057), r=0.003, segs=3, mat=cromo)
        mango = L.cilindro(n + ' mango', 0.015, 0.120, (x, Y_GRUPO - 0.058 - 0.120, Z_PANEL0 - 0.050), eje='Y', segs=32, r=0.006, radio2=0.012, mat=negro_b)
        L.girar_malla(mango, (x, Y_GRUPO - 0.058, Z_PANEL0 - 0.050), 'X', 10)
        for sx in (-1, 1):
            L.cilindro(f'{n} pitorro {sx}', 0.005, 0.024, (x + sx * 0.014, Y_GRUPO - 0.006, Z_PANEL0 - 0.085), segs=24, mat=cromo)
        # botonera: 3 teclas con aro rojo + tecla de icono, y display encima
        for j in range(4):
            xb = x - 0.045 + j * 0.030
            L.caja(f'{n} tecla {j + 1} aro', 0.020, 0.0015, 0.020, (xb, Y_PANEL - 0.00075, Z_PANEL0 + 0.040), mat=rojo_led if j < 3 else negro, suave=False)
            L.caja(f'{n} tecla {j + 1}', 0.017, 0.004, 0.017, (xb, Y_PANEL - 0.0035, Z_PANEL0 + 0.042), r=0.001, segs=2, mat=negro)
        L.plano(f'{n} display', 0.040, 0.018, (x, Y_PANEL - 0.0004, Z_PANEL0 + 0.088), normal='-Y', mat=mat_display)
    # oreja del mango: 10 grados hacia abajo se aplica al mango; el resto queda horizontal

    # --- manometro central, ruedas de vapor, interruptor general, grifo de agua
    rutam = os.path.join(L.CALCAS_DIR, 'A1_manometro.png')
    calca_manometro(rutam)
    L.tubo('manometro aro', 0.032, 0.0285, 0.010, (0, Y_PANEL - 0.010, Z_PANEL0 + 0.050), eje='Y', segs=64, mat=cromo)
    L.cilindro('manometro esfera', 0.0285, 0.003, (0, Y_PANEL - 0.004, Z_PANEL0 + 0.050), eje='Y', segs=64, mat=negro)
    L.calca('manometro calca', rutam, 0.056, 0.056, (0, Y_PANEL - 0.0043, Z_PANEL0 + 0.050), normal='-Y', emision=0.5)
    L.cilindro('manometro vidrio', 0.0285, 0.002, (0, Y_PANEL - 0.008, Z_PANEL0 + 0.050), eje='Y', segs=64, mat=L.mat_vidrio('Vidrio manometro'))
    for k, sx in enumerate((-1, 1)):
        x = sx * (A / 2 - 0.060)
        L.cilindro(f'rueda vapor {k + 1}', 0.025, 0.030, (x, Y_PANEL - 0.030, Z_PANEL0 + 0.050), eje='Y', segs=64, r=0.004, mat=negro)
        for j in range(12):
            a = math.radians(j * 30)
            L.caja(f'rueda vapor {k + 1} estria {j + 1}', 0.006, 0.024, 0.004, (x + 0.024 * math.cos(a), Y_PANEL - 0.016, Z_PANEL0 + 0.050 + 0.024 * math.sin(a) - 0.002),
                   mat=negro, suave=False)
        L.cilindro(f'rueda vapor {k + 1} eje', 0.008, 0.006, (x, Y_PANEL - 0.036, Z_PANEL0 + 0.050), eje='Y', segs=32, mat=cromo)
    rutai = os.path.join(L.CALCAS_DIR, 'A1_interruptor.png')
    calca_interruptor(rutai)
    L.caja('interruptor placa', 0.050, 0.003, 0.050, (-0.360, Y_CUERPO - 0.0015, Z_PANEL0 - 0.075), r=0.001, segs=2, mat=negro)
    L.calca('interruptor calca', rutai, 0.048, 0.048, (-0.360, Y_CUERPO - 0.0034, Z_PANEL0 - 0.050), normal='-Y')
    L.cilindro('interruptor mando', 0.012, 0.012, (-0.360, Y_CUERPO - 0.015, Z_PANEL0 - 0.050), eje='Y', segs=32, r=0.002, mat=negro)
    L.caja('interruptor mando pala', 0.006, 0.010, 0.020, (-0.360, Y_CUERPO - 0.020, Z_PANEL0 - 0.060), r=0.001, segs=2, mat=negro)
    # grifo de agua caliente: codo cromado con boquilla de bulbo
    L.tubo_curva('grifo agua', [(0.340, Y_CUERPO + 0.010, Z_PANEL0 - 0.020), (0.340, Y_CUERPO - 0.030, Z_PANEL0 - 0.022),
                                (0.340, Y_CUERPO - 0.045, Z_PANEL0 - 0.050)], 0.007, mat=cromo)
    L.perfil_revolucion('grifo agua bulbo', [(0.006, 0.0), (0.011, 0.006), (0.012, 0.016), (0.009, 0.026), (0.006, 0.030)],
                        (0.340, Y_CUERPO - 0.045, Z_PANEL0 - 0.085), segs=48, mat=cromo)
    # --- lanzas de vapor: tubo cromado con rotula y empunadura de goma, hacia fuera y abajo
    for k, sx in enumerate((-1, 1)):
        x0 = sx * (A / 2 - 0.045)
        esfera(f'lanza {k + 1} rotula', 0.014, (x0, Y_CUERPO - 0.030, Z_PANEL0 - 0.030), mat=cromo)
        pts = [(x0, Y_CUERPO + 0.005, Z_PANEL0 - 0.020), (x0, Y_CUERPO - 0.040, Z_PANEL0 - 0.035),
               (x0 + sx * 0.005, Y_CUERPO - 0.110, Z_PANEL0 - 0.090), (x0 + sx * 0.010, Y_CUERPO - 0.160, Z_PANEL0 - 0.145)]
        L.tubo_curva(f'lanza {k + 1}', pts, 0.006, mat=cromo)
        L.tubo_curva(f'lanza {k + 1} empunadura', [(x0 + sx * 0.006, Y_CUERPO - 0.118, Z_PANEL0 - 0.099),
                                                    (x0 + sx * 0.009, Y_CUERPO - 0.150, Z_PANEL0 - 0.134)], 0.010, mat=goma)
        L.cilindro(f'lanza {k + 1} punta', 0.0075, 0.012, (x0 + sx * 0.010, Y_CUERPO - 0.160, Z_PANEL0 - 0.155), segs=32, r=0.002, mat=cromo)

    # --- trasera: panel liso con placa y salida de cable
    L.caja('placa trasera', 0.080, 0.002, 0.050, (0.30, Y_TRAS - 0.0015, 0.15), mat=L.mat_aluminio('Placa aluminio', rug=0.3), suave=False)
    P.cable('cable', (-0.30, Y_TRAS, 0.12), largo=0.30, d=0.010)
    return dict(ignorar=('cable',))
