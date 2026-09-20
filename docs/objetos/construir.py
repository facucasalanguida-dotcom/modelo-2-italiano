# -*- coding: utf-8 -*-
"""
Lanzador: construye un objeto de la biblioteca y genera su .blend y su hoja
de vistas.

    python3 construir.py K1              # medidas + 4 vistas + blend
    python3 construir.py K1 --rapido     # 1 vista pequena (para iterar)
    python3 construir.py K1 --sin-render # solo medidas + blend
    python3 construir.py todos           # todos los que tengan obj_<TAG>.py

Cada objeto vive en obj_<TAG>.py y expone build() -> None; el lanzador se
encarga del documento nuevo, del control de medidas, del render y del guardado.
"""
import importlib
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import lib as L  # noqa: E402


def construir(tag, modo='completo'):
    mod = importlib.import_module(f'obj_{tag}')
    t0 = time.time()
    L.nuevo_documento(tag)
    L.raiz(tag)
    extra = mod.build() or {}
    print(f'[{tag}] construido en {time.time() - t0:.1f} s')
    kw = dict(ignorar=extra.get('ignorar', ()), medidas=extra.get('medidas'),
              altura=extra.get('altura', 0.0))
    vistas = extra.get('vistas', L.VISTAS)
    if modo == 'rapido':
        L.finalizar(tag, spp=64, res=(800, 600), vistas=[vistas[0]], **kw)
    elif modo == 'sin-render':
        L.finalizar(tag, render=False, **kw)
    else:
        L.finalizar(tag, spp=extra.get('spp', 192), res=(1100, 825),
                    vistas=vistas, lente=extra.get('lente', 50.0), **kw)
    print(f'[{tag}] total {time.time() - t0:.0f} s')


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    modo = 'completo'
    if '--rapido' in sys.argv:
        modo = 'rapido'
    if '--sin-render' in sys.argv:
        modo = 'sin-render'
    tags = args or ['todos']
    if tags == ['todos']:
        tags = sorted(f[4:-3] for f in os.listdir(AQUI) if f.startswith('obj_') and f.endswith('.py'))
    for t in tags:
        construir(t, modo)
