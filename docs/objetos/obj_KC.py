# -*- coding: utf-8 -*-
"""
KC · Campana mural recta sin turbina Gavinox CMRMS2012, 2000 x 1200 x 500.

Referencia: renders y planos acotados del fabricante (Gavinox / Mi
Mobiliario Hosteleria, mismo texto que Makro). AISI-304 satinado de 0,8 mm en
frontal, laterales, canal y marcos; techo y trasera galvanizados. Cuatro
filtros de lamas de 490 x 490 x 50 en un plano inclinado a 45 grados que
arranca a 130 mm de la pared (canal recogegrasas trasero) y sube hacia el
frente; canal perimetral inferior con valvula de desague inox centrada en el
frente. Sin turbina, sin luz, sin logos.

El origen esta en el centro de la huella y z = 0 es el borde INFERIOR de la
campana (en el plano va a +2,00). La pared queda en +Y.
Supuesto: boca de salida en el techo (500 x 300 sobre el plenum), asas de
varilla en los filtros, alto del canal (30 mm).
"""
import math
import lib as L

A, F, H = 2.000, 1.200, 0.500
E = 0.0015                       # chapa (0,8 real; 1,5 para que renderice limpio)
CANAL_A, CANAL_H = 0.045, 0.030  # canal recogegrasas perimetral
Y_PARED = F / 2                  # +0,60
Y_FRENTE = -F / 2
FILTRO = 0.490                   # filtros 490 x 490 x 50
E_FILTRO = 0.050
Y_ARRANQUE = Y_PARED - 0.130     # arranque del plano de filtros (a 130 de la pared)
Z_ARRANQUE = 0.035
ANG = 45.0                       # inclinacion del plano de filtros


