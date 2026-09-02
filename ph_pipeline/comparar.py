# Antes / despues: la misma camara, render base (Cycles procedural) frente
# al render con recursos reales. Genera lado a lado + dos detalles ampliados.
import sys
from PIL import Image, ImageDraw, ImageFont
antes = Image.open(sys.argv[1]).convert('RGB')
despues = Image.open(sys.argv[2]).convert('RGB')
salida = sys.argv[3]
W, H = despues.size
antes = antes.resize((W, H), Image.LANCZOS)
f = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 44)
def rotular(im, txt):
    im = im.copy(); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 420, 70], fill=(20, 24, 28)); d.text((18, 12), txt, font=f, fill=(240, 232, 216)); return im
lado = Image.new('RGB', (W*2 + 24, H), (20, 24, 28))
lado.paste(rotular(antes, 'ANTES · procedural'), (0, 0)); lado.paste(rotular(despues, 'DESPUÉS · Poly Haven'), (W + 24, 0))
lado.thumbnail((3200, 1800)); lado.save(salida, quality=92)
# detalles: zona de la cafetera/vitrina y zona de suelo/barra
for i, (x0, y0, x1, y1) in enumerate(((int(W*0.30), int(H*0.28), int(W*0.62), int(H*0.62)),
                                       (int(W*0.45), int(H*0.62), int(W*0.85), int(H*0.98)))):
    a = antes.crop((x0, y0, x1, y1)); b = despues.crop((x0, y0, x1, y1))
    det = Image.new('RGB', (a.width*2 + 16, a.height), (20, 24, 28))
    det.paste(rotular(a, 'ANTES'), (0, 0)); det.paste(rotular(b, 'DESPUÉS'), (a.width + 16, 0))
    det.save(salida.replace('.jpg', f'_detalle{i+1}.jpg'), quality=92)
print('comparativas listas')
