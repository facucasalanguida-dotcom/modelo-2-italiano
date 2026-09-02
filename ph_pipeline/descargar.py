# Descarga activos CC0 de Poly Haven por id: HDRI (8k .hdr), texturas (4k jpg,
# todos los mapas) y modelos (.blend 4k con sus texturas).
import json, os, sys, urllib.request, time
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) proyecto-casa-margot/1.0'}
SP = os.path.dirname(os.path.abspath(__file__))

def get_json(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
        return json.load(r)

def bajar(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        return os.path.getsize(dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    for intento in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r, open(dest + '.part', 'wb') as f:
                while True:
                    b = r.read(1 << 20)
                    if not b: break
                    f.write(b)
            os.replace(dest + '.part', dest)
            return os.path.getsize(dest)
        except Exception as e:
            print('   reintento', intento, dest, e, flush=True); time.sleep(3)
    raise RuntimeError('no se pudo bajar ' + url)

for aid in sys.argv[1:]:
    files = get_json(f'https://api.polyhaven.com/files/{aid}')
    carpeta = f'{SP}/{aid}'
    if 'hdri' in files:
        res = '8k' if '8k' in files['hdri'] else max(files['hdri'])
        u = files['hdri'][res]['hdr']['url']
        n = bajar(u, f'{carpeta}/{aid}_{res}.hdr')
        print(f'HDRI {aid} {res}: {n//1024//1024} MB', flush=True)
    elif 'blend' in files:
        res = '4k' if '4k' in files['blend'] else max(files['blend'])
        bl = files['blend'][res]['blend']
        n = bajar(bl['url'], f'{carpeta}/{aid}.blend')
        tot = n
        for rel, inf in bl.get('include', {}).items():
            tot += bajar(inf['url'], f'{carpeta}/{rel}')
        print(f'MODELO {aid} {res}: {tot//1024//1024} MB, {1+len(bl.get("include",{}))} ficheros', flush=True)
    else:
        tot, mapas = 0, []
        for mapa, resd in files.items():
            if mapa in ('blend', 'gltf', 'fbx', 'usd', 'mtlx'): continue
            res = '4k' if '4k' in resd else max(resd)
            fmts = resd[res]
            fmt = 'jpg' if 'jpg' in fmts else ('png' if 'png' in fmts else max(fmts))
            u = fmts[fmt]['url']
            tot += bajar(u, f'{carpeta}/{mapa}.{fmt}')
            mapas.append(f'{mapa}.{fmt}')
        print(f'TEXTURA {aid}: {tot//1024//1024} MB  {mapas}', flush=True)
print('DESCARGAS OK', flush=True)
