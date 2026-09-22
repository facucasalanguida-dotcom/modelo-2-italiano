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

from rutas import SCRATCH, PH, LOGO   # noqa: E402

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


def sustraer(cuerpo, cortador, borrar=True):
    """Resta booleana. El cortador tiene que sobresalir de la cara que corta:
    si queda a hueso deja dos caras coincidentes y el render parpadea."""
    md = cuerpo.modifiers.new('corte', 'BOOLEAN')
    md.operation = 'DIFFERENCE'
    md.object = cortador
    md.solver = 'EXACT'
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(cuerpo.evaluated_get(dg))
    vieja = cuerpo.data
    cuerpo.data = me
    cuerpo.modifiers.remove(md)
    bpy.data.meshes.remove(vieja)
    if borrar:
        bpy.data.objects.remove(cortador, do_unlink=True)
    return cuerpo


def malla_libre(nombre, verts, faces, mat, col, suave=True):
    """Malla a medida, para las piezas que no son cajas ni cilindros."""
    return _malla(nombre, verts, faces, mat, col, suave)


def girar(ob, centro, grados, eje='Z'):
    import mathutils
    c = Vector(centro)
    R = mathutils.Matrix.Rotation(math.radians(grados), 4, eje)
    for v in ob.data.vertices:
        v.co = R @ (v.co - c) + c
    return ob


# =============================================== 1. escena limpia y ajustes
# La misma escena no se expone igual desde dentro que desde la calle. El HDRI
# va a 4,2 para que entre luz de sobra por el escaparate de doble altura, y a
# la intemperie eso son casi dos pasos de mas: el cielo y los paramentos
# salian quemados. Desde fuera se cierra el diafragma, como haria cualquiera.
EXPOSICION_BASE = 0.65
EXPOSICION = {'calle': -1.30, 'fachada': -1.30}


# Por defecto CPU: la maquina donde se monto esto no tiene tarjeta. Con
# --gpu se buscan las tarjetas que Cycles sepa usar -OptiX y CUDA en NVIDIA,
# HIP en AMD, Metal en Mac, oneAPI en Intel- y se encienden todas junto con
# la CPU. Si no hay ninguna, se avisa y se sigue por CPU en vez de reventar.
USAR_GPU = False


def _dispositivo():
    if not USAR_GPU:
        return 'CPU'
    try:
        pref = bpy.context.preferences.addons['cycles'].preferences
        for tipo in ('OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI'):
            try:
                pref.compute_device_type = tipo
            except Exception:
                continue
            pref.get_devices()
            tarjetas = [d for d in pref.devices if d.type == tipo]
            if not tarjetas:
                continue
            for d in pref.devices:
                d.use = True          # tarjetas y CPU a la vez
            print(f'  GPU: {tipo} ->', ', '.join(d.name for d in tarjetas), flush=True)
            return 'GPU'
    except Exception as e:
        print('  GPU: no se pudo activar (', e, ')', flush=True)
    print('  GPU: no hay tarjeta que Cycles sepa usar; se renderiza por CPU', flush=True)
    return 'CPU'


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
    sc.cycles.device = _dispositivo()
    sc.cycles.samples = spp
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.010
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = 'OPENIMAGEDENOISE'
        sc.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    except Exception:
        pass
    sc.cycles.max_bounces = 12
    sc.cycles.diffuse_bounces = 6
    sc.cycles.glossy_bounces = 6
    sc.cycles.transmission_bounces = 8
    # Los paños de vidrio no son refractivos: son un Transparent BSDF con algo
    # de glossy encima -un vidrio de refraccion real en un paño de 4 m deja el
    # interior lleno de ruido-. Pero cada cara que atraviesa un Transparent
    # gasta un rebote de los de esta cuenta, y una caja de vidrio gasta dos.
    # Con 6 se agotaban enseguida: desde la planta alta, el antepecho (2) mas
    # otro paño (2) mas el ventanal (2) son justo 6, y al pasarse Cycles corta
    # el rayo y devuelve NEGRO. Por eso la barandilla de vidrio salia como un
    # panel negro. Son rebotes baratos -el rayo solo sigue recto-, asi que se
    # sube con holgura.
    sc.cycles.transparent_max_bounces = 32
    sc.cycles.sample_clamp_indirect = 10.0
    sc.cycles.blur_glossy = 0.6
    # Fast GI fuera. Estaba puesto con ao_bounces_render = 3 para ahorrar un
    # tercio del tiempo, con la idea de que no se notaba. Si se nota: a partir
    # del tercer rebote Cycles cambia el transporte de luz por una
    # aproximacion de oclusion, y en una superficie transmisiva eso la vuelve
    # opaca y oscura. Mirando desde la planta alta a traves del antepecho de
    # vidrio y luego del ventanal son cuatro superficies, se pasa del limite y
    # el vidrio sale negro. El ahorro tampoco hace ya falta: el lote se
    # renderiza con tarjeta.
    try:
        sc.cycles.use_fast_gi = False
    except Exception:
        pass
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
    sc.view_settings.exposure = EXPOSICION_BASE
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
    if '· hoja' in nm and s['mat'] in ('madera', 'vidrio'):
        return True                       # las puertas se rehacen con herrajes
    return False


# ------------------------------------------------- retranqueo de la entrada
# La puerta NO esta en el plano de fachada: la entrada va metida hacia dentro.
# Lo dice la propia planta baja, aunque el dibujo 2D la grafie en la linea del
# escaparate:
#   * la medianera Este engorda de 0,150 a 0,330 SOLO entre y = 0,330 y
#     y = 1,429 ('Medianera Este - cuello'). Ese engorde es el costado del
#     hueco; no hay otra razon para que un muro medianero sea el doble de
#     grueso justo el primer metro y vuelva a su espesor despues.
#   * la cota 1,06 del plano mide exactamente ese tramo (0,370 a 1,429), que
#     es el fondo del vestibulo, y la nota lo llama VESTIBULO DE ACCESO.
#   * la cadena de fachada es 1,31 de escaparate + 2,06 de puerta + 0,34 de
#     muro = 3,71, de P5 (6,331) a la cara exterior de la medianera (10,040).
# Asi que el hueco de 2,06 x 2,10 se abre en la fachada y la puerta se planta
# 1,06 mas adentro, en y = 1,429, que es justo donde muere el cuello y
# empieza la pared del plotter.
#
# Lo que queda delante de la puerta es un cubo de obra: paredes y techo. El
# costado Este es la cara del cuello (x = 9,710) y el Oeste es un tabique de
# 96 mm cuya cara vista cae en x = 7,641, la jamba que midio el cliente: sus
# 1,31 de P5 a la jamba y sus 2,23 de ancho de vestibulo suman los 3,559 que
# hay de P5 al muro Este, luego la jamba es una linea sin grueso y el tabique
# tiene que crecer hacia el escaparate. El vidrio pierde ahi 96 mm por debajo
# del techo del cubo y sigue entero por encima.
RETRANQUEO = dict(x0=7.641, x1=9.710, y0=0.370, y1=1.429,
                  alto=2.100, canto=0.140, zocalo=0.130, e_pared=0.096)


def _retranquear(cajas):
    """Mete la puerta de acceso al fondo del vestibulo y abre el hueco.

    Toca los solidos del plano en el propio diccionario, antes de dibujar,
    para que la carpinteria -que rehace las hojas leyendo j['cajas']- las
    encuentre ya en su sitio.
    """
    R = RETRANQUEO
    for s in cajas:
        nm = s['nombre'] or ''
        if nm in ('Escaparate · zócalo de piedra', 'Escaparate · vidrio'):
            # el escaparate es del escaparate: no cruza el hueco de la
            # entrada, y muere medio milimetro antes de la jamba para no
            # compartir plano con el tabique que lo tapa
            s['x1'] = R['x0'] - DESPEGUE
        elif nm.startswith('Puerta de acceso · hoja'):
            # al fondo del retranqueo y apoyada en el pavimento: 2,10 de hueco
            # de paso, no 2,10 medidos desde el zocalo del escaparate
            s['y0'], s['y1'] = R['y1'] - 0.049, R['y1']
            s['z0'] = 0.0
            if abs(s['x1'] - 9.701) < 1e-6:
                s['x1'] = R['x1'] + SOLAPE      # cierra contra el cuello
        elif nm == 'Puerta de acceso · montante superior':
            s['x1'] = R['x1']                   # el pano macizo, hasta el cuello


def _asentar(cajas):
    """Apoyos del plano que no cuadran con el mueble que los sostiene."""
    for s in cajas:
        if (s['nombre'] or '').startswith('B4 ·'):
            # La bandeja de la chopera es de 40 x 40 y la tabla de P2 solo
            # tiene 39 de fondo (y 1,621..2,011). El plano dibuja la columna
            # en y 1,701..2,101: 90 mm de bandeja volando por el Norte de la
            # tabla, en el aire. Se centra sobre ella y quedan 5 mm por lado.
            d = 1.616 - s['y0']
            s['y0'] += d
            s['y1'] += d


DESPEGUE = 0.0005                 # medio milimetro


def _despegar(cajas):
    """Separa las caras que dos solidos del plano comparten exactamente.

    El plano dibuja la esquina en L de dos tabiques como dos cajas que
    solapan el bloque del rincon, y las dos llevan su cara en el mismo plano
    y mirando al mismo lado. Cycles no tiene forma de saber cual esta
    delante, y donde eso pasa sale una franja negra a lo alto de la esquina
    (se veia en el rincon del baño y en el doblez de la mampara). La cura es
    retirar medio milimetro la cara de la caja mas pequeña: alli esta metida
    dentro de la otra, asi que esa cara deja de verse, y donde la caja no
    solapa el escalon de medio milimetro no lo aprecia nadie.

    Devuelve {indice de la caja: {clave: desplazamiento}}.
    """
    ejes = (('x0', 'x1'), ('y0', 'y1'), ('z0', 'z1'))

    def vol(s):
        return (s['x1'] - s['x0']) * (s['y1'] - s['y0']) * (s['z1'] - s['z0'])

    ajustes = {}
    for i, a in enumerate(cajas):
        for k, b in enumerate(cajas[i + 1:], i + 1):
            if any(min(a[c1], b[c1]) - max(a[c0], b[c0]) <= DESPEGUE for c0, c1 in ejes):
                continue                   # no se interpenetran de verdad
            j = i if vol(a) < vol(b) else k
            # solo en planta: retirar media decima en Z abriria una rendija
            # de luz entre el arranque del muro y el suelo o el techo
            for c0, c1 in ejes[:2]:
                for c, sg in ((c0, +1), (c1, -1)):
                    if abs(a[c] - b[c]) < 1e-9:
                        ajustes.setdefault(j, {})[c] = sg * DESPEGUE
    return ajustes


def arquitectura():
    """Muros, forjado, escalera, carpinteria y mobiliario fijo del plano."""
    j = json.load(open(os.path.join(PLANOS, 'MODELO_3D.json'), encoding='utf-8'))
    _retranquear(j['cajas'])
    _asentar(j['cajas'])
    ajustes = _despegar(j['cajas'])
    print('  caras coplanarias despegadas:', len(ajustes), flush=True)
    n = 0
    for i, s in enumerate(j['cajas']):
        if sustituido(s):
            continue
        m = MAT.get(s['mat'])
        nm = s['nombre'] or ''
        col = 'Planta alta' if s['tag'].startswith('14') else 'Obra'
        d = ajustes.get(i, {})
        x0, x1 = s['x0'] + d.get('x0', 0.0), s['x1'] + d.get('x1', 0.0)
        y0, y1 = s['y0'] + d.get('y0', 0.0), s['y1'] + d.get('y1', 0.0)
        z0 = s['z0'] + d.get('z0', 0.0)
        z1 = s['z1'] + d.get('z1', 0.0)
        if s['nombre'].startswith('Tramo largo') and s['mat'] == 'vidrio':
            z1 = Z_SOFITO          # el vidrio de la L, hasta el techo
        if s['nombre'] == 'Puerta de acceso · montante superior':
            # El plano lo dibuja en vidrio, pero encima de la puerta va
            # pared, no ventanal. Se le da el grueso entero de la fachada
            # -de 0,370 a 0,419, el mismo que el dintel de arriba y que las
            # hojas de abajo- en vez de los 29 mm que tenia de acristalado,
            # para que el pano suba continuo de la puerta al dintel.
            m = MAT['muro']
            y0, y1 = 0.370, 0.419
        if s['nombre'] in ('Tramo largo 3,60', 'Doblez 0,74'):
            # La pared en L iba con la clave 'tabique' del plano, que es un
            # enlucido mas frio y mas blanco que el de los muros. Se pinta
            # del mismo color que las paredes.
            m = MAT['muro']
        if s['nombre'] == 'Viga P1b':
            # La viga acostada iba de 2,100 a 2,310: entera por debajo del
            # forjado y en una zona de doble altura donde encima no hay nada.
            # Por mucho que se alargara hasta el canto seguia leyendose como
            # una barra colgada en el aire, y darle entrega por debajo del
            # bloque tampoco vale, porque el bloque tiene que ser macizo y
            # sin nada colgando del intrados.
            #
            # Se sube a la franja del propio forjado: ocupa de 2,310 a 2,560,
            # el mismo canto que la planta alta, y muere a hueso contra su
            # cara Oeste (x = 2,411). Asi la viga es un brazo del bloque que
            # sale hasta el machon P1 -misma cara inferior, misma cara
            # superior, mismo plano de testa- en vez de una pieza suelta por
            # debajo. Gana 40 mm de canto respecto al plano.
            x1 = 2.411
            z0, z1 = Z_SOFITO, Z_PA
        ob = caja(s['nombre'], x0, y0, x1, y1, z0, z1, m, col)
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


