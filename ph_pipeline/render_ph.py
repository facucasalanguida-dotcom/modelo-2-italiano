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
        cand = os.path.join(f'{PH}/{aid}', fp[2:].replace('\\', '/')) if fp.startswith('//') else fp
        if not os.path.exists(cand):
            # el .blend pide .exr y aqui hay .png/.jpg (o al reves): misma base, otra extension
            base_ = os.path.join(f'{PH}/{aid}/textures', os.path.splitext(os.path.basename(cand))[0])
            cand = next((base_ + ext for ext in ('.png', '.jpg', '.exr') if os.path.exists(base_ + ext)), None)
        if cand and cand != fp:
            img_.filepath = cand; img_.reload()
        elif not cand:
            print('   AVISO textura ausente:', aid, os.path.basename(fp), flush=True)
    return obs

def instanciar(obs, loc, escala=1.0, rotz=0.0, primera=False):
    raiz = bpy.data.objects.new('ph_raiz', None)
    col_pb.objects.link(raiz)
    raiz.location = loc; raiz.scale = (escala,)*3; raiz.rotation_euler = (0, 0, rotz)
    for o in obs:
        n = o if primera else o.copy()
        if not primera: n.data = o.data
        if n.name not in col_pb.objects: col_pb.objects.link(n)
        if len(obs) == 1:       # pieza suelta: su desplazamiento interno del .blend no pinta nada aqui
            n.location = (0, 0, 0); n.rotation_euler = (0, 0, 0)
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
    # arrimada a la mesa: el frente del asiento queda bajo el canto del tablero
    cx += 0.07 * math.cos(ang); cy += 0.07 * math.sin(ang)
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

# 3e. la barra: cafetera afinada, tazas de porcelana, tartas y croissants reales
gxy = ns['gxy']; primitive = ns['primitive']; MATS = ns['MAT']
ns['GIRO'] = ns['BAR_GIRO']
def mundo(x, y): return gxy(x, y)
def cerca(px, py, r, z0, z1, mats=None):
    out = []
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or ob.location.length < 1e-6: continue
        if mats and not any(sl.material and sl.material.name in mats for sl in ob.material_slots): continue
        if (ob.location.x-px)**2 + (ob.location.y-py)**2 < r*r and z0 <= ob.location.z <= z1: out.append(ob)
    return out

import mathutils
def local_xy(wx, wy):
    ox_, oy_, sx_, sy_ = ns['BAR_GIRO']
    return sx_ + (wy - oy_), sy_ - (wx - ox_)
def sonda(lx, ly, z_ini=1.6):
    bpy.context.view_layer.update()
    dg_ = bpy.context.evaluated_depsgraph_get()
    wx, wy = mundo(lx, ly)
    hit, loc, nrm, idx, hob, mtx = scene.ray_cast(dg_, (wx, wy, z_ini), (0, 0, -1), distance=3.0)
    return (loc.z if hit else None), (hob.name if hit else '-')
top_alto, nom_a = sonda(6.22, 7.40); top_bajo, nom_b = sonda(3.64, 6.95)
print(f'   sonda: mostrador alto {top_alto:.3f} ({nom_a}) | mostrador bajo {top_bajo:.3f} ({nom_b})', flush=True)
dz_alto = top_alto - 1.04
if abs(dz_alto) > 0.002:          # lo parametrico se creo a 1.04; se apoya en la tabla real
    n_baj = 0
    for ob in bpy.data.objects:
        if ob.type != 'MESH': continue
        if ob.name.startswith('Cafetera - '): ob.location.z += dz_alto; n_baj += 1; continue
        if ob.location.length < 1e-6: continue
        lx_, ly_ = local_xy(ob.location.x, ob.location.y)
        if 6.13 <= lx_ <= 7.81 and 6.46 <= ly_ <= 7.47 and 1.03 <= ob.location.z <= 1.60:
            ob.location.z += dz_alto; n_baj += 1
    print(f'   mostrador alto: {n_baj} objetos bajados {dz_alto*1000:.0f} mm', flush=True)
