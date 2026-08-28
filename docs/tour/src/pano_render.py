"""Panoramicas equirectangulares del recorrido, sobre la planta reorganizada.
Reanudable: salta las que ya existen."""
import os, math, sys, time
os.environ['NAPOLI_NO_RENDER'] = '1'
exec(open('/home/user/modelo-2-italiano/blender_scene.py').read())

SP = '/tmp/claude-0/-home-user-modelo-2-italiano/30d2763c-3169-519a-ac78-c5a47134634b/scratchpad'
OUT = os.path.join(SP, 'panos')
os.makedirs(OUT, exist_ok=True)

scene.render.use_persistent_data = True
scene.cycles.samples = 192
scene.render.resolution_x = 3072
scene.render.resolution_y = 1536
scene.view_settings.exposure = -0.45

# Nueve posiciones, todas comprobadas contra la geometria: holgura minima
# 0,44 m y cada salto entre puntos es un recorrido realmente andable.
PANOS = {
    'p_entrada':    (8.20, 1.65),
    'p_ventanal':   (4.55, 2.15),
    'p_sala':       (5.60, 4.00),
    'p_barra':      (3.55, 4.40),
    'p_fondo':      (3.50, 6.60),
    'p_paso':       (1.55, 6.40),
    'p_tras_barra': (1.30, 3.60),
    'p_cocina':     (1.70, 7.80),
    'p_escalera':   (8.05, 4.50),
}

which = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(PANOS)
for k in which:
    dst = os.path.join(OUT, k + '.png')
    if os.path.exists(dst):
        print('YA HECHA', k, flush=True)
        continue
    x, y = PANOS[k]
    cd = bpy.data.cameras.new('p')
    cd.type = 'PANO'
    try:
        cd.panorama_type = 'EQUIRECTANGULAR'
    except Exception:
        cd.cycles.panorama_type = 'EQUIRECTANGULAR'
    cd.clip_start = 0.05
    cam = bpy.data.objects.new('pcam', cd)
    scene.collection.objects.link(cam)
    cam.location = (x, y, 1.55)
    cam.rotation_euler = (math.radians(90), 0, 0)   # centro de imagen = +Y
    scene.camera = cam
    scene.render.filepath = dst
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print('PANO OK', k, '%.0fs' % (time.time() - t), flush=True)
print('PANOS DONE', flush=True)
