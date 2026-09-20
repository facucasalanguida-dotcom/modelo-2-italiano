# -*- coding: utf-8 -*-
"""
A6 · Estante mural de cartelas modelo compacto Fricosmos 011410,
1250 x 400 x 245 (dos unidades en la trasbarra: 2,50 en total).

Referencia: catalogo Fricosmos (tabla y croquis) y renders del mismo
modelo en otros tamanos. Todo inox satinado soldado en una pieza: bandeja
1250 x 400 con canto de doble pliegue de 35, peto trasero de 45 y dos
cartelas triangulares (165 de alto x 340 de fondo) con labio doblado en la
hipotenusa y tres taladros O 8 en la cara de pared, retranqueadas 70 de
los extremos. H = 245 es la altura total: cartela + canto + peto.

Origen: centro de la huella y z = 0 en la parte BAJA de las cartelas; la
pared en +Y (cara trasera del peto). Supuesto: peto 45, canto 35, cartela
retranqueada 70.
"""
import lib as L

A, F, H = 1.250, 0.400, 0.245
E_CANTO = 0.035
PETO_H = 0.045
CART_D, CART_E = 0.340, 0.0015
Y_PARED = F / 2


def build():
    inox = L.mat_inox()
    z_est = H - PETO_H - E_CANTO       # cara inferior del estante: el peto remata en H
    # bandeja con canto de doble pliegue: caja + vaciado inferior (canto de 35 hacia abajo)
    L.caja('estante', A, F, E_CANTO, (0, 0, z_est), r=0.002, segs=3, mat=inox)   # bloque macizo: se lee igual que el doble pliegue cerrado
    L.caja('peto', A, 0.0015, PETO_H, (0, Y_PARED - 0.00075, H - PETO_H), r=0.0006, segs=2, mat=inox)
    # cartelas: triangulo en el plano Y-Z extruido 1,5 mm en X, con labio en la hipotenusa
    for k, x in enumerate((-A / 2 + 0.070, A / 2 - 0.070)):
        pts = [(Y_PARED, 0.0), (Y_PARED, z_est), (Y_PARED - CART_D, z_est)]
        L.prisma_yz(f'cartela {k + 1}', pts, x - CART_E / 2, x + CART_E / 2, mat=inox)
        # labio de rigidez de 15 mm doblado en la hipotenusa
        import math
        largo = math.hypot(CART_D, z_est) - 0.012
        sx = -1 if k == 0 else 1
        lab = L.caja(f'cartela {k + 1} labio', 0.015, largo, 0.0015, (x + sx * (CART_E / 2 + 0.0075), Y_PARED - CART_D / 2, z_est / 2 - 0.0002), mat=inox, suave=False)
        L.girar_malla(lab, (x, Y_PARED - CART_D / 2, z_est / 2), 'X', -math.degrees(math.atan2(z_est, CART_D)))
        for j, z in enumerate((0.025, 0.080, 0.135)):
            L.sustraer(L.bpy.data.objects[f'cartela {k + 1}'], L.cilindro(f'taladro {k + 1}.{j + 1}', 0.004, 0.02, (x - 0.01, Y_PARED - 0.020, z), eje='X', segs=16))
    return dict(altura=1.60, vistas=[('34', -35, 20), ('frente', 0, 5), ('desde abajo', -30, -25), ('lateral', 90, 10)])
