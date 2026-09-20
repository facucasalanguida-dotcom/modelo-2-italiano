# -*- coding: utf-8 -*-
"""
CASA MARGOT — escena completa para Cycles.

Toda la geometria de obra sale de docs/planos/MODELO_3D.json, que genera
export_sketchup.py desde estructura.py, mobiliario.py y equipamiento.py: las
mismas fuentes que dibujan las laminas. Encima van, con geometria fina:

  · los 24 aparatos de docs/objetos (biblioteca 1:1 verificada),
  · el mobiliario de sala parametrico (mesas, sillas, taburetes, sillon),
  · la planta alta, con el mismo lenguaje que la baja,
  · la pared azzurro con el logo Casa Margot en vinilo de plotter,
  · la decoracion de trattoria.

    python3 escena.py --vista barra --spp 1500 --ancho 3840
    python3 escena.py --todas
"""
import argparse
import json
import math
import os
import random
import sys

import bpy
import bmesh
from mathutils import Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(AQUI, '..', '..', '..'))
PLANOS = os.path.join(REPO, 'docs', 'planos')
OBJETOS = os.path.join(REPO, 'docs', 'objetos')
sys.path.insert(0, PLANOS)
sys.path.insert(0, AQUI)

import estructura as E          # noqa: E402
import mobiliario as MB         # noqa: E402
import equipamiento as Q        # noqa: E402
import materiales as MT         # noqa: E402

SCRATCH = os.environ.get('CM_SCRATCH', '/tmp/claude-0/-home-user-modelo-2-italiano/'
                                       '30d2763c-3169-519a-ac78-c5a47134634b/scratchpad')
PH = os.path.join(SCRATCH, 'ph')
LOGO = os.path.join(SCRATCH, 'logo', 'casa_margot_recortado.png')

random.seed(11)

# ---- cotas que la escena necesita y el plano no fija (mismas que el .rb)
Z_SOFITO = 2.310                 # intrados del forjado del altillo
Z_PA = E.H_PA                    # 2,560 suelo de planta alta
Z_TECHO = E.H_PA + E.H_LIBRE_PA  # 5,060 techo del altillo
H_MESA = 0.750
E_TABLERO = 0.040
SOLAPE = 0.004                   # los acabados se meten en su soporte:
                                 # dos caras coincidentes dan z-fighting
SEPARACION_MURO = 0.030          # los aparatos no van a hueso con la pared:
                                 # sus conexiones traseras necesitan sitio

MAT = {}
COL = {}


# =========================================================== utiles de escena
def coleccion(nombre):
    if nombre not in COL:
        c = bpy.data.collections.new(nombre)
        bpy.context.scene.collection.children.link(c)
        COL[nombre] = c
    return COL[nombre]


def _malla(nombre, verts, faces, mat, col, suave=False):
    me = bpy.data.meshes.new(nombre)
    me.from_pydata(verts, [], faces)
    me.validate()
    if mat is not None:
        me.materials.append(mat)
    if suave:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(nombre, me)
    coleccion(col).objects.link(ob)
    return ob


