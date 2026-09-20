# -*- coding: utf-8 -*-
"""
Libreria base de la biblioteca de objetos 1:1 para el render final.
Se ejecuta con el modulo `bpy` (Blender 5.0 como modulo de Python), Cycles.

CONVENCIONES (iguales para todos los objetos)
  - Unidades: metros. Cada objeto sale a milimetro exacto sobre las medidas
    de docs/planos/equipamiento.py (ancho x fondo x alto), que es la unica
    fuente de verdad.
  - Origen del objeto: centro de su huella, z = 0 en la base (apoya en el
    suelo o en la encimera en z = 0). El FRENTE mira a -Y; el ancho va en X,
    el fondo en Y, el alto en Z.
  - Cada objeto es una coleccion <TAG> con un Empty raiz <TAG> y todas sus
    piezas como mallas hijas. Mover el Empty mueve el aparato entero.
  - Materiales procedurales (no dependen de texturas externas), salvo las
    calcas (serigrafia, pantallas), que van como imagenes empaquetadas.
  - Salida: blend/<TAG>.blend (autocontenido, comprimido) y
    preview/<TAG>.png (hoja de 4 vistas) + preview/<TAG>_34.png.
"""
import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
PLANOS = os.path.join(os.path.dirname(AQUI), 'planos')
sys.path.insert(0, PLANOS)
import equipamiento as Q          # noqa: E402

BLEND_DIR = os.path.join(AQUI, 'blend')
PREVIEW_DIR = os.path.join(AQUI, 'preview')
CALCAS_DIR = os.path.join(AQUI, 'calcas')
SCRATCH = os.environ.get('OBJ_SCRATCH',
                         '/tmp/claude-0/-home-user-modelo-2-italiano/'
                         '30d2763c-3169-519a-ac78-c5a47134634b/scratchpad')
HDRI = os.path.join(SCRATCH, 'ph', 'studio_small_09_2k.hdr')
for d in (BLEND_DIR, PREVIEW_DIR, CALCAS_DIR):
    os.makedirs(d, exist_ok=True)

MEDIDAS = {p['tag']: (p['a'], p['f'], p['h']) for p in Q.todos()}
FICHAS = {p['tag']: p for p in Q.todos()}


# ============================================================ documento
def nuevo_documento(tag):
    # los materiales cacheados pertenecen al documento anterior: al abrir uno
    # nuevo quedan liberados y hay que olvidarlos (si no, el segundo objeto
    # del mismo proceso falla al tocar un datablock muerto)
    _MATS.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = tag
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0
    sc.unit_settings.length_unit = 'METERS'
    return sc


_col_actual = None
_raiz_actual = None


def raiz(tag):
    """Coleccion <TAG> + Empty raiz <TAG> en el origen."""
    global _col_actual, _raiz_actual
    col = bpy.data.collections.new(tag)
    bpy.context.scene.collection.children.link(col)
    e = bpy.data.objects.new(tag, None)
    e.empty_display_type = 'ARROWS'
    e.empty_display_size = 0.15
    col.objects.link(e)
    f = FICHAS.get(tag)
    if f:
        e['tag'] = tag
        e['nombre'] = f['nombre']
        e['ancho_fondo_alto_m'] = list(MEDIDAS[tag])
        e['makro'] = f['url'] or 'no es de Makro'
    _col_actual, _raiz_actual = col, e
    return col, e


def _registrar(ob, mat=None, parent=None):
    """Enlaza la malla a la coleccion actual, la cuelga del Empty raiz y le
    pone material. Devuelve el objeto."""
    col = _col_actual or bpy.context.scene.collection
    col.objects.link(ob)
    ob.parent = parent if parent is not None else _raiz_actual
    if mat is not None:
        if isinstance(mat, (list, tuple)):
            for m in mat:
                ob.data.materials.append(m)
        else:
            ob.data.materials.append(mat)
    return ob


# ============================================================ UV
def uv_cubo(ob, escala=1.0):
    """Proyeccion cubica manual, determinista, en coordenadas de objeto
    (metros / escala). Sirve para el rayado del inox y para las calcas."""
    me = ob.data
    if not me.uv_layers:
        me.uv_layers.new(name='UVMap')
    uv = me.uv_layers[0].data
    for poly in me.polygons:
        n = poly.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            if az >= ax and az >= ay:
                u, v = co.x, co.y
            elif ax >= ay:
                u, v = co.y, co.z
            else:
                u, v = co.x, co.z
            uv[li].uv = (u / escala, v / escala)


# ============================================================ geometria
def _malla_desde_bm(nombre, bm, mat=None, parent=None, uv=True, suave=False):
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    me.update()
    ob = bpy.data.objects.new(nombre, me)
    _registrar(ob, mat, parent)
    if uv:
        uv_cubo(ob)
    if suave:
        for p in me.polygons:
            p.use_smooth = True
        _autosuave(ob)
    return ob


def normales_ponderadas(ob):
    """Normales personalizadas ponderadas por area (modificador Weighted
    Normal aplicado): las caras planas grandes quedan realmente planas
    aunque esten suavizadas junto a biseles finos. Evita el 'abanico' de
    reflejos en tapas y frentes."""
    if ob.type != 'MESH' or not any(p.use_smooth for p in ob.data.polygons):
        return ob
    mod = ob.modifiers.new('wn', 'WEIGHTED_NORMAL')
    mod.mode = 'FACE_AREA'
    mod.keep_sharp = True
    mod.weight = 50
    try:
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
            bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception:
        ob.modifiers.remove(mod)
    return ob


def _autosuave(ob, ang=30.0):
    """Sombreado suave por angulo (Smooth by Angle) sin depender del
    operador: modificador de nodos si existe, si no marca todo suave."""
    try:
        with bpy.context.temp_override(object=ob, active_object=ob,
                                       selected_objects=[ob]):
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(ang))
    except Exception:
        pass
    normales_ponderadas(ob)


