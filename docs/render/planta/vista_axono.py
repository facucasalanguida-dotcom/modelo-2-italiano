"""Axonometrica de la planta baja: sin forjado, sin calle y sin los muros
que quedan del lado de la camara (este y coronacion sur)."""
import os, time
os.environ['NAPOLI_NO_RENDER'] = '1'
exec(open('/home/user/modelo-2-italiano/blender_scene.py').read())

col_pa.hide_render = True
scene.render.use_persistent_data = True
scene.cycles.samples = 48
scene.view_settings.exposure = -0.30
SP = '/tmp/claude-0/-home-user-modelo-2-italiano/30d2763c-3169-519a-ac78-c5a47134634b/scratchpad'

# contexto urbano fuera
for ob in list(scene.objects):
    if ob.type != 'MESH':
        continue
    c = [sum(v) / 8 for v in zip(*[(ob.matrix_world @ Vector(v))[:] for v in ob.bound_box])]
    if not (-0.5 <= c[0] <= 10.6 and -0.5 <= c[1] <= 9.7):
        ob.hide_render = True

# muros del lado de la camara: taparian el interior
TAPAN = ('Medianera Este', 'Medianera Este - cuello',
         'Ventanal Sur - peto alto', 'Ventanal Sur - banda de rotulo',
         'Ventanal Sur - cabecero', 'Toldo', 'Toldo - faldon')
n = 0
for ob in scene.objects:
    if ob.name in TAPAN or ob.name.startswith(('Toldo', 'Rotulo')):
        ob.hide_render = True
        n += 1
print('muros/toldo ocultados:', n, flush=True)

cd = bpy.data.cameras.new('o')
cd.type = 'ORTHO'
cd.ortho_scale = 15.4
cd.clip_start = 0.1
cd.clip_end = 200
cam = bpy.data.objects.new('ocam', cd)
scene.collection.objects.link(cam)
cam.location = (5.01 + 7.5, 4.57 - 8.5, 13.5)     # sureste, ~52 grados
d = Vector((5.01, 4.57, 1.0)) - Vector(cam.location)
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam
scene.render.resolution_x = 1800
scene.render.resolution_y = 1350
scene.render.filepath = os.path.join(SP, 'planta_axono.png')
t = time.time()
bpy.ops.render.render(write_still=True)
print('VISTA OK axono %.0fs' % (time.time() - t), flush=True)
print('VISTAS DONE', flush=True)
