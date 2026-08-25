# Construye la escena fotorrealista del Café Napoli en Blender (bpy headless)
# a partir de solids.json (geometría exacta del generador de SketchUp).
import bpy, bmesh, json, math, random
from mathutils import Vector

random.seed(7)
S = json.load(open('solids.json'))

# ---------------------------------------------------------------- limpieza
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 208
scene.cycles.use_denoising = True
try: scene.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
scene.cycles.sample_clamp_indirect = 10.0
scene.cycles.max_bounces = 8
scene.cycles.transmission_bounces = 8
scene.cycles.transparent_max_bounces = 12
scene.render.resolution_x = 1792
scene.render.resolution_y = 1120
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Punchy'

# ---------------------------------------------------------------- materiales
def _principled(m):
    nt = m.node_tree
    return nt, nt.nodes['Principled BSDF']

def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m

def set_in(bsdf, key, val):
    if key in bsdf.inputs:
        bsdf.inputs[key].default_value = val

def plain(name, rgb, rough=0.6, metal=0.0, sheen=0.0):
    m = new_mat(name); nt, b = _principled(m)
    set_in(b, 'Base Color', (*rgb, 1)); set_in(b, 'Roughness', rough)
    set_in(b, 'Metallic', metal)
    if sheen: set_in(b, 'Sheen Weight', sheen)
    return m

def wood(name, c1, c2, scale=1.4, rough=0.35, rot=0.0):
    m = new_mat(name); nt, b = _principled(m)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0, 0, rot)
    mp.inputs['Scale'].default_value = (1, 8, 8)
    wv = nt.nodes.new('ShaderNodeTexWave')
    wv.inputs['Scale'].default_value = scale
    wv.inputs['Distortion'].default_value = 1.6
    wv.inputs['Detail'].default_value = 1.0
    cr = nt.nodes.new('ShaderNodeValToRGB')
    cr.color_ramp.elements[0].color = (*c1, 1)
    cr.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], wv.inputs['Vector'])
    nt.links.new(wv.outputs['Fac'], cr.inputs['Fac'])
    nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
    ns = nt.nodes.new('ShaderNodeTexNoise')
    ns.inputs['Scale'].default_value = 20
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = rough - 0.06
    mr.inputs['To Max'].default_value = rough + 0.08
    nt.links.new(ns.outputs['Fac'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], b.inputs['Roughness'])
    return m

def glassm(name, tint=(1, 1, 1), rough=0.0):
    m = new_mat(name); nt, b = _principled(m)
    set_in(b, 'Base Color', (*tint, 1)); set_in(b, 'Roughness', rough)
    set_in(b, 'Transmission Weight', 1.0); set_in(b, 'IOR', 1.45)
    return m

def emitm(name, rgb, strength):
    m = new_mat(name); nt, b = _principled(m)
    set_in(b, 'Base Color', (*rgb, 1))
    set_in(b, 'Emission Color', (*rgb, 1))
    set_in(b, 'Emission Strength', strength)
    return m

def wall(name, rgb, rough=0.85):
    m = new_mat(name); nt, b = _principled(m)
    ns = nt.nodes.new('ShaderNodeTexNoise')
    ns.inputs['Scale'].default_value = 9.0
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    mx.inputs['Factor'].default_value = 0.05
    mx.inputs[6].default_value = (*rgb, 1)
    mx.inputs[7].default_value = (rgb[0]*0.9, rgb[1]*0.9, rgb[2]*0.9, 1)
    nt.links.new(ns.outputs['Fac'], mx.inputs['Factor'])
    nt.links.new(mx.outputs[2], b.inputs['Base Color'])
    set_in(b, 'Roughness', rough)
    return m

TEXDIR = '/tmp/claude-0/-home-user-modelo-2-italiano/30d2763c-3169-519a-ac78-c5a47134634b/scratchpad/tex'
_imgcache = {}
def teximg(fn, noncolor=False):
    key = (fn, noncolor)
    if key not in _imgcache:
        im = bpy.data.images.load(f'{TEXDIR}/{fn}.png')
        if noncolor:
            im.colorspace_settings.name = 'Non-Color'
        _imgcache[key] = im
    return _imgcache[key]

def pbr_tex(name, diff=None, rough=None, nrm=None, tile=1.0, tint=None,
            coat=0.0, nrm_str=0.6, color=None, base_rough=0.5, sheen=0.0,
            metal=0.0, generated=False):
    m = new_mat(name); nt, b = _principled(m)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1.0/tile, 1.0/tile, 1.0/tile)
    src = tc.outputs['Generated' if generated else 'Object']
    nt.links.new(src, mp.inputs['Vector'])
    def img_node(fn, noncolor):
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = teximg(fn, noncolor)
        n.projection = 'BOX'; n.projection_blend = 0.3
        nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
        return n
    if diff:
        d = img_node(diff, False)
        if tint:
            mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
            mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1.0
            mx.inputs[7].default_value = (*tint, 1)
            nt.links.new(d.outputs['Color'], mx.inputs[6])
            nt.links.new(mx.outputs[2], b.inputs['Base Color'])
        else:
            nt.links.new(d.outputs['Color'], b.inputs['Base Color'])
    elif color:
        set_in(b, 'Base Color', (*color, 1))
    if rough:
        r = img_node(rough, True)
        nt.links.new(r.outputs['Color'], b.inputs['Roughness'])
    else:
        set_in(b, 'Roughness', base_rough)
    if nrm:
        n = img_node(nrm, True)
        nm_ = nt.nodes.new('ShaderNodeNormalMap')
        nm_.inputs['Strength'].default_value = nrm_str
        nt.links.new(n.outputs['Color'], nm_.inputs['Color'])
        nt.links.new(nm_.outputs['Normal'], b.inputs['Normal'])
    if coat: set_in(b, 'Coat Weight', coat)
    if sheen: set_in(b, 'Sheen Weight', sheen)
    if metal: set_in(b, 'Metallic', metal)
    return m