def caja(nombre, x0, y0, x1, y1, z0, z1, mat, col='Obra'):
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    if z1 < z0:
        z0, z1 = z1, z0
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
         (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return _malla(nombre, v, f, mat, col)


def prisma(nombre, pts, z0, z1, mat, col='Obra'):
    """Poligono en planta extruido en Z."""
    n = len(pts)
    v = [(p[0], p[1], z0) for p in pts] + [(p[0], p[1], z1) for p in pts]
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    f += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    return _malla(nombre, v, f, mat, col)


def panel(nombre, pts_yz, x0, x1, mat, col='Obra'):
    """Poligono en el plano YZ extruido en X."""
    n = len(pts_yz)
    v = [(x0, p[0], p[1]) for p in pts_yz] + [(x1, p[0], p[1]) for p in pts_yz]
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    f += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    return _malla(nombre, v, f, mat, col)


def cilindro(nombre, cx, cy, r, z0, z1, mat, col='Obra', segs=48):
    pts = [(cx + r * math.cos(2 * math.pi * i / segs),
            cy + r * math.sin(2 * math.pi * i / segs)) for i in range(segs)]
    ob = prisma(nombre, pts, z0, z1, mat, col)
    for p in ob.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return ob


def bisel(ob, ancho=0.0022, segs=2, angulo=50.0):
    """Un bisel pequeno en todas las aristas: sin el, nada parece real."""
    md = ob.modifiers.new('bisel', 'BEVEL')
    md.width = ancho
    md.segments = segs
    md.limit_method = 'ANGLE'
    md.angle_limit = math.radians(angulo)
    md.harden_normals = False
    return ob


def girar(ob, centro, grados, eje='Z'):
    import mathutils
    c = Vector(centro)
    R = mathutils.Matrix.Rotation(math.radians(grados), 4, eje)
    for v in ob.data.vertices:
        v.co = R @ (v.co - c) + c
    return ob


# =============================================== 1. escena limpia y ajustes
def escena_nueva(spp=512, ancho=2560, alto=1440):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # los datablocks de imagen mueren con el fichero: si no se vacian los
    # caches, el segundo montaje apunta a imagenes que ya no existen
    MT._img_cache.clear()
    MT._map_cache.clear()
    _importados.clear()
    COL.clear()
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = spp
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.006
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = 'OPENIMAGEDENOISE'
        sc.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    except Exception:
        pass
    sc.cycles.max_bounces = 12
    sc.cycles.diffuse_bounces = 6
    sc.cycles.glossy_bounces = 6
    sc.cycles.transmission_bounces = 12
    sc.cycles.transparent_max_bounces = 16
    sc.cycles.sample_clamp_indirect = 10.0
    sc.cycles.blur_glossy = 0.6
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.render.resolution_x = ancho
    sc.render.resolution_y = alto
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    try:
        sc.cycles.filter_width = 1.6
    except Exception:
        pass
    sc.view_settings.view_transform = 'AgX'
    try:
        sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    sc.view_settings.exposure = 0.65
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_depth = '16'
    return sc


# ================================================== 2. arquitectura del plano
# lo que el plano dibuja en bruto y aqui se sustituye por geometria fina
TAGS_BIBLIOTECA = set(('A1 A2 A3 A4 A5 A6 A7 B1 B2 B3 B4 K1 K2 K3 K4 K5 K6 K7 K8 K9 '
                       'K10 KC V1 V2').split())


def _tag_de(nombre):
    t = (nombre or '').split(' · ')[0].strip()
    return t if t in TAGS_BIBLIOTECA else None


def sustituido(s):
    """True si ese solido del plano lo rehace la escena con mas detalle."""
    nm = s['nombre'] or ''
    if _tag_de(nm):
        return True                       # aparato de la biblioteca
    if s['mat'] in ('mesa', 'silla'):
        return True                       # mobiliario parametrico
    if s['mat'] == 'luz':
        return True                       # luminarias parametricas
    if nm.startswith('Frente de la barra'):
        return True                       # se rehace en listones azzurro
    if nm.startswith('Pilar ') and 'P3' in nm:
        return True                       # se forra de listones
    return False


def arquitectura():
    """Muros, forjado, escalera, carpinteria y mobiliario fijo del plano."""
    j = json.load(open(os.path.join(PLANOS, 'MODELO_3D.json'), encoding='utf-8'))
    n = 0
    for s in j['cajas']:
        if sustituido(s):
            continue
        m = MAT.get(s['mat'])
        col = 'Planta alta' if s['tag'].startswith('14') else 'Obra'
        ob = caja(s['nombre'], s['x0'], s['y0'], s['x1'], s['y1'], s['z0'], s['z1'], m, col)
        if s['mat'] not in ('vidrio',):
            bisel(ob)
        n += 1
    for s in j['prismas']:
        if sustituido(s):
            continue
        ob = prisma(s['nombre'], s['pts'], s['z0'], s['z1'], MAT.get(s['mat']))
        bisel(ob)
        n += 1
    for s in j['cilindros']:
        if sustituido(s):
            continue
        cilindro(s['nombre'], s['cx'], s['cy'], s['r'], s['z0'], s['z1'], MAT.get(s['mat']))
        n += 1
    for s in j['paneles']:
        if sustituido(s):
            continue
        ob = panel(s['nombre'], s['pts_yz'], s['x0'], s['x1'], MAT.get(s['mat']))
        bisel(ob)
        n += 1
    return n, j


# ------------------------------------------------- suelos, techos y remates
def suelos_y_techos():
    """El plano no dibuja pavimento ni techo: aqui si, que es lo que se ve."""
    # pavimento de planta baja: roble, en toda la huella util
    caja('Pavimento planta baja', 0.200, 0.330, 9.940, 9.060, -0.018, 0.001,
         MAT['_suelo'], 'Obra')
    # El techo de planta baja NO se dibuja: donde hay altillo, el techo es el
    # intrados del propio forjado (el plano ya lo trae), y donde no lo hay el
    # local es de doble altura hasta el techo del altillo. Ponerlo plano a
    # 2,31 en todo el local cerraba la doble altura y dejaba el local a oscuras.
    # pavimento del altillo, sobre el forjado
    caja('Pavimento planta alta', 2.411, 3.939, 9.890, 8.957, Z_PA - 0.018,
         Z_PA + 0.001, MAT['_suelo'], 'Planta alta')


def listones(nombre, x0, y0, x1, y1, z0, z1, mat, ancho=0.028, hueco=0.016,
             fondo=0.022, eje='x', col='Obra'):
    """Celosia de listones verticales: el lenguaje de la casa.

    Va en el frente de la barra, en el forro del pilar y en los antepechos.
    """
    paso = ancho + hueco
    obs = []
    if eje == 'x':
        n = max(1, int(round((x1 - x0) / paso)))
        paso = (x1 - x0) / n
        for i in range(n):
            cx = x0 + paso * (i + 0.5)
            obs.append(caja(f'{nombre} {i + 1}', cx - ancho / 2, y0, cx + ancho / 2,
                            y0 + fondo, z0, z1, mat, col))
    else:
        n = max(1, int(round((y1 - y0) / paso)))
        paso = (y1 - y0) / n
        for i in range(n):
            cy = y0 + paso * (i + 0.5)
            obs.append(caja(f'{nombre} {i + 1}', x0, cy - ancho / 2, x0 + fondo,
                            cy + ancho / 2, z0, z1, mat, col))
    for o in obs:
        bisel(o, 0.0016)
    return obs


# ---------------------------------------- frente de la barra y forro del pilar
def frente_barra():
    """El mostrador, en listones verticales azzurro Napoli.

    Es el elemento que fija el caracter del local: los mismos listones de la
    referencia, pero en el azul del Napoli en vez del azul apagado anterior.
    Abajo queda el retranqueo de 50 mm con la tira de LED.
    """
    mx0, mx1 = Q.MOSTRADOR_X
    my0, my1 = Q.MOSTRADOR_Y
    z0, z1 = 0.050, Q.H_ENCIMERA
    # fondo oscuro para que los huecos entre listones no se vean como agujeros
    caja('Frente de la barra · fondo', mx1 - 0.030, my0, mx1 - 0.020, my1, 0.0, z1,
         MAT['_negro'])
    listones('Frente de la barra · liston', mx1 - 0.022, my0, mx1, my1, z0, z1,
             MAT['_liston_azul'], ancho=0.034, hueco=0.014, fondo=0.022, eje='y')
    # zocalo retranqueado y tira de LED que lame el suelo
    caja('Frente de la barra · zocalo', mx1 - 0.050, my0, mx1 - 0.022, my1, 0.0, z0,
         MAT['_negro'])
    led = caja('Frente de la barra · LED', mx1 - 0.046, my0 + 0.01, mx1 - 0.030,
               my1 - 0.01, 0.030, 0.042, MAT['_luz_calida'])
    led.visible_shadow = False
    # canto superior de madera sobre los listones
    caja('Frente de la barra · canto', mx1 - 0.055, my0, mx1 + 0.012, my1,
         z1, z1 + 0.042, MAT['mesa'])
    # La misma banda azzurro en el canto del forjado, que es donde va en la
    # referencia: cuelga 0,30 por debajo del intrados y llega al suelo del
    # altillo. Dos tramos, el del vacio Sur y el que da a la cocina.
    caja('Banda de rotulo Sur', 2.405, 3.917, 9.890, 3.945,
         Z_SOFITO - 0.12, Z_PA - 0.001, MAT['_pared_napoli'])
    caja('Banda de rotulo Oeste', 2.389, 3.945, 2.417, 8.957,
         Z_SOFITO - 0.34, Z_PA - 0.001, MAT['_pared_napoli'])


def cocina_inox():
    """La cocina, forrada de acero inoxidable.

    Es lo que pide el cliente y lo que exige sanidad: chapa de inox del
    rodapie al techo en los dos paramentos de trabajo (medianera Norte y muro
    Oeste), con la junta horizontal a la altura de los aparatos colgados.
    """
    c = Q.COCINA
    x0, x1 = c['x0'], c['x1']
    y0, y1 = c['y0'], Q.NICHO['y1']
    z1 = 2.150
    e = 0.008
    # paramento Norte (detras de la linea de coccion, dentro del hundimiento)
    caja('Cocina · chapa Norte', x0, y1 - e, x1, y1 + SOLAPE, 0.0, z1, MAT['inox'], 'Obra')
    # paramento Oeste (detras del fregadero y los hornos)
    caja('Cocina · chapa Oeste', x0 - SOLAPE, y0, x0 + e, y1, 0.0, z1, MAT['inox'], 'Obra')
    # pared en L por su cara de cocina, hasta la altura de la mesada
    caja('Cocina · chapa Este', x1 - e, y0, x1 + SOLAPE, y1, 0.0, 1.500, MAT['inox'], 'Obra')
    # junta horizontal: dos perfiles que rompen el paño y dan una linea de luz
    for zz in (1.500, 2.150):
        caja(f'Cocina · junta {zz:.2f} N', x0, y1 - 0.014, x1, y1 - e,
             zz - 0.006, zz, MAT['inox'], 'Obra')
    # barra portautensilios sobre la bancada, como en la referencia
    cilindro('Cocina · barra utensilios', 0, 0, 0.001, 0, 0.001, MAT['inox'], 'Obra', 4)
    bpy.data.objects.remove(bpy.data.objects['Cocina · barra utensilios'], do_unlink=True)
    yb = y1 - 0.060
    caja('Cocina · riel', x0 + 0.35, yb - 0.012, x0 + 1.75, yb + 0.012,
         1.480, 1.504, MAT['inox'], 'Obra')
    for i in range(6):
        x = x0 + 0.45 + i * 0.24
        caja(f'Cocina · gancho {i + 1}', x - 0.004, yb - 0.004, x + 0.004, yb + 0.004,
             1.400, 1.492, MAT['inox'], 'Obra')
        # cazo o utensilio colgado
        if i % 2 == 0:
            cilindro(f'Cocina · cazo {i + 1}', x, yb, 0.075, 1.250, 1.395,
                     MAT['inox'], 'Obra', 28)
        else:
            caja(f'Cocina · pala {i + 1}', x - 0.035, yb - 0.006, x + 0.035,
                 yb + 0.006, 1.230, 1.395, MAT['inox'], 'Obra')


def forro_pilar():
    """P3, el pilar exento de la sala, forrado de listones en sus cuatro caras."""
    x0, y0, x1, y1 = 5.670, 4.688, 6.320, 5.758
    d = 0.026 + SOLAPE
    listones('Forro P3 Sur', x0, y0 - d + SOLAPE, x1, y0, 0.0, Z_SOFITO,
             MAT['_liston'], fondo=d, eje='x')
    listones('Forro P3 Norte', x0, y1 - SOLAPE, x1, y1 + d, 0.0, Z_SOFITO,
             MAT['_liston'], fondo=d, eje='x')
    listones('Forro P3 Oeste', x0 - d + SOLAPE, y0, x0, y1, 0.0, Z_SOFITO,
             MAT['_liston'], fondo=d, eje='y')
    listones('Forro P3 Este', x1 - SOLAPE, y0, x1 + d, y1, 0.0, Z_SOFITO,
             MAT['_liston'], fondo=d, eje='y')


# ================================================ 3. los 24 aparatos 1:1
# Como esta puesto cada aparato en el local: giro sobre Z y contra que cara
# apoya. La biblioteca construye todo con el frente hacia -Y.
#   0    frente al Sur (linea de coccion, contra el muro Norte)
#   90   frente al Este (muro Oeste: trasbarra y linea de cocina)
#  -90   frente al Oeste (pared en L y frente de barra visto desde la sala)
GIRO = {
    'K1': 0, 'K2': 0, 'K3': 0, 'K4': 0, 'KC': 0,          # bancada de coccion
    'K5': 90, 'K6': 90, 'K7': 90, 'K8': 90, 'K9': 90,     # muro Oeste de cocina
    'K10': -90,                                           # pared en L
    'A1': 90, 'A2': 90, 'A3': 90, 'A4': 90, 'A5': 90, 'A6': 90,   # trasbarra
    'A7': 0,                                              # cara Sur de P3
    'V1': -90, 'V2': -90, 'B1': 90, 'B3': -90, 'B4': -90, 'B2': 0,
}


def _hueco_del_plano(j):
    """Caja que el plano reserva a cada aparato, por su etiqueta."""
    out = {}
    for s in j['cajas'] + j['cilindros']:
        t = _tag_de(s['nombre'])
        if not t:
            continue
        if 'cx' in s:
            b = (s['cx'] - s['r'], s['cy'] - s['r'], s['z0'],
                 s['cx'] + s['r'], s['cy'] + s['r'], s['z1'])
        else:
            b = (s['x0'], s['y0'], s['z0'], s['x1'], s['y1'], s['z1'])
        if t in out:
            o = out[t]
            b = (min(o[0], b[0]), min(o[1], b[1]), min(o[2], b[2]),
                 max(o[3], b[3]), max(o[4], b[4]), max(o[5], b[5]))
        out[t] = b
    return out


def aparatos(j):
    """Trae los 24 .blend de la biblioteca y los planta en su hueco."""
    huecos = _hueco_del_plano(j)
    col = coleccion('Aparatos')
    puestos = []
    for tag in sorted(TAGS_BIBLIOTECA):
        ruta = os.path.join(OBJETOS, 'blend', f'{tag}.blend')
        if not os.path.exists(ruta) or tag not in huecos:
            print(f'   (falta {tag})')
            continue
        antes = set(bpy.data.objects.keys())
        with bpy.data.libraries.load(ruta, link=False) as (src, dst):
            dst.collections = [tag] if tag in src.collections else []
        traidos = [o for o in bpy.data.objects if o.name not in antes]
        mallas = [o for o in traidos if o.type == 'MESH']
        if not mallas:
            continue
        # la coleccion viene con su Empty raiz: se cuelga todo de la escena
        for o in traidos:
            if o.users_collection:
                for c in list(o.users_collection):
                    c.objects.unlink(o)
            col.objects.link(o)
        raiz = next((o for o in traidos if o.type == 'EMPTY' and o.name.split('.')[0] == tag), None)
        # caja real del objeto (en su sistema: frente a -Y, base en z=0)
        lo = Vector((1e9,) * 3)
        hi = Vector((-1e9,) * 3)
        for o in mallas:
            for c in o.bound_box:
                w = o.matrix_world @ Vector(c)
                for i in range(3):
                    lo[i] = min(lo[i], w[i])
                    hi[i] = max(hi[i], w[i])
        g = GIRO.get(tag, 0)
        x0, y0, z0, x1, y1, z1 = huecos[tag]
        # centro del hueco en planta y base a la cota del plano
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        # separacion del muro: el objeto se retira hacia su frente
        s = SEPARACION_MURO
        if g == 90:
            cx += s
        elif g == -90:
            cx -= s
        elif g == 0:
            cy -= s
        raiz_ob = raiz if raiz is not None else mallas[0]
        padres = [o for o in traidos if o.parent is None]
        import mathutils
        M = (mathutils.Matrix.Translation((cx, cy, z0))
             @ mathutils.Matrix.Rotation(math.radians(g), 4, 'Z'))
        for o in padres:
            o.matrix_world = M @ o.matrix_world
        puestos.append(tag)
    return puestos


# ==================================================== 4. mobiliario de sala
def blando(ob, radio=0.018, segs=4, sub=1):
    """Cojin: bisel gordo y una subdivision. Lo que separa un cubo de un asiento."""
    md = ob.modifiers.new('cojin', 'BEVEL')
    md.width = radio
    md.segments = segs
    md.limit_method = 'ANGLE'
    md.angle_limit = math.radians(60)
    if sub:
        sm = ob.modifiers.new('suave', 'SUBSURF')
        sm.levels = sm.render_levels = sub
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def pata_conica(nombre, cx, cy, z0, z1, r0, r1, mat, col, segs=14, inclinacion=(0, 0)):
    v, f = [], []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        v.append((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0))
    for i in range(segs):
        a = 2 * math.pi * i / segs
        v.append((cx + inclinacion[0] + r1 * math.cos(a),
                  cy + inclinacion[1] + r1 * math.sin(a), z1))
    f.append(tuple(range(segs - 1, -1, -1)))
    f.append(tuple(range(segs, 2 * segs)))
    for i in range(segs):
        f.append((i, (i + 1) % segs, (i + 1) % segs + segs, i + segs))
    ob = _malla(nombre, v, f, mat, col)
    for p in ob.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return ob


def silla(nombre, cx, cy, ang, tela, col='Mobiliario'):
    """Silla de concha tapizada sobre cuatro patas de madera.

    Es la de las referencias: asiento y respaldo envolvente en boucle crema,
    patas conicas de roble claro.
    """
    A, F = 0.430, 0.440                 # ancho y fondo del asiento
    Z_AS, E_AS = 0.450, 0.075
    obs = []
    asiento = caja(f'{nombre} asiento', cx - A / 2, cy - F / 2, cx + A / 2, cy + F / 2,
                   Z_AS - E_AS, Z_AS, tela, col)
    obs.append(blando(asiento, 0.026, 4, 1))
    # respaldo envolvente: arco de sectores que abraza el asiento
    R, ab = 0.300, math.radians(122)
    n = 13
    for i in range(n):
        t = -ab / 2 + ab * i / (n - 1)
        px = cx + R * math.sin(t)
        py = cy + F / 2 - R * 0.42 + R * math.cos(t) * 0.52
        h = 0.330 - 0.085 * abs(t / (ab / 2)) ** 1.7
        seg = caja(f'{nombre} respaldo {i + 1}', px - 0.030, py - 0.030, px + 0.030,
                   py + 0.030, Z_AS - 0.030, Z_AS + h, tela, col)
        girar(seg, (px, py, 0), math.degrees(t))
        obs.append(blando(seg, 0.022, 3, 1))
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        px, py = cx + sx * (A / 2 - 0.055), cy + sy * (F / 2 - 0.055)
        obs.append(pata_conica(f'{nombre} pata {sx}{sy}', px, py, 0.0, Z_AS - E_AS + 0.01,
                               0.0115, 0.017, MAT['silla'], col,
                               inclinacion=(-sx * 0.022, -sy * 0.022)))
    for o in obs:
        girar(o, (cx, cy, 0), ang)
    return obs


def mesa(nombre, cx, cy, w, d, redonda=False, col='Mobiliario'):
    """Tablero de roble sobre pie central negro de disco, como en las fotos."""
    obs = []
    if redonda:
        tab = cilindro(f'{nombre} tablero', cx, cy, w / 2, H_MESA - E_TABLERO, H_MESA,
                       MAT['mesa'], col, segs=72)
    else:
        tab = caja(f'{nombre} tablero', cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2,
                   H_MESA - E_TABLERO, H_MESA, MAT['mesa'], col)
    bisel(tab, 0.004, 3)
    obs.append(tab)
    rb = 0.230 if max(w, d) < 1.0 else 0.300
    base = cilindro(f'{nombre} base', cx, cy, rb, 0.0, 0.016, MAT['carp'], col, segs=56)
    bisel(base, 0.003, 3)
    obs.append(base)
    obs.append(pata_conica(f'{nombre} fuste', cx, cy, 0.014, H_MESA - E_TABLERO,
                           0.036, 0.030, MAT['carp'], col, segs=28))
    if w > 1.6:            # mesa larga: dos pies
        for s in (-1, 1):
            px = cx + s * (w / 2 - 0.45)
            obs.append(cilindro(f'{nombre} base {s}', px, cy, 0.260, 0.0, 0.016,
                                MAT['carp'], col, segs=56))
            obs.append(pata_conica(f'{nombre} fuste {s}', px, cy, 0.014,
                                   H_MESA - E_TABLERO, 0.036, 0.030, MAT['carp'], col, 28))
        for o in (obs[1], obs[2]):
            bpy.data.objects.remove(o, do_unlink=True)
        obs = [obs[0]] + obs[3:]
    return obs


def taburete(nombre, cx, cy, z=0.760, col='Mobiliario'):
    """Taburete de madera de asiento redondo, sin respaldo."""
    obs = [cilindro(f'{nombre} asiento', cx, cy, 0.165, z - 0.034, z,
                    MAT['silla'], col, segs=48)]
    bisel(obs[0], 0.010, 4)
    for i in range(4):
        a = math.radians(45 + 90 * i)
        px, py = cx + 0.118 * math.cos(a), cy + 0.118 * math.sin(a)
        obs.append(pata_conica(f'{nombre} pata {i}', px, py, 0.0, z - 0.032,
                               0.013, 0.019, MAT['silla'], col,
                               inclinacion=(-0.050 * math.cos(a), -0.050 * math.sin(a))))
    # travesanos
    for i in range(4):
        a0 = math.radians(45 + 90 * i)
        a1 = math.radians(45 + 90 * (i + 1))
        r = 0.150
        x0_, y0_ = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1_, y1_ = cx + r * math.cos(a1), cy + r * math.sin(a1)
        t = caja(f'{nombre} travesano {i}', min(x0_, x1_), min(y0_, y1_),
                 max(x0_, x1_), max(y0_, y1_), 0.230, 0.244, MAT['silla'], col)
        obs.append(bisel(t, 0.003, 2))
    return obs


def sillon_corrido():
    """Banco corrido contra el muro Norte: asiento y respaldo capitonados."""
    x0, x1 = 2.430, 7.500
    y1 = 8.733
    y0 = y1 - 0.560
    obs = []
    base = caja('Sillon base', x0, y0, x1, y1, 0.0, 0.400, MAT['_negro'])
    bisel(base, 0.004)
    obs.append(base)
    # cojin de asiento por tramos, para que se lea el capitone
    n = int((x1 - x0) / 0.70)
    for i in range(n):
        a = x0 + (x1 - x0) * i / n
        b = x0 + (x1 - x0) * (i + 1) / n
        c = caja(f'Sillon cojin {i + 1}', a + 0.006, y0, b - 0.006, y1 - 0.02,
                 0.400, 0.470, MAT['sillon'])
        obs.append(blando(c, 0.030, 4, 1))
        r = caja(f'Sillon respaldo {i + 1}', a + 0.006, y1 - 0.130, b - 0.006, y1,
                 0.470, 1.050, MAT['sillon'])
        obs.append(blando(r, 0.030, 4, 1))
    return obs


def mobiliario():
    """Mesas, sillas y taburetes de las dos plantas, desde mobiliario.py."""
    telas = (MAT['sillon'], MAT['sillon'])
    n_sillas = 0
    for planta, mesas, col in (('PB', MB.MESAS_PB, 'Mobiliario'),
                               ('PA', MB.MESAS_PA, 'Planta alta')):
        dz = 0.0 if planta == 'PB' else Z_PA
        for k, m in enumerate(mesas):
            tag, tipo, x0, y0, x1, y1, lados = m
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            obs = mesa(f'{tag} mesa', cx, cy, x1 - x0, y1 - y0,
                       redonda=(tipo == 'redonda'), col=col)
            for i, (sx0, sy0, sx1, sy1) in enumerate(MB.sillas(m)):
                scx, scy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
                ang = math.degrees(math.atan2(cy - scy, cx - scx)) - 90
                obs += silla(f'{tag} silla {i + 1}', scx, scy, ang,
                             telas[(k + i) % 2], col=col)
                n_sillas += 1
            if dz:
                for o in obs:
                    for v in o.data.vertices:
                        v.co.z += dz
    # taburetes frente al mostrador, del lado de la sala
    mx1 = Q.MOSTRADOR_X[1]
    for i, ty in enumerate((2.30, 2.95, 3.60)):
        taburete(f'Taburete {i + 1}', mx1 + 0.42, ty)
    sillon_corrido()
    return n_sillas


# ========================================== 5. pared azzurro con el logo
# La caja de escalera: su cara Oeste es la pared ciega que se ve de frente
# al venir de la puerta, justo antes de subir. Va pintada entera de azzurro
# y lleva el logo en vinilo de plotter.
PARED_LOGO = dict(x=8.650, y0=3.939, y1=7.738, z0=0.0, z1=Z_SOFITO)


def pared_logo():
    P = PARED_LOGO
    # la pared, pintada entera del azul del Napoli (2 mm por delante del muro)
    caja('Pared azzurro Napoli', P['x'] - 0.002, P['y0'], P['x'] + SOLAPE,
         P['y1'], P['z0'], P['z1'] - 0.001, MAT['_pared_napoli'])
    if not os.path.exists(LOGO):
        print('   (sin logo: falta', LOGO, ')')
        return
    from PIL import Image
    w_px, h_px = Image.open(LOGO).size
    ancho = 1.900                      # vinilo de 1,90 m de ancho
    alto = ancho * h_px / w_px
    cy, cz = (P['y0'] + P['y1']) / 2, 1.470
    x = P['x'] - 0.0035                # el vinilo, delante de la pintura
    me = bpy.data.meshes.new('Logo Casa Margot')
    v = [(x, cy - ancho / 2, cz - alto / 2), (x, cy + ancho / 2, cz - alto / 2),
         (x, cy + ancho / 2, cz + alto / 2), (x, cy - ancho / 2, cz + alto / 2)]
    me.from_pydata(v, [], [(0, 1, 2, 3)])
    me.uv_layers.new()
    uv = me.uv_layers[0].data
    # el plano mira a -X: visto desde la sala, +Y cae a la izquierda, asi que
    # la U va al reves o el logo sale en espejo
    for i, c in enumerate(((1, 0), (0, 0), (0, 1), (1, 1))):
        uv[i].uv = c
    me.materials.append(MT.calca('Vinilo logo Casa Margot', LOGO, rug=0.55))
    ob = bpy.data.objects.new('Logo Casa Margot', me)
    coleccion('Obra').objects.link(ob)
    return ob


# ===================================================== 6. planta alta
def planta_alta():
    """El altillo, con el mismo lenguaje que la planta baja.

    El plano ya trae tabiques, aseo, almacen y huecos; lo que falta es lo que
    hace habitacion: antepecho de vidrio con pasamanos, celosia de listones en
    el testero, luminarias y el suelo, que se pone en suelos_y_techos().
    """
    col = 'Planta alta'
    z = Z_PA
    # --- antepechos de vidrio del vacio, con pasamanos de roble
    bordes = [((2.461, 3.988), (2.461, 7.509)),      # borde Oeste del vacio
              ((2.461, 3.988), (6.320, 3.988))]      # borde Sur del vacio
    for k, ((ax, ay), (bx, by)) in enumerate(bordes):
        if abs(bx - ax) < 1e-6:
            caja(f'Antepecho PA {k + 1}', ax - 0.006, ay, ax + 0.006, by,
                 z, z + E.H_BARANDA, MAT['vidrio'], col)
            caja(f'Pasamanos PA {k + 1}', ax - 0.026, ay, ax + 0.026, by,
                 z + E.H_BARANDA, z + E.H_BARANDA + 0.042, MAT['mesa'], col)
        else:
            caja(f'Antepecho PA {k + 1}', ax, ay - 0.006, bx, ay + 0.006,
                 z, z + E.H_BARANDA, MAT['vidrio'], col)
            caja(f'Pasamanos PA {k + 1}', ax, ay - 0.026, bx, ay + 0.026,
                 z + E.H_BARANDA, z + E.H_BARANDA + 0.042, MAT['mesa'], col)
    # --- celosia de listones en el testero Norte del altillo, como abajo
    listones('Celosia PA', 2.600, 8.720, 6.200, 8.740, z, z + 2.150,
             MAT['_liston'], ancho=0.030, hueco=0.018, fondo=0.020, eje='x', col=col)
    # --- banda azzurro sobre la celosia, gemela de la de abajo
    caja('Banda azzurro PA', 2.600, 8.714, 6.200, 8.734, z + 2.150, z + 2.420,
         MAT['_pared_napoli'], col)
    # --- estantes de botellas en el testero Oeste (simetria con la trasbarra)
    for i in range(3):
        zz = z + 0.90 + i * 0.42
        caja(f'Estante PA {i + 1}', 2.500, 5.100, 2.780, 7.300, zz, zz + 0.030,
             MAT['mesa'], col)


# ==================================================== 7. luminarias
def luminaria_colgante(nombre, cx, cy, z_borde, d=0.340, h=0.200, col='Luces'):
    """Pantalla de opal con aro de laton y varilla negra, la de las fotos."""
    z0 = z_borde
    z1 = z0 + h
    pan = cilindro(f'{nombre} pantalla', cx, cy, d / 2, z0, z1, MAT['_opal'], col, 48)
    aro = cilindro(f'{nombre} aro', cx, cy, d / 2 + 0.006, z0 - 0.012, z0 + 0.022,
                   MAT['_laton'], col, 48)
    bisel(aro, 0.002, 2)
    disco = cilindro(f'{nombre} luz', cx, cy, d / 2 - 0.012, z0 + 0.004, z0 + 0.010,
                     MAT['luz'], col, 48)
    disco.visible_shadow = False
    techo = Z_SOFITO if z_borde < Z_PA else Z_TECHO
    cilindro(f'{nombre} varilla', cx, cy, 0.008, z1, techo, MAT['carp'], col, 16)
    cilindro(f'{nombre} florn', cx, cy, 0.048, techo - 0.016, techo, MAT['carp'], col, 24)
    # la luz de verdad: un area pequeno dentro de la pantalla
    lz = bpy.data.lights.new(f'{nombre} foco', 'AREA')
    lz.shape = 'DISK'
    lz.size = d * 0.8
    lz.energy = 420.0
    lz.color = (1.0, 0.87, 0.70)
    ob = bpy.data.objects.new(f'{nombre} foco', lz)
    ob.location = (cx, cy, z0 + 0.02)
    coleccion(col).objects.link(ob)
    return ob


def aplique(nombre, x, y, z, normal='-Y', col='Luces'):
    """Aplique cuadrado de pared, luz calida rasante."""
    e = 0.055
    if normal in ('-Y', '+Y'):
        s = -1 if normal == '-Y' else 1
        caja(nombre, x - 0.090, y, x + 0.090, y + s * e, z - 0.090, z + 0.090,
             MAT['_opal'], col)
    else:
        s = -1 if normal == '-X' else 1
        caja(nombre, x, y - 0.090, x + s * e, y + 0.090, z - 0.090, z + 0.090,
             MAT['_opal'], col)
    lz = bpy.data.lights.new(f'{nombre} luz', 'AREA')
    lz.size = 0.16
    lz.energy = 130.0
    lz.color = (1.0, 0.82, 0.62)
    ob = bpy.data.objects.new(f'{nombre} luz', lz)
    dx = {'-Y': (0, -e - 0.01, 0), '+Y': (0, e + 0.01, 0),
          '-X': (-e - 0.01, 0, 0), '+X': (e + 0.01, 0, 0)}[normal]
    ob.location = (x + dx[0], y + dx[1], z)
    coleccion(col).objects.link(ob)
    return ob


def empotrado(nombre, x, y, z, col='Luces'):
    cilindro(nombre, x, y, 0.045, z - 0.014, z, MAT['_opal'], col, 24)
    lz = bpy.data.lights.new(f'{nombre} luz', 'SPOT')
    lz.energy = 260.0
    lz.spot_size = math.radians(80)
    lz.spot_blend = 0.55
    lz.shadow_soft_size = 0.035
    lz.color = (1.0, 0.85, 0.66)
    ob = bpy.data.objects.new(f'{nombre} luz', lz)
    ob.location = (x, y, z - 0.02)
    ob.rotation_euler = (math.pi, 0, 0)
    coleccion(col).objects.link(ob)
    return ob


def luces(j):
    """Coloca las luminarias donde las pone el plano, ya con geometria y luz."""
    n = 0
    for s in j['cajas'] + j['cilindros']:
        if s['mat'] != 'luz':
            continue
        nm = s['nombre']
        if 'cx' in s:
            x, y = s['cx'], s['cy']
        else:
            x, y = (s['x0'] + s['x1']) / 2, (s['y0'] + s['y1']) / 2
        if nm.startswith('Colgante'):
            luminaria_colgante(nm, x, y, s['z0'])
        elif nm.startswith('Aplique'):
            aplique(nm, x, y, (s['z0'] + s['z1']) / 2, '-X' if x < 1.2 else '-Y')
        else:
            empotrado(nm, x, y, s['z1'])
        n += 1
    # el altillo necesita su propia luz: el plano no la trae
    for i, (x, y) in enumerate(((3.85, 4.80), (3.85, 6.20), (7.54, 5.43))):
        luminaria_colgante(f'Colgante PA {i + 1}', x, y, Z_PA + 1.700)
    for i, (x, y) in enumerate(((2.90, 8.60), (5.90, 8.60))):
        aplique(f'Aplique PA {i + 1}', x, y, Z_PA + 1.950, '-Y')

    # --- cocina: pantallas estancas suspendidas. Los cuatro empotrados que el
    #     proyecto pone aqui caen en la doble altura y no alumbran nada.
    for i, y in enumerate((6.20, 7.30, 8.40)):
        x0_, x1_ = 0.45, 2.25
        caja(f'Cocina · pantalla {i + 1}', x0_, y - 0.055, x1_, y + 0.055,
             2.560, 2.620, MAT['_opal'], 'Luces')
        for xv in (x0_ + 0.12, x1_ - 0.12):
            cilindro(f'Cocina · tirante {i + 1} {xv:.2f}', xv, y, 0.005, 2.620,
                     Z_TECHO, MAT['carp'], 'Luces', 10)
        lz = bpy.data.lights.new(f'Cocina luz {i + 1}', 'AREA')
        lz.shape = 'RECTANGLE'
        lz.size, lz.size_y = x1_ - x0_, 0.11
        lz.energy = 55.0
        lz.color = (1.0, 0.95, 0.88)
        ob = bpy.data.objects.new(f'Cocina luz {i + 1}', lz)
        ob.location = ((x0_ + x1_) / 2, y, 2.552)
        coleccion('Luces').objects.link(ob)

    # --- tira de LED bajo el estante de la trasbarra: la luz de trabajo y el
    #     brillo que hace que las botellas se lean
    caja('LED trasbarra', 0.26, 2.05, 0.60, 4.72, 1.596, 1.604,
         MAT['_luz_calida'], 'Luces')
    lz = bpy.data.lights.new('LED trasbarra luz', 'AREA')
    lz.shape = 'RECTANGLE'
    lz.size, lz.size_y = 0.30, 2.60
    lz.energy = 90.0
    lz.color = (1.0, 0.88, 0.72)
    ob = bpy.data.objects.new('LED trasbarra luz', lz)
    ob.location = (0.45, 3.39, 1.588)
    coleccion('Luces').objects.link(ob)

    # --- banador que lame la banda azzurro del canto del forjado
    for nm_, loc, tam, rot in (('Banda Sur', (6.15, 3.99, 2.15), (7.4, 0.25), 0.0),
                               ('Banda Oeste', (2.47, 6.45, 2.15), (0.25, 5.0), 0.0)):
        lz = bpy.data.lights.new(f'Banador {nm_}', 'AREA')
        lz.shape = 'RECTANGLE'
        lz.size, lz.size_y = tam
        lz.energy = 70.0
        lz.color = (1.0, 0.93, 0.85)
        ob = bpy.data.objects.new(f'Banador {nm_}', lz)
        ob.location = loc
        ob.rotation_euler = (math.radians(90) if 'Sur' in nm_ else math.radians(90),
                             0, 0 if 'Sur' in nm_ else math.radians(90))
        ob.data.energy = 70.0
        coleccion('Luces').objects.link(ob)
    return n


# ================================================== 8. decoracion italiana
_importados = {}


def importar(aid, nombres=None):
    """Trae un modelo CC0 de Poly Haven y lo deja fuera de escena, de molde."""
    if aid in _importados:
        return _importados[aid]
    ruta = os.path.join(PH, aid, f'{aid}.blend')
    if not os.path.exists(ruta):
        print(f'   (falta el modelo {aid})')
        _importados[aid] = []
        return []
    antes = set(bpy.data.objects.keys())
    with bpy.data.libraries.load(ruta, link=False) as (src, dst):
        dst.objects = [n for n in src.objects
                       if 'LOD1' not in n and 'LOD2' not in n and 'LOD3' not in n
                       and (nombres is None or n in nombres)]
    obs = [o for o in bpy.data.objects if o.name not in antes and o.type == 'MESH']
    molde = coleccion('_moldes')
    for o in obs:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        molde.objects.link(o)
    _importados[aid] = obs
    return obs


def poner(aid, x, y, z, escala=1.0, giro=0.0, col='Decoracion', nombres=None):
    """Copia enlazada de un modelo importado, apoyada en (x, y, z)."""
    molde = importar(aid, nombres)
    if not molde:
        return []
    # caja del conjunto, para apoyarlo por su base y centrarlo en planta
    lo = Vector((1e9,) * 3)
    hi = Vector((-1e9,) * 3)
    for o in molde:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], w[i])
                hi[i] = max(hi[i], w[i])
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    import mathutils
    M = (mathutils.Matrix.Translation((x, y, z))
         @ mathutils.Matrix.Rotation(math.radians(giro), 4, 'Z')
         @ mathutils.Matrix.Scale(escala, 4)
         @ mathutils.Matrix.Translation((-cx, -cy, -lo[2])))
    out = []
    for o in molde:
        c = o.copy()                      # malla enlazada: no duplica memoria
        c.matrix_world = M @ o.matrix_world
        coleccion(col).objects.link(c)
        out.append(c)
    return out


