# Genera el index.html de la raiz (documento completo para Vercel)
# a partir de docs/web/cafe_napoli_landing.html (fragmento para artifact).
import os

REPO = '/home/user/modelo-2-italiano'
src = open(os.path.join(REPO, 'docs/web/cafe_napoli_landing.html')).read()

# La cabecera termina en el primer </style> (title + fuentes + estilos);
# el resto (nav, hero, secciones, scripts) es el cuerpo. Se usa el PRIMER
# </style> porque el JSON del tour contiene otros mas adelante.
marca = '</style>'
i = src.index(marca) + len(marca)
cabeza, cuerpo = src[:i].rstrip(), src[i:].strip()

html = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{cabeza}
</head>
<body>
{cuerpo}
</body>
</html>
'''
out = os.path.join(REPO, 'index.html')
open(out, 'w').write(html)
print('index:', out, len(html) // 1024, 'KB')