def _bevel_bm(bm, edges, r, segs):
    if r <= 0 or not edges:
        return
    bmesh.ops.bevel(bm, geom=edges, offset=r, offset_type='OFFSET',
                    segments=segs, profile=0.5, affect='EDGES',
                    clamp_overlap=True, loop_slide=True)


def caja(nombre, w, d, h, pos=(0, 0, 0), r=0.0, r_vert=None, segs=4,
         mat=None, parent=None, suave=True):
    """Caja de w (X) x d (Y) x h (Z). `pos` es el centro de la base.
    r: radio de todas las aristas. r_vert: radio propio de las 4 aristas
    verticales (para cuerpos con esquinas redondeadas y cantos superiores
    finos): si se da, r se aplica solo a las horizontales."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w, d, h), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(pos[0], pos[1], pos[2] + h / 2), verts=bm.verts)
    bm.edges.ensure_lookup_table()
    if r_vert is not None:
        vert_e = [e for e in bm.edges
                  if abs((e.verts[0].co - e.verts[1].co).normalized().z) > 0.99]
        _bevel_bm(bm, vert_e, min(r_vert, w / 2 - 1e-4, d / 2 - 1e-4), max(segs, 6))
        bm.edges.ensure_lookup_table()
        horiz_e = [e for e in bm.edges
                   if abs((e.verts[0].co - e.verts[1].co).normalized().z) < 0.01]
        _bevel_bm(bm, horiz_e, min(r, h / 2 - 1e-4), segs)
    elif r > 0:
        _bevel_bm(bm, list(bm.edges), min(r, w / 2 - 1e-4, d / 2 - 1e-4, h / 2 - 1e-4), segs)
    return _malla_desde_bm(nombre, bm, mat, parent, suave=suave and (r > 0 or r_vert))


def cilindro(nombre, radio, h, pos=(0, 0, 0), eje='Z', segs=64, r=0.0,
             r_segs=3, mat=None, parent=None, radio2=None):
    """Cilindro (o cono truncado con radio2) de altura h a lo largo de `eje`.
    `pos` es el centro de la cara inferior (para eje Z) o del extremo
    negativo (X, Y). r: redondeo de las aristas de las tapas."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs,
                          radius1=radio, radius2=radio if radio2 is None else radio2,
                          depth=h)
    bmesh.ops.translate(bm, vec=(0, 0, h / 2), verts=bm.verts)
    if r > 0:
        bm.edges.ensure_lookup_table()
        tapas = [e for e in bm.edges
                 if abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-6]
        _bevel_bm(bm, tapas, min(r, radio * 0.9, h / 2 - 1e-4), r_segs)
    if eje == 'X':
        bmesh.ops.rotate(bm, cent=(0, 0, 0), verts=bm.verts, matrix=_rot('Y', 90))
    elif eje == 'Y':
        bmesh.ops.rotate(bm, cent=(0, 0, 0), verts=bm.verts,
                         matrix=_rot('X', -90))
    bmesh.ops.translate(bm, vec=pos, verts=bm.verts)
    return _malla_desde_bm(nombre, bm, mat, parent, suave=True)


def _rot(eje, grados):
    from mathutils import Matrix
    return Matrix.Rotation(math.radians(grados), 3, eje)


def tubo(nombre, r_ext, r_int, h, pos=(0, 0, 0), eje='Z', segs=64, mat=None,
         parent=None):
    """Tubo hueco (anillo extruido)."""
    bm = bmesh.new()
    v_ext = [bm.verts.new((r_ext * math.cos(2 * math.pi * i / segs),
                           r_ext * math.sin(2 * math.pi * i / segs), 0)) for i in range(segs)]
    v_int = [bm.verts.new((r_int * math.cos(2 * math.pi * i / segs),
                           r_int * math.sin(2 * math.pi * i / segs), 0)) for i in range(segs)]
    caras = []
    for i in range(segs):
        j = (i + 1) % segs
        caras.append(bm.faces.new((v_ext[i], v_ext[j], v_int[j], v_int[i])))
    res = bmesh.ops.extrude_face_region(bm, geom=caras)
    vs = [g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, h), verts=vs)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if eje == 'X':
        bmesh.ops.rotate(bm, cent=(0, 0, 0), verts=bm.verts, matrix=_rot('Y', 90))
    elif eje == 'Y':
        bmesh.ops.rotate(bm, cent=(0, 0, 0), verts=bm.verts, matrix=_rot('X', -90))
    bmesh.ops.translate(bm, vec=pos, verts=bm.verts)
    return _malla_desde_bm(nombre, bm, mat, parent, suave=True)