def srgb(hexs):
    v = [int(hexs[i:i+2], 16)/255 for i in (0, 2, 4)]
    return tuple(c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4 for c in v)

MAT = {
 'CN Muro':           pbr_tex('muro', 'wall_diff', 'wall_rough', 'wall_nrm', 3.0, nrm_str=0.5),
 'CN Medianera':      pbr_tex('medianera', 'wall_diff', 'wall_rough', 'wall_nrm', 3.0, tint=(0.93, 0.93, 0.92), nrm_str=0.5),
 'CN Tabique':        pbr_tex('tabique', 'wall_diff', 'wall_rough', 'wall_nrm', 3.0, tint=(1.03, 1.03, 1.02), nrm_str=0.4),
 'CN Techo':          pbr_tex('techo', 'wall_diff', 'wall_rough', 'wall_nrm', 3.0, tint=(1.06, 1.06, 1.04), nrm_str=0.3),
 'CN Suelo roble':    pbr_tex('suelo', 'floor_diff', 'floor_rough', 'floor_nrm', 2.4, coat=0.12, nrm_str=0.9),
 'CN Hormigon':       pbr_tex('hormigon', 'wall_diff', 'wall_rough', 'wall_nrm', 3.0, tint=(0.82, 0.80, 0.78), nrm_str=0.7),
 'CN Madera liston':  pbr_tex('liston', 'wood_diff_v', 'wood_rough_v', 'wood_nrm_v', 1.3, nrm_str=0.6),
 'CN Madera tablero': pbr_tex('tablero', 'wood_diff', 'wood_rough', 'wood_nrm', 1.1, tint=(0.82, 0.72, 0.60), coat=0.1, nrm_str=0.55),
 'CN Madera clara':   pbr_tex('clara', 'wood_diff', 'wood_rough', 'wood_nrm', 1.5, tint=(1.06, 1.03, 0.98), nrm_str=0.5),
 'CN Acero inox':     plain('inox', srgb('E8EAEC'), 0.17, 1.0),
 'CN Vidrio':         glassm('vidrio'),
 'CN Carpinteria':    plain('carpinteria', srgb('2A2A28'), 0.4, 0.4),
 'CN Rotulo':         plain('rotulo', srgb('3E6B99'), 0.35),
 'CN Tela':           pbr_tex('tela', None, 'fabric_rough', 'fabric_nrm', 1.0, color=srgb('E7DFD1'), sheen=1.0, nrm_str=0.5),
 'CN Tela azul':      pbr_tex('tela_azul', None, 'fabric_rough', 'fabric_nrm', 1.0, color=srgb('6C8AA8'), sheen=1.0, nrm_str=0.5),
 'CN Negro mate':     plain('negro', srgb('262524'), 0.55),
 'CN Laton':          plain('laton', srgb('C69E54'), 0.25, 1.0),
 'CN Opal':           emitm('opal', srgb('FFF4E0'), 1.7),
 'CN Planta':         plain('planta', srgb('6E8B5A'), 0.8),
 'CN Terracota':      plain('terracota', srgb('BA8263'), 0.7),
 'CN Azul Napoli':    pbr_tex('napoli', None, 'wood_rough_v', 'wood_nrm_v', 1.3, color=srgb('3E6B99'), nrm_str=0.35, base_rough=0.45),
 'CN Blanco roto':    pbr_tex('blanco', 'wall_diff', 'wall_rough', 'wall_nrm', 3.0, tint=(1.10, 1.09, 1.07), nrm_str=0.3),
 'CN Luz calida':     emitm('luzcalida', srgb('FFD9A0'), 1.9),
 'CN Instalacion':    plain('instalacion', srgb('AAACAE'), 0.5, 0.6),
}
ARTE = [pbr_tex(f'arte{i}', f'art_{i}', None, None, 1.0, generated=True,
                base_rough=0.65) for i in range(3)]