# --------------------------------------------------------------- carpinteria
# El plano dibuja cada puerta como una tabla: una caja de 40 mm de canto. De
# cerca eso no cuela, asi que aqui se rehacen enteras: cerco dentro del hueco,
# tapajuntas a las dos caras, hoja de dos cuarterones con montantes y
# travesanos, tres pernios y manilla de palanca con roseta a ambos lados.
CERCO = 0.028                    # canto del cerco, dentro del hueco
TAPAJUNTAS, TJ_VUELO = 0.055, 0.012
HOJA_E, NUCLEO_E = 0.042, 0.020  # grueso del bastidor y del cuarteron hundido
HOLGURA, BAJO_PUERTA = 0.003, 0.010
MONTANTE, TRAV_SUP, TRAV_CERR, TRAV_INF = 0.105, 0.105, 0.180, 0.200
ALTO_MANILLA = 1.020             # sobre el pavimento de su planta
# la del baño va mas corta que las demas, como pidio el cliente
ALTO_HOJA = {'Baño': 2.030}


def _cil_eje(nombre, p, r, largo, eje, mat, col, segs=24):
    """Cilindro tumbado: el helper solo sabe hacerlos de pie."""
    x, y, z = p
    ob = cilindro(nombre, x, y, r, z - largo / 2, z + largo / 2, mat, col, segs=segs)
    if eje == 'X':
        girar(ob, (x, y, z), 90, 'Y')
    elif eje == 'Y':
        girar(ob, (x, y, z), 90, 'X')
    return ob


def _manilla(C, D, a, b_cara, z, sentido, mat, nm, col):
    """Roseta, cuello y palanca en una cara de la hoja.

    sentido es hacia donde mira la cara: +1 si da a la b creciente, -1 si a la
    decreciente. La roseta se mete 2 mm en la hoja para no dejar dos caras
    pegadas, y de ella sale el cuello y la palanca.
    """
    v = sentido
    D(f'{nm} roseta', (a, b_cara + v * 0.004, z), 0.028, 0.012, mat, col)
    D(f'{nm} cuello', (a, b_cara + v * 0.028, z), 0.011, 0.040, mat, col)
    C(f'{nm} palanca', a - 0.105, b_cara + v * 0.040, a + 0.013, b_cara + v * 0.062,
      z - 0.011, z + 0.011, mat)
    D(f'{nm} bocallave', (a, b_cara + v * 0.003, z - 0.055), 0.012, 0.010, mat, col)


def _puerta_madera(s, dintel, col):
    """Una puerta de paso completa donde el plano ponia una tabla."""
    nm = s['nombre'].split(' · ')[0]
    x0, x1, y0, y1 = s['x0'], s['x1'], s['y0'], s['y1']
    tumbada = (x1 - x0) >= (y1 - y0)       # la hoja se desarrolla en X
    if tumbada:
        a0, a1 = x0, x1
        b0, b1 = ((dintel['y0'], dintel['y1']) if dintel else (y0 - 0.030, y1 + 0.030))
        def C(n, aa0, bb0, aa1, bb1, zz0, zz1, m):
            return caja(n, aa0, bb0, aa1, bb1, zz0, zz1, m, col)
        def D(n, p, r, largo, m, cl):
            return _cil_eje(n, (p[0], p[1], p[2]), r, largo, 'Y', m, cl)
    else:
        a0, a1 = y0, y1
        b0, b1 = ((dintel['x0'], dintel['x1']) if dintel else (x0 - 0.030, x1 + 0.030))
        def C(n, aa0, bb0, aa1, bb1, zz0, zz1, m):
            return caja(n, bb0, aa0, bb1, aa1, zz0, zz1, m, col)
        def D(n, p, r, largo, m, cl):
            return _cil_eje(n, (p[1], p[0], p[2]), r, largo, 'X', m, cl)

    madera, herraje = MAT['madera'], MAT['inox']
    z0 = s['z0']
    alto = ALTO_HOJA.get(nm, s['z1'] - z0)
    ztop = z0 + alto                       # cara inferior del cabecero
    zc = ztop + CERCO                      # trasdos del cerco

    piezas = []
    # si la hoja se acorta, el hueco que queda se cierra con el mismo tabique
    if zc < s['z1']:
        piezas.append(C(f'{nm} · ciego sobre la puerta', a0 - SOLAPE, b0, a1 + SOLAPE,
                        b1, zc - SOLAPE, s['z1'] + SOLAPE, MAT['tabique']))
    # cerco: las jambas se meten 4 mm en la mocheta y el cabecero en las jambas
    for lado, aa in (('izquierda', a0), ('derecha', a1)):
        sg = 1 if aa == a0 else -1
        piezas.append(C(f'{nm} · jamba {lado}', aa - sg * SOLAPE, b0 - 0.002,
                        aa + sg * CERCO, b1 + 0.002, z0, zc, madera))
    piezas.append(C(f'{nm} · cabecero del cerco', a0 + CERCO - 0.002, b0 - 0.002,
                    a1 - CERCO + 0.002, b1 + 0.002, ztop, zc, madera))
    # tapajuntas a las dos caras, metidos 2 mm en el paramento
    for cara, bb, sg in (('interior', b0, -1), ('exterior', b1, 1)):
        bj0, bj1 = bb - sg * 0.002, bb + sg * TJ_VUELO
        for lado, aa, sa in (('izquierdo', a0, 1), ('derecho', a1, -1)):
            piezas.append(C(f'{nm} · tapajuntas {lado} {cara}',
                            aa - sa * (TAPAJUNTAS - 0.006), min(bj0, bj1),
                            aa + sa * 0.006, max(bj0, bj1), z0, zc + 0.008, madera))
        piezas.append(C(f'{nm} · tapajuntas superior {cara}',
                        a0 - TAPAJUNTAS + 0.006, min(bj0, bj1),
                        a1 + TAPAJUNTAS - 0.006, max(bj0, bj1),
                        zc + 0.006, zc + 0.006 + TAPAJUNTAS, madera))

    # hoja: nucleo hundido y bastidor por delante, que deja dos cuarterones
    la0, la1 = a0 + CERCO + HOLGURA, a1 - CERCO - HOLGURA
    lz0, lz1 = z0 + BAJO_PUERTA, ztop - HOLGURA
    bc = (b0 + b1) / 2
    n0, n1 = bc - NUCLEO_E / 2, bc + NUCLEO_E / 2
    h0, h1 = bc - HOJA_E / 2, bc + HOJA_E / 2
    piezas.append(C(f'{nm} · hoja nucleo', la0, n0, la1, n1, lz0, lz1, madera))
    for lado, aa, sa in (('izquierdo', la0, 1), ('derecho', la1, -1)):
        piezas.append(C(f'{nm} · hoja montante {lado}', aa, h0,
                        aa + sa * MONTANTE, h1, lz0, lz1, madera))
    ta0, ta1 = la0 + MONTANTE - 0.002, la1 - MONTANTE + 0.002
    zcerr = lz0 + ALTO_MANILLA
    for lado, zz0, zz1 in (('superior', lz1 - TRAV_SUP, lz1),
                           ('de la cerradura', zcerr - TRAV_CERR / 2, zcerr + TRAV_CERR / 2),
                           ('inferior', lz0, lz0 + TRAV_INF)):
        piezas.append(C(f'{nm} · hoja travesano {lado}', ta0, h0, ta1, h1, zz0, zz1, madera))

    # pernios en la jamba izquierda y manilla en el canto de la cerradura
    for i, zz in enumerate((lz0 + 0.240, (lz0 + lz1) / 2, lz1 - 0.240)):
        cx, cy = (la0, bc) if tumbada else (bc, la0)
        piezas.append(cilindro(f'{nm} · pernio {i + 1}', cx, cy, 0.009,
                               zz - 0.040, zz + 0.040, herraje, col, segs=20))
    am = la1 - MONTANTE / 2
    _manilla(C, D, am, h0, zcerr, -1, herraje, f'{nm} ·', col)
    _manilla(C, D, am, h1, zcerr, +1, herraje, f'{nm} ·', col)

    for ob in piezas:
        bisel(ob)
    return piezas


def _puerta_vidrio(s, col='Obra'):
    """La puerta de acceso: hoja de vidrio con bastidor de inox y tirador."""
    nm = s['nombre']
    x0, x1 = s['x0'], s['x1']
    y0, y1 = s['y0'], s['y1']
    z0, z1 = s['z0'], s['z1']
    inox, vid = MAT['inox'], MAT['vidrio']
    yc = (y0 + y1) / 2
    piezas = []
    # bastidor: zocalo alto, cabecero y dos montantes
    piezas.append(caja(f'{nm} · zocalo', x0, y0, x1, y1, z0, z0 + 0.140, inox, col))
    piezas.append(caja(f'{nm} · cabecero', x0, y0, x1, y1, z1 - 0.100, z1, inox, col))
    for lado, xx, sx in (('izquierdo', x0, 1), ('derecho', x1, -1)):
        piezas.append(caja(f'{nm} · montante {lado}', xx, y0, xx + sx * 0.050, y1,
                           z0 + 0.140 - SOLAPE, z1 - 0.100 + SOLAPE, inox, col))
    # el vidrio, mas fino y metido en el bastidor
    piezas.append(caja(f'{nm} · vidrio', x0 + 0.046, yc - 0.006, x1 - 0.046,
                       yc + 0.006, z0 + 0.136, z1 - 0.096, vid, col))
    # tirador vertical de tubo, separado 55 mm de la hoja
    xt = x0 + 0.110 if 'hoja 2' in nm else x1 - 0.110
    zt0, zt1 = z0 + 0.750, z0 + 1.650
    for cara, yb, sg in (('exterior', y0, -1), ('interior', y1, 1)):
        yt = yb + sg * 0.055
        piezas.append(cilindro(f'{nm} · tirador {cara}', xt, yt, 0.016, zt0, zt1,
                               inox, col, segs=20))
        for zz in (zt0 + 0.030, zt1 - 0.030):
            piezas.append(_cil_eje(f'{nm} · soporte del tirador {cara}',
                                   (xt, (yt + yb) / 2, zz), 0.010, 0.075, 'Y', inox, col))
    for ob in piezas:
        if ob.data.materials and ob.data.materials[0] is not vid:
            bisel(ob)
    return piezas


def carpinteria(j):
    """Rehace las puertas del plano con cerco, hoja de cuarterones y herrajes."""
    dinteles = {}
    for s in j['cajas']:
        nm = s['nombre'] or ''
        if 'dintel' in nm:
            dinteles[nm.split(' · ')[0]] = s
    n = 0
    for s in j['cajas']:
        nm = s['nombre'] or ''
        if '· hoja' not in nm:
            continue
        col = 'Planta alta' if s['tag'].startswith('14') else 'Obra'
        if s['mat'] == 'madera':
            _puerta_madera(s, dinteles.get(nm.split(' · ')[0]), col)
            n += 1
        elif s['mat'] == 'vidrio':
            _puerta_vidrio(s, col)
            n += 1
    return n


