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
(CM_01_calle.png ... CM_20_almacen.png; las camaras estan en recorrido.py):

    python lote.py --recorrido --gpu --salida .\\recorrido

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
    ap.add_argument('--spp', type=int, default=96)
    ap.add_argument('--ancho', type=int, default=3840)
    ap.add_argument('--alto', type=int, default=2160)
    ap.add_argument('--gpu', action='store_true')
    ap.add_argument('--blender', default='')
    ap.add_argument('--dry', action='store_true', help='solo enseña que lanzaria')
    a = ap.parse_args()

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
    print(f'Calidad : {a.ancho}x{a.alto}  {a.spp} muestras  '
          f'{"GPU" if a.gpu else "CPU"}')
    print(f'Vistas  : {len(vistas)}\n', flush=True)

    hechas, fallos, t_lote = 0, [], time.time()
    for i, v in enumerate(vistas, 1):
        destino = os.path.join(a.salida, f'CM_{v}.png')
        if os.path.exists(destino):
            print(f'[{i}/{len(vistas)}] {v}: ya estaba', flush=True)
            hechas += 1
            continue
        for spp in (a.spp, a.spp // 2):
            orden = [blender, '--background', '--python', ESCENA, '--',
                     '--vista', v, '--spp', str(spp), '--ancho', str(a.ancho),
                     '--alto', str(a.alto), '--salida', a.salida]
            if a.gpu:
                orden.append('--gpu')
            if a.dry:
                print(' '.join(f'"{o}"' if ' ' in o else o for o in orden))
                break
            if spp != a.spp:
                # Se reintenta bajando muestras, no resolucion: si se baja la
                # resolucion la entrega sale con vistas de dos tamaños.
                print(f'[{i}/{len(vistas)}] {v}: fallo; reintento con {spp}',
                      flush=True)
            else:
                print(f'[{i}/{len(vistas)}] {v}: {time.strftime("%H:%M:%S")}',
                      flush=True)
            t0 = time.time()
            r = subprocess.run(orden)
            if r.returncode == 2:
                # Faltan los activos: le va a pasar a las quince, asi que se
                # para el lote entero en vez de encadenar quince fallos.
                sys.exit('\nLote parado: hay que bajar los activos primero.')
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
            if os.path.exists(destino):
                print(f'[{i}/{len(vistas)}] {v}: listo en '
                      f'{(time.time() - t0) / 60:.0f} min', flush=True)
                hechas += 1
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