# vidrio arquitectónico: Transparent BSDF + un 7 % de glossy, para que el
# denoiser vea a través y los paños grandes queden transparentes de verdad
def arch_glass():
    m = bpy.data.materials.new('vidrio_arq'); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    out = nt.nodes['Material Output']
    mix = nt.nodes.new('ShaderNodeMixShader')
    tr  = nt.nodes.new('ShaderNodeBsdfTransparent')
    tr.inputs['Color'].default_value = (0.96, 0.98, 0.99, 1)
    gl  = nt.nodes.new('ShaderNodeBsdfGlossy')
    gl.inputs['Roughness'].default_value = 0.02
    mix.inputs['Fac'].default_value = 0.07
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(gl.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return m
M_VIDRIO_ARQ = arch_glass()
M_CERAMICA = plain('ceramica', srgb('F5F1E8'), 0.35)
M_CROISSANT = plain('croissant', srgb('A96524'), 0.5)
M_BOLLO    = plain('bollo', srgb('5E3A1E'), 0.5)
M_VVERDE   = glassm('vidrio_verde', srgb('2E4F33'))
M_VAMBAR   = glassm('vidrio_ambar', srgb('7A4416'))
M_CORCHO   = plain('corcho', srgb('C9A468'), 0.8)
M_FLOR_B   = plain('flor_blanca', srgb('F2EEE2'), 0.7)
M_FLOR_A   = plain('flor_amar', srgb('D9B84A'), 0.7)
M_TALLO    = plain('tallo', srgb('5A7A42'), 0.8)
M_FOLLAJE  = plain('follaje', srgb('4F6B3E'), 0.9)
M_CAFE     = plain('cafe_liquido', srgb('3A2417'), 0.15)

# ---------------------------------------------------------------- geometría
col_pb = bpy.data.collections.new('PB'); scene.collection.children.link(col_pb)
col_pa = bpy.data.collections.new('PA'); scene.collection.children.link(col_pa)

PA_TAGS = ('04 Forjado planta alta', '05 Cubierta', '06 Particiones planta alta',
           '09 Barandillas')
def is_pa(s):
    nm = s['name'] or ''
    if s['tag'] in PA_TAGS: return True
    if nm.startswith(('PA ', 'Frente de altillo', 'Banda de rotulo del altillo')):
        return True
    if nm == 'Pavimento roble planta alta': return True
    if nm.startswith(('Barandilla',)): return True
    return False

def add_mesh(name, verts, faces, mat, col, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
        try: me.set_sharp_from_angle(angle=math.radians(40))
        except Exception: pass
    ob = bpy.data.objects.new(name, me)
    if mat: me.materials.append(mat)
    col.objects.link(ob)
    if name.startswith(('Asiento', 'Respaldo')) or 'cojin' in name:
        bv = ob.modifiers.new('bv', 'BEVEL')
        bv.width = 0.018; bv.segments = 3
    else:
        bv = ob.modifiers.new('bv', 'BEVEL')
        bv.width = 0.004; bv.segments = 2
    bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(45)
    return ob

def prism(name, poly, n, d, mat, col):
    off = Vector(n) * d
    vs = [Vector(p) for p in poly]
    verts = vs + [v + off for v in vs]
    k = len(vs)
    faces = [list(range(k)), [i + k for i in range(k)][::-1]]
    for i in range(k):
        j = (i + 1) % k
        faces.append([i, j, j + k, i + k])
    return add_mesh(name, verts, faces, mat, col, smooth=(k >= 16))

def centro(s):
    xs = [p[0] for p in s['poly']]; ys = [p[1] for p in s['poly']]
    zs = [p[2] for p in s['poly']]
    n, d = s['n'], s['d']
    cx, cy, cz = sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs)
    return (cx + n[0]*d/2, cy + n[1]*d/2, cz + n[2]*d/2)

M_LED = emitm('led', srgb('FFE3B0'), 14.0)

# tiras LED bajo el frente de cada balda de vitrina
def led_strip(x0, x1, y, z):
    verts = [(x0, y-0.006, z), (x1, y-0.006, z), (x1, y+0.006, z), (x0, y+0.006, z)]
    add_mesh('LED', verts, [[0, 1, 2, 3]], M_LED, col_pb)

lamparas, empotrados, apliques = [], [], []
productos, botellas, plantas = [], [], []

for s in S:
    nm = s['name'] or 'solido'
    mat = MAT.get(s['mat'])
    if nm == 'Foco':
        lamparas.append(centro(s))
    if nm == 'Empotrado de techo':
        empotrados.append(centro(s))
    if nm == 'Aplique de pared':
        apliques.append(centro(s))
    if nm.endswith('- producto'):
        productos.append(s); continue
    if 'Vitrina' in nm and '- balda' in nm:
        xs_ = [p[0] for p in s['poly']]; ys_ = [p[1] for p in s['poly']]
        zs_ = [p[2] for p in s['poly']]
        z_ = min(min(zs_), min(zs_) + s['n'][2]*s['d'])
        led_strip(min(xs_) + 0.02, max(xs_) - 0.02, min(ys_) + 0.02, z_ - 0.004)
    if nm == 'Botella':
        botellas.append(s); continue
    if nm == 'Copa' and s['mat'] == 'CN Planta':
        plantas.append(s); continue
    if s['tag'] == '26 Mesas y sillas':
        continue                       # mobiliario parametrico de alta calidad
    if nm.startswith('Pizarra'):
        continue                       # sustituida por la carta de menu
    if nm.startswith(('Maquina de cafe', 'Grupo de cafe', 'Molinillo')):
        continue                       # cafetera y molinillo parametricos
    if s['mat'] == 'CN Vidrio' and nm.startswith(
            ('PB Mampara de vidrio', 'Escaparate - pano', 'Barandilla')):
        mat = M_VIDRIO_ARQ
    if '- lamina' in nm:
        mat = ARTE[hash(nm) % 3]
    elif nm.startswith('Cuadro Sur'):
        mat = ARTE[hash(nm) % 3]        # estos no llevan lamina separada
    elif nm.startswith('Cuadro'):
        mat = MAT['CN Negro mate']
    col = col_pa if is_pa(s) else col_pb
    prism(nm, s['poly'], s['n'], s['d'], mat, col)

# ---------------------------------------------------------------- props
def primitive(kind, mat, loc, scale, rot=(0,0,0), col=col_pb, seg=24):
    if kind == 'sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg//2,
                                             radius=1, location=loc)
    elif kind == 'cyl':
        bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=1, depth=1,
                                            location=loc)
    elif kind == 'cone':
        bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=1, radius2=0.55,
                                        depth=1, location=loc)
    elif kind == 'torus':
        bpy.ops.mesh.primitive_torus_add(location=loc,
                                         major_radius=1, minor_radius=0.18,
                                         major_segments=seg, minor_segments=10)
    ob = bpy.context.active_object
    ob.scale = scale
    ob.rotation_euler = rot
    ob.data.materials.append(mat)
    for p in ob.data.polygons: p.use_smooth = True
    try: ob.data.set_sharp_from_angle(angle=math.radians(46))
    except Exception: pass
    for c in ob.users_collection: c.objects.unlink(ob)
    col.objects.link(ob)
    return ob