# ---------------------------------------------------- luz de la escalera
# Perfil de aluminio bajo el mamperlan de cada peldaño, con la tira metida
# entre los dos labios. El plano dibuja la escalera como cajas macizas
# apiladas, asi que el frente de cada peldaño es su contrahuella y ahi va el
# perfil. Un peldaño puede venir partido en dos cajas donde la escalera se
# estrecha: manda la que tiene la Y mas baja, que es la que se ve.
LED_RETRANQUEO = 0.060           # lo que se retira el perfil de cada costado
LED_LABIO = 0.005                # canto de los labios de aluminio
LED_ALTO = 0.020                 # alto de la tira
LED_BAJO = 0.025                 # del mamperlan al labio de arriba


def leds_escalera(j):
    """Una linea de led bajo el mamperlan de cada peldaño."""
    frentes = {}
    for s in j['cajas']:
        nm = s['nombre'] or ''
        if not nm.startswith('Peldaño'):
            continue
        a = frentes.get(nm)
        if a is None or s['y0'] < a['y0']:
            frentes[nm] = s
    n = 0
    for nm, s in sorted(frentes.items(), key=lambda kv: kv[1]['y0']):
        x0, x1 = s['x0'] + LED_RETRANQUEO, s['x1'] - LED_RETRANQUEO
        yf, zt = s['y0'], s['z1']
        z_alto = zt - LED_BAJO                       # cara baja del labio de arriba
        z_bajo = z_alto - LED_ALTO                   # cara alta del labio de abajo
        # los labios vuelan 12 mm y se meten 4 en la contrahuella
        for lado, za, zb in (('superior', z_alto, z_alto + LED_LABIO),
                             ('inferior', z_bajo - LED_LABIO, z_bajo)):
            caja(f'{nm} · labio {lado}', x0, yf - 0.012, x1, yf + SOLAPE, za, zb,
                 MAT['_perfil_led'], 'Luces')
        # la tira, retranqueada entre los labios: asi se ve la linea de luz y
        # no el punto, y no comparte plano con la contrahuella
        caja(f'{nm} · tira led', x0, yf - 0.006, x1, yf - 0.002, z_bajo, z_alto,
             MAT['_led_escalon'], 'Luces')
        n += 1
    return n


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
    # Pavimento del altillo, sobre el forjado. Va con la MISMA planta que el
    # forjado -E.FORJADO-, no con su rectangulo envolvente: el poligono tiene
    # recortado el hueco de la escalera (x 8,811..9,890 entre y 3,939 y 7,738)
    # y si aqui se pone una caja, el roble tapa el hueco y la escalera sube
    # contra un techo a 2,54. El forjado lo traia bien; el pavimento no.
    prisma('Pavimento planta alta', E.FORJADO, Z_PA - 0.018, Z_PA + 0.001,
           MAT['_suelo'], 'Planta alta')


def vestibulo():
    """El cubo de la entrada: paredes de obra y techo, con la puerta al fondo.

    Lo que hay delante de la hoja no es un retorno de escaparate: es una caja
    de obra abierta solo a la calle. El costado Este ya lo da el cuello de la
    medianera y el fondo lo cierra la propia puerta; aqui van el costado Oeste
    y el techo, que es lo que hace que la entrada sea un hueco de 2,06 x 2,10
    y no un agujero abierto hasta los cinco metros de la doble altura.
    """
    R = RETRANQUEO
    xp = R['x0'] - R['e_pared']              # trasdos del tabique del costado
    # Costado Oeste. Arranca medio milimetro por detras de la linea de fachada
    # -ahi tiene su cara el zocalo de piedra del escaparate- y baja del suelo
    # para que no se vea la junta con el pavimento.
    ob = caja('Vestíbulo · pared Oeste', xp, R['y0'] + DESPEGUE, R['x0'], R['y1'],
              -0.010, R['alto'], MAT['muro'])
    bisel(ob)
    # Techo del cubo: vuela 6 mm sobre el tabique para caparlo, se hunde 4 mm
    # en la cabeza de la puerta y se mete en el cuello de la medianera.
    ob = caja('Vestíbulo · techo', xp - 0.006, R['y0'] + 0.001,
              R['x1'] + SOLAPE, R['y1'] - DESPEGUE,
              R['alto'] - SOLAPE, R['alto'] + R['canto'], MAT['muro'])
    bisel(ob)


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
    """El mostrador, en el mismo liston de roble que las columnas.

    Iba en listones azzurro Napoli. Ahora lleva el mismo revestimiento que
    P1, P3 y P4 -roble, y con el mismo ancho de liston y la misma junta, 28
    y 16 mm- para que el local se lea con un solo lenguaje de madera. Abajo
    queda el retranqueo de 50 mm con la tira de LED.
    """
    mx0, mx1 = Q.MOSTRADOR_X
    my0, my1 = Q.MOSTRADOR_Y
    z0 = 0.050
    # La barra no es una pieza continua de 2,79. Solo hay mostrador de verdad
    # al Norte de y = 3,970, que es donde el plano pone la encimera a medida y
    # su tabla de roble. Al Sur estan las dos vitrinas, y alli no hay barra:
    # hay un frente de madera y nada mas, puesto para tapar el zocalo de las
    # vitrinas, que se quedan a la vista de la bandeja para arriba.
    #
    # Antes el frente subia a 0,900 de punta a punta y llevaba encima su canto
    # de roble tambien de punta a punta: sobre las vitrinas salia una tapa de
    # barra que no existe, y justo detras de ella asomaba el trasdos negro de
    # los listones. Ese era el pano negro de delante de las vitrinas.
    Y_MOSTRADOR = 3.970
    Z_BASE_VITRINA = 0.420      # coronacion del zocalo de la vitrina comprada
    for nm, ya, yb, z1, con_canto in (
            ('vitrinas', my0, Y_MOSTRADOR, Z_BASE_VITRINA, False),
            ('mostrador', Y_MOSTRADOR, my1, Q.H_ENCIMERA, True)):
        # fondo oscuro para que los huecos entre listones no se vean como agujeros
        caja(f'Frente de la barra · fondo {nm}', mx1 - 0.030, ya, mx1 - 0.020, yb,
             0.0, z1, MAT['_negro'])
        listones(f'Frente de la barra · liston {nm}', mx1 - 0.022, ya, mx1, yb,
                 z0, z1, MAT['_liston'], fondo=0.022, eje='y')
        # zocalo retranqueado y tira de LED que lame el suelo
        caja(f'Frente de la barra · zocalo {nm}', mx1 - 0.050, ya, mx1 - 0.022, yb,
             0.0, z0, MAT['_negro'])
        led = caja(f'Frente de la barra · LED {nm}', mx1 - 0.046, ya + 0.01,
                   mx1 - 0.030, yb - 0.01, 0.030, 0.042, MAT['_luz_calida'])
        led.visible_shadow = False
        if con_canto:
            # canto superior de madera: solo donde hay mostrador
            caja(f'Frente de la barra · canto {nm}', mx1 - 0.055, ya, mx1 + 0.012,
                 yb, z1, z1 + 0.042, MAT['mesa'])
    # Testa Norte del mostrador: el trasdos negro de los listones acababa a la
    # vista justo donde arranca la pared en L y se leia como una franja negra.
    # Se cierra con un remate blanco, que ademas continua la linea de la L.
    caja('Frente de la barra · remate Norte', mx1 - 0.062, my1 - 0.004,
         mx1 + 0.014, my1 + 0.014, 0.0, Q.H_ENCIMERA + 0.042,
         MAT['muro'])

    # Canto del forjado: en la referencia es una banda blanca lisa que no
    # sobresale nada por debajo del intrados. Antes colgaba 120 mm y ademas
    # iba en azzurro, que es justo al reves de lo que pide el cliente. Va
    # a tope contra el canto del forjado, sin solapar, para no dejar dos
    # caras inferiores en el mismo plano.
    caja('Canto del forjado Sur', 2.405, 3.907, 9.890, 3.939,
         Z_SOFITO, Z_PA - 0.001, MAT['_blanco_lacado'])
    # El canto Oeste da al paso de servicio y a la cocina: ahi no se forra.


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


def remate_vidrio_L():
    """Reborde blanco del vidrio de la pared en L.

    Un perfil fino que cierra el canto de arriba del vidrio y otro en la junta
    del vidrio con la fabrica de la L, que es como se remata de obra un pano
    de vidrio apoyado sobre un antepecho.
    """
    x0, x1 = 2.460, 2.500          # el pano del plano
    y0, y1 = 5.457, 8.927
    z_ab, z_ar = 1.220, Z_SOFITO      # el vidrio llega al techo
    e = 0.012                      # cuanto sobresale del vidrio
    h = 0.030                      # canto del perfil: fino
    m = MAT['_blanco_lacado']
    # el remate de arriba cuelga del techo, no lo atraviesa
    caja('Vidrio L · remate superior', x0 - e, y0, x1 + e, y1,
         z_ar - h, z_ar, m, 'Obra')
    caja('Vidrio L · remate inferior', x0 - e, y0, x1 + e, y1,
         z_ab - h * 0.5, z_ab + h * 0.5, m, 'Obra')
    for nm, ya, yb in (('Sur', y0, y0 + h), ('Norte', y1 - h, y1)):
        caja(f'Vidrio L · jamba {nm}', x0 - e, ya, x1 + e, yb,
             z_ab, z_ar - h, m, 'Obra')


def losas(nombre, x0, y0, x1, y1, z0, z1, mat, alto=0.72, junta=0.009,
          fondo=0.022, eje='x', col='Obra'):
    """Aplacado de losas de piedra, por hiladas y con junta abierta.

    Misma firma que listones para que el forro de una columna se arme igual
    con una cosa que con la otra: la losa ocupa todo el ancho de la cara y
    se apila en altura.

    mat puede ser una lista de materiales. Entonces cada hilada coge uno,
    y ademas sale un poco mas gruesa o mas fina y un pelin mas corta o mas
    larga que la de al lado: la piedra cortada no da todas las piezas
    iguales, y si salen iguales se ve que es un render. La semilla sale del
    nombre de la pieza, no de hash(), que cambia de una ejecucion a otra y
    dejaria cada vista con un despiece distinto.
    """
    import zlib
    rnd = random.Random(zlib.crc32(nombre.encode()))
    varios = isinstance(mat, (list, tuple))
    n = max(1, int(round((z1 - z0) / alto)))
    paso = (z1 - z0) / n
    obs = []
    for i in range(n):
        m = mat[rnd.randrange(len(mat))] if varios else mat
        j = junta * rnd.uniform(0.7, 1.35)
        f = fondo + (rnd.uniform(-0.0015, 0.0035) if varios else 0.0)
        za = z0 + paso * i + (j / 2 if i else 0.0)
        zb = z0 + paso * (i + 1) - (j / 2 if i < n - 1 else 0.0)
        if eje == 'x':
            obs.append(caja(f'{nombre} hilada {i + 1}', x0, y0, x1, y0 + f,
                            za, zb, m, col))
        else:
            obs.append(caja(f'{nombre} hilada {i + 1}', x0, y0, x0 + f, y1,
                            za, zb, m, col))
    for o in obs:
        bisel(o, 0.0022, segs=2)
    return obs


# Las cinco columnas del proyecto: caras que quedan a la vista y con que se
# forran. P2 -la pilastra del ventanal- y P5 -la de fachada- van en losa de
# piedra gris negro; las otras tres, en liston de roble. Y enteras: del
# pavimento al techo, no hasta el intrados de planta alta.
#   S = cara Sur (y0)   N = Norte (y1)   O = Oeste (x0)   E = Este (x1)
PILARES = (
    ('P1', 0.250, 4.759, 0.550, 5.357, 'SNE', 'liston'),   # machon del muro Oeste
    ('P2', 1.290, 1.561, 1.870, 2.011, 'SONE', 'losa'),    # pilastra del ventanal,
                                                           # forrada tambien por la
                                                           # cara Sur, que da a la calle
    ('P3', 5.670, 4.688, 6.320, 5.758, 'SNOE', 'liston'),  # exento, en la sala
    ('P4', 9.689, 4.708, 9.890, 5.309, 'SNO', 'liston'),   # machon de la medianera
    ('P5', 5.731, 0.000, 6.331, 1.000, 'SONE', 'losa'),    # pilar de fachada; la
                                                           # cara Norte solo la tapa
                                                           # el muro del cuello hasta
                                                           # x 5,980, el resto se ve
    # El machon de P5 no acaba en la columna: sigue hacia dentro con el muro
    # del cuello y la jamba del ventanal, y ese retorno se ve desde la sala y
    # desde el vestibulo. Salia en enlucido al lado de la losa. Se forra la
    # cara Norte de la jamba (y = 1,810) y todo el costado Este (x = 5,980)
    # de y 1,000 a 1,810, que es muro del cuello abajo y jamba arriba.
    ('P5i', 5.870, 1.000, 5.980, 1.810, 'ONE', 'losa'),    # retorno interior de P5
)