zb = top_alto
# -- cafetera: esmalte negro brillante en el panel, acero cepillado en cuerpo y calientatazas
esm = bpy.data.materials.new('esmalte_negro'); esm.use_nodes = True
b_ = esm.node_tree.nodes['Principled BSDF']
b_.inputs['Base Color'].default_value = (0.012, 0.012, 0.013, 1); b_.inputs['Roughness'].default_value = 0.12
for k, v in (('Coat Weight', 1.0), ('Coat Roughness', 0.05)):
    if k in b_.inputs: b_.inputs[k].default_value = v
acero = bpy.data.materials.new('acero_cepillado'); acero.use_nodes = True
b_ = acero.node_tree.nodes['Principled BSDF']
b_.inputs['Base Color'].default_value = (0.75, 0.76, 0.77, 1); b_.inputs['Metallic'].default_value = 1.0
b_.inputs['Roughness'].default_value = 0.28
if 'Anisotropic' in b_.inputs: b_.inputs['Anisotropic'].default_value = 0.7
for nm_ in ('Cafetera - cuerpo', 'Cafetera - calientatazas'):
    ob = bpy.data.objects.get(nm_)
    if ob: ob.data.materials[0] = acero
ob = bpy.data.objects.get('Cafetera - panel')
if ob: ob.data.materials[0] = esm
# manometros con esfera blanca y aro cromado, placa de marca, segunda lanza
M_CROMO = ns['M_CROMO']
esf = bpy.data.materials.new('esfera_manometro'); esf.use_nodes = True
esf.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.92, 0.90, 0.85, 1)
esf.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.4
for gx in (6.45, 6.89):
    # bisel clavado en el panel (6.79) y esfera que asoma 4 mm por delante del bisel
    # (primitive: escala = medida total) aro clavado 2,5 mm en el panel (6.79); esfera solapada 0,5 mm con el aro
    primitive('cyl', M_CROMO, (gx, 6.790, zb + 0.27), (0.024, 0.024, 0.005), (math.radians(90), 0, 0), seg=24).name = 'manometro_aro'
    primitive('cyl', esf,     (gx, 6.7865, zb + 0.27), (0.020, 0.020, 0.003), (math.radians(90), 0, 0), seg=24).name = 'manometro_esfera'
primitive('cube', M_CROMO, (6.67, 6.788, zb + 0.30), (0.11, 0.003, 0.024)).name = 'placa_marca'
# lanzas de vapor: la original quedaba separada del cuerpo. Ahora nacen dentro del cuerpo (anclaje
# a 6.835 de fondo, 22 cm de altura), salen por el borde inferior de cada lado del panel y bajan
# hacia delante sobre la bandeja (18 cm, 35 grados hacia delante, 6 hacia fuera)
wx_, wy_ = mundo(7.06, 6.95)
for ob in cerca(wx_, wy_, 0.03, zb + 0.10, zb + 0.22, {'cromo'}): bpy.data.objects.remove(ob)
for ax_, sg_ in ((6.345, 1), (6.995, -1)):
    d_ = (0.086 * sg_, 0.574, 0.795)                     # direccion de la punta al anclaje
    c_ = (ax_ - 0.09 * d_[0], 6.835 - 0.09 * d_[1], zb + 0.22 - 0.09 * d_[2])
    primitive('cyl', M_CROMO, c_, (0.007, 0.007, 0.18),
              (math.radians(-35), math.radians(6 * sg_), 0), seg=12).name = 'lanza_vapor'
    primitive('sphere', M_CROMO, (6.32 if sg_ > 0 else 7.02, 6.90, zb + 0.30), (0.014, 0.014, 0.014), seg=16).name = 'valvula_vapor'
# -- tazas del calientatazas: fuera los cilindros, entran tazas de porcelana
tx0, ty0 = mundo(6.67, 7.05)
for ob in cerca(tx0, ty0, 0.40, zb + 0.38, zb + 0.45, {'ceramica'}): bpy.data.objects.remove(ob)
te = importar('tea_set_01', None)
tset = {o.name: o for o in te}
# porcelana blanca: se apaga casi del todo el motivo floral
m_te = next(m for o in te if o.type == 'MESH' for m in o.data.materials if m and 'Dots' not in m.name)
nt_ = m_te.node_tree; b_ = nt_.nodes['Principled BSDF']
ld_ = next((l for l in nt_.links if l.to_node == b_ and l.to_socket.name == 'Base Color'), None)
if ld_:
    mx_ = nt_.nodes.new('ShaderNodeMix'); mx_.data_type = 'RGBA'; mx_.inputs['Factor'].default_value = 0.88
    mx_.inputs[7].default_value = (0.93, 0.92, 0.90, 1)
    nt_.links.new(ld_.from_socket, mx_.inputs[6]); nt_.links.remove(ld_); nt_.links.new(mx_.outputs[2], b_.inputs['Base Color'])