# bolleria en las vitrinas: croissants con forma de croissant, donuts y bollos
def croissant(cx, cy, z0, ang, sc):
    # cuerpo central y lobulos decrecientes siguiendo un arco
    for k, (off, size) in enumerate([(0.0, 1.0), (0.042, 0.78), (0.078, 0.5),
                                     (-0.042, 0.78), (-0.078, 0.5)]):
        aa = ang + off * 16
        px = cx + math.sin(off*13) * sc * 0.01
        lx = cx + off * sc * math.cos(ang) - math.sin(ang) * abs(off) * 0.55 * sc
        ly = cy + off * sc * math.sin(ang) + math.cos(ang) * abs(off) * 0.55 * sc
        primitive('sphere', M_CROISSANT, (lx, ly, z0 + 0.019 * size + 0.004),
                  (0.034*sc*size, 0.024*sc*size, 0.021*sc*size),
                  (0, 0, aa), seg=16)

def donut(cx, cy, z0, choc):
    bpy.ops.mesh.primitive_torus_add(location=(cx, cy, z0 + 0.014),
                                     major_radius=0.028, minor_radius=0.013,
                                     major_segments=24, minor_segments=12)
    ob = bpy.context.active_object
    ob.scale = (1, 1, 0.82)
    ob.data.materials.append(M_BOLLO if choc else M_CROISSANT)
    for pg in ob.data.polygons: pg.use_smooth = True
    for c in ob.users_collection: c.objects.unlink(ob)
    col_pb.objects.link(ob)

for i, s in enumerate(productos):
    cx, cy, cz = centro(s)
    zs = [p[2] for p in s['poly']]
    z0 = min(min(zs), min(zs) + s['n'][2]*s['d'])
    k = i % 4
    if k == 0 or k == 1:
        croissant(cx, cy, z0, math.radians(random.uniform(0, 360)),
                  random.uniform(0.9, 1.1))
    elif k == 2:
        donut(cx, cy, z0, i % 8 < 4)
    else:
        primitive('sphere', M_BOLLO, (cx, cy, z0 + 0.024),
                  (0.045, 0.045, 0.026))

# botellas de vidrio en la estanteria
for s in botellas:
    xs = [p[0] for p in s['poly']]; ys = [p[1] for p in s['poly']]
    cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
    z0 = s['poly'][0][2]
    h = abs(s['d'])
    mat = M_VAMBAR if s['mat'] == 'CN Terracota' else M_VVERDE
    cuerpo = h * 0.62
    primitive('cyl', mat, (cx, cy, z0 + cuerpo/2), (0.034, 0.034, cuerpo))
    primitive('cone', mat, (cx, cy, z0 + cuerpo + h*0.14), (0.033, 0.033, h*0.28))
    primitive('cyl', mat, (cx, cy, z0 + cuerpo + h*0.28 + h*0.05),
              (0.011, 0.011, h*0.10))
    primitive('cyl', M_CORCHO, (cx, cy, z0 + cuerpo + h*0.28 + h*0.115),
              (0.012, 0.012, 0.012))

# follaje de las plantas: racimos densos de esferitas en tres verdes
M_HOJAS = [plain('hoja_oscura', srgb('3F5A32'), 0.85),
           plain('hoja_media', srgb('557440'), 0.85),
           plain('hoja_clara', srgb('6E8B52'), 0.85)]

def copa_hojas(cx, cy, cz, rx, rz, n, rmin, rmax, seed):
    rl = random.Random(seed)
    for _ in range(n):
        a = rl.uniform(0, 2*math.pi)
        u = rl.uniform(0, 1) ** 0.6
        dz = rl.uniform(-1, 1)
        px = cx + math.cos(a) * u * rx
        py = cy + math.sin(a) * u * rx
        pz = cz + dz * rz
        rs = rl.uniform(rmin, rmax)
        primitive('sphere', M_HOJAS[rl.randrange(3)], (px, py, pz),
                  (rs, rs, rs*0.9), seg=10)

for s in plantas:
    xs = [p[0] for p in s['poly']]; ys = [p[1] for p in s['poly']]
    cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
    zs = [p[2] for p in s['poly']]
    z0 = min(min(zs), min(zs) + s['n'][2]*s['d'])
    z1 = max(max(zs), max(zs) + s['n'][2]*s['d'])
    rr = (max(xs) - min(xs))/2
    copa_hojas(cx, cy, (z0+z1)/2, rr*0.85, (z1-z0)*0.5, 60, rr*0.16, rr*0.30,
               int(cx*97 + cy*31))

M_PATA = pbr_tex('pata_madera', 'wood_diff', 'wood_rough', 'wood_nrm',
                  0.6, tint=(1.02, 0.98, 0.92), nrm_str=0.3)

def _rot2(px, py, ang):
    c, si = math.cos(ang), math.sin(ang)
    return px*c - py*si, px*si + py*c

