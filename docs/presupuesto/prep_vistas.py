# Prepara las cuatro vistas de referencia marcadas por el cliente:
# las mismas imagenes de la galeria web, reescaladas para impresion.
import base64, io, json, os
from PIL import Image

REPO = '/home/user/modelo-2-italiano'
SP   = os.path.dirname(os.path.abspath(__file__))

# (fichero de origen, pie) — orden de lectura en el documento
VISTAS = [
    ('01_entrada.jpg',          'La entrada'),
    ('03_barra.jpg',            'La barra'),
    ('04_vitrinas.jpg',         'Vitrinas de obrador'),
    ('02b_mesa_ventanal.jpg',   'Mesa junto al ventanal'),
]

ANCHO = 760          # ~470 ppp a los 41 mm que ocupan en la hoja
salida = []
for fich, pie in VISTAS:
    im = Image.open(f'{REPO}/docs/render/v2/{fich}').convert('RGB')
    im = im.resize((ANCHO, round(ANCHO * im.height / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=86, optimize=True, progressive=True)
    salida.append({'t': pie, 'd': base64.b64encode(buf.getvalue()).decode()})
    print(f'{pie:24s} {im.size}  {len(buf.getvalue())//1024} KB')

json.dump(salida, open(f'{SP}/vistas.json', 'w'))
print('vistas.json:', os.path.getsize(f'{SP}/vistas.json') // 1024, 'KB')
