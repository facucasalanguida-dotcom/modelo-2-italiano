#!/usr/bin/env python3
"""Deja lista una maquina para renderizar Casa Margot.

El repositorio lleva el codigo, los planos, el logo en PDF y los 24 aparatos
de Makro. Lo que NO lleva son 1,5 GB de texturas y modelos de Poly Haven ni
el coche: son CC0 y se bajan de su fuente, que es mas sano que arrastrarlos
por el repositorio. Esto los baja y los deja con el nombre y en el sitio que
espera materiales.mapas().

    export CM_SCRATCH=~/casa_margot_activos     # Windows: set CM_SCRATCH=...
    python3 preparar_activos.py

Es idempotente: lo que ya esta no se vuelve a bajar, asi que se puede
relanzar si se corta a medias. Al terminar deja:

    $CM_SCRATCH/ph/<aid>/textures/<aid>_<clave>_4k.<ext>      texturas 4K
    $CM_SCRATCH/ph/<aid>/textures_2k/<aid>_<clave>_4k.<ext>   las mismas a 2K
    $CM_SCRATCH/ph/<aid>/<aid>.blend                          modelos (2K)
    $CM_SCRATCH/ph/<aid>/<aid>_8k.hdr                         el HDRI del cielo
    $CM_SCRATCH/coches/bmw27/bmw27/bmw27_cpu.blend            el coche
    $CM_SCRATCH/logo/casa_margot_recortado.png                el vinilo del logo

La escena usa las copias a 2K salvo que se pida CM_4K=1: Cycles carga cada
mapa entero en memoria y con ~120 mapas a 4096x4096 el proceso pasa de 13 GB.
"""
import ast, io, json, os, subprocess, sys, time, zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.environ.get('CM_SCRATCH') or os.path.join(AQUI, 'activos')
PH = os.path.join(SCRATCH, 'ph')
CACHE = os.path.join(SCRATCH, 'api')
CLAVES = {'Diffuse': 'diff', 'Rough': 'rough', 'nor_gl': 'nor_gl',
          'Displacement': 'disp', 'AO': 'ao'}

# Lo que pide la escena, escrito a mano. Es la red de seguridad: si no se
# puede leer el indice de Poly Haven -sin linea, o la API caida- se baja al
# menos esto. Lo que manda de verdad es lo que se deduce del codigo en
# necesarios(), para que no se quede desfasada sola.
BASE = {
    'hdri': ['wide_street_01'],
    'textura': ['asphalt_02', 'clay_roof_tiles', 'concrete_floor_worn_001',
                'dark_rock', 'granite_tile', 'large_floor_tiles_02', 'marble_01',
                'oak_veneer_01', 'plastered_wall', 'white_plaster_02', 'wood_floor'],
    'modelo': ['brass_pot_01', 'ceramic_vase_01', 'ceramic_vase_02', 'croissant',
               'fire_hydrant', 'food_apple_01', 'food_lime_01', 'food_pomegranate_01',
               'jacaranda_tree', 'jug_01', 'metal_jug', 'metal_trash_can',
               'modular_street_seating', 'painted_wooden_bench', 'planter_pot_clay',
               'potted_plant_01', 'potted_plant_02', 'tea_set_01', 'tree_small_02',
               'wicker_basket_01', 'wicker_basket_02', 'wooden_bowl_01'],
}


def indice():
    """El catalogo entero de Poly Haven: 2.380 activos con su tipo."""
    d = os.path.join(CACHE, 'index.json')
    if not os.path.exists(d):
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run(['curl', '-sS', '--fail',
                        'https://api.polyhaven.com/assets', '-o', d])
    try:
        return json.load(open(d))
    except Exception:
        return {}


def necesarios():
    """Que activos pide la escena, leidos del propio codigo.

    Se sacan todas las cadenas literales de escena.py y materiales.py y se
    cruzan con el catalogo: lo que coincide es un activo de Poly Haven que
    la escena nombra. Asi añadir un material o un objeto nuevo no obliga a
    acordarse de tocar este fichero. Se une con BASE por si acaso.
    """
    out = {k: set(v) for k, v in BASE.items()}
    idx = indice()
    if not idx:
        print('  (sin indice de Poly Haven: se usa la lista de seguridad)',
              flush=True)
        return {k: sorted(v) for k, v in out.items()}
    tipo = {0: 'hdri', 1: 'textura', 2: 'modelo'}
    lits = set()
    for f in ('escena.py', 'materiales.py'):
        try:
            arbol = ast.parse(io.open(os.path.join(AQUI, f), encoding='utf-8').read())
        except Exception as e:
            print(f'  (no se pudo leer {f}: {e})', flush=True)
            continue
        for n in ast.walk(arbol):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                lits.add(n.value)
    nuevos = 0
    for s in sorted(lits & set(idx)):
        t = tipo.get(idx[s].get('type'))
        if t and s not in out[t]:
            out[t].add(s)
            nuevos += 1
    print(f'  {sum(len(v) for v in out.values())} activos que pide la escena'
          f'{f" ({nuevos} que no estaban en la lista de seguridad)" if nuevos else ""}',
          flush=True)
    return {k: sorted(v) for k, v in out.items()}