def bevelmod(ob, w, seg):
    bv = ob.modifiers.new('bv', 'BEVEL')
    bv.width = w; bv.segments = seg
    bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(45)
    return ob

# Silla de casco curvo tapizado con patas de madera torneada
def silla_real(cx, cy, ang, tela):
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        lx, ly = _rot2(sx*0.155, sy*0.155, ang)
        primitive('cone', M_PATA, (cx + lx, cy + ly, 0.215),
                  (0.017, 0.017, 0.43), (sx*0.06, -sy*0.06, 0), seg=12)
    st = primitive('cyl', tela, (cx, cy, 0.455), (0.205, 0.205, 0.055))
    bevelmod(st, 0.022, 3)
    # respaldo: casco curvado de 150 grados, malla de quads limpia
    n = 20
    r0, r1 = 0.205, 0.165
    z0v, z1v = 0.48, 0.78
    a0 = ang + math.pi - math.radians(75)
    a1 = ang + math.pi + math.radians(75)
    vs = []
    for i in range(n + 1):
        t = a0 + (a1 - a0) * i / n
        co, si2 = math.cos(t), math.sin(t)
        vs += [(cx + r0*co, cy + r0*si2, z0v), (cx + r1*co, cy + r1*si2, z0v),
               (cx + r0*co, cy + r0*si2, z1v), (cx + r1*co, cy + r1*si2, z1v)]
    fs = []
    for i in range(n):
        k = i*4
        fs += [[k, k+4, k+6, k+2],       # cara exterior
               [k+1, k+3, k+7, k+5],     # cara interior
               [k+2, k+6, k+7, k+3],     # canto superior
               [k+4, k, k+1, k+5]]       # canto inferior
    fs += [[0, 2, 3, 1], [4*n, 4*n+1, 4*n+3, 4*n+2]]
    sh = add_mesh('Silla - respaldo', vs, fs, tela, col_pb, smooth=False)
    for pg in sh.data.polygons: pg.use_smooth = True
    try: sh.data.set_sharp_from_angle(angle=math.radians(40))
    except Exception: pass
    for m in sh.modifiers:
        if m.type == 'BEVEL': m.width = 0.016; m.segments = 3

def mesa_real(cx, cy):
    b = primitive('cyl', MAT['CN Negro mate'], (cx, cy, 0.015),
                  (0.20, 0.20, 0.03)); bevelmod(b, 0.008, 2)
    primitive('cyl', MAT['CN Negro mate'], (cx, cy, 0.37), (0.026, 0.026, 0.68))
    tp = primitive('cyl', MAT['CN Madera tablero'], (cx, cy, 0.735),
                   (0.37, 0.37, 0.035), seg=48)
    bevelmod(tp, 0.012, 3)

def taburete(cx, cy):
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        primitive('cone', M_PATA, (cx + sx*0.12, cy + sy*0.12, 0.31),
                  (0.017, 0.017, 0.62), (sx*0.09, -sy*0.09, 0), seg=12)
    tor = primitive('torus', MAT['CN Negro mate'], (cx, cy, 0.24),
                    (0.135, 0.135, 0.135), seg=24)
    st = primitive('cyl', MAT['CN Madera tablero'], (cx, cy, 0.645),
                   (0.165, 0.165, 0.045), seg=32)
    bevelmod(st, 0.015, 3)

def box3(name, x0, y0, x1, y1, z0, z1, mat):
    verts = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
             (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    faces = [[0,1,2,3],[7,6,5,4],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]]
    return add_mesh(name, verts, faces, mat, col_pb)

M_CROMO = plain('cromo', srgb('D9DDE0'), 0.12, 1.0)

def cafetera():
    zb = 1.04
    bx3 = box3('Cafetera - cuerpo', 6.32, 6.80, 7.02, 7.28, zb, zb + 0.36,
               M_CROMO)
    for m in bx3.modifiers:
        if m.type == 'BEVEL': m.width = 0.02; m.segments = 3
    box3('Cafetera - bandeja', 6.34, 6.72, 7.00, 6.90, zb, zb + 0.02,
         MAT['CN Negro mate'])
    box3('Cafetera - panel', 6.34, 6.79, 7.00, 6.81, zb + 0.10, zb + 0.34,
         MAT['CN Negro mate'])
    for i, gx in enumerate((6.52, 6.82)):
        primitive('cyl', M_CROMO, (gx, 6.83, zb + 0.115), (0.045, 0.045, 0.07))
        primitive('cyl', M_CROMO, (gx, 6.80, zb + 0.075), (0.05, 0.05, 0.018))
        primitive('cyl', MAT['CN Negro mate'],
                  (gx, 6.70, zb + 0.065), (0.013, 0.013, 0.13),
                  (math.radians(80), 0, 0), seg=12)
    primitive('cyl', M_CROMO, (7.06, 6.95, zb + 0.16), (0.008, 0.008, 0.22),
              (math.radians(25), math.radians(10), 0), seg=10)
    box3('Cafetera - calientatazas', 6.34, 6.82, 7.00, 7.26,
         zb + 0.36, zb + 0.375, M_CROMO)
    for k, (dx, dy) in enumerate(((0.12, 0.10), (0.28, 0.16), (0.45, 0.09),
                                  (0.20, 0.30), (0.38, 0.28))):
        primitive('cyl', M_CERAMICA, (6.36 + dx, 6.84 + dy, zb + 0.405),
                  (0.033, 0.033, 0.05))
    # molinillo
    primitive('cyl', MAT['CN Negro mate'], (7.27, 6.98, zb + 0.15),
              (0.055, 0.055, 0.30))
    primitive('cone', glassm('tolva'), (7.27, 6.98, zb + 0.37),
              (0.055, 0.055, 0.14), (math.pi, 0, 0))

