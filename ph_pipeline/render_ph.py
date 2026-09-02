# Render "nivel superior": construye la escena base (blender_scene.py) y le
# aplica los recursos reales de Poly Haven (CC0): HDRI de calle, texturas
# escaneadas 4K, bisel global, desgaste, y modelos reales de plantas,
# arboles y botellas. Camara identica a la vista original para comparar.
import os, sys, math, glob, random
os.environ['NAPOLI_NO_RENDER'] = '1'
REPO = '/home/user/modelo-2-italiano'
SP   = '/tmp/claude-0/-home-user-modelo-2-italiano/30d2763c-3169-519a-ac78-c5a47134634b/scratchpad'
PH   = f'{SP}/ph'
os.chdir('/tmp/claude-0/-home-user-modelo-2-italiano/30d2763c-3169-519a-ac78-c5a47134634b/scratchpad')          # blender_scene.py lee solids.json del directorio actual

VISTA   = os.environ.get('PH_VISTA', 'R_barra')
PREVIEW = bool(os.environ.get('PH_PREVIEW'))
HDRI_ROT = float(os.environ.get('PH_ROT', '-102.5'))     # grados, eje Z
HDRI_STR = float(os.environ.get('PH_STR', '3.0'))
EXPO     = float(os.environ.get('PH_EXPO', '0.0'))
SALIDA   = os.environ.get('PH_OUT', f'ph_{VISTA}.png')

ns = {'PH_EXPO_VAL': EXPO}      # render_view importa os al final: no usar os alli
src = open(f'{REPO}/blender_scene.py').read()
src = src.replace("scene.view_settings.exposure = -0.35 if hide_pa else -0.45",
                  "scene.view_settings.exposure = PH_EXPO_VAL")
src = src.replace("def silla_real(cx, cy, ang, tela):", "def _silla_real_o(cx, cy, ang, tela):")
src = src.replace("def mesa_real(cx, cy):", '''SILLAS_REG, TABUR_REG = [], []
def silla_real(cx, cy, ang, tela):
    antes = set(o.name for o in bpy.data.objects)
    _silla_real_o(cx, cy, ang, tela)
    SILLAS_REG.append((ang, tela.name, [o for o in bpy.data.objects if o.name not in antes]))

def mesa_real(cx, cy):''')
src = src.replace("def taburete(cx, cy):", "def _taburete_o(cx, cy):")
src = src.replace("def box3(name, x0, y0, x1, y1, z0, z1, mat):", '''def taburete(cx, cy):
    antes = set(o.name for o in bpy.data.objects)
    _taburete_o(cx, cy)
    TABUR_REG.append([o for o in bpy.data.objects if o.name not in antes])

def box3(name, x0, y0, x1, y1, z0, z1, mat):''')
exec(compile(src, 'blender_scene.py', 'exec'), ns)
bpy, scene, col_pb = ns['bpy'], ns['scene'], ns['col_pb']
plantas, botellas = ns['plantas'], ns['botellas']
print('escena base construida:', len(bpy.data.objects), 'objetos', flush=True)

# =============================================================== utilidades
_img = {}
def imagen(path, noncolor=False):
    key = (path, noncolor)
    if key not in _img:
        im = bpy.data.images.load(path)
        if noncolor: im.colorspace_settings.name = 'Non-Color'
        _img[key] = im
    return _img[key]

def mapas(aid):
    d = f'{PH}/{aid}/textures'
    def uno(pat):
        c = sorted(glob.glob(f'{d}/{aid}_{pat}_4k.*'), key=lambda x: (not x.endswith('.png'), x))
        return c[0] if c else None
    return {'diff': uno('diff'), 'rough': uno('rough'), 'nrm': uno('nor_gl'),
            'ao': uno('ao'), 'disp': uno('disp')}

def nodo_hacia(nt, socket_name, node_type=None):
    """Nodo enlazado a la entrada `socket_name` del Principled."""
    b = nt.nodes['Principled BSDF']
    for l in nt.links:
        if l.to_node == b and l.to_socket.name == socket_name:
            n = l.from_node
            if node_type is None or n.bl_idname == node_type: return n
            return n
    return None

