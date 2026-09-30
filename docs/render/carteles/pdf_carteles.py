#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF de los carteles: portada con los cinco modelos, y por cada cartel una
pagina con sus seis acabados y despues cada acabado a pagina completa.

    python3 pdf_carteles.py [--carpeta DIR] [--salida Carteles_CasaMargot.pdf]

Lee los PNG que deja carteles.py (<cartel>_<acabado>.png). Cada imagen se
mete una sola vez y las paginas que la repiten la reutilizan, asi que el PDF
pesa lo que pesan las treinta fotos y nada mas.
"""
import argparse
import io
import os
import sys

import pymupdf
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, '..', 'escena'))
from rutas import SCRATCH   # noqa: E402

CARTELES = [('ovalo', 'Óvalo en bandera', 'letras en relieve'),
            ('caja', 'Caja de luz en bandera', 'logo en el costado y en la testa'),
            ('placa', 'Placa cuadrada', 'canto retroiluminado'),
            ('colgado', 'Caja de luz colgada', 'de un soporte en el pilar'),
            ('barra', 'Barra en la pared', 'logo calado y halo de luz')]
ACABADOS = [('blanco', 'Blanco'), ('marmol_blanco', 'Mármol blanco y oro'),
            ('negro', 'Negro'), ('marmol_negro', 'Mármol negro'),
            ('oro', 'Oro'), ('marmol_rosa', 'Mármol rosa')]

A4 = pymupdf.paper_rect('a4')
W, H = A4.width, A4.height
M = 36.0
TINTA = (0.08, 0.08, 0.08)
GRIS = (0.35, 0.35, 0.35)
AZZURRO = (0x12 / 255, 0xA0 / 255, 0xD7 / 255)
FUENTE = '/usr/share/fonts/truetype/liberation/LiberationSans-{}.ttf'


class Doc:
    def __init__(self, carpeta):
        self.d = pymupdf.open()
        self.carpeta = carpeta
        self.xref = {}

    def pagina(self):
        p = self.d.new_page(width=W, height=H)
        p.insert_font(fontname='R', fontfile=FUENTE.format('Regular'))
        p.insert_font(fontname='B', fontfile=FUENTE.format('Bold'))
        return p

    def imagen(self, p, cartel, acabado, rect):
        """La foto encajada en rect sin deformar; devuelve donde quedo."""
        ruta = os.path.join(self.carpeta, f'{cartel}_{acabado}.png')
        im = Image.open(ruta)
        k = min(rect.width / im.width, rect.height / im.height)
        w, h = im.width * k, im.height * k
        r = pymupdf.Rect(rect.x0 + (rect.width - w) / 2, rect.y0,
                         rect.x0 + (rect.width + w) / 2, rect.y0 + h)
        if ruta in self.xref:
            p.insert_image(r, xref=self.xref[ruta])
        else:
            b = io.BytesIO()
            im.convert('RGB').save(b, 'JPEG', quality=88)
            self.xref[ruta] = p.insert_image(r, stream=b.getvalue())
        return r


def texto(p, x, y, t, tam, fuente='R', color=TINTA, centro=False):
    if centro:
        x -= pymupdf.get_text_length(t, fontname='helv', fontsize=tam) / 2
    p.insert_text((x, y), t, fontname=fuente, fontsize=tam, color=color)


def cabecera(p, titulo, sub):
    p.draw_rect(pymupdf.Rect(0, 0, W, 6), color=None, fill=AZZURRO)
    texto(p, M, M + 14, 'CASA MARGOT  ·  CARTELES', 9, 'B', GRIS)
    texto(p, M, M + 40, titulo, 22, 'B')
    if sub:
        texto(p, M, M + 58, sub, 11, 'R', GRIS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--carpeta', default=os.path.join(SCRATCH, 'carteles', 'final'))
    ap.add_argument('--salida', default=None)
    a = ap.parse_args()
    salida = a.salida or os.path.join(a.carpeta, 'Carteles_CasaMargot.pdf')
    D = Doc(a.carpeta)

    # ---- portada: los cinco carteles en blanco
    p = D.pagina()
    cabecera(p, 'Cinco carteles con el logo y fondo azzurro',
             'Cada uno en los seis acabados del logo de la hoja de ideas.')
    cw, ch = (W - 2 * M - 2 * 14) / 3, (W - 2 * M - 2 * 14) / 3 * 1.25
    for i, (cl, nombre, _sub) in enumerate(CARTELES):
        f, c = divmod(i, 3)
        n_fila = 3 if f == 0 else 2
        x0 = (W - (n_fila * cw + (n_fila - 1) * 14)) / 2 + c * (cw + 14)
        y0 = M + 90 + f * (ch + 44)
        r = D.imagen(p, cl, 'blanco', pymupdf.Rect(x0, y0, x0 + cw, y0 + ch))
        texto(p, r.x0, r.y1 + 16, f'{i + 1}. {nombre}', 10, 'B')
    texto(p, M, H - M, 'Acabados: blanco, mármol blanco y oro, negro, mármol negro, '
          'oro y mármol rosa.', 9, 'R', GRIS)

    for i, (cl, nombre, sub) in enumerate(CARTELES):
        # ---- los seis acabados en una pagina
        p = D.pagina()
        cabecera(p, f'{i + 1}. {nombre}', sub)
        gx, gy = 16, 26
        top = M + 76
        ch = (H - top - M - 2 * gy) / 3 - 14
        cw = ch / 1.25
        x_ini = (W - 2 * cw - gx) / 2
        for j, (ac, etiqueta) in enumerate(ACABADOS):
            f, c = divmod(j, 2)
            x0, y0 = x_ini + c * (cw + gx), top + f * (ch + 14 + gy)
            r = D.imagen(p, cl, ac, pymupdf.Rect(x0, y0, x0 + cw, y0 + ch))
            texto(p, r.x0, r.y1 + 13, etiqueta, 9.5, 'R')
        # ---- y cada acabado a pagina completa
        for ac, etiqueta in ACABADOS:
            p = D.pagina()
            cabecera(p, f'{i + 1}. {nombre}', etiqueta)
            r = D.imagen(p, cl, ac, pymupdf.Rect(M, M + 76, W - M, H - M - 10))
    D.d.save(salida, garbage=3, deflate=True)
    print(salida, D.d.page_count, 'paginas',
          round(os.path.getsize(salida) / 1e6, 1), 'MB')


if __name__ == '__main__':
    main()
