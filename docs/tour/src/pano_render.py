# Panoramicas equirectangulares 360 de la planta baja, calidad Cycles.
import os
os.environ['NAPOLI_NO_RENDER'] = '1'
exec(open('/home/user/modelo-2-italiano/blender_scene.py').read())
import math, sys

scene.cycles.samples = 128
scene.render.resolution_x = 3072
scene.render.resolution_y = 1536
scene.view_settings.exposure = -0.45   # mismo revelado que las vistas finales

PANOS = {
 'p_entrada':  (8.15, 1.55),
 'p_ventanal': (4.90, 2.20),
 'p_sala':     (3.05, 3.45),
 'p_mampara':  (2.30, 5.85),
 'p_barra':    (5.35, 6.10),
 'p_escalera': (7.55, 4.35),
 'p_tras_barra': (5.60, 7.95),
 'p_cocina':   (1.75, 7.55),
}

def render_pano(name, x, y):
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
    scene.render.filepath = os.path.join(
        '/tmp/claude-0/-home-user-modelo-2-italiano/30d2763c-3169-519a-ac78-c5a47134634b/scratchpad', name + '.png')
    bpy.ops.render.render(write_still=True)
    print('PANO OK', name, flush=True)

which = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(PANOS)
for k in which:
    px, py = PANOS[k]
    render_pano(k, px, py)
print('PANOS DONE', flush=True)