def retex(nombre, aid, tam_m, tint=None, nrm_str=1.0, variar_rug=0.0, ao_fac=0.55):
    """Sustituye las texturas procedurales de un material pbr_tex por las
    escaneadas de Poly Haven, conservando el resto del arbol de nodos."""
    m = bpy.data.materials.get(nombre)
    if not m: print('   (no existe material', nombre, ')'); return
    nt, b = m.node_tree, m.node_tree.nodes['Principled BSDF']
    mp = mapas(aid)
    for n in nt.nodes:
        if n.bl_idname == 'ShaderNodeMapping':
            n.inputs['Scale'].default_value = (1/tam_m, 1/tam_m, 1/tam_m)
    # que imagen alimenta que
    for l in list(nt.links):
        if l.from_node.bl_idname != 'ShaderNodeTexImage': continue
        dst = l.to_node
        if dst == b and l.to_socket.name == 'Base Color' or dst.bl_idname == 'ShaderNodeMix':
            if mp['diff']: l.from_node.image = imagen(mp['diff'])
        elif dst == b and l.to_socket.name == 'Roughness':
            if mp['rough']: l.from_node.image = imagen(mp['rough'], True)
        elif dst.bl_idname == 'ShaderNodeNormalMap':
            if mp['nrm']:
                l.from_node.image = imagen(mp['nrm'], True)
                dst.inputs['Strength'].default_value = nrm_str
    # tinte
    if tint is not None:
        for n in nt.nodes:
            if n.bl_idname == 'ShaderNodeMix' and n.blend_type == 'MULTIPLY':
                n.inputs[7].default_value = (*tint, 1)
    # oclusion ambiental escaneada multiplicando el color
    if mp['ao']:
        src_link = next((l for l in nt.links if l.to_node == b and l.to_socket.name == 'Base Color'), None)
        if src_link:
            mapn = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeMapping')
            aoi = nt.nodes.new('ShaderNodeTexImage'); aoi.image = imagen(mp['ao'], True)
            aoi.projection = 'BOX'; aoi.projection_blend = 0.3
            nt.links.new(mapn.outputs['Vector'], aoi.inputs['Vector'])
            mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
            mx.inputs['Factor'].default_value = ao_fac
            nt.links.new(src_link.from_socket, mx.inputs[6]); nt.links.new(aoi.outputs['Color'], mx.inputs[7])
            nt.links.remove(src_link); nt.links.new(mx.outputs[2], b.inputs['Base Color'])
    # variacion de rugosidad (desgaste, manchas de uso)
    if variar_rug > 0:
        rl = next((l for l in nt.links if l.to_node == b and l.to_socket.name == 'Roughness'), None)
        if rl:
            ns_ = nt.nodes.new('ShaderNodeTexNoise'); ns_.inputs['Scale'].default_value = 2.5
            ns_.inputs['Detail'].default_value = 6.0
            mr = nt.nodes.new('ShaderNodeMapRange')
            mr.inputs['From Min'].default_value = 0.3; mr.inputs['From Max'].default_value = 0.7
            mr.inputs['To Min'].default_value = 1 - variar_rug; mr.inputs['To Max'].default_value = 1 + variar_rug
            nt.links.new(ns_.outputs['Fac'], mr.inputs['Value'])
            mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.use_clamp = True
            nt.links.new(rl.from_socket, mul.inputs[0]); nt.links.new(mr.outputs['Result'], mul.inputs[1])
            nt.links.remove(rl); nt.links.new(mul.outputs['Value'], b.inputs['Roughness'])
    print('   retex', nombre, '<-', aid, flush=True)