b_.inputs['Roughness'].default_value = 0.18
if 'Coat Weight' in b_.inputs: b_.inputs['Coat Weight'].default_value = 0.6
taza_a, taza_b = tset['tea_set_01_cup_small_01'], tset['tea_set_01_cup_small_02']
plat_a, plat_b = tset['tea_set_01_saucer_circular_03'], tset['tea_set_01_saucer_circular_04']
usados = set()
def pieza(o, lx, ly, z, rotz, esc=1.0):
    wx, wy = mundo(lx, ly)
    primera = o.name not in usados; usados.add(o.name)
    r_ = instanciar([o], (wx, wy, z), escala=esc, rotz=rotz + math.pi/2, primera=primera)
    for ch in r_.children:      # las piezas del juego traen su propio desplazamiento en el .blend
        ch.location = (0, 0, 0); ch.rotation_euler = (0, 0, 0); ch.scale = (1, 1, 1)
    return r_
for i, (dx, dy) in enumerate(((0.10, 0.10), (0.30, 0.10), (0.50, 0.10), (0.10, 0.30), (0.30, 0.30), (0.50, 0.30))):
    pieza(taza_a if i % 2 else taza_b, 6.36 + dx, 6.86 + dy, zb + 0.375, rl.uniform(0, 6.28))
# -- pilas de platillos y tazas del mostrador: fuera cilindros, entran platillos apilados
for (lx, ly, r_) in ((7.05, 6.80, 0.09), (7.25, 6.71, 0.12)):
    wx, wy = mundo(lx, ly)
    for ob in cerca(wx, wy, r_, zb, zb + 0.12, {'ceramica'}): bpy.data.objects.remove(ob)
for k in range(3):        # platillos anidados (6 mm entre uno y otro) y taza asentada en el hueco del ultimo
    pieza(plat_a if k % 2 else plat_b, 7.14, 6.72, zb + 0.006 * k, rl.uniform(0, 6.28))
pieza(taza_a, 7.14, 6.72, zb + 0.0125, rl.uniform(0, 6.28))
pieza(tset['tea_set_01_sugar_cup_01'], 7.14, 6.92, zb, 0.0)
pieza(tset['tea_set_01_sugar_cup_01_lid'], 7.14, 6.92, zb, 0.0)
# -- molinillo y caja: separados y alineados al fondo de la barra
def mover(lx0, ly0, lx1, ly1, r=0.07, z0=zb, z1=zb + 0.6):
    wx0, wy0 = mundo(lx0, ly0); wx1, wy1 = mundo(lx1, ly1)
    for ob in cerca(wx0, wy0, r, z0, z1):
        ob.location.x += wx1 - wx0; ob.location.y += wy1 - wy0
for gx in (6.52, 6.82):               # mangos de los portafiltros: 1 cm separados del grupo -> pegados
    mover(gx, 6.70, gx, 6.72, r=0.02, z0=zb + 0.04, z1=zb + 0.09)
