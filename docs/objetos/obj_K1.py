# -*- coding: utf-8 -*-
"""
K1 · Placa de coccion Bartscher 2K6000 GLN (art. 104907), 700 x 455 x 120.

Referencia: ficha tecnica oficial de Bartscher y fotos de catalogo. Es una
vitroceramica radiante SCHOTT CERAN de dos zonas de 3 kW lado a lado (Makro
la titula "induccion", pero es este modelo: 2 x O 230, 6 kW, 400 V, 700 x
455 x 120). Visualmente: vidrio negro brillante embutido a ras en un marco de
inox cepillado, frontal de 105 mm con dos ruletas negras (disco plano O 48
con digitos blancos 0-10 en sentido antihorario y casquete O 38 con
indicador blanco) en el tercio alto del frontal, punto indice fijo sobre
cada ruleta, placa plateada Bartscher centrada, cuatro patas negras O 40 x 15.

Confirmado: medidas exteriores, vidrio 650 de ancho, 2 zonas O 230 con
centros a 200 de los laterales, ruletas a 55 de los laterales, patas
retranqueadas 50. Supuesto (marcado como tal): fondo del vidrio 405 y
ruletas a z = 80 (por proporcion de la foto oficial), rejilla de
ventilacion trasera y salida del cable.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

TAG = 'K1'
A, F, H = 0.700, 0.455, 0.120          # ancho, fondo, alto (ficha oficial)
H_PATA = 0.015                         # patas negras O 40
H_CUERPO = H - H_PATA                  # 105 mm de frontal
G_A, G_F = 0.650, 0.405                # vidrio (ancho confirmado, fondo por foto)
M_LADO, M_TRAS = 0.025, 0.020          # marcos laterales y trasero
G_Y = F / 2 - M_TRAS - G_F / 2         # centro del vidrio en Y
ZONA_X = 0.150                         # centros de zona a 200 de los laterales
D_ZONA = 0.230
D_MANDO = 0.040
X_MANDO = A / 2 - 0.055
Z_MANDO = 0.080                        # centro de las ruletas (foto: 37 bajo el canto)
Z_LOGO = H_PATA + H_CUERPO / 2 - 0.004  # placa a media altura


def _fuente(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_escala(ruta):
    """Digitos blancos 0-10 sobre el disco negro de la ruleta: 0 arriba y
    1..10 en sentido ANTIHORARIO (paso 27 grados), sin rayas, como en la foto.
    Fondo transparente. 48 x 48 mm -> 700 px."""
    import math
    S = 700
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    f = _fuente(50, True)
    R = 306                              # 21 mm
    for i in range(11):
        ang = math.radians(-90 - 27 * i)
        x, y = S / 2 + R * math.cos(ang), S / 2 + R * math.sin(ang)
        t = str(i)
        bb = dr.textbbox((0, 0), t, font=f)
        dr.text((x - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), t, font=f, fill=(235, 235, 232, 255))
    im.save(ruta)


def calca_logo(ruta):
    """Placa plateada con 'Bartscher' en negro: 80 x 25 mm -> 800 x 250."""
    W, Hh = 800, 250
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((2, 2, W - 3, Hh - 3), radius=28, fill=(170, 172, 176, 255), outline=(120, 122, 126, 255), width=3)
    f = _fuente(150, True)
    t = 'Bartscher'
    bb = dr.textbbox((0, 0), t, font=f)
    dr.text(((W - (bb[2] - bb[0])) / 2 - bb[0], (Hh - (bb[3] - bb[1])) / 2 - bb[1]), t, font=f, fill=(25, 25, 28, 255))
    im.save(ruta)


def calca_vidrio(ruta):
    """Serigrafia del vidrio: rectangulo perimetral de esquinas redondeadas
    (trazo 4,5 mm centrado a 12 mm del borde), anillo O 55 en cada zona
    (trazo 5), marcas en L en las esquinas delanteras y 'SCHOTT CERAN'
    vertical en la esquina trasera derecha. 650 x 405 mm -> 2 px / mm."""
    W, Hh = int(G_A * 2000), int(G_F * 2000)
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    gris = (175, 178, 180, 235)
    m = 24
    dr.rounded_rectangle((m, m, W - m, Hh - m), radius=40, outline=gris, width=9)
    for cx in (W / 2 - ZONA_X * 2000, W / 2 + ZONA_X * 2000):
        cy = Hh / 2
        r = 55 / 2 * 2
        dr.ellipse((cx - r, cy - r, cx + r, cy + r), outline=gris, width=10)
    # marcas en L en las esquinas delanteras (la delantera es la de abajo: -Y)
    for sx in (m + 20, W - m - 20):
        d = 1 if sx < W / 2 else -1
        dr.line((sx, Hh - m - 20, sx + d * 40, Hh - m - 20), fill=gris, width=6)
        dr.line((sx, Hh - m - 20, sx, Hh - m - 36), fill=gris, width=6)
    # 'SCHOTT CERAN' girado 90 grados (se lee de abajo arriba), atras a la derecha
    f = _fuente(20)
    bb = dr.textbbox((0, 0), 'SCHOTT CERAN', font=f)
    tw, th = bb[2] - bb[0] + 4, bb[3] - bb[1] + 4
    tim = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(tim).text((-bb[0] + 2, -bb[1] + 2), 'SCHOTT CERAN', font=f, fill=gris)
    tim = tim.rotate(90, expand=True)
    im.paste(tim, (W - m - 30 - tim.width, m + 40), tim)
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
    blanco = L.mat_plastico('Plastico blanco', (0.85, 0.85, 0.82))
    ruta = os.path.join(L.CALCAS_DIR, 'K1_escala.png')
    calca_escala(ruta)
    for i, x in enumerate((-X_MANDO, X_MANDO)):
        # disco plano O 48 x 3 con los digitos, casquete O 38 x 17 con indicador blanco 8 x 22
        L.cilindro(f'mando {i + 1} disco', 0.024, 0.003, (x, -F / 2 - 0.003, Z_MANDO), eje='Y', r=0.001, segs=64, mat=negro)
        L.calca(f'mando {i + 1} escala', ruta, 0.048, 0.048, (x, -F / 2 - 0.0033, Z_MANDO), normal='-Y')
        P.mando_ruleta(f'mando {i + 1}', (x, -F / 2 - 0.003, Z_MANDO), d=0.038, alto=0.017, mat=negro, faldon=False, marca=False)
        L.caja(f'mando {i + 1} indicador', 0.008, 0.0006, 0.022, (x, -F / 2 - 0.0203, Z_MANDO - 0.006), mat=blanco, suave=False)
        # punto indice fijo en el panel, 6 mm sobre el disco
        L.cilindro(f'mando {i + 1} indice', 0.001, 0.0004, (x, -F / 2 - 0.0004, Z_MANDO + 0.030), eje='Y', segs=16, mat=blanco)
    ruta = os.path.join(L.CALCAS_DIR, 'K1_logo.png')
    calca_logo(ruta)
    L.calca('K1 logo', ruta, 0.080, 0.025, (0, -F / 2 - 0.0004, Z_LOGO), normal='-Y')

    # --- patas negras O 40 x 15, retranqueadas 50 de las esquinas
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        L.cilindro(f'pata {i + 1}', 0.020, H_PATA, (sx * (A / 2 - 0.050), sy * (F / 2 - 0.050), 0),
                   r=0.004, segs=48, mat=negro)

    # --- trasera (supuesto): rejilla de ventilacion baja y salida de cable
    P.rejilla_ranuras('rejilla trasera', (0.12, F / 2, H_PATA + 0.070), 0.22, 0.045, normal='+Y', paso=0.010, ranura=0.005, cuerpo=cuerpo)
    L.cilindro('prensaestopas', 0.010, 0.012, (-0.22, F / 2, H_PATA + 0.035), eje='Y', segs=32, r=0.002, mat=negro)
    P.cable('cable', (-0.22, F / 2 + 0.012, H_PATA + 0.035), largo=0.30, d=0.011)

    return dict(ignorar=('mando', 'cable', 'prensaestopas'))