def pilar_escalera():
    """El perfil de acero que hay en obra al pie de la escalera.

    En la foto de obra es un montante gris vertical que sube del suelo hasta
    el intrados del forjado. Su cabeza muere justo en la ESQUINA ENTRANTE del
    altillo: el punto (8,811 / 3,939) donde el borde Sur del forjado se
    encuentra con el costado del hueco de la escalera. Es la esquina que de
    verdad necesita apoyo, y por eso el perfil esta ahi y no en otro sitio.

    En planta cae dentro del grueso del antepecho de la escalera -CAJA_ESC_PB,
    x 8,650..8,811-, arrimado a su extremo Sur. Como ese antepecho tiene el
    borde superior en rampante (1,209 en el arranque), el perfil solo asoma de
    ahi para arriba: desde la sala, el antepecho y el perfil se leen como una
    sola pilastra de 160 que sube del suelo al forjado. Por eso va enlucido
    como el antepecho y no forrado de roble: forrarlo era pegarle una caja de
    madera a un paño de yeso, que es justo lo que quedaba feo.

    Sostiene parte del techo y no se puede quitar.
    """
    # Caras coplanarias con el antepecho -la Sur y la Este-: se retiran un
    # DESPEGUE para que no peleen en el render. La cabeza se hunde un SOLAPE
    # en el forjado, que ahi si lo hay.
    x0, x1 = 8.651, 8.811 - DESPEGUE
    y0, y1 = 3.939 + DESPEGUE, 4.099
    ob = caja('Pilar de la escalera', x0, y0, x1, y1, 0.0, Z_SOFITO + SOLAPE,
              MAT['muro'])
    bisel(ob)
    return 1


def forro_pilares():
    """Forra las columnas de arriba abajo, cada una con lo suyo."""
    n = 0
    for tag, x0, y0, x1, y1, caras, tipo in PILARES:
        fondo = 0.026 if tipo == 'liston' else 0.022
        d = fondo + SOLAPE
        mat = MAT['_liston'] if tipo == 'liston' else MAT['_losa_piedra']
        poner_forro = (lambda *a, **k: listones(*a, fondo=d, **k)) if tipo == 'liston' \
            else (lambda *a, **k: losas(*a, fondo=d, **k))
        # las caras Sur y Norte se prolongan para cerrar la esquina cuando el
        # costado tambien va forrado; asi no queda un vacio de 26 mm en el
        # canto y los costados topan contra ellas sin solaparse
        ax0 = x0 - d if 'O' in caras else x0
        ax1 = x1 + d if 'E' in caras else x1
        if 'S' in caras:
            poner_forro(f'Forro {tag} Sur', ax0, y0 - d + SOLAPE, ax1, y0,
                        0.0, Z_TECHO, mat, eje='x')
            n += 1
        if 'N' in caras:
            poner_forro(f'Forro {tag} Norte', ax0, y1 - SOLAPE, ax1, y1 + d,
                        0.0, Z_TECHO, mat, eje='x')
            n += 1
        if 'O' in caras:
            poner_forro(f'Forro {tag} Oeste', x0 - d + SOLAPE, y0, x0, y1,
                        0.0, Z_TECHO, mat, eje='y')
            n += 1
        if 'E' in caras:
            poner_forro(f'Forro {tag} Este', x1 - SOLAPE, y0, x1 + d, y1,
                        0.0, Z_TECHO, mat, eje='y')
            n += 1
    return n


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
    # Las vitrinas miran al cliente, no al camarero. El objeto tiene el cristal
    # frontal, el panel de control y la rejilla del condensador en su cara -Y,
    # y las dos puertas correderas con sus tiradores en la +Y. Con -90 el
    # cristal daba al pasillo de servicio y el cliente veia las correderas por
    # detras. El cliente esta al Este, asi que van a +90.
    'V1': 90, 'V2': 90, 'B1': 90, 'B3': -90, 'B2': 0,
    # La chopera mira al Norte, no al Oeste. El objeto tiene el frente en -Y:
    # ahi estan los tres caños, las manetas y la rejilla donde va el vaso, y
    # la columna queda detras. Con -90 los caños apuntaban a la pared Oeste,
    # contra la que nadie puede ponerse: la tabla de P2 llega hasta ella. El
    # que tira la cerveza esta al Norte, en la calle de servicio, asi que el
    # frente tiene que girar 180 y quedar de cara a el.
    'B4': 180,
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
        # separacion del muro: el objeto se retira hacia su frente. Las
        # vitrinas no tienen muro detras -van embebidas en el mostrador, con
        # el pasillo de servicio por detras-, asi que a ellas no se les aplica:
        # solo empujaria el cristal por delante del canto de la barra.
        # Las vitrinas no llevan separacion de muro -no tienen muro detras- y
        # ademas van 20 mm hacia dentro, para que su cara de cristal enrase con
        # la del liston (x = 2,530) y el zocalo de la vitrina quede detras de
        # la madera, que es para lo que esta puesta.
        s = -0.020 if tag in ('V1', 'V2') else SEPARACION_MURO
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
        luz_expositor(tag, huecos[tag])
        puestos.append(tag)
    return puestos


def luz_expositor(tag, hueco):
    """Luz dentro de los muebles de puerta de cristal.

    Un expositor apagado es una caja negra: el LED que llevan los objetos de
    la biblioteca vale de cerca, pero en la escena hace falta un area dentro
    del mueble para que se lea el genero.
    """
    cfg = {'A7': (14.0, 0.34), 'V1': (12.0, 0.45), 'V2': (12.0, 0.45),
           'A5': (5.0, 0.30), 'K8': (0.0, 0.0), 'K9': (0.0, 0.0)}
    if tag not in cfg or cfg[tag][0] <= 0:
        return
    pot, tam = cfg[tag]
    x0, y0, z0, x1, y1, z1 = hueco
    n = 3 if (z1 - z0) > 1.2 else 1
    for i in range(n):
        z = z0 + (z1 - z0) * (i + 1) / (n + 0.6)
        lz = bpy.data.lights.new(f'{tag} luz interior {i + 1}', 'AREA')
        lz.shape = 'RECTANGLE'
        lz.size = max(0.12, min(x1 - x0, y1 - y0) * 0.7)
        lz.size_y = tam
        lz.energy = pot
        lz.color = (0.95, 0.97, 1.0)
        ob = bpy.data.objects.new(f'{tag} luz interior {i + 1}', lz)
        ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, z)
        ob.rotation_euler = (math.radians(180), 0, 0)
        coleccion('Luces').objects.link(ob)


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
    """Banco corrido contra el muro Norte, en la caja que fija el plano.

    equipamiento/mobiliario lo dibujan en x 2,530..7,400, y 8,357..8,957, con
    el asiento a 0,42 y el respaldo hasta 1,05. La cara interior del muro
    Norte es 8,957: no hay trasdosado.
    """
    x0, x1 = 2.530, 7.400
    y1 = 8.957
    y0 = 8.357
    obs = []
    base = caja('Sillon base', x0, y0, x1, y1, 0.0, 0.360, MAT['_negro'])
    bisel(base, 0.004)
    obs.append(base)
    # cojin de asiento por tramos, para que se lea el capitone
    n = int((x1 - x0) / 0.70)
    for i in range(n):
        a = x0 + (x1 - x0) * i / n
        b = x0 + (x1 - x0) * (i + 1) / n
        c = caja(f'Sillon cojin {i + 1}', a + 0.006, y0, b - 0.006, y1 - 0.10,
                 0.360, 0.420, MAT['sillon'])
        obs.append(blando(c, 0.030, 4, 1))
        r = caja(f'Sillon respaldo {i + 1}', a + 0.006, y1 - 0.100, b - 0.006, y1,
                 0.420, 1.050, MAT['sillon'])
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
                # La silla se construye con el respaldo en +Y, o sea mirando a
                # -Y con giro 0. Para que mire a la mesa hace falta
                #   sin(a) = dx/|d|  y  cos(a) = -dy/|d|,  es decir  a = atan2(dx, -dy).
                # Con -90 en vez de +90 salian las 29 sillas de espaldas a la mesa.
                dx, dy = cx - scx, cy - scy
                ang = math.degrees(math.atan2(dx, -dy))
                obs += silla(f'{tag} silla {i + 1}', scx, scy, ang,
                             telas[(k + i) % 2], col=col)
                n_sillas += 1
            if dz:
                for o in obs:
                    for v in o.data.vertices:
                        v.co.z += dz
    # El plano no lleva taburetes en el mostrador, asi que no se ponen: la
    # escena dibuja lo que hay proyectado, no lo que quedaria bonito.
    sillon_corrido()
    return n_sillas


# ========================================== 5. pared azzurro con el logo
# La pared que se ve a la derecha al entrar, antes de subir la escalera, es
# la MEDIANERA ESTE: su cara interior esta en x = 9,890 y el tramo que va del
# cuello (1,429) al primer peldano (3,579) queda libre. El cerramiento de la
# escalera -CAJA_ESC_PB, que el plano trae como panel- solo cubre de y 3,939
# a 7,738, asi que en ese tramo no hay muro donde pintar.
# Ese tramo es de doble altura: no hay forjado hasta y = 3,939.
PARED_LOGO = dict(x=9.890, y0=1.429, y1=3.579, z0=0.0, z1=Z_TECHO - 0.005)


def _medida_png(ruta):
    """Ancho y alto de un PNG, con Blender y no con Pillow.

    El Python que Blender lleva dentro no trae Pillow, y el vinilo hay que
    medirlo para sacar su proporcion. La imagen se carga y se suelta.
    """
    img = bpy.data.images.load(ruta, check_existing=False)
    w, h = img.size[0], img.size[1]
    bpy.data.images.remove(img)
    return w, h


def pared_logo():
    P = PARED_LOGO
    # la pared, pintada entera del azul del Napoli (2 mm por delante del muro)
    caja('Pared azzurro Napoli', P['x'] - 0.006, P['y0'], P['x'] + SOLAPE,
         P['y1'], P['z0'], P['z1'], MAT['_pared_napoli'])
    # La pared del plotter es la que va de la puerta a la escalera, y el
    # cuello de la medianera la dobla: al retranquear la entrada, el canto de
    # ese cuello -180 mm, de x 9,710 a 9,890- queda mirando a la sala justo al
    # lado de la puerta. Sin pintar salia como una franja de enlucido gris
    # entre la hoja y el azul. Se pinta tambien, y asi el plotter da la vuelta
    # a la jamba y la pared se lee de una pieza.
    R = RETRANQUEO
    caja('Pared azzurro Napoli · jamba', R['x1'], P['y0'] - SOLAPE,
         P['x'] - 0.006 + SOLAPE, P['y0'] + 0.006, P['z0'], P['z1'] - DESPEGUE,
         MAT['_pared_napoli'])
    if not os.path.exists(LOGO):
        print('   (sin logo: falta', LOGO, ')')
        return
    w_px, h_px = _medida_png(LOGO)
    ancho = 1.560                      # vinilo, centrado en los 2,15 del tramo
    alto = ancho * h_px / w_px
    cy, cz = (P['y0'] + P['y1']) / 2, 1.620
    x = P['x'] - 0.0095                # el vinilo, delante de la pintura
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
    # Aqui iban tres estantes de botellas, por simetria con la trasbarra.
    # No hay donde anclarlos: entre y = 5,100 y 7,300 el testero Oeste del
    # altillo es el vacio, el tabique del aseo no arranca hasta y = 7,509 y
    # el vidrio del borde muere en 3,560. Volaban sobre el hueco.


# ==================================================== 7. luminarias
def _dentro(poli, x, y):
    """Punto dentro de un poligono en planta (regla par-impar)."""
    dentro = False
    n = len(poli)
    for i in range(n):
        x0, y0 = poli[i]
        x1, y1 = poli[(i + 1) % n]
        if (y0 > y) != (y1 > y):
            xc = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            if x < xc:
                dentro = not dentro
    return dentro


