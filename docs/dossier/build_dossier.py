#!/usr/bin/env python3
"""Dossier de Casa Margot: portada, paleta y una pagina por render.

    python3 build_dossier.py --fotos ../render/casa_margot --salida CASA_MARGOT.pdf

Las paginas son 16:9 para que los renders entren a sangre sin bandas: son
3840x2160 y cualquier formato de papel les dejaria franjas arriba y abajo.

El logo se incrusta como VECTOR desde docs/pared/CASA_MARGOT_LOGO_NERO.pdf,
no como imagen: en el PDF final se puede ampliar sin que pixele.

Los colores no son inventados: salen de materiales.py, que es de donde los
toma el render. Si alli cambia un albedo, aqui hay que cambiarlo tambien.
"""
import argparse, os, sys
import fitz

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(AQUI, '..', '..'))
LOGO_PDF = os.path.join(REPO, 'docs', 'pared', 'CASA_MARGOT_LOGO_NERO.pdf')

W, H = 842.0, 473.6                      # 16:9 sobre el ancho de un A4 apaisado
M = 46.0                                 # margen de las paginas de texto

AZZURRO = '12A0D7'                       # SSC Napoli, Pantone 2995 C
CREMA = 'F2EFE8'                         # el blanco roto de las paredes
TINTA = '262524'                         # el negro mate del proyecto

# nombre, hex, donde se usa. Tomados de docs/render/escena/materiales.py
PALETA = [
    ('Azzurro Napoli', AZZURRO, 'Pared del plotter y banda de rótulo'),
    ('Blanco roto', 'F2EFE8', 'Paramentos y falso techo'),
    ('Enlucido', 'EDE6D8', 'Muros de obra'),
    ('Hormigón', 'C9C4BA', 'Pilares vistos'),
    ('Roble', 'C89C6A', 'Listón de columnas y frente de barra'),
    ('Roble de suelo', 'C09563', 'Pavimento y peldaños'),
    ('Tablero de mesa', 'C79B68', 'Mesas y pasamanos'),
    ('Mármol', 'E6E1D6', 'Encimeras'),
    ('Losa de piedra', '34363A', 'Revestimiento de P2 y P5'),
    ('Negro mate', '262524', 'Carpintería y zócalos'),
    ('Latón', 'C69E54', 'Aros de las luminarias'),
    ('Terracota', 'A9714F', 'Maceteros'),
]

# orden y pie de cada vista
VISTAS = [
    ('fachada', 'La fachada desde la acera de enfrente'),
    ('entrada', 'La entrada, nada más cruzar la puerta'),
    ('logo', 'La pared del plotter, de la escalera a la puerta'),
    ('general', 'Panorámica del local desde la esquina de entrada'),
    ('barra', 'La barra en diagonal, con la trasbarra al fondo'),
    ('barra_frente', 'El mostrador de frente, desde la sala'),
    ('chopera', 'La barra por dentro, hacia la chopera'),
    ('trasbarra', 'El punto de vista del camarero'),
    ('cocina', 'La cocina: línea de cocción y campana'),
    ('escaparate', 'El ventanal de doble altura desde dentro'),
    ('escalera', 'La escalera, con LED en cada peldaño'),
    ('sillon', 'El sillón corrido contra el muro Norte'),
    ('alta', 'El altillo'),
    ('alta_cowork', 'La mesa de cowork, ocho puestos'),
    ('alta_vacio', 'Asomado al vacío de doble altura'),
]


def rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def fondo(page, color):
    page.draw_rect(fitz.Rect(0, 0, W, H), color=None, fill=rgb(color))


def logo(page, rect, doc_logo):
    """El logo, como vector y guardando su proporcion dentro de rect."""
    o = doc_logo[0].rect
    k = min(rect.width / o.width, rect.height / o.height)
    w, h = o.width * k, o.height * k
    x0 = rect.x0 + (rect.width - w) / 2
    y0 = rect.y0 + (rect.height - h) / 2
    page.show_pdf_page(fitz.Rect(x0, y0, x0 + w, y0 + h), doc_logo, 0)


def texto(page, x, y, s, tam=11, color=TINTA, font='helv'):
    page.insert_text(fitz.Point(x, y), s, fontsize=tam, fontname=font,
                     color=rgb(color))


def portada(doc, doc_logo, subtitulo):
    p = doc.new_page(width=W, height=H)
    fondo(p, CREMA)
    p.draw_rect(fitz.Rect(0, H - 26, W, H), color=None, fill=rgb(AZZURRO))
    logo(p, fitz.Rect(M, 96, W - M, 300), doc_logo)
    p.draw_line(fitz.Point(W / 2 - 60, 344), fitz.Point(W / 2 + 60, 344),
                color=rgb(AZZURRO), width=1.4)
    for i, s in enumerate(subtitulo):
        w = fitz.get_text_length(s, fontname='helv', fontsize=10.5)
        texto(p, (W - w) / 2, 372 + i * 17, s, 10.5)


