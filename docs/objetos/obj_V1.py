# -*- coding: utf-8 -*-
"""
V1 / V2 · Vitrina expositora refrigerada de mostrador (pasteleria / tapas),
1000 x 700 x 1250, dos unidades iguales (V2 importa este build).
No es de Makro: diseno propio siguiendo la tipologia Infrico VBR 9 R (cristal
curvo abatible, laterales en "D" de chapa negra con cristal inserto, plano
de exposicion inox, 2 estantes de vidrio escalonados con perfil de aluminio
y LED, puertas correderas traseras de vidrio, zocalo lacado con rejilla y
controlador digital), con las cotas del plano oficial reescaladas de
976 x 810 x 1300 a 1000 x 700 x 1250 (zocalo 415, zona acristalada 835).

Acabado elegido: zocalo lacado antracita mate (RAL 7016), laterales negro
brillo, perfiles inox / aluminio anodizado, interior inox y negro.
Origen: centro de la huella, frente (cristal curvo) hacia -Y.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 1.000, 0.700, 1.250
Y_FRENTE, Y_TRAS = -F / 2, F / 2
E_LAT = 0.019                        # panel lateral
Z_PLANO = 0.415                      # cara superior del plano de exposicion
E_PLANO = 0.020
Y_ZOC = Y_FRENTE + 0.040             # frente del zocalo (el plano vuela 40)
Z_TOP0, TOP_H = H - 0.050, 0.050     # perfil superior
Y_TOP = -0.020                       # frente del perfil superior
X_INT = A / 2 - E_LAT                # cara interior de los laterales
# arco del cristal: tangente vertical en P1 = (Y_FRENTE, Z_ARC0) y pasa por P2 = (Y_TOP, Z_TOP0)
Z_ARC0 = 0.450
_dy, _dz = Y_TOP - Y_FRENTE, Z_TOP0 - Z_ARC0
R_ARC = (_dy ** 2 + _dz ** 2) / (2 * _dy)
CY, CZ = Y_FRENTE + R_ARC, Z_ARC0    # centro del arco
A1 = math.pi
A2 = math.atan2(Z_TOP0 - CZ, Y_TOP - CY)


def arco(r, n=28, desde=A1, hasta=A2):
    return [(CY + r * math.cos(desde + (hasta - desde) * i / n), CZ + r * math.sin(desde + (hasta - desde) * i / n)) for i in range(n + 1)]


def _f(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_control(ruta):
    W, Hh = 400, 120
    im = Image.new('RGBA', (W, Hh), (10, 10, 12, 255))
    dr = ImageDraw.Draw(im)
    dr.text((30, 22), '4.0', font=_f(70, True), fill=(255, 45, 25, 255))
    for k in range(4):
        dr.rounded_rectangle((200 + k * 46, 40, 232 + k * 46, 80), radius=5, fill=(60, 60, 62, 255))
    im.save(ruta)


def build():
    inox = L.mat_inox()
    inox_p = L.mat_inox_pulido()
    alu = L.mat_aluminio('Aluminio anodizado')
    negro_b = L.mat_chapa('Chapa negro brillo', (0.01, 0.01, 0.011), rug=0.12, brillo=0.6, piel=0.05)
    negro = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    antracita = L.mat_chapa('Lacado antracita', (0.045, 0.047, 0.050), rug=0.45, brillo=0.1)
    vidrio = L.mat_vidrio('Vidrio templado', tinte=(0.92, 0.98, 0.96))
    led = L.mat_led('LED blanco', (1.0, 0.97, 0.92), 12.0)
    oscuro = L.mat_plastico('Interior oscuro', (0.01, 0.01, 0.01), rug=0.9)

    # --- zocalo lacado con pies, rejilla negra y controlador
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        P.pata_regulable(f'pie {i + 1}', (sx * (A / 2 - 0.060), (Y_ZOC + 0.060) if sy < 0 else (Y_TRAS - 0.060), 0), 0.032, d_tubo=0.024, d_pie=0.040, h_pie=0.012, mat_tubo=negro)
    zoc = L.caja('zocalo', A - 2 * E_LAT, Y_TRAS - Y_ZOC, Z_PLANO - E_PLANO - 0.040, (0, (Y_ZOC + Y_TRAS) / 2, 0.020), r=0.003, segs=3, mat=antracita)
    P.rejilla_ranuras('rejilla condensador', (-0.12, Y_ZOC, 0.140), 0.600, 0.200, normal='-Y', paso=0.012, ranura=0.006, orient='H', mat=negro, cuerpo=zoc)
    ruta = os.path.join(L.CALCAS_DIR, 'V1_control.png')
    calca_control(ruta)
    L.caja('control marco', 0.104, 0.003, 0.034, (0.38, Y_ZOC - 0.0015, 0.060), r=0.001, segs=2, mat=negro)
    L.calca('V1 control', ruta, 0.100, 0.030, (0.38, Y_ZOC - 0.0034, 0.077), normal='-Y', emision=1.5)
    # franja inox entre zocalo y plano
    L.caja('franja inox', A - 2 * E_LAT, Y_TRAS - Y_ZOC, 0.022, (0, (Y_ZOC + Y_TRAS) / 2, Z_PLANO - E_PLANO - 0.020), mat=inox, suave=False)

    # --- plano de exposicion inox: vuela 40 por delante, ranura de retorno delante y rejilla de impulsion detras
    plano = L.caja('plano exposicion', A - 2 * E_LAT, F, E_PLANO, (0, 0, Z_PLANO - E_PLANO), r=0.002, segs=2, mat=inox)
    L.sustraer(plano, L.caja('ranura retorno', A - 2 * E_LAT - 0.060, 0.012, 0.010, (0, Y_FRENTE + 0.045, Z_PLANO - 0.008)))
    L.caja('ranura retorno fondo', A - 2 * E_LAT - 0.062, 0.010, 0.002, (0, Y_FRENTE + 0.045, Z_PLANO - 0.009), mat=oscuro, suave=False)
    L.caja('perfil inferior cristal', A - 2 * E_LAT, 0.030, 0.035, (0, Y_FRENTE + 0.015, Z_PLANO), r=0.002, segs=2, mat=alu)
    # cubierta del evaporador al fondo del plano, con rejilla de impulsion
    evap = L.caja('cubierta evaporador', A - 2 * E_LAT - 0.004, 0.110, 0.070, (0, Y_TRAS - 0.100 - 0.055, Z_PLANO), r=0.003, segs=3, mat=inox)
    P.rejilla_ranuras('rejilla impulsion', (0, Y_TRAS - 0.100 - 0.110, Z_PLANO + 0.040), 0.800, 0.040, normal='-Y', paso=0.010, ranura=0.005, orient='V', mat=inox, cuerpo=evap)

    # --- laterales en "D": chapa negra de 19 con cristal inserto (marco de 60)
    ext = [(Y_TRAS, Z_PLANO - E_PLANO - 0.020), (Y_TRAS, H), (Y_TOP, H)] + list(reversed(arco(R_ARC))) + [(Y_FRENTE, Z_PLANO - E_PLANO - 0.020)]
    # hueco del cristal: marco de 60 detras y abajo, 10 arriba; el arco interior (R - 60) se corta a esas alturas
    ri = R_ARC - 0.060
    zi0, zi1 = Z_PLANO + 0.060, Z_TOP0 - 0.010
    a_abajo = math.pi - math.asin((zi0 - CZ) / ri)
    a_arriba = math.pi - math.asin((zi1 - CZ) / ri)
    int_ = [(Y_TRAS - 0.060, zi0), (Y_TRAS - 0.060, zi1)] + list(reversed(arco(ri, desde=a_abajo, hasta=a_arriba)))
    for k, sx in enumerate((-1, 1)):
        x0, x1 = sx * X_INT, sx * A / 2
        lat = L.prisma_yz(f'lateral {k + 1}', ext, min(x0, x1), max(x0, x1), mat=negro_b, suave=True)
        L.sustraer(lat, L.prisma_yz(f'lateral {k + 1} hueco', int_, min(x0, x1) - 0.01, max(x0, x1) + 0.01))
        L.prisma_yz(f'lateral {k + 1} cristal', int_, sx * (X_INT + 0.006) if sx > 0 else sx * (X_INT + 0.012), sx * (X_INT + 0.012) if sx > 0 else sx * (X_INT + 0.006), mat=vidrio)
    # --- cristal frontal curvo de 6 mm entre laterales, y perfil superior con LED
    banda = arco(R_ARC) + list(reversed(arco(R_ARC - 0.006)))
    L.prisma_yz('cristal frontal', banda, -X_INT, X_INT, mat=vidrio, suave=True)
    L.caja('bisagra cristal', A - 2 * E_LAT - 0.002, 0.028, 0.020, (0, Y_TOP + 0.016, Z_TOP0 - 0.012), r=0.002, segs=2, mat=alu)
    top = L.caja('perfil superior', A - 2 * E_LAT, Y_TRAS - Y_TOP, TOP_H, (0, (Y_TOP + Y_TRAS) / 2, Z_TOP0), r=0.004, segs=3, mat=inox)
    L.caja('LED superior', A - 2 * E_LAT - 0.040, 0.015, 0.004, (0, Y_TOP + 0.060, Z_TOP0 - 0.014), mat=led, suave=False)
    L.caja('luminaria superior', A - 2 * E_LAT - 0.030, 0.030, 0.012, (0, Y_TOP + 0.060, Z_TOP0 - 0.012), r=0.002, segs=2, mat=alu)

    # --- cremalleras, mensulas y 2 estantes de vidrio escalonados con perfil LED
    for sx in (-1, 1):
        L.caja(f'cremallera {sx}', 0.020, 0.030, Z_TOP0 - Z_PLANO - 0.010, (sx * (X_INT - 0.010), Y_TRAS - 0.130, Z_PLANO + 0.005), mat=negro, suave=False)
    for k, (dz, fondo) in enumerate(((0.280, 0.330), (0.500, 0.250))):
        z = Z_PLANO + dz
        y_tras = Y_TRAS - 0.130
        L.caja(f'estante {k + 1}', A - 2 * E_LAT - 0.054, fondo - 0.010, 0.008, (0, y_tras - (fondo - 0.010) / 2, z), r=0.001, segs=2, mat=vidrio)
        L.caja(f'estante {k + 1} perfil', A - 2 * E_LAT - 0.050, 0.030, 0.030, (0, y_tras - fondo + 0.015, z - 0.018), r=0.002, segs=2, mat=alu)
        L.caja(f'estante {k + 1} LED', A - 2 * E_LAT - 0.080, 0.012, 0.003, (0, y_tras - fondo + 0.015, z - 0.021), mat=led, suave=False)
        for sx in (-1, 1):
            L.caja(f'estante {k + 1} mensula {sx}', 0.012, fondo - 0.020, 0.020, (sx * (X_INT - 0.026), y_tras - fondo / 2, z - 0.020), r=0.001, segs=2, mat=negro)

    # --- puertas correderas traseras de vidrio con marco negro y tiradores
    for k, (x, y) in enumerate(((-0.240, Y_TRAS - 0.022), (0.240, Y_TRAS - 0.040))):
        w, h = 0.482, Z_TOP0 - Z_PLANO - 0.020
        marco = L.caja(f'puerta {k + 1} marco', w, 0.016, h, (x, y, Z_PLANO + 0.010), r=0.002, segs=2, mat=negro)
        L.sustraer(marco, L.caja(f'puerta {k + 1} hueco', w - 0.040, 0.030, h - 0.040, (x, y, Z_PLANO + 0.030)))
        L.caja(f'puerta {k + 1} cristal', w - 0.038, 0.005, h - 0.038, (x, y, Z_PLANO + 0.029), mat=vidrio, suave=False)
        L.caja(f'puerta {k + 1} tirador', 0.018, 0.012, 0.120, (x + (0.215 if k == 0 else -0.215), y + 0.014, Z_PLANO + h / 2 - 0.060), r=0.003, segs=3, mat=negro)
    L.caja('carril 1', A - 2 * E_LAT, 0.050, 0.011, (0, Y_TRAS - 0.031, Z_PLANO - 0.001), mat=alu, suave=False)
    L.caja('carril 2', A - 2 * E_LAT, 0.050, 0.010, (0, Y_TRAS - 0.031, Z_TOP0 - 0.010), mat=alu, suave=False)
    return dict(ignorar=())
