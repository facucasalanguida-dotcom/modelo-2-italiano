"""Vistas cenital y axonometrica de la planta baja, sin forjado ni calle."""
import os, math, time
os.environ['NAPOLI_NO_RENDER'] = '1'
exec(open('/home/user/modelo-2-italiano/blender_scene.py').read())

col_pa.hide_render = True          # oculta forjado, cubierta y barandillas
scene.render.use_persistent_data = True
scene.cycles.samples = 48
scene.view_settings.exposure = -0.30
SP = '/tmp/claude-0/-home-user-modelo-2-italiano/30d2763c-3169-519a-ac78-c5a47134634b/scratchpad'

# El local ocupa x[0, 10.04] y[0, 9.16]. Todo lo que quede fuera es contexto
# urbano (aceras, calzada, edificios vecinos, farolas, arboles de la calle)
# y estorba en una vista de planta: se oculta.
fuera = 0
for ob in list(scene.objects):
    if ob.type != 'MESH':
        continue
    c = [sum(v) / 8 for v in zip(*[(ob.matrix_world @ Vector(v))[:] for v in ob.bound_box])]
    if not (-0.5 <= c[0] <= 10.6 and -0.5 <= c[1] <= 9.7):
        ob.hide_render = True
        fuera += 1
print('ocultados por estar fuera del local:', fuera, flush=True)

CX, CY = 5.01, 4.57
LADO = 10.06


def render_orto(fn, eye, target, escala, res):
    cd = bpy.data.cameras.new('o')
    cd.type = 'ORTHO'
    cd.ortho_scale = escala
    cd.clip_start = 0.1
    cd.clip_end = 200
    cam = bpy.data.objects.new('ocam', cd)
    scene.collection.objects.link(cam)
    cam.location = eye
    d = Vector(target) - Vector(eye)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]
    scene.render.filepath = os.path.join(SP, fn)
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print('VISTA OK', fn, '%.0fs' % (time.time() - t), flush=True)


# 1) cenital pura, norte arriba (el ventanal queda abajo)
render_orto('planta_cenital.png', (CX, CY, 14.0), (CX, CY, 0.0),
            LADO * 1.04, (1700, 1700))

# 2) axonometrica desde el sureste, para reconocer los muebles
render_orto('planta_axono.png', (CX + 8.0, CY - 9.0, 10.0), (CX, CY, 1.0),
            LADO * 1.22, (1800, 1350))
print('VISTAS DONE', flush=True)
