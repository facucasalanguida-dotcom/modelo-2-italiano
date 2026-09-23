#!/usr/bin/env python3
"""El video de dron por Casa Margot, renderizado en este PC.

Una sola toma tranquila de la calle a la planta alta (la trayectoria esta en
dron.py): 3840 x 2160 a 60 fotogramas por segundo. Se renderiza fotograma a
fotograma en PNG, por tramos -un proceso de Blender por tramo-, y al final se
juntan en un MP4. Si se corta, se relanza igual y sigue donde iba.

Primero, una prueba: renderiza tres fotogramas sueltos y dice cuanto tardaria
el video entero en este PC con esos ajustes.

    python video.py --prueba --maxima --gpu

Luego el video:

    python video.py --maxima --gpu

--maxima: hasta 2048 muestras por pixel, umbral de ruido 0,005 y recursos a lo
mas alto (texturas 4K, cielo 16K), como las fotos. Si la tarjeta no puede con
todo, baja de nivel solo, pero antes de empezar: el video entero sale con el
mismo nivel, que un cambio a mitad se notaria. Con --spp y --umbral se
afina (menos muestras o mas umbral = mas rapido). --fps 30 lo hace en la
mitad de tiempo.

Sale en la carpeta video\\: los fotogramas dron_00001.png... y, al terminar,
CasaMargot_dron.mp4. Los PNG ocupan unos 12 MB cada uno (unos 100 GB los
8.000); son el original, por si se quiere montar en un editor.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import dron  # noqa: E402  (solo la trayectoria: no necesita Blender)
from lote import buscar_blender  # noqa: E402

ENTORNO = {'maxima': {'CM_4K': '1', 'CM_MAXIMA': '1'}, '4k': {'CM_4K': '1'}, '2k': {}}
NOMBRE = {'maxima': 'calidad maxima', '4k': 'materiales a 4K', '2k': 'texturas a 2K'}


def png_bueno(ruta):
    """Un PNG entero: si Blender se corto escribiendolo, le falta el final."""
    try:
        if os.path.getsize(ruta) < 1000:
            return False
        with open(ruta, 'rb') as f:
            f.seek(-12, os.SEEK_END)
            return b'IEND' in f.read()
    except OSError:
        return False


def hechos(salida, total):
    ok = set()
    for n in range(1, total + 1):
        r = os.path.join(salida, f'dron_{n:05d}.png')
        if os.path.exists(r):
            if png_bueno(r):
                ok.add(n)
            else:
                os.remove(r)                 # a medias: se repite
    return ok


def lanzar(blender, script, args, nivel, lineas=None):
    """Lanza Blender y va enseñando lo que dice; si se pide, se lo guarda."""
    entorno = dict(os.environ)
    for k in ('CM_4K', 'CM_MAXIMA'):
        entorno.pop(k, None)
    entorno.update(ENTORNO[nivel])
    orden = [blender, '--background', '--python', os.path.join(AQUI, script), '--'] + args
    if lineas is None:
        return subprocess.run(orden, env=entorno).returncode
    p = subprocess.Popen(orden, env=entorno, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding='utf-8', errors='replace')
    for ln in p.stdout:
        print(ln, end='', flush=True)
        lineas.append(ln)
    return p.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--salida', default=os.path.join(AQUI, 'video'))
    ap.add_argument('--maxima', action='store_true')
    ap.add_argument('--sin-4k', action='store_true')
    ap.add_argument('--fps', type=int, default=60)
    ap.add_argument('--ancho', type=int, default=3840)
    ap.add_argument('--alto', type=int, default=2160)
    ap.add_argument('--spp', type=int, default=None, help='muestras (512; 2048 con --maxima)')
    ap.add_argument('--umbral', type=float, default=None,
                    help='ruido tolerado por pixel (0,010; 0,005 con --maxima)')
    ap.add_argument('--tramo', type=int, default=120, help='fotogramas por proceso')
    ap.add_argument('--gpu', action='store_true')
    ap.add_argument('--blender', default='')
    ap.add_argument('--prueba', action='store_true',
                    help='solo tres fotogramas y la cuenta de cuanto tardaria todo')
    ap.add_argument('--montar', action='store_true', help='solo juntar los PNG en el MP4')
    ap.add_argument('--codec', default='H264', choices=('H264', 'H265'))
    a = ap.parse_args()
    a.spp = a.spp or (2048 if a.maxima else 512)
    a.umbral = a.umbral or (0.005 if a.maxima else 0.010)

    blender = a.blender or buscar_blender()
    if not blender:
        sys.exit('No encuentro Blender. Pasalo con --blender "ruta\\a\\blender.exe"')
    salida = os.path.abspath(os.path.expanduser(a.salida))
    os.makedirs(salida, exist_ok=True)
    r = dron.resumen(a.fps)
    total = r['fotogramas']
    mp4 = os.path.join(salida, 'CasaMargot_dron.mp4')
    print(f'Blender : {blender}')
    print(f'Salida  : {salida}')
    print(f'Video   : {r["segundos"]} s, {total} fotogramas a {a.fps} fps, '
          f'{a.ancho}x{a.alto}, {r["metros"]} m de vuelo')
    print(f'Calidad : {a.spp} muestras, umbral {a.umbral}, '
          f'{"GPU" if a.gpu else "CPU"}\n', flush=True)
    comun = ['--fps', str(a.fps), '--spp', str(a.spp), '--umbral', str(a.umbral),
             '--ancho', str(a.ancho), '--alto', str(a.alto), '--salida', salida]
    if a.gpu:
        comun.append('--gpu')

    # el nivel de texturas: el mismo para todo el video
    f_nivel = os.path.join(salida, 'nivel.json')
    niveles = ['maxima', '4k', '2k'] if (a.maxima and not a.sin_4k) else ['2k']
    fijo = None
    if os.path.exists(f_nivel):
        fijo = json.load(open(f_nivel, encoding='utf-8')).get('nivel')
        niveles = [fijo]

    if a.montar:
        sys.exit(lanzar(blender, 'montar_video.py', ['--carpeta', salida, '--fps', str(a.fps),
                                                      '--salida', mp4, '--codec', a.codec], '2k'))

    if a.prueba:
        # principio (calle), mitad (planta baja) y final (planta alta)
        muestras = [max(2, total // 12), total // 2, total - total // 10]
        for nivel in niveles:
            print(f'PRUEBA con {NOMBRE[nivel]}: fotogramas {muestras}', flush=True)
            lineas = []
            rc = lanzar(blender, 'video_blender.py',
                        comun + ['--prueba', ','.join(map(str, muestras))], nivel, lineas)
            fotos = [os.path.join(salida, f'prueba_{n:05d}.png') for n in muestras]
            if rc == 0 and all(os.path.exists(f) for f in fotos):
                break
            if rc == 2 and nivel != '2k':
                niveles = ['2k']
            print(f'  con {NOMBRE[nivel]} no sale; pruebo un nivel por debajo', flush=True)
        else:
            sys.exit('La prueba no sale: mira el error de arriba.')
        # el primero lleva ademas el subir la escena a la tarjeta: cuentan los otros
        ts = [float(m.group(1)) for ln in lineas
              for m in [re.search(r'PRUEBA fotograma \d+: ([\d.]+) s', ln)] if m]
        por = sum(ts[1:]) / len(ts[1:]) if len(ts) > 1 else (ts[0] if ts else 0)
        horas = por * total / 3600
        print(f'\nCON {NOMBRE[nivel].upper()}: unos {por:.0f} s por fotograma -> el video '
              f'entero, unas {horas:.0f} h ({horas / 24:.1f} dias) en este PC.', flush=True)
        print(f'Las tres imagenes de prueba estan en {salida}.', flush=True)
        return

    t_ini = time.time()
    while True:
        ok = hechos(salida, total)
        falta = [n for n in range(1, total + 1) if n not in ok]
        if not falta:
            break
        a0 = falta[0]
        a1 = min(total, a0 + a.tramo - 1)
        nivel = niveles[0]
        print(f'[{len(ok)}/{total}] tramo {a0}..{a1}  ({NOMBRE[nivel]})  '
              f'{time.strftime("%H:%M:%S")}', flush=True)
        rc = lanzar(blender, 'video_blender.py',
                    comun + ['--desde', str(a0), '--hasta', str(a1)], nivel)
        nuevos = hechos(salida, total) - ok
        if nuevos:
            if fijo is None:
                fijo = nivel
                json.dump({'nivel': nivel}, open(f_nivel, 'w', encoding='utf-8'))
            continue
        if rc == 2 and nivel != '2k':
            print('  no estan las texturas a 4K: el video va con las de 2K', flush=True)
            niveles = ['2k']
            continue
        if fijo is None and len(niveles) > 1:
            print(f'  con {NOMBRE[nivel]} no sale ni un fotograma; bajo un nivel', flush=True)
            niveles = niveles[1:]
            continue
        sys.exit(f'\nEl tramo {a0}..{a1} no sale (error arriba). Lo hecho se queda: '
                 'al relanzar sigue desde ahi.')
    print(f'\nFOTOGRAMAS COMPLETOS ({total}) en {(time.time() - t_ini) / 3600:.1f} h. '
          'Montando el MP4...', flush=True)
    rc = lanzar(blender, 'montar_video.py', ['--carpeta', salida, '--fps', str(a.fps),
                                             '--salida', mp4, '--codec', a.codec], '2k')
    print(f'\nVIDEO: {mp4}' if rc == 0 and os.path.exists(mp4)
          else '\nNo se pudo montar el MP4: python video.py --montar lo reintenta.')


if __name__ == '__main__':
    main()
