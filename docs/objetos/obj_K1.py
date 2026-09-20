# -*- coding: utf-8 -*-
"""
K1 · Placa de coccion Bartscher 2K6000 GLN (art. 104907), 700 x 455 x 120.

Referencia: ficha tecnica oficial de Bartscher y fotos de catalogo. Es una
vitroceramica radiante SCHOTT CERAN de dos zonas de 3 kW lado a lado (Makro
la titula "induccion", pero es este modelo: 2 x O 230, 6 kW, 400 V, 700 x
455 x 120). Visualmente: vidrio negro brillante embutido a ras en un marco de
inox cepillado, frontal de 105 mm con dos ruletas negras O 40 con escala 0-10
serigrafiada, logo Bartscher centrado, cuatro patas negras O 40 x 15.

Confirmado: medidas exteriores, vidrio 650 de ancho, 2 zonas O 230 con
centros a 200 de los laterales, ruletas a 55 de los laterales, patas
retranqueadas 50. Supuesto (marcado como tal): fondo exacto del vidrio (390,
por proporcion de foto), rejilla de ventilacion trasera y salida del cable.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

TAG = 'K1'
A, F, H = 0.700, 0.455, 0.120          # ancho, fondo, alto (ficha oficial)
H_PATA = 0.015                         # patas negras O 40
H_CUERPO = H - H_PATA                  # 105 mm de frontal
G_A, G_F = 0.650, 0.390                # vidrio (ancho confirmado, fondo supuesto)
M_LADO, M_TRAS = 0.025, 0.020          # marcos laterales y trasero
G_Y = F / 2 - M_TRAS - G_F / 2         # centro del vidrio en Y
ZONA_X = 0.150                         # centros de zona a 200 de los laterales
D_ZONA = 0.230
D_MANDO = 0.040
X_MANDO = A / 2 - 0.055
Z_MANDO = H_PATA + H_CUERPO / 2 - 0.004


def _fuente(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_escala(ruta):
    """Escala 0-10 alrededor de la ruleta: 0 arriba, 1-10 en sentido
    horario, en gris oscuro (como en la foto) sobre transparente. 70 x 70 mm -> 700 px."""
    import math
    S = 700
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    f = _fuente(44, True)
    R = 260
    # 0 arriba; el 10 a la derecha del 0; la escala ocupa ~300 grados
    for i in range(11):
        ang = math.radians(-90 + (i * 300 / 10) - 150) if i else math.radians(-90)
        if i:
            ang = math.radians(-90 - 150 + i * 30)
        x, y = S / 2 + R * math.cos(ang), S / 2 + R * math.sin(ang)
        t = str(i)
        bb = dr.textbbox((0, 0), t, font=f)
        dr.text((x - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), t, font=f, fill=(40, 40, 42, 255))
        # raya de la escala
        r1, r2 = R - 48, R - 30
        dr.line((S / 2 + r1 * math.cos(ang), S / 2 + r1 * math.sin(ang),
                 S / 2 + r2 * math.cos(ang), S / 2 + r2 * math.sin(ang)), fill=(40, 40, 42, 255), width=5)
    im.save(ruta)


def calca_logo(ruta):
    """Placa plateada con 'Bartscher' en negro: 80 x 25 mm -> 800 x 250."""
    W, Hh = 800, 250
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((2, 2, W - 3, Hh - 3), radius=28, fill=(205, 207, 210, 255), outline=(150, 152, 155, 255), width=3)
    f = _fuente(150, True)
    t = 'Bartscher'
    bb = dr.textbbox((0, 0), t, font=f)
    dr.text(((W - (bb[2] - bb[0])) / 2 - bb[0], (Hh - (bb[3] - bb[1])) / 2 - bb[1]), t, font=f, fill=(25, 25, 28, 255))
    im.save(ruta)


def calca_vidrio(ruta):
    """Serigrafia del vidrio: rectangulo perimetral a 15 mm, anillo O 55 en
    cada zona, marcas en L delante y 'SCHOTT CERAN' delante a la derecha.
    650 x 390 mm -> 1300 x 780 px (2 px / mm)."""
    W, Hh = 1300, 780
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    gris = (175, 178, 180, 235)
    m = 30
    dr.rectangle((m, m, W - m, Hh - m), outline=gris, width=3)
    for cx in (W / 2 - ZONA_X * 2000, W / 2 + ZONA_X * 2000):
        cy = Hh / 2
        r = 55 / 2 * 2
        dr.ellipse((cx - r, cy - r, cx + r, cy + r), outline=gris, width=4)
    # marcas en L en las esquinas delanteras (la delantera es la de abajo: -Y)
    for sx in (m + 20, W - m - 20):
        d = 1 if sx < W / 2 else -1
        dr.line((sx, Hh - m - 20, sx + d * 40, Hh - m - 20), fill=gris, width=4)
        dr.line((sx, Hh - m - 20, sx, Hh - m - 60), fill=gris, width=4)
    f = _fuente(20)
    dr.text((W - m - 170, Hh - m - 40), 'SCHOTT CERAN', font=f, fill=gris)
    im.save(ruta)


def build():
    inox = L.mat_inox()
    negro = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    vitro = L.mat_vitroceramica()
    goma = L.mat_goma()

    # --- cuerpo: cajon de inox con cantos de plegado (r 2 mm)
    cuerpo = L.caja('cuerpo', A, F, H_CUERPO, (0, 0, H_PATA), r=0.002, segs=3, mat=inox)
    # hueco del vidrio, 3 mm de profundidad, con 1 mm de junta alrededor
    corte = L.caja('corte vidrio', G_A + 0.002, G_F + 0.002, 0.010, (0, G_Y, H - 0.003), r=0.004)
    L.sustraer(cuerpo, corte)
    # junta negra en el fondo del hueco (se ve como linea fina alrededor)
    L.caja('junta vidrio', G_A + 0.002, G_F + 0.002, 0.0015, (0, G_Y, H - 0.003), mat=goma, suave=False)
    # vidrio 1 mm por debajo del marco
    L.caja('vidrio', G_A, G_F, 0.0015, (0, G_Y, H - 0.0025), r=0.0006, segs=2, mat=vitro)
    # serigrafia del vidrio
    ruta = os.path.join(L.CALCAS_DIR, 'K1_vidrio.png')
    calca_vidrio(ruta)
    L.calca('K1 vidrio', ruta, G_A, G_F, (0, G_Y, H - 0.001 + 0.0002), normal='+Z')
    # las zonas radiantes no se ven con el aparato apagado: solo la
    # serigrafia (anillo pequeno) las senala, como en las fotos.

    # --- frontal: ruletas con escala y logo
    for i, x in enumerate((-X_MANDO, X_MANDO)):
        P.mando_ruleta(f'mando {i + 1}', (x, -F / 2, Z_MANDO), d=D_MANDO, alto=0.020, mat=negro)
    ruta = os.path.join(L.CALCAS_DIR, 'K1_escala.png')
    calca_escala(ruta)
    for i, x in enumerate((-X_MANDO, X_MANDO)):
        L.calca(f'K1 escala {i + 1}', ruta, 0.070, 0.070, (x, -F / 2 - 0.0003, Z_MANDO), normal='-Y')
    ruta = os.path.join(L.CALCAS_DIR, 'K1_logo.png')
    calca_logo(ruta)
    L.calca('K1 logo', ruta, 0.080, 0.025, (0, -F / 2 - 0.0004, Z_MANDO), normal='-Y')

    # --- patas negras O 40 x 15, retranqueadas 50 de las esquinas
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        L.cilindro(f'pata {i + 1}', 0.020, H_PATA, (sx * (A / 2 - 0.050), sy * (F / 2 - 0.050), 0),
                   r=0.004, segs=48, mat=negro)

    # --- trasera (supuesto): rejilla de ventilacion baja y salida de cable
    P.rejilla_ranuras('rejilla trasera', (0.12, F / 2, H_PATA + 0.070), 0.22, 0.045, normal='+Y', paso=0.010, ranura=0.005)
    L.cilindro('prensaestopas', 0.010, 0.012, (-0.22, F / 2, H_PATA + 0.035), eje='Y', segs=32, r=0.002, mat=negro)
    P.cable('cable', (-0.22, F / 2 + 0.012, H_PATA + 0.035), largo=0.30, d=0.011)

    return dict(ignorar=('mando', 'cable', 'prensaestopas'))