def techo_sobre(x, y, z_pieza=0.0):
    """A que altura esta el techo sobre un punto.

    Donde hay altillo, el techo es el intrados del forjado (2,310). Donde el
    local es de doble altura -toda la franja Sur y la cocina- el techo es el
    del altillo (5,060). Los seis colgantes del proyecto caen justo en la
    doble altura, asi que colgarlos de 2,310 los dejaba con la varilla
    acabada en el aire.
    """
    if z_pieza >= Z_PA:
        return Z_TECHO
    R = RETRANQUEO
    if (R['x0'] <= x <= R['x1'] and R['y0'] <= y <= R['y1']
            and z_pieza < R['alto']):
        return R['alto']          # bajo el dintel del retranqueo de entrada
    return Z_SOFITO if _dentro(E.FORJADO, x, y) else Z_TECHO


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
    techo = techo_sobre(cx, cy, z_borde)
    caida = techo - z1
    # caidas largas van de cable, no de varilla rigida: 3,4 m de tubo de 8 mm
    # no se sostienen y ademas cantan
    r = 0.0035 if caida > 1.5 else 0.008
    cilindro(f'{nombre} suspension', cx, cy, r, z1, techo, MAT['carp'], col, 16)
    cilindro(f'{nombre} floron', cx, cy, 0.052, techo - 0.018, techo,
             MAT['carp'], col, 24)
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
            # Un empotrado necesita un techo donde empotrarse. Los cuatro de
            # la fila x = 1,10 caen fuera del forjado, en la doble altura de
            # la cocina, y quedaban flotando a 2,31 con cinco metros de aire
            # encima. La cocina ya lleva sus pantallas suspendidas.
            if abs(techo_sobre(x, y, s['z1']) - s['z1']) > 0.030:
                continue
            empotrado(nm, x, y, s['z1'])
        n += 1
    # el altillo necesita su propia luz: el plano no la trae
    for i, (x, y) in enumerate(((3.85, 4.80), (3.85, 6.20), (7.54, 5.43))):
        luminaria_colgante(f'Colgante PA {i + 1}', x, y, Z_PA + 1.700)
    # contra la cara de la celosia (y = 8,720), no a 120 mm de ella
    for i, (x, y) in enumerate(((2.90, 8.722), (5.90, 8.722))):
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


def _elegir_lod(disponibles, lod):
    """Los modelos de Poly Haven traen varios niveles de detalle.

    Un arbol en LOD0 son 2-4 millones de triangulos: puesto diez veces en la
    calle son 26 millones y el render se va a las nubes. De cerca hace falta
    el LOD0; para el arbolado de la calle, el LOD1 es indistinguible.
    """
    nombres = [n for n in disponibles if 'geometry_nodes' not in n]
    if lod <= 0:
        return [n for n in nombres if '_LOD' not in n or n.endswith('_LOD0')]
    suf = f'_LOD{lod}'
    con = [n for n in nombres if n.endswith(suf)]
    sin = [n for n in nombres if '_LOD' not in n]
    return (con + sin) or [n for n in nombres if n.endswith('_LOD0')]


def importar(aid, nombres=None, lod=0):
    """Trae un modelo CC0 de Poly Haven y lo deja fuera de escena, de molde."""
    clave = (aid, lod)
    if clave in _importados:
        return _importados[clave]
    ruta = os.path.join(PH, aid, f'{aid}.blend')
    if not os.path.exists(ruta):
        print(f'   (falta el modelo {aid})')
        _importados[clave] = []
        return []
    antes = set(bpy.data.objects.keys())
    with bpy.data.libraries.load(ruta, link=False) as (src, dst):
        elegidos = _elegir_lod(src.objects, lod)
        dst.objects = [n for n in elegidos if nombres is None or n in nombres]
    obs = [o for o in bpy.data.objects if o.name not in antes and o.type == 'MESH']
    _recolocar_texturas(aid)
    molde = coleccion('_moldes')
    for o in obs:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        molde.objects.link(o)
        # el molde no se renderiza: solo esta para copiarlo
        o.hide_render = True
        o.hide_viewport = True
    _importados[clave] = obs
    return obs


def _recolocar_texturas(aid):
    """Los .blend de Poly Haven apuntan a texturas .exr y el descargador las
    trae en png/jpg: sin esto los modelos pierden rugosidad y normal."""
    d2 = os.path.join(PH, aid, 'textures_2k')
    d = d2 if (MT.DOS_K and os.path.isdir(d2)) else os.path.join(PH, aid, 'textures')
    if not os.path.isdir(d):
        return
    hay = os.listdir(d)
    for im in bpy.data.images:
        fp = bpy.path.abspath(im.filepath)
        if not fp:
            continue
        base = os.path.splitext(os.path.basename(fp))[0]
        if os.path.exists(fp) and os.path.dirname(fp) == d:
            continue
        for f in hay:
            if os.path.splitext(f)[0] == base:
                im.filepath = os.path.join(d, f)
                im.reload()
                break


def poner(aid, x, y, z, escala=1.0, giro=0.0, col='Decoracion', nombres=None,
          lod=0, altura=None):
    """Copia enlazada de un modelo importado, apoyada en (x, y, z).

    Con `altura` se escala a esa altura real en metros, que es lo unico
    fiable: los modelos de Poly Haven vienen a su tamano natural y un
    jacaranda mide 20 m, asi que un factor a ojo se va de madre.
    """
    molde = importar(aid, nombres, lod)
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
    if altura:
        alto = max(1e-6, hi[2] - lo[2])
        escala = altura / alto
    import mathutils
    M = (mathutils.Matrix.Translation((x, y, z))
         @ mathutils.Matrix.Rotation(math.radians(giro), 4, 'Z')
         @ mathutils.Matrix.Scale(escala, 4)
         @ mathutils.Matrix.Translation((-cx, -cy, -lo[2])))
    out = []
    for o in molde:
        c = o.copy()                      # malla enlazada: no duplica memoria
        c.matrix_world = M @ o.matrix_world
        c.hide_render = False
        c.hide_viewport = False
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
    # La balda del A6 esta en z 1,800 y va de y 2,884 a 4,134 (medido sobre el
    # objeto montado). Las botellas iban a 1,855 y repartidas de 2,30 a 4,38:
    # flotaban 55 mm y cuatro de las nueve se salian de la balda por los topes.
    z_est = 1.798                              # 2 mm dentro de la balda
    for i in range(9):
        y = 2.95 + i * 0.14
        botella(f'Botella estante {i + 1}', 0.42, y, z_est,
                alto=0.28 + 0.06 * ((i * 7) % 3) / 2)
    # Los tarros arrancaban en y = 2,45 y la balda no empieza hasta 2,884:
    # los dos primeros colgaban en el aire delante del estante.
    for i in range(4):
        tarro(f'Tarro pasta {i + 1}', 0.62, 3.05 + i * 0.30, z_est, alto=0.20 + 0.03 * (i % 2))
    # tazas de espresso boca abajo sobre la cafetera y la mesada
    for i in range(6):
        taza(f'Taza barra {i + 1}', 0.40 + 0.11 * (i % 3), 4.20 + 0.12 * (i // 3), 0.905)
    # ---- mostrador: lo que ve el cliente
    mx1 = Q.MOSTRADOR_X[1]
    z_tabla = Q.H_ENCIMERA + 0.040
    # La tabla del mostrador va de y 3,97 a 4,76 y lleva en medio el soporte
    # del TPV (B3: x 2,05..2,25, y 4,17..4,42). La cesta estaba justo encima
    # de el -la tablet salia de dentro del mimbre- y la tercera copa caia 20 mm
    # por fuera del canto Norte. Cada cosa a su franja libre: la cesta al Norte
    # del TPV, el jarron al Sur y las copas al filo Este.
    poner('wicker_basket_01', 2.12, 4.60, z_tabla, escala=0.85, giro=18)
    poner('ceramic_vase_01', 2.20, 4.08, z_tabla, escala=0.9, giro=-25)
    for i in range(3):
        copa(f'Copa mostrador {i + 1}', mx1 - 0.16, 4.44 + i * 0.09, z_tabla)
    # ---- botellero sobre la vitrina y aceite en el paso
    poner('jug_01', 0.45, 4.62, 0.905, escala=1.0, giro=35)
    poner('metal_jug', 0.66, 4.60, 0.905, escala=0.9, giro=-15)
    # ---- plantas: terracota, el verde de la trattoria
    # delante de la puerta del baño no va ninguna: estorba el paso. Y delante
    # de la pared azzurro tampoco: ahi va la pared y el logo, nada mas.
    # Queda una sola, y es la unica que estaba en suelo libre. Las otras tres
    # estaban metidas dentro de algo, que es como no estar:
    #   (2,24 · 3,15) dentro de la vitrina V1 y de su motor
    #   (2,58 · 8,45) dentro del asiento del sillon corrido
    #   (7,72 · 8,45) dentro del baño de planta baja
    poner('potted_plant_01', 2.70, 6.85, 0.0, altura=0.75, giro=60)
    # ---- fruta y pan en la mesa de trabajo de la cocina
    # Iban a la cota de la barra (0,900) y en x = 1,30 / 1,75, que es el
    # pasillo entre el fregadero (muere en x = 0,85) y la mesa refrigerada
    # (arranca en 1,83): no habia nada debajo y colgaban en el aire. Van sobre
    # la K10, que es la mesa de trabajo, y su tablero esta a 0,850, no a 0,900.
    z_k10 = 0.850
    poner('wooden_bowl_01', 2.10, 6.30, z_k10, escala=1.0, giro=25)
    for i, aid in enumerate(('food_apple_01', 'food_lime_01', 'food_pomegranate_01')):
        poner(aid, 2.06 + 0.05 * i, 6.28 + 0.04 * (i % 2), z_k10 + 0.045,
              escala=1.0, giro=i * 55)
    poner('wicker_basket_02', 2.10, 6.85, z_k10, escala=0.9, giro=-12)
    # ---- la pared del sillon corrido: solo cuadros, repartidos
    for i, x in enumerate((3.05, 3.95, 4.85, 6.10, 7.00)):
        alto = 0.560 if i % 2 == 0 else 0.460
        cuadro(f'Cuadro {i + 1}', x, 8.957, 1.700, alto * 0.78, alto, '-Y')
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
            # La de cowork es 1,00 x 2,40 con el lado largo en Y, no en X. Las
            # tres tazas se repartian en cx -0,7 / 0 / +0,7, o sea a lo ancho:
            # la primera y la tercera caian 200 mm por fuera del tablero y
            # colgaban sobre el suelo. Se reparten por el lado largo, sea cual
            # sea, y metidas 250 mm de cada testero.
            largo_x = (x1 - x0) >= (y1 - y0)
            a0, a1 = (x0, x1) if largo_x else (y0, y1)
            for i in range(3):
                t = a0 + 0.25 + (a1 - a0 - 0.50) * i / 2
                tx, ty = (t, cy + 0.20) if largo_x else (cx + 0.20, t)
                taza(f'Taza PA {tag} {i}', tx, ty, z, col='Planta alta')
            poner('ceramic_vase_02', cx, cy, z, escala=0.85, giro=20, col='Planta alta')
        else:
            poner('wicker_basket_01', cx, cy, z, escala=0.7, giro=-20, col='Planta alta')
            for i in range(4):
                copa(f'Copa PA {i}', cx + 0.22 * math.cos(i * 1.57),
                     cy + 0.22 * math.sin(i * 1.57), z, col='Planta alta')
    # Las botellas y la ceramica iban sobre los estantes del testero Oeste,
    # que se han quitado por no tener pared donde anclarse.


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
    """La calle entera: acera, calzada, la manzana de enfrente, arbolado,
    mobiliario urbano y coches aparcados.

    Por un escaparate de doble altura se ve la ciudad de cerca, asi que no
    vale con el HDRI: el HDRI pone el cielo y la luz, y esto pone la calle.
    """
    import ciudad as C
    rnd = random.Random(31)
    C.suelo_urbano(CIUDAD_API, MAT)
    C.edificios(CIUDAD_API, MAT, rnd)

    # arbolado en los alcorques de nuestra acera
    for i, x in enumerate(C.ALCORQUES):
        aid = 'jacaranda_tree' if (i % 2 and _hay('jacaranda_tree')) else 'tree_small_02'
        poner(aid, x, C.Y_ACERA + 0.90, C.H_BORDILLO - 0.02, altura=7.2 + 0.8 * (i % 2),
              giro=i * 53, col='Ciudad', lod=1)
    # arbolado de la acera de enfrente, mas lejos y mas suelto
    for i, x in enumerate((-9.0, 14.0)):
        poner('tree_small_02', x, C.Y_ACERA_OP - 1.20, C.H_BORDILLO - 0.02,
              altura=6.4 + 0.9 * (i % 2), giro=i * 71, col='Ciudad', lod=1)

    # mobiliario urbano
    for i, x in enumerate((-5.2, 2.0, 8.6, 15.2, 21.8)):
        C.farola(CIUDAD_API, MAT, x, C.Y_ACERA + 0.55, nombre=f'Farola {i + 1}')
    for i, x in enumerate((-2.6, -1.9, 3.4, 4.1, 9.8, 10.5, 16.2, 16.9)):
        C.bolardo(CIUDAD_API, MAT, x, C.Y_ACERA + 0.42, f'Bolardo {i + 1}')
    for aid, x, y, g in (('metal_trash_can', 6.10, C.Y_ACERA + 0.70, 20),
                         ('fire_hydrant', -6.40, C.Y_ACERA + 0.60, -30),
                         ('painted_wooden_bench', 13.20, C.Y_ACERA + 0.95, 180),
                         ('modular_street_seating', -9.60, C.Y_ACERA + 1.05, 0)):
        if _hay(aid):
            poner(aid, x, y, C.H_BORDILLO, escala=1.0, giro=g, col='Ciudad')

    # La terraza no esta en el proyecto: la acera se deja libre.

    # coches aparcados en la banda, y un par en el otro sentido
    for i, x in enumerate((-7.6, -2.0, 3.8, 9.8, 16.2, 21.8)):
        if i == 3:
            continue                       # hueco libre, que no parezca un catalogo
        poner_bmw(x, C.Y_APARCA + 0.95, 1.5 - 3.0 * (i % 2),
                  COLORES_COCHE[i % len(COLORES_COCHE)], f'Coche {i + 1}')
    for i, x in enumerate((-11.4, 6.6, 18.8)):
        poner_bmw(x, C.Y_ACERA_OP + 2.05, 180 + 2.0 * (i % 2),
                  COLORES_COCHE[(i + 3) % len(COLORES_COCHE)], f'Coche op {i + 1}')


def acera_corta():
    """Para las vistas que no ven la calle: acera y calzada y nada mas.

    Montar la manzana entera, los arboles y los coches cuesta 6 millones de
    triangulos y 3 GB; si por la camara no se ve la calle, no compensa.
    """
    import ciudad as C
    caja('Acera', -16.0, C.Y_ACERA, 26.0, C.Y_FACHADA + 0.4, 0.0, C.H_BORDILLO,
         MAT['_acera'], 'Ciudad')
    caja('Calzada', -16.0, -14.0, 26.0, C.Y_ACERA - 0.18, -0.130, -0.002,
         MAT['_asfalto'], 'Ciudad')
    caja('Bordillo', -16.0, C.Y_ACERA - 0.18, 26.0, C.Y_ACERA, -0.120,
         C.H_BORDILLO, MAT['piedra'], 'Ciudad')


# ---------------------------------------------------------------- coches
# Poly Haven no tiene coches (521 modelos, comprobado contra su API en vivo)
# y ambientCG tampoco (400). Los de gazebo_models eran low-poly y no daban el
# pego. El bueno esta en los ficheros de demostracion de Blender: la escena
# de referencia BMW27 trae un BMW 1M completo -carroceria con subdivision,
# lunas, llantas con el rodel, discos de freno, opticas con ojos de angel,
# pilotos, parrilla, espejos, escape, matricula e interior- en 188.000
# triangulos. La coleccion se llama '1M' y hay que traerla entera, porque las
# ruedas y los frenos son empties que instancian colecciones.
#   https://download.blender.org/demo/test/BMW27_2.blend.zip
BMW = os.path.join(SCRATCH, 'coches', 'bmw27', 'bmw27', 'bmw27_cpu.blend')
BMW_LARGO = 4.55                 # a lo que se escala el conjunto

# la flota de la calle: (color de carroceria, si lleva las lunas tintadas)
COLORES_COCHE = ['2E3238', 'DCDCD8', '1E3050', '9AA0A6', '6E1714', '35403A']
_BMW_CAJA = []                   # la caja del modelo se mide una vez y vale para todos


def _caja_instancias(col):
    """Caja envolvente de una coleccion contando la geometria instanciada.

    Las ruedas y los frenos son empties que instancian colecciones: su
    geometria no aparece en bound_box, solo en el depsgraph evaluado.
    """
    import mathutils
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    dentro = {o.name for o in col.all_objects}
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for inst in dg.object_instances:
        o = inst.object
        if o is None or o.type != 'MESH':
            continue
        src = inst.parent if inst.is_instance else o
        if src is None or src.original.name not in dentro:
            continue
        for c in o.bound_box:
            w = inst.matrix_world @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], w[i])
                hi[i] = max(hi[i], w[i])
    return lo, hi


