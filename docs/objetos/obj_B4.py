# -*- coding: utf-8 -*-
"""
B4 · Columna tirador completa en "T" de 3 grifos con bandeja 40 x 40,
400 x 400 x 550 (pack columna T de Install Beer, mismo producto que Makro).

Referencia: 9 fotos del pack (columna sola, con grifos, con medallones y
frontal del pack de 3 grifos). Tubo vertical y horizontal de inox satinado
O 76 (3"), tapas planas rehundidas con tornillo central en los extremos,
pletina de registro sobre el lomo con un tornillo en cada punta; tres
grifos de laton cromado (tuerca moleteada, cuello, bola O 40 con tapon
frontal, cano recto O 8 hacia abajo) separados 120 entre ejes, con maneta
de plastico negro brillante en gota sobre casquillo cromado moleteado,
inclinada 10 grados hacia atras; tres medallones cromados O 90 lisos sobre
soporte de varilla; bandeja inox 400 x 400 x 40 con reborde de 10 y
rejilla extraible de inox brillante 300 x 178 con ranuras en tres columnas
y agujero O 95 para el aclarador de vasos (no incluido, como en la foto).

Confirmado: bandeja 400 x 400, disposicion, materiales, forma de grifos y
manetas, medallones (fotos del fabricante). Supuesto: O 76 de los tubos,
altura del eje (413) para que la maneta remate en 550, largo del tubo 390.
La rejilla se modela SIN el film azul de proteccion.
"""
import math
import lib as L

A, F, H = 0.400, 0.400, 0.550
R_TUBO = 0.038
Y_COL = 0.090                                  # eje de la columna (mitad trasera)
L_TUBO = 0.390
INCL = 10.0                                    # inclinacion de la maneta hacia atras
Z_EJE = H - 0.038 - 0.100 * math.cos(math.radians(INCL))   # 0,4135: la maneta remata en H
X_GRIFOS = (-0.120, 0.0, 0.120)
H_BANDEJA = 0.040
Z_PLACA = H_BANDEJA - 0.008                    # placa superior de la bandeja, 8 bajo el reborde