mover(7.27, 6.98, 7.16, 7.25)          # molinillo, al fondo entre la cafetera y el TPV (sin tocar la caja)
primitive('cyl', M_CROMO, (7.16, 7.25, zb + 0.0025), (0.060, 0.060, 0.005), seg=32).name = 'molinillo_base'
primitive('cyl', M_CROMO, (7.16, 7.25, zb + 0.296), (0.058, 0.058, 0.004), seg=32).name = 'molinillo_aro'
primitive('cyl', M_CROMO, (7.16, 7.19, zb + 0.15), (0.006, 0.006, 0.035), (math.radians(-60), 0, 0), seg=10).name = 'molinillo_salida'
# TPV: la base y la pantalla vienen del modelo (Caja - base / Caja - pantalla); se le pone la pantalla encendida
m_tpv = bpy.data.materials.new('tpv_encendido'); m_tpv.use_nodes = True
b_ = m_tpv.node_tree.nodes['Principled BSDF']
b_.inputs['Base Color'].default_value = (0.55, 0.62, 0.72, 1); b_.inputs['Roughness'].default_value = 0.15
b_.inputs['Emission Color'].default_value = (0.62, 0.70, 0.82, 1); b_.inputs['Emission Strength'].default_value = 0.7
primitive('cube', m_tpv, (7.52, 6.8892, 1.20), (0.26, 0.002, 0.20)).name = 'tpv_pantalla'
# -- soportes de tarta: la tarta paramétrica se sustituye por una real
tarta = importar('carrot_cake', None)
# los dos soportes estaban en el rebaje de las vitrinas (uno en el aire, otro dentro de la vitrina):
# pasan al extremo sur de la tabla del mostrador bajo, apoyados en su altura real
dz_bajo = top_bajo - 1.04
for j, ((lx0, ly0), (lx1, ly1)) in enumerate((((3.85, 6.75), (3.64, 6.75)), ((4.05, 7.14), (3.64, 7.15)))):
    wx0, wy0 = mundo(lx0, ly0); wx1, wy1 = mundo(lx1, ly1)
    for ob in cerca(wx0, wy0, 0.12, 1.13, 1.21, {'croissant', 'crema_past', 'fruta_roja', 'fruta_oscura'}):
        bpy.data.objects.remove(ob)
    for ob in cerca(wx0, wy0, 0.12, 1.03, 1.15, {'ceramica'}):
        ob.location.x += wx1 - wx0; ob.location.y += wy1 - wy0; ob.location.z += dz_bajo
    instanciar(tarta, (wx1, wy1, top_bajo + 0.0945), escala=0.86, rotz=rl.uniform(0, 6.28), primera=(j == 0))
# -- vitrina: croissants y napolitanas parametricos -> croissant fotogrametrico
cro = importar('croissant', None)
ns['GIRO'] = None
nc = 0
for i, s_ in enumerate(ns['productos']):
    k = i % 6
    if k not in (0, 1, 3): continue
    cx, cy, _ = ns['centro'](s_)
    zs = [p[2] for p in s_['poly']]
    z0 = min(min(zs), min(zs) + s_['n'][2]*s_['d'])
    for ob in cerca(cx, cy, 0.105, z0 + 0.004, z0 + 0.08, {'croissant', 'bollo'}): bpy.data.objects.remove(ob)
    # a lo largo de la balda (eje Y), con un pelin de giro; asi no pisa la etiqueta ni al vecino
    rz = math.pi/2 + rl.choice((0, math.pi)) + math.radians(rl.uniform(-8, 8))
    instanciar(cro, (cx, cy, z0 + 0.003), escala=rl.uniform(0.78, 0.86), rotz=rz, primera=(nc == 0)); nc += 1
print('   barra: tazas 7, platillos 3, tartas 2, croissants', nc, flush=True)
# originales importados que no se han colocado: se quedaban en el origen del mundo -> fuera
n_lim = 0
for ob in list(bpy.data.objects):
    if ob.type != 'MESH' or ob.parent is not None: continue
    if not ob.name.startswith(('potted_', 'tree_', 'wine_', 'dining_chair', 'metal_stool', 'tea_set', 'carrot_cake', 'croissant')): continue
    if abs(ob.location.x) < 1.0 and abs(ob.location.y) < 1.0:
        bpy.data.objects.remove(ob); n_lim += 1
print('   originales sin usar eliminados:', n_lim, flush=True)

# ================================================ 4. bisel global 2,5 mm
print('4. biseles', flush=True)
nb = 0; motivo = {'modelo': 0, 'ya': 0, 'tam': 0, 'mat': 0}
for ob in bpy.data.objects:
    if ob.type != 'MESH': continue
    if ob.name.startswith(('potted_', 'tree_', 'wine_', 'painted_', 'dining_chair', 'metal_stool', 'tea_set', 'carrot_cake', 'croissant')): motivo['modelo'] += 1; continue
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