cafetera()

# azucarero, salero y servilletero en cada mesa
M_METAL = plain('tapa_metal', srgb('B9BDC0'), 0.3, 1.0)
def set_mesa(mx, my, seed):
    rl = random.Random(seed)
    a = rl.uniform(0, 2*math.pi)
    px, py = mx + 0.20*math.cos(a), my + 0.20*math.sin(a)
    box3('Servilletero', px - 0.055, py - 0.02, px + 0.055, py + 0.02,
         0.76, 0.845, M_CERAMICA)
    for k in (-1, 1):
        primitive('cyl', glassm('frasco'), (px + k*0.03, py - 0.06, 0.795),
                  (0.014, 0.014, 0.06), seg=12)
        primitive('cyl', M_METAL, (px + k*0.03, py - 0.06, 0.833),
                  (0.0145, 0.0145, 0.014), seg=12)

MESAS_R = [(2.00, 2.65), (2.00, 4.15), (2.00, 5.60),
           (4.15, 2.65), (4.15, 4.15), (4.15, 5.60)]
for i, (mx, my) in enumerate(MESAS_R):
    mesa_real(mx, my)
    t1 = MAT['CN Tela azul'] if i % 2 == 0 else MAT['CN Tela']
    t2 = MAT['CN Tela'] if i % 2 == 0 else MAT['CN Tela azul']
    j = (i * 37) % 13 - 6
    silla_real(mx - 0.63, my, math.radians(j), t1)
    silla_real(mx + 0.63, my, math.pi + math.radians(-j), t2)
    set_mesa(mx, my, i * 11 + 3)

# taburetes frente al mostrador alto de la barra
for tx in (6.55, 7.15, 7.75):
    taburete(tx, 6.12)

# ---- carta de menu sobre la pared norte ------------------------------------
def menu_board():
    x0, x1 = 7.62, 9.32
    y = 8.905
    z0, z1 = 1.42, 2.28
    box3('Carta - marco', x0 - 0.02, y - 0.052, x1 + 0.02, y - 0.04,
         z0 - 0.02, z1 + 0.02, MAT['CN Negro mate'])
    box3('Carta - panel', x0, y - 0.055, x1, y - 0.045, z0, z1,
         plain('carta_blanca', srgb('F4F1E9'), 0.7))
    m_txt = plain('carta_texto', srgb('3A3A38'), 0.6)
    def linea(txt, tx, tz, h):
        cu = bpy.data.curves.new('t', 'FONT'); cu.body = txt
        cu.size = h; cu.extrude = 0.001; cu.align_x = 'LEFT'
        ob = bpy.data.objects.new('carta_txt', cu)
        ob.location = (tx, y - 0.058, tz)
        ob.rotation_euler = (math.radians(90), 0, 0)
        ob.data.materials.append(m_txt)
        col_pb.objects.link(ob)
    linea('CAFFE', 7.78, 2.08, 0.075)
    for k, t in enumerate(['Espresso ........ 1,50', 'Cappuccino .... 2,20',
                           'Caffe Latte ..... 2,80', 'Cortado ......... 1,80']):
        linea(t, 7.78, 1.94 - k*0.115, 0.052)
    linea('COLAZIONE', 8.55, 2.08, 0.075)
    for k, t in enumerate(['Cornetto ........ 1,80', 'Tiramisu ........ 3,50',
                           'Panini ............ 4,50', 'Spremuta ....... 3,00']):
        linea(t, 8.55, 1.94 - k*0.115, 0.052)

menu_board()

# taza con cafe + platillo
def taza(x, y, z):
    primitive('cyl', M_CERAMICA, (x, y, z + 0.004), (0.055, 0.055, 0.008))
    primitive('cyl', M_CERAMICA, (x, y, z + 0.008 + 0.028), (0.037, 0.037, 0.056))
    primitive('cyl', M_CAFE, (x, y, z + 0.008 + 0.052), (0.031, 0.031, 0.004))
    primitive('torus', M_CERAMICA, (x + 0.040, y, z + 0.038),
              (0.016, 0.016, 0.016), (math.radians(90), 0, 0), seg=16)

def jarron(x, y, z):
    primitive('cyl', M_CERAMICA, (x, y, z + 0.030),
              (0.020, 0.020, 0.06))
    random.seed(int(x*53 + y*17))
    for k in range(3):
        a = random.uniform(0, 6.28); r = 0.012
        fx, fy = x + math.cos(a)*r, y + math.sin(a)*r
        h = random.uniform(0.075, 0.105)
        primitive('cyl', M_TALLO, (fx, fy, z + 0.05 + h/2),
                  (0.0016, 0.0016, h), seg=8)
        primitive('sphere', (M_FLOR_B, M_FLOR_A)[k % 2],
                  (fx, fy, z + 0.05 + h + 0.008), (0.011, 0.011, 0.009), seg=12)

MESAS = [(2.00, 2.65), (2.00, 4.15), (2.00, 5.60),
         (4.15, 2.65), (4.15, 4.15), (4.15, 5.60)]
ZT = 0.76
for i, (mx, my) in enumerate(MESAS):
    jarron(mx - 0.10, my + 0.11, ZT)
    if i % 3 != 1:
        taza(mx + 0.14, my - 0.10, ZT)
    if i % 3 == 0:
        taza(mx - 0.16, my - 0.13, ZT)

