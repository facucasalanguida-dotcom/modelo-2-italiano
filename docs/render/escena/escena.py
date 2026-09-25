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
import recorrido as RC          # noqa: E402

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

# Con CM_MAXIMA (lote.py --maxima) los recursos van a lo mas alto que hay:
# los modelos de Poly Haven con sus texturas a 4K (ph/<aid>/4k), el cielo a
# 16K y los arboles de la calle en LOD0, con todo su detalle. Las texturas de
# los materiales las sube a 4K CM_4K, en materiales.py. Sin ellas, como
# siempre: modelos a 2K, cielo a 8K y arbolado en LOD1, que cabe en cualquier
# tarjeta.
MAXIMA = os.environ.get('CM_MAXIMA', '') != ''
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
            # Solo la tarjeta. Con la CPU tambien, en un portatil la CPU apenas
            # suma al lado de la grafica, pero comparte con ella la
            # refrigeracion: se calentaba todo (75 grados de CPU) y la tarjeta
            # podia acabar bajando el ritmo por temperatura.
            for d in pref.devices:
                d.use = (d.type == tipo)
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


# Piezas del plano que fachada_real() rehace a partir del video de la fachada
# (IMG_6570). El muro del cuello y la jamba no existen en obra: el rincon entre
# el ventanal y P5 es un retorno ACRISTALADO, con su perfil y su travesaño.
FACHADA_REHECHA = ('Solera de planta baja',   # bajo el suelo no se ve, y en
                                           # el retranqueo tapaba la acera
                   'Muro Oeste del cuello', 'Ventanal Sur · jamba',
                   'Ventanal Sur · paño 2', 'Escaparate · zócalo de piedra',
                   'Puerta de acceso · montante superior')
FACHADA_REHECHA_PREFIJOS = ('Ventanal Sur · travesaño', 'Ventanal Sur · zócalo',
                            'Dintel de fachada Sur', 'Dintel de fachada Este')


def sustituido(s):
    """True si ese solido del plano lo rehace la escena con mas detalle."""
    nm = s['nombre'] or ''
    if nm in FACHADA_REHECHA or nm.startswith(FACHADA_REHECHA_PREFIJOS):
        return True                       # lo rehace fachada_real(), del video
    if '· motor' in nm:
        return False                      # el motor de la vitrina si se dibuja:
                                          # va visto dentro del hueco de abajo
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
    if nm in ('Borde Oeste del vacio', 'Borde Sur del vacio'):
        return True                       # el antepecho lo pone planta_alta()
    if nm.startswith('Sillón corrido'):
        return True                       # lo rehace sillon_corrido(), con sus
                                          # cojines: la caja del plano los tapaba
                                          # y su frente parpadeaba con la base
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


def _vidrio_L(cajas):
    """Mete el vidrio de la pared en L dentro de sus perfiles.

    El plano lo pone de 5,457 a 8,927 y de 1,220 a 2,570: sus testas caen en
    el mismo plano que las caras de las jambas, del remate inferior y del
    tabique Doblez (y = 5,457), y su canto de abajo sobre la coronacion del
    muro (z = 1,220). En esa testa salia una banda negra al pie del montante:
    el rayo cruzaba el vidrio, caia dentro de la jamba por la cara coincidente
    y ya no salia. Ademas subia hasta 2,570, 9 mm por encima del suelo de la
    planta alta. Ahora cada canto queda embebido en su perfil.
    """
    for s in cajas:
        if (s.get('nombre') or '') == 'Tramo largo 3,60 · vidrio':
            s['y0'] += 0.010          # dentro de la jamba Sur (5,457..5,487)
            s['y1'] -= 0.010          # dentro de la jamba Norte
            s['z0'] = 1.226           # dentro del remate inferior (1,205..1,235)
            s['z1'] = Z_SOFITO - 0.012   # dentro del remate superior (2,280..2,310)


# El hueco que queda entre el borde en rampante del cerramiento de la
# escalera y el techo, junto al montante, lo quiere el cliente mas grande. El
# borde baja 0,75 paralelo a si mismo -de 0,85 a 0,10 sobre la linea de los
# peldaños: queda como una zanca y desde la sala se ve casi toda la
# escalera- y el hueco llega hasta y 7,13 antes de morir en el techo. El
# montante y el forjado que vuela por encima, con su acabado, no se tocan.
BAJADA_HUECO_ESCALERA = 0.75


def _panel_escalera(paneles):
    """El cerramiento del costado de la escalera arranca en el montante gris.

    El plano lo empieza en y = 3,939, la esquina del altillo, con el borde
    superior en rampante de (3,939 / 1,209) a (5,84 / 2,31). En obra empieza
    en el montante, a mitad del 5.º peldaño, y los peldaños de delante quedan
    vistos de lado. Se recorta por el Sur hasta la cara Norte del montante,
    siguiendo el mismo rampante, y el rampante baja BAJADA_HUECO_ESCALERA
    con la misma pendiente: el borde toca el techo mas al Norte. El resto del
    panel no cambia.
    """
    y_ini = PILAR_ESCALERA['y1']
    pend = (2.310 - 1.209) / (5.84 - 3.939)
    b = BAJADA_HUECO_ESCALERA
    for s in paneles:
        if s['nombre'] != 'Caja de escalera (planta baja)':
            continue
        pts = [tuple(p) for p in s['pts_yz']]
        assert ((3.939, 0.0) in pts and (3.939, 1.209) in pts
                and (5.84, 2.31) in pts), pts
        z_ini = 1.209 - b + (y_ini - 3.939) * pend
        y_techo = 5.84 + b / pend
        s['pts_yz'] = [[y_ini, 0.0] if p == (3.939, 0.0) else
                       [y_ini, round(z_ini, 4)] if p == (3.939, 1.209) else
                       [round(y_techo, 4), 2.31] if p == (5.84, 2.31) else
                       list(p) for p in pts]


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
            # La coronacion tambien pelea: dos tabiques que solapan en el
            # rincon y mueren a la misma cota dejan dos caras hacia arriba en
            # el mismo plano, y sale un cuadrado negro en la esquina (pasaba
            # en el doblez de la pared en L, a 1,220). Se baja la del solido
            # menor, salvo que muera contra un techo -ahi si abriria rendija-.
            if abs(a['z1'] - b['z1']) < 1e-9 and not any(
                    abs(a['z1'] - t) < 0.001 for t in (Z_SOFITO, Z_PA, Z_TECHO)):
                ajustes.setdefault(j, {})['z1'] = -DESPEGUE
    return ajustes


def arquitectura():
    """Muros, forjado, escalera, carpinteria y mobiliario fijo del plano."""
    j = json.load(open(os.path.join(PLANOS, 'MODELO_3D.json'), encoding='utf-8'))
    _retranquear(j['cajas'])
    _panel_escalera(j['paneles'])
    _asentar(j['cajas'])
    _vidrio_L(j['cajas'])
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
        if s['nombre'] in ('Ventanal Sur · paño 1', 'Escaparate · vidrio'):
            # el canto de abajo, dentro del vierteaguas: sobre su cara de
            # arriba (0,130) el vidrio tocaba un opaco en el mismo plano
            z0 = FA_VIERTE - SOLAPE
            # y los de los lados, dentro de los montantes: acababan a ras de
            # su cara exterior y las dos caras parpadeaban
            x0, x1 = x0 + SOLAPE, x1 - SOLAPE
        if s['nombre'].startswith('Tramo largo') and s['mat'] == 'vidrio':
            # hasta el techo, pero con el canto metido en el remate superior
            # (2,280..2,310): a 2,310 justos coincidia con el intrados
            z1 = Z_SOFITO - 0.012
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
    # su cara de abajo, medio mm por debajo de la del dintel: en el mismo
    # plano parpadeaban madera y tabique
    piezas.append(C(f'{nm} · cabecero del cerco', a0 + CERCO - 0.002, b0 - 0.002,
                    a1 - CERCO + 0.002, b1 + 0.002, ztop - DESPEGUE, zc, madera))
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
    # Con la forma del interior y no con una caja: la caja salia al porche y
    # al retranqueo de la entrada, y con la acera ya a nivel del local esos
    # dos suelos exteriores habrian salido de roble. El borde sigue la linea
    # de los vidrios -ventanal, retorno, escaparate, cubo- y la de la puerta.
    pts = [(0.200, 9.060), (9.940, 9.060), (9.940, 1.404), (7.593, 1.404),
           (7.593, 0.395), (6.331, 0.395), (6.331, 1.000), (5.735, 1.000),
           (5.735, 1.591), (0.200, 1.591)]
    prisma('Pavimento planta baja', pts[::-1], -0.018, 0.001, MAT['_suelo'], 'Obra')
    # El techo de planta baja NO se dibuja: donde hay altillo, el techo es el
    # intrados del propio forjado (el plano ya lo trae), y donde no lo hay el
    # local es de doble altura hasta el techo del altillo. Ponerlo plano a
    # 2,31 en todo el local cerraba la doble altura y dejaba el local a oscuras.
    # Techo de pladur de la cocina. El resto de la planta baja ya tiene techo
    # -el intrados del forjado, a 2,310- pero la cocina cae fuera del altillo
    # y se quedaba abierta a la doble altura hasta los 5,06. Va enlucido con
    # el mismo material que sus paredes, que es lo que pidio el cliente.
    #   Oeste x 0,250 trasdos del Muro Oeste;  Este x 2,448 cara Oeste de la
    #   pared en L, para no pisar su remate (2,448..2,512 entre 2,280 y 2,310)
    #   Norte y 9,008 trasdos de la medianera
    #   Sur   la viga P1b: el cliente lo quiere cortado en la viga, que su
    #                 canto y la cara de la viga queden en un solo plano.
    # A RAS del intrados de la viga y del forjado (2,310), no colgado 15 mm
    # por debajo: colgado, su canto asomaba bajo la cara de la viga como un
    # reborde, y pasada la testa de la viga (x 2,411) volaba solo. Asi la
    # cara de la viga es lo unico que se ve de frente, y por debajo viga,
    # forjado y techo son un mismo plano. Se mete 4 mm en la viga (y 5,183)
    # y en el forjado (x 2,411), medio milimetro por encima de sus caras de
    # abajo, para que no haya junta abierta ni dos caras en el mismo plano.
    #   debajo de la viga (y 4,933..5,183) el techo es la propia viga
    #   entre la viga y y 7,509 el forjado cubre x >= 2,411
    #   de y 7,509 al Norte el forjado arranca en 2,461: el techo llega a la L
    # La campana KC (x 0,31..2,31, y 7,778..8,978, de 2,00 a 2,54) sube por
    # encima de los 2,31: el techo la rodea, no la atraviesa. Entero, dejaba
    # una tapa de yeso dentro de la campana, a media altura de los filtros.
    kx0, ky0, kx1, ky1 = CAMPANA_KC
    yv = E.VIGA[4] - SOLAPE                  # cara Norte de la viga, 5,183
    xf = 2.411 + SOLAPE                      # cara Oeste del forjado
    for nm, a0, b0, a1, b1 in (('', 0.250, yv, xf, 7.509),
                               (' junto a la L', 0.250, 7.509, 2.448, ky0),
                               (' Oeste', 0.250, ky0, kx0, 9.008),
                               (' Este', kx1, ky0, 2.448, 9.008),
                               (' Norte', kx0, ky1, kx1, 9.008)):
        caja(f'Techo de pladur · cocina{nm}', a0, b0, a1, b1,
             Z_TECHO_COCINA, Z_TECHO_COCINA + 0.015, MAT['muro'], 'Obra')

    # Pavimento del altillo, sobre el forjado. Va con la MISMA planta que el
    # forjado -E.FORJADO-, no con su rectangulo envolvente: el poligono tiene
    # recortado el hueco de la escalera (x 8,811..9,890 entre y 3,939 y 7,738)
    # y si aqui se pone una caja, el roble tapa el hueco y la escalera sube
    # contra un techo a 2,54. El forjado lo traia bien; el pavimento no.
    # Arranca en la cara de arriba del forjado: bajando 18 mm sus cantos
    # coincidian con los del forjado en todo el borde del altillo.
    prisma('Pavimento planta alta', E.FORJADO, Z_PA - DESPEGUE, Z_PA + 0.001,
           MAT['_suelo'], 'Planta alta')


# Huella en planta de la campana KC tal como la planta aparatos() -
# comprobada contra su caja envolvente en la escena montada.
CAMPANA_KC = (0.310, 7.778, 2.310, 8.978)
# Cara de abajo del techo de pladur de la cocina: a ras del intrados de la
# viga P1b y del forjado, medio milimetro por encima para no compartir plano.
Z_TECHO_COCINA = Z_SOFITO + DESPEGUE


