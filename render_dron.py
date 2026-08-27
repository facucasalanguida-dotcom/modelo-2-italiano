"""Render del vuelo de dron por la planta baja. Reanudable.

Salta los fotogramas ya escritos, asi que una interrupcion cuesta como
mucho el fotograma en curso.

Variables de entorno:
  NAP_OUT     carpeta de salida            (obligatoria)
  NAP_W/NAP_H resolucion                   (def. 1280x720)
  NAP_SMP     muestras Cycles              (def. 32)
  NAP_N       numero total de fotogramas   (def. 240)
  NAPOLI_LOW  1 = geometria ligera (previsualizacion)
"""
import os, sys, time, math

OUT = os.environ['NAP_OUT']
W = int(os.environ.get('NAP_W', 1280))
H = int(os.environ.get('NAP_H', 720))
SMP = int(os.environ.get('NAP_SMP', 32))
N = int(os.environ.get('NAP_N', 240))
os.makedirs(OUT, exist_ok=True)


def orden_progresivo(n):
    """Extremos, luego el punto medio de cada hueco.

    En cualquier instante los fotogramas ya calculados estan repartidos por
    TODO el vuelo: siempre hay un video completo, cada vez mas fluido, y no
    se repite ni un fotograma.
    """
    from collections import deque
    out, vistos = [0, n - 1], {0, n - 1}
    cola = deque([(0, n - 1)])
    while cola:
        a, b = cola.popleft()
        m = (a + b) // 2
        if a < m < b and m not in vistos:
            vistos.add(m)
            out.append(m)
            cola.append((a, m))
            cola.append((m, b))
    out += [i for i in range(n) if i not in vistos]
    return out


pendientes = [i for i in orden_progresivo(N)
              if not os.path.exists(f'{OUT}/f_{i:04d}.png')]
if not pendientes:
    print('VIDEO DONE (nada pendiente)', flush=True)
    sys.exit(0)
print(f'PENDIENTES {len(pendientes)}/{N}', flush=True)

os.environ['NAPOLI_NO_RENDER'] = '1'
t0 = time.time()
exec(open('/home/user/modelo-2-italiano/blender_scene.py').read())
print(f'ESCENA CARGADA {time.time() - t0:.0f}s', flush=True)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ruta_dron import camara

scene.render.use_persistent_data = True      # solo se mueve la camara
scene.cycles.samples = SMP
scene.render.resolution_x = W
scene.render.resolution_y = H
scene.view_settings.exposure = -0.45         # mismo revelado que los renders fijos

cd = bpy.data.cameras.new('drone')
cd.lens = 20                                 # gran angular, look de dron
cd.clip_start = 0.03
cam = bpy.data.objects.new('dronecam', cd)
scene.collection.objects.link(cam)
scene.camera = cam

for k, i in enumerate(pendientes):
    pos, mira = camara(i / (N - 1))
    cam.location = pos
    d = [mira[j] - pos[j] for j in range(3)]
    cam.rotation_euler = (math.atan2(math.hypot(d[0], d[1]), -d[2]), 0,
                          math.atan2(d[1], d[0]) - math.pi / 2)
    scene.render.filepath = f'{OUT}/f_{i:04d}.png'
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print(f'FRAME {i:04d} ({k + 1}/{len(pendientes)}) {time.time() - t:.0f}s', flush=True)
print('VIDEO DONE', flush=True)
