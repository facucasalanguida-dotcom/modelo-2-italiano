#!/usr/bin/env python3
"""Pinta la pizarra del menu que va en la pared de detras de la barra.

Pizarra de 1,60 x 1,10 m: el logo de Casa Margot arriba, en blanco tiza,
sacado del mismo PDF que el vinilo, y debajo cuatro apartados de cocina
italiana escritos a tiza. Deja el resultado en docs/pared/, junto al logo,
para que la escena lo encuentre sin bajar nada.

Los platos son de muestra, los de una trattoria: para poner la carta de
verdad basta con cambiar MENU y volver a lanzarlo.

    python3 rehacer_pizarra.py

Las letras son Playfair Display (titulos) y Caveat (la tiza), de Google
Fonts, con licencia OFL; se bajan una vez a la carpeta de activos.
"""
import os
import urllib.request

import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from rutas import SCRATCH

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF = os.path.join(RAIZ, 'pared', 'CASA_MARGOT_LOGO_NERO.pdf')
SAL = os.path.join(RAIZ, 'pared', 'CASA_MARGOT_PIZARRA_MENU.jpg')
FUENTES = os.path.join(SCRATCH, 'fuentes')
GF = 'https://raw.githubusercontent.com/google/fonts/main/ofl/'
LETRAS = {
    'titulo': ('PlayfairDisplay-Italic[wght].ttf', 'playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf'),
    'tiza': ('Caveat[wght].ttf', 'caveat/Caveat%5Bwght%5D.ttf'),
}

MENU = [
    ('Antipasti', ['Bruschetta al pomodoro', 'Burrata e pomodorini',
                   'Tagliere di salumi e formaggi', 'Arancini siciliani']),
    ('Pizze', ['Margherita', 'Diavola', 'Quattro formaggi',
               'Prosciutto e funghi', 'Capricciosa']),
    ('Pasta', ['Spaghetti alla carbonara', 'Tagliatelle al ragù',
               'Lasagna alla bolognese', "Penne all'arrabbiata", 'Gnocchi al pesto']),
    ('Dolci', ['Tiramisù', 'Panna cotta', 'Cannoli siciliani', 'Affogato al caffè']),
]

W, H = 3200, 2200                  # 2000 px por metro: 1,60 x 1,10 m
TIZA = np.array([238, 235, 226], dtype=np.float32)
FONDO = np.array([36, 41, 38], dtype=np.float32)


def fuente(clave, tam, peso=None):
    nombre, ruta = LETRAS[clave]
    local = os.path.join(FUENTES, nombre)
    if not os.path.exists(local):
        os.makedirs(FUENTES, exist_ok=True)
        urllib.request.urlretrieve(GF + ruta, local)
    f = ImageFont.truetype(local, tam)
    if peso:
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
    return f


def ruido(rng, escala, forma):
    """Ruido suave: gaussiano a baja resolucion y escalado."""
    h, w = forma
    pequeno = rng.normal(0.0, 1.0, (max(2, h // escala), max(2, w // escala)))
    im = Image.fromarray(((pequeno - pequeno.min()) / np.ptp(pequeno) * 255).astype(np.uint8))
    return np.asarray(im.resize((w, h), Image.BICUBIC), dtype=np.float32) / 255.0


def logo_tiza(ancho):
    pix = pymupdf.open(PDF)[0].get_pixmap(dpi=300, alpha=True)
    im = Image.frombytes('RGBA', (pix.width, pix.height), pix.samples)
    a = np.asarray(im)[..., 3]
    ys, xs = np.where(a > 8)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    alto = round(im.height * ancho / im.width)
    return np.asarray(im.resize((ancho, alto), Image.LANCZOS))[..., 3].astype(np.float32) / 255.0


def main():
    rng = np.random.default_rng(7)
    # --- la pizarra: gris verdoso casi negro, con restos de borrar
    fondo = np.ones((H, W, 3), np.float32) * FONDO
    manchas = ruido(rng, 180, (H, W))
    fondo += (manchas[..., None] - 0.5) * 16.0
    fondo += rng.normal(0.0, 3.2, (H, W, 1))
    # --- lo escrito, en una capa de alfa que luego se ensucia de tiza
    capa = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(capa)
    # el logo, arriba y centrado
    lg = logo_tiza(1000)
    y0 = 100
    alfa = np.zeros((H, W), np.float32)
    x0 = (W - lg.shape[1]) // 2
    alfa[y0:y0 + lg.shape[0], x0:x0 + lg.shape[1]] = lg
    y_sub = y0 + lg.shape[0] + 26
    sub = fuente('tiza', 88, 500)
    d.text((W / 2, y_sub), 'cucina italiana', font=sub, fill=255, anchor='ma')
    # filete bajo el subtitulo
    yf = y_sub + 122
    d.line([(W / 2 - 520, yf), (W / 2 - 60, yf)], fill=200, width=5)
    d.line([(W / 2 + 60, yf), (W / 2 + 520, yf)], fill=200, width=5)
    d.ellipse([(W / 2 - 14, yf - 14), (W / 2 + 14, yf + 14)], outline=220, width=5)
    # cuatro apartados en dos columnas
    tit = fuente('titulo', 98, 600)
    pl = fuente('tiza', 78, 450)
    cols = (W * 0.27, W * 0.73)
    PASO = 88                          # entre renglones
    fila = 150 + 60 + PASO * max(len(p) for _, p in MENU) + 40
    filas = (yf + 70, yf + 70 + fila)
    for i, (seccion, platos) in enumerate(MENU):
        cx = cols[i % 2]
        y = filas[i // 2]
        d.text((cx, y), seccion, font=tit, fill=255, anchor='ma')
        bb = d.textbbox((cx, y), seccion, font=tit, anchor='ma')
        d.line([(cx - 150, bb[3] + 22), (cx + 150, bb[3] + 22)], fill=190, width=4)
        yy = bb[3] + 62
        for p in platos:
            d.text((cx, yy), p, font=pl, fill=245, anchor='ma')
            yy += PASO
        assert yy < H - 40, ('no cabe', seccion, yy)
    # separador vertical de puntos
    for yy in range(filas[0] + 20, H - 110, 46):
        d.ellipse([(W / 2 - 5, yy - 5), (W / 2 + 5, yy + 5)], fill=150)
    alfa = np.maximum(alfa, np.asarray(capa.filter(ImageFilter.GaussianBlur(0.8)),
                                       dtype=np.float32) / 255.0)
    # grano de tiza: el trazo no cubre del todo y se come en los bordes
    grano = np.clip(rng.normal(0.86, 0.14, (H, W)), 0.35, 1.0)
    grano *= 0.85 + 0.15 * ruido(rng, 6, (H, W))
    alfa = alfa * grano
    img = fondo * (1.0 - alfa[..., None]) + TIZA * alfa[..., None]
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    out.save(SAL, quality=90)
    print('pizarra:', SAL, out.size)


if __name__ == '__main__':
    main()