# ================================================ 4b. asentar: nada flotando
import mathutils
IGN = ('lanza_vapor', 'manometro', 'placa_marca', 'valvula', 'molinillo_aro', 'molinillo_salida', '_lid', 'tpv_pantalla')
PREF = ('potted_', 'tree_', 'wine_', 'dining_chair', 'metal_stool', 'tea_set', 'carrot_cake', 'croissant')
def grupos_escena():
    """Cada objeto suelto es un grupo; los hijos de una raiz ph_raiz forman uno."""
    g = {}
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or any(k in ob.name for k in IGN): continue
        if ob.parent and ob.parent.name.startswith('ph_raiz'):
            g.setdefault(ob.parent.name, {'raiz': ob.parent, 'objs': [], 'nombre': ob.name})['objs'].append(ob.name)
        elif ob.location.length > 1e-6:
            g.setdefault(ob.name, {'raiz': ob, 'objs': [], 'nombre': ob.name})['objs'].append(ob.name)
    return g
def cajas_eval(dg):
    c = {}
    for ob in bpy.data.objects:
        if ob.type != 'MESH': continue
        ev = ob.evaluated_get(dg)
        bb = [ev.matrix_world @ mathutils.Vector(v) for v in ev.bound_box]
        c[ob.name] = (min(b.x for b in bb), max(b.x for b in bb), min(b.y for b in bb), max(b.y for b in bb),
                      min(b.z for b in bb), max(b.z for b in bb))
    return c
def hueco_grupo(nombres, dg, cajas):
    xs0 = [cajas[n][0] for n in nombres]; xs1 = [cajas[n][1] for n in nombres]
    ys0 = [cajas[n][2] for n in nombres]; ys1 = [cajas[n][3] for n in nombres]
    zmin = min(cajas[n][4] for n in nombres)
    cx = (min(xs0) + max(xs1)) / 2; cy = (min(ys0) + max(ys1)) / 2
    mejor = None; sop = '-'; propios = set(nombres)
    for nm, (x0, x1, y0, y1, z0, z1) in cajas.items():
        if nm in propios or z0 > zmin + 0.005: continue
        if not (x0 - 0.001 <= cx <= x1 + 0.001 and y0 - 0.001 <= cy <= y1 + 0.001): continue
        ev = bpy.data.objects[nm].evaluated_get(dg); mi = ev.matrix_world.inverted()
        o_l = mi @ mathutils.Vector((cx, cy, zmin + 0.003)); d_l = mi.to_3x3() @ mathutils.Vector((0, 0, -1))
        hit, loc, nrm, idx = ev.ray_cast(o_l, d_l, distance=1000.0)
        if not hit: continue
        zw = (ev.matrix_world @ loc).z
        if zw > zmin + 0.004: continue          # hemos nacido dentro de este objeto: no es apoyo
        if mejor is None or zw > mejor: mejor = zw; sop = nm
    return zmin, (None if mejor is None else zmin - mejor), sop, (cx, cy)

def en_zona(cx, cy, z):
    lx, ly = local_xy(cx, cy)
    if 6.13 <= lx <= 7.81 and 6.46 <= ly <= 7.47 and 0.97 <= z <= 1.60: return 'barra alta'
    if 3.40 <= lx <= 3.86 and 6.46 <= ly <= 7.47 and 0.85 <= z <= 1.30: return 'barra baja'
    if 2.15 <= cx <= 2.45 and 2.10 <= cy <= 4.10 and 0.79 <= z <= 1.12: return 'vitrina'
    return None

n_as = 0; mm_max = 0.0
for pasada in range(2):        # dos pasadas: lo apilado (platillos, taza) se asienta sobre lo ya asentado
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); cajas = cajas_eval(dg)
    for clave, g in grupos_escena().items():
        zmin, gap, sop, (cx, cy) = hueco_grupo(g['objs'], dg, cajas)
        zona = en_zona(cx, cy, zmin) or (g['nombre'].startswith(('wine_', 'tea_set', 'carrot_cake', 'croissant')) and 'modelo')
        if not zona or gap is None: continue
        if 0.0005 < gap < 0.015:
            g['raiz'].location.z -= gap; n_as += 1; mm_max = max(mm_max, gap)
            for n in g['objs']:
                x0, x1, y0, y1, z0, z1 = cajas[n]; cajas[n] = (x0, x1, y0, y1, z0 - gap, z1 - gap)
print(f'   asentados: {n_as} objetos (max {mm_max*1000:.1f} mm)', flush=True)

