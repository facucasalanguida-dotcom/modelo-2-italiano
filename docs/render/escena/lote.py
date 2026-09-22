#!/usr/bin/env python3
"""Renderiza varias vistas, cada una en su proceso.

Lo mismo que lote.sh pero sin bash, que en Windows no hay. Un proceso por
vista: montar la escena se come casi 6 GB, asi que si una se queda sin
memoria se pierde esa y no el lote entero, y la memoria vuelve al sistema
entre vista y vista.

    python lote.py --salida .\\renders --gpu
    python lote.py --salida ./renders --vistas alta,cocina --spp 192

Sin --vistas hace las quince de la serie. Se salta las que ya esten hechas,
asi que si se corta a media noche se relanza y sigue donde iba.

El recorrido de 20 fotos, de la calle al almacen de arriba y en orden
(CM_01_calle.png ... CM_20_almacen.png; las camaras estan en recorrido.py),
a la maxima calidad:

    python lote.py --recorrido --maxima --gpu --salida .\\recorrido

--maxima es 3840 x 2160, hasta 2048 muestras por pixel y un umbral de ruido
de 0,005 (el normal es 0,010): el muestreo adaptativo deja de insistir en
cada pixel en cuanto esta limpio, asi que las zonas faciles no gastan las
2048. Se puede subir mas con --spp 4096 o bajar el umbral con --umbral.
Tambien prueba las texturas a 4K; si una vista no sale con ellas (la
tarjeta se queda sin memoria) la repite con las de 2K. Con una tarjeta de
menos de 12 GB conviene saltarse ese intento: --sin-4k.

Busca el Blender solo. Si no lo encuentra -o si se prefiere- se le dice:

    python lote.py --blender "C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe"
"""
import argparse, glob, os, shutil, subprocess, sys, time

AQUI = os.path.dirname(os.path.abspath(__file__))
ESCENA = os.path.join(AQUI, 'escena.py')
sys.path.insert(0, AQUI)
import recorrido  # noqa: E402  (solo datos: las 20 camaras del recorrido)

SERIE = ['fachada', 'logo', 'escalera', 'escaparate', 'sillon', 'trasbarra',
         'cocina', 'barra', 'barra_frente', 'chopera', 'alta', 'alta_cowork',
         'alta_vacio', 'general', 'entrada']

# Sitios donde suele estar el ejecutable si no esta en el PATH.
CANDIDATOS = [
    r'C:\Program Files\Blender Foundation\Blender {v}\blender.exe',
    r'C:\Program Files\Blender Foundation\Blender\blender.exe',
    '/Applications/Blender.app/Contents/MacOS/Blender',
    '/usr/bin/blender', '/usr/local/bin/blender', '/snap/bin/blender',
]