# El coche es la escena de demostracion de Blender, CC0 como el resto.
# BMW27_2 y no BMW27: el primero trae bmw27/bmw27_cpu.blend con la coleccion
# '1M' que carga poner_bmw(); el segundo es un BMW27.blend suelto sin ella.
BMW_ZIP = 'https://download.blender.org/demo/test/BMW27_2.blend.zip'
BMW_DENTRO = os.path.join('bmw27', 'bmw27_cpu.blend')


def bajar(url, dest, minimo=1000):
    """curl con reintentos. urllib se come un 403 del proxy; curl no."""
    if os.path.exists(dest) and os.path.getsize(dest) > minimo:
        return 0
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    for intento in range(4):
        r = subprocess.run(['curl', '-sS', '-L', '--fail', url, '-o', dest + '.part'],
                           capture_output=True)
        if r.returncode == 0 and os.path.exists(dest + '.part') \
                and os.path.getsize(dest + '.part') > minimo:
            os.replace(dest + '.part', dest)
            return os.path.getsize(dest)
        time.sleep(2 * (intento + 1))
    print('   FALLO', url, flush=True)
    return 0


def ficheros(aid):
    d = os.path.join(CACHE, f'{aid}.json')
    if not os.path.exists(d):
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run(['curl', '-sS', '--fail',
                        f'https://api.polyhaven.com/files/{aid}', '-o', d])
    return json.load(open(d))


def poly_haven(nec):
    tot = 0
    for aid in nec['hdri']:
        f = ficheros(aid)
        res = '8k' if '8k' in f['hdri'] else max(f['hdri'])
        tot += bajar(f['hdri'][res]['hdr']['url'], f'{PH}/{aid}/{aid}_{res}.hdr')
        print(f'  HDRI    {aid} {res}', flush=True)
    for aid in nec['textura']:
        f = ficheros(aid)
        for res, carpeta in (('4k', 'textures'), ('2k', 'textures_2k')):
            for nombre, clave in CLAVES.items():
                nodo = f.get(nombre)
                if not nodo or res not in nodo:
                    continue
                fmts = nodo[res]
                fmt = 'jpg' if 'jpg' in fmts else ('png' if 'png' in fmts else max(fmts))
                tot += bajar(fmts[fmt]['url'],
                             f'{PH}/{aid}/{carpeta}/{aid}_{clave}_4k.{fmt}')
        print(f'  TEXTURA {aid}', flush=True)
    for aid in nec['modelo']:
        f = ficheros(aid)
        # a 2K a proposito: a 4K los 22 modelos revientan la memoria de Cycles,
        # y son objetos pequeños que nunca ocupan mucho en pantalla
        res = '2k' if '2k' in f['blend'] else max(f['blend'])
        bl = f['blend'][res]['blend']
        tot += bajar(bl['url'], f'{PH}/{aid}/{aid}.blend')
        for rel, inf in bl.get('include', {}).items():
            tot += bajar(inf['url'], f'{PH}/{aid}/{rel}')
        print(f'  MODELO  {aid} {res}', flush=True)
    return tot


def coche():
    destino = os.path.join(SCRATCH, 'coches', 'bmw27')
    if os.path.exists(os.path.join(destino, BMW_DENTRO)):
        print('  COCHE   ya estaba', flush=True)
        return 0
    z = os.path.join(SCRATCH, 'coches', 'bmw27.zip')
    n = bajar(BMW_ZIP, z, minimo=100000)
    if not os.path.exists(z):
        print('  COCHE   FALLO: la calle saldra sin coches', flush=True)
        return 0
    with zipfile.ZipFile(z) as f:
        f.extractall(destino)
    os.remove(z)
    if not os.path.exists(os.path.join(destino, BMW_DENTRO)):
        print('  COCHE   el zip no trae', BMW_DENTRO, flush=True)
    else:
        print('  COCHE   bmw27 listo', flush=True)
    return n


def logo():
    sal = os.path.join(SCRATCH, 'logo', 'casa_margot_recortado.png')
    if os.path.exists(sal):
        print('  LOGO    ya estaba', flush=True)
        return
    r = subprocess.run([sys.executable, os.path.join(AQUI, 'rehacer_logo.py')],
                       env={**os.environ, 'CM_SCRATCH': SCRATCH})
    if r.returncode:
        print('  LOGO    FALLO: hace falta  pip install pymupdf pillow numpy', flush=True)


if __name__ == '__main__':
    print('activos en', SCRATCH, flush=True)
    tot = poly_haven(necesarios()) + coche()
    logo()
    print(f'\nLISTO  {tot / 1e6:.0f} MB bajados', flush=True)
    print('Ahora:  export CM_SCRATCH=' + SCRATCH, flush=True)
