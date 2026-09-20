# -*- coding: utf-8 -*-
"""
K6 · Lavavajillas industrial cesta 50 x 50 ST500 (Clima Hosteleria "Linea
Varsovia" = Stalgast 801505), 565 x 651 x 863.

Referencia: foto oficial de Clima y fotos Stalgast de la misma carcasa.
Carcasa entera de inox satinado: tapa con tres nervios frente-trasera, banda
de mandos superior (~95) a ras del frente con "ST500", dos iconos de termometro con LED y tres
ruletas AZULES con LED e icono (lavado, programa 1/2, encendido); puerta
frontal abatible hacia abajo, retranqueada 4 tras la banda, con asa en arco de
pletina inox y apoyos negros; zocalo inferior liso ligeramente retranqueado;
laterales con un gran rectangulo embutido; cuatro pies negros regulables;
trasera gris con caja de conexiones, toma de agua y desague en un rebaje de 40.

Confirmado: 565 x 651 (alto 863 segun Clima; Stalgast dice 835), puerta,
panel, asa. Supuesto: reparto exacto de alturas, trasera (gris con tomas).
AVISO del plano: con 863 de alto no cabe bajo el escurridor del fregadero K7
(luz ~805); ya esta anotado en CONFLICTOS del modelo 3D.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 0.565, 0.651, 0.863
H_PIE = 0.028
E_TAPA = 0.005
Y_FRENTE, Y_TRAS = -F / 2, F / 2
Z_BANDA0 = H - E_TAPA - 0.095          # arranque de la banda de mandos
PUERTA_W, PUERTA_H, PUERTA_E = 0.520, 0.430, 0.006
Z_PUERTA0 = Z_BANDA0 - PUERTA_H         # 0,333
Y_PUERTA = Y_FRENTE + 0.004             # cara de la puerta, retranqueada 4 tras la banda
F_CUERPO = F - 0.040                    # el cuerpo deja 40 detras para tomas y trasera


def _f(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_banda(ruta):
    """Serigrafia de la banda de mandos (565 x 95 mm a 4 px/mm): ST500,
    dos termometros, iconos de ventilador, reloj 1/2 y 'I'."""
    W, Hh = int(A * 4000), int(0.095 * 4000)
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    gris = (110, 112, 115, 255)
    negro = (30, 30, 32, 255)

    def px(x, z):
        return (W / 2 + x * 4000, Hh - z * 4000)

    x0, y0 = px(-0.235, 0.066)
    dr.text((x0, y0 - 20), 'ST500', font=_f(48, True), fill=gris)
    # termometros (cuba arriba, calderin abajo)
    for z in (0.070, 0.040):
        cx, cy = px(-0.150, z)
        dr.rounded_rectangle((cx - 5, cy - 16, cx + 5, cy + 4), radius=5, outline=negro, width=3)
        dr.ellipse((cx - 9, cy + 1, cx + 9, cy + 19), outline=negro, width=3)
    # icono ventilador (lavado)
    cx, cy = px(-0.060, 0.072)
    for a in (0, 120, 240):
        r = math.radians(a)
        dr.pieslice((cx - 22, cy - 22, cx + 22, cy + 22), a - 30, a + 30, fill=negro)
    dr.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(255, 255, 255, 255))
    # reloj con 1/2
    cx, cy = px(0.050, 0.072)
    dr.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), outline=negro, width=4)
    dr.line((cx, cy, cx, cy - 14), fill=negro, width=4)
    dr.line((cx, cy, cx + 10, cy), fill=negro, width=4)
    dr.text((cx + 26, cy - 16), '1/2', font=_f(24, True), fill=negro)
    # encendido I
    cx, cy = px(0.160, 0.072)
    dr.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), outline=negro, width=4)
    dr.line((cx, cy - 12, cx, cy + 12), fill=negro, width=5)
    im.save(ruta)


def build():
    inox = L.mat_inox()
    inox_p = L.mat_inox_pulido()
    plast = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    azul = L.mat_plastico('Plastico azul', (0.04, 0.16, 0.85), rug=0.35, brillo=0.3)
    gris = L.mat_chapa('Chapa gris trasera', (0.25, 0.26, 0.27), rug=0.5, brillo=0.05)

    # --- pies regulables y cuerpo
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        L.cilindro(f'pie {i + 1}', 0.0175, 0.012, (sx * (A / 2 - 0.040), sy * (F / 2 - 0.045), 0), r=0.003, segs=32, mat=plast)
        L.cilindro(f'pie {i + 1} rosca', 0.008, H_PIE - 0.012, (sx * (A / 2 - 0.040), sy * (F / 2 - 0.045), 0.012), segs=24, mat=inox_p)
    cuerpo = L.caja('cuerpo', A, F_CUERPO, H - H_PIE - E_TAPA, (0, Y_FRENTE + F_CUERPO / 2, H_PIE), r=0.002, segs=3, mat=inox)
    # rebaje de 10 mm bajo la banda (la puerta queda 4 mm por detras de la banda) y zocalo 8 mm mas atras
    # el cortador sobresale 5 mm por delante: si su cara trasera coincidiera
    # con la del cuerpo, la booleana dejaria dos caras superpuestas con
    # normales opuestas (franjas de interferencia en el render)
    L.sustraer(cuerpo, L.caja('rebaje puerta', A + 0.01, 0.015, Z_BANDA0 - H_PIE, (0, Y_FRENTE + 0.0025, H_PIE - 0.001)))
    L.sustraer(cuerpo, L.caja('zocalo rebaje', A + 0.01, 0.023, Z_PUERTA0 - H_PIE - 0.004, (0, Y_FRENTE + 0.0065, H_PIE - 0.002)))
    # tapa con tres nervios
    L.caja('tapa', A, F, E_TAPA, (0, 0, H - E_TAPA - 0.0015), r=0.002, segs=2, mat=inox)
    for i, x in enumerate((-0.14, 0.0, 0.14)):
        L.caja(f'nervio {i + 1}', 0.010, F - 0.080, 0.0015, (x, 0, H - 0.0015), r=0.0007, segs=2, mat=inox)
    # recuadro embutido de 1,5 mm en los laterales, con marco de 30
    for nm, sx in (('derecho', 1), ('izquierdo', -1)):
        L.sustraer(cuerpo, L.caja(f'embutido {nm}', 0.003, F_CUERPO - 0.060, H - H_PIE - E_TAPA - 0.060,
                                  (sx * A / 2, Y_FRENTE + F_CUERPO / 2, H_PIE + 0.030), r=0.0015, segs=3))

    # --- puerta abatible con asa en arco
    L.caja('puerta', PUERTA_W, PUERTA_E, PUERTA_H, (0, Y_PUERTA + PUERTA_E / 2, Z_PUERTA0), r=0.002, segs=3, mat=inox)
    L.caja('puerta junta', PUERTA_W + 0.004, 0.002, PUERTA_H + 0.004, (0, Y_PUERTA + PUERTA_E - 0.001, Z_PUERTA0 - 0.002),
           mat=L.mat_goma(), suave=False)
    za = Z_PUERTA0 + PUERTA_H - 0.040
    # arco de pletina: 7 tramos sobre una circunferencia de radio 0,6 (flecha ~25 mm)
    R, n = 0.60, 7
    ang_tot = 0.35 / R
    for i in range(n):
        a = -ang_tot / 2 + ang_tot * (i + 0.5) / n
        seg = L.caja(f'asa {i + 1}', 0.35 / n + 0.002, 0.005, 0.030, (R * math.sin(a), Y_PUERTA - 0.035 - (R * math.cos(a) - R) + 0.0, za - 0.015),
                     r=0.001, segs=2, mat=inox_p)
        L.girar_malla(seg, (R * math.sin(a), Y_PUERTA - 0.035 - (R * math.cos(a) - R), za), 'Z', math.degrees(a))
    for i, x in enumerate((-0.175, 0.175)):
        L.caja(f'asa apoyo {i + 1}', 0.024, 0.038, 0.034, (x, Y_PUERTA - 0.019, za - 0.017), r=0.004, segs=3, mat=plast)

    # --- banda de mandos
    ruta = os.path.join(L.CALCAS_DIR, 'K6_banda.png')
    calca_banda(ruta)
    L.calca('K6 banda', ruta, A - 0.004, 0.095 - 0.002, (0, Y_FRENTE - 0.0003, Z_BANDA0 + 0.0475), normal='-Y')
    yb = Y_FRENTE
    for nm, x, col, fz in (('mando lavado', -0.060, (0.15, 0.15, 0.15), 0.1), ('mando programa', 0.050, (0.1, 0.4, 1.0), 4.0), ('mando encendido', 0.160, (0.1, 0.9, 0.2), 4.0)):
        P.mando_ruleta(nm, (x, yb, Z_BANDA0 + 0.045), d=0.028, alto=0.016, mat=azul)
        P.piloto(nm + ' piloto', (x - 0.022, yb, Z_BANDA0 + 0.072), d=0.006, color=col, fuerza=fz)
    P.piloto('piloto cuba', (-0.172, yb, Z_BANDA0 + 0.070), d=0.006, color=(0.1, 0.4, 1.0))
    P.piloto('piloto calderin', (-0.172, yb, Z_BANDA0 + 0.040), d=0.006, color=(0.1, 0.4, 1.0))

    # --- trasera: panel gris con caja de conexiones, entrada de agua y desague
    L.caja('trasera', A - 0.004, 0.003, H - H_PIE - E_TAPA - 0.004, (0, Y_TRAS - 0.040 + 0.0015, H_PIE + 0.002), mat=gris, suave=False)
    L.caja('caja conexiones', 0.120, 0.030, 0.090, (0.15, Y_TRAS - 0.037 + 0.015, 0.45), r=0.003, mat=gris)
    L.cilindro('toma agua', 0.012, 0.030, (-0.15, Y_TRAS - 0.037, 0.30), eje='Y', segs=24, r=0.002, mat=L.mat_cromo())
    L.cilindro('desague', 0.016, 0.030, (0.0, Y_TRAS - 0.037, 0.12), eje='Y', segs=24, r=0.002, mat=plast)

    return dict(ignorar=('asa', 'mando', 'piloto'))
