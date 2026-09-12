# -*- coding: utf-8 -*-
"""
Envuelve `pagina.html` en un documento HTML completo y escribe `index.html`.

`pagina.html` es solo el cuerpo (titulo, estilos, contenido y script) porque
asi es como lo publica el Artifact de Claude, que aporta el esqueleto. Para
servir el sitio desde cualquier hosting estatico hace falta el documento
entero, y de eso se encarga este script.

    python3 build_sitio.py
"""

import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
CUERPO = os.path.join(AQUI, 'pagina.html')
SALIDA = os.path.join(AQUI, 'index.html')

DESCRIPCION = ('Visualizacion arquitectonica y documentacion tecnica de obra. '
               'Renders en Cycles, recorridos 360, planos acotados y grafica '
               'de obra a partir del levantamiento real.')

ESQUELETO = '''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{descripcion}">
<meta name="color-scheme" content="dark">
<meta property="og:type" content="website">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descripcion}">
<meta property="og:image" content="img/hero-barra.jpg">
<meta name="twitter:card" content="summary_large_image">
<style>
  html{{color-scheme:dark}}
  body{{margin:0;font:14px system-ui,sans-serif}}
  img{{max-width:100%}}
  [hidden]{{display:none!important}}
</style>
{cuerpo}
</body>
</html>
'''


def main():
    cuerpo = open(CUERPO, encoding='utf-8').read()
    m = re.search(r'<title>(.*?)</title>', cuerpo, re.S)
    titulo = m.group(1).strip() if m else 'Portfolio'

    # El <title> y los <link>/<style> van en la cabecera; el resto, al cuerpo.
    corte = cuerpo.index('<header')
    cabeza, resto = cuerpo[:corte], cuerpo[corte:]

    doc = ESQUELETO.format(titulo=titulo, descripcion=DESCRIPCION,
                           cuerpo=cabeza + '</head>\n<body>\n' + resto)
    open(SALIDA, 'w', encoding='utf-8').write(doc)
    print('index.html  %.1f KB' % (os.path.getsize(SALIDA) / 1024))


if __name__ == '__main__':
    main()