def build():
    inox = L.mat_inox_satinado()
    inox_p = L.mat_inox_pulido()
    galva = L.mat_aluminio('Galvanizado', rug=0.55, color=(0.50, 0.51, 0.52))

    # --- caja: frontal, laterales, techo, trasera
    L.caja('frontal', A, E, H, (0, Y_FRENTE + E / 2, 0), r=0.0006, segs=2, mat=inox)
    L.caja('lateral izquierdo', E, F, H, (-A / 2 + E / 2, 0, 0), r=0.0006, segs=2, mat=inox)
    L.caja('lateral derecho', E, F, H, (A / 2 - E / 2, 0, 0), r=0.0006, segs=2, mat=inox)
    L.caja('techo', A, F, E, (0, 0, H - E), mat=galva, suave=False)
    L.caja('trasera', A, E, H, (0, Y_PARED - E / 2, 0), mat=galva, suave=False)
    # boca de salida en el techo (supuesta): collar rectangular sobre el plenum
    collar = L.caja('boca de salida', 0.500, 0.300, 0.040, (0, Y_PARED - 0.30, H), r=0.002, mat=galva)
    L.sustraer(collar, L.caja('boca hueco', 0.480, 0.280, 0.10, (0, Y_PARED - 0.30, H - 0.03)))

    # --- canal recogegrasas perimetral (frente y laterales): fondo + labio interior
    L.caja('canal frente', A, CANAL_A, E, (0, Y_FRENTE + CANAL_A / 2, 0), mat=inox, suave=False)
    L.caja('canal frente labio', A, E, CANAL_H, (0, Y_FRENTE + CANAL_A - E / 2, 0), r=0.0006, segs=2, mat=inox)
    for nm, sx in (('izquierdo', -1), ('derecho', 1)):
        L.caja(f'canal {nm}', CANAL_A, F, E, (sx * (A / 2 - CANAL_A / 2), 0, 0), mat=inox, suave=False)
        L.caja(f'canal {nm} labio', E, F, CANAL_H, (sx * (A / 2 - CANAL_A + E / 2), 0, 0), r=0.0006, segs=2, mat=inox)
    # canal trasero: fondo de 130 hasta la pared, donde apoyan los filtros
    L.caja('canal trasero', A, 0.130, E, (0, Y_PARED - 0.065, 0), mat=inox, suave=False)
    L.caja('canal trasero labio', A, E, Z_ARRANQUE, (0, Y_ARRANQUE + E / 2, 0), r=0.0006, segs=2, mat=inox)
    # valvula de desague en el centro del frente, colgando del canal
    L.cilindro('desague cuerpo', 0.010, 0.030, (0, Y_FRENTE + 0.022, -0.030), segs=32, r=0.002, mat=inox_p)
    L.cilindro('desague maneta', 0.003, 0.035, (0, Y_FRENTE + 0.022, -0.018), eje='Y', segs=16, r=0.001, mat=inox_p)
    L.cilindro('desague tapon', 0.008, 0.006, (0, Y_FRENTE + 0.022, -0.036), segs=32, r=0.002, mat=inox_p)

    # --- plano inclinado: filtros (490 de desarrollo) + chapa de plenum hasta el techo
    s, c = math.sin(math.radians(ANG)), math.cos(math.radians(ANG))
    # chapa galvanizada del plenum, por encima de los filtros hasta el techo
    largo_plenum = (H - Z_ARRANQUE) / s - FILTRO
    y_fin_filtro, z_fin_filtro = Y_ARRANQUE - FILTRO * c, Z_ARRANQUE + FILTRO * s
    pl = L.caja('plenum', A - 2 * E, largo_plenum, E, (0, y_fin_filtro - largo_plenum / 2, z_fin_filtro), mat=galva, suave=False)
    L.girar_malla(pl, (0, y_fin_filtro, z_fin_filtro), 'X', -ANG)
    # perfiles en U arriba y abajo del plano de filtros (guias)
    for nm, y0, z0 in (('guia inferior', Y_ARRANQUE, Z_ARRANQUE), ('guia superior', y_fin_filtro, z_fin_filtro)):
        g = L.caja(nm, A - 2 * E, 0.030, 0.012, (0, y0 - 0.015, z0 - 0.006), r=0.001, segs=2, mat=inox)
        L.girar_malla(g, (0, y0, z0), 'X', -ANG)

    # --- cuatro filtros de lamas 490 x 490 x 50, sobre el plano inclinado.
    # Cada filtro se construye plano, con su espesor centrado en el plano de
    # filtros (z = Z_ARRANQUE +- 25) y su desarrollo hacia -Y desde el borde
    # de arranque; luego se gira -45 grados alrededor de ese borde, con lo que
    # sube hacia el frente igual que la chapa del plenum.
    n_lamas = 21
    m = 0.015
    paso = (FILTRO - 2 * m) / n_lamas
    z0 = Z_ARRANQUE - E_FILTRO / 2
    for k in range(4):
        xc = -1.5 * (FILTRO + 0.005) + k * (FILTRO + 0.005)
        yc = Y_ARRANQUE - FILTRO / 2
        piezas = [
            L.caja(f'filtro {k + 1} marco inf', FILTRO, m, E_FILTRO, (xc, Y_ARRANQUE - m / 2, z0), r=0.001, segs=2, mat=inox),
            L.caja(f'filtro {k + 1} marco sup', FILTRO, m, E_FILTRO, (xc, Y_ARRANQUE - FILTRO + m / 2, z0), r=0.001, segs=2, mat=inox),
            L.caja(f'filtro {k + 1} marco izq', m, FILTRO - 2 * m, E_FILTRO, (xc - FILTRO / 2 + m / 2, yc, z0), r=0.001, segs=2, mat=inox),
            L.caja(f'filtro {k + 1} marco der', m, FILTRO - 2 * m, E_FILTRO, (xc + FILTRO / 2 - m / 2, yc, z0), r=0.001, segs=2, mat=inox),
        ]
        # lamas en V: dos capas de chapas inclinadas alternas que recorren el
        # filtro de abajo arriba (perpendiculares al frente de la campana)
        for i in range(n_lamas):
            x = xc - (FILTRO - 2 * m) / 2 + paso * (i + 0.5)
            for capa, (dz, ang, dx) in enumerate(((0.012, 35, -paso * 0.22), (0.032, -35, paso * 0.22))):
                lama = L.caja(f'filtro {k + 1} lama {i + 1}.{capa + 1}', 0.0008, FILTRO - 2 * m - 0.004, 0.016,
                              (x + dx, yc, z0 + dz), mat=inox_p, suave=False)
                L.girar_malla(lama, (x + dx, yc, z0 + dz + 0.008), 'Y', ang)
                piezas.append(lama)
        # asa de varilla en la cara vista (la de abajo), cerca del borde inferior
        piezas.append(L.tubo_curva(f'filtro {k + 1} asa',
                                   [(xc - 0.05, Y_ARRANQUE - 0.07, z0), (xc - 0.05, Y_ARRANQUE - 0.07, z0 - 0.022),
                                    (xc + 0.05, Y_ARRANQUE - 0.07, z0 - 0.022), (xc + 0.05, Y_ARRANQUE - 0.07, z0)],
                                   0.003, segs=12, mat=inox_p, suavizar=False))
        for ob in piezas:
            L.girar_malla(ob, (0, Y_ARRANQUE, Z_ARRANQUE), 'X', -ANG)

    # la campana va colgada a +2,00: las vistas se hacen desde abajo
    return dict(ignorar=('desague', 'boca de salida'), altura=2.0,
                vistas=[('34 desde abajo', -35, -22), ('frente desde abajo', 0, -30),
                        ('lateral', 90, -10), ('trasera-superior', 150, 25)])