def build():
    inox = L.mat_inox()
    inox_s = L.mat_inox_satinado()
    inox_p = L.mat_inox_pulido()
    cromo = L.mat_cromo()
    negro = L.mat_plastico('Plastico negro brillante', (0.01, 0.01, 0.011), rug=0.16, brillo=0.5)
    y_frente = Y_COL - R_TUBO                  # cara frontal del tubo horizontal (+0,052)

    # --- bandeja 400 x 400 x 40: reborde de 10, placa 8 mas baja, hueco de la rejilla
    ban = L.caja('bandeja', A, F, H_BANDEJA, (0, 0, 0), r=0.0015, segs=3, mat=inox)
    L.sustraer(ban, L.caja('bandeja rebaje', A - 0.020, F - 0.020, 0.020, (0, 0, Z_PLACA), r_vert=0.006))
    GX, GY, GW, GD = 0.0, -0.096, 0.300, 0.178
    L.sustraer(ban, L.caja('bandeja hueco rejilla', GW + 0.003, GD + 0.003, 0.028, (GX, GY, Z_PLACA - 0.026), r_vert=0.012))
    # rejilla: placa de 1,5 con ranuras (3 columnas x 13 filas), agujero O 95 y taladro O 10
    rej = L.caja('rejilla', GW, GD, 0.0015, (GX, GY, Z_PLACA - 0.0035), r_vert=0.011, mat=inox_p, suave=False)
    cortes = []
    for col in range(3):
        xc = GX - GW / 2 + 0.024 + 0.040 * col
        for fila in range(13):
            yc = GY - GD / 2 + 0.024 + 0.011 * fila
            cortes.append(L.caja(f'ranura {col}.{fila}', 0.032, 0.0045, 0.01, (xc, yc, Z_PLACA - 0.008), r_vert=0.002))
    cortes.append(L.cilindro('agujero aclarador', 0.0475, 0.01, (GX + GW / 2 - 0.068, GY, Z_PLACA - 0.008), segs=64))
    cortes.append(L.cilindro('taladro', 0.005, 0.01, (GX + GW / 2 - 0.016, GY + GD / 2 - 0.016, Z_PLACA - 0.008), segs=24))
    cortes.append(L.cilindro('taladro 2', 0.005, 0.01, (GX - GW / 2 + 0.012, GY - GD / 2 + 0.012, Z_PLACA - 0.008), segs=24))
    L.sustraer(rej, L.unir('rejilla cortes', cortes))

    # --- columna: tubo vertical y tubo horizontal con tapas rehundidas y pletina de registro
    L.cilindro('tubo vertical', R_TUBO, Z_EJE - 0.020, (0, Y_COL, 0.020), segs=96, mat=inox_s)
    th = L.cilindro('tubo horizontal', R_TUBO, L_TUBO, (-L_TUBO / 2, Y_COL, Z_EJE), eje='X', segs=96, mat=inox_s)
    for k, sx in enumerate((-1, 1)):
        x_ext = sx * L_TUBO / 2
        L.sustraer(th, L.cilindro(f'tapa hueco {k + 1}', R_TUBO - 0.0025, 0.006, (x_ext - (0.005 if sx > 0 else 0.001), Y_COL, Z_EJE), eje='X', segs=96))
        L.cilindro(f'tapa {k + 1}', R_TUBO - 0.0027, 0.002, (x_ext - (0.007 if sx > 0 else -0.005), Y_COL, Z_EJE), eje='X', segs=96, mat=inox_s)
        L.cilindro(f'tapa {k + 1} tornillo', 0.004, 0.0015, (x_ext - (0.005 if sx > 0 else -0.0035), Y_COL, Z_EJE), eje='X', segs=24, r=0.0005, mat=inox_p)
    L.caja('pletina', 0.340, 0.020, 0.0025, (0, Y_COL, Z_EJE + R_TUBO - 0.0015), r=0.0005, segs=2, mat=inox_s)
    for k, x in enumerate((-0.160, 0.160)):
        L.cilindro(f'pletina tornillo {k + 1}', 0.003, 0.001, (x, Y_COL, Z_EJE + R_TUBO + 0.001), segs=24, r=0.0004, mat=inox_p)

    # --- tres grifos cromados con maneta negra, y tres medallones
    for k, x in enumerate(X_GRIFOS):
        n = f'grifo {k + 1}'
        L.cilindro(n + ' tuerca', 0.014, 0.012, (x, y_frente - 0.010, Z_EJE), eje='Y', segs=48, r=0.001, mat=cromo)
        L.cilindro(n + ' cuello', 0.010, 0.014, (x, y_frente - 0.023, Z_EJE), eje='Y', segs=48, mat=cromo)
        yb = y_frente - 0.038                      # centro de la bola (+0,014)
        L.perfil_revolucion(n + ' bola', [(0.0, -0.020), (0.012, -0.016), (0.0185, -0.0075), (0.020, 0.0),
                                          (0.0185, 0.0075), (0.012, 0.016), (0.0, 0.020)],
                            (x, yb, Z_EJE), segs=64, mat=cromo)
        L.cilindro(n + ' tapon', 0.008, 0.003, (x, yb - 0.0215, Z_EJE), eje='Y', segs=32, r=0.0008, mat=cromo)
        L.cilindro(n + ' cano', 0.004, 0.096, (x, yb - 0.008, Z_EJE - 0.108), segs=32, r=0.0008, mat=cromo)
        # maneta: casquillo moleteado + gota de plastico negro, inclinada hacia atras
        L.cilindro(n + ' casquillo', 0.008, 0.020, (x, yb, Z_EJE + 0.018), segs=48, r=0.0008, mat=cromo)
        gota = L.perfil_revolucion(n + ' maneta', [(0.0065, 0.0), (0.0105, 0.018), (0.0125, 0.045), (0.0105, 0.072),
                                                  (0.006, 0.092), (0.0025, 0.0985), (0.0, 0.100)],
                                   (x, yb, Z_EJE + 0.038), segs=48, mat=negro)
        L.girar_malla(gota, (x, yb, Z_EJE + 0.038), 'X', -INCL)
        # medallon cromado O 90 sobre varilla, delante de la bola
        ym = -0.016
        L.cilindro(f'medallon {k + 1}', 0.045, 0.005, (x, ym - 0.0025, Z_EJE - 0.005), eje='Y', segs=96, r=0.0015, mat=cromo)
        L.cilindro(f'medallon {k + 1} varilla', 0.005, y_frente + 0.010 - ym, (x + 0.028, ym, Z_EJE + 0.025), eje='Y', segs=24, mat=cromo)
        L.cilindro(f'medallon {k + 1} brida', 0.012, 0.004, (x + 0.028, y_frente - 0.002, Z_EJE + 0.025), eje='Y', segs=32, r=0.0008, mat=cromo)
    return dict()
