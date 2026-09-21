#!/usr/bin/env python3
"""Vuelve a bajar los activos de Poly Haven que necesita la escena.

El contenedor se reinicio y se llevo el scratchpad. El codigo estaba
pusheado y se recupero del repositorio; los activos hay que rebajarlos.

Reglas de sitio y nombre, que es lo que espera materiales.mapas():
  texturas -> ph/<aid>/textures/<aid>_<clave>_4k.<ext>   (4K)
              ph/<aid>/textures_2k/<aid>_<clave>_4k.<ext> (2K, mismo nombre)
  modelos  -> ph/<aid>/<aid>.blend + sus texturas donde las pide el blend.
              Se bajan a 2K a proposito: a 4K los 22 modelos revientan la
              memoria de Cycles, y son objetos pequeños.
  hdri     -> ph/<aid>/<aid>_8k.hdr
"""
import json, os, subprocess, sys, time

S = os.path.dirname(os.path.abspath(__file__))
PH = os.path.join(S, 'ph')
CLAVES = {'Diffuse': 'diff', 'Rough': 'rough', 'nor_gl': 'nor_gl',
          'Displacement': 'disp', 'AO': 'ao'}


def curl(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        return 0
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    for intento in range(4):
        r = subprocess.run(['curl', '-sS', '-L', '--fail', url, '-o', dest + '.part'],
                           capture_output=True)
        if r.returncode == 0 and os.path.getsize(dest + '.part') > 1000:
            os.replace(dest + '.part', dest)
            return os.path.getsize(dest)
        time.sleep(2 * (intento + 1))
    print('   FALLO', url, flush=True)
    return 0


def ficheros(aid):
    d = os.path.join(S, f'f_{aid}.json')
    if not os.path.exists(d):
        subprocess.run(['curl', '-sS', f'https://api.polyhaven.com/files/{aid}', '-o', d])
    return json.load(open(d))


nec = json.load(open(os.path.join(S, 'necesarios.json')))
tot = 0
for aid in nec.get('hdri', []):
    f = ficheros(aid)
    res = '8k' if '8k' in f['hdri'] else max(f['hdri'])
    tot += curl(f['hdri'][res]['hdr']['url'], f'{PH}/{aid}/{aid}_{res}.hdr')
    print(f'HDRI {aid} {res}', flush=True)

for aid in nec.get('textura', []):
    f = ficheros(aid)
    for res, carpeta in (('4k', 'textures'), ('2k', 'textures_2k')):
        for nombre, clave in CLAVES.items():
            nodo = f.get(nombre)
            if not nodo or res not in nodo:
                continue
            fmts = nodo[res]
            fmt = 'jpg' if 'jpg' in fmts else ('png' if 'png' in fmts else max(fmts))
            tot += curl(fmts[fmt]['url'], f'{PH}/{aid}/{carpeta}/{aid}_{clave}_4k.{fmt}')
    print(f'TEXTURA {aid}', flush=True)

for aid in nec.get('modelo', []):
    f = ficheros(aid)
    res = '2k' if '2k' in f['blend'] else max(f['blend'])
    bl = f['blend'][res]['blend']
    tot += curl(bl['url'], f'{PH}/{aid}/{aid}.blend')
    for rel, inf in bl.get('include', {}).items():
        tot += curl(inf['url'], f'{PH}/{aid}/{rel}')
    print(f'MODELO {aid} {res}: {1 + len(bl.get("include", {}))} ficheros', flush=True)

print(f'RESTAURACION OK  {tot / 1e6:.0f} MB', flush=True)
