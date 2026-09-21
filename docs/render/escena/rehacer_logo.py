#!/usr/bin/env python3
"""Rehace el vinilo del logo a partir del PDF 1:1 que hay en el repositorio.

El contenedor puede reiniciarse y llevarse el scratchpad. Esto lo reconstruye
sin depender de nada que no este versionado.

El PDF es una lamina de tinta sobre fondo crema. Como el vinilo va sobre la
pared azzurro, el crema se vuelve transparente -asi se ve el azul entre los
trazos, que es lo que hace un vinilo de corte- y el azul del rotulo se corta
en crema, porque contra la pared azzurro no se leeria.
"""
import os
import numpy as np
import pymupdf
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF = os.path.join(RAIZ, 'pared', 'Vinilo_CasaMargot_1a1.pdf')
SCRATCH = os.environ.get('CM_SCRATCH', '/tmp/claude-0/-home-user-modelo-2-italiano/'
                         '30d2763c-3169-519a-ac78-c5a47134634b/scratchpad')
SAL = os.path.join(SCRATCH, 'logo', 'casa_margot_recortado.png')

CREMA = np.array([239, 231, 216], np.float32)
AZUL = np.array([58, 106, 137], np.float32)

# El PDF esta a escala 1:1 y mide 3,35 x 3,90 m: a 300 ppp saldrian 40.000 px
# y mupdf se planta. A 24 ppp son 3.000 px de ancho, de sobra para 1,56 m.
pix = pymupdf.open(PDF)[0].get_pixmap(dpi=24, alpha=True)
a = np.asarray(Image.frombytes('RGBA', (pix.width, pix.height), pix.samples)).astype(np.float32)
rgb, al = a[..., :3].copy(), a[..., 3] / 255.0
tinta = np.clip((np.linalg.norm(rgb - CREMA, axis=2) - 12) / 26.0, 0, 1) * al
rgb[np.linalg.norm(rgb - AZUL, axis=2) < 70] = CREMA
ys, xs = np.where(tinta > 0.05)
im = Image.fromarray(np.dstack([rgb, tinta * 255]).astype(np.uint8), 'RGBA')
os.makedirs(os.path.dirname(SAL), exist_ok=True)
im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(SAL)
print('vinilo rehecho:', SAL)
