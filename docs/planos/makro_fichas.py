# -*- coding: utf-8 -*-
"""
Descarga las fichas de Makro de todo el equipamiento y guarda sus medidas.

Makro bloquea las peticiones que llegan desde centros de datos, asi que este
script hay que ejecutarlo desde un ordenador con conexion normal (casa u
oficina). Abre cada ficha en un Chromium real, guarda el HTML completo y
saca nombre, medidas, precio e imagen a `makro_fichas.json`.

Preparacion (una sola vez):

    pip install playwright
    playwright install chromium

Uso:

    python3 makro_fichas.py                # abre una ventana y recorre las fichas
    python3 makro_fichas.py --headless     # sin ventana
    python3 makro_fichas.py --perfil       # reutiliza un perfil de Chromium donde
                                           # puedes iniciar sesion en Makro a mano
                                           # la primera vez (para ver precios de socio)
    python3 makro_fichas.py K5 A3          # solo esos rotulos

Sale: makro_fichas.json y la carpeta makro_html/ con una pagina por rotulo.
Ese JSON es lo unico que hay que enviar de vuelta.
"""

import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import equipamiento as Q

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, 'makro_fichas.json')
HTML_DIR = os.path.join(AQUI, 'makro_html')
PERFIL = os.path.join(AQUI, '.perfil_chromium')

# "600 x 615 x 1870 mm", "47 x 55 x 38 cm", "1360 × 700 × 850 mm", "80x70 cm"
RE_DIM = re.compile(
    r'(\d{1,4}(?:[.,]\d{1,2})?)\s*[x×X]\s*(\d{1,4}(?:[.,]\d{1,2})?)'
    r'(?:\s*[x×X]\s*(\d{1,4}(?:[.,]\d{1,2})?))?\s*(mm|cm)\b')
RE_ETIQ = re.compile(
    r'(ancho|anchura|fondo|profundidad|alto|altura|largo|longitud|di[aá]metro)'
    r'\s*[:\-]?\s*(\d{1,4}(?:[.,]\d{1,2})?)\s*(mm|cm)', re.I)
RE_PRECIO = re.compile(r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*€')


def a_metros(valor, unidad):
    v = float(str(valor).replace(',', '.'))
    return round(v / (1000.0 if unidad == 'mm' else 100.0), 3)


def medidas_de(texto):
    """Todas las medidas que aparecen en el texto, en metros."""
    tripletas = []
    for a, b, c, u in RE_DIM.findall(texto):
        dims = [a_metros(a, u), a_metros(b, u)] + ([a_metros(c, u)] if c else [])
        # descartar cosas que no son un aparato (cestas de 0,40 x 0,40, cubetas)
        if all(0.05 <= d <= 3.5 for d in dims):
            tripletas.append(dims)
    etiquetadas = {}
    for etq, v, u in RE_ETIQ.findall(texto):
        etiquetadas.setdefault(etq.lower(), a_metros(v, u))
    return tripletas, etiquetadas


def leer_json_ld(page):
    datos = []
    for s in page.query_selector_all('script[type="application/ld+json"]'):
        try:
            datos.append(json.loads(s.inner_text()))
        except Exception:
            pass
    return datos


def ficha(page, item):
    page.goto(item['url'], wait_until='domcontentloaded', timeout=60000)
    try:
        page.wait_for_load_state('networkidle', timeout=20000)
    except Exception:
        pass
    time.sleep(1.5)
    html = page.content()
    texto = page.inner_text('body')
    os.makedirs(HTML_DIR, exist_ok=True)
    open(os.path.join(HTML_DIR, item['tag'] + '.html'), 'w', encoding='utf-8').write(html)

    tripletas, etiquetadas = medidas_de(texto)
    ld = leer_json_ld(page)
    nombre = page.title()
    imagen = precio = None
    for d in ld:
        for nodo in (d if isinstance(d, list) else [d]):
            if isinstance(nodo, dict) and nodo.get('@type') in ('Product',):
                nombre = nodo.get('name') or nombre
                im = nodo.get('image')
                imagen = im[0] if isinstance(im, list) else im
                of = nodo.get('offers') or {}
                if isinstance(of, list):
                    of = of[0] if of else {}
                precio = of.get('price') or precio
    if precio is None:
        m = RE_PRECIO.search(texto)
        precio = m.group(1) if m else None

    return dict(tag=item['tag'], nombre_plano=item['nombre'], url=item['url'],
                titulo=nombre, medidas_encontradas=tripletas,
                medidas_etiquetadas=etiquetadas, precio=precio, imagen=imagen,
                bloqueado=('403' in nombre or len(texto) < 400))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    headless = '--headless' in sys.argv
    perfil = '--perfil' in sys.argv
    items = [p for p in Q.todos() if p.get('url') and (not args or p['tag'] in args)]
    if not items:
        print('No hay fichas que descargar.'); return

    from playwright.sync_api import sync_playwright
    resultados = {}
    with sync_playwright() as pw:
        if perfil:
            ctx = pw.chromium.launch_persistent_context(PERFIL, headless=headless,
                                                        locale='es-ES')
            page = ctx.new_page()
            if not headless:
                print('Si quieres precios de socio, inicia sesion en la ventana y '
                      'pulsa Intro aqui.')
                page.goto('https://www.makro.es/')
                input()
        else:
            navegador = pw.chromium.launch(headless=headless)
            ctx = navegador.new_context(locale='es-ES')
            page = ctx.new_page()

        for i, item in enumerate(items, 1):
            print(f'[{i:2d}/{len(items)}] {item["tag"]:4s} {item["nombre"][:60]}')
            try:
                r = ficha(page, item)
            except Exception as e:
                r = dict(tag=item['tag'], url=item['url'], error=str(e))
            resultados[item['tag']] = r
            if r.get('bloqueado'):
                print('        ! la pagina parece bloqueada o vacia')
            else:
                print('        medidas:', r.get('medidas_encontradas') or '-',
                      '| precio:', r.get('precio') or '-')
            time.sleep(1.0)
        ctx.close()

    json.dump(resultados, open(SALIDA, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=2)
    print(f'\nGuardado {SALIDA} con {len(resultados)} fichas. Envia ese archivo.')


if __name__ == '__main__':
    main()