def buscar_blender():
    p = shutil.which('blender')
    if p:
        return p
    for pat in CANDIDATOS:
        if '{v}' in pat:
            for v in ('5.4', '5.3', '5.2', '5.1', '5.0'):
                c = pat.format(v=v)
                if os.path.exists(c):
                    return c
        elif os.path.exists(pat):
            return pat
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--salida', default=os.path.join(AQUI, 'renders'))
    ap.add_argument('--vistas', default='', help='coma: alta,cocina,...')
    ap.add_argument('--recorrido', action='store_true',
                    help='las 20 fotos del recorrido, en orden (recorrido.py)')
    ap.add_argument('--maxima', action='store_true',
                    help='maxima calidad: 4K, hasta 2048 muestras, umbral 0,005 y '
                         'texturas a 4K si caben en la tarjeta')
    ap.add_argument('--sin-4k', action='store_true',
                    help='con --maxima, no probar las texturas a 4K (tarjetas de '
                         'menos de 12 GB)')
    ap.add_argument('--spp', type=int, default=None, help='muestras (96; 2048 con --maxima)')
    ap.add_argument('--umbral', type=float, default=None,
                    help='ruido tolerado por pixel (0,010; 0,005 con --maxima)')
    ap.add_argument('--ancho', type=int, default=3840)
    ap.add_argument('--alto', type=int, default=2160)
    ap.add_argument('--gpu', action='store_true')
    ap.add_argument('--blender', default='')
    ap.add_argument('--dry', action='store_true', help='solo enseña que lanzaria')
    a = ap.parse_args()
    if a.spp is None:
        a.spp = 2048 if a.maxima else 96
    if a.umbral is None:
        a.umbral = 0.005 if a.maxima else 0.010

    blender = a.blender or buscar_blender()
    if not blender and not a.dry:
        sys.exit('No encuentro Blender. Pasalo con --blender "ruta\\a\\blender.exe"')
    blender = blender or 'blender'          # en --dry solo se enseña la orden
    # absoluta: Blender resuelve las relativas contra el .blend, no contra el
    # directorio de trabajo, y '.\\renders' acababa en C:\\renders
    a.salida = os.path.abspath(os.path.expanduser(a.salida))
    os.makedirs(a.salida, exist_ok=True)
    vistas = [v.strip() for v in a.vistas.split(',') if v.strip()] or SERIE
    if a.recorrido:
        vistas = list(recorrido.NOMBRES)

    print(f'Blender : {blender}')
    print(f'Salida  : {a.salida}')
    print(f'Calidad : {a.ancho}x{a.alto}  {a.spp} muestras  umbral {a.umbral}  '
          f'{"GPU" if a.gpu else "CPU"}')
    print(f'Vistas  : {len(vistas)}\n', flush=True)

    # Con --maxima se prueba primero con las texturas a 4K (CM_4K=1): son
    # ~120 mapas de 4096 y piden unos 10 GB mas de memoria que las de 2K. Si
    # la vista no sale con ellas -tarjeta sin memoria- se repite esa vista con
    # las de 2K, y solo despues se bajan muestras. Si las 4K no estan bajadas
    # se sigue con las 2K todo el lote.
    usar_4k = a.maxima and not a.sin_4k
    sin_memoria_4k = 0
    hechas, fallos, t_lote = 0, [], time.time()
    for i, v in enumerate(vistas, 1):
        destino = os.path.join(a.salida, f'CM_{v}.png')
        if os.path.exists(destino):
            print(f'[{i}/{len(vistas)}] {v}: ya estaba', flush=True)
            hechas += 1
            continue
        intentos = [(a.spp, True), (a.spp, False), (a.spp // 2, False)]
        for n, (spp, k4) in enumerate(intentos):
            if k4 and not usar_4k:
                continue
            entorno = dict(os.environ)
            entorno.pop('CM_4K', None)
            if k4:
                entorno['CM_4K'] = '1'
            orden = [blender, '--background', '--python', ESCENA, '--',
                     '--vista', v, '--spp', str(spp), '--ancho', str(a.ancho),
                     '--alto', str(a.alto), '--umbral', str(a.umbral),
                     '--salida', a.salida]
            if a.gpu:
                orden.append('--gpu')
            if a.dry:
                print(('CM_4K=1 ' if k4 else '') +
                      ' '.join(f'"{o}"' if ' ' in o else o for o in orden))
                break
            tex = 'texturas 4K' if k4 else 'texturas 2K'
            if n and not (n == 1 and not usar_4k):
                # Se reintenta bajando texturas y luego muestras, nunca la
                # resolucion: la entrega saldria con vistas de dos tamaños.
                print(f'[{i}/{len(vistas)}] {v}: fallo; reintento con {spp} '
                      f'muestras y {tex}', flush=True)
            else:
                print(f'[{i}/{len(vistas)}] {v}: {time.strftime("%H:%M:%S")}  ({tex})',
                      flush=True)
            t0 = time.time()
            r = subprocess.run(orden, env=entorno)
            if r.returncode == 2:
                if k4:
                    print(f'[{i}/{len(vistas)}] {v}: no estan las texturas a 4K; '
                          'sigo con las de 2K', flush=True)
                    usar_4k = False
                    continue
                # Faltan los activos: le va a pasar a las quince, asi que se
                # para el lote entero en vez de encadenar quince fallos.
                sys.exit('\nLote parado: hay que bajar los activos primero.')
            if os.path.exists(destino):
                print(f'[{i}/{len(vistas)}] {v}: listo en '
                      f'{(time.time() - t0) / 60:.0f} min', flush=True)
                hechas += 1
                break
            if k4:
                # sin memoria para las 4K: esta vista, con las de 2K. Si les
                # pasa a dos, la tarjeta no da para ellas y el resto va a 2K
                sin_memoria_4k += 1
                if sin_memoria_4k >= 2:
                    print('  dos vistas sin sitio para las texturas a 4K: el resto '
                          'del lote, con las de 2K', flush=True)
                    usar_4k = False
                continue
            if r.returncode and time.time() - t0 < 60:
                # No es falta de memoria ni tiempo: se ha roto al montar, y con
                # la mitad de muestras se rompe igual. No se insiste, pero se
                # sigue con las demas: puede ser cosa de esta vista sola -la de
                # fachada es la unica que carga la ciudad y el HDRI de 8K- y
                # parar el lote por ella dejaria catorce sin hacer.
                print(f'[{i}/{len(vistas)}] {v}: se rompio al montar; sigo con '
                      'las demas. El error esta arriba', flush=True)
                fallos.append(v)
                break
        else:
            if not a.dry:
                fallos.append(v)
                print(f'[{i}/{len(vistas)}] {v}: NO SALE', flush=True)

    if not a.dry:
        print(f'\nLOTE TERMINADO  {hechas}/{len(vistas)} en '
              f'{(time.time() - t_lote) / 3600:.1f} h', flush=True)
        if fallos:
            print('  no salieron:', ', '.join(fallos), flush=True)
        for f in sorted(glob.glob(os.path.join(a.salida, 'CM_*.png'))):
            print(f'  {os.path.basename(f)}  {os.path.getsize(f) / 1e6:.0f} MB')


if __name__ == '__main__':
    main()