def _congelar(col):
    """Deja la coleccion en mallas sueltas con su sitio de ahora.

    El BMW viene aparejado: la carroceria lleva modificador de armadura y las
    ruedas y los frenos cuelgan de ella con restricciones de suelo
    (la suspension). Mientras ese aparejo esta vivo, mover la matriz del
    objeto raiz no arrastra la geometria evaluada -las restricciones la
    vuelven a clavar donde estaba- y el coche acaba descolocado. Como la pose
    esta en reposo, quitar el aparejo no cambia ni un milimetro (comprobado:
    la caja envolvente sale identica antes y despues), y a cambio deja el
    conjunto como mallas independientes que se pueden colocar con una matriz.
    """
    bpy.context.view_layer.update()
    mw = {o.name: o.matrix_world.copy() for o in col.all_objects}
    for o in list(col.all_objects):
        o.constraints.clear()
        o.animation_data_clear()          # los drivers apuntaban a las restricciones
        for m in list(getattr(o, 'modifiers', [])):
            if m.type == 'ARMATURE':
                o.modifiers.remove(m)
    for o in list(col.all_objects):
        o.parent = None
        o.matrix_world = mw[o.name]
    for a in [o for o in col.all_objects if o.type == 'ARMATURE']:
        bpy.data.objects.remove(a, do_unlink=True)


def poner_bmw(x, y, giro, hexcol, nombre, col='Ciudad', z_apoyo=-0.010, subdiv=1):
    """Trae el BMW de la escena de demostracion y lo planta en la calle.

    Se importa una vez por coche en vez de duplicar: son 188.000 triangulos,
    sale barato, y asi cada uno lleva su propio material de carroceria y se
    le puede cambiar el color sin tocar a los demas.

    Queda con el eje largo en X mirando a +X, centrado en (x, y) y apoyado en
    la rasante: el largo se mide sobre la caja real -ya instanciada- y no
    sobre una constante, asi que el coche se apoya solo aunque cambie el
    modelo. z_apoyo es la cota de la banda de rodadura; por defecto 8 mm por
    debajo del asfalto (-0,002) para que la huella del neumatico se aplaste
    contra el suelo en vez de dejar una linea de luz.
    """
    if not os.path.exists(BMW):
        print('   (falta el BMW: descarga BMW27_2.blend.zip)')
        return []
    import mathutils
    antes = set(bpy.data.collections.keys())
    with bpy.data.libraries.load(BMW, link=False) as (src, dst):
        dst.collections = ['1M']
    nueva = next((c for c in bpy.data.collections if c.name not in antes), None)
    if nueva is None:
        return []
    nueva.name = f'{nombre}'
    coleccion(col).children.link(nueva)
    _congelar(nueva)

    # El modelo viene con subdivision de render hasta nivel 3: cada nivel
    # multiplica por cuatro, y ocho coches asi se comen la memoria antes de
    # empezar a trazar rayos. A veinte metros de la camara, el nivel 1 ya no
    # deja ver facetas en la chapa.
    for o in nueva.all_objects:
        for m in getattr(o, 'modifiers', []):
            if m.type == 'SUBSURF':
                m.render_levels = min(m.render_levels, subdiv)
                m.levels = m.render_levels

    # Color de la carroceria. Ojo: la chapa no es un Principled, es una mezcla
    # de dos BsdfAnisotropic (capa de color rugosa + barniz liso) unidas por
    # un LayerWeight. Hay que tocar el Color del que hace de capa de color,
    # que es el de rugosidad alta; el otro es el barniz y se deja.
    rgb = MT.srgb(hexcol)
    for o in nueva.all_objects:
        for sl in getattr(o, 'material_slots', []):
            m = sl.material
            if not m or not m.use_nodes:
                continue
            if m.name.split('.')[0] not in ('CarShellNew', 'BMWWhite', 'BMWSilver'):
                continue
            anis = [n for n in m.node_tree.nodes
                    if n.bl_idname == 'ShaderNodeBsdfAnisotropic']
            if not anis:
                continue
            capa = max(anis, key=lambda n: n.inputs['Roughness'].default_value)
            capa.inputs['Color'].default_value = (*rgb, 1)

    # medir la caja obliga a evaluar el depsgraph entero; como todos los
    # coches salen del mismo fichero, se mide con el primero y se guarda.
    if not _BMW_CAJA:
        _BMW_CAJA.extend(_caja_instancias(nueva))
    lo, hi = _BMW_CAJA
    k = BMW_LARGO / (hi.x - lo.x)
    cx, cy = (lo.x + hi.x) / 2, (lo.y + hi.y) / 2
    M = (mathutils.Matrix.Translation((x, y, z_apoyo - k * lo.z))
         @ mathutils.Matrix.Rotation(math.radians(giro), 4, 'Z')
         @ mathutils.Matrix.Scale(k, 4)
         @ mathutils.Matrix.Translation((-cx, -cy, 0.0)))
    obs = list(nueva.all_objects)
    for o in obs:
        o.matrix_world = M @ o.matrix_world
    return obs


def _hay(aid):
    return os.path.exists(os.path.join(PH, aid, f'{aid}.blend'))


class _CiudadAPI:
    """Puente para que ciudad.py use las primitivas de la escena."""
    caja = staticmethod(lambda *a, **k: caja(*a, **k))
    cilindro = staticmethod(lambda *a, **k: cilindro(*a, **k))
    bisel = staticmethod(lambda *a, **k: bisel(*a, **k))
    girar = staticmethod(lambda *a, **k: girar(*a, **k))
    malla = staticmethod(lambda *a, **k: malla_libre(*a, **k))
    sustraer = staticmethod(lambda *a, **k: sustraer(*a, **k))
    prisma = staticmethod(lambda *a, **k: prisma(*a, **k))


CIUDAD_API = _CiudadAPI()


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


def camara_orto(nombre, ojo, mira, escala, despl=(0.0, 0.0)):
    """Camara ortografica, para plantas y axonometrias."""
    cam = bpy.data.cameras.new(nombre)
    cam.type = 'ORTHO'
    cam.ortho_scale = escala
    cam.clip_start = 0.01
    cam.clip_end = 300.0
    cam.shift_x, cam.shift_y = despl
    ob = bpy.data.objects.new(nombre, cam)
    coleccion('Camaras').objects.link(ob)
    d = Vector(mira) - Vector(ojo)
    ob.location = ojo
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob


def ocultar_sobre(z, salvo=()):
    """Esconde del render lo que esta por encima de una cota.

    Es lo que convierte la escena en una planta: se quita el techo y lo que
    estorba, sin tocar la geometria.
    """
    n = 0
    for ob in bpy.data.objects:
        if ob.type not in ('MESH', 'LIGHT') or any(k in ob.name for k in salvo):
            continue
        if ob.type == 'LIGHT':
            continue
        zmin = min((ob.matrix_world @ Vector(c)).z for c in ob.bound_box)
        if zmin >= z:
            ob.hide_render = True
            n += 1
    return n


def mostrar_todo():
    for ob in bpy.data.objects:
        ob.hide_render = False