# platos y tazas junto a la cafetera (mostrador alto, tabla a 1.04)
ZB = 0.98 + 0.06
for k in range(4):
    primitive('cyl', M_CERAMICA, (7.55, 6.80, ZB + 0.008 + k*0.016),
              (0.062, 0.062, 0.014))
for dx, dy in ((0.0, 0.0), (0.11, 0.05), (0.05, -0.09)):
    primitive('cyl', M_CERAMICA, (7.72 + dx, 6.72 + dy, ZB + 0.026),
              (0.036, 0.036, 0.052))

# texto del rotulo del altillo (mirando a la entrada)
def texto(txt, loc, h, rot, mat, extrude=0.006):
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = txt
    cu.size = h; cu.extrude = extrude; cu.align_x = 'CENTER'
    ob = bpy.data.objects.new('txt', cu)
    ob.location = loc; ob.rotation_euler = rot
    ob.data.materials.append(mat)
    col_pb.objects.link(ob)
_t = bpy.data.curves.new('t', 'FONT'); _t.body = 'CAFE  NAPOLI'
_t.size = 0.15; _t.extrude = 0.006; _t.align_x = 'CENTER'
_to = bpy.data.objects.new('txt_altillo', _t)
_to.location = (5.5, 3.884, 2.655)
_to.rotation_euler = (math.radians(90), 0, 0)
_to.data.materials.append(plain('crema', srgb('F2EEE2'), .4))
col_pa.objects.link(_to)
texto('CAFE  NAPOLI', (7.97, 0.325, 3.16), 0.26,
      (math.radians(90), 0, 0), plain('crema2', srgb('F2EEE2'), .4))

# ---- contexto exterior: acera, calzada, edificio de enfrente ---------------
M_ACERA = pbr_tex('acera_tx', 'wall_diff', 'wall_rough', 'wall_nrm', 2.0,
                  tint=(0.62, 0.61, 0.59), nrm_str=0.5)
M_ASFAL = plain('asfalto', srgb('4A4A48'), 0.9)
add_mesh('acera', [(-4, -2.2, -0.001), (15, -2.2, -0.001),
                   (15, 0.38, -0.001), (-4, 0.38, -0.001)],
         [[0, 1, 2, 3]], M_ACERA, col_pb)
add_mesh('calzada', [(-4, -8.5, -0.012), (15, -8.5, -0.012),
                     (15, -2.2, -0.012), (-4, -2.2, -0.012)],
         [[0, 1, 2, 3]], M_ASFAL, col_pb)
M_FACHV = pbr_tex('fachada_vecina', 'facade', None, None, 7.0,
                  base_rough=0.8)
add_mesh('edificio_enfrente', [(-4, -8.6, 0), (15, -8.6, 0),
                               (15, -8.6, 8.5), (-4, -8.6, 8.5)],
         [[0, 1, 2, 3]], M_FACHV, col_pb)

# arboles de calle con alcorque
for tx in (5.35, 11.3):
    box3('Alcorque', tx - 0.5, -1.95, tx + 0.5, -0.95, -0.003, 0.008,
         plain('alcorque', srgb('5A5248'), 0.9))
    primitive('cyl', pbr_tex('tronco_arbol', 'wood_diff_v', None, 'wood_nrm_v',
                             0.5, tint=(0.55, 0.45, 0.36), base_rough=0.8),
              (tx, -1.45, 1.30), (0.09, 0.09, 2.6), seg=14)
    copa_hojas(tx, -1.45, 3.15, 0.95, 0.75, 90, 0.14, 0.26, int(tx*13))

# toldo azul sobre el escaparate, como el de la referencia
M_TOLDO = pbr_tex('toldo', None, 'fabric_rough', 'fabric_nrm', 0.8,
                  color=srgb('3E6B99'), sheen=0.6, nrm_str=0.4)
tx0, tx1 = 6.23, 9.71
ty0, tproj = 0.33, 1.15
tz1, tz0 = 2.98, 2.55
vs = [(tx0, ty0, tz1), (tx1, ty0, tz1),
      (tx1, ty0 - tproj, tz0), (tx0, ty0 - tproj, tz0),
      (tx0, ty0, tz1 - 0.02), (tx1, ty0, tz1 - 0.02),
      (tx1, ty0 - tproj, tz0 - 0.02), (tx0, ty0 - tproj, tz0 - 0.02)]
fs = [[0, 1, 2, 3], [7, 6, 5, 4], [0, 4, 5, 1], [1, 5, 6, 2],
      [2, 6, 7, 3], [3, 7, 4, 0]]
add_mesh('Toldo', vs, fs, M_TOLDO, col_pb)
box3('Toldo - faldon', tx0, ty0 - tproj - 0.02, tx1, ty0 - tproj,
     tz0 - 0.18, tz0, M_TOLDO)

# terraza: dos mesas con sillas en la acera
for i, tx in enumerate((6.85, 9.05)):
    mesa_real(tx, -1.05)
    silla_real(tx, -0.42, math.radians(-90 + (7 if i else -5)), MAT['CN Tela'])
    silla_real(tx, -1.68, math.radians(90 + (-6 if i else 8)),
               MAT['CN Tela azul'])
    set_mesa(tx, -1.05, 91 + i)