# ---------------------------------------------------------- piezas propias
def copa(nombre, x, y, z, col='Decoracion'):
    """Copa de vino de perfil de revolucion."""
    perfil = [(0.000, 0.000), (0.038, 0.000), (0.040, 0.004), (0.010, 0.010),
              (0.006, 0.020), (0.006, 0.090), (0.012, 0.100), (0.030, 0.118),
              (0.038, 0.145), (0.040, 0.180), (0.038, 0.182), (0.035, 0.150),
              (0.026, 0.120), (0.010, 0.104), (0.004, 0.092), (0.004, 0.020),
              (0.008, 0.008), (0.036, 0.003), (0.000, 0.003)]
    return _revolucion(nombre, perfil, x, y, z, MAT['_vidrio_copa'], col, 40)


def _revolucion(nombre, perfil, x, y, z, mat, col, segs=36):
    v, f = [], []
    n = len(perfil)
    for i in range(segs):
        a = 2 * math.pi * i / segs
        ca, sa = math.cos(a), math.sin(a)
        for (r, h) in perfil:
            v.append((x + r * ca, y + r * sa, z + h))
    for i in range(segs):
        j = (i + 1) % segs
        for k in range(n - 1):
            f.append((i * n + k, j * n + k, j * n + k + 1, i * n + k + 1))
    ob = _malla(nombre, v, f, mat, col, suave=True)
    return ob


