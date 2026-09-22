#!/usr/bin/env python3
"""Rehace el vinilo del logo desde el PDF que hay en el repositorio.

El contenedor puede reiniciarse y llevarse el scratchpad; esto lo reconstruye
sin depender de ningun adjunto.

El PDF es el logo en negro sobre fondo transparente, que es justo lo que va
en la pared azzurro: el logo y nada mas, sin lamina, sin marco y sin fondo.
"""
import os
import numpy as np
import pymupdf
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF = os.path.join(RAIZ, 'pared', 'CASA_MARGOT_LOGO_NERO.pdf')
SCRATCH = os.environ.get('CM_SCRATCH', '/tmp/claude-0/-home-user-modelo-2-italiano/'
                         '30d2763c-3169-519a-ac78-c5a47134634b/scratchpad')
SAL = os.path.join(SCRATCH, 'logo', 'casa_margot_recortado.png')

# A 400 ppp el logo sale de ~7.000 px de ancho: el vinilo de la pared mide
# 1,56 m y en una foto a 4K puede ocupar 1.500 px o mas. A 120 salia de 2.097
# y los bordes de las letras se veian blandos.
pix = pymupdf.open(PDF)[0].get_pixmap(dpi=400, alpha=True)
im = Image.frombytes('RGBA', (pix.width, pix.height), pix.samples)
ys, xs = np.where(np.asarray(im)[..., 3] > 8)
os.makedirs(os.path.dirname(SAL), exist_ok=True)
im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(SAL)
print('vinilo rehecho:', SAL, Image.open(SAL).size)