def vestibulo():
    """El cubo de la entrada: paredes de obra y techo, con la puerta al fondo.

    Lo que hay delante de la hoja es una caja abierta solo a la calle. El
    costado Este ya lo da el cuello de la medianera y el fondo lo cierra la
    propia puerta; aqui van el costado Oeste y el techo, que es lo que hace
    que la entrada sea un hueco de 2,06 x 2,10 y no un agujero abierto hasta
    los cinco metros de la doble altura.

    El costado Oeste es de VIDRIO con rebordes del color de la pared. El
    techo si es pladur macizo, tambien del color de la pared.
    """
    R = RETRANQUEO
    xp = R['x0'] - R['e_pared']              # trasdos del tabique del costado
    # Costado Oeste: NO es un tabique, es un pano de vidrio. Antes de entrar,
    # a la izquierda, se ve la sala a traves del cristal. Va enmarcado con
    # rebordes del color de la pared -montantes de 60 arriba, abajo y en las
    # dos jambas- y el vidrio por el medio, de 12, centrado en el grueso.
    C = 0.060                                # ancho del reborde
    ey0, ey1 = R['y0'] + DESPEGUE, R['y1']
    ez0, ez1 = -0.010, R['alto']
    for nm, y0, y1, z0, z1 in (
            ('inferior', ey0, ey1, ez0, ez0 + C),
            ('superior', ey0, ey1, ez1 - C, ez1),
            ('jamba calle', ey0, ey0 + C, ez0 + C, ez1 - C),
            ('jamba puerta', ey1 - C, ey1, ez0 + C, ez1 - C)):
        # crema, el mismo lacado que el resto de la fachada: es el que se ve
        # en las fotos del retranqueo
        bisel(caja(f'Vestíbulo · reborde {nm}', xp, y0, R['x0'], y1, z0, z1,
                   MAT['_perfil_crema']))
    xc = (xp + R['x0']) / 2
    caja('Vestíbulo · vidrio Oeste', xc - 0.006, ey0 + C - SOLAPE, xc + 0.006,
         ey1 - C + SOLAPE, ez0 + C - SOLAPE, ez1 - C + SOLAPE, MAT['vidrio'])
    # Techo del cubo: vuela 6 mm sobre el tabique para caparlo, se hunde 4 mm
    # en la cabeza de la puerta y se mete en el cuello de la medianera. Por
    # delante arranca en la cara interior de la perfileria de fachada
    # (y 0,425): desde 0,371 asomaba un bloque de pladur 9 mm por delante
    # del vidrio del escaparate, en su esquina derecha, de 2,10 a 2,24.
    ob = caja('Vestíbulo · techo', xp - 0.006, 0.425 - SOLAPE,
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
    # El plano arranca la vitrina a 0,600 (V1/V2 van de 0,600 a 1,250), asi
    # que la madera sube hasta ahi: queda medio frente de madera y medio de
    # vitrina, que es como lo quiere el cliente. Antes moria en 0,420 y la
    # madera se quedaba en un tercio.
    Z_BASE_VITRINA = VITRINA_BASE     # y ahora hasta la vitrina acortada
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
            # medio mm por debajo de la tabla: con la cara de abajo en el
            # mismo plano que la suya parpadeaban
            caja(f'Frente de la barra · canto {nm}', mx1 - 0.055, ya, mx1 + 0.012,
                 yb, z1 - DESPEGUE, z1 + 0.042, MAT['mesa'])
    # Balda en la que apoyan las dos vitrinas acortadas. Por debajo queda el
    # hueco abierto al pasillo, con los dos motores y el lavavasos del plano.
    # su trasera y su testa Sur, medio mm por dentro de las de la vitrina
    bisel(caja('Vitrinas · balda de apoyo', VITRINA_TRASERA + DESPEGUE, my0 + DESPEGUE,
               mx1 - 0.030, Y_MOSTRADOR, VITRINA_BASE - 0.025, VITRINA_BASE, MAT['inox']))
    # Testa Norte del mostrador: el trasdos negro de los listones acababa a la
    # vista justo donde arranca la pared en L y se leia como una franja negra.
    # Se cierra con un remate blanco, que ademas continua la linea de la L.
    caja('Frente de la barra · remate Norte', mx1 - 0.062, my1 - 0.004,
         mx1 + 0.014, my1 + 0.014, 0.0, Q.H_ENCIMERA + 0.042 - DESPEGUE,
         MAT['muro'])

    # Canto del forjado: en la referencia es una banda blanca lisa que no
    # sobresale nada por debajo del intrados. Antes colgaba 120 mm y ademas
    # iba en azzurro, que es justo al reves de lo que pide el cliente. Va
    # a tope contra el canto del forjado, sin solapar, para no dejar dos
    # caras inferiores en el mismo plano. Acaba donde acaba el forjado, en
    # la esquina del hueco de la escalera (x 8,811): seguia hasta la
    # medianera (9,890) y cruzaba el hueco como una viga suelta.
    caja('Canto del forjado Sur', 2.405, 3.907, 8.811, 3.939,
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
    # Hasta la coronacion de la pared en L (1,220), no hasta 1,500: subia
    # 280 mm por encima del muro y asomaba dentro de la cristalera.
    caja('Cocina · chapa Este', x1 - e, y0, x1 + SOLAPE, y1, 0.0,
         E.H_PARED_L - DESPEGUE, MAT['inox'], 'Obra')
    # junta horizontal: dos perfiles que rompen el paño y dan una linea de luz
    for zz in (1.500, 2.150):
        caja(f'Cocina · junta {zz:.2f} N', x0, y1 - 0.014, x1, y1 - e,
             zz - 0.006, zz, MAT['inox'], 'Obra')
    # barra portautensilios sobre la bancada, como en la referencia
    cilindro('Cocina · barra utensilios', 0, 0, 0.001, 0, 0.001, MAT['inox'], 'Obra', 4)
    bpy.data.objects.remove(bpy.data.objects['Cocina · barra utensilios'], do_unlink=True)
    # Los cazos colgaban hasta 1,250 y los aparatos de debajo (K2, K3) llegan
    # a 1,26-1,27: se metian dentro. Y a 60 mm del muro, con 75 de radio,
    # los cazos entraban en la chapa. Todo sube 100 mm y se separa 86 mm; el
    # riel va cogido al muro con dos escuadras, no en el aire.
    yb = y1 - 0.086
    caja('Cocina · riel', x0 + 0.35, yb - 0.012, x0 + 1.75, yb + 0.012,
         1.580, 1.604, MAT['inox'], 'Obra')
    for xe in (x0 + 0.38, x0 + 1.72):
        caja(f'Cocina · escuadra del riel {xe:.2f}', xe - 0.010, yb, xe + 0.010,
             y1 - e + SOLAPE, 1.580 + DESPEGUE, 1.604 - DESPEGUE, MAT['inox'], 'Obra')
    for i in range(6):
        x = x0 + 0.45 + i * 0.24
        # el gancho entra 5 mm en lo que cuelga: antes quedaba 5 mm por encima
        caja(f'Cocina · gancho {i + 1}', x - 0.004, yb - 0.004, x + 0.004, yb + 0.004,
             1.490, 1.592, MAT['inox'], 'Obra')
        # cazo o utensilio colgado
        if i % 2 == 0:
            cilindro(f'Cocina · cazo {i + 1}', x, yb, 0.075, 1.350, 1.495,
                     MAT['inox'], 'Obra', 28)
        else:
            caja(f'Cocina · pala {i + 1}', x - 0.035, yb - 0.006, x + 0.035,
                 yb + 0.006, 1.330, 1.495, MAT['inox'], 'Obra')


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
    # Las jambas arrancan ENCIMA del remate inferior, no dentro de el: tienen
    # su mismo ancho, y al solapar 15 mm sus caras laterales caian en el mismo
    # plano y mirando al mismo lado. Era la banda negra al pie del montante.
    for nm, ya, yb in (('Sur', y0, y0 + h), ('Norte', y1 - h, y1)):
        caja(f'Vidrio L · jamba {nm}', x0 - e, ya, x1 + e, yb,
             z_ab + h * 0.5, z_ar - h, m, 'Obra')


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
    # P2 y P5: lo que da a la calle va en arenisca y lo monta fachada_real()
    # a partir del video de la fachada. Aqui quedan solo sus caras interiores,
    # en la pizarra que ya tenian.
    ('P2', 1.290, 1.561, 1.870, 2.011, 'ONE', 'losa'),     # pilastra del ventanal
    ('P3', 5.670, 4.688, 6.320, 5.758, 'SNOE', 'liston'),  # exento, en la sala
    ('P4', 9.689, 4.708, 9.890, 5.309, 'SNO', 'liston'),   # machon de la medianera
    # P5 entero lo forra fachada_real(): tres caras a la calle en arenisca y
    # las interiores en pizarra.
)


# El montante gris de la escalera, en planta. Centrado a mitad del 5.º
# peldaño (4,619..4,879), que es donde esta en la segunda foto de obra, la
# tomada desde la sala: no en la esquina del altillo, sino 0,73 m mas atras,
# con el forjado volando por delante de el.
PILAR_ESCALERA = dict(x0=8.651, x1=8.811, y0=4.669, y1=4.829)


def pilar_escalera():
    """El perfil de acero que hay en obra junto a la escalera.

    En las fotos de obra es un montante gris vertical, de 160, que sube del
    suelo hasta el intrados del forjado por el costado Oeste del tramo, a
    haces con el borde del hueco (x 8,811). No esta en la esquina del
    altillo: esta a mitad del 5.º peldaño, y el forjado vuela 0,73 m por
    delante de el hasta su esquina (8,811 / 3,939).

    El cerramiento del costado -CAJA_ESC_PB- arranca en el: los peldaños de
    delante quedan vistos de lado, y el montante se ve entero del suelo al
    techo (ver _panel_escalera).

    Va enlucido con el mismo material que el cerramiento, no forrado de
    roble: es lo que eligio el cliente.

    Sostiene parte del techo y no se puede quitar.
    """
    # La cara Este se retira un DESPEGUE de la del hueco del forjado, con la
    # que comparte plano; la cabeza se hunde un SOLAPE en el forjado.
    P = PILAR_ESCALERA
    x0, x1 = P['x0'], P['x1'] - DESPEGUE
    y0, y1 = P['y0'], P['y1']
    ob = caja('Pilar de la escalera', x0, y0, x1, y1, 0.0, Z_SOFITO + SOLAPE,
              MAT['tabique'])
    bisel(ob)
    return 1


def aplacado(nombre, x0, y0, x1, y1, z0, z1, eje='x', zocalo=0.090,
             tonos=None, gris=0.05, col='Obra'):
    """Aplacado de arenisca como el de la fachada real.

    Hiladas de 0,28 a 0,42 de alto y en cada una una o dos losas, con la
    junta vertical corrida respecto a la de abajo, y cada losa de su tono:
    asi esta en el video. Al pie, un zocalo gris oscuro que acaba en 0,080,
    a la misma altura que la banda de la perfileria (arranca en -0,010). La caja
    (x0..x1, y0..y1) es la capa del aplacado; eje dice hacia donde corre la
    cara. La semilla sale del nombre y no de hash(), para que el despiece
    sea el mismo en todas las vistas.
    """
    import zlib
    rnd = random.Random(zlib.crc32(nombre.encode()))
    tonos = tonos or MAT['_arenisca']
    J = 0.005
    obs = []
    if zocalo > 0:
        # el mismo gris mate que la banda de la perfileria: en el video es
        # una banda continua bajo vidrios y machones, no un negro brillante
        obs.append(caja(f'{nombre} zocalo', x0, y0, x1, y1, z0, z0 + zocalo,
                        MAT['_pizarra_fachada'][0], col))
    tot = z1 - (z0 + zocalo)
    alturas = []
    while sum(alturas) < tot:
        alturas.append(rnd.uniform(0.28, 0.42))
    alturas = [a * tot / sum(alturas) for a in alturas]
    L = (x1 - x0) if eje == 'x' else (y1 - y0)
    a0 = x0 if eje == 'x' else y0
    z = z0 + zocalo
    previo = None
    for i, h in enumerate(alturas):
        za = z + (J / 2 if i else 0.0)
        zb = z + h - (J / 2 if i < len(alturas) - 1 else 0.0)
        cortes = []
        if L > 0.70:              # en el video P2 y P5 Sur van a una losa
            c = rnd.uniform(0.32, 0.68) * L
            for _ in range(8):                 # que no caiga sobre la de abajo
                if previo is None or abs(c - previo) > 0.12:
                    break
                c = rnd.uniform(0.32, 0.68) * L
            cortes, previo = [c], c
        else:
            previo = None
        bordes = [0.0] + cortes + [L]
        for t in range(len(bordes) - 1):
            ua = a0 + bordes[t] + (J / 2 if t else 0.0)
            ub = a0 + bordes[t + 1] - (J / 2 if t < len(bordes) - 2 else 0.0)
            m = tonos[rnd.randrange(len(tonos))]
            if gris and rnd.random() < gris:
                m = MAT['_arenisca_gris']
            if eje == 'x':
                obs.append(caja(f'{nombre} {i + 1}.{t + 1}', ua, y0, ub, y1,
                                za, zb, m, col))
            else:
                obs.append(caja(f'{nombre} {i + 1}.{t + 1}', x0, ua, x1, ub,
                                za, zb, m, col))
        z += h
    for o in obs:
        bisel(o, 0.0018, segs=2)
    return obs


# Cotas de la perfileria de la fachada Oeste, leidas del video (IMG_6570)
# con el travesaño del plano (2,27..2,33) y el remate del vidrio (4,70) como
# escala. Las intermedias son estimaciones sobre fotos en escorzo: +-5 cm.
FA_BASE = 0.080         # banda oscura corrida al pie de todo el frente
FA_VIERTE = 0.130       # vierteaguas crema; el vidrio arranca aqui
FA_TRAVESANOS = ((2.270, 2.330),     # el del plano
                 (2.720, 2.780),     # donde va la caja del toldo
                 (4.320, 4.380))     # remate del vidrio alto
# Faja ciega de rotulo, crema. Llega hasta el intrados: medido sobre el
# fotograma 31 del segundo video, el mas lejano y frontal, la faja mide
# ~0,68 y no hay dintel de revoco entre ella y el balcon, como habia.
FA_FAJA = (4.380, Z_TECHO)
FA_PERFIL = 0.060                    # cara vista de montantes y travesaños


def _perfil(nombre, x0, y0, x1, y1, z0, z1, mat=None):
    ob = caja(nombre, x0, y0, x1, y1, z0, z1, mat or MAT['_perfil_crema'])
    bisel(ob, 0.0015, segs=2)
    return ob


def _paño_fachada(nombre, a0, a1, eje, p0, p1, montantes=(True, True),
                  travesaños=None, faja_fin=None):
    """Un paño de la fachada: banda, vierteaguas, montantes, travesaños,
    faja de rotulo hasta el intrados. eje='x' corre en X con la perfileria entre
    y = p0..p1; eje='y' corre en Y con la perfileria entre x = p0..p1.

    Los travesaños van ENTRE los montantes, no de punta a punta: si no, su
    testa cae en el mismo plano que la del montante y en cada cruce sale un
    cuadro negro. faja_fin recorta la faja en su extremo final para que no
    solape con la del paño contiguo en una esquina.
    """
    C = FA_PERFIL

    def c(nm, u0, u1, z0, z1, mat=None, d=0.0):
        if eje == 'x':
            return _perfil(nm, u0, p0 - d, u1, p1 + d, z0, z1, mat)
        return _perfil(nm, p0 - d, u0, p1 + d, u1, z0, z1, mat)
    t0 = a0 + (C if montantes[0] else 0.0)
    t1 = a1 - (C if montantes[1] else 0.0)
    c(f'{nombre} · banda', a0, a1, -0.010, FA_BASE, MAT['_pizarra_fachada'][0])
    c(f'{nombre} · vierteaguas', a0, a1, FA_BASE, FA_VIERTE)
    if montantes[0]:
        c(f'{nombre} · montante 1', a0, a0 + C, FA_VIERTE, FA_FAJA[0])
    if montantes[1]:
        c(f'{nombre} · montante 2', a1 - C, a1, FA_VIERTE, FA_FAJA[0])
    for k, (z0, z1) in enumerate(travesaños or FA_TRAVESANOS):
        c(f'{nombre} · travesaño {k + 1}', t0, t1, z0, z1)
    c(f'{nombre} · faja', a0, faja_fin or a1, FA_FAJA[0], FA_FAJA[1] + SOLAPE, d=0.006)


def fachada_real():
    """La fachada Oeste tal y como esta en el video (IMG_6570).

    Lo que el modelo tenia mal, pieza a pieza, contra los fotogramas:
      - P2 y P5 iban en pizarra negra. Son de ARENISCA en tonos beige, ocre
        y rosado, a hiladas, con un zocalo oscuro al pie.
      - la perfileria era negra y el paño grande un vidrio unico de 4,6 m.
        Es CREMA, y el paño se parte en vidrio bajo, banda del toldo, vidrio
        alto y faja de rotulo arriba.
      - el paño estrecho del Oeste lleva ademas una hoja practicable entre
        0,86 y 1,72, con dos cierres de laton en su travesaño bajo.
      - el rincon entre el ventanal y P5 no es muro: es un retorno de
        vidrio con la misma perfileria.
      - el porche estaba abierto al cielo. Lo cubre el voladizo del edificio.
    El escaparate del Este y la puerta no se tocan: en el video estan
    detras de la persiana. Tampoco se pone el rotulo del inquilino
    anterior. Los toldos si, recogidos como en las fotos: los pone toldos().
    """
    d = 0.026 + SOLAPE
    YP0, YP1 = 1.561, 1.621                 # fondo de la perfileria del ventanal
    XR = 5.735                              # plano del retorno acristalado
    XP0, XP1 = XR - 0.030, XR + 0.030       # fondo de su perfileria
    # el retorno arranca en la cara Norte de P5, dentro del forro Norte
    # (1,0255..1,0284): en 1,030 quedaba una rendija de 2 a 4 mm
    YR0 = 1.025

    # --- P2: su cara a la calle en arenisca, cubriendo las esquinas de sus
    #     costados, que forra forro_pilares()
    aplacado('Aplacado P2 Sur', 1.290 - d, YP0 - d + SOLAPE, 1.870 + d, YP0,
             -0.010, Z_TECHO, eje='x')
    # --- P5: las tres caras que dan a la calle en arenisca; su costado Este
    #     solo hasta el escaparate (y 0,37): de ahi para dentro es interior
    x0, x1, y0, y1 = 5.731, 6.331, 0.000, 1.000
    aplacado('Aplacado P5 Sur', x0 - d, y0 - d, x1 + d, y0 + SOLAPE,
             -0.010, Z_TECHO, eje='x')
    # hasta el arranque del retorno (YR0), no hasta la cara Norte de P5: si
    # no, entre la arenisca y el perfil del retorno asomaba de arriba abajo
    # el canto del forro Norte, que es de pizarra, como una linea negra
    aplacado('Aplacado P5 Oeste', x0 - d, y0, x0 + SOLAPE, YR0,
             -0.010, Z_TECHO, eje='y')
    aplacado('Aplacado P5 Este', x1 - SOLAPE, y0, x1 + d, 0.370,
             -0.010, Z_TECHO, eje='y')
    losas('Forro P5 Este interior', x1 - SOLAPE, 0.420, x1 + d, y1,
          0.0, Z_TECHO, MAT['_losa_piedra'], fondo=d, eje='y')
    losas('Forro P5 Norte', x0, y1 - SOLAPE, x1 + d, y1 + d,
          0.0, Z_TECHO, MAT['_losa_piedra'], fondo=d, eje='x')

    # --- paño estrecho (x 0,51..1,29) y paño grande (x 1,87..retorno)
    _paño_fachada('Fachada paño 1', 0.510, 1.290, 'x', YP0, YP1)
    _paño_fachada('Fachada paño 2', 1.870, XP1, 'x', YP0, YP1)
    caja('Fachada paño 2 · vidrio', 1.870, 1.573, XR, 1.609, FA_VIERTE - SOLAPE,
         FA_FAJA[1], MAT['vidrio'])
    # junta a tope entre los dos vidrios bajos del paño grande
    caja('Fachada paño 2 · junta', 3.796, 1.571, 3.804, 1.611, FA_VIERTE,
         FA_TRAVESANOS[0][0], MAT['_negro'])
    # la hoja practicable del paño estrecho, con sus dos cierres de laton
    C = FA_PERFIL
    for nm, z0, z1 in (('bajo', 0.860, 0.920), ('alto', 1.660, 1.720)):
        _perfil(f'Fachada paño 1 · hoja {nm}', 0.510 + C, YP0, 1.290 - C, YP1, z0, z1)
    for nm, u0 in (('izq', 0.510 + C), ('der', 1.290 - C - 0.040)):
        _perfil(f'Fachada paño 1 · hoja {nm}', u0, YP0, u0 + 0.040, YP1, 0.920, 1.660)
    for k, xc in enumerate((0.720, 1.080)):
        caja(f'Fachada paño 1 · cierre {k + 1}', xc - 0.018, YP0 - 0.008, xc + 0.018,
             YP0 + SOLAPE, 0.895, 0.935, MAT['_laton'])

    # --- retorno acristalado del rincon, de la cara Norte de P5 al ventanal;
    #     su montante del lado del ventanal es el propio montante de esquina
    # En el video (v1 f_03 y f_06) el retorno solo lleva el travesaño de
    # 2,30 y el remate de arriba: no tiene el de 2,72 de la caja del toldo.
    _paño_fachada('Fachada retorno', YR0, YP0, 'y', XP0, XP1,
                  montantes=(True, False), faja_fin=YP0 - 0.006,
                  travesaños=(FA_TRAVESANOS[0], FA_TRAVESANOS[2]))
    caja('Fachada retorno · vidrio', XR - 0.006, YR0, XR + 0.006, 1.573,
         FA_VIERTE - SOLAPE, FA_FAJA[1], MAT['vidrio'])

    # --- franja de pizarra del extremo Oeste: losas lisas con junta, de
    #     arriba abajo, por la cara Sur del machon SO
    aplacado('Aplacado SO', 0.000, YP0 - d + SOLAPE, 0.510, YP0, -0.010, Z_TECHO,
             eje='x', zocalo=0.0, tonos=MAT['_pizarra_fachada'], gris=0.0)

    # --- balcon curvo del primer piso sobre el porche. En los dos videos el
    #     forjado del porche no es plano ni recto: es el vuelo de un balcon
    #     con el canto curvo hacia la calle, de revoco, con un canto grueso.
    #     Flecha de 1,00 m estimada sobre los fotogramas: +-0,25 m.
    import math
    c, f = 5.731, 1.00
    Rr = (c * c / 4 + f * f) / (2 * f)
    xc, yc = c / 2, -f + Rr
    arco = [(x, yc - math.sqrt(Rr * Rr - (x - xc) ** 2))
            for x in (c * i / 32 for i in range(33))]
    pts = [(0.0, YP0)] + arco + [(c, YP0)]
    bisel(prisma('Balcon curvo sobre el porche', pts, Z_TECHO, Z_TECHO + 0.400,
                 MAT['_revoco_fachada']))
    # la caja de viga que baja del intrados en el extremo Oeste, delante del
    # paño estrecho, con su cara lisa hacia la calle. En v2 f_12 y f_31 cubre
    # la franja de pizarra, el paño estrecho y P2, hasta donde arranca la
    # faja del paño grande (1,87); por detras, contra la faja (1,555).
    # medio mm por dentro de la cara Oeste del aplacado, no a ras
    bisel(caja('Caja de viga del porche', DESPEGUE, 0.000, 1.870, 1.559,
               4.600, Z_TECHO + SOLAPE, MAT['_revoco_fachada']))

    # ================================================ PARTE ESTE
    # Segundo video y las dos fotos: escaparate con montante bajo, puerta
    # retranqueada con persiana, lamas de ventilacion encima de la puerta y
    # el costado Este del retranqueo en arenisca. No se ponen el rotulo, la
    # persiana ni el vinilo translucido del inquilino anterior; el toldo lo
    # pone toldos().
    R = RETRANQUEO
    YE0, YE1 = 0.365, 0.425                 # perfileria en la linea de fachada
    E0, E1 = 6.331, R['x0'] - DESPEGUE      # escaparate, hasta el hueco
    D0, D1 = R['x0'], R['x1']               # la puerta, hasta el cuello
    # Encima del vidrio bajo: travesaño fino a 2,04, un montante bajo de
    # 2,10 a 2,27 con tres barrotes finos, y de 2,27 a la caja del toldo
    # (2,78) una banda crema ciega, la misma altura que la de la persiana de
    # la puerta (fotos 1 y 2). Antes llevaba ahi un travesaño y vidrio.
    _paño_fachada('Fachada escaparate', E0, E1, 'x', YE0, YE1,
                  travesaños=((2.040, 2.100), (2.270, FA_TRAVESANOS[1][1]),
                              FA_TRAVESANOS[2]))
    for k, u in enumerate((E0 + C + 0.045, (E0 + E1) / 2, E1 - C - 0.045)):
        # por la cara de la calle, entre la perfileria (0,365) y el vidrio (0,380)
        caja(f'Fachada escaparate · barrote {k + 1}', u - 0.008, 0.367, u + 0.008,
             0.379, 2.100 - SOLAPE, 2.270 + SOLAPE, MAT['_perfil_crema'])

    # sobre la puerta, en la linea de fachada: banda de la persiana,
    # travesaño, paño de lamas de 2 x 2, travesaño, faja y dintel. A la
    # izquierda le vale el montante del escaparate.
    def e(nm, u0, u1, z0, z1, mat=None, dd=0.0):
        return _perfil(nm, u0, YE0 - dd, u1, YE1 + dd, z0, z1, mat)
    e('Fachada puerta · montante', D1 - C, D1, R['alto'], FA_FAJA[0])
    e('Fachada puerta · banda de la persiana', D0, D1 - C, R['alto'], 2.720)
    for k, (z0, z1) in enumerate(FA_TRAVESANOS[1:]):
        e(f'Fachada puerta · travesaño {k + 1}', D0, D1 - C, z0, z1)
    e('Fachada puerta · faja', D0, D1, FA_FAJA[0], FA_FAJA[1] + SOLAPE, dd=0.006)
    L0, L1 = FA_TRAVESANOS[1][1], FA_TRAVESANOS[2][0]     # 2,78 .. 4,32
    xm = (D0 + D1 - C) / 2
    e('Fachada lamas · montante central', xm - C / 2, xm + C / 2, L0, L1)
    # la fila de arriba es un tercio del paño (foto 2: ~10 lamas arriba y
    # ~25 abajo), no un cuarto
    LT0, LT1 = 3.800, 3.860
    e('Fachada lamas · travesaño', D0, xm - C / 2, LT0, LT1)
    e('Fachada lamas · travesaño 2', xm + C / 2, D1 - C, LT0, LT1)
    # el fondo, 4 mm por delante de la cara interior de la perfileria: en
    # 0,425 justos compartia plano con travesaños y montante central
    # Es negro solo por la cara de la calle, para que las juntas entre lamas
    # se lean oscuras; por dentro, desde el altillo, salian cuatro cuadros
    # negros en la pared: se trasdosa en el crema de la perfileria.
    caja('Fachada lamas · fondo', D0, YE1 - 0.0075, D1 - C, YE1 - 0.0055, L0, L1,
         MAT['_negro'])
    caja('Fachada lamas · trasdos', D0, YE1 - 0.0055, D1 - C, YE1 - SOLAPE, L0, L1,
         MAT['_perfil_crema'])
    n_lamas = 0
    for u0, u1 in ((D0, xm - C / 2), (xm + C / 2, D1 - C)):
        for z0, z1 in ((L0, LT0), (LT1, L1)):
            paso = 0.045
            k = max(1, int((z1 - z0) / paso))
            paso = (z1 - z0) / k
            for i in range(k):
                zc = z0 + paso * (i + 0.5)
                caja(f'Fachada lama {n_lamas + 1}', u0, YE0 + 0.008, u1,
                     YE1 - 0.008, zc - 0.007, zc + 0.007, MAT['_perfil_crema'])
                n_lamas += 1

    # costado Este del retranqueo, forrado de arenisca como los machones; se
    # para antes de las hojas de la puerta
    aplacado('Aplacado retranqueo Este', D1 - d, R['y0'], D1 + SOLAPE, 1.375,
             -0.010, R['alto'], eje='y')
    return 1


# ================================================================ toldos
# Los dos toldos del local, tal y como estan en las fotos de la fachada
# (sep. 2026). Son toldos de brazos articulados, de manivela, en semicofre:
# una capota blanca corrida, atornillada a la fachada con dos soportes, tapa
# por arriba el tubo de enrollamiento con la lona; al recogerlo, los brazos se
# pliegan contra la pared bajo el tubo y la barra de carga -el perfil del
# borde de la lona, con el faldon colgando- queda debajo del rollo. Estan
# recogidos, y asi se ponen.
#   - Entrada (Este): una capota de P5 al cuello de la medianera
#     (x 6,36..9,71), bajo las lamas (2,78), lona roja y DOS barras de carga
#     con su faldon, la de la izquierda sobre el escaparate y la de la
#     derecha sobre la puerta: son dos toldos bajo la misma capota. Las
#     barras, medidas sobre la foto frontal (escala: el hueco de 3,38).
#   - Ventanal (Oeste): sobre el travesaño de 2,72 -el que el video ya daba
#     como sitio de la caja del toldo- de P2 al retorno (x 1,90..5,70), lona
#     crema con franja roja al pie del faldon. El rotulo impreso en el faldon
#     es del inquilino anterior y no se pone.
LONA_ROJA = 'B03C30'
LONA_CREMA = 'D8C7A3'
FRANJA_ROJA = 'C0452B'
ALUMINIO_TOLDO = 'EEEDEA'

# Propuesta: con CM_TOLDOS=abiertos los toldos salen DESPLEGADOS como los
# tenia el local (fotos de la terraza de 2017 y 2021), en lona azzurro Napoli
# y con el logo de Casa Margot en el faldon y encima de la lona. Sin la
# variable salen como estan hoy: recogidos y con sus colores. Son DOS toldos,
# cada uno de una pieza:
#   - el grande, de todo el ventanal: del extremo Oeste (la piedra oscura) a
#     P5, a unos 3,97 de altura -lo que pide su vuelo a 30 grados-, con una
#     sola lona y una sola barra de carga,
#     y en su costado Oeste una cortina lateral que cuelga de la lona hasta
#     el suelo, de la fachada al poste, con una ventana transparente
#   - el de la entrada, bajo la capota de hoy, de P5 al cuello de la
#     medianera, bajo las lamas. Su capota no puede subir, asi que a 30
#     grados vuela 1,0 y no llega a la linea del grande.
# Los dos caen 30 grados y llevan la barra de carga a 2,08, con un faldon de
# 0,22 que queda a 1,85 del suelo, y se apoyan
# delante en postes blancos: el grande en su extremo Oeste, a la altura de P2
# y en su extremo Este; el de la entrada en sus dos extremos y delante de la
# puerta.
TOLDOS_ABIERTOS = os.environ.get('CM_TOLDOS', '') == 'abiertos'
Y_FRENTE_TERRAZA = -1.600            # linea de las barras de carga de A, B y C
Z_BARRA_TERRAZA = 2.080              # lo alto de esas barras
FALDON_ABIERTO = 0.220               # el faldon que lleva el logo
CAIDA_TOLDOS = 30.0                  # grados de pendiente de las lonas
POSTE_R = 0.024                      # postes de aluminio blanco, de 48 mm


def _barra_yz(nombre, a, b, grueso, x0, x1, mat):
    """Un perfil recto de a a b en el plano YZ, de grueso dado, entre x0 y x1."""
    (ya, za), (yb, zb) = a, b
    dy, dz = yb - ya, zb - za
    L = math.hypot(dy, dz)
    ny, nz = -dz / L * grueso / 2, dy / L * grueso / 2
    pts = [(ya + ny, za + nz), (yb + ny, zb + nz), (yb - ny, zb - nz), (ya - ny, za - nz)]
    return panel(nombre, pts, x0, x1, mat)


def _logo_faldon(nombre, xc, y, zc, alto):
    """El logo de Casa Margot, centrado en un faldon que mira a la calle (-Y)."""
    if not os.path.exists(LOGO):
        return None
    w_px, h_px = _medida_png(LOGO)
    ancho = alto * w_px / h_px
    me = bpy.data.meshes.new(nombre)
    me.from_pydata([(xc - ancho / 2, y, zc - alto / 2), (xc + ancho / 2, y, zc - alto / 2),
                    (xc + ancho / 2, y, zc + alto / 2), (xc - ancho / 2, y, zc + alto / 2)],
                   [], [(0, 1, 2, 3)])
    me.uv_layers.new()
    for i, c in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        me.uv_layers[0].data[i].uv = c
    me.materials.append(MT.calca('Logo del toldo', LOGO, rug=0.7))
    ob = bpy.data.objects.new(nombre, me)
    coleccion('Obra').objects.link(ob)
    return ob


def _logo_lona(nombre, xc, a, b, ancho):
    """El logo encima de la lona, a lo largo de su pendiente, de a (arriba,
    en la fachada) a b (abajo, en la barra), en el plano YZ; se lee desde
    arriba con la fachada al fondo."""
    if not os.path.exists(LOGO):
        return None
    w_px, h_px = _medida_png(LOGO)
    alto = ancho * h_px / w_px
    (ya, za), (yb, zb) = a, b
    L = math.hypot(yb - ya, zb - za)
    dy, dz = (yb - ya) / L, (zb - za) / L        # hacia la calle y hacia abajo
    ny, nz = -dz, dy                              # normal hacia arriba
    if nz < 0:
        ny, nz = -ny, -nz
    cy, cz = (ya + yb) / 2 + ny * 0.004, (za + zb) / 2 + nz * 0.004
    h = alto / 2
    v = [(xc - ancho / 2, cy + dy * h, cz + dz * h), (xc + ancho / 2, cy + dy * h, cz + dz * h),
         (xc + ancho / 2, cy - dy * h, cz - dz * h), (xc - ancho / 2, cy - dy * h, cz - dz * h)]
    me = bpy.data.meshes.new(nombre)
    me.from_pydata(v, [], [(0, 1, 2, 3)])
    me.uv_layers.new()
    for i, c in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        me.uv_layers[0].data[i].uv = c
    me.materials.append(MT.calca('Logo de la lona', LOGO, rug=0.8))
    ob = bpy.data.objects.new(nombre, me)
    coleccion('Obra').objects.link(ob)
    return ob


def _cortina_lateral(nombre, x, a, b, y_pared, tela, al, grueso=0.004):
    """Cortina que cuelga del costado de la lona hasta el suelo, de la fachada
    al poste, con su contrapeso abajo y una ventana transparente, como la de
    la foto de 2017. x: su plano; a..b: el borde de la lona (arriba en la
    fachada, abajo en la barra)."""
    (ya, za), (yb, zb) = a, b
    z_pie, z_bajo = 0.160, 0.800            # contrapeso y alto del zocalo de lona
    marco = 0.220                            # tela alrededor de la ventana

    def borde(y):                            # cota del borde de la lona en y
        return za + (zb - za) * (ya - y) / (ya - yb)
    x0, x1 = x - grueso / 2, x + grueso / 2
    y_f, y_p = min(ya, y_pared), yb          # de la fachada a la barra
    obs = []
    # zocalo de lona, de lado a lado
    obs.append(panel(f'{nombre} · zocalo', [(y_f, z_pie), (y_p, z_pie), (y_p, z_bajo),
                                            (y_f, z_bajo)], x0, x1, tela))
    # franjas de delante y de detras, hasta el borde de la lona
    for nm, u0, u1 in (('trasera', y_f - marco, y_f), ('delantera', y_p, y_p + marco)):
        u0, u1 = max(u0, y_p), min(u1, y_f)
        obs.append(panel(f'{nombre} · franja {nm}', [(u1, z_bajo), (u0, z_bajo),
                                                     (u0, borde(u0)), (u1, borde(u1))], x0, x1, tela))
    # franja de arriba, bajo la lona, de una franja a la otra
    wa, wb = y_f - marco, y_p + marco
    obs.append(panel(f'{nombre} · franja alta', [(wa, borde(wa) - marco), (wb, borde(wb) - marco),
                                                 (wb, borde(wb)), (wa, borde(wa))], x0, x1, tela))
    # la ventana de PVC cristal
    obs.append(panel(f'{nombre} · ventana', [(wa, z_bajo), (wb, z_bajo), (wb, borde(wb) - marco),
                                             (wa, borde(wa) - marco)], x0 + 0.001, x1 - 0.001,
                     MAT['vidrio']))
    # contrapeso blanco al pie
    obs.append(caja(f'{nombre} · contrapeso', x0 - 0.012, y_p, x1 + 0.012, y_f,
                    z_pie - 0.040, z_pie, al))
    return obs


def _toldo(nombre, x0, x1, yf, z_cap, fondo, lona, barras, faldon, logo=False,
           logo_arriba=False):
    """Toldos de brazos articulados en semicofre, en una fachada que da al
    Sur (-Y), bajo una misma capota.

    x0..x1: la capota; yf: la cara de la fachada; z_cap: lo alto de la
    capota; fondo: lo que vuela la capota; faldon: [(alto, color), ...] de
    arriba abajo. barras: un dict por toldo, con a0..a1 (su ancho) y, si esta
    desplegado, 'salida' (vuelo en horizontal) y 'z' (lo alto de su barra de
    carga) o 'caida' (grados), y 'postes' (las x de sus postes). Recogido, la
    barra queda bajo el rollo y los brazos plegados detras de ella.
    Desplegado, la lona baja del rollo a la barra de carga, dos brazos por
    toldo la sostienen y los postes la apoyan en el suelo; con logo, el de
    Casa Margot va centrado en cada faldon.
    """
    al = MT.liso(f'{nombre} · aluminio', MT.srgb(ALUMINIO_TOLDO), 0.35)
    tela = MT.liso(f'{nombre} · lona', MT.srgb(lona), 0.85, sheen_=True)
    y0, y1 = yf - fondo, yf - DESPEGUE
    obs = []
    # capota: tapa y un frente corto, con sus dos testeros. Es un semicofre:
    # el rollo de lona asoma por debajo del frente, como en las fotos.
    obs.append(caja(f'{nombre} · capota', x0, y0, x1, y1, z_cap - 0.020, z_cap, al))
    obs.append(caja(f'{nombre} · capota frente', x0, y0, x1, y0 + 0.015,
                    z_cap - 0.075, z_cap - 0.020, al))
    for k, xa in enumerate((x0, x1 - 0.008)):
        obs.append(caja(f'{nombre} · testero {k + 1}', xa, y0 + 0.015, xa + 0.008, y1,
                        z_cap - 0.150, z_cap - 0.020, al))
        # soporte a la pared, detras del rollo
        xs = x0 + 0.04 if k == 0 else x1 - 0.09
        obs.append(caja(f'{nombre} · soporte {k + 1}', xs, yf - 0.050, xs + 0.050, y1,
                        z_cap - 0.210, z_cap - 0.020, al))
    abierto = any(b.get('salida', 0) > 0 for b in barras)
    # el tubo con la lona enrollada, entre los testeros; desplegado queda
    # casi solo el tubo
    r = 0.035 if abierto else 0.050
    yr, zr = yf - fondo / 2, z_cap - 0.095
    rollo = cilindro(f'{nombre} · lona enrollada', 0.0, 0.0, r, 0.0,
                     x1 - x0 - 0.020, tela, 'Obra', 32)
    rollo.rotation_euler = (0.0, math.pi / 2, 0.0)
    rollo.location = (x0 + 0.010, yr, zr)
    obs.append(rollo)
    logos = []
    for k, b in enumerate(barras):
        a0, a1 = b['a0'], b['a1']
        salida = b.get('salida', 0.0)
        if salida <= 0:
            yb, zb = y0 + 0.070, zr - r         # la barra, debajo del rollo
        else:
            yb = yr - salida
            zb = b['z'] if 'z' in b else zr - r - salida * math.tan(math.radians(b['caida']))
            z_lona = zr - r
            # la lona, del rollo a la barra de carga
            obs.append(_barra_yz(f'{nombre} · lona {k + 1}', (yr, z_lona), (yb + 0.035, zb),
                                 0.004, a0, a1, tela))
            # dos brazos, de la pared a la barra, con el codo casi abierto y
            # siempre por debajo de la lona
            hombro = (yf - 0.030, zr - 0.220)
            punta = (yb + 0.030, zb - 0.030)
            ym = (hombro[0] + punta[0]) / 2
            z_lona_m = z_lona + (zb - z_lona) * (yr - ym) / (yr - yb - 0.035)
            codo = (ym, min((hombro[1] + punta[1]) / 2 + 0.060, z_lona_m - 0.045))
            for j, xa in enumerate((a0 + 0.080, a1 - 0.080 - 0.035)):
                obs.append(_barra_yz(f'{nombre} · brazo {k + 1}.{j + 1} a', hombro, codo,
                                     0.040, xa, xa + 0.035, al))
                obs.append(_barra_yz(f'{nombre} · brazo {k + 1}.{j + 1} b', codo, punta,
                                     0.036, xa, xa + 0.035, al))
                obs.append(caja(f'{nombre} · hombro {k + 1}.{j + 1}', xa - 0.010, yf - 0.060,
                                xa + 0.045, y1, zr - 0.260, zr - 0.180, al))
            if logo_arriba:
                lg = _logo_lona(f'{nombre} · logo en la lona {k + 1}', (a0 + a1) / 2,
                                (yr, z_lona), (yb + 0.035, zb),
                                min(0.42 * (a1 - a0), 0.55 * (yr - yb) * 3.1))
                if lg:
                    logos.append(lg)
            if b.get('cortina'):
                xc_ = a0 - 0.004 if b['cortina'] == 'oeste' else a1 + 0.004
                obs += _cortina_lateral(f'{nombre} · cortina {b["cortina"]}', xc_,
                                        (yr, z_lona - 0.004), (yb + 0.035, zb - 0.004),
                                        yf - 0.040, tela, al)
            # los postes, del suelo a la barra, con su placa de anclaje
            for j, xp in enumerate(b.get('postes', ())):
                yp = yb - 0.030
                obs.append(cilindro(f'{nombre} · poste {k + 1}.{j + 1}', xp, yp, POSTE_R,
                                    0.0, zb - 0.055 + SOLAPE, al, 'Obra', 24))
                obs.append(caja(f'{nombre} · placa del poste {k + 1}.{j + 1}', xp - 0.070,
                                yp - 0.070, xp + 0.070, yp + 0.070, 0.0, 0.008, al))
        # la barra de carga y su faldon por la cara de fuera
        obs.append(caja(f'{nombre} · barra de carga {k + 1}', a0, yb - 0.060, a1,
                        yb, zb - 0.055, zb, al))
        z = zb - 0.015
        for i, (alto, color) in enumerate(faldon):
            m = tela if color == lona else MT.liso(f'{nombre} · faldon {i}',
                                                   MT.srgb(color), 0.85, sheen_=True)
            obs.append(caja(f'{nombre} · faldon {k + 1}.{i + 1}', a0, yb - 0.0645, a1,
                            yb - 0.0605, z - alto, z, m))
            z -= alto
        if logo:
            alto_f = sum(a for a, _ in faldon)
            lg = _logo_faldon(f'{nombre} · logo {k + 1}', (a0 + a1) / 2, yb - 0.0655,
                              zb - 0.015 - alto_f / 2, alto_f * 0.70)
            if lg:
                logos.append(lg)
    for o in obs:
        if o is not rollo and 'poste' not in o.name:
            bisel(o, 0.0015, segs=2)
    return len(obs) + len(logos)


def toldos():
    """Los toldos de la fachada, donde estan en la realidad.

    Recogidos y con sus colores, como hoy; con CM_TOLDOS=abiertos,
    desplegados como en 2021, en azzurro Napoli y con el logo en el faldon.
    """
    if not TOLDOS_ABIERTOS:
        n = _toldo('Toldo de la entrada', 6.362, 9.710 - DESPEGUE, 0.365, 2.780, 0.200,
                   LONA_ROJA, barras=(dict(a0=6.500, a1=7.860), dict(a0=8.420, a1=9.580)),
                   faldon=((0.220, LONA_ROJA),))
        n += _toldo('Toldo del ventanal', 1.905, 5.700, 1.561, 2.830, 0.180,
                    LONA_CREMA, barras=(dict(a0=1.925, a1=5.680),),
                    faldon=((0.120, LONA_CREMA), (0.030, FRANJA_ROJA)))
        return n
    az = MT.AZZURRO
    f = ((FALDON_ABIERTO, az),)
    yF, zF = Y_FRENTE_TERRAZA, Z_BARRA_TERRAZA

    def hasta_la_linea(yf, fondo, a0, a1, postes):
        return dict(a0=a0, a1=a1, salida=yf - fondo / 2 - yF, z=zF, postes=postes)
    # el grande: una capota de la piedra del extremo Oeste a P5, por delante
    # de la cara del aplacado (1,535), una lona, una barra de carga, tres
    # postes y la cortina lateral en su costado Oeste
    tg = math.tan(math.radians(CAIDA_TOLDOS))
    grande = hasta_la_linea(1.535, 0.180, 0.040, 5.680, (0.075, 1.895, 5.650))
    grande['cortina'] = 'oeste'
    # la capota, tan alta como pida el vuelo hasta la linea a esa caida
    z_cap = zF + grande['salida'] * tg + 0.130
    n = _toldo('Toldo grande', 0.020, 5.700, 1.535, z_cap, 0.180, az,
               barras=(grande,), faldon=f, logo=True, logo_arriba=True)
    # el de la entrada: bajo las lamas, de P5 al cuello, una lona y tres
    # postes, el del medio delante de la puerta
    # su capota se queda bajo las lamas: a esa caida vuela lo que da
    sal_e = (2.780 - 0.130 - zF) / tg
    n += _toldo('Toldo de la entrada', 6.362, 9.710 - DESPEGUE, 0.365, 2.780, 0.200, az,
                barras=(dict(a0=6.420, a1=9.650, salida=sal_e, z=zF,
                             postes=(6.450, 7.930, 9.620)),),
                faldon=f, logo=True, logo_arriba=True)
    return n


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
    # B1 iba a 90, con la puerta y el display contra el frente de madera:
    # desde el pasillo solo se le veia la trasera, un cubo con un cable.
    'V1': 90, 'V2': 90, 'B1': -90, 'B3': -90, 'B2': 0,
    # La chopera mira al Norte, no al Oeste. El objeto tiene el frente en -Y:
    # ahi estan los tres caños, las manetas y la rejilla donde va el vaso, y
    # la columna queda detras. Con -90 los caños apuntaban a la pared Oeste,
    # contra la que nadie puede ponerse: la tabla de P2 llega hasta ella. El
    # que tira la cerveza esta al Norte, en la calle de servicio, asi que el
    # frente tiene que girar 180 y quedar de cara a el.
    'B4': 180,
}
# Correcciones en Y sobre el centro del hueco del plano. La cafetera A1 se
# metia 30 mm en el forro de P1: se corre 32 mm al Sur y el molino A2 con
# ella, hasta tocar la granizadora A3, que baja los 2 mm que faltan. Al Sur
# de A3 la mesada esta libre hasta el peto (y 2,611).
CORRE_Y = {'A1': -0.032, 'A2': -0.032, 'A3': -0.002}


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