def taza(nombre, x, y, z, col='Decoracion', r=0.038, h=0.062):
    perfil = [(0.000, 0.000), (r * 0.62, 0.000), (r * 0.66, 0.004), (r * 0.92, h * 0.72),
              (r, h), (r - 0.0035, h), (r * 0.90, h * 0.72), (r * 0.60, 0.006),
              (0.000, 0.006)]
    ob = _revolucion(nombre, perfil, x, y, z, MAT['_blanco'], col, 32)
    # plato
    pl = _revolucion(f'{nombre} plato', [(0.000, 0.000), (0.060, 0.000), (0.066, 0.004),
                                         (0.068, 0.009), (0.064, 0.009), (0.058, 0.005),
                                         (0.000, 0.005)], x, y, z - 0.009,
                     MAT['_blanco'], col, 32)
    return [ob, pl]


def plato(nombre, x, y, z, r=0.115, col='Decoracion'):
    perfil = [(0.000, 0.000), (r * 0.80, 0.000), (r, 0.014), (r, 0.019),
              (r * 0.78, 0.006), (0.000, 0.006)]
    return _revolucion(nombre, perfil, x, y, z, MAT['_blanco'], col, 40)


def botella(nombre, x, y, z, alto=0.300, col='Decoracion', vidrio=None, giro=0.0):
    """Botella de aceite o de vino, de perfil."""
    r = 0.038
    c = alto * 0.62
    perfil = [(0.000, 0.000), (r, 0.006), (r, c), (r * 0.72, c + 0.055),
              (0.014, c + 0.105), (0.013, alto - 0.020), (0.016, alto - 0.006),
              (0.016, alto), (0.000, alto)]
    ob = _revolucion(nombre, perfil, x, y, z,
                     vidrio or MT.vidrio(f'{nombre} vidrio', (0.16, 0.34, 0.12), 0.03),
                     col, 28)
    # etiqueta
    caja(f'{nombre} etiqueta', x - r * 0.99, y - r * 0.99, x + r * 0.99, y + r * 0.99,
         z + alto * 0.17, z + alto * 0.42, MAT['_blanco'], col)
    return ob


