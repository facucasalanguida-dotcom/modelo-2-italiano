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

El recorrido de 26 fotos, de la calle al almacen de arriba y en orden
(CM_01_calle.png ... CM_20_almacen.png; despues la barra y la cocina por
dentro y las dos plantas cenitales, CM_21 ... CM_26; las camaras estan en
recorrido.py), a la maxima calidad:

    python lote.py --recorrido --maxima --gpu --salida .\\recorrido

Solo las seis ultimas (21-26), si las 20 primeras ya estan hechas:

    python lote.py --vistas 21_barra_dentro,22_trasbarra,23_cocina_fondo,24_cocina_linea,25_planta_baja,26_planta_alta --gpu --spp 512 --salida .\\recorrido

--maxima es 3840 x 2160, hasta 2048 muestras por pixel y un umbral de ruido
de 0,005 (el normal es 0,010): el muestreo adaptativo deja de insistir en
cada pixel en cuanto esta limpio, asi que las zonas faciles no gastan las
2048. Se puede subir mas con --spp 4096 o bajar el umbral con --umbral.
Y los recursos, a lo mas alto que hay: texturas de materiales y modelos a
4K, cielo a 16K y arboles con todo su detalle. Eso pide una tarjeta de 16 a
24 GB; si una vista no sale, se repite sola con los materiales a 4K y lo
demas normal, y si tampoco, con todo a 2K. --sin-4k va directo a 2K.

Busca el Blender solo. Si no lo encuentra -o si se prefiere- se le dice:

    python lote.py --blender "C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe"
"""
import argparse, glob, os, shutil, subprocess, sys, time

AQUI = os.path.dirname(os.path.abspath(__file__))
ESCENA = os.path.join(AQUI, 'escena.py')
sys.path.insert(0, AQUI)
import recorrido  # noqa: E402  (solo datos: las camaras del recorrido)

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
                    help='las 26 fotos del recorrido, en orden (recorrido.py)')
    ap.add_argument('--maxima', action='store_true',
                    help='maxima calidad: 4K, hasta 2048 muestras, umbral 0,005 y '
                         'recursos a lo mas alto (texturas 4K, cielo 16K) si caben')
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

    # Niveles de calidad, de mas a menos. Con --maxima cada vista se prueba
    # primero con todo a lo mas alto (CM_MAXIMA y CM_4K: texturas de los
    # materiales y de los modelos a 4K, cielo a 16K, arboles con todo su
    # detalle). Si no sale -la tarjeta se queda sin memoria- se repite con
    # solo los materiales a 4K, luego con todo a 2K y, por ultimo, con la
    # mitad de muestras. Un nivel que falla en dos vistas ya no se prueba en
    # las demas. Si faltan las texturas a 4K se sigue a 2K sin parar el lote.
    ENTORNO = {'maxima': {'CM_4K': '1', 'CM_MAXIMA': '1'}, '4k': {'CM_4K': '1'}, '2k': {}}
    NOMBRE = {'maxima': 'calidad maxima', '4k': 'materiales a 4K', '2k': 'texturas a 2K'}
    niveles = ['maxima', '4k', '2k'] if (a.maxima and not a.sin_4k) else ['2k']
    sin_memoria = {}
    hechas, fallos, t_lote = 0, [], time.time()
    for i, v in enumerate(vistas, 1):
        destino = os.path.join(a.salida, f'CM_{v}.png')
        if os.path.exists(destino):
            print(f'[{i}/{len(vistas)}] {v}: ya estaba', flush=True)
            hechas += 1
            continue
        intentos = [(a.spp, n) for n in ('maxima', '4k', '2k')] + [(a.spp // 2, '2k')]
        primero = True
        for spp, nivel in intentos:
            if nivel not in niveles:
                continue
            entorno = dict(os.environ)
            for k in ('CM_4K', 'CM_MAXIMA'):
                entorno.pop(k, None)
            entorno.update(ENTORNO[nivel])
            orden = [blender, '--background', '--python', ESCENA, '--',
                     '--vista', v, '--spp', str(spp), '--ancho', str(a.ancho),
                     '--alto', str(a.alto), '--umbral', str(a.umbral),
                     '--salida', a.salida]
            if a.gpu:
                orden.append('--gpu')
            if a.dry:
                print(' '.join(f'{k}={x}' for k, x in ENTORNO[nivel].items()) + ' ' +
                      ' '.join(f'"{o}"' if ' ' in o else o for o in orden))
                break
            if primero:
                print(f'[{i}/{len(vistas)}] {v}: {time.strftime("%H:%M:%S")}  '
                      f'({NOMBRE[nivel]}, {spp} muestras)', flush=True)
            else:
                # Se reintenta bajando calidad de texturas y luego muestras,
                # nunca la resolucion: la entrega saldria con dos tamaños.
                print(f'[{i}/{len(vistas)}] {v}: fallo; reintento con '
                      f'{NOMBRE[nivel]} y {spp} muestras', flush=True)
            primero = False
            t0 = time.time()
            r = subprocess.run(orden, env=entorno)
            if r.returncode == 2:
                if nivel != '2k':
                    print(f'[{i}/{len(vistas)}] {v}: no estan las texturas a 4K; '
                          'el lote sigue con las de 2K', flush=True)
                    niveles = ['2k']
                    continue
                # Faltan los activos: le va a pasar a todas, asi que se para
                # el lote entero en vez de encadenar fallos.
                sys.exit('\nLote parado: hay que bajar los activos primero '
                         '(python preparar_activos.py).')
            if os.path.exists(destino):
                print(f'[{i}/{len(vistas)}] {v}: listo en '
                      f'{(time.time() - t0) / 60:.0f} min', flush=True)
                hechas += 1
                break
            if nivel != '2k':
                sin_memoria[nivel] = sin_memoria.get(nivel, 0) + 1
                if sin_memoria[nivel] >= 2 and nivel in niveles:
                    niveles.remove(nivel)
                    print(f'  dos vistas sin sitio para "{NOMBRE[nivel]}": el resto '
                          'del lote empieza un nivel mas abajo', flush=True)
                continue
            if r.returncode and time.time() - t0 < 60:
                # No es falta de memoria ni tiempo: se ha roto al montar, y con
                # la mitad de muestras se rompe igual. No se insiste, pero se
                # sigue con las demas: puede ser cosa de esta vista sola -las
                # de calle son las unicas que cargan la ciudad y el cielo- y
                # parar el lote por ella dejaria las demas sin hacer.
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
