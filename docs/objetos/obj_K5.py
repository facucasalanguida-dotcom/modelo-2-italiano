# -*- coding: utf-8 -*-
"""
K5 · Horno de conveccion electrico de sobremesa, 4 bandejas 454 x 327,
590 x 595 x 575 (familia OEM YXD-8A / EB-8F / HEB-4F / Malka HCV6, vendido
en Makro por Osteleria).

Referencia: fotos de cuatro distribuidores con los mismos datos. Carcasa de
inox satinado con cantos vivos; puerta de marco negro con cristal doble
(ventana 430 x 330 con esquinas redondeadas) abatible hacia abajo, asa
tubular inox O 25 con tapones negros a lo largo de la parte alta; banda
superior con ranuras de ventilacion; panel de mandos inferior de 75 mm con
tres ruletas negras (TIME POWER, TOP HEATING, TEMPERATURE), cuatro pilotos
(verde/rojo, verde/rojo) y pulsador cromado STEAM; camara inox 460 x 380 x
360 con dos discos de ventilador perforados al fondo, cuatro niveles de
guias de varilla, lampara con cupula a la izquierda y resistencias del
grill bajo el techo; cuatro tacos negros.

La marca/serigrafia exacta de la unidad de Makro no esta confirmada: el
panel lleva los textos genericos de esta familia y ningun logotipo.
El fondo de 0,595 es hasta el frente de la puerta; el asa sobresale 35 mm y
se excluye del control de medidas.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import lib as L
import partes as P

A, F, H = 0.590, 0.595, 0.575
H_PIE = 0.022
Y_FRENTE, Y_TRAS = -F / 2, F / 2
Z_PANEL = H_PIE + 0.075            # techo de la banda de mandos: 0,097
PUERTA_W, PUERTA_H, PUERTA_E = 0.540, 0.430, 0.030
Z_PUERTA0 = Z_PANEL
VENT_W, VENT_H = 0.430, 0.330      # ventana de cristal
CAM_W, CAM_D, CAM_H = 0.460, 0.380, 0.360
Z_CAM0 = 0.115


def _f(px, negrita=False):
    n = 'DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + n, px)


def calca_panel(ruta):
    """Textos del panel a 4 px/mm (590 x 75 mm), mas las escalas de las
    tres ruletas."""
    import math
    W, Hh = int(A * 4000), int(0.075 * 4000)
    im = Image.new('RGBA', (W, Hh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    negro = (25, 25, 27, 255)
    f = _f(22)

    def px(x, z):
        return (W / 2 + x * 4000, Hh - (z - H_PIE) * 4000)

    for t, x, z in (('TIME POWER', -0.235, 0.070), ('POWER LIGHT', -0.135, 0.062), ('HOT LIGHT', -0.085, 0.062),
                    ('TOP HEATING', 0.045, 0.062), ('STEAM LIGHT', 0.095, 0.062), ('STEAM', 0.13, 0.062),
                    ('HOT LIGHT', 0.165, 0.062), ('TEMPERATURE', 0.245, 0.048)):
        bb = dr.textbbox((0, 0), t, font=f)
        x0, y0 = px(x, z)
        dr.text((x0 - (bb[2] - bb[0]) / 2 - bb[0], y0 - bb[1]), t, font=f, fill=negro)
    # escalas: marcas radiales alrededor de cada ruleta
    for x, n in ((-0.200, 12), (0.010, 10), (0.210, 12)):
        cx, cy = px(x, 0.045)
        for i in range(n):
            a = math.radians(-225 + i * (270 / (n - 1)))
            r1, r2 = 0.026 * 4000, 0.030 * 4000
            dr.line((cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + r2 * math.cos(a), cy + r2 * math.sin(a)), fill=negro, width=4)
    im.save(ruta)


def build():
    inox = L.mat_inox()
    inox_p = L.mat_inox_pulido()
    negro = L.mat_chapa('Chapa negra satinada', (0.02, 0.02, 0.02), rug=0.45, brillo=0.15)
    plast = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    vidrio = L.mat_vidrio('Vidrio de horno', tinte=(0.55, 0.58, 0.56))
    cromo = L.mat_cromo()
    perf = L.mat_chapa_perforada('Tapa de ventilador', d=0.006, paso=0.012)

    # --- tacos y cuerpo
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        L.cilindro(f'taco {i + 1}', 0.0175, H_PIE, (sx * (A / 2 - 0.040), sy * (F / 2 - 0.040), 0), r=0.004, segs=40, mat=plast)
    cuerpo = L.caja('cuerpo', A, F, H - H_PIE, (0, 0, H_PIE), r=0.002, segs=3, mat=inox)
    # hueco de la puerta (retranqueo de 30 mm en el frente) y camara
    L.sustraer(cuerpo, L.caja('hueco puerta', PUERTA_W + 0.004, PUERTA_E + 0.002, PUERTA_H + 0.004,
                              (0, Y_FRENTE + PUERTA_E / 2 - 0.001, Z_PUERTA0 - 0.002)))
    L.sustraer(cuerpo, L.caja('camara', CAM_W, CAM_D + 0.05, CAM_H, (0, Y_FRENTE + PUERTA_E + CAM_D / 2 - 0.025, Z_CAM0), r_vert=0.012, r=0.012, segs=4))
    # ranuras de ventilacion en la tapa, sobre la puerta
    for i in range(6):
        L.sustraer(cuerpo, L.caja(f'ranura {i + 1}', 0.040, 0.008, 0.02, (-0.125 + i * 0.050, Y_FRENTE + 0.018, H - 0.01), r=0.002))

    # --- puerta: marco negro con ventana redondeada, cristal exterior e interior
    puerta = L.caja('puerta', PUERTA_W, PUERTA_E, PUERTA_H, (0, Y_FRENTE + PUERTA_E / 2, Z_PUERTA0), r=0.003, segs=3, mat=negro)
    zc = Z_PUERTA0 + PUERTA_H / 2
    L.sustraer(puerta, L.caja('ventana', VENT_W, 0.10, VENT_H, (0, Y_FRENTE + PUERTA_E / 2, zc - VENT_H / 2), r_vert=0.0, r=0.0, segs=2))
    for nm, y in (('cristal exterior', Y_FRENTE + 0.004), ('cristal interior', Y_FRENTE + PUERTA_E - 0.004)):
        L.caja(nm, VENT_W + 0.02, 0.004, VENT_H + 0.02, (0, y, zc - VENT_H / 2 - 0.01), mat=vidrio, suave=False)
    # asa tubular O 25 con tapones negros, sobre dos soportes
    za = Z_PUERTA0 + PUERTA_H - 0.045
    ya = Y_FRENTE - 0.035
    L.cilindro('asa', 0.0125, 0.500, (-0.250, ya, za), eje='X', segs=40, mat=inox_p)
    for i, x in enumerate((-0.250, 0.250)):
        L.cilindro(f'asa tapon {i + 1}', 0.013, 0.012, (x - (0.012 if x < 0 else 0), ya, za), eje='X', segs=32, r=0.003, mat=plast)
        L.cilindro(f'asa soporte {i + 1}', 0.009, 0.035, (x * 0.88, Y_FRENTE - 0.035, za), eje='Y', segs=24, mat=inox_p)
    # bisagras abajo (dos pletinas) y cierre
    for i, x in enumerate((-0.24, 0.24)):
        L.caja(f'bisagra {i + 1}', 0.030, 0.012, 0.020, (x, Y_FRENTE + 0.006, Z_PUERTA0 - 0.008), r=0.002, segs=2, mat=inox_p)

    # --- interior de la camara
    y0 = Y_FRENTE + PUERTA_E                     # plano de entrada
    y_fondo = y0 + CAM_D
    for k in range(4):
        z = Z_CAM0 + 0.045 + k * 0.070
        for sx in (-1, 1):
            x = sx * (CAM_W / 2 - 0.008)
            L.cilindro(f'guia {k + 1}{"i" if sx < 0 else "d"} a', 0.003, CAM_D - 0.06, (x, y0 + 0.03, z), eje='Y', segs=12, mat=inox_p)
            L.cilindro(f'guia {k + 1}{"i" if sx < 0 else "d"} b', 0.003, CAM_D - 0.06, (x - sx * 0.020, y0 + 0.03, z), eje='Y', segs=12, mat=inox_p)
    for i, x in enumerate((-0.11, 0.11)):
        L.cilindro(f'ventilador {i + 1}', 0.075, 0.003, (x, y_fondo - 0.004, Z_CAM0 + CAM_H / 2), eje='Y', segs=64, mat=perf)
        L.cilindro(f'ventilador {i + 1} aro', 0.080, 0.006, (x, y_fondo - 0.007, Z_CAM0 + CAM_H / 2), eje='Y', segs=64, r=0.001, mat=inox_p)
    L.cilindro('lampara', 0.020, 0.030, (-CAM_W / 2 + 0.0, y0 + 0.10, Z_CAM0 + 0.26), eje='X', segs=32, r=0.008,
               mat=L.mat_vidrio('Tulipa', tinte=(0.98, 0.98, 0.96), rug=0.15))
    for i, x in enumerate((-0.12, 0.0, 0.12)):
        L.cilindro(f'grill {i + 1}', 0.004, CAM_D - 0.05, (x, y0 + 0.025, Z_CAM0 + CAM_H - 0.018), eje='Y', segs=16,
                   mat=L.mat_plastico('Resistencia negra', (0.03, 0.03, 0.03), rug=0.6))
    # dos bandejas inox en los niveles 2 y 3
    for k in (1, 2):
        z = Z_CAM0 + 0.045 + k * 0.070 + 0.004
        b = L.caja(f'bandeja {k + 1}', 0.454, 0.327, 0.018, (0, y0 + 0.03 + 0.327 / 2, z), r=0.002, segs=2, mat=inox_p)
        L.sustraer(b, L.caja(f'bandeja {k + 1} hueco', 0.454 - 0.003, 0.327 - 0.003, 0.03, (0, y0 + 0.03 + 0.327 / 2, z + 0.0012)))

    # --- panel de mandos (banda inferior)
    ruta = os.path.join(L.CALCAS_DIR, 'K5_panel.png')
    calca_panel(ruta)
    L.calca('K5 panel', ruta, A - 0.004, 0.075 - 0.002, (0, Y_FRENTE - 0.0003, H_PIE + 0.0375), normal='-Y')
    zk = H_PIE + 0.045
    for nm, x in (('mando tiempo', -0.200), ('mando grill', 0.010), ('mando temperatura', 0.210)):
        P.mando_ruleta(nm, (x, Y_FRENTE, zk), d=0.040, alto=0.020, mat=plast)
    for nm, x, col in (('piloto verde 1', -0.135, (0.1, 1.0, 0.2)), ('piloto rojo 1', -0.085, (1.0, 0.05, 0.02)),
                       ('piloto verde 2', 0.095, (0.1, 1.0, 0.2)), ('piloto rojo 2', 0.165, (1.0, 0.05, 0.02))):
        P.piloto(nm, (x, Y_FRENTE, zk), d=0.010, color=col)
        L.cilindro(nm + ' aro', 0.0075, 0.003, (x, Y_FRENTE - 0.003, zk), eje='Y', segs=32, r=0.001, mat=plast)
    P.boton('pulsador vapor', (0.130, Y_FRENTE, zk), d=0.012, alto=0.006, mat=cromo)

    # --- trasera: cable y toma de agua
    L.cilindro('prensaestopas', 0.009, 0.010, (-0.20, Y_TRAS, 0.12), eje='Y', segs=24, r=0.002, mat=plast)
    P.cable('cable', (-0.20, Y_TRAS + 0.010, 0.12), largo=0.30, d=0.010)
    L.cilindro('toma de agua', 0.012, 0.015, (0.20, Y_TRAS, 0.15), eje='Y', segs=24, r=0.002, mat=cromo)

    return dict(ignorar=('asa', 'cable', 'prensaestopas', 'toma de agua', 'mando', 'piloto', 'pulsador'))