# ================================================ 4c. comprobacion (PH_CHECK=1 solo sospechosos, 2 todo)
if os.environ.get('PH_CHECK'):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); cajas = cajas_eval(dg)
    filas = []
    for clave, g in grupos_escena().items():
        zmin, gap, sop, (cx, cy) = hueco_grupo(g['objs'], dg, cajas)
        if not (g['nombre'].startswith(PREF) or en_zona(cx, cy, zmin)): continue
        filas.append((g['nombre'], gap, sop, (cx, cy, zmin)))
    filas.sort(key=lambda r: -(r[1] if r[1] is not None else 9))
    malos = 0
    for nm, gap, sop, cc in filas:
        malo = gap is None or gap > 0.006 or gap < -0.02
        malos += malo
        if malo or os.environ.get('PH_CHECK') == '2':
            print(f'{"!!" if malo else "  "} {nm:34s} hueco={("?" if gap is None else f"{gap*1000:.1f}mm"):>9s} sobre={sop:26s} ({cc[0]:.2f},{cc[1]:.2f},{cc[2]:.3f})', flush=True)
    print('CHECK LISTO', malos, 'sospechosos de', len(filas), flush=True)
    raise SystemExit(0)

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

PASADAS = int(os.environ.get('PH_PASADAS', '0'))
if PASADAS:
    # render por pasadas reanudable: cada pasada escribe (via nodo File Output del compositor) un EXR
    # multiparte lineal en media precision con la imagen, el albedo y la normal de denoise, con semilla
    # distinta; fusionar.py las promedia y pasa el denoiser. Si la maquina se cae solo se pierde la
    # pasada en curso: las ya escritas se saltan al relanzar.
    c.use_denoising = False
    for vl in scene.view_layers: vl.cycles.denoising_store_passes = True
    scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_depth = '8'
    ntc = bpy.data.node_groups.new('comp_pasadas', 'CompositorNodeTree')
    scene.compositing_node_group = ntc; scene.render.use_compositing = True
    rlay = ntc.nodes.new('CompositorNodeRLayers'); rlay.scene = scene
    ntc.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    gout = ntc.nodes.new('NodeGroupOutput'); ntc.links.new(rlay.outputs['Image'], gout.inputs['Image'])
    fout = ntc.nodes.new('CompositorNodeOutputFile')
    fout.format.file_format = 'OPEN_EXR_MULTILAYER'; fout.format.color_depth = '16'; fout.format.exr_codec = 'ZIP'
    fout.save_as_render = False
    for it in list(fout.file_output_items): fout.file_output_items.remove(it)
    for nm_, sock_ in (('img', 'Image'), ('alb', 'Denoising Albedo'), ('nor', 'Denoising Normal')):
        fout.file_output_items.new('RGBA', nm_); ntc.links.new(rlay.outputs[sock_], fout.inputs[nm_])
    os.makedirs(f'{SP}/pasadas', exist_ok=True); fout.directory = f'{SP}/pasadas/'
    import json as _json
    vs_ = scene.view_settings
    _json.dump({'view_transform': vs_.view_transform, 'look': vs_.look,
                'exposure': EXPO, 'gamma': vs_.gamma,
                'use_white_balance': getattr(vs_, 'use_white_balance', False),
                'white_balance_temperature': getattr(vs_, 'white_balance_temperature', 6500),
                'white_balance_tint': getattr(vs_, 'white_balance_tint', 10),
                'w': scene.render.resolution_x, 'h': scene.render.resolution_y},
               open(f'{SP}/pasadas/vista.json', 'w'))
    scene.frame_set(1)
    for v in VISTA.split(','):
        eye, tgt, lens, hide, fs = ns['views'][v]
        for k in range(PASADAS):
            nombre = f'{v}_p{k:02d}'
            if os.path.exists(f'{SP}/pasadas/{nombre}.exr'): print('   pasada ya hecha:', nombre, flush=True); continue
            fout.file_name = nombre
            c.seed = 1 + 7919 * k
            ns['render_view'](f'pasadas/{nombre}.png', eye, tgt, lens, hide, fs)
            print(f'PASADA OK {v} {k+1}/{PASADAS}', flush=True)
    print('LISTO pasadas', VISTA, flush=True)
else:
    for v in VISTA.split(','):
        eye, tgt, lens, hide, fs = ns['views'][v]
        fn = SALIDA if ',' not in VISTA else SALIDA.replace('.png', f'_{v}.png')
        ns['render_view'](fn, eye, tgt, lens, hide, fs)
    print('LISTO', SALIDA, flush=True)