# ojo, mira, lente: las vistas que cuentan el local
VISTAS = {
    # ---------------------------------------------------------- planta baja
    # la barra en diagonal, con el mostrador huyendo y la trasbarra al fondo
    'barra':        ((4.90, 1.95, 1.520), (1.35, 4.30, 1.060), 24.0),
    # el mostrador de frente, desde la sala
    'barra_frente': ((4.35, 3.15, 1.480), (2.10, 3.35, 1.180), 30.0),
    # desde dentro de la barra, el punto de vista del camarero
    'trasbarra':    ((1.42, 2.35, 1.560), (1.05, 4.70, 1.150), 22.0),
    # la sala desde la entrada, con el pilar forrado y la escalera
    'sala':         ((8.75, 2.10, 1.600), (4.10, 6.30, 1.220), 21.0),
    # la fila del sillon corrido, contra el muro Norte
    'sillon':       ((7.90, 6.20, 1.520), (3.20, 8.30, 1.150), 24.0),
    # el hueco central entre la barra y el pilar
    'sala_centro':  ((6.90, 7.60, 1.560), (3.30, 3.90, 1.200), 20.0),
    # desde dentro hacia el escaparate de doble altura
    'escaparate':   ((4.60, 6.30, 1.580), (6.10, 1.30, 1.900), 24.0),
    # la entrada, nada mas cruzar la puerta. Antes la camara estaba en
    # y = 1,15, que ahora cae DENTRO del retranqueo: la vista salia entera a
    # traves del vidrio de la puerta, velada de reflejos. Se pasa al otro
    # lado del umbral (y = 1,429).
    'entrada':      ((8.62, 1.92, 1.620), (4.60, 5.40, 1.400), 20.0),
    # la pared azzurro con el logo, de frente
    'logo':         ((6.35, 1.95, 1.680), (9.88, 2.78, 1.470), 26.0),
    # La escalera desde la sala: el tramo entero subiendo contra la medianera
    # Este, con la pared del plotter debajo. La camara se queda al Sur de
    # y = 3,939, que es donde arranca el forjado del altillo: mas al Norte el
    # techo baja a 2,310 y el encuadre se cierra.
    'escalera_sala': ((8.05, 1.95, 1.640), (9.35, 6.30, 1.500), 21.0),
    'escalera_sala_b': ((7.20, 2.40, 2.050), (9.30, 5.60, 1.100), 24.0),
    # El mismo punto de vista que la foto de obra: al pie del tramo, a la
    # altura de los ojos y mirando hacia arriba, para ver el pilar forrado
    # junto al arranque y el antepecho de la planta alta.
    'escalera_pilar': ((8.55, 2.25, 1.620), (9.30, 6.20, 1.950), 19.0),
    # La escalera de costado: alzado del tramo. La camara mira en +X desde la
    # sala, por debajo del forjado, asi que el tramo sale de perfil -la linea
    # de peldaños y lo que haya sobre ella- en vez de en escorzo. Ojo: el
    # costado Oeste lo cierra CAJA_ESC_PB, un panel cuyo borde superior sigue
    # el rampante (1,209 en el arranque, 2,310 a partir de y 5,84), asi que
    # desde la sala solo se ve el tramo alto. El alzado limpio sale cortando
    # por x = 8,60, no desde aqui.
    'escalera_costado': ((5.20, 5.70, 1.560), (9.35, 5.70, 1.180), 35.0),
    # el arranque de la escalera, con la linea de led de cada peldaño.
    # La camara anterior -(7,35 / 5,40) mirando a (9,35 / 6,60)- encuadraba
    # el costado ciego de la escalera: salia un paño de enlucido y nada mas.
    'escalera':     ((8.10, 2.55, 1.180), (9.40, 5.60, 0.480), 30.0),
    # La barra entera por dentro, mirando al Sur hacia la chopera: es el plano
    # inverso de 'trasbarra', por la misma calle de servicio (x 0,85..1,90),
    # desde la boca Norte. A la izquierda la mesada con la cafetera y la
    # balda; a la derecha las vitrinas; al fondo la columna de 3 grifos sobre
    # la tabla de P2, con los barriles debajo y el ventanal Sur detras.
    'chopera':      ((1.40, 5.60, 2.100), (1.15, 2.10, 0.950), 24.0),
    # la cocina desde dentro, con la campana y la linea de coccion
    'cocina':       ((2.16, 5.90, 1.600), (1.05, 8.70, 1.120), 21.0),
    # la cocina desde el paso de servicio, con la mampara en primer plano
    'cocina_paso':  ((2.95, 4.95, 1.580), (1.30, 7.60, 1.250), 24.0),
    # panoramica general desde la esquina de entrada
    'general':      ((9.30, 1.70, 2.150), (3.40, 6.60, 1.250), 18.0),
    # ---------------------------------------------------------- planta alta
    'alta':         ((8.45, 6.95, Z_PA + 1.580), (3.55, 5.60, Z_PA + 1.120), 20.0),
    'alta_cowork':  ((6.60, 6.80, Z_PA + 1.540), (3.60, 5.00, Z_PA + 1.100), 24.0),
    'alta_redonda': ((4.90, 4.80, Z_PA + 1.540), (7.60, 5.60, Z_PA + 1.120), 26.0),
    # asomado al vacio, mirando la planta baja
    'alta_vacio':   ((3.35, 5.20, Z_PA + 1.620), (5.60, 2.20, 0.900), 22.0),
    # el desembarco de la escalera
    'alta_escalera':((8.20, 8.10, Z_PA + 1.580), (4.60, 5.40, Z_PA + 1.150), 21.0),
    # ------------------------------------------------------------- exterior
    # la fachada desde la acera de enfrente
    'fachada':      ((6.20, -9.20, 1.700), (5.60, 1.60, 2.600), 28.0),
    # la calle, con el local a un lado
    'calle':        ((-3.80, -5.40, 1.650), (12.00, -2.60, 2.000), 24.0),
}