def tarro(nombre, x, y, z, alto=0.220, r=0.058, col='Decoracion'):
    """Tarro de cristal con pasta: la despensa a la vista."""
    perfil = [(0.000, 0.000), (r, 0.004), (r, alto - 0.030), (r * 0.86, alto - 0.010),
              (r * 0.86, alto), (0.000, alto)]
    _revolucion(nombre, perfil, x, y, z, MT.vidrio(f'{nombre} v', (0.98, 0.98, 0.96)), col, 28)
    cilindro(f'{nombre} tapa', x, y, r * 0.90, z + alto, z + alto + 0.016,
             MAT['_laton'], col, 28)
    relleno = cilindro(f'{nombre} pasta', x, y, r * 0.92, z + 0.010, z + alto - 0.045,
                       MT.liso(f'{nombre} m', MT.srgb('E3C275'), 0.75), col, 28)
    return relleno


def cuadro(nombre, x, y, z, ancho, alto, normal='-Y', col='Decoracion'):
    """Lamina enmarcada en negro."""
    e = 0.028
    if normal in ('-Y', '+Y'):
        s = -1 if normal == '-Y' else 1
        caja(nombre, x - ancho / 2, y, x + ancho / 2, y + s * e,
             z - alto / 2, z + alto / 2, MAT['carp'], col)
        caja(f'{nombre} lamina', x - ancho / 2 + 0.045, y + s * (e + 0.001),
             x + ancho / 2 - 0.045, y + s * (e + 0.002),
             z - alto / 2 + 0.045, z + alto / 2 - 0.045, MAT['_blanco'], col)
    else:
        s = -1 if normal == '-X' else 1
        caja(nombre, x, y - ancho / 2, x + s * e, y + ancho / 2,
             z - alto / 2, z + alto / 2, MAT['carp'], col)
        caja(f'{nombre} lamina', x + s * (e + 0.001), y - ancho / 2 + 0.045,
             x + s * (e + 0.002), y + ancho / 2 - 0.045,
             z - alto / 2 + 0.045, z + alto / 2 - 0.045, MAT['_blanco'], col)