def prisma(nombre, pts, h, pos=(0, 0, 0), mat=None, parent=None, r=0.0,
           segs=4, suave=False):
    """Poligono 2D (lista de (x, y), antihorario) extruido h en Z.
    `pos` desplaza el conjunto; z de pos = base."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0)) for x, y in pts]
    f = bm.faces.new(vs)
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    top = [g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, h), verts=top)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if r > 0:
        bm.edges.ensure_lookup_table()
        _bevel_bm(bm, list(bm.edges), r, segs)
    bmesh.ops.translate(bm, vec=pos, verts=bm.verts)
    return _malla_desde_bm(nombre, bm, mat, parent, suave=suave or r > 0)


def perfil_revolucion(nombre, perfil, pos=(0, 0, 0), segs=64, mat=None,
                      parent=None, cerrar=True):
    """Superficie de revolucion alrededor de Z de un perfil [(r, z), ...]
    ordenado de abajo arriba. Con cerrar=True tapa arriba y abajo."""
    bm = bmesh.new()
    anillos = []
    for r, z in perfil:
        if r < 1e-6:
            anillos.append([bm.verts.new((0, 0, z))] * segs)
        else:
            anillos.append([bm.verts.new((r * math.cos(2 * math.pi * i / segs),
                                          r * math.sin(2 * math.pi * i / segs), z))
                            for i in range(segs)])
    for a, b in zip(anillos, anillos[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            quad = [a[i], a[j], b[j], b[i]]
            uniq = []
            for v in quad:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) >= 3:
                try:
                    bm.faces.new(uniq)
                except ValueError:
                    pass
    if cerrar:
        for anillo in (anillos[0], anillos[-1]):
            if anillo[0] is not anillo[1]:
                try:
                    bm.faces.new(anillo)
                except ValueError:
                    pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.translate(bm, vec=pos, verts=bm.verts)
    return _malla_desde_bm(nombre, bm, mat, parent, suave=True)


def toro(nombre, R, r, pos=(0, 0, 0), segs=64, segs_r=16, mat=None, parent=None):
    bm = bmesh.new()
    anillos = []
    for j in range(segs_r):
        t = 2 * math.pi * j / segs_r
        rr, zz = R + r * math.cos(t), r * math.sin(t)
        anillos.append([bm.verts.new((rr * math.cos(2 * math.pi * i / segs),
                                      rr * math.sin(2 * math.pi * i / segs), zz))
                        for i in range(segs)])
    for j in range(segs_r):
        a, b = anillos[j], anillos[(j + 1) % segs_r]
        for i in range(segs):
            k = (i + 1) % segs
            bm.faces.new((a[i], a[k], b[k], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.translate(bm, vec=pos, verts=bm.verts)
    return _malla_desde_bm(nombre, bm, mat, parent, suave=True)


def tubo_curva(nombre, puntos, radio, segs=24, res=16, mat=None, parent=None,
               suavizar=True, tapas=True):
    """Tubo a lo largo de una polilinea suavizada (curva Bezier con las
    tangentes automaticas) convertida a malla. Para grifos, tiradores
    curvos, cables y asas. `puntos`: lista de (x, y, z)."""
    cu = bpy.data.curves.new(nombre, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radio
    cu.bevel_resolution = max(2, segs // 4 - 1)
    cu.resolution_u = res
    cu.use_fill_caps = tapas
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(puntos) - 1)
    for bp, p in zip(sp.bezier_points, puntos):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO' if suavizar else 'VECTOR'
    ob = _curva_a_malla(nombre, cu)
    for pg in ob.data.polygons:
        pg.use_smooth = True
    _registrar(ob, mat, parent)
    uv_cubo(ob)
    return ob


def _curva_a_malla(nombre, cu):
    """Evalua una curva (o texto) con su bisel/extrusion y devuelve un
    objeto malla nuevo, sin depender de operadores de interfaz."""
    tmp = bpy.data.objects.new(nombre + ' tmp', cu)
    bpy.context.scene.collection.objects.link(tmp)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg), depsgraph=dg)
    me.name = nombre
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.curves.remove(cu)
    return bpy.data.objects.new(nombre, me)


def prisma_yz(nombre, pts_yz, x0, x1, mat=None, parent=None, r=0.0, segs=3, suave=False):
    """Poligono en el plano Y-Z (lista de (y, z), antihorario visto desde
    +X) extruido en X de x0 a x1. Para cabezales con panel inclinado,
    petos en cuna, perfiles de campana..."""
    bm = bmesh.new()
    vs = [bm.verts.new((x0, y, z)) for y, z in pts_yz]
    f = bm.faces.new(vs)
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    top = [g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(x1 - x0, 0, 0), verts=top)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if r > 0:
        bm.edges.ensure_lookup_table()
        _bevel_bm(bm, list(bm.edges), r, segs)
    return _malla_desde_bm(nombre, bm, mat, parent, suave=suave or r > 0)


def girar_malla(ob, pivote, eje, grados):
    """Gira la malla (los vertices, no el objeto) alrededor de `pivote`
    (punto) y del eje 'X', 'Y' o 'Z'. Para inclinar paneles, mandos sobre
    caras inclinadas, asas..."""
    from mathutils import Matrix
    M = Matrix.Rotation(math.radians(grados), 4, eje)
    pv = Vector(pivote)
    me = ob.data
    for v in me.vertices:
        v.co = (M @ (v.co - pv)) + pv
    me.update()
    return ob


def mat_chapa_perforada(nombre='Chapa perforada', d=0.003, paso=0.005, base=None):
    """Inox con agujeros al tresbolillo hechos con alfa (Voronoi en UV):
    para cestos, bandejas y filtros. d: diametro del agujero, paso:
    distancia entre centros (las UV van en metros)."""
    if nombre in _MATS and _MATS[nombre].name in bpy.data.materials:
        return _MATS[nombre]
    if base is not None:
        # copia del material base (p. ej. mat_inox_satinado()) con los agujeros encima
        m = base.copy()
        m.name = nombre
        _MATS[nombre] = m
    else:
        m = mat_inox(nombre, rug=0.22, aniso=0.4, rayado=0.02, huellas=0.03,
                     color=(0.56, 0.565, 0.575))
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tc = next(n for n in nt.nodes if n.type == 'TEX_COORD')
    vor = nt.nodes.new('ShaderNodeTexVoronoi')
    vor.location = (-800, -600)
    vor.voronoi_dimensions = '2D'
    vor.feature = 'F1'
    vor.distance = 'EUCLIDEAN'
    vor.inputs['Scale'].default_value = 1.0 / paso
    vor.inputs['Randomness'].default_value = 0.0
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.location = (-1000, -600)
    # tresbolillo: se inclina la rejilla 30 grados
    mp.inputs['Rotation'].default_value = (0, 0, math.radians(30))
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], vor.inputs['Vector'])
    # distancia F1 va de 0 (centro) a ~0.5*paso*escala; agujero si < d/2
    mth = nt.nodes.new('ShaderNodeMath')
    mth.location = (-500, -600)
    mth.operation = 'GREATER_THAN'
    mth.inputs[1].default_value = (d / 2) / paso
    nt.links.new(vor.outputs['Distance'], mth.inputs[0])
    nt.links.new(mth.outputs['Value'], bsdf.inputs['Alpha'])
    m.blend_method = 'CLIP'
    try:
        m.surface_render_method = 'DITHERED'
    except Exception:
        pass
    return m


def plano(nombre, w, h, pos=(0, 0, 0), normal='-Y', mat=None, parent=None, rot=None):
    """Plano de w x h con su normal hacia `normal`: '-Y' (frente), '+Y',
    '+X', '-X', '+Z', '-Z'. `pos` = centro del plano. Para calcas.
    rot: (eje, grados) de giro adicional sobre el centro del plano, para
    calcas en caras inclinadas."""
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in ((-w / 2, -h / 2, 0), (w / 2, -h / 2, 0),
                                     (w / 2, h / 2, 0), (-w / 2, h / 2, 0))]
    bm.faces.new(vs)
    m = {'+Z': None, '-Z': _rot('X', 180), '-Y': _rot('X', 90), '+Y': _rot('X', -90),
         '+X': _rot('Y', 90), '-X': _rot('Y', -90)}[normal]
    if m is not None:
        bmesh.ops.rotate(bm, cent=(0, 0, 0), verts=bm.verts, matrix=m)
    if rot is not None:
        bmesh.ops.rotate(bm, cent=(0, 0, 0), verts=bm.verts, matrix=_rot(rot[0], rot[1]))
    bmesh.ops.translate(bm, vec=pos, verts=bm.verts)
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    uvl = me.uv_layers.new(name='UVMap')
    for li, uvc in zip(range(4), ((0, 0), (1, 0), (1, 1), (0, 1))):
        uvl.data[li].uv = uvc
    ob = bpy.data.objects.new(nombre, me)
    return _registrar(ob, mat, parent)


def sustraer(ob, cortador, borrar=True):
    """Booleana de diferencia (solver exacto) aplicada."""
    mod = ob.modifiers.new('bool', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cortador
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if borrar:
        bpy.data.objects.remove(cortador, do_unlink=True)
    uv_cubo(ob)
    normales_ponderadas(ob)
    return ob


def unir(nombre, objetos, mat=None):
    """Une varias mallas en una (join)."""
    with bpy.context.temp_override(object=objetos[0], active_object=objetos[0],
                                   selected_objects=objetos,
                                   selected_editable_objects=objetos):
        bpy.ops.object.join()
    ob = objetos[0]
    ob.name = nombre
    ob.data.name = nombre
    return ob


def texto(nombre, cadena, alto, pos=(0, 0, 0), normal='-Y', grosor=0.0005,
          mat=None, parent=None, alinear='CENTER', fuente=None, negrita=False):
    """Texto en relieve convertido a malla. `alto` = altura de mayusculas
    aproximada en m. Queda con su cara hacia `normal`."""
    cu = bpy.data.curves.new(nombre, 'FONT')
    cu.body = cadena
    cu.size = alto / 0.7
    cu.extrude = grosor / 2
    cu.align_x = alinear
    cu.align_y = 'CENTER'
    if fuente:
        try:
            cu.font = bpy.data.fonts.load(fuente)
        except Exception:
            pass
    ob = _curva_a_malla(nombre, cu)
    rot = {'-Y': (math.pi / 2, 0, 0), '+Y': (math.pi / 2, 0, math.pi),
           '+X': (math.pi / 2, 0, math.pi / 2), '-X': (math.pi / 2, 0, -math.pi / 2),
           '+Z': (0, 0, 0)}[normal]
    ob.rotation_euler = rot
    ob.location = pos
    return _registrar(ob, mat, parent)


# ============================================================ materiales
_MATS = {}


def _base(nombre):
    if nombre in _MATS and _MATS[nombre].name in bpy.data.materials:
        return None
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (600, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    _MATS[nombre] = m
    return m, nt, bsdf


def _ruido(nt, escala, detalle=2.0, rug=0.5, loc=(-600, 0), coords=None, mapping=None):
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.location = loc
    n.inputs['Scale'].default_value = escala
    n.inputs['Detail'].default_value = detalle
    n.inputs['Roughness'].default_value = rug
    if mapping is not None:
        nt.links.new(mapping.outputs['Vector'], n.inputs['Vector'])
    elif coords is not None:
        nt.links.new(coords, n.inputs['Vector'])
    return n


def mat_inox(nombre='INOX cepillado', rug=0.34, aniso=0.75, rayado=0.10,
             color=(0.500, 0.505, 0.515), direccion=0.0, huellas=0.06,
             escala_rayado=700.0):
    """Acero inoxidable cepillado: Principled metalico anisotropo con el
    rayado como bump direccional y huellas/manchas que varian la rugosidad.
    direccion: 0 = rayado a lo largo de U (horizontal en las caras
    verticales), 0.25 = a lo largo de V."""
    b = _base(nombre)
    if b is None:
        return _MATS[nombre]
    m, nt, bsdf = b
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = rug
    bsdf.inputs['Anisotropic'].default_value = aniso
    bsdf.inputs['Anisotropic Rotation'].default_value = direccion
    bsdf.inputs['Specular IOR Level'].default_value = 0.5
    tc = nt.nodes.new('ShaderNodeTexCoord')
    tc.location = (-1300, 0)
    tang = nt.nodes.new('ShaderNodeTangent')
    tang.location = (0, -400)
    tang.direction_type = 'UV_MAP'
    tang.uv_map = 'UVMap'
    nt.links.new(tang.outputs['Tangent'], bsdf.inputs['Tangent'])
    # rayado: ruido muy estirado a lo largo de U
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.location = (-1050, 200)
    mp.inputs['Scale'].default_value = (1.0, escala_rayado / 4.0, 1.0) if direccion == 0.0 \
        else (escala_rayado / 4.0, 1.0, 1.0)
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])
    ray = _ruido(nt, 4.0, detalle=3.0, rug=0.6, loc=(-800, 200), mapping=mp)
    bump = nt.nodes.new('ShaderNodeBump')
    bump.location = (0, -150)
    bump.inputs['Strength'].default_value = rayado
    bump.inputs['Distance'].default_value = 0.0008
    nt.links.new(ray.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    # huellas y manchas: rugosidad variable a escala de 10-20 cm
    hu = _ruido(nt, 18.0, detalle=4.0, rug=0.7, loc=(-800, -250), coords=tc.outputs['UV'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.location = (-500, -250)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (rug - huellas * 0.5,) * 3 + (1,)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (rug + huellas,) * 3 + (1,)
    nt.links.new(hu.outputs['Fac'], ramp.inputs['Fac'])
    # el rayado tambien modula un poco la rugosidad
    mix = nt.nodes.new('ShaderNodeMix')
    mix.location = (-200, -250)
    mix.data_type = 'FLOAT'
    mix.inputs['Factor'].default_value = 0.25
    nt.links.new(ramp.outputs['Color'], mix.inputs[2])
    nt.links.new(ray.outputs['Fac'], mix.inputs[3])
    nt.links.new(mix.outputs[0], bsdf.inputs['Roughness'])
    return m


def mat_inox_satinado(nombre='INOX satinado'):
    return mat_inox(nombre, rug=0.44, aniso=0.55, rayado=0.06, huellas=0.08,
                    escala_rayado=1400.0)


def mat_inox_pulido(nombre='INOX pulido'):
    return mat_inox(nombre, rug=0.12, aniso=0.25, rayado=0.006, huellas=0.02,
                    color=(0.58, 0.585, 0.595), escala_rayado=600.0)


def mat_cromo(nombre='Cromo', rug=0.07):
    b = _base(nombre)
    if b is None:
        return _MATS[nombre]
    m, nt, bsdf = b
    bsdf.inputs['Base Color'].default_value = (0.90, 0.90, 0.92, 1)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = rug
    return m


def mat_aluminio(nombre='Aluminio anodizado', rug=0.35, color=(0.70, 0.70, 0.71)):
    b = _base(nombre)
    if b is None:
        return _MATS[nombre]
    m, nt, bsdf = b
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = rug
    tc = nt.nodes.new('ShaderNodeTexCoord')
    n = _ruido(nt, 400.0, detalle=2.0, rug=0.5, loc=(-600, -200), coords=tc.outputs['Object'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.03
    bump.inputs['Distance'].default_value = 0.0005
    nt.links.new(n.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def mat_chapa(nombre, color, rug=0.38, brillo=0.25, piel=0.15):
    """Chapa lacada / pintura en polvo: dielectrico con capa de barniz y
    un poco de piel de naranja."""
    b = _base(nombre)
    if b is None:
        return _MATS[nombre]
    m, nt, bsdf = b
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = rug
    bsdf.inputs['Coat Weight'].default_value = brillo
    bsdf.inputs['Coat Roughness'].default_value = 0.12
    tc = nt.nodes.new('ShaderNodeTexCoord')
    n = _ruido(nt, 900.0, detalle=1.5, rug=0.5, loc=(-600, -200), coords=tc.outputs['Object'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = piel
    bump.inputs['Distance'].default_value = 0.0002
    nt.links.new(n.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def mat_plastico(nombre, color, rug=0.42, brillo=0.0):
    b = _base(nombre)
    if b is None:
        return _MATS[nombre]
    m, nt, bsdf = b
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = rug
    bsdf.inputs['Specular IOR Level'].default_value = 0.45
    bsdf.inputs['Coat Weight'].default_value = brillo
    tc = nt.nodes.new('ShaderNodeTexCoord')
    n = _ruido(nt, 1500.0, detalle=1.0, rug=0.5, loc=(-600, -200), coords=tc.outputs['Object'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.06
    bump.inputs['Distance'].default_value = 0.0001
    nt.links.new(n.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def mat_goma(nombre='Goma negra', color=(0.015, 0.015, 0.015)):
    return mat_plastico(nombre, color, rug=0.75)


def mat_vidrio(nombre='Vidrio', tinte=(0.94, 0.985, 0.965), rug=0.0):
    b = _base(nombre)
    if b is None:
        return _MATS[nombre]
    m, nt, bsdf = b
    bsdf.inputs['Base Color'].default_value = (*tinte, 1)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = rug
    bsdf.inputs['IOR'].default_value = 1.50
    bsdf.inputs['Transmission Weight'].default_value = 1.0
    # transparente para los rayos de sombra: lo que hay detras del vidrio
    # (calcas, esferas, interiores) recibe luz directa, como en un vidrio real
    salida = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    lp = nt.nodes.new('ShaderNodeLightPath')
    lp.location = (-200, 400)
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    tr.location = (0, 300)
    mx = nt.nodes.new('ShaderNodeMixShader')
    mx.location = (250, 200)
    nt.links.new(lp.outputs['Is Shadow Ray'], mx.inputs['Fac'])
    nt.links.new(bsdf.outputs['BSDF'], mx.inputs[1])
    nt.links.new(tr.outputs['BSDF'], mx.inputs[2])
    nt.links.new(mx.outputs['Shader'], salida.inputs['Surface'])
    return m


def mat_policarbonato(nombre='Policarbonato', tinte=(0.97, 0.97, 0.96)):
    return mat_vidrio(nombre, tinte, rug=0.04)


def mat_vitroceramica(nombre='Vitroceramica negra', color=(0.004, 0.004, 0.005), rug=0.03):
    """Vidrio negro brillante (vitroceramica, cristal de puerta de horno
    visto desde fuera): dielectrico oscuro muy liso, sin bump."""
    b = _base(nombre)
    if b is None:
        return _MATS[nombre]
    m, nt, bsdf = b
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = rug
    bsdf.inputs['IOR'].default_value = 1.52
    bsdf.inputs['Specular IOR Level'].default_value = 0.55
    return m


def mat_led(nombre, color=(1.0, 1.0, 1.0), fuerza=8.0):
    b = _base(nombre)
    if b is None:
        return _MATS[nombre]
    m, nt, bsdf = b
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Emission Color'].default_value = (*color, 1)
    bsdf.inputs['Emission Strength'].default_value = fuerza
    bsdf.inputs['Roughness'].default_value = 0.3
    return m


def mat_calca(nombre, ruta_png, fuerza_emision=0.0, rug=0.35):
    """Imagen PNG con alfa sobre un plano: serigrafia, pantallas, logos.
    La imagen se empaqueta en el .blend."""
    b = _base(nombre)
    if b is None:
        return _MATS[nombre]
    m, nt, bsdf = b
    m.blend_method = 'BLEND'
    img = bpy.data.images.load(ruta_png)
    img.pack()
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.location = (-400, 0)
    tex.image = img
    tex.interpolation = 'Cubic'
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])
    bsdf.inputs['Roughness'].default_value = rug
    bsdf.inputs['Specular IOR Level'].default_value = 0.3
    if fuerza_emision > 0:
        nt.links.new(tex.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = fuerza_emision
    return m


def calca(nombre, ruta_png, w, h, pos, normal='-Y', emision=0.0, parent=None, rot=None):
    """Plano con la imagen, separado 0,3 mm de la superficie (la separacion
    la pone quien llama en `pos`)."""
    return plano(nombre, w, h, pos, normal, mat_calca('Calca ' + nombre, ruta_png, emision), parent, rot=rot)


# ============================================================ calcas (PIL)
def png_texto(ruta, lineas, ancho_px, alto_px, color=(30, 30, 30), fondo=None,
              tam=None, fuente='DejaVuSans.ttf', margen=0.1):
    """Genera un PNG con alfa con una o varias lineas de texto centradas.
    `lineas`: str o lista de (texto, tamano_relativo, color) / str."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGBA', (ancho_px, alto_px), (0, 0, 0, 0) if fondo is None else (*fondo, 255))
    dr = ImageDraw.Draw(img)
    if isinstance(lineas, str):
        lineas = [lineas]
    n = len(lineas)
    y = alto_px * margen
    alto_util = alto_px * (1 - 2 * margen)
    for ln in lineas:
        if isinstance(ln, str):
            t, rel, col = ln, 1.0, color
        else:
            ln = list(ln)
            t = ln[0]
            rel = ln[1] if len(ln) > 1 else 1.0
            col = ln[2] if len(ln) > 2 else color
        size = int(tam * rel) if tam else int(alto_util / n * 0.72 * rel)
        try:
            f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + fuente, size)
        except Exception:
            f = ImageFont.load_default()
        bb = dr.textbbox((0, 0), t, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        dr.text(((ancho_px - tw) / 2 - bb[0], y + (alto_util / n - th) / 2 - bb[1]), t, font=f, fill=(*col, 255))
        y += alto_util / n
    img.save(ruta)
    return ruta


# ============================================================ control
def bbox_coleccion(col):
    xs, ys, zs = [], [], []
    for ob in col.all_objects:
        if ob.type != 'MESH':
            continue
        for c in ob.bound_box:
            p = ob.matrix_world @ Vector(c)
            xs.append(p.x)
            ys.append(p.y)
            zs.append(p.z)
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def comprobar_medidas(tag, medidas=None, tol=0.0015, ignorar=()):
    """Compara la caja envolvente con ancho x fondo x alto del plano.
    Falla si se desvia mas de `tol` (1,5 mm) o si el origen no esta en el
    centro de la huella con la base en z = 0. `ignorar`: nombres de mallas
    que sobresalen a proposito (cable, chimenea, mandos, tiradores) y no
    cuentan; vale el nombre exacto o el prefijo (`'mando'` excluye
    'mando faldon', 'mando indice'...)."""
    a, f, h = medidas or MEDIDAS[tag]
    col = bpy.data.collections[tag]
    xs, ys, zs = [], [], []
    ignorar = tuple(ignorar)
    for ob in col.all_objects:
        if ob.type != 'MESH' or ob.name.startswith('Calca'):
            continue
        if any(ob.name == i or ob.name.startswith(i + ' ') for i in ignorar):
            continue
        for c in ob.bound_box:
            p = ob.matrix_world @ Vector(c)
            xs.append(p.x)
            ys.append(p.y)
            zs.append(p.z)
    w, d, z = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    fallos = []
    for nm, v, esp in (('ancho', w, a), ('fondo', d, f), ('alto', z, h)):
        if abs(v - esp) > tol:
            fallos.append(f'{nm}: {v:.4f} (plano {esp:.3f}, desvio {1000 * (v - esp):+.1f} mm)')
    if abs(min(zs)) > tol:
        fallos.append(f'base en z = {min(zs):.4f}, no en 0')
    if abs(cx) > tol or abs(cy) > tol:
        fallos.append(f'origen descentrado: ({cx:.4f}, {cy:.4f})')
    n = sum(1 for ob in col.all_objects if ob.type == 'MESH')
    tri = sum(len(ob.data.polygons) for ob in col.all_objects if ob.type == 'MESH')
    print(f'[{tag}] {w:.4f} x {d:.4f} x {z:.4f}  (plano {a} x {f} x {h})  '
          f'{n} mallas, {tri} caras')
    if fallos:
        for x in fallos:
            print(f'   FALLO {x}')
        raise SystemExit(f'{tag}: medidas fuera de tolerancia')
    print(f'[{tag}] medidas OK (tolerancia {1000 * tol:.1f} mm), origen OK')
    return w, d, z


# ============================================================ plato y render
Z_TECHO_PLATO = 6.0


def plato(tam=30.0):
    """Ciclorama blanco, HDRI de estudio y luz principal suave."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new('Estudio')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes['Background']
    if os.path.exists(HDRI):
        env = nt.nodes.new('ShaderNodeTexEnvironment')
        env.image = bpy.data.images.load(HDRI)
        env.image.pack()
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Rotation'].default_value = (0, 0, math.radians(-60))
        tc = nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
        nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
        nt.links.new(env.outputs['Color'], bg.inputs['Color'])
        bg.inputs['Strength'].default_value = 0.9
    else:
        bg.inputs['Color'].default_value = (0.75, 0.75, 0.75, 1)
        bg.inputs['Strength'].default_value = 1.0
    col = bpy.data.collections.new('_plato')
    sc.collection.children.link(col)
    # ciclorama: suelo + pared trasera con curva
    m = bpy.data.materials.new('_ciclorama')
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.72, 0.72, 0.72, 1)
    b.inputs['Roughness'].default_value = 0.6
    bm = bmesh.new()
    perfil = [(-tam, 0)]
    R = 1.5
    for i in range(0, 13):
        t = math.radians(90 * i / 12)
        perfil.append((tam / 2 - R + R * math.sin(t), R - R * math.cos(t)))
    perfil.append((tam / 2, tam))
    vs_a = [bm.verts.new((-tam, y, z)) for y, z in perfil]
    vs_b = [bm.verts.new((tam, y, z)) for y, z in perfil]
    for i in range(len(perfil) - 1):
        bm.faces.new((vs_a[i], vs_b[i], vs_b[i + 1], vs_a[i + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('_ciclorama')
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new('_ciclorama', me)
    ob.data.materials.append(m)
    col.objects.link(ob)
    # techo blanco a 6 m: como una tienda de luz, para que el inox refleje
    # claro tambien dentro de cubas y cestos
    mt = bpy.data.materials.new('_techo')
    mt.use_nodes = True
    mt.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.92, 0.92, 0.92, 1)
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=tam)
    bmesh.ops.translate(bm, vec=(0, 0, Z_TECHO_PLATO), verts=bm.verts)
    me2 = bpy.data.meshes.new('_techo')
    bm.to_mesh(me2)
    bm.free()
    ob2 = bpy.data.objects.new('_techo', me2)
    ob2.data.materials.append(mt)
    col.objects.link(ob2)
    # luz principal: area grande, arriba a la izquierda y delante
    ld = bpy.data.lights.new('_key', 'AREA')
    ld.energy = 250.0
    ld.size = 2.5
    ld.shape = 'RECTANGLE'
    ld.size_y = 1.6
    lo = bpy.data.objects.new('_key', ld)
    lo.location = (-1.6, -2.6, 2.8)
    _apuntar(lo, (0, 0, 0.5))
    col.objects.link(lo)
    ld2 = bpy.data.lights.new('_fill', 'AREA')
    ld2.energy = 60.0
    ld2.size = 3.0
    lo2 = bpy.data.objects.new('_fill', ld2)
    lo2.location = (2.8, -2.0, 1.4)
    _apuntar(lo2, (0, 0, 0.5))
    col.objects.link(lo2)
    ld3 = bpy.data.lights.new('_rim', 'AREA')
    ld3.energy = 90.0
    ld3.size = 1.2
    lo3 = bpy.data.objects.new('_rim', ld3)
    lo3.location = (1.2, 2.6, 2.4)
    _apuntar(lo3, (0, 0, 0.6))
    col.objects.link(lo3)
    return col


def _apuntar(ob, punto):
    d = Vector(punto) - Vector(ob.location)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def _camara(nombre, lente=50.0):
    cd = bpy.data.cameras.new(nombre)
    cd.lens = lente
    cd.sensor_width = 36.0
    cd.clip_start = 0.01
    ob = bpy.data.objects.new(nombre, cd)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def encuadrar(cam, tag, azimut, elevacion, margen=1.22, lente=50.0, hacia=None,
              res=(4, 3)):
    """Coloca la camara mirando al centro de la caja envolvente desde
    azimut/elevacion (grados; azimut 0 = frente -Y, positivo hacia la
    derecha del espectador) y a la distancia justa para que quepa."""
    lo, hi = bbox_coleccion(bpy.data.collections[tag])
    c = Vector(((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2))
    if hacia is not None:
        c = Vector(hacia)
    esquinas = [Vector((x, y, z)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    R = max((e - c).length for e in esquinas)
    cam.data.lens = lente
    fov_h = 2 * math.atan(cam.data.sensor_width / 2 / lente)
    fov_v = 2 * math.atan(cam.data.sensor_width * res[1] / res[0] / 2 / lente)
    fov = min(fov_h, fov_v)
    dist = R * margen / math.sin(fov / 2)
    az, el = math.radians(azimut), math.radians(elevacion)
    dirv = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    pos = c + dirv * dist
    # la camara se queda dentro del plato: ni bajo el suelo ni sobre el techo
    z_min, z_max = 0.15, Z_TECHO_PLATO - 0.3
    if pos.z < z_min or pos.z > z_max:
        pos.z = min(max(pos.z, z_min), z_max)
        # se aleja en horizontal para conservar el encuadre
        horiz = Vector((dirv.x, dirv.y, 0.0))
        if horiz.length > 1e-6:
            horiz.normalize()
            dh = math.sqrt(max(dist ** 2 - (pos.z - c.z) ** 2, 0.0))
            pos = Vector((c.x + horiz.x * dh, c.y + horiz.y * dh, pos.z))
    cam.location = pos
    _apuntar(cam, c)
    return cam


def _ajustes_render(spp, res):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = spp
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = 'OPENIMAGEDENOISE'
        sc.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    except Exception:
        pass
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 6
    sc.cycles.transmission_bounces = 8
    sc.cycles.transparent_max_bounces = 12
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 0.5
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.image_settings.compression = 60
    sc.view_settings.view_transform = 'AgX'
    try:
        sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    sc.view_settings.exposure = 0.0


VISTAS = [('34', -35, 20), ('frente', 0, 6), ('lateral', 90, 8), ('trasera', 150, 22)]


def render_vistas(tag, spp=160, res=(1000, 750), vistas=VISTAS, lente=50.0,
                  salida=None):
    """Renderiza las vistas de control y compone la hoja preview/<TAG>.png."""
    import time
    from PIL import Image, ImageDraw, ImageFont
    salida = salida or PREVIEW_DIR
    _ajustes_render(spp, res)
    sc = bpy.context.scene
    cam = _camara('_cam', lente)
    sc.camera = cam
    rutas = []
    ciclo = bpy.data.objects.get('_ciclorama')
    for nm, az, el in vistas:
        encuadrar(cam, tag, az, el, lente=lente, res=res)
        if ciclo is not None:
            # el ciclorama gira con la camara: la pared siempre queda detras
            ciclo.rotation_euler = (0, 0, math.radians(az))
        ruta = os.path.join(SCRATCH, f'_v_{tag}_{nm}.png')
        sc.render.filepath = ruta
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print(f'   vista {nm}: {time.time() - t:.0f} s')
        rutas.append((nm, ruta))
    # hoja 2 x 2
    W, H = res
    hoja = Image.new('RGB', (2 * W + 30, 2 * H + 30 + 60), (245, 245, 245))
    dr = ImageDraw.Draw(hoja)
    try:
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
        f2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
    except Exception:
        f = f2 = ImageFont.load_default()
    a, fo, h = MEDIDAS.get(tag, (0, 0, 0))
    fi = FICHAS.get(tag, {}).get('nombre', tag)
    dr.text((20, 14), f'{tag} · {fi}', font=f, fill=(20, 20, 20))
    dr.text((20, 48), f'{a:.3f} x {fo:.3f} x {h:.3f} m (ancho x fondo x alto) · escala 1:1', font=f2, fill=(80, 80, 80))
    for i, (nm, ruta) in enumerate(rutas):
        im = Image.open(ruta).convert('RGB')
        x = 10 + (i % 2) * (W + 10)
        y = 70 + (i // 2) * (H + 10)
        hoja.paste(im, (x, y))
        dr.text((x + 12, y + 8), nm, font=f2, fill=(30, 30, 30))
    out = os.path.join(salida, f'{tag}.png')
    hoja.save(out, optimize=True)
    Image.open(rutas[0][1]).convert('RGB').save(os.path.join(salida, f'{tag}_34.png'), optimize=True)
    for _, r in rutas:
        os.remove(r)
    # la camara y el plato no viajan en el .blend del objeto
    bpy.data.objects.remove(cam, do_unlink=True)
    print(f'   hoja: {out}')
    return out


def guardar(tag):
    """Quita el plato, empaqueta y guarda blend/<TAG>.blend."""
    if '_plato' in bpy.data.collections:
        col = bpy.data.collections['_plato']
        for ob in list(col.all_objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(col)
    for ob in list(bpy.data.objects):
        if ob.name.startswith('_cam'):
            bpy.data.objects.remove(ob, do_unlink=True)
    for w in list(bpy.data.worlds):
        bpy.data.worlds.remove(w)
    for im in list(bpy.data.images):
        if im.filepath and im.filepath.endswith('.hdr'):
            bpy.data.images.remove(im)
    for m in list(bpy.data.materials):
        if m.name.startswith('_'):
            bpy.data.materials.remove(m)
    bpy.ops.file.pack_all()
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    ruta = os.path.join(BLEND_DIR, f'{tag}.blend')
    bpy.ops.wm.save_as_mainfile(filepath=ruta, compress=True)
    print(f'[{tag}] guardado {ruta} ({os.path.getsize(ruta) / 1e6:.1f} MB)')
    return ruta


def finalizar(tag, medidas=None, ignorar=(), spp=160, res=(1000, 750), vistas=VISTAS,
              lente=50.0, render=True, altura=0.0):
    """Control de medidas, plato, render de vistas y guardado. `altura`:
    a que cota se cuelga el objeto en el plato para las vistas (campanas,
    estantes murales: se ven desde abajo); se deshace antes de guardar."""
    comprobar_medidas(tag, medidas, ignorar=ignorar)
    if render:
        plato()
        raiz_ob = bpy.data.objects.get(tag)
        if altura and raiz_ob is not None:
            raiz_ob.location.z = altura
            bpy.context.view_layer.update()
        render_vistas(tag, spp=spp, res=res, vistas=vistas, lente=lente)
        if altura and raiz_ob is not None:
            raiz_ob.location.z = 0.0
            bpy.context.view_layer.update()
    return guardar(tag)