def pbr_ph(nombre, aid, tam_m, tint=None):
    """Material nuevo completo a partir de un set escaneado."""
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    nt, b = m.node_tree, m.node_tree.nodes['Principled BSDF']
    mp = mapas(aid)
    tc = nt.nodes.new('ShaderNodeTexCoord'); mpn = nt.nodes.new('ShaderNodeMapping')
    mpn.inputs['Scale'].default_value = (1/tam_m,)*3
    nt.links.new(tc.outputs['Object'], mpn.inputs['Vector'])
    def img(p, nc):
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = imagen(p, nc)
        n.projection = 'BOX'; n.projection_blend = 0.3
        nt.links.new(mpn.outputs['Vector'], n.inputs['Vector']); return n
    d = img(mp['diff'], False)
    if tint:
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
        mx.inputs['Factor'].default_value = 1.0; mx.inputs[7].default_value = (*tint, 1)
        nt.links.new(d.outputs['Color'], mx.inputs[6]); nt.links.new(mx.outputs[2], b.inputs['Base Color'])
    else:
        nt.links.new(d.outputs['Color'], b.inputs['Base Color'])
    if mp['rough']: nt.links.new(img(mp['rough'], True).outputs['Color'], b.inputs['Roughness'])
    if mp['nrm']:
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 1.0
        nt.links.new(img(mp['nrm'], True).outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    return m

def reasignar(nombre_viejo, m_nuevo, solo_objetos=None):
    for ob in bpy.data.objects:
        if ob.type != 'MESH': continue
        if solo_objetos and not any(ob.name.startswith(s) for s in solo_objetos): continue
        for sl in ob.material_slots:
            if sl.material and sl.material.name == nombre_viejo: sl.material = m_nuevo

# ========================================================= 1. luz: HDRI real
print('1. HDRI', flush=True)
hdr = glob.glob(f'{PH}/wide_street_01/*.hdr')[0]
w = scene.world; nt = w.node_tree; nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground')
env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(hdr)
tc = nt.nodes.new('ShaderNodeTexCoord'); mpw = nt.nodes.new('ShaderNodeMapping')
mpw.inputs['Rotation'].default_value = (0, 0, math.radians(HDRI_ROT))
nt.links.new(tc.outputs['Generated'], mpw.inputs['Vector']); nt.links.new(mpw.outputs['Vector'], env.inputs['Vector'])
nt.links.new(env.outputs['Color'], bg.inputs['Color'])
bg.inputs['Strength'].default_value = HDRI_STR
bgc = nt.nodes.new('ShaderNodeBackground'); nt.links.new(env.outputs['Color'], bgc.inputs['Color'])
bgc.inputs['Strength'].default_value = float(os.environ.get('PH_STR_CAM', '1.4'))
lp = nt.nodes.new('ShaderNodeLightPath'); mixw = nt.nodes.new('ShaderNodeMixShader')
nt.links.new(lp.outputs['Is Camera Ray'], mixw.inputs['Fac'])
nt.links.new(bg.outputs['Background'], mixw.inputs[1]); nt.links.new(bgc.outputs['Background'], mixw.inputs[2])
nt.links.new(mixw.outputs['Shader'], out.inputs['Surface'])
# fuera el sol y los paneles que fingian la luz de dia; los rellenos altos, a la mitad
for ob in list(bpy.data.objects):
    if ob.type != 'LIGHT': continue
    ld = ob.data
    if ld.type == 'SUN': bpy.data.objects.remove(ob); continue
    if ld.type == 'AREA' and ld.energy in (300, 150) and ob.location.y < 2.0: bpy.data.objects.remove(ob); continue
    if ld.type == 'AREA': ld.energy *= 0.5

for nm_ in ('edificio_A', 'edificio_B', 'edificio_C'):
    ob = bpy.data.objects.get(nm_)
    if ob: bpy.data.objects.remove(ob)
print('   edificios de caja retirados', flush=True)

# =============================================== 2. materiales escaneados 4K
print('2. materiales', flush=True)
retex('suelo',    'wood_floor',       1.70, tint=(1.0, 0.96, 0.90), variar_rug=0.18)
retex('tablero',  'oak_veneer_01',    1.83, tint=(0.88, 0.72, 0.56), variar_rug=0.12)
retex('pata_madera', 'oak_veneer_01', 1.83, tint=(0.90, 0.76, 0.60))
retex('clara',    'oak_veneer_01',    1.83, tint=(1.0, 1.0, 1.0))
retex('liston',   'oak_veneer_01',    1.83, tint=None, variar_rug=0.10)
retex('napoli',   'oak_veneer_01',    1.83, tint=None, nrm_str=0.55, variar_rug=0.20)
for nm_, tint_ in (('muro', (1.10, 1.04, 0.94)), ('tabique', (1.10, 1.07, 1.00)),
                   ('techo', (1.08, 1.07, 1.04)), ('blanco', (1.10, 1.09, 1.06)),
                   ('medianera', (0.98, 0.96, 0.93))):
    retex(nm_, 'white_plaster_02', 1.0, tint=tint_, nrm_str=0.6)
retex('hormigon', 'plastered_wall',   2.0, tint=(0.86, 0.85, 0.83))
retex('piedra',   'granite_tile',     2.3, tint=None, variar_rug=0.10)
retex('acera_tx', 'large_floor_tiles_02', 3.0, tint=(1.02, 0.99, 0.94))
retex('toldo',    'denim_fabric',      0.35, tint=None, nrm_str=0.5)
reasignar('asfalto', pbr_ph('asfalto_ph', 'asphalt_02', 3.0))
reasignar('acera_tx', pbr_ph('soportal_ph', 'concrete_floor_worn_001', 3.0, tint=(1.02, 0.98, 0.92)), ['soportal'])
# acero cepillado anisotropo y laton con velo de uso
for nm_, rug, ani in (('inox', 0.20, 0.45), ('laton', 0.30, 0.30)):
    m = bpy.data.materials.get(nm_)
    if m:
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Roughness'].default_value = rug
        if 'Anisotropic' in b.inputs: b.inputs['Anisotropic'].default_value = ani
        nt_ = m.node_tree
        ns_ = nt_.nodes.new('ShaderNodeTexNoise'); ns_.inputs['Scale'].default_value = 90
        ns_.inputs['Detail'].default_value = 3.0
        mr = nt_.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = 0.30; mr.inputs['From Max'].default_value = 0.70
        mr.inputs['To Min'].default_value = rug * 0.92; mr.inputs['To Max'].default_value = rug * 1.12
        nt_.links.new(ns_.outputs['Fac'], mr.inputs['Value']); nt_.links.new(mr.outputs['Result'], b.inputs['Roughness'])

# ================================================== 3. modelos reales (CC0)
print('3. modelos', flush=True)
def importar(aid, nombres):
    ruta = f'{PH}/{aid}/{aid}.blend'
    antes = set(bpy.data.images.keys())
    with bpy.data.libraries.load(ruta, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if (nombres is None and 'LOD1' not in n and 'geometry_nodes' not in n)
                       or (nombres is not None and n in nombres)]
    obs = [o for o in dst.objects if o]
    for img_ in bpy.data.images:
        if img_.name in antes or not img_.filepath: continue
        fp = img_.filepath
        if fp.startswith('//'):
            cand = os.path.join(f'{PH}/{aid}', fp[2:].replace('\\', '/'))
            if os.path.exists(cand): img_.filepath = cand; img_.reload()
    return obs

def instanciar(obs, loc, escala=1.0, rotz=0.0, primera=False):
    raiz = bpy.data.objects.new('ph_raiz', None)
    col_pb.objects.link(raiz)
    raiz.location = loc; raiz.scale = (escala,)*3; raiz.rotation_euler = (0, 0, rotz)
    for o in obs:
        n = o if primera else o.copy()
        if not primera: n.data = o.data
        if n.name not in col_pb.objects: col_pb.objects.link(n)
        n.parent = raiz
    return raiz

def borrar_cerca(cx, cy, z0, z1, r=0.06, materiales=None):
    for ob in list(bpy.data.objects):
        if ob.type != 'MESH': continue
        if materiales and not any(sl.material and sl.material.name in materiales for sl in ob.material_slots): continue
        dx, dy = ob.location.x - cx, ob.location.y - cy
        if dx*dx + dy*dy < r*r and z0 - 0.02 < ob.location.z < z1 + 0.02:
            bpy.data.objects.remove(ob)

# 3a. plantas de interior: fuera las esferas, entran las macetas reales
HOJAS = {'hoja_oscura', 'hoja_media', 'hoja_clara'}
p1 = importar('potted_plant_01', ['potted_plant_01_stem', 'potted_plant_01_pot', 'potted_plant_01_pebbles', 'potted_plant_01_leaves'])
p2 = importar('potted_plant_02', ['potted_plant_02_pot', 'potted_plant_02_leaves', 'potted_plant_02_dirt'])
rl = random.Random(7)
for i, s in enumerate(plantas):
    xs = [p[0] for p in s['poly']]; ys = [p[1] for p in s['poly']]
    cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
    zs = [p[2] for p in s['poly']]
    z0 = min(min(zs), min(zs) + s['n'][2]*s['d']); z1 = max(max(zs), max(zs) + s['n'][2]*s['d'])
    rr = (max(xs) - min(xs)) / 2
    borrar_cerca(cx, cy, z0 - 0.5, z1 + 0.5, r=rr + 0.3, materiales=HOJAS)
    for ob in list(bpy.data.objects):        # la maceta del modelo original
        if ob.name.startswith('Maceta') and (ob.location.x-cx)**2 + (ob.location.y-cy)**2 < (rr+0.3)**2:
            bpy.data.objects.remove(ob)
    alto_obj = z1 - z0
    suelo_z = 0.0
    if alto_obj > 1.0:
        instanciar(p1, (cx, cy, suelo_z), escala=min(1.25, (z1 - suelo_z) / 1.35), rotz=rl.uniform(0, 6.28), primera=(i == 0))
    else:
        instanciar(p2, (cx, cy, suelo_z), escala=min(1.3, (z1 - suelo_z) / 0.84), rotz=rl.uniform(0, 6.28), primera=(i == 0))
print('   plantas:', len(plantas), flush=True)

# 3b. arboles de la acera: modelo real de arbol de alcorque
for ob in list(bpy.data.objects):
    if ob.type == 'MESH' and any(sl.material and sl.material.name in HOJAS | {'tronco_arbol'} for sl in ob.material_slots):
        bpy.data.objects.remove(ob)
arb = importar('tree_small_02', ['tree_small_02_trunk', 'tree_small_02_LOD0',
                                 'tree_small_02_leaves_a_LOD0', 'tree_small_02_leaves_b_LOD0',
                                 'tree_small_02_leaves_c_LOD0', 'tree_small_02_leaves_d_LOD0'])
for k, tx in enumerate((0.2, 4.55, 11.5, 15.6)):
    instanciar(arb, (tx, -1.45, 0.0), escala=rl.uniform(0.95, 1.15), rotz=rl.uniform(0, 6.28), primera=(k == 0))
print('   arboles: 4', flush=True)

# 3c. botellas del estante: botellas de vino reales con etiqueta
bot = importar('wine_bottles_01', ['wine_bottles_01_champagne', 'wine_bottles_01_burgundy',
                                   'wine_bottles_01_bordeaux', 'wine_bottles_01_alsace'])
altos = {o.name: (o.dimensions.z or 0.33) for o in bot}
for bi, s in enumerate(botellas):
    xs = [p[0] for p in s['poly']]; ys = [p[1] for p in s['poly']]
    cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
    z0 = s['poly'][0][2]; h = abs(s['d'])
    borrar_cerca(cx, cy, z0, z0 + h, r=0.05)
    o = bot[bi % len(bot)]
    esc = h / altos[o.name]
    instanciar([o], (cx, cy, z0), escala=esc, rotz=rl.uniform(0, 6.28), primera=(bi < len(bot)))
print('   botellas:', len(botellas), flush=True)

# 3d. sillas de mesa y taburetes de barra: modelos reales
import mathutils
def centro_objs(objs):
    # el respaldo se construye en coordenadas de mundo y su objeto queda en
    # el origen: no cuenta para el centro
    pts = [o.location for o in objs if o.type == 'MESH' and o.location.length > 1e-6]
    return (sum(p.x for p in pts)/len(pts), sum(p.y for p in pts)/len(pts))

def frente_local(objs):
    """Direccion a la que mira la silla en coords del modelo: opuesta al respaldo."""
    xs, ys, zs = [], [], []
    for o in objs:
        if o.type != 'MESH': continue
        for v in o.data.vertices:
            w = o.matrix_world @ v.co
            xs.append(w.x); ys.append(w.y); zs.append(w.z)
    cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
    zmax = max(zs); alto = [(x, y) for x, y, z in zip(xs, ys, zs) if z > zmax - 0.30]
    bx = sum(x for x, _ in alto)/len(alto) - cx; by = sum(y for _, y in alto)/len(alto) - cy
    return math.atan2(-by, -bx), (cx, cy)

def tela_acolchada(m_base, nombre, rgb):
    """Variante del material del modelo: el tapizado de cuero pasa a tela
    del color pedido (mascara por luminancia del atlas), patas intactas."""
    m = m_base.copy(); m.name = nombre
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    ld = next(l for l in nt.links if l.to_node == b and l.to_socket.name == 'Base Color')
    orig = ld.from_socket
    lum = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(orig, lum.inputs['Color'])
    masc = nt.nodes.new('ShaderNodeMapRange')
    masc.inputs['From Min'].default_value = 0.004; masc.inputs['From Max'].default_value = 0.009   # patas < 0.004, cuero 0.01-0.03
    nt.links.new(lum.outputs['Val'], masc.inputs['Value'])
    sombra = nt.nodes.new('ShaderNodeMapRange')       # pliegues del capitone
    sombra.inputs['From Min'].default_value = 0.008; sombra.inputs['From Max'].default_value = 0.030
    sombra.inputs['To Min'].default_value = 0.62; sombra.inputs['To Max'].default_value = 1.05
    nt.links.new(lum.outputs['Val'], sombra.inputs['Value'])
    tela = nt.nodes.new('ShaderNodeMix'); tela.data_type = 'RGBA'; tela.blend_type = 'MULTIPLY'
    tela.inputs['Factor'].default_value = 1.0; tela.inputs[6].default_value = (*rgb, 1)
    nt.links.new(sombra.outputs['Result'], tela.inputs[7])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    nt.links.new(masc.outputs['Result'], mix.inputs['Factor'])
    nt.links.new(orig, mix.inputs[6]); nt.links.new(tela.outputs[2], mix.inputs[7])
    nt.links.remove(ld); nt.links.new(mix.outputs[2], b.inputs['Base Color'])
    # tela: mate y con brillo de fibra, nada de cuero
    lr = next((l for l in nt.links if l.to_node == b and l.to_socket.name == 'Roughness'), None)
    if lr:
        mr = nt.nodes.new('ShaderNodeMath'); mr.operation = 'MULTIPLY'; mr.use_clamp = True
        nt.links.new(lr.from_socket, mr.inputs[0]); mr.inputs[1].default_value = 1.6
        nt.links.remove(lr); nt.links.new(mr.outputs['Value'], b.inputs['Roughness'])
    for k, v in (('Sheen Weight', 0.5), ('Sheen Roughness', 0.6), ('Specular IOR Level', 0.3)):
        if k in b.inputs: b.inputs[k].default_value = v
    return m

silla = importar('dining_chair_02', None)
ang_frente, (ox, oy) = frente_local(silla)
m_base = next(m for o in silla if o.type == 'MESH' for m in o.data.materials if m and 'Dots' not in m.name)
telas = {'boucle_crema': tela_acolchada(m_base, 'silla_crema', ns['srgb']('E9DFC9')),
         'boucle_arena': tela_acolchada(m_base, 'silla_arena', ns['srgb']('D9C5A4'))}
for i, (ang, tela_nm, objs) in enumerate(ns['SILLAS_REG']):
    cx, cy = centro_objs(objs)
    for o in objs: bpy.data.objects.remove(o)
    rz = ang - ang_frente
    raiz = instanciar(silla, (0, 0, 0), escala=1.0, rotz=rz, primera=(i == 0))
    dx, dy = ox*math.cos(rz) - oy*math.sin(rz), ox*math.sin(rz) + oy*math.cos(rz)
    raiz.location = (cx - dx, cy - dy, 0.0)
    for n_ in raiz.children:
        if n_.type == 'MESH':
            for sl in n_.material_slots:
                if sl.material and 'Dots' not in sl.material.name:
                    sl.link = 'OBJECT'; sl.material = telas.get(tela_nm, telas['boucle_crema'])
print('   sillas:', len(ns['SILLAS_REG']), flush=True)

tab = importar('metal_stool_01', None)
alto_tab = max((o.matrix_world @ mathutils.Vector(c)).z for o in tab if o.type == 'MESH' for c in o.bound_box)
_, (tx0, ty0) = frente_local(tab)
for i, objs in enumerate(ns['TABUR_REG']):
    cx, cy = centro_objs(objs)
    for o in objs: bpy.data.objects.remove(o)
    esc = 0.66 / alto_tab
    rz = rl.uniform(0, 6.28)
    raiz = instanciar(tab, (0, 0, 0), escala=esc, rotz=rz, primera=(i == 0))
    dx, dy = (tx0*math.cos(rz) - ty0*math.sin(rz))*esc, (tx0*math.sin(rz) + ty0*math.cos(rz))*esc
    raiz.location = (cx - dx, cy - dy, 0.0)
print('   taburetes:', len(ns['TABUR_REG']), flush=True)

# ================================================ 4. bisel global 2,5 mm
print('4. biseles', flush=True)
nb = 0; motivo = {'modelo': 0, 'ya': 0, 'tam': 0, 'mat': 0}
for ob in bpy.data.objects:
    if ob.type != 'MESH': continue
    if ob.name.startswith(('potted_', 'tree_', 'wine_', 'painted_', 'dining_chair', 'metal_stool')): motivo['modelo'] += 1; continue
    if any(m.type in ('BEVEL', 'SUBSURF') for m in ob.modifiers): motivo['ya'] += 1; continue
    if max(ob.dimensions) < 0.05 or min(ob.dimensions) < 0.004: motivo['tam'] += 1; continue
    if ob.data.materials and ob.data.materials[0] and ob.data.materials[0].name.startswith(('vidrio', 'LED', 'opal', 'luz')): motivo['mat'] += 1; continue
    bv = ob.modifiers.new('bisel', 'BEVEL')
    bv.width = 0.0025; bv.segments = 3; bv.limit_method = 'ANGLE'
    bv.angle_limit = math.radians(40); bv.use_clamp_overlap = True
    try:
        ob.data.polygons.foreach_set('use_smooth', [True] * len(ob.data.polygons))
        ob.data.set_sharp_from_angle(angle=math.radians(40))
        bv.harden_normals = True
    except Exception:
        pass
    nb += 1
print('   biselados:', nb, 'saltados:', motivo, flush=True)

# ================================================ 5. ajustes de render
print('5. render', flush=True)
c = scene.cycles
if PREVIEW:
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720
    c.samples = 96; c.adaptive_threshold = 0.05
else:
    scene.render.resolution_x, scene.render.resolution_y = 2560, 1440
    c.samples = int(os.environ.get('PH_SMP', '1536')); c.adaptive_threshold = 0.005
    c.adaptive_min_samples = 64
c.max_bounces = 12; c.diffuse_bounces = 8; c.glossy_bounces = 8
c.transmission_bounces = 12; c.transparent_max_bounces = 24
c.sample_clamp_indirect = 40.0; c.sample_clamp_direct = 0.0
c.blur_glossy = 0.5
for attr, val in (('use_light_tree', True), ('denoising_prefilter', 'ACCURATE'),
                  ('denoising_input_passes', 'RGB_ALBEDO_NORMAL'), ('use_denoising', True)):
    try: setattr(c, attr, val)
    except Exception as e: print('   (sin', attr, ')')
scene.render.use_persistent_data = True
scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_depth = '16'

for v in VISTA.split(','):
    eye, tgt, lens, hide, fs = ns['views'][v]
    fn = SALIDA if ',' not in VISTA else SALIDA.replace('.png', f'_{v}.png')
    ns['render_view'](fn, eye, tgt, lens, hide, fs)
print('LISTO', SALIDA, flush=True)