def decoracion():
    """Todo lo que hace que el local parezca abierto y no un plano en 3D."""
    rnd = random.Random(23)
    # ---- trasbarra: estante A6 con botellas, tarros de pasta y vajilla
    z_est = 1.600 + 0.245 + 0.010
    for i in range(9):
        y = 2.30 + i * 0.26
        botella(f'Botella estante {i + 1}', 0.42, y, z_est,
                alto=0.28 + 0.06 * ((i * 7) % 3) / 2)
    for i in range(4):
        tarro(f'Tarro pasta {i + 1}', 0.62, 2.45 + i * 0.30, z_est, alto=0.20 + 0.03 * (i % 2))
    # tazas de espresso boca abajo sobre la cafetera y la mesada
    for i in range(6):
        taza(f'Taza barra {i + 1}', 0.40 + 0.11 * (i % 3), 4.20 + 0.12 * (i // 3), 0.905)
    # ---- mostrador: lo que ve el cliente
    mx1 = Q.MOSTRADOR_X[1]
    z_tabla = Q.H_ENCIMERA + 0.040
    poner('wicker_basket_01', mx1 - 0.30, 4.35, z_tabla, escala=0.85, giro=18)
    poner('ceramic_vase_01', mx1 - 0.30, 4.08, z_tabla, escala=0.9, giro=-25)
    for i in range(3):
        copa(f'Copa mostrador {i + 1}', mx1 - 0.16, 4.60 + i * 0.09, z_tabla)
    # ---- botellero sobre la vitrina y aceite en el paso
    poner('jug_01', 0.45, 4.62, 0.905, escala=1.0, giro=35)
    poner('metal_jug', 0.66, 4.60, 0.905, escala=0.9, giro=-15)
    # ---- barrica de vino como mesa alta junto al ventanal
    poner('wine_barrel_01', 7.90, 2.35, 0.0, escala=1.0, giro=12)
    poner('wine_bottles_01', 7.90, 2.35, 0.86, escala=1.0, giro=-40)
    # ---- plantas: terracota, el verde de la trattoria
    for aid, x, y, s, g in (('potted_plant_01', 2.20, 3.30, 1.0, 20),
                            ('potted_plant_02', 8.35, 7.95, 1.1, -30),
                            ('potted_plant_01', 5.98, 4.35, 0.9, 60),
                            ('tree_small_02', 9.55, 2.10, 1.0, 10)):
        poner(aid, x, y, 0.0, escala=s, giro=g)
    for i, (x, y) in enumerate(((2.62, 8.55), (7.10, 8.55))):
        poner('planter_pot_clay', x, y, 0.0, escala=1.2, giro=i * 40)
    # ---- fruta y pan en el paso de la cocina
    poner('wooden_bowl_01', 1.30, 6.90, Q.H_ENCIMERA, escala=1.0, giro=25)
    for i, aid in enumerate(('food_apple_01', 'food_lime_01', 'food_pomegranate_01')):
        poner(aid, 1.26 + 0.05 * i, 6.88 + 0.04 * (i % 2), Q.H_ENCIMERA + 0.045,
              escala=1.0, giro=i * 55)
    poner('wicker_basket_02', 1.75, 6.90, Q.H_ENCIMERA, escala=0.9, giro=-12)
    # ---- cuadros en la pared Norte y en el testero
    for i, x in enumerate((3.30, 4.10, 4.90)):
        cuadro(f'Cuadro {i + 1}', x, 8.700, 1.700, 0.440, 0.560, '-Y')
    # ---- mesas puestas: cada una cuenta algo distinto
    for k, m in enumerate(MB.MESAS_PB):
        tag, tipo, x0, y0, x1, y1, lados = m
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        z = H_MESA
        estilo = k % 4
        if estilo == 0:
            taza('Taza ' + tag, cx - 0.14, cy + 0.05, z)
            taza('Taza b ' + tag, cx + 0.13, cy - 0.06, z)
            plato('Plato ' + tag, cx, cy + 0.17, z, r=0.085)
        elif estilo == 1:
            copa('Copa ' + tag + ' 1', cx - 0.12, cy + 0.08, z)
            copa('Copa ' + tag + ' 2', cx + 0.11, cy + 0.06, z)
            botella('Vino ' + tag, cx, cy - 0.13, z, alto=0.300)
        elif estilo == 2:
            poner('tea_set_01', cx, cy, z, escala=1.0, giro=rnd.uniform(-30, 30))
        else:
            plato('Plato ' + tag, cx - 0.05, cy, z)
            poner('croissant', cx - 0.05, cy, z + 0.008, escala=1.0,
                  giro=rnd.uniform(0, 360))
            taza('Taza ' + tag, cx + 0.16, cy + 0.03, z)
        # aceite y sal en todas
        botella('Aceite ' + tag, cx + 0.22, cy + 0.20, z, alto=0.185)
    # ---- mesas de planta alta
    for k, m in enumerate(MB.MESAS_PA):
        tag, tipo, x0, y0, x1, y1, lados = m
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        z = H_MESA + Z_PA
        if tipo == 'cowork':
            for i in range(3):
                taza(f'Taza PA {tag} {i}', cx - 0.7 + i * 0.7, cy + 0.2, z,
                     col='Planta alta')
            poner('ceramic_vase_02', cx, cy, z, escala=0.85, giro=20, col='Planta alta')
        else:
            poner('wicker_basket_01', cx, cy, z, escala=0.7, giro=-20, col='Planta alta')
            for i in range(4):
                copa(f'Copa PA {i}', cx + 0.22 * math.cos(i * 1.57),
                     cy + 0.22 * math.sin(i * 1.57), z, col='Planta alta')
    # ---- estantes del altillo con botellas y ceramica
    for i in range(3):
        zz = Z_PA + 0.90 + i * 0.42 + 0.030
        for k in range(6):
            botella(f'Botella PA {i}{k}', 2.64, 5.25 + k * 0.33, zz,
                    alto=0.26 + 0.05 * (k % 3), col='Planta alta')
    poner('brass_pot_01', 2.66, 7.10, Z_PA + 0.90 + 0.84 + 0.03, escala=0.9,
          col='Planta alta')
    poner('ceramic_vase_03', 2.66, 5.05, Z_PA + 0.93, escala=0.9, col='Planta alta')


# ==================================================== 9. exterior y cielo
def mundo(rot=-102.5, fuerza=4.2):
    """Cielo real: HDRI de calle de Poly Haven."""
    w = bpy.data.worlds.new('Casa Margot')
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = fuerza
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    hdri = os.path.join(PH, 'wide_street_01', 'wide_street_01_8k.hdr')
    if os.path.exists(hdri):
        env = nt.nodes.new('ShaderNodeTexEnvironment')
        env.image = MT.imagen(hdri)
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Rotation'].default_value = (0, 0, math.radians(rot))
        tc = nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
        nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
        nt.links.new(env.outputs['Color'], bg.inputs['Color'])
    else:
        bg.inputs['Color'].default_value = (0.42, 0.52, 0.68, 1)
    return w


def exterior():
    """Acera, calzada y arbolado: lo que se ve por el escaparate."""
    caja('Acera', -14.0, -12.0, 24.0, 1.500, -0.020, 0.000,
         MT.pbr('Acera', 'large_floor_tiles_02', 3.0, tint=(1.02, 0.99, 0.94)), 'Exterior')
    caja('Calzada', -14.0, -12.0, 24.0, -3.200, -0.150, -0.020,
         MT.pbr('Asfalto', 'asphalt_02', 3.0), 'Exterior')
    caja('Bordillo', -14.0, -3.260, 24.0, -3.200, -0.020, 0.120,
         MAT['piedra'], 'Exterior')
    for i, x in enumerate((-3.0, 2.5, 8.0, 13.5)):
        poner('tree_small_02', x, -1.30, 0.0, escala=2.6 + 0.4 * (i % 2),
              giro=i * 47, col='Exterior')


# ==================================================== 10. camaras y render
def camara(nombre, ojo, mira, lente=28.0, despl=0.0):
    """Camara de arquitectura: mira a un punto y se deja el horizonte recto."""
    import mathutils
    cam = bpy.data.cameras.new(nombre)
    cam.lens = lente
    cam.sensor_width = 36.0
    cam.clip_start = 0.02
    cam.clip_end = 200.0
    cam.shift_y = despl
    ob = bpy.data.objects.new(nombre, cam)
    coleccion('Camaras').objects.link(ob)
    d = Vector(mira) - Vector(ojo)
    ob.location = ojo
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


# ojo, mira, lente: las siete vistas que cuentan el local
VISTAS = {
    # la barra en diagonal, con el mostrador huyendo y la trasbarra al fondo
    'barra':      ((4.90, 1.95, 1.520), (1.35, 4.30, 1.060), 24.0),
    # la sala desde la entrada, con el pilar forrado y la escalera
    'sala':       ((8.75, 2.10, 1.600), (4.10, 6.30, 1.220), 21.0),
    # desde dentro hacia el escaparate de doble altura
    'escaparate': ((4.60, 6.30, 1.580), (6.10, 1.30, 1.900), 24.0),
    # la cocina vista desde la sala, a traves de la mampara
    'cocina':     ((2.16, 5.90, 1.600), (1.05, 8.70, 1.120), 21.0),
    # la pared azzurro con el logo, de frente
    'logo':       ((7.05, 2.80, 1.560), (8.64, 5.90, 1.430), 30.0),
    # el altillo
    'alta':       ((8.30, 7.75, Z_PA + 1.560), (3.85, 4.95, Z_PA + 1.150), 21.0),
    # panoramica general desde la esquina de entrada
    'general':    ((9.30, 1.70, 2.150), (3.40, 6.60, 1.250), 18.0),
}


def compositor():
    """Un velo de brillo en las luces: es lo que acaba de hacer la foto."""
    sc = bpy.context.scene
    sc.use_nodes = True

    def glare(nt):
        g = nt.nodes.new('CompositorNodeGlare')
        # en Blender 5 los ajustes del nodo son entradas, no propiedades
        val = {'Type': 'Fog Glow', 'Quality': 'High', 'Threshold': 1.05,
               'Strength': 0.30, 'Size': 0.62, 'Saturation': 1.0}
        for k, v in val.items():
            if k in g.inputs:
                try:
                    g.inputs[k].default_value = v
                except Exception:
                    pass
            elif hasattr(g, k.lower()):
                setattr(g, k.lower(), v)
        return g

    if hasattr(sc, 'compositing_node_group'):
        nt = sc.compositing_node_group
        if nt is None:
            nt = bpy.data.node_groups.new('Compositor', 'CompositorNodeTree')
            sc.compositing_node_group = nt
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        nt.interface.clear()
        nt.interface.new_socket('Image', in_out='INPUT', socket_type='NodeSocketColor')
        nt.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        gi = nt.nodes.new('NodeGroupInput')
        gi.location = (-400, 0)
        go = nt.nodes.new('NodeGroupOutput')
        go.location = (400, 0)
        g = glare(nt)
        nt.links.new(gi.outputs[0], g.inputs['Image'])
        nt.links.new(g.outputs['Image'], go.inputs[0])
        return nt

    nt = sc.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    ren = nt.nodes.new('CompositorNodeRLayers')
    g = glare(nt)
    out = nt.nodes.new('CompositorNodeComposite')
    nt.links.new(ren.outputs['Image'], g.inputs['Image'])
    nt.links.new(g.outputs['Image'], out.inputs['Image'])
    return nt


def construir(spp, ancho, alto, con_decoracion=True, con_glare=False):
    global MAT
    sc = escena_nueva(spp, ancho, alto)
    MAT = MT.construir()
    print('  materiales:', len(MAT), flush=True)
    n, j = arquitectura()
    print('  obra:', n, 'solidos', flush=True)
    suelos_y_techos()
    frente_barra()
    forro_pilar()
    cocina_inox()
    pared_logo()
    planta_alta()
    puestos = aparatos(j)
    print('  aparatos 1:1:', len(puestos), '/', len(TAGS_BIBLIOTECA), flush=True)
    ns = mobiliario()
    print('  mobiliario:', ns, 'sillas', flush=True)
    nl = luces(j)
    print('  luminarias del plano:', nl, flush=True)
    mundo()
    exterior()
    if con_decoracion:
        decoracion()
        print('  decoracion puesta', flush=True)
    if con_glare:
        compositor()
    else:
        bpy.context.scene.use_nodes = False
    return sc


def render(vista, salida, spp, ancho, alto, rapido=False):
    sc = bpy.context.scene
    ojo, mira, lente = VISTAS[vista]
    cam = camara(f'cam {vista}', ojo, mira, lente)
    sc.camera = cam
    sc.render.filepath = salida
    if rapido:
        sc.cycles.samples = max(24, spp // 16)
        sc.render.resolution_x = ancho // 3
        sc.render.resolution_y = alto // 3
    bpy.ops.render.render(write_still=True)
    return salida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vista', default='barra')
    ap.add_argument('--todas', action='store_true')
    ap.add_argument('--spp', type=int, default=1200)
    ap.add_argument('--ancho', type=int, default=3840)
    ap.add_argument('--alto', type=int, default=2160)
    ap.add_argument('--rapido', action='store_true')
    ap.add_argument('--sin-decoracion', action='store_true')
    ap.add_argument('--glare', action='store_true')
    ap.add_argument('--salida', default=os.path.join(SCRATCH, 'renders'))
    ap.add_argument('--guardar-blend', default='')
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None)

    os.makedirs(a.salida, exist_ok=True)
    print('Casa Margot · montando la escena', flush=True)
    construir(a.spp, a.ancho, a.alto, not a.sin_decoracion, a.glare)
    print('  objetos en escena:', len(bpy.data.objects), flush=True)
    if a.guardar_blend:
        bpy.ops.wm.save_as_mainfile(filepath=a.guardar_blend)
        print('  guardado', a.guardar_blend, flush=True)
    vistas = list(VISTAS) if a.todas else [a.vista]
    for v in vistas:
        f = os.path.join(a.salida, f'CM_{v}.png')
        print(f'  render {v} -> {f}', flush=True)
        import time
        t = time.time()
        render(v, f, a.spp, a.ancho, a.alto, a.rapido)
        print(f'  {v} listo en {time.time() - t:.0f} s', flush=True)


if __name__ == '__main__':
    main()
