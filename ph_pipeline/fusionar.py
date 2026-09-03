# Promedia las pasadas EXR de una vista (imagen + albedo + normal) y pasa el denoiser OIDN
# con la misma gestion de color que el render directo (AgX + look + exposicion).
#   python3 fusionar.py R_barra salida.png [max_pasadas]
import sys, glob, os, json, numpy as np, OpenEXR
os.chdir(os.path.dirname(os.path.abspath(__file__)))
vista, salida = sys.argv[1], sys.argv[2]
maxp = int(sys.argv[3]) if len(sys.argv) > 3 else 999
ficheros = sorted(glob.glob(f'../pasadas/{vista}_p*.exr'))[:maxp]
assert ficheros, 'no hay pasadas'
cfg = json.load(open('../pasadas/vista.json'))
acc = {}
for f in ficheros:
    with OpenEXR.File(f) as ex:
        for p in ex.parts:
            nm = p.name() if callable(p.name) else p.name
            ch = p.channels() if callable(p.channels) else p.channels
            a = np.asarray(ch[nm].pixels, dtype=np.float32)
            acc[nm] = acc.get(nm, 0) + a
n = len(ficheros)
for k in acc: acc[k] = acc[k] / n
print(f'   fusionadas {n} pasadas de {vista}; capas {[(k, v.shape) for k, v in acc.items()]}', flush=True)
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
h, w = acc['img'].shape[:2]
def imagen(nombre, arr):
    im = bpy.data.images.new(nombre, w, h, alpha=True, float_buffer=True)
    a = np.asarray(arr, dtype=np.float32)
    if a.shape[2] == 3: a = np.concatenate([a, np.ones_like(a[..., :1])], axis=-1)
    if nombre != 'img': a = a.copy(); a[..., 3] = 1.0
    a = a[::-1]                        # OpenEXR: fila 0 arriba; Blender: fila 0 abajo
    im.pixels.foreach_set(np.ascontiguousarray(a).ravel())
    return im
nt = bpy.data.node_groups.new('fusion', 'CompositorNodeTree'); sc.compositing_node_group = nt
sc.render.use_compositing = True; sc.render.use_sequencer = False
n_img = nt.nodes.new('CompositorNodeImage'); n_img.image = imagen('img', acc['img'])
n_den = nt.nodes.new('CompositorNodeDenoise')
for attr, val in (('use_hdr', True), ('prefilter', 'ACCURATE'), ('quality', 'HIGH')):
    try: setattr(n_den, attr, val)
    except Exception: pass
nt.links.new(n_img.outputs['Image'], n_den.inputs['Image'])
for capa, entrada in (('alb', 'Albedo'), ('nor', 'Normal')):
    if capa in acc and entrada in n_den.inputs:
        nd = nt.nodes.new('CompositorNodeImage'); nd.image = imagen(capa, acc[capa])
        nt.links.new(nd.outputs['Image'], n_den.inputs[entrada])
    else: print('   AVISO: sin', capa, entrada, [i.name for i in n_den.inputs])
nt.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
gout = nt.nodes.new('NodeGroupOutput'); nt.links.new(n_den.outputs['Image'], gout.inputs['Image'])
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera = cam
sc.render.engine = 'BLENDER_WORKBENCH'
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
sc.view_settings.view_transform = cfg['view_transform']; sc.view_settings.look = cfg['look']
sc.view_settings.exposure = cfg['exposure']; sc.view_settings.gamma = cfg['gamma']
# balance de blancos de la escena (blender_scene.py: 5600 K); si el json es antiguo, esos valores
try:
    sc.view_settings.use_white_balance = cfg.get('use_white_balance', True)
    sc.view_settings.white_balance_temperature = cfg.get('white_balance_temperature', 5600)
    sc.view_settings.white_balance_tint = cfg.get('white_balance_tint', sc.view_settings.white_balance_tint)
except Exception as e: print('   AVISO balance de blancos:', e)
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_depth = '16'
sc.render.image_settings.color_mode = 'RGB'
sc.render.filepath = os.path.abspath(os.path.join('..', salida))
bpy.ops.render.render(write_still=True)
print('FUSION OK', sc.render.filepath, f'({n} pasadas)', flush=True)