# ---------------------------------------------------------------- luces
def light(kind, loc, power, color=(1.0, 0.78, 0.55), size=0.05, rot=None):
    ld = bpy.data.lights.new('l', kind)
    ld.energy = power; ld.color = color
    if kind in ('POINT', 'SPOT'): ld.shadow_soft_size = size
    if kind == 'SPOT': ld.spot_size = math.radians(95); ld.spot_blend = 0.6
    if kind == 'AREA': ld.size = size
    ob = bpy.data.objects.new('l', ld)
    ob.location = loc
    if rot: ob.rotation_euler = rot
    col_pb.objects.link(ob)
    return ob

for cx, cy, cz in lamparas:
    light('POINT', (cx, cy, cz - 0.05), 22)
for cx, cy, cz in empotrados:
    light('SPOT', (cx, cy, cz - 0.04), 9, rot=(0, 0, 0))
for cx, cy, cz in apliques:
    light('POINT', (cx + 0.14, cy, cz + 0.06), 6, size=0.03)

# sol y cielo
sun = bpy.data.lights.new('sun', 'SUN')
sun.energy = 3.8; sun.angle = math.radians(2)
so = bpy.data.objects.new('sun', sun)
so.rotation_euler = (math.radians(62), 0, math.radians(-155))
col_pb.objects.link(so)
w = bpy.data.worlds.new('w'); scene.world = w; w.use_nodes = True
bgn = w.node_tree.nodes['Background']
try:
    sky = w.node_tree.nodes.new('ShaderNodeTexSky')
    sky.sun_elevation = math.radians(38); sky.sun_rotation = math.radians(25)
    sky.sun_intensity = 0.35
    w.node_tree.links.new(sky.outputs['Color'], bgn.inputs['Color'])
    bgn.inputs['Strength'].default_value = 0.95
except Exception:
    bgn.inputs['Color'].default_value = (0.75, 0.83, 0.92, 1)
    bgn.inputs['Strength'].default_value = 0.6

# luz de dia entrando por el escaparate
light('AREA', (7.97, 0.32, 1.6), 520, (0.88, 0.92, 1.0), 3.0,
      rot=(math.radians(-90), 0, 0))
# relleno alto en la doble altura para el ambiente aireado de la referencia
light('AREA', (7.9, 2.0, 5.2), 320, (1.0, 0.97, 0.92), 2.6,
      rot=(0, 0, 0))
light('AREA', (5.0, 5.0, 2.60), 140, (1.0, 0.96, 0.90), 2.2, rot=(0, 0, 0))

# ---------------------------------------------------------------- camaras
def render_view(fn, eye, target, lens=24, hide_pa=False, fstop=4.0):
    col_pa.hide_render = hide_pa
    scene.view_settings.exposure = -0.25 if hide_pa else 0.30
    cd = bpy.data.cameras.new('c'); cd.lens = lens; cd.sensor_width = 36
    cd.clip_start = 0.03
    cd.dof.use_dof = True
    cd.dof.focus_distance = (Vector(target) - Vector(eye)).length * 0.85
    cd.dof.aperture_fstop = fstop
    cam = bpy.data.objects.new('cam', cd)
    scene.collection.objects.link(cam)
    cam.location = eye
    d = Vector(target) - Vector(eye)
    dh = Vector((d.x, d.y, 0.0))
    pitch = math.atan2(d.z, dh.length)
    if abs(pitch) < math.radians(26) and dh.length > 0.1:
        cam.rotation_euler = dh.to_track_quat('-Z', 'Y').to_euler()
        cd.shift_y = math.tan(pitch) * lens / cd.sensor_width
    else:
        cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam
    import os
    scene.render.filepath = os.path.join('/tmp/claude-0/-home-user-modelo-2-italiano/30d2763c-3169-519a-ac78-c5a47134634b/scratchpad', fn)
    bpy.ops.render.render(write_still=True)
    print('RENDER OK', fn, flush=True)

import sys
views = {
 'R_entrada':   ((8.55, 1.30, 1.55), (4.90, 7.35, 1.05), 26, False, 4.0),
 'R_barra':     ((2.55, 4.65, 1.50), (6.90, 7.30, 1.00), 27, False, 3.5),
 'R_sala':      ((1.15, 6.55, 1.55), (6.50, 1.60, 1.10), 24, False, 4.5),
 'R_vitrinas':  ((5.15, 5.45, 1.35), (4.35, 7.30, 0.95), 30, False, 2.6),
 'R_mampara':   ((4.90, 4.30, 1.60), (1.00, 8.10, 1.10), 25, False, 3.5),
 'R_aerea':     ((11.5, -1.8, 9.5), (4.6, 5.2, 0.4), 30, True, 11.0),
 'R_fachada':   ((8.6, -4.6, 1.55), (7.6, 0.5, 2.3), 27, False, 8.0),
 'R_barra_frontal': ((5.75, 4.35, 1.45), (5.75, 7.43, 1.02), 28, False, 5.0),
 'R_rincon':        ((0.72, 2.15, 1.52), (6.60, 7.10, 1.05), 22, False, 5.0),
 'R_detalle':       ((2.95, 2.02, 1.12), (2.02, 2.70, 0.80), 50, False, 2.2),
 'R_estanteria':    ((5.90, 5.72, 1.30), (5.90, 8.95, 1.48), 24, False, 4.5),
 'R_escalera':      ((7.00, 2.85, 1.50), (9.45, 6.55, 1.75), 24, False, 5.0),
 'R_terraza':       ((3.40, -3.90, 1.60), (8.30, 0.20, 2.00), 28, False, 6.0),
}
which = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(views)
for k in which:
    eye, tgt, lens, hide, fs = views[k]
    render_view(k + '.png', eye, tgt, lens, hide, fs)
