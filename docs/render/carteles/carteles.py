#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carteles de Casa Margot.

Los cinco carteles de referencia que mando el cliente (30 set. 2026),
adaptados con el logo horizontal de Casa Margot y el fondo azzurro, en los
seis acabados del logo de su hoja de ideas: blanco, negro y oro, y marmol
blanco con vetas de oro, marmol negro y marmol rosa.

    ovalo    ovalo en bandera, marco de color y letras en relieve   (G's)
    caja     caja de luz en bandera, logo en las caras               (Кицуня)
    placa    placa cuadrada en bandera, canto retroiluminado         (Aesop)
    colgado  caja de luz alargada colgada de un soporte              (Jam)
    barra    barra en la pared, logo calado y halo de luz            (Watanabe)

    python3 carteles.py [--carteles ovalo,caja] [--acabados blanco,oro]
                        [--spp 64] [--ancho 900] [--salida DIR]

Cada cartel se monta en su escena y se renderiza una vez por acabado; al
final sale una hoja por cartel con las seis opciones, en el mismo orden que
la hoja de ideas.

El logo sale del PDF vectorial del repositorio (docs/pared/
CASA_MARGOT_LOGO_NERO.pdf): se pasa a SVG y Blender lo importa como curvas,
asi que el relieve y el calado son exactos, sin redibujar nada. Los tres
marmoles son las muestras de la hoja de ideas del cliente y no se versionan:
se buscan en $CM_SCRATCH/carteles/texturas/marmol_{blanco,negro,rosa}.jpg.
Las paredes son texturas CC0 de Poly Haven (painted_brick, red_brick_03,
plaster_grey_04, plastered_wall), en las mismas carpetas que usa la escena
del local.
"""
import argparse
import math
import os
import sys
import time

import bpy                      # antes que addon_utils y bmesh: los trae bpy
import addon_utils              # noqa: E402
import bmesh                    # noqa: E402
from mathutils import Matrix, Vector   # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(AQUI, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'docs', 'render', 'escena'))
from rutas import PH, SCRATCH   # noqa: E402

PDF_LOGO = os.path.join(REPO, 'docs', 'pared', 'CASA_MARGOT_LOGO_NERO.pdf')
TRABAJO = os.path.join(SCRATCH, 'carteles')
SVG_LOGO = os.path.join(TRABAJO, 'logo_h.svg')
TEXTURAS = os.path.join(TRABAJO, 'texturas')

AZZURRO = '12A0D7'          # SSC Napoli, Pantone 2995 C: el de todo el proyecto
ORO = 'B4A86D'              # el oro de la hoja de ideas (su tono claro)

# en el orden de la hoja de ideas: tres filas de dos
ACABADOS = [('blanco', 'Blanco'), ('marmol_blanco', 'Mármol blanco y oro'),
            ('negro', 'Negro'), ('marmol_negro', 'Mármol negro'),
            ('oro', 'Oro'), ('marmol_rosa', 'Mármol rosa')]


# =================================================================== utiles
def srgb(h):
    """Hex de diseno -> lineal, que es lo que come Cycles."""
    v = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v)


def svg_logo():
    """El logo horizontal en SVG, sacado del PDF vectorial del repositorio."""
    if not os.path.exists(SVG_LOGO):
        import pymupdf
        os.makedirs(TRABAJO, exist_ok=True)
        pagina = pymupdf.open(PDF_LOGO)[0]
        open(SVG_LOGO, 'w').write(pagina.get_svg_image(text_as_path=True))
    return SVG_LOGO


def escena_nueva(ancho, alto, spp):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_curve_svg', default_set=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = spp
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 4
    sc.cycles.sample_clamp_indirect = 6.0
    sc.cycles.blur_glossy = 1.0
    sc.render.resolution_x, sc.render.resolution_y = ancho, alto
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    # Khronos PBR Neutral: hecho para que los colores de marca salgan como
    # son. Con AgX las cajas de luz azzurro salian lavadas, casi blancas.
    sc.view_settings.view_transform = 'Khronos PBR Neutral'
    return sc


def mundo(color, fuerza):
    w = bpy.data.worlds.new('Mundo')
    bpy.context.scene.world = w
    w.use_nodes = True
    fondo = w.node_tree.nodes['Background']
    fondo.inputs['Color'].default_value = (*srgb(color), 1)
    fondo.inputs['Strength'].default_value = fuerza


def objeto(nombre, datos):
    ob = bpy.data.objects.new(nombre, datos)
    bpy.context.scene.collection.objects.link(ob)
    return ob


# ================================================================ materiales
def mat_liso(nombre, color, rough=0.4, metal=0.0, coat=0.0, emis=None, fuerza=0.0):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*srgb(color), 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if coat:
        b.inputs['Coat Weight'].default_value = coat
        b.inputs['Coat Roughness'].default_value = 0.06
    if emis and fuerza:
        b.inputs['Emission Color'].default_value = (*srgb(emis), 1)
        b.inputs['Emission Strength'].default_value = fuerza
    return m


def _mapeo(nt, escala):
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = escala
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    return mp


def _imagen(nt, ruta, vector, dato=False):
    tx = nt.nodes.new('ShaderNodeTexImage')
    tx.image = bpy.data.images.load(ruta, check_existing=True)
    if dato:
        tx.image.colorspace_settings.name = 'Non-Color'
    tx.projection = 'BOX'
    tx.projection_blend = 0.3
    tx.extension = 'MIRROR'
    nt.links.new(vector, tx.inputs['Vector'])
    return tx


def mat_marmol(nombre, clave, ancho_logo):
    """Marmol pulido con la muestra de la hoja de ideas. Una muestra cubre
    ~0,35 del ancho del logo: con la muestra a tamaño de hoja (~0,8) el trazo
    del logo, de 4 mm, caia entero entre dos vetas y el marmol no se leia.
    Se corrige su proporcion para que las vetas no salgan estiradas."""
    ruta = os.path.join(TEXTURAS, f'{clave}.jpg')
    if not os.path.exists(ruta):
        raise SystemExit(f'Falta la muestra de marmol: {ruta}')
    m = mat_liso(nombre, 'FFFFFF', rough=0.12, coat=0.35)
    nt = m.node_tree
    im = bpy.data.images.load(ruta, check_existing=True)
    prop = im.size[0] / im.size[1]
    k = 1.0 / (0.35 * ancho_logo)
    mp = _mapeo(nt, (k, k * prop, k))
    tx = _imagen(nt, ruta, mp.outputs['Vector'])
    nt.links.new(tx.outputs['Color'], nt.nodes['Principled BSDF'].inputs['Base Color'])
    return m


def mat_pbr(nombre, aid, tam, tinte=None, relieve=0.5, sat=None, val=None):
    """Textura de Poly Haven a 2K, en proyeccion de caja sobre coordenadas de
    objeto: tam es lo que mide una tesela en metros. sat y val corrigen la
    saturacion y el valor antes del tinte (painted_brick es azul claro)."""
    d = os.path.join(PH, aid, 'textures_2k')
    m = mat_liso(nombre, 'FFFFFF', rough=0.8)
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    mp = _mapeo(nt, (1 / tam,) * 3)
    dif = _imagen(nt, os.path.join(d, f'{aid}_diff_4k.jpg'), mp.outputs['Vector'])
    col = dif.outputs['Color']
    if sat is not None or val is not None:
        hs = nt.nodes.new('ShaderNodeHueSaturation')
        hs.inputs['Saturation'].default_value = 1.0 if sat is None else sat
        hs.inputs['Value'].default_value = 1.0 if val is None else val
        nt.links.new(col, hs.inputs['Color'])
        col = hs.outputs['Color']
    if tinte:
        mx = nt.nodes.new('ShaderNodeMix')
        mx.data_type = 'RGBA'
        mx.blend_type = 'MULTIPLY'
        mx.inputs['Factor'].default_value = 1.0
        nt.links.new(col, mx.inputs['A'])
        mx.inputs['B'].default_value = (*srgb(tinte), 1)
        col = mx.outputs['Result']
    nt.links.new(col, b.inputs['Base Color'])
    rg = _imagen(nt, os.path.join(d, f'{aid}_rough_4k.jpg'), mp.outputs['Vector'], dato=True)
    nt.links.new(rg.outputs['Color'], b.inputs['Roughness'])
    dp = _imagen(nt, os.path.join(d, f'{aid}_disp_4k.jpg'), mp.outputs['Vector'], dato=True)
    bu = nt.nodes.new('ShaderNodeBump')
    bu.inputs['Strength'].default_value = relieve
    bu.inputs['Distance'].default_value = 0.01
    nt.links.new(dp.outputs['Color'], bu.inputs['Height'])
    nt.links.new(bu.outputs['Normal'], b.inputs['Normal'])
    return m


def mat_estriado(nombre, color, paso, eje):
    """Panel de listones verticales en media cana, de paso dado, en relieve."""
    m = mat_liso(nombre, color, rough=0.65)
    nt = m.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sp = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sp.inputs['Vector'])
    mu = nt.nodes.new('ShaderNodeMath')
    mu.operation = 'MULTIPLY'
    mu.inputs[1].default_value = math.pi / paso
    nt.links.new(sp.outputs[eje], mu.inputs[0])
    si = nt.nodes.new('ShaderNodeMath')
    si.operation = 'SINE'
    nt.links.new(mu.outputs[0], si.inputs[0])
    ab = nt.nodes.new('ShaderNodeMath')
    ab.operation = 'ABSOLUTE'
    nt.links.new(si.outputs[0], ab.inputs[0])
    bu = nt.nodes.new('ShaderNodeBump')
    bu.inputs['Strength'].default_value = 1.0
    bu.inputs['Distance'].default_value = 0.006
    nt.links.new(ab.outputs[0], bu.inputs['Height'])
    nt.links.new(bu.outputs['Normal'], nt.nodes['Principled BSDF'].inputs['Normal'])
    return m


def mat_acabado(clave, ancho_logo, luz=0.0):
    """El logo en cada acabado. luz > 0: el blanco va iluminado por detras
    (calado o impreso en una caja de luz); los demas son opacos."""
    # blanco y negro satinados: brillantes, el negro reflejaba la luz de
    # frente y en la testa de la caja se leia gris, casi hueco
    if clave == 'blanco':
        return mat_liso('Logo blanco', 'F4F4F0', rough=0.5,
                        emis='FFF6EA' if luz else None, fuerza=luz)
    if clave == 'negro':
        return mat_liso('Logo negro', '141414', rough=0.75)
    if clave == 'oro':
        return mat_liso('Logo oro', ORO, rough=0.3, metal=0.85)
    return mat_marmol(f'Logo {clave}', clave, ancho_logo)


# ================================================================= geometria
def malla(nombre, verts, caras, mat, bisel=0.0):
    me = bpy.data.meshes.new(nombre)
    me.from_pydata([tuple(v) for v in verts], [], caras)
    me.validate()
    ob = objeto(nombre, me)
    me.materials.append(mat)
    if bisel:
        md = ob.modifiers.new('Bisel', 'BEVEL')
        md.width = bisel
        md.segments = 3
        md.limit_method = 'ANGLE'
    return ob


def caja(nombre, x0, y0, x1, y1, z0, z1, mat, bisel=0.0):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return malla(nombre, v, f, mat, bisel)


def _punto(base, p, d):
    o, r, u, n = base
    return o + r * p[0] + u * p[1] + n * d


def prisma(nombre, pts, d0, d1, base, mat, bisel=0.0):
    """Prisma de un contorno 2D antihorario, de d0 a d1 sobre la normal."""
    k = len(pts)
    v = [_punto(base, p, d0) for p in pts] + [_punto(base, p, d1) for p in pts]
    f = [list(range(k))[::-1], list(range(k, 2 * k))]
    f += [[i, (i + 1) % k, k + (i + 1) % k, k + i] for i in range(k)]
    return malla(nombre, v, f, mat, bisel)


def anillo(nombre, ext, inn, d0, d1, base, mat, bisel=0.0):
    """Marco entre dos contornos antihorarios del mismo numero de puntos."""
    k = len(ext)
    v = ([_punto(base, p, d0) for p in ext] + [_punto(base, p, d1) for p in ext] +
         [_punto(base, p, d0) for p in inn] + [_punto(base, p, d1) for p in inn])
    E0, E1, I0, I1 = 0, k, 2 * k, 3 * k
    f = []
    for i in range(k):
        j = (i + 1) % k
        f.append([E1 + i, E1 + j, I1 + j, I1 + i])        # cara de delante
        f.append([E0 + j, E0 + i, I0 + i, I0 + j])        # cara de detras
        f.append([E0 + i, E0 + j, E1 + j, E1 + i])        # canto de fuera
        f.append([I0 + j, I0 + i, I1 + i, I1 + j])        # canto de dentro
    return malla(nombre, v, f, mat, bisel)


def superelipse(a, b, n=2.6, k=120):
    out = []
    for i in range(k):
        t = 2 * math.pi * i / k
        c, s = math.cos(t), math.sin(t)
        out.append((a * math.copysign(abs(c) ** (2 / n), c),
                    b * math.copysign(abs(s) ** (2 / n), s)))
    return out


def base(o, r, u):
    r, u = Vector(r).normalized(), Vector(u).normalized()
    return Vector(o), r, u, r.cross(u)


def logo(nombre, ancho, fondo, o, r, u, bisel=0.0):
    """El logo horizontal como malla de ancho y fondo dados, apoyado por
    detras en el punto o de una cara, leyendose con r a la derecha y u hacia
    arriba (su frente mira a r x u)."""
    antes = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=svg_logo())
    curvas = [ob for ob in bpy.data.objects if ob not in antes and ob.type == 'CURVE']
    xs, ys = [], []
    for c in curvas:
        for p in c.bound_box:
            w = c.matrix_world @ Vector(p)
            xs.append(w.x)
            ys.append(w.y)
    s = ancho / (max(xs) - min(xs))
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    M = (Matrix.Translation((0, 0, fondo / 2)) @ Matrix.Scale(s, 4) @
         Matrix.Translation((-cx, -cy, 0)))
    bm = bmesh.new()
    for c in curvas:
        c.data.resolution_u = 24
        c.data.extrude = fondo / (2 * s)
    dg = bpy.context.evaluated_depsgraph_get()
    for c in curvas:
        ev = c.evaluated_get(dg)
        me = ev.to_mesh()
        me.transform(M @ c.matrix_world)
        bm.from_mesh(me)
        ev.to_mesh_clear()
    for c in curvas:
        dat = c.data
        bpy.data.objects.remove(c)
        bpy.data.curves.remove(dat)
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    ob = objeto(nombre, me)
    B = base(o, r, u)
    ob.matrix_world = Matrix(((B[1].x, B[2].x, B[3].x, B[0].x),
                              (B[1].y, B[2].y, B[3].y, B[0].y),
                              (B[1].z, B[2].z, B[3].z, B[0].z),
                              (0, 0, 0, 1)))
    if bisel:
        md = ob.modifiers.new('Bisel', 'BEVEL')
        md.width = bisel
        md.segments = 2
        md.limit_method = 'ANGLE'
    return ob


# ================================================================ luz y camara
def _apuntar(ob, pos, mira):
    ob.location = pos
    ob.rotation_euler = (Vector(mira) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()


def luz_area(nombre, pos, mira, tam, potencia, color='FFFFFF'):
    lz = bpy.data.lights.new(nombre, 'AREA')
    lz.shape = 'RECTANGLE'
    lz.size, lz.size_y = (tam, tam) if isinstance(tam, (int, float)) else tam
    lz.energy = potencia
    lz.color = srgb(color)
    ob = objeto(nombre, lz)
    _apuntar(ob, pos, mira)
    return ob


def sol(direccion, fuerza, color='FFFFFF', angulo=0.8):
    lz = bpy.data.lights.new('Sol', 'SUN')
    lz.energy = fuerza
    lz.angle = math.radians(angulo)
    lz.color = srgb(color)
    ob = objeto('Sol', lz)
    ob.rotation_euler = Vector(direccion).to_track_quat('-Z', 'Y').to_euler()
    return ob


def camara(ojo, mira, lente, exposicion=0.0):
    cam = bpy.data.cameras.new('Camara')
    cam.lens = lente
    ob = objeto('Camara', cam)
    _apuntar(ob, ojo, mira)
    sc = bpy.context.scene
    sc.camera = ob
    sc.view_settings.exposure = exposicion
    return ob


# ================================================================== carteles
# Cada montaje deja la escena lista y devuelve (logos, ancho del logo, luz
# del blanco): los objetos a los que se les cambia el acabado, el ancho para
# escalar el marmol y la fuerza con la que brilla el blanco (0 = no brilla).

def montar_ovalo():
    """Ovalo en bandera (G's): marco y fondo azzurro, logo en relieve de 2 cm
    dentro del marco, colgado de una pletina en la pared de listones."""
    mundo('C9D6E3', 0.55)
    arena = 'E6D3BF'
    caja('Pared de montaje', -0.10, -3.0, 0.0, 0.90, 0.0, 3.2,
         mat_estriado('Listones pared', arena, 0.032, 'Y'))
    caja('Pared de fondo', 0.0, 0.90, 3.0, 1.00, 0.0, 3.2,
         mat_estriado('Listones fondo', arena, 0.032, 'X'))
    azz = mat_liso('Azzurro satinado', AZZURRO, rough=0.35)
    azz_mate = mat_liso('Azzurro mate', AZZURRO, rough=0.55)
    xc, zc, a, b, banda = 0.46, 1.70, 0.32, 0.19, 0.032
    B = base((xc, 0.0, zc), (1, 0, 0), (0, 0, 1))          # mira a -Y
    anillo('Ovalo · marco', superelipse(a, b), superelipse(a - banda, b - banda),
           -0.035, 0.035, B, azz, bisel=0.003)
    prisma('Ovalo · fondo', superelipse(a - banda + 0.002, b - banda + 0.002),
           -0.005, 0.005, B, azz_mate)
    # pletina: placa atornillada a la pared y brazo hasta el marco
    caja('Pletina · placa', 0.0, -0.02, 0.008, 0.02, zc - 0.08, zc + 0.08, azz, 0.002)
    caja('Pletina · brazo', 0.008, -0.004, xc - a + 0.01, 0.004, zc - 0.02, zc + 0.02,
         azz, 0.002)
    ancho = 0.48
    lg = logo('Logo', ancho, 0.02, (xc, -0.005, zc), (1, 0, 0), (0, 0, 1), bisel=0.0006)
    # sol que da de lleno en la pared de montaje y rasante en la de fondo,
    # como en la foto: la sombra del cartel cae en la pared de los listones
    sol((-0.80, 0.30, -0.52), 3.4, 'FFF1DC', 0.6)
    camara((1.02, -1.02, 1.45), (0.46, 0.0, 1.70), 40, exposicion=-0.3)
    return [lg], ancho, 0.0


def montar_caja():
    """Caja de luz en bandera (Кицуня): metacrilato azzurro iluminado por
    dentro, logo en el costado largo y en la testa, en pared de ladrillo
    encalado con una pilastra de revoco."""
    mundo('E4E2DC', 0.7)
    caja('Pared', -2.5, 0.0, 2.5, 0.3, 0.0, 6.0,
         mat_pbr('Ladrillo encalado', 'painted_brick', 1.8, tinte='F4EFE6', sat=0.08, val=1.25))
    caja('Pilastra', -0.95, -0.03, -0.35, 0.0, 0.0, 6.0,
         mat_pbr('Revoco arena', 'plaster_grey_04', 1.5, tinte='E0CBAE'))
    luz = mat_liso('Caja azzurro', AZZURRO, rough=0.3, coat=0.2, emis=AZZURRO, fuerza=0.9)
    caja('Caja de luz', -0.17, -0.62, 0.17, 0.0, 1.85, 2.17, luz, bisel=0.006)
    ancho = 0.46
    logos = [logo('Logo costado', ancho, 0.0006, (0.17, -0.31, 2.01), (0, 1, 0), (0, 0, 1)),
             logo('Logo testa', 0.28, 0.0006, (0.0, -0.62, 2.01), (1, 0, 0), (0, 0, 1))]
    luz_area('Cielo cubierto', (-1.5, -2.5, 3.0), (0.0, -0.3, 2.0), 1.5, 220, 'F4F1EA')
    camara((1.05, -1.55, 1.50), (0.02, -0.30, 1.98), 35, exposicion=0.0)
    return logos, ancho, 3.0


def montar_placa():
    """Placa cuadrada en bandera (Aesop): dos caras azzurro con el canto
    retroiluminado entre ellas, en pletina de acero sobre ladrillo rojo, de
    noche."""
    mundo('0B1424', 0.35)
    caja('Pared', -2.5, 0.0, 2.5, 0.3, 0.0, 4.0, mat_pbr('Ladrillo rojo', 'red_brick_03', 1.0))
    y0, y1, z0, z1 = -0.72, -0.12, 2.30, 2.90
    caja('Placa · canto de luz', -0.018, y0, 0.018, y1, z0, z1,
         mat_liso('Canto de luz', 'FFFFFF', emis='F4F8FF', fuerza=8.0))
    azz = mat_liso('Azzurro satinado', AZZURRO, rough=0.35)
    caja('Placa · cara Este', 0.018, y0, 0.030, y1, z0, z1, azz, 0.002)
    caja('Placa · cara Oeste', -0.030, y0, -0.018, y1, z0, z1, azz, 0.002)
    acero = mat_liso('Acero', '2A2A2C', rough=0.45, metal=0.7)
    caja('Pletina', -0.022, -0.012, 0.022, 0.0, z0 - 0.06, z1 + 0.06, acero, 0.002)
    for i, zb in enumerate((z0 + 0.10, z1 - 0.10)):
        caja(f'Brazo {i + 1}', -0.008, y1, 0.008, -0.012, zb - 0.015, zb + 0.015, acero)
    ancho = 0.46
    lg = logo('Logo', ancho, 0.0015, (0.030, (y0 + y1) / 2, (z0 + z1) / 2),
              (0, 1, 0), (0, 0, 1))
    luz_area('Farola', (1.8, -2.2, 3.6), (0.0, -0.4, 2.2), 0.4, 60, 'FFD9A8')
    # relleno neutro desde la calle: con solo la farola calida el azzurro
    # viraba a verde
    luz_area('Relleno', (1.6, -1.2, 2.0), (0.03, -0.42, 2.6), 0.8, 30, 'EEF2F8')
    camara((0.98, -1.42, 1.78), (0.02, -0.42, 2.62), 35, exposicion=0.0)
    return [lg], ancho, 6.0


def montar_colgado():
    """Caja de luz alargada (Jam): azzurro iluminada, colgada de un soporte
    oscuro en un pilar gris, delante de una pared oscura."""
    mundo('101216', 0.25)
    caja('Pared de fondo', -3.0, 1.2, 3.0, 1.4, 0.0, 4.0,
         mat_pbr('Pared oscura', 'plastered_wall', 2.0, tinte='3A3C40'))
    caja('Pilar', 0.62, -0.30, 0.95, 1.2, 0.0, 4.0,
         mat_pbr('Pilar gris', 'plaster_grey_04', 1.5, tinte='A9ABAE'))
    luz = mat_liso('Caja azzurro', AZZURRO, rough=0.3, coat=0.2, emis=AZZURRO, fuerza=0.9)
    caja('Caja de luz', -0.52, -0.08, 0.48, 0.08, 2.00, 2.40, luz, bisel=0.008)
    caja('Soporte', 0.48, -0.05, 0.62, 0.05, 2.06, 2.34,
         mat_liso('Soporte', '2B2C2E', rough=0.5, metal=0.4), 0.003)
    ancho = 0.66
    lg = logo('Logo', ancho, 0.0006, (-0.02, -0.08, 2.20), (1, 0, 0), (0, 0, 1))
    luz_area('Luz cenital', (0.0, -0.6, 3.6), (0.0, 0.0, 2.2), 1.2, 40, 'F2F4F7')
    camara((-0.60, -1.75, 1.80), (0.0, 0.0, 2.20), 45, exposicion=0.0)
    return [lg], ancho, 3.0


def montar_barra():
    """Barra en la pared (Watanabe): azzurro, separada 2 cm del muro, logo
    calado con luz detras y halo arriba y abajo, en revoco gris, de noche."""
    mundo('0C0F14', 0.3)
    caja('Muro', -0.55, 0.0, 1.8, 0.25, 0.0, 2.2,
         mat_pbr('Revoco gris', 'plaster_grey_04', 1.5, tinte='8C9096'))
    caja('Barra', -0.40, -0.07, 0.40, -0.02, 1.28, 1.56,
         mat_liso('Azzurro satinado', AZZURRO, rough=0.35), 0.003)
    ancho = 0.62
    lg = logo('Logo', ancho, 0.003, (0.0, -0.07, 1.42), (1, 0, 0), (0, 0, 1))
    calida = 'FFD8A8'
    luz_area('Halo arriba', (0.0, -0.045, 1.565), (0.0, -0.045, 3.0), (0.76, 0.02), 12, calida)
    luz_area('Halo abajo', (0.0, -0.045, 1.275), (0.0, -0.045, 0.0), (0.76, 0.02), 12, calida)
    luz_area('Halo detras', (0.0, -0.019, 1.42), (0.0, 1.0, 1.42), (0.70, 0.22), 8, calida)
    luz_area('Relleno', (-0.8, -2.0, 1.8), (0.0, 0.0, 1.42), 1.0, 25, 'E8EEF5')
    camara((-0.42, -1.45, 1.44), (0.03, 0.0, 1.42), 40, exposicion=0.0)
    return [lg], ancho, 8.0


CARTELES = [
    ('ovalo', 'Óvalo en bandera · letras en relieve', montar_ovalo),
    ('caja', 'Caja de luz en bandera', montar_caja),
    ('placa', 'Placa cuadrada · canto de luz', montar_placa),
    ('colgado', 'Caja de luz colgada', montar_colgado),
    ('barra', 'Barra · logo calado y halo', montar_barra),
]


# ===================================================================== hojas
def hoja(titulo, imagenes, salida):
    """Las seis opciones de un cartel en una hoja, como la de ideas."""
    from PIL import Image, ImageDraw, ImageFont
    fuente = '/usr/share/fonts/truetype/liberation/LiberationSans-{}.ttf'
    f_eti = ImageFont.truetype(fuente.format('Regular'), 34)
    tiles = [(nombre, Image.open(r).convert('RGB')) for nombre, r in imagenes]
    # a tamaño real: reducidas a la mitad, el marmol del logo no se veia
    tw, th = tiles[0][1].width, tiles[0][1].height
    m, cab, pie = 28, 104, 62
    W = 2 * tw + 3 * m
    H = cab + 3 * (th + pie) + m
    lienzo = Image.new('RGB', (W, H), (246, 244, 240))
    d = ImageDraw.Draw(lienzo)
    texto = f'CASA MARGOT  ·  {titulo}'
    tam = 56
    while tam > 20:
        f_tit = ImageFont.truetype(fuente.format('Bold'), tam)
        if d.textlength(texto, font=f_tit) <= W - 2 * m:
            break
        tam -= 2
    d.text((m, 30), texto, font=f_tit, fill=(20, 20, 20))
    for i, (nombre, im) in enumerate(tiles):
        c, f = i % 2, i // 2
        x, y = m + c * (tw + m), cab + f * (th + pie)
        lienzo.paste(im, (x, y))
        d.text((x, y + th + 12), nombre, font=f_eti, fill=(40, 40, 40))
    lienzo.save(salida, quality=90)


# ====================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--carteles', default=','.join(c[0] for c in CARTELES))
    ap.add_argument('--acabados', default=','.join(a[0] for a in ACABADOS))
    ap.add_argument('--spp', type=int, default=64)
    ap.add_argument('--ancho', type=int, default=900)
    ap.add_argument('--salida', default=os.path.join(TRABAJO, 'render'))
    a = ap.parse_args()
    os.makedirs(a.salida, exist_ok=True)
    pedidos = a.carteles.split(',')
    acabados = [x for x in ACABADOS if x[0] in a.acabados.split(',')]
    for clave, titulo, montar in CARTELES:
        if clave not in pedidos:
            continue
        escena_nueva(a.ancho, round(a.ancho * 1.25), a.spp)
        logos, ancho_logo, luz = montar()
        hechas = []
        for ac, nombre in acabados:
            m = mat_acabado(ac, ancho_logo, luz)
            for lg in logos:
                lg.data.materials.clear()
                lg.data.materials.append(m)
            ruta = os.path.join(a.salida, f'{clave}_{ac}.png')
            bpy.context.scene.render.filepath = ruta
            t = time.time()
            bpy.ops.render.render(write_still=True)
            print(f'  {clave} {ac} en {time.time() - t:.0f} s', flush=True)
            hechas.append((nombre, ruta))
        if len(hechas) == len(ACABADOS):
            hoja(titulo, hechas, os.path.join(a.salida, f'{clave}_opciones.jpg'))
            print(f'  hoja {clave}_opciones.jpg', flush=True)
    print('LISTO', flush=True)


if __name__ == '__main__':
    main()
