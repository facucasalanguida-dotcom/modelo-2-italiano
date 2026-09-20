# -*- coding: utf-8 -*-
"""
B2 · Barril (keg) de cerveza de acero inoxidable, O 320 x 600.
No es de Makro: diseno propio con la silueta de un keg DIN 50 L (Thielmann)
escalada al O 320 del plano, manteniendo las alturas absolutas de aros y
nervios: aro superior hueco de 76 con reborde enrollado y dos asas ranuradas
ovaladas pasantes, hombro concavo, cuerpo O 304 con dos nervios de rodadura
toroidales (a 40 % y 62 % de la altura desde arriba), aro inferior de 80 con
tres orificios de drenaje, tapa concava con cuello del fitting O 60 y tapon
de plastico negro O 50. Inox satinado industrial con cordones de soldadura.
Origen: centro, z = 0 en el apoyo.
"""
import math
import lib as L

D, H = 0.320, 0.600
R = D / 2


def build():
    inox = L.mat_inox_satinado()
    inox_c = L.mat_inox('INOX cuerpo keg', rug=0.30, aniso=0.6, huellas=0.10)
    negro = L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))

    # --- cuerpo de revolucion (r, z) de abajo arriba
    rb = R - 0.008                    # cuerpo cilindrico, 8 mm menor que los aros
    def nervio(z):                    # nervio de rodadura toroidal (6 mm de saliente)
        return [(rb, z - 0.016), (rb + 0.004, z - 0.011), (R - 0.002, z - 0.005), (R - 0.002, z + 0.005), (rb + 0.004, z + 0.011), (rb, z + 0.016)]
    perfil = [(0.0, 0.0), (R - 0.020, 0.0), (R - 0.004, 0.0), (R, 0.004), (R, 0.076), (R - 0.004, 0.080), (rb, 0.100)] + \
        nervio(0.228) + nervio(0.364) + \
        [(rb, 0.480), (R - 0.004, 0.520), (R, 0.524), (R, 0.596), (R - 0.002, 0.599), (R - 0.005, H), (R - 0.008, 0.599),
         (R - 0.008, H - 0.065), (0.120, H - 0.045), (0.060, H - 0.038), (0.030, H - 0.040)]   # aro superior hueco, hombro y domo
    cuerpo = L.perfil_revolucion('cuerpo', perfil, (0, 0, 0), segs=128, mat=inox_c, cerrar=True)
    # asas: dos ranuras ovaladas opuestas en el aro superior
    for k, ang in enumerate((90.0, 270.0)):
        a = math.radians(ang)
        c = (R * math.cos(a), R * math.sin(a), 0.548)
        ran = L.caja(f'asa {k + 1} ranura', 0.110, 0.030, 0.035, (c[0], c[1], c[2] - 0.0175), r_vert=0.017, segs=8)
        L.girar_malla(ran, (c[0], c[1], c[2]), 'Z', ang - 90.0)
        L.sustraer(cuerpo, ran)
    # orificios de drenaje en el aro inferior (radiales)
    for k in range(3):
        cil = L.cilindro(f'drenaje {k + 1}', 0.006, 0.040, (0, R - 0.035, 0.030), eje='Y', segs=16)
        L.girar_malla(cil, (0, 0, 0), 'Z', 30 + 120 * k)
        L.sustraer(cuerpo, cil)
    # cordones de soldadura (hombro y fondo): toros finos
    L.toro('soldadura superior', rb, 0.0012, (0, 0, 0.482), segs=128, segs_r=8, mat=inox)
    L.toro('soldadura inferior', rb, 0.0012, (0, 0, 0.098), segs=128, segs_r=8, mat=inox)
    # fitting central: cuello + anillo + tapon de plastico
    L.cilindro('fitting cuello', 0.030, 0.026, (0, 0, H - 0.040), segs=64, r=0.002, mat=inox)
    L.tubo('fitting anillo', 0.033, 0.026, 0.006, (0, 0, H - 0.019), segs=64, mat=inox)
    L.cilindro('fitting tapon', 0.025, 0.010, (0, 0, H - 0.016), segs=64, r=0.003, mat=negro)
    L.sustraer(L.bpy.data.objects['fitting tapon'], L.cilindro('fitting tapon hueco', 0.012, 0.010, (0, 0, H - 0.010), segs=32))
    return dict(ignorar=())