def pagina_paleta(doc, doc_logo):
    p = doc.new_page(width=W, height=H)
    fondo(p, CREMA)
    texto(p, M, M + 12, 'COLOR', 17, TINTA, 'hebo')
    p.draw_line(fitz.Point(M, M + 24), fitz.Point(M + 58, M + 24),
                color=rgb(AZZURRO), width=1.4)
    cols, cw = 4, (W - 2 * M) / 4
    for i, (nombre, h, uso) in enumerate(PALETA):
        cx = M + (i % cols) * cw
        cy = M + 52 + (i // cols) * 118
        p.draw_rect(fitz.Rect(cx, cy, cx + cw - 22, cy + 56),
                    color=None, fill=rgb(h))
        texto(p, cx, cy + 74, nombre, 9.5, TINTA, 'hebo')
        texto(p, cx, cy + 87, '#' + h, 8.5, AZZURRO)
        texto(p, cx, cy + 100, uso, 8, '6B6862')
    logo(p, fitz.Rect(W - M - 104, M - 6, W - M, M + 30), doc_logo)


def pagina_foto(doc, ruta, pie, n, total, ancho=0):
    p = doc.new_page(width=W, height=H)
    fondo(p, TINTA)
    # a sangre, guardando proporcion: se ajusta al lado que sobre
    import PIL.Image, tempfile
    im = PIL.Image.open(ruta)
    if ancho and im.width > ancho:
        im = im.convert('RGB')
        im.thumbnail((ancho, ancho * 10), PIL.Image.LANCZOS)
        t = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        im.save(t.name, quality=88, optimize=True)
        ruta = t.name
    iw, ih = im.size
    k = max(W / iw, H / ih)
    w, h = iw * k, ih * k
    x0, y0 = (W - w) / 2, (H - h) / 2
    p.insert_image(fitz.Rect(x0, y0, x0 + w, y0 + h), filename=ruta)
    # banda de pie
    p.draw_rect(fitz.Rect(0, H - 30, W, H), color=None, fill=rgb(TINTA))
    p.draw_rect(fitz.Rect(0, H - 30, 4, H), color=None, fill=rgb(AZZURRO))
    texto(p, 18, H - 11, pie, 9.5, CREMA)
    s = f'{n:02d} / {total:02d}'
    texto(p, W - 18 - fitz.get_text_length(s, fontname='helv', fontsize=9.5),
          H - 11, s, 9.5, AZZURRO)


def contraportada(doc, doc_logo, pie):
    p = doc.new_page(width=W, height=H)
    fondo(p, AZZURRO)
    p.draw_rect(fitz.Rect(M, H / 2 - 62, W - M, H / 2 + 20),
                color=None, fill=rgb(CREMA))
    logo(p, fitz.Rect(M + 20, H / 2 - 54, W - M - 20, H / 2 + 12), doc_logo)
    for i, s in enumerate(pie):
        w = fitz.get_text_length(s, fontname='helv', fontsize=9.5)
        texto(p, (W - w) / 2, H / 2 + 56 + i * 15, s, 9.5, CREMA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fotos', default=os.path.join(REPO, 'docs', 'render', 'casa_margot'))
    ap.add_argument('--salida', default=os.path.join(AQUI, 'CASA_MARGOT_dossier.pdf'))
    ap.add_argument('--titulo', default='Proyecto de interiorismo')
    ap.add_argument('--ancho', type=int, default=0,
                    help='reescala las fotos a este ancho en px para el PDF '
                         'de correo; 0 las deja como estan')
    ap.add_argument('--lugar', default='Málaga')
    a = ap.parse_args()

    if not os.path.exists(LOGO_PDF):
        sys.exit('No encuentro el logo: ' + LOGO_PDF)
    doc_logo = fitz.open(LOGO_PDF)
    doc = fitz.open()

    # se cogen en el orden de VISTAS, y lo que sobre va detras por nombre
    fotos, vistos = [], set()
    for clave, pie in VISTAS:
        for ext in ('.jpg', '.png'):
            r = os.path.join(a.fotos, f'CM_{clave}{ext}')
            if os.path.exists(r):
                fotos.append((r, pie)); vistos.add(os.path.basename(r)); break
    for f in sorted(os.listdir(a.fotos)):
        if f.lower().endswith(('.jpg', '.png')) and f not in vistos:
            base = os.path.splitext(f)[0]
            if base + '.png' in vistos or base + '.jpg' in vistos:
                continue
            fotos.append((os.path.join(a.fotos, f), base.replace('CM_', '')))
    if not fotos:
        sys.exit('No hay fotos en ' + a.fotos)

    portada(doc, doc_logo, [a.titulo, a.lugar, f'{len(fotos)} vistas'])
    pagina_paleta(doc, doc_logo)
    for i, (r, pie) in enumerate(fotos, 1):
        pagina_foto(doc, r, pie, i, len(fotos), a.ancho)
    contraportada(doc, doc_logo, [a.lugar])

    doc.set_metadata({'title': 'Casa Margot · ' + a.titulo, 'subject': a.lugar})
    doc.save(a.salida, deflate=True, garbage=4)
    print(f'{a.salida}  ·  {len(doc)} paginas  ·  '
          f'{os.path.getsize(a.salida) / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