# plantas y axonometrias: camara ortografica y recorte por cota
#   nombre: (ojo, mira, escala_orto, cota_de_recorte)
ORTOS = {
    'planta_baja':  ((5.10, 5.30, 14.0), (5.10, 5.30, 0.0), 11.4, 2.28),
    'planta_alta':  ((6.15, 6.45, 16.0), (6.15, 6.45, Z_PA), 9.0, Z_PA + 2.30),
    'axonometrica': ((-7.0, -8.5, 13.5), (5.10, 5.30, 1.20), 17.0, 2.60),
    'axono_alta':   ((-5.0, -6.5, 15.5), (6.15, 6.45, Z_PA + 1.1), 13.0, Z_PA + 2.35),
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


# vistas desde las que se ve la calle: solo en esas se monta la ciudad
VE_LA_CALLE = {'escaparate', 'fachada', 'calle', 'entrada', 'general', 'sala',
               'barra', 'sala_centro', 'alta_vacio', 'axonometrica', 'axono_alta',
               'planta_baja', 'barra_frente'}


def construir(spp, ancho, alto, con_decoracion=True, con_glare=False,
              con_ciudad=True):
    global MAT
    sc = escena_nueva(spp, ancho, alto)
    MAT = MT.construir()
    print('  materiales:', len(MAT), flush=True)
    if MT.sin_textura:
        # Un material sin su mapa de color no rompe nada: sale liso. El render
        # termina, parece correcto y esta mal. Mejor pararlo.
        print('\n  *** SIN TEXTURA: ' + ', '.join(sorted(set(MT.sin_textura))),
              flush=True)
        print('  Los mapas no estan en', PH, flush=True)
        print('  Hay que bajarlos:  python preparar_activos.py\n', flush=True)
        sys.exit(2)
    n, j = arquitectura()
    print('  obra:', n, 'solidos', flush=True)
    print('  puertas:', carpinteria(j), flush=True)
    suelos_y_techos()
    vestibulo()
    frente_barra()
    print('  caras de columna forradas:', forro_pilares(), flush=True)
    print('  pilar de la escalera:', pilar_escalera(), flush=True)
    cocina_inox()
    remate_vidrio_L()
    pared_logo()
    planta_alta()
    puestos = aparatos(j)
    print('  aparatos 1:1:', len(puestos), '/', len(TAGS_BIBLIOTECA), flush=True)
    ns = mobiliario()
    print('  mobiliario:', ns, 'sillas', flush=True)
    nl = luces(j)
    print('  luminarias del plano:', nl, flush=True)
    print('  led en peldaños:', leds_escalera(j), flush=True)
    mundo()
    if con_ciudad:
        exterior()
    else:
        acera_corta()
    if con_decoracion:
        decoracion()
        caracter_italiano()
        print('  decoracion puesta', flush=True)
    if con_glare:
        compositor()
    else:
        bpy.context.scene.use_nodes = False
    return sc


def render(vista, salida, spp, ancho, alto, rapido=False):
    sc = bpy.context.scene
    mostrar_todo()
    if vista in ORTOS:
        ojo, mira, escala, corte = ORTOS[vista]
        cam = camara_orto(f'cam {vista}', ojo, mira, escala)
        n = ocultar_sobre(corte)
        print(f'    (planta: {n} piezas por encima de {corte:.2f} fuera)', flush=True)
        if vista.startswith('planta'):          # las plantas, cuadradas
            alto = ancho
    else:
        ojo, mira, lente = VISTAS[vista]
        cam = camara(f'cam {vista}', ojo, mira, lente)
    sc.camera = cam
    sc.view_settings.exposure = EXPOSICION.get(vista, EXPOSICION_BASE)
    sc.render.resolution_x = ancho
    sc.render.resolution_y = alto
    sc.render.filepath = salida
    if rapido:
        sc.cycles.samples = max(24, spp // 16)
        sc.render.resolution_x = ancho // 3
        sc.render.resolution_y = alto // 3
    bpy.ops.render.render(write_still=True)
    mostrar_todo()
    return salida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vista', default='barra')
    ap.add_argument('--todas', action='store_true')
    ap.add_argument('--vistas', default='')
    ap.add_argument('--spp', type=int, default=1200)
    ap.add_argument('--ancho', type=int, default=3840)
    ap.add_argument('--alto', type=int, default=2160)
    ap.add_argument('--rapido', action='store_true')
    ap.add_argument('--sin-decoracion', action='store_true')
    ap.add_argument('--glare', action='store_true')
    ap.add_argument('--sin-ciudad', action='store_true')
    ap.add_argument('--salida', default=os.path.join(SCRATCH, 'renders'))
    ap.add_argument('--guardar-blend', default='')
    ap.add_argument('--gpu', action='store_true',
                    help='renderiza con la tarjeta grafica en vez de la CPU')
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None)

    global USAR_GPU
    USAR_GPU = a.gpu
    # Absoluta siempre. Blender resuelve una ruta relativa contra el .blend,
    # no contra el directorio de trabajo: '.\\renders' acababa en C:\\renders.
    a.salida = os.path.abspath(os.path.expanduser(a.salida))
    os.makedirs(a.salida, exist_ok=True)
    todas = list(VISTAS) + list(ORTOS)
    if a.vistas:
        vistas = [v.strip() for v in a.vistas.split(',') if v.strip() in todas]
    else:
        vistas = todas if a.todas else [a.vista]
    print('Casa Margot · montando la escena', flush=True)
    print('  activos:', SCRATCH, flush=True)
    # Sin activos la escena se montaba igual -sin texturas, sin el logo y sin
    # los 22 modelos de decoracion- y el render salia mal pareciendo bien. Se
    # para antes de gastar el render. El coche solo hace falta en las vistas
    # de calle, asi que ese es aviso y no parada.
    if not os.path.isdir(os.path.join(SCRATCH, 'coches')):
        print('  aviso: falta el coche; la calle saldra vacia', flush=True)
    faltan = [n for n, c in (('las texturas y modelos de Poly Haven', PH),
                             ('el vinilo del logo', os.path.dirname(LOGO)))
              if not os.path.isdir(c)]
    if faltan:
        print('\n  *** NO ESTAN ' + ' NI '.join(faltan).upper() + ' ***\n',
              flush=True)
        print('  Se buscaron en:', SCRATCH, flush=True)
        print('  El render saldria sin texturas, asi que no se hace. Antes:',
              flush=True)
        print('      python preparar_activos.py', flush=True)
        print('  Si ya estan bajados pero en otro sitio, hay que decirlo:',
              flush=True)
        print('      set CM_SCRATCH=C:\\ruta\\a\\los\\activos    (Windows)',
              flush=True)
        print('      export CM_SCRATCH=/ruta/a/los/activos   (Mac y Linux)\n',
              flush=True)
        sys.exit(2)
    ciudad = any(v in VE_LA_CALLE for v in vistas) and not a.sin_ciudad
    construir(a.spp, a.ancho, a.alto, not a.sin_decoracion, a.glare, ciudad)
    print('  ciudad:', 'montada' if ciudad else 'no hace falta en estas vistas', flush=True)
    print('  objetos en escena:', len(bpy.data.objects), flush=True)
    if a.guardar_blend:
        bpy.ops.wm.save_as_mainfile(filepath=a.guardar_blend)
        print('  guardado', a.guardar_blend, flush=True)
    for v in vistas:
        f = os.path.join(a.salida, f'CM_{v}.png')
        print(f'  render {v} -> {f}', flush=True)
        import time
        t = time.time()
        render(v, f, a.spp, a.ancho, a.alto, a.rapido)
        print(f'  {v} listo en {time.time() - t:.0f} s', flush=True)


# ------------------------------------------- piezas de caracter italiano
def _calca_png(nombre, ancho_px, alto_px, dibujar):
    """Genera un PNG con PIL en el scratch y devuelve su ruta."""
    from PIL import Image, ImageDraw
    d = os.path.join(SCRATCH, 'calcas')
    os.makedirs(d, exist_ok=True)
    ruta = os.path.join(d, f'{nombre}.png')
    im = Image.new('RGBA', (ancho_px, alto_px), (0, 0, 0, 0))
    dibujar(im, ImageDraw.Draw(im))
    im.save(ruta)
    return ruta


def _fuente(px, negrita=False, cursiva=False):
    """Solo hay DejaVu: la cursiva se hace con el serif, que ademas queda
    mejor en una carta de trattoria."""
    from PIL import ImageFont
    n = 'DejaVuSerif' if cursiva else 'DejaVuSans'
    if negrita:
        n += '-Bold'
    return ImageFont.truetype(f'/usr/share/fonts/truetype/dejavu/{n}.ttf', px)


def pizarra_menu(x, y, z, normal='-Y', ancho=0.62, alto=0.88, col='Decoracion'):
    """Pizarra de carta del dia, escrita a mano."""
    def dib(im, dr):
        W, H = im.size
        dr.rectangle((0, 0, W, H), fill=(26, 28, 27, 255))
        dr.text((W * 0.16, H * 0.06), 'MENU', font=_fuente(int(H * 0.085), True),
                fill=(242, 238, 228, 255))
        dr.text((W * 0.10, H * 0.155), 'del giorno', font=_fuente(int(H * 0.070), False, True),
                fill=(232, 226, 212, 255))
        dr.line((W * 0.10, H * 0.255, W * 0.90, H * 0.255), fill=(200, 196, 186, 255), width=3)
        platos = [('Antipasto della casa', '9,50'), ('Tagliatelle al ragù', '12,00'),
                  ('Gnocchi al pesto', '11,50'), ('Parmigiana', '10,50'),
                  ('Tiramisù', '5,50'), ('Caffè Margot', '1,80')]
        f = _fuente(int(H * 0.044))
        for i, (p, pr) in enumerate(platos):
            yy = H * (0.315 + i * 0.088)
            dr.text((W * 0.09, yy), p, font=f, fill=(238, 233, 220, 255))
            # el precio, alineado a la derecha: si no, los platos largos se
            # comian la cifra ("Antipasto della casa9,50")
            anc = dr.textlength(pr, font=f)
            dr.text((W * 0.91 - anc, yy), pr, font=f, fill=(226, 200, 140, 255))
        dr.text((W * 0.30, H * 0.905), '~ Casa Margot ~',
                font=_fuente(int(H * 0.050), False, True), fill=(210, 205, 190, 255))
    ruta = _calca_png('pizarra_menu', 620, 880, dib)
    e = 0.030
    s = -1 if normal in ('-Y', '-X') else 1
    if normal in ('-Y', '+Y'):
        caja('Pizarra marco', x - ancho / 2 - 0.030, y, x + ancho / 2 + 0.030,
             y + s * e, z - alto / 2 - 0.030, z + alto / 2 + 0.030, MAT['mesa'], col)
        v = [(x - ancho / 2, y + s * (e + 0.002), z - alto / 2),
             (x + ancho / 2, y + s * (e + 0.002), z - alto / 2),
             (x + ancho / 2, y + s * (e + 0.002), z + alto / 2),
             (x - ancho / 2, y + s * (e + 0.002), z + alto / 2)]
        uvs = ((1, 0), (0, 0), (0, 1), (1, 1)) if s < 0 else ((0, 0), (1, 0), (1, 1), (0, 1))
    else:
        caja('Pizarra marco', x, y - ancho / 2 - 0.030, x + s * e,
             y + ancho / 2 + 0.030, z - alto / 2 - 0.030, z + alto / 2 + 0.030,
             MAT['mesa'], col)
        v = [(x + s * (e + 0.002), y - ancho / 2, z - alto / 2),
             (x + s * (e + 0.002), y + ancho / 2, z - alto / 2),
             (x + s * (e + 0.002), y + ancho / 2, z + alto / 2),
             (x + s * (e + 0.002), y - ancho / 2, z + alto / 2)]
        uvs = ((0, 0), (1, 0), (1, 1), (0, 1)) if s > 0 else ((1, 0), (0, 0), (0, 1), (1, 1))
    me = bpy.data.meshes.new('Pizarra carta')
    me.from_pydata(v, [], [(0, 1, 2, 3)])
    me.uv_layers.new()
    for i, c in enumerate(uvs):
        me.uv_layers[0].data[i].uv = c
    me.materials.append(MT.calca('Carta del dia', ruta, rug=0.85))
    ob = bpy.data.objects.new('Pizarra carta', me)
    coleccion(col).objects.link(ob)
    return ob


def nichos_botellas(x0, x1, y, z0, alto=0.95, n=5, normal='-Y', col='Decoracion'):
    """Hornacinas iluminadas con botellas, como en las fotos de referencia.

    Carcasa abierta: trasera, dos costados, tapa, fondo y montantes. Antes era
    un bloque macizo con las botellas dentro, asi que no se veia nada.
    """
    prof = 0.190
    s_ = -1 if normal == '-Y' else 1
    e = 0.026                                  # grueso de la madera
    ya, yb = (y, y + s_ * prof) if s_ > 0 else (y + s_ * prof, y)
    # trasera clara, que es la que recoge la luz
    caja('Nichos · trasera', x0, y - s_ * 0.004, x1, y + s_ * 0.020,
         z0, z0 + alto, MAT['_blanco'], col)
    # tapa, fondo y costados
    caja('Nichos · tapa', x0, ya, x1, yb, z0 + alto - e, z0 + alto, MAT['_liston'], col)
    caja('Nichos · base', x0, ya, x1, yb, z0, z0 + e, MAT['_liston'], col)
    caja('Nichos · costado i', x0, ya, x0 + e, yb, z0, z0 + alto, MAT['_liston'], col)
    caja('Nichos · costado d', x1 - e, ya, x1, yb, z0, z0 + alto, MAT['_liston'], col)
    paso = (x1 - x0 - 2 * e) / n
    for i in range(n):
        a = x0 + e + paso * i
        b = a + paso
        if i:                                  # montante entre hornacinas
            caja(f'Nichos · montante {i}', a - e / 2, ya, a + e / 2, yb,
                 z0 + e, z0 + alto - e, MAT['_liston'], col)
        # balda intermedia
        zb_ = z0 + alto * 0.52
        caja(f'Nichos · balda {i + 1}', a + e / 2, ya, b - e / 2, yb,
             zb_, zb_ + 0.016, MAT['_liston'], col)
        # LED bajo la tapa y bajo la balda
        for zz, pot in ((z0 + alto - e - 0.012, 7.0), (zb_ - 0.012, 5.0)):
            caja(f'Nichos · led {i + 1} {zz:.2f}', a + 0.02, y + s_ * 0.030,
                 b - 0.02, y + s_ * 0.055, zz, zz + 0.010,
                 MAT['_luz_calida'], col)
            lz = bpy.data.lights.new(f'Nicho luz {i + 1} {zz:.2f}', 'AREA')
            lz.shape = 'RECTANGLE'
            lz.size, lz.size_y = b - a - 0.04, prof * 0.7
            lz.energy = pot
            lz.color = (1.0, 0.87, 0.70)
            ob = bpy.data.objects.new(f'Nicho luz {i + 1} {zz:.2f}', lz)
            ob.location = ((a + b) / 2, y + s_ * prof * 0.55, zz - 0.004)
            ob.rotation_euler = (math.radians(180), 0, 0)
            coleccion('Luces').objects.link(ob)
        # genero: botellas abajo, ceramica arriba
        for k in range(3):
            bx = a + (b - a) * (k + 0.5) / 3
            botella(f'Nicho {i + 1} botella {k + 1}', bx, y + s_ * prof * 0.55,
                    z0 + e + 0.004, alto=0.24 + 0.04 * ((i + k) % 3), col=col)
        if i % 2 == 0:
            poner('ceramic_vase_02', (a + b) / 2, y + s_ * prof * 0.55,
                  zb_ + 0.016, altura=0.26, giro=i * 37, col=col)
        else:
            for k in range(2):
                bx = a + (b - a) * (k + 0.5) / 2
                botella(f'Nicho {i + 1} alta {k + 1}', bx, y + s_ * prof * 0.55,
                        zb_ + 0.016, alto=0.26, col=col)


def logo_escaparate():
    """El logo en vinilo sobre el vidrio del escaparate, como lo pondria el
    rotulista: a la altura de la vista, legible desde la calle."""
    if not os.path.exists(LOGO):
        return
    w_px, h_px = _medida_png(LOGO)
    ancho = 1.15
    alto = ancho * h_px / w_px
    y = 1.585                      # cara interior del vidrio del ventanal Sur
    cx, cz = 3.60, 1.62
    me = bpy.data.meshes.new('Logo escaparate')
    v = [(cx - ancho / 2, y, cz - alto / 2), (cx + ancho / 2, y, cz - alto / 2),
         (cx + ancho / 2, y, cz + alto / 2), (cx - ancho / 2, y, cz + alto / 2)]
    me.from_pydata(v, [], [(0, 1, 2, 3)])
    me.uv_layers.new()
    for i, c in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        me.uv_layers[0].data[i].uv = c
    me.materials.append(MT.calca('Vinilo escaparate', LOGO, rug=0.40))
    ob = bpy.data.objects.new('Logo escaparate', me)
    coleccion('Decoracion').objects.link(ob)
    return ob


def caracter_italiano():
    """Lo que convierte el local en una trattoria y no en una cafeteria."""
    # Ni carta en pizarra en el paso de servicio ni hornacinas sobre el
    # sillon: ese tramo es zona de paso y la pared del sillon lleva solo
    # cuadros.
    # el logo en el vidrio del ventanal
    logo_escaparate()
    # el expositor de bebidas, lleno: sus cinco parrillas estan a 0,46 / 0,73
    # / 1,00 / 1,27 / 1,54 (obj_A7: Z_INT0 + 0,190 + k * 0,270)
    ax, ay = 5.995, 4.078                      # centro y cara interior del frente
    for k in range(5):
        z = 0.462 + k * 0.270
        for j in range(6):
            bx = ax - 0.185 + j * 0.074
            for f, dy in ((0, 0.075), (1, 0.230)):
                botella(f'A7 botella {k}{j}{f}', bx, ay + dy, z + 0.006,
                        alto=0.225 if k % 2 == 0 else 0.245, col='Decoracion')
    # Cesta de pan del paso. Estaba en x = 2,75 y la tabla del mostrador muere
    # en 2,53: volaba 220 mm por delante del canto. Se pasa a la mesa de
    # trabajo de la cocina, con la fruta y la otra cesta.
    poner('wicker_basket_02', 2.10, 7.35, 0.850, escala=0.8, giro=15)
    # Ceramica al pie del ventanal. Iba a la cota del zocalo (0,130) como si
    # hubiera alfeizar, pero el ventanal arranca del suelo: la vasija de
    # vidrio va de 0,130 a 4,700 y no hay repisa ninguna, asi que las piezas
    # colgaban a 129 mm del pavimento. Van al suelo.
    for i, x in enumerate((4.35, 5.05, 5.75)):
        poner(('ceramic_vase_01', 'ceramic_vase_02', 'brass_pot_01')[i % 3],
              x, 1.760, 0.001, escala=0.8, giro=i * 63)


if __name__ == '__main__':
    main()