# Arranque de la vitrina acortada. El plano la pone de 0,600 a 1,250, pero
# bajo V2 mete el lavavasos B1, que mide 0,670: el propio plano no cabe. Con
# la vitrina comprada, que tiene la bandeja a 0,40, el lavavasos se metia 27 cm
# dentro de ella. El cliente la quiere mas CORTA, no mas alta: la corona se
# queda en 1,250 y la bandeja sube hasta aqui, 30 mm por encima del
# lavavasos para que quepa la balda en la que apoya.
VITRINA_BASE = 0.700
# Trasera de las vitrinas: la del plano (x 1,90). El modelo comprado mide 0,70
# de fondo y, con el frente enrasado en 2,530, su trasera caia en 1,830: la
# esquina Sur de V2 y la balda se metian 43 mm en P2 y en su forro (hasta
# 1,896 entre y 1,968 y 2,011). Se escala el fondo, no se mueve el frente.
VITRINA_TRASERA = 1.900


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
        # El estante A6 va colgado del muro, sin patas: separado 30 mm como
        # los aparatos de suelo quedaba en el aire
        if tag == 'A6':
            s = 0.0
        if g == 90:
            cx += s
        elif g == -90:
            cx -= s
        elif g == 0:
            cy -= s
        cy += CORRE_Y.get(tag, 0.0)
        raiz_ob = raiz if raiz is not None else mallas[0]
        padres = [o for o in traidos if o.parent is None]
        import mathutils
        M = (mathutils.Matrix.Translation((cx, cy, z0))
             @ mathutils.Matrix.Rotation(math.radians(g), 4, 'Z'))
        for o in padres:
            o.matrix_world = M @ o.matrix_world
        if tag in ('V1', 'V2'):
            # El modelo comprado trae un zocalo macizo de 1,830 a 2,490 que
            # cierra todo el bajo de la vitrina. En obra ahi no hay caja: hay
            # un hueco abierto por detras con el motor dentro, a la derecha, y
            # el lavavasos B1 al lado. Se BORRA, no se oculta: render() llama
            # a mostrar_todo() y un hide_render se perderia en la primera vista.
            for o in [o for o in traidos
                      if o.type == 'MESH' and o.name.split('.')[0] == 'zocalo']:
                traidos.remove(o)
                bpy.data.objects.remove(o, do_unlink=True)
            # Acortarla, no elevarla: escala en Z respecto de la corona, que
            # no se mueve, hasta que la bandeja quede en VITRINA_BASE.
            bpy.context.view_layer.update()

            def _zs(o):
                return [(o.matrix_world @ Vector(c)).z for c in o.bound_box]
            mallas_v = [o for o in traidos if o.type == 'MESH']
            z_top = max(max(_zs(o)) for o in mallas_v)
            z_band = min(min(_zs(o)) for o in mallas_v
                         if o.name.startswith('plano exposicion'))
            k = (z_top - VITRINA_BASE) / (z_top - z_band)
            S = (mathutils.Matrix.Translation((0, 0, z_top))
                 @ mathutils.Matrix.Scale(k, 4, (0, 0, 1))
                 @ mathutils.Matrix.Translation((0, 0, -z_top)))
            for o in padres:
                o.matrix_world = S @ o.matrix_world
            bpy.context.view_layer.update()
            # Lo que la vitrina traia por debajo de la bandeja -pies,
            # rejilla del condensador, mando- se quedaria flotando en el
            # hueco: fuera, de las hojas hacia la raiz.
            fuera = [o for o in traidos if o.type == 'MESH'
                     and max(_zs(o)) < VITRINA_BASE - 0.020]
            fuera.sort(key=lambda o: -len(o.children_recursive))
            fuera.reverse()
            for o in fuera:
                traidos.remove(o)
                bpy.data.objects.remove(o, do_unlink=True)
            padres = [o for o in traidos if o.parent is None]
            xs = [(o.matrix_world @ Vector(c)).x for o in traidos
                  if o.type == 'MESH' for c in o.bound_box]
            x_fr, x_tr = max(xs), min(xs)
            kx = (x_fr - VITRINA_TRASERA) / (x_fr - x_tr)
            S = (mathutils.Matrix.Translation((x_fr, 0, 0))
                 @ mathutils.Matrix.Scale(kx, 4, (1, 0, 0))
                 @ mathutils.Matrix.Translation((-x_fr, 0, 0)))
            for o in padres:
                o.matrix_world = S @ o.matrix_world
            bpy.context.view_layer.update()
            h = huecos[tag]
            luz_expositor(tag, (h[0], h[1], VITRINA_BASE, h[3], h[4], h[5]))
            puestos.append(tag)
            continue
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
        # cada una bajo su balda, alumbrando HACIA ABAJO. Giradas 180 grados
        # emitian hacia arriba y la camara las veia como laminas blancas
        # flotando a media vitrina.
        z = z0 + (z1 - z0) * (i + 1) / (n + 0.25)
        lz = bpy.data.lights.new(f'{tag} luz interior {i + 1}', 'AREA')
        lz.shape = 'RECTANGLE'
        lz.size = max(0.12, min(x1 - x0, y1 - y0) * 0.7)
        lz.size_y = tam
        lz.energy = pot
        lz.color = (0.95, 0.97, 1.0)
        ob = bpy.data.objects.new(f'{tag} luz interior {i + 1}', lz)
        ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, z)
        # alumbra el genero pero no se ve: ni de frente, ni a traves del
        # cristal del mueble, ni reflejada en sus baldas de vidrio
        ob.visible_camera = False
        ob.visible_transmission = False
        ob.visible_glossy = False
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
# escalera -CAJA_ESC_PB, que el plano trae como panel- solo cubre de y 4,829
# (el montante gris) a 7,738, asi que en ese tramo no hay muro donde pintar.
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
    hace habitacion: antepecho de vidrio, luminarias y el suelo, que se pone
    en suelos_y_techos().
    """
    col = 'Planta alta'
    z = Z_PA
    # --- antepechos de vidrio del vacio, sin pasamanos: el cliente quiere
    #     el vidrio limpio, sin el reborde de roble que llevaba encima
    # Son los 'Borde Oeste/Sur del vacio' del plano, que traen vidrio de 50
    # mm; se descartan alli y se ponen aqui a 12, para que no haya dos
    # vidrios pegados. El Sur llega hasta donde lo lleva el plano, 8,759.
    bordes = [((2.461, 3.988), (2.461, 7.509)),      # borde Oeste del vacio
              ((2.461, 3.988), (8.759, 3.988))]      # borde Sur del vacio
    for k, ((ax, ay), (bx, by)) in enumerate(bordes):
        if abs(bx - ax) < 1e-6:
            caja(f'Antepecho PA {k + 1}', ax - 0.006, ay, ax + 0.006, by,
                 z, z + E.H_BARANDA, MAT['vidrio'], col)
        else:
            caja(f'Antepecho PA {k + 1}', ax, ay - 0.006, bx, ay + 0.006,
                 z, z + E.H_BARANDA, MAT['vidrio'], col)
    # En el testero Norte iba una celosia de listones con su banda azzurro,
    # gemela de la de abajo. Ese testero es el fondo del aseo, del inodoro y
    # del almacen, asi que quedaba dentro de ellos: fuera, lo pide el cliente.
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
            # Ojo: el 'Colgante 6' del plano, en (8,90, 0,95), cae dentro del
            # cubo de la entrada y cuelga a 1,72, delante de la puerta. Se
            # deja donde lo pone el plano: pasarlo tras la puerta lo ponia
            # delante del logo de la pared del plotter.
            luminaria_colgante(nm, x, y, s['z0'])
        elif nm.startswith('Aplique'):
            if x < 1.2:
                # los de la cocina, contra la cara del Muro Oeste (x 0,250):
                # con '-X' la caja daba la espalda al muro y la luz quedaba
                # dentro de el, en x 0,245
                aplique(nm, 0.250 + DESPEGUE, y, (s['z0'] + s['z1']) / 2, '+X')
            else:
                aplique(nm, x, y, (s['z0'] + s['z1']) / 2, '-Y')
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
    # el del aseo y el del almacen, contra la medianera Norte (8,957), metidos
    # 2 mm en ella. Iban en la celosia (8,720), que ya no esta.
    for i, (x, y) in enumerate(((2.90, 8.959), (5.90, 8.959))):
        aplique(f'Aplique PA {i + 1}', x, y, Z_PA + 1.950, '-Y')

    # --- cocina: pantallas estancas suspendidas. Los cuatro empotrados que el
    #     proyecto pone aqui caen en la doble altura y no alumbran nada.
    # Colgaban a 2,560 con tirantes hasta los 5,06 porque la cocina no tenia
    # techo. Ahora lo tiene (Z_TECHO_COCINA): van adosadas a el.
    # la tercera iba en y 8,40, dentro de la campana KC (7,778..8,978), que
    # ya lleva su propia luz. Las tres, a paso igual entre el machon P1 -su
    # forro Norte llega a 5,387 y la pantalla empieza en x 0,45, dentro de
    # el- y la campana (7,778)
    for i, y in enumerate((5.45, 6.35, 7.25)):
        x0_, x1_ = 0.45, 2.25
        caja(f'Cocina · pantalla {i + 1}', x0_, y - 0.055, x1_, y + 0.055,
             Z_TECHO_COCINA - 0.060, Z_TECHO_COCINA + SOLAPE, MAT['_opal'],
             'Luces')
        lz = bpy.data.lights.new(f'Cocina luz {i + 1}', 'AREA')
        lz.shape = 'RECTANGLE'
        lz.size, lz.size_y = x1_ - x0_, 0.11
        lz.energy = 55.0
        lz.color = (1.0, 0.95, 0.88)
        ob = bpy.data.objects.new(f'Cocina luz {i + 1}', lz)
        ob.location = ((x0_ + x1_) / 2, y, Z_TECHO_COCINA - 0.068)
        coleccion('Luces').objects.link(ob)

    # --- tira de LED bajo el estante de la trasbarra: la luz de trabajo y el
    #     brillo que hace que las botellas se lean
    # arranca en la cara del muro (0,250), no a 10 mm de ella, y su cara de
    # arriba toca la punta de las cartelas del estante A6 (1,600): con el
    # estante contra el muro ya no las tocaba y quedaba en el aire
    caja('LED trasbarra', 0.250, 2.05, 0.60, 4.72, 1.592, 1.600,
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
    texturas = None
    if MAXIMA:
        r4 = os.path.join(PH, aid, '4k', f'{aid}.blend')
        if os.path.exists(r4):
            ruta, texturas = r4, os.path.join(PH, aid, '4k', 'textures')
        else:
            print(f'   (falta el modelo {aid} a 4K: va con el de 2K)')
    if not os.path.exists(ruta):
        print(f'   (falta el modelo {aid})')
        _importados[clave] = []
        return []
    antes = set(bpy.data.objects.keys())
    with bpy.data.libraries.load(ruta, link=False) as (src, dst):
        elegidos = _elegir_lod(src.objects, lod)
        dst.objects = [n for n in elegidos if nombres is None or n in nombres]
    obs = [o for o in bpy.data.objects if o.name not in antes and o.type == 'MESH']
    _recolocar_texturas(aid, texturas)
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


def _recolocar_texturas(aid, d=None):
    """Los .blend de Poly Haven apuntan a texturas .exr y el descargador las
    trae en png/jpg: sin esto los modelos pierden rugosidad y normal. d es la
    carpeta de texturas del modelo que se ha cargado (la de 4K con MAXIMA)."""
    if d is None:
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


def taza(nombre, x, y, z, col='Decoracion', r=0.038, h=0.062, con_plato=True):
    """Taza con su plato. z es donde apoya el conjunto.

    El plato iba en z - 0,009 y la taza en z: el plato quedaba metido 9 mm en
    el tablero. Ahora el plato apoya en z y la taza en el fondo del plato,
    5 mm mas arriba. Sin plato (las del calientatazas) la taza apoya en z.
    """
    perfil = [(0.000, 0.000), (r * 0.62, 0.000), (r * 0.66, 0.004), (r * 0.92, h * 0.72),
              (r, h), (r - 0.0035, h), (r * 0.90, h * 0.72), (r * 0.60, 0.006),
              (0.000, 0.006)]
    ob = _revolucion(nombre, perfil, x, y, z + (0.005 if con_plato else 0.0),
                     MAT['_blanco'], col, 32)
    if not con_plato:
        return [ob]
    pl = _revolucion(f'{nombre} plato', [(0.000, 0.000), (0.060, 0.000), (0.066, 0.004),
                                         (0.068, 0.009), (0.064, 0.009), (0.058, 0.005),
                                         (0.000, 0.005)], x, y, z,
                     MAT['_blanco'], col, 32)
    return [ob, pl]


def plato(nombre, x, y, z, r=0.115, col='Decoracion'):
    perfil = [(0.000, 0.000), (r * 0.80, 0.000), (r, 0.014), (r, 0.019),
              (r * 0.78, 0.006), (0.000, 0.006)]
    return _revolucion(nombre, perfil, x, y, z, MAT['_blanco'], col, 40)


# Lo que ocupa en planta una botella de las de botella(): la etiqueta es una
# caja de 2 x 0,99 r de lado y sus esquinas llegan a 53 mm del eje. Con el
# radio del vidrio (38 mm) el aceite y el vinagre se metian las etiquetas.
R_BOTELLA = 0.054


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
    # la pasta apoya en el fondo del vidrio (a 4 mm en el canto): a 10 mm flotaba
    relleno = cilindro(f'{nombre} pasta', x, y, r * 0.92, z + 0.004, z + alto - 0.045,
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


# ----------------------------------------------------- la mesa de trattoria
_MAT_MESA = {}


def _mat_mesa(clave):
    """Materiales de las piezas de mesa, creados una sola vez."""
    if clave not in _MAT_MESA:
        _MAT_MESA[clave] = {
            'fiasco': lambda: MT.vidrio('Vidrio de fiasco', (0.10, 0.24, 0.11), 0.02),
            'paja': lambda: MT.liso('Paja del fiasco', MT.srgb('C9A25C'), 0.85, sheen_=True),
            'paja_osc': lambda: MT.liso('Atadura de paja', MT.srgb('8E6A34'), 0.8),
            'cera': lambda: MT.liso('Cera de vela', MT.srgb('F3EDE0'), 0.45),
            'llama': lambda: MT.emision('Llama de vela', (1.0, 0.62, 0.26), 30.0),
            'mecha': lambda: MT.liso('Mecha', MT.srgb('1E1B18'), 0.9),
            'vinagre': lambda: MT.vidrio('Vidrio de vinagre', (0.20, 0.08, 0.035), 0.02),
            'sal': lambda: MT.liso('Molinillo blanco', MT.srgb('ECE8DF'), 0.35, coat=0.3),
            'tierra': lambda: MT.liso('Tierra de maceta', MT.srgb('3B2A1E'), 0.95),
            'albahaca': lambda: MT.liso('Albahaca', MT.srgb('3F7C2C'), 0.5, sheen_=True),
            'grissini': lambda: MT.liso('Grissini', MT.srgb('D8AF6C'), 0.75),
            'vaso': lambda: MT.vidrio('Vidrio de vaso', (0.97, 0.99, 0.98), 0.0),
        }[clave]()
    return _MAT_MESA[clave]


def fiasco(nombre, x, y, z, col='Decoracion'):
    """Fiasco de Chianti con su funda de paja y una vela encendida."""
    perfil = [(0.000, 0.000), (0.030, 0.000), (0.052, 0.012), (0.064, 0.040),
              (0.066, 0.070), (0.058, 0.105), (0.040, 0.132), (0.018, 0.155),
              (0.013, 0.175), (0.012, 0.250), (0.015, 0.254), (0.015, 0.262),
              (0.000, 0.262)]
    _revolucion(nombre, perfil, x, y, z, _mat_mesa('fiasco'), col, 36)
    # la paja, 3 mm por fuera del vidrio, hasta pasada la panza
    paja = [(0.030, 0.0005), (0.055, 0.012), (0.067, 0.040), (0.069, 0.070),
            (0.061, 0.104), (0.050, 0.118)]
    _revolucion(f'{nombre} paja', paja, x, y, z, _mat_mesa('paja'), col, 36)
    _revolucion(f'{nombre} atadura', [(0.0505, 0.112), (0.0535, 0.114),
                                      (0.0535, 0.121), (0.0485, 0.123)],
                x, y, z, _mat_mesa('paja_osc'), col, 36)
    # la vela, metida en el cuello, con tres regueros de cera
    zb = z + 0.250
    cilindro(f'{nombre} vela', x, y, 0.0105, zb, zb + 0.080, _mat_mesa('cera'), col, 24)
    for k, (a, l) in enumerate(((0.3, 0.050), (2.4, 0.030), (4.3, 0.065))):
        rx, ry = x + 0.0125 * math.cos(a), y + 0.0125 * math.sin(a)
        cilindro(f'{nombre} cera {k + 1}', rx, ry, 0.0028, zb + 0.004 - l,
                 zb + 0.010, _mat_mesa('cera'), col, 10)
    cilindro(f'{nombre} mecha', x, y, 0.0009, zb + 0.080, zb + 0.086,
             _mat_mesa('mecha'), col, 8)
    llama = _revolucion(f'{nombre} llama', [(0.000, 0.000), (0.0035, 0.004),
                                            (0.0042, 0.010), (0.0028, 0.017),
                                            (0.000, 0.024)],
                        x, y, zb + 0.083, _mat_mesa('llama'), col, 16)
    llama.visible_shadow = False
    lz = bpy.data.lights.new(f'{nombre} luz', 'POINT')
    lz.energy = 0.9
    lz.shadow_soft_size = 0.006
    lz.color = (1.0, 0.70, 0.40)
    ob = bpy.data.objects.new(f'{nombre} luz', lz)
    ob.location = (x, y, zb + 0.095)
    coleccion(col).objects.link(ob)
    return llama


def molinillo(nombre, x, y, z, alto=0.140, mat=None, col='Decoracion'):
    """Molinillo de sal o de pimienta."""
    r = 0.021
    perfil = [(0.000, 0.000), (r, 0.000), (r, 0.004), (r * 0.90, 0.012),
              (r * 0.78, alto * 0.45), (r * 0.95, alto * 0.62), (r * 0.95, alto * 0.80),
              (r * 0.70, alto * 0.90), (r * 0.42, alto * 0.95), (0.009, alto),
              (0.000, alto)]
    return _revolucion(nombre, perfil, x, y, z, mat or MAT['mesa'], col, 28)


def albahaca(nombre, x, y, z, col='Decoracion'):
    """Maceta de barro con albahaca: el verde de la mesa italiana."""
    import zlib
    import mathutils
    maceta = [(0.000, 0.000), (0.033, 0.000), (0.035, 0.004), (0.044, 0.060),
              (0.048, 0.061), (0.048, 0.070), (0.043, 0.070), (0.040, 0.064),
              (0.000, 0.064)]
    _revolucion(nombre, maceta, x, y, z, MAT['_terracota'], col, 32)
    cilindro(f'{nombre} tierra', x, y, 0.041, z + 0.056, z + 0.063,
             _mat_mesa('tierra'), col, 24)
    rnd = random.Random(zlib.crc32(nombre.encode()))
    bm = bmesh.new()
    # Siete tallos que salen de la tierra (arrancan 5 mm dentro) y las hojas
    # cogidas a ellos por pares, en tres nudos. Antes eran 34 hojas sueltas
    # entre 20 y 30 mm por encima de la tierra: una nube verde en el aire.
    # Todo cabe en 62 mm de radio, dentro de lo que se le reserva en la mesa.
    for t in range(7):
        th = 2 * math.pi * t / 7 + rnd.uniform(-0.3, 0.3)
        incl = rnd.uniform(0.08, 0.30)               # desde la vertical
        largo = rnd.uniform(0.055, 0.078)
        base = Vector((x + 0.006 * math.cos(th), y + 0.006 * math.sin(th), z + 0.058))
        eje = Vector((math.sin(incl) * math.cos(th), math.sin(incl) * math.sin(th),
                      math.cos(incl)))
        g = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.0022,
                                  radius2=0.0012, depth=largo)
        M = (mathutils.Matrix.Translation(base + eje * (largo / 2))
             @ Vector((0, 0, 1)).rotation_difference(eje).to_matrix().to_4x4())
        bmesh.ops.transform(bm, matrix=M, verts=g['verts'])
        for n, f in enumerate((0.45, 0.72, 1.0)):
            nudo = base + eje * (largo * f)
            for lado in (0, 1):
                a = th + (math.pi / 2 if n % 2 else 0.0) + lado * math.pi \
                    + rnd.uniform(-0.25, 0.25)
                tam = rnd.uniform(0.80, 1.0) * (1.10 - 0.25 * f)
                sube = rnd.uniform(0.35, 0.9)
                # la hoja arranca en el tallo: su centro, a media hoja de el
                d = Vector((math.cos(a) * math.cos(sube), math.sin(a) * math.cos(sube),
                            math.sin(sube)))
                c = nudo + d * (0.016 * tam)
                g = bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=1.0)
                M = (mathutils.Matrix.Translation(c)
                     @ mathutils.Matrix.Rotation(a, 4, 'Z')
                     @ mathutils.Matrix.Rotation(-sube, 4, 'Y')
                     @ mathutils.Matrix.Diagonal((0.019 * tam, 0.011 * tam, 0.0022, 1.0)))
                bmesh.ops.transform(bm, matrix=M, verts=g['verts'])
    me = bpy.data.meshes.new(f'{nombre} hojas')
    bm.to_mesh(me)
    bm.free()
    for pl in me.polygons:
        pl.use_smooth = True
    me.materials.append(_mat_mesa('albahaca'))
    ob = bpy.data.objects.new(f'{nombre} hojas', me)
    coleccion(col).objects.link(ob)
    return ob


def grissini(nombre, x, y, z, n=11, col='Decoracion'):
    """Vaso de grissini, un poco abiertos."""
    import zlib
    import mathutils
    vaso = [(0.000, 0.000), (0.030, 0.000), (0.032, 0.003), (0.036, 0.110),
            (0.033, 0.110), (0.029, 0.007), (0.000, 0.007)]
    _revolucion(f'{nombre} vaso', vaso, x, y, z, _mat_mesa('vaso'), col, 32)
    rnd = random.Random(zlib.crc32(nombre.encode()))
    bm = bmesh.new()
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.2, 0.2)
        r0 = rnd.uniform(0.006, 0.020)
        largo = rnd.uniform(0.200, 0.250)
        g = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.0045,
                                  radius2=0.0040, depth=largo)
        M = (mathutils.Matrix.Translation((x + r0 * math.cos(a), y + r0 * math.sin(a),
                                           z + 0.008))
             @ mathutils.Matrix.Rotation(a, 4, 'Z')
             @ mathutils.Matrix.Rotation(rnd.uniform(0.07, 0.20), 4, 'Y')
             @ mathutils.Matrix.Translation((0, 0, largo / 2)))
        bmesh.ops.transform(bm, matrix=M, verts=g['verts'])
    me = bpy.data.meshes.new(f'{nombre} palitos')
    bm.to_mesh(me)
    bm.free()
    me.materials.append(_mat_mesa('grissini'))
    ob = bpy.data.objects.new(f'{nombre} palitos', me)
    coleccion(col).objects.link(ob)
    return ob


def _colocar(ocup, r, dentro, nota, paso=0.015):
    """Primer hueco libre de radio r sobre un tablero, el de mejor nota.

    ocup es la lista de (x, y, r) de lo que ya hay encima; dentro(x, y, r)
    dice si el circulo cabe en el tablero; nota(x, y) puntua cada sitio. Lo
    colocado se apunta en ocup. Si no hay sitio devuelve None y la pieza no
    se pone: mejor una pieza menos que una encima de otra.
    """
    mejor = None
    xs = [i * paso for i in range(-60, 61)]
    for dx in xs:
        for dy in xs:
            if not dentro(dx, dy, r):
                continue
            if any((dx - ox) ** 2 + (dy - oy) ** 2 < (r + orr + 0.012) ** 2
                   for ox, oy, orr in ocup):
                continue
            n = nota(dx, dy)
            if mejor is None or n > mejor[0]:
                mejor = (n, dx, dy)
    if mejor is None:
        return None
    ocup.append((mejor[1], mejor[2], r))
    return mejor[1], mejor[2]


def _huella(obs, cx, cy):
    """Circulo que envuelve en planta unas piezas, relativo a (cx, cy)."""
    xs, ys = [], []
    for o in obs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            xs.append(w.x)
            ys.append(w.y)
    mx, my = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return (mx - cx, my - cy, max(max(xs) - min(xs), max(ys) - min(ys)) / 2 + 0.005)


def mesa_italiana(tag, cx, cy, w, d, z, ocup, k, redonda=False, col='Decoracion',
                  aceite=None):
    """Lo que la hace mesa de trattoria: fiasco con vela, aceite y vinagre,
    sal y pimienta, albahaca o grissini, y limones en las de cuatro.

    Cada pieza busca su hueco entre lo que ya hay (ocup): en las mesas
    cuadradas, con las sillas a Norte y Sur, el centro de mesa va a los
    testeros y los condimentos se arriman al aceite.
    """
    m = 0.035                                   # margen al canto
    largo_x = w >= d                            # los testeros, en el lado largo
    grande = max(w, d) > 1.0
    if redonda:
        R = w / 2

        def dentro(x, y, r):
            return math.hypot(x, y) + r <= R - m
    else:
        def dentro(x, y, r):
            return abs(x) + r <= w / 2 - m and abs(y) + r <= d / 2 - m
    lado = -1 if k % 2 == 0 else 1              # testero del fiasco, alterno

    def cerca(px, py):
        return lambda x, y: -math.hypot(x - px, y - py)

    def testero(sx):
        if redonda:
            return lambda x, y: -abs(math.hypot(x, y) - 0.30) - 0.02 * abs(y)
        if largo_x:
            return lambda x, y: sx * x - 1.5 * abs(y)
        return lambda x, y: sx * y - 1.5 * abs(x)

    puestos = []
    # el aceite de la mesa (aceite = su sitio, relativo al centro), para
    # arrimarle el vinagre, la sal y la pimienta; las de arriba no lo llevaban
    # y se les pone
    if aceite:
        ax, ay = aceite
    else:
        p = _colocar(ocup, R_BOTELLA, dentro, testero(-lado))
        ax, ay = p if p else (0.0, 0.0)
        if p:
            puestos.append(botella(f'Aceite {tag}', cx + p[0], cy + p[1], z,
                                   alto=0.185, col=col))
    p = _colocar(ocup, 0.070, dentro, testero(lado))
    if p:
        puestos.append(fiasco(f'Fiasco {tag}', cx + p[0], cy + p[1], z, col=col))
    p = _colocar(ocup, R_BOTELLA, dentro, cerca(ax, ay))
    if p:
        puestos.append(botella(f'Vinagre {tag}', cx + p[0], cy + p[1], z, alto=0.170,
                               col=col, vidrio=_mat_mesa('vinagre')))
    for nm, mat, alto in (('Pimienta', MAT['mesa'], 0.145), ('Sal', _mat_mesa('sal'), 0.130)):
        p = _colocar(ocup, 0.023, dentro, cerca(ax, ay))
        if p:
            puestos.append(molinillo(f'{nm} {tag}', cx + p[0], cy + p[1], z, alto, mat, col))
    if k % 2 == 0 or grande:
        p = _colocar(ocup, 0.052, dentro, testero(-lado))
        if p:
            puestos.append(albahaca(f'Albahaca {tag}', cx + p[0], cy + p[1], z, col=col))
    if k % 2 == 1 or grande:
        p = _colocar(ocup, 0.040, dentro, testero(-lado))
        if p:
            puestos.append(grissini(f'Grissini {tag}', cx + p[0], cy + p[1], z, col=col))
    if w > 1.0 and not redonda:
        # cuenco de limones en las de cuatro del comedor
        p = _colocar(ocup, 0.095, dentro, lambda x, y: -abs(x) - 1.5 * abs(y))
        if p:
            bx, by = cx + p[0], cy + p[1]
            puestos += poner('wooden_bowl_01', bx, by, z, escala=1.0, giro=k * 40, col=col)
            # cada limon se apoya donde da un rayo vertical sobre el cuenco:
            # ni flotando ni metido en la madera
            bpy.context.view_layer.update()
            dg = bpy.context.evaluated_depsgraph_get()
            for i, (dx, dy, g) in enumerate(((-0.035, -0.015, 10), (0.035, -0.020, 95),
                                              (0.000, 0.045, 200))):
                ok, loc, *_ = bpy.context.scene.ray_cast(
                    dg, Vector((bx + dx, by + dy, z + 0.40)), Vector((0, 0, -1)))
                zl = loc.z if ok and loc.z < z + 0.10 else z + 0.020
                puestos += poner('lemon', bx + dx, by + dy, zl - 0.004, escala=1.0,
                                 giro=g, col=col)
    return puestos


def _dejar_caer(x, y, r, z_desde, dg):
    """Cota de la base de una pieza casi esferica, de radio r en planta,
    que se deja caer en (x, y) hasta tocar lo que tiene debajo.

    Rayos verticales por un disco de radio r: la esfera toca donde la
    superficie mas se le acerca, no solo bajo su centro, que en un cuenco
    concavo la metia por el lado del borde. None si debajo no hay nada.
    """
    zc = None
    for f in (0.0, 0.3, 0.55, 0.8):
        for k in range(8 if f else 1):
            a = 2 * math.pi * k / 8
            ok, loc, *_ = bpy.context.scene.ray_cast(
                dg, Vector((x + f * r * math.cos(a), y + f * r * math.sin(a), z_desde)),
                Vector((0, 0, -1)))
            if ok:
                c = loc.z + r * math.sqrt(1.0 - f * f)
                zc = c if zc is None else max(zc, c)
    return None if zc is None else zc - r


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
    # El estante va de x 0,250 a 0,650, contra el muro: en x = 0,62 los tarros
    # (58 mm de radio) volaban 28 mm por fuera del canto.
    for i in range(4):
        tarro(f'Tarro pasta {i + 1}', 0.585, 3.05 + i * 0.30, z_est, alto=0.20 + 0.03 * (i % 2))
    # Tazas de espresso sobre el calientatazas de la cafetera, sin plato, que
    # es donde se ponen a calentar. Iban a la cota de la mesada (0,905) justo
    # donde esta la maquina, y salian de dentro de su cuerpo. Cada una apoya
    # donde da un rayo vertical sobre la bandeja de arriba.
    cal = next((o for o in bpy.data.objects
                if o.type == 'MESH' and o.name.split('.')[0] == 'calientatazas'), None)
    if cal is not None:
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        ws = [cal.matrix_world @ Vector(c) for c in cal.bound_box]
        xc = (min(w.x for w in ws) + max(w.x for w in ws)) / 2
        yc = (min(w.y for w in ws) + max(w.y for w in ws)) / 2
        zt = max(w.z for w in ws)
        # tres por dos: la bandeja son dos chapas con una junta de 2 mm justo
        # en el centro (y = 4,227), y una fila ahi hundia las tazas en ella
        for i in range(6):
            tx, ty = xc + (i % 3 - 1) * 0.095, yc + (i // 3 - 0.5) * 0.095
            ok, loc, *_ = bpy.context.scene.ray_cast(
                dg, Vector((tx, ty, zt + 0.05)), Vector((0, 0, -1)), distance=0.20)
            if ok:
                taza(f'Taza barra {i + 1}', tx, ty, loc.z, con_plato=False)
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
    # ---- las dos jarras, en la mesada de la trasbarra
    # En (0,45 / 4,55) y (0,66 / 4,60) caian dentro de la cafetera, que ocupa
    # la mesada de y 3,727 a 4,727. Van al tramo libre, entre el peto (2,611)
    # y la granizadora (3,357), apoyadas en la mesada (0,900).
    poner('jug_01', 0.46, 2.80, 0.900, escala=1.0, giro=35)
    poner('metal_jug', 0.52, 3.15, 0.900, escala=0.9, giro=-15)
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
    # La fruta iba a 50 mm una de otra y a una cota fija: la lima se metia en
    # la granada y la manzana en la lima. Van en triangulo alrededor del
    # centro del cuenco (2,10 / 6,30), a 68 mm de el y a 118 mm entre si, y
    # cada una se deja caer sobre la madera: el cuenco es concavo y apoyada
    # por el punto de debajo de su centro se metia por el lado del borde.
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    frutas = [(aid, 2.10 + 0.068 * math.cos(math.radians(a)),
               6.30 + 0.068 * math.sin(math.radians(a)), r)
              for aid, a, r in (('food_apple_01', 210, 0.049), ('food_lime_01', 330, 0.031),
                                ('food_pomegranate_01', 90, 0.058))]
    cotas = [_dejar_caer(fx, fy, r, z_k10 + 0.40, dg) for aid, fx, fy, r in frutas]
    for i, ((aid, fx, fy, r), zf) in enumerate(zip(frutas, cotas)):
        poner(aid, fx, fy, (zf if zf is not None else z_k10 + 0.020) - 0.002,
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
        ocup = []                       # lo que hay encima, para no pisarlo
        if estilo == 0:
            taza('Taza ' + tag, cx - 0.14, cy + 0.05, z)
            taza('Taza b ' + tag, cx + 0.13, cy - 0.06, z)
            plato('Plato ' + tag, cx, cy + 0.17, z, r=0.085)
            ocup += [(-0.14, 0.05, 0.070), (0.13, -0.06, 0.070), (0.0, 0.17, 0.090)]
        elif estilo == 1:
            copa('Copa ' + tag + ' 1', cx - 0.12, cy + 0.08, z)
            copa('Copa ' + tag + ' 2', cx + 0.11, cy + 0.06, z)
            botella('Vino ' + tag, cx, cy - 0.13, z, alto=0.300)
            ocup += [(-0.12, 0.08, 0.043), (0.11, 0.06, 0.043), (0.0, -0.13, R_BOTELLA)]
        elif estilo == 2:
            te = poner('tea_set_01', cx, cy, z, escala=1.0, giro=rnd.uniform(-30, 30))
            ocup.append(_huella(te, cx, cy))
        else:
            plato('Plato ' + tag, cx - 0.05, cy, z)
            poner('croissant', cx - 0.05, cy, z + 0.006, escala=1.0,
                  giro=rnd.uniform(0, 360))
            taza('Taza ' + tag, cx + 0.16, cy + 0.03, z)
            ocup += [(-0.05, 0.0, 0.120), (0.16, 0.03, 0.070)]
        # aceite en todas; con el, el vinagre, la sal y la pimienta
        botella('Aceite ' + tag, cx + 0.22, cy + 0.20, z, alto=0.185)
        ocup.append((0.22, 0.20, R_BOTELLA))
        mesa_italiana(tag, cx, cy, x1 - x0, y1 - y0, z, ocup, k, aceite=(0.22, 0.20))
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
            ocup = []
            for i in range(3):
                t = a0 + 0.25 + (a1 - a0 - 0.50) * i / 2
                tx, ty = (t, cy + 0.20) if largo_x else (cx + 0.20, t)
                taza(f'Taza PA {tag} {i}', tx, ty, z, col='Planta alta')
                ocup.append((tx - cx, ty - cy, 0.070))
            ja = poner('ceramic_vase_02', cx, cy, z, escala=0.85, giro=20, col='Planta alta')
            ocup.append(_huella(ja, cx, cy))
            # la de cowork no es de comer: albahaca, grissini y la vela
            mesa_italiana(tag, cx, cy, x1 - x0, y1 - y0, z, ocup, k, col='Planta alta')
        else:
            ocup = []
            ce = poner('wicker_basket_01', cx, cy, z, escala=0.7, giro=-20, col='Planta alta')
            ocup.append(_huella(ce, cx, cy))
            for i in range(4):
                copa(f'Copa PA {i}', cx + 0.22 * math.cos(i * 1.57),
                     cy + 0.22 * math.sin(i * 1.57), z, col='Planta alta')
                ocup.append((0.22 * math.cos(i * 1.57), 0.22 * math.sin(i * 1.57), 0.043))
            mesa_italiana(tag, cx, cy, x1 - x0, y1 - y0, z, ocup, k,
                          redonda=(tipo == 'redonda'), col='Planta alta')
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
    if MAXIMA:
        h16 = os.path.join(PH, 'wide_street_01', 'wide_street_01_16k.hdr')
        if os.path.exists(h16):
            hdri = h16
        else:
            print('   (falta el cielo a 16K: va con el de 8K)')
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
              giro=i * 53, col='Ciudad', lod=0 if MAXIMA else 1)
    # arbolado de la acera de enfrente, mas lejos y mas suelto. A 1,20 del
    # bordillo la copa se metia en los balcones y en el toldo de enfrente: va
    # a 0,35, del lado de la calzada, que es donde hay aire
    for i, x in enumerate((-9.0, 14.0)):
        poner('tree_small_02', x, C.Y_ACERA_OP - 0.35, C.H_BORDILLO - 0.02,
              altura=6.4 + 0.9 * (i % 2), giro=i * 71, col='Ciudad',
              lod=0 if MAXIMA else 1)

    # mobiliario urbano
    for i, x in enumerate((-5.2, 2.0, 8.6, 15.2, 21.8)):
        C.farola(CIUDAD_API, MAT, x, C.Y_ACERA + 0.55, nombre=f'Farola {i + 1}')
    # la ultima pareja, 10 cm al Oeste: el bolardo de 16,9 pisaba el marco
    # del alcorque de 17,5, que arranca en 16,90
    for i, x in enumerate((-2.6, -1.9, 3.4, 4.1, 9.8, 10.5, 16.1, 16.8)):
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
    caja('Acera', -16.0, C.Y_ACERA, 26.0, C.Y_FACHADA + 0.4, C.H_BORDILLO - 0.15,
         C.H_BORDILLO,
         MAT['_acera'], 'Ciudad')
    caja('Calzada', -16.0, -14.0, 26.0, C.Y_ACERA - 0.18, C.Z_CALZADA - 0.128,
         C.Z_CALZADA,
         MAT['_asfalto'], 'Ciudad')
    caja('Bordillo', -16.0, C.Y_ACERA - 0.18, 26.0, C.Y_ACERA, C.Z_CALZADA - 0.120,
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


def poner_bmw(x, y, giro, hexcol, nombre, col='Ciudad', z_apoyo=None, subdiv=1):
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
    if z_apoyo is None:
        import ciudad as C
        z_apoyo = C.Z_CALZADA - 0.008      # 8 mm hundido en el asfalto
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
    # El mismo punto de vista que la primera foto de obra: al pie del tramo,
    # a la altura de los ojos y mirando hacia arriba, con el montante gris y
    # el antepecho de la planta alta.
    'escalera_pilar': ((8.55, 2.25, 1.620), (9.30, 6.20, 1.950), 19.0),
    # El de la segunda foto de obra, desde la sala: el montante a mitad del
    # 5.º peldaño y el forjado volando por delante de el. Sacado de la foto
    # (movil en vertical, a 1,29 de altura): va en vertical, 9 x 16.
    'escalera_obra': ((6.55, 2.35, 1.290), (8.49, 4.64, 1.290), 26.0),
    # La escalera de costado, tal como se ve desde la sala. Ojo: el costado
    # Oeste lo cierra CAJA_ESC_PB, un panel cuyo borde superior sigue el
    # rampante (ver _panel_escalera: hoy llega al techo en y 7,13), asi que de
    # costado se ve ese panel y el tramo solo asoma por encima. La camara
    # anterior, en (5,20 / 5,70), tenia P3 a 44 cm y solo sacaba listones;
    # esta esta al Norte de P3 y ve el 93 % del costado (comprobado con rayos).
    # El alzado del tramo entero sale en seccion por x = 8,62, no desde aqui.
    'escalera_costado': ((6.00, 6.40, 1.600), (8.70, 5.60, 1.600), 18.0),
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
    # --- las de la revision de la fachada contra los videos. Van pensadas
    #     en vertical (3 x 4): con lote.py, --ancho 2400 --alto 3200
    'fachada_general': ((5.60, -7.80, 1.650), (5.10, 0.60, 2.700), 20.0),
    'fachada_oeste':   ((1.55, -2.10, 1.500), (1.45, 1.56, 2.450), 20.0),
    'fachada_esquina': ((3.70, -0.60, 1.600), (5.80, 1.10, 2.300), 18.0),
    'fachada_este':    ((8.10, -3.20, 1.600), (7.95, 0.40, 2.650), 20.0),
    'porche_intrados': ((2.60, -1.40, 1.600), (2.10, 0.70, 4.600), 16.0),
    'escaparate_alto': ((7.40, -1.90, 1.650), (7.60, 0.40, 3.100), 20.0),
    # --- y en horizontal, como las demas
    'cubo_calle':      ((8.70, -1.60, 1.620), (7.60, 1.05, 1.250), 24.0),
    'vitrinas_detras': ((1.05, 2.95, 0.620), (2.30, 2.95, 0.300), 16.0),
    'cocina_campana':  ((1.30, 6.30, 1.450), (1.30, 8.30, 2.350), 16.0),
    'antepecho_pa':    ((5.30, 6.90, Z_PA + 1.550), (2.50, 4.10, Z_PA + 0.650), 20.0),
    'antepecho_pa2':   ((5.20, 4.15, Z_PA + 1.600), (8.70, 3.95, Z_PA + 0.500), 18.0),
    'lamas_interior':  ((6.80, 4.30, Z_PA + 1.600), (8.60, 0.40, 3.500), 18.0),
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
               'planta_baja', 'barra_frente', 'fachada_general', 'fachada_oeste',
               'fachada_esquina', 'fachada_este', 'porche_intrados',
               'escaparate_alto', 'cubo_calle'}

# el recorrido (recorrido.py), de la calle al almacen de arriba, y sus dos
# plantas cenitales: nombre -> (centro, lado en metros, cota de corte)
PLANTAS = {}
assert abs(RC.Z_PA - Z_PA) < 1e-9, 'recorrido.py tiene otra cota de planta alta'
for _t in RC.RECORRIDO:
    if _t.get('tipo') == 'planta':
        PLANTAS[_t['nombre']] = (_t['centro'], _t['ancho_m'], _t['corte'])
    else:
        VISTAS[_t['nombre']] = (_t['ojo'], _t['mira'], _t['lente'], _t.get('despl', 0.0))
    if _t['exp'] is not None:
        EXPOSICION[_t['nombre']] = _t['exp']
    if _t['calle']:
        VE_LA_CALLE.add(_t['nombre'])


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
    fachada_real()
    print('  fachada Oeste rehecha desde el video', flush=True)
    print('  toldos de la fachada,', 'desplegados como en 2021, en azzurro y con logo:'
          if TOLDOS_ABIERTOS else 'recogidos:', toldos(), 'piezas', flush=True)
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


def fondo_planta():
    """Suelo neutro muy por debajo de todo, solo para las plantas cenitales.

    Mirando hacia abajo, fuera del edificio -donde no hay vecinos ni acera-
    la camara veria el suelo de la foto del cielo. Queda debajo de la acera
    y de los suelos: desde las otras vistas no se ve.
    """
    if 'Fondo de las plantas' in bpy.data.objects:
        return
    caja('Fondo de las plantas', -60, -60, 60, 60, -0.40, -0.38,
         MT.liso('Fondo de las plantas', MT.srgb('D9D6D0'), 0.9), 'Obra')


def render(vista, salida, spp, ancho, alto, rapido=False):
    sc = bpy.context.scene
    mostrar_todo()
    if vista in PLANTAS:
        (cx, cy), lado, corte = PLANTAS[vista]
        fondo_planta()
        cam = camara_orto(f'cam {vista}', (cx, cy, 30.0), (cx, cy, 0.0), lado)
        # mirando recto hacia abajo, con el Norte arriba y la calle abajo
        cam.rotation_euler = (0.0, 0.0, 0.0)
        # El corte lo hace el plano de recorte cercano de la camara, que en una
        # ortografica es un plano: lo que queda por encima de la cota no existe
        # para la camara, y los muros cortados salen en negro, como en un
        # plano. Y lo que queda entero por encima -techos, forjado, cubierta-
        # fuera tambien para la luz: el cielo entra desde arriba, como en una
        # maqueta, y se ven hasta los cuartos cerrados (el baño de abajo y el
        # inodoro de arriba, que con sus techos puestos salian en negro).
        cam.data.clip_start = 30.0 - corte
        cam.data.clip_end = 31.0
        n = ocultar_sobre(corte)
        print(f'    (planta cenital cortada a {corte:.2f}: {n} piezas por encima fuera)',
              flush=True)
        alto = ancho                            # cuadrada
    elif vista in ORTOS:
        ojo, mira, escala, corte = ORTOS[vista]
        cam = camara_orto(f'cam {vista}', ojo, mira, escala)
        n = ocultar_sobre(corte)
        print(f'    (planta: {n} piezas por encima de {corte:.2f} fuera)', flush=True)
        if vista.startswith('planta'):          # las plantas, cuadradas
            alto = ancho
    else:
        ojo, mira, lente, *resto = VISTAS[vista]
        cam = camara(f'cam {vista}', ojo, mira, lente, despl=resto[0] if resto else 0.0)
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
    ap.add_argument('--umbral', type=float, default=0.010,
                    help='ruido que se tolera por pixel antes de dejar de muestrear '
                         '(muestreo adaptativo): menos es mas limpio y mas lento')
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None)

    global USAR_GPU
    USAR_GPU = a.gpu
    # Absoluta siempre. Blender resuelve una ruta relativa contra el .blend,
    # no contra el directorio de trabajo: '.\\renders' acababa en C:\\renders.
    a.salida = os.path.abspath(os.path.expanduser(a.salida))
    os.makedirs(a.salida, exist_ok=True)
    todas = list(VISTAS) + list(ORTOS) + list(PLANTAS)
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
    bpy.context.scene.cycles.adaptive_threshold = a.umbral
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
            ob.visible_camera = False             # alumbra hacia abajo
            ob.visible_transmission = False
            ob.visible_glossy = False
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
    y = 1.609 + DESPEGUE           # cara interior del vidrio del ventanal Sur
    # centrado en el vidrio bajo de la derecha (3,804..5,705): en 3,60 la
    # junta a tope de los dos vidrios (3,80) le cruzaba el nombre
    cx, cz = 4.75, 1.62
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


# La pizarra del menu, en la pared de detras de la barra (el Muro Oeste,
# cara x = 0,250), centrada sobre la balda de las botellas (y 2,884..4,134,
# a 1,800; las botellas llegan a 2,15). La imagen la pinta
# rehacer_pizarra.py: logo en tiza y cuatro apartados de la carta.
PIZARRA = dict(x=0.250, yc=3.509, zc=2.850, ancho=1.600, alto=1.100, marco=0.050,
               fondo=0.035)
PIZARRA_IMG = os.path.join(REPO, 'docs', 'pared', 'CASA_MARGOT_PIZARRA_MENU.jpg')


def pizarra_menu():
    """Pizarra con el logo y la carta, enmarcada en el liston de roble."""
    if not os.path.exists(PIZARRA_IMG):
        print('   (sin pizarra: falta', PIZARRA_IMG, ')')
        return None
    P = PIZARRA
    x0 = P['x']
    y0, y1 = P['yc'] - P['ancho'] / 2, P['yc'] + P['ancho'] / 2
    z0, z1 = P['zc'] - P['alto'] / 2, P['zc'] + P['alto'] / 2
    m, f = P['marco'], P['fondo']
    col = 'Decoracion'
    # trasdos de la pizarra, pegado al muro
    caja('Pizarra · tablero', x0 - SOLAPE, y0, x0 + f - 0.012, y1, z0, z1, MAT['_negro'], col)
    # marco: los largueros de arriba y abajo de punta a punta, los montantes
    # entre ellos (asi no se cruzan dos testas en el mismo plano)
    for nm, a0, a1, b0, b1 in (('abajo', y0 - m, y1 + m, z0 - m, z0),
                               ('arriba', y0 - m, y1 + m, z1, z1 + m),
                               ('izquierda', y0 - m, y0, z0, z1),
                               ('derecha', y1, y1 + m, z0, z1)):
        bisel(caja(f'Pizarra · marco {nm}', x0 - SOLAPE, a0, x0 + f, a1, b0, b1,
                   MAT['_liston'], col), 0.003, 2)
    # la cara pintada, un plano con la imagen, mirando a la barra (+X)
    xc = x0 + f - 0.012 + DESPEGUE
    me = bpy.data.meshes.new('Pizarra del menu')
    v = [(xc, y0, z0), (xc, y1, z0), (xc, y1, z1), (xc, y0, z1)]
    me.from_pydata(v, [], [(0, 1, 2, 3)])
    me.uv_layers.new()
    for i, c in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        me.uv_layers[0].data[i].uv = c
    me.materials.append(MT.calca('Pizarra del menu', PIZARRA_IMG, rug=0.85))
    ob = bpy.data.objects.new('Pizarra del menu', me)
    coleccion(col).objects.link(ob)
    return ob


def caracter_italiano():
    """Lo que convierte el local en una trattoria y no en una cafeteria."""
    # Ni carta en pizarra en el paso de servicio ni hornacinas sobre el
    # sillon: ese tramo es zona de paso y la pared del sillon lleva solo
    # cuadros.
    # el logo en el vidrio del ventanal
    logo_escaparate()
    # la carta en pizarra, detras de la barra
    pizarra_menu()
    # el expositor de bebidas, lleno: sus cinco parrillas estan a 0,46 / 0,73
    # / 1,00 / 1,27 / 1,54 (obj_A7: Z_INT0 + 0,190 + k * 0,270)
    # Entre las cremalleras de los laterales quedan libres x 5,777..6,213:
    # seis botellas a 74 mm se salian por los dos lados y se metian en ellas.
    # Van cinco a 85 mm. La parrilla son varillas a 25 mm con la cara de
    # arriba en z + 0,0005: el culo de la botella, que es abombado, baja
    # 2 mm entre ellas y descansa en las que tiene debajo (antes flotaba
    # 5 mm por encima de todas).
    ax, ay = 5.995, 4.078                      # centro y cara interior del frente
    for k in range(5):
        z = 0.462 + k * 0.270
        for j in range(5):
            bx = ax + (j - 2) * 0.085
            for f, dy in ((0, 0.075), (1, 0.230)):
                botella(f'A7 botella {k}{j}{f}', bx, ay + dy, z - 0.0015,
                        alto=0.225 if k % 2 == 0 else 0.245, col='Decoracion')
    # Cesta de pan del paso. Estaba en x = 2,75 y la tabla del mostrador muere
    # en 2,53: volaba 220 mm por delante del canto. Se pasa a la mesa de
    # trabajo de la cocina, con la fruta y la otra cesta.
    poner('wicker_basket_02', 2.10, 7.35, 0.850, escala=0.8, giro=15)
    # Ceramica al pie del ventanal, SOBRE el 'Zocalo del ventanal' del plano
    # (x 1,87..5,87, y 1,621..1,968, de 0 a 0,130): puestas en el suelo se
    # enterraban 13 cm en la piedra. Centradas en su fondo (y 1,795) y 15 cm
    # mas al Oeste: la olla de laton mide 0,34 y en (5,66, 1,76) se metia
    # en el vidrio del ventanal y en el montante del retorno (5,705).
    # la tercera pieza, a x 5,75, se metia 49 mm en el retorno de P5i
    # (5,870..5,980): las tres se corren al Oeste manteniendo el paso de 0,70
    for i, x in enumerate((4.11, 4.81, 5.51)):
        poner(('ceramic_vase_01', 'ceramic_vase_02', 'brass_pot_01')[i % 3],
              x, 1.795, 0.130 + DESPEGUE, escala=0.8, giro=i * 63)


if __name__ == '__main__':
    main()
