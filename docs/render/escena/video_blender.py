"""Renderiza fotogramas del vuelo de dron dentro de Blender.

No se lanza a mano: lo lanza video.py, un proceso por tramo de fotogramas.

    blender --background --python video_blender.py -- --desde 1 --hasta 120
        --fps 60 --spp 2048 --umbral 0.005 --ancho 3840 --alto 2160
        --salida CARPETA [--gpu] [--prueba 1,4000,8000]

Monta la escena una vez, con la calle, abre la puerta de entrada, pone la
camara del dron fotograma a fotograma (dron.py) y renderiza el tramo. Los
fotogramas que ya estan en la carpeta se saltan, asi que si se corta no se
pierde nada de lo hecho.
"""
import argparse
import math
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import escena as ES  # noqa: E402
import dron  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

PATRON = 'dron_#####'           # dron_00001.png, dron_00002.png...


def abrir_puerta(angulo=80.0):
    """Las dos hojas de la puerta de la calle, abiertas hacia el cubo.

    Solo para el video, que el dron tiene que entrar: el modelo sigue con la
    puerta cerrada. Cada hoja gira sobre su canto de bisagra (el de la jamba)
    y queda pegada a su costado del cubo; a 80 grados y no a 90, para que el
    tirador de fuera no toque el vidrio del costado.
    """
    n = 0
    for pref, (px, py), signo in (('Puerta de acceso · hoja 1', (7.641, 1.380), -1),
                                  ('Puerta de acceso · hoja 2', (9.714, 1.380), 1)):
        M = (Matrix.Translation((px, py, 0.0))
             @ Matrix.Rotation(math.radians(signo * angulo), 4, 'Z')
             @ Matrix.Translation((-px, -py, 0.0)))
        for o in bpy.data.objects:
            if o.name.startswith(pref):
                o.matrix_world = M @ o.matrix_world
                n += 1
    return n


def camara_dron(fps):
    """La camara con un fotograma clave en cada fotograma, y la exposicion."""
    sc = bpy.context.scene
    datos = bpy.data.cameras.new('Dron')
    datos.lens = dron.LENTE
    datos.sensor_width = 36.0
    datos.clip_start = 0.02
    datos.clip_end = 250.0
    cam = bpy.data.objects.new('Dron', datos)
    sc.collection.objects.link(cam)
    cam.rotation_mode = 'QUATERNION'
    # claves lineales: con una por fotograma, las curvas de Bezier se pasan
    # de largo entre dos y el desenfoque de movimiento las veria
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
    fr = dron.fotogramas(fps)
    q_ant, e_ant = None, None
    for n, (p, d, e) in enumerate(fr, start=1):
        q = Vector(d).to_track_quat('-Z', 'Y')      # sin alabeo: horizonte recto
        if q_ant is not None and q_ant.dot(q) < 0:
            q.negate()                               # el mismo giro, sin dar la vuelta
        cam.location = p
        cam.rotation_quaternion = q
        cam.keyframe_insert('location', frame=n)
        cam.keyframe_insert('rotation_quaternion', frame=n)
        if e_ant is None or abs(e - e_ant) > 1e-4 or n == len(fr):
            sc.view_settings.exposure = e
            sc.view_settings.keyframe_insert('exposure', frame=n)
            e_ant = e
        q_ant = q
    sc.camera = cam
    return len(fr)


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--desde', type=int, default=1)
    ap.add_argument('--hasta', type=int, default=0)
    ap.add_argument('--fps', type=int, default=60)
    ap.add_argument('--spp', type=int, default=2048)
    ap.add_argument('--umbral', type=float, default=0.005)
    ap.add_argument('--ancho', type=int, default=3840)
    ap.add_argument('--alto', type=int, default=2160)
    ap.add_argument('--salida', required=True)
    ap.add_argument('--gpu', action='store_true')
    ap.add_argument('--prueba', default='', help='fotogramas sueltos, p. ej. 1,4000,8000')
    a = ap.parse_args(argv)

    ES.USAR_GPU = a.gpu
    salida = os.path.abspath(a.salida)
    os.makedirs(salida, exist_ok=True)
    print('Casa Margot · video de dron: montando la escena', flush=True)
    ES.construir(a.spp, a.ancho, a.alto, con_decoracion=True, con_glare=False,
                 con_ciudad=True)
    sc = bpy.context.scene
    sc.cycles.adaptive_threshold = a.umbral
    sc.cycles.use_animated_seed = True
    print('  puerta de la calle abierta:', abrir_puerta(), 'piezas', flush=True)
    total = camara_dron(a.fps)
    print(f'  camara del dron: {total} fotogramas a {a.fps} fps', flush=True)

    r = sc.render
    r.resolution_x, r.resolution_y, r.resolution_percentage = a.ancho, a.alto, 100
    r.fps = a.fps
    # el dron se mueve: un poco de desenfoque, como una camara a 1/120 s
    r.use_motion_blur = True
    r.motion_blur_shutter = 0.5
    # la escena no cambia entre fotogramas, solo la camara: se sube una vez
    # a la tarjeta y no en cada fotograma
    r.use_persistent_data = True
    r.image_settings.file_format = 'PNG'
    r.image_settings.color_mode = 'RGB'
    r.image_settings.color_depth = '8'
    r.image_settings.compression = 15
    r.use_overwrite = False                 # lo que ya esta hecho no se repite
    r.use_placeholder = False

    if a.prueba:
        for n in [int(x) for x in a.prueba.split(',') if x.strip()]:
            n = max(1, min(total, n))
            sc.frame_set(n)
            r.filepath = os.path.join(salida, f'prueba_{n:05d}.png')
            t = time.time()
            bpy.ops.render.render(write_still=True)
            print(f'PRUEBA fotograma {n}: {time.time() - t:.1f} s', flush=True)
        return

    sc.frame_start = max(1, a.desde)
    sc.frame_end = min(total, a.hasta or total)
    r.filepath = os.path.join(salida, PATRON)
    print(f'  renderizando {sc.frame_start}..{sc.frame_end} en {salida}', flush=True)
    bpy.ops.render.render(animation=True)
    print('TRAMO LISTO', flush=True)


if __name__ == '__main__':
    main()
