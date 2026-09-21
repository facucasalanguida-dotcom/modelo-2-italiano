# -*- coding: utf-8 -*-
"""
Paleta de materiales de Casa Margot para Cycles.

Es la misma paleta con la que se hicieron los renders anteriores (texturas
escaneadas 4K de Poly Haven, CC0, proyeccion de caja sobre coordenadas de
objeto), con un solo cambio de proyecto: el azul del frente de la barra y de
la banda de rotulo pasa a ser el azzurro oficial del SSC Napoli.

    AZZURRO = #12A0D7   (Pantone 2995 C, RGB 18/160/215)

Las claves del diccionario MAT son las del generador de planos
(docs/planos/export_sketchup.MAT), asi que la escena se puede texturizar
recorriendo MODELO_3D.json sin traducir nada.
"""
import glob
import os

import bpy

PH = os.environ.get('PH_DIR', '/tmp/claude-0/-home-user-modelo-2-italiano/'
                              '30d2763c-3169-519a-ac78-c5a47134634b/scratchpad/ph')

AZZURRO = '12A0D7'          # SSC Napoli, Pantone 2995 C
AZUL_HONDO = '003C82'       # el azul oscuro del escudo, para detalles

_img_cache = {}
_map_cache = {}


# ------------------------------------------------------------------ utiles
def srgb(hexs):
    """Hex de diseno -> lineal, que es lo que come Cycles."""
    v = [int(hexs[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in v)


def imagen(ruta, sin_color=False):
    k = (ruta, sin_color)
    if k not in _img_cache:
        im = bpy.data.images.load(ruta)
        if sin_color:
            im.colorspace_settings.name = 'Non-Color'
        _img_cache[k] = im
    return _img_cache[k]


# Cycles carga cada mapa entero en RAM. Con ~120 mapas a 4096x4096 el proceso
# pasa de 13 GB y lo mata el sistema, asi que se usan las copias a 2K que
# genera scratchpad/ph/hacer_2k.py. A la resolucion de salida no se distingue:
# la proyeccion de caja reparte la textura en tramos de 1,5 a 3 m.
DOS_K = os.environ.get('CM_4K', '') == ''


def mapas(aid):
    """Mapas de un activo de Poly Haven ya descargado (2K salvo que se pida 4K)."""
    if aid in _map_cache:
        return _map_cache[aid]
    d2 = f'{PH}/{aid}/textures_2k'
    d = d2 if (DOS_K and os.path.isdir(d2)) else f'{PH}/{aid}/textures'

    def uno(pat):
        c = sorted(glob.glob(f'{d}/{aid}_{pat}_4k.*'),
                   key=lambda x: (not x.endswith('.png'), x))
        return c[0] if c else None

    m = {'diff': uno('diff'), 'rough': uno('rough'), 'nrm': uno('nor_gl'),
         'ao': uno('ao'), 'disp': uno('disp')}
    _map_cache[aid] = m
    return m


_medias = {}


def media_lineal(ruta):
    """Media lineal de una textura. Sirve para normalizarla y poder fijar el
    albedo de verdad: el enlucido escaneado de Poly Haven refleja un 26 %, y
    una pared pintada refleja el 75-85 %. Sin esto las paredes salen grises."""
    if ruta not in _medias:
        import numpy as np
        from PIL import Image
        im = Image.open(ruta).convert('RGB')
        im.thumbnail((128, 128))
        a = np.asarray(im, dtype=float) / 255.0
        lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        _medias[ruta] = tuple(max(1e-4, float(v)) for v in lin.reshape(-1, 3).mean(0))
    return _medias[ruta]


def _nuevo(nombre):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (700, 0)
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.location = (350, 0)
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    return m, nt, b


def _set(b, clave, valor):
    if clave in b.inputs:
        b.inputs[clave].default_value = valor


# ------------------------------------------------------------- fabricas
def liso(nombre, rgb, rug=0.6, metal=0.0, coat=0.0, aniso=0.0, sheen_=False):
    m, nt, b = _nuevo(nombre)
    if sheen_:
        _set(b, 'Sheen Weight', 0.7)
        _set(b, 'Sheen Roughness', 0.4)
    _set(b, 'Base Color', (*rgb, 1))
    _set(b, 'Roughness', rug)
    _set(b, 'Metallic', metal)
    _set(b, 'Coat Weight', coat)
    _set(b, 'Anisotropic', aniso)
    return m


def pbr(nombre, aid, tam=1.0, tint=None, color=None, nrm_str=0.6, coat=0.0,
        metal=0.0, rug=None, ao_fac=0.5, mezcla_caja=0.3, generada=False,
        albedo=None):
    """Material escaneado: color + rugosidad + normal, en proyeccion de caja.

    tam es el lado en metros que ocupa una repeticion de la textura, medido
    sobre el objeto: asi la escala no depende de las UV, que la geometria
    generada no trae.
    """
    m, nt, b = _nuevo(nombre)
    mp_ = mapas(aid)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    tc.location = (-1100, 0)
    mapa = nt.nodes.new('ShaderNodeMapping')
    mapa.location = (-900, 0)
    mapa.inputs['Scale'].default_value = (1 / tam, 1 / tam, 1 / tam)
    nt.links.new(tc.outputs['Generated' if generada else 'Object'], mapa.inputs['Vector'])

    def tex(ruta, sin_color, y):
        n = nt.nodes.new('ShaderNodeTexImage')
        n.location = (-650, y)
        n.image = imagen(ruta, sin_color)
        n.projection = 'BOX'
        n.projection_blend = mezcla_caja
        nt.links.new(mapa.outputs['Vector'], n.inputs['Vector'])
        return n

    col = None
    if color is not None:
        _set(b, 'Base Color', (*color, 1))
    elif mp_['diff']:
        col = tex(mp_['diff'], False, 300).outputs['Color']
        if mp_['ao'] and ao_fac > 0:
            ao = tex(mp_['ao'], True, 600)
            mx = nt.nodes.new('ShaderNodeMix')
            mx.location = (-380, 450)
            mx.data_type = 'RGBA'
            mx.blend_type = 'MULTIPLY'
            mx.inputs['Factor'].default_value = ao_fac
            nt.links.new(col, mx.inputs[6])
            nt.links.new(ao.outputs['Color'], mx.inputs[7])
            col = mx.outputs[2]
        if albedo:
            # la textura se normaliza por su media y se multiplica por el
            # albedo pedido: conserva el grano y fija la claridad real
            med = media_lineal(mp_['diff'])
            obj = srgb(albedo)
            k = tuple(min(6.0, obj[i] / med[i]) for i in range(3))
            ma = nt.nodes.new('ShaderNodeMix')
            ma.location = (-180, 480)
            ma.data_type = 'RGBA'
            ma.blend_type = 'MULTIPLY'
            ma.inputs['Factor'].default_value = 1.0
            ma.inputs[7].default_value = (*k, 1)
            nt.links.new(col, ma.inputs[6])
            col = ma.outputs[2]
        if tint:
            mt = nt.nodes.new('ShaderNodeMix')
            mt.location = (-180, 380)
            mt.data_type = 'RGBA'
            mt.blend_type = 'MULTIPLY'
            mt.inputs['Factor'].default_value = 1.0
            mt.inputs[7].default_value = (*tint, 1)
            nt.links.new(col, mt.inputs[6])
            col = mt.outputs[2]
        nt.links.new(col, b.inputs['Base Color'])

    if rug is not None:
        _set(b, 'Roughness', rug)
    elif mp_['rough']:
        nt.links.new(tex(mp_['rough'], True, 0).outputs['Color'], b.inputs['Roughness'])
    else:
        _set(b, 'Roughness', 0.5)

    if mp_['nrm'] and nrm_str > 0:
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nm.location = (-380, -300)
        nm.inputs['Strength'].default_value = nrm_str
        nt.links.new(tex(mp_['nrm'], True, -300).outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])

    _set(b, 'Coat Weight', coat)
    _set(b, 'Metallic', metal)
    return m


def pintura(nombre, hexcol, rug=0.42, coat=0.10, textura='white_plaster_02', tam=2.4):
    """Pared pintada: el color manda, pero conserva el grano del enlucido."""
    m = pbr(nombre, textura, tam, color=srgb(hexcol), nrm_str=0.35, coat=coat, rug=rug)
    return m


def madera_tenida(nombre, hexcol, tam=1.3, nrm_str=0.45, rug=0.45):
    """Madera pintada: el veteado sigue leyendose en normal y rugosidad.

    Es como se resolvio el frente de la barra en los renders anteriores, y es
    lo que hace que el azul no parezca plastico.
    """
    return pbr(nombre, 'oak_veneer_01', tam, color=srgb(hexcol),
               nrm_str=nrm_str, rug=rug, ao_fac=0.0)


def inox(nombre, rug=0.18, aniso=0.45, color='CBD0D4'):
    """Acero inoxidable cepillado con velo de uso."""
    m, nt, b = _nuevo(nombre)
    _set(b, 'Base Color', (*srgb(color), 1))
    _set(b, 'Metallic', 1.0)
    _set(b, 'Anisotropic', aniso)
    ns = nt.nodes.new('ShaderNodeTexNoise')
    ns.location = (-600, -200)
    ns.inputs['Scale'].default_value = 90.0
    ns.inputs['Detail'].default_value = 3.0
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.location = (-350, -200)
    mr.inputs['From Min'].default_value = 0.30
    mr.inputs['From Max'].default_value = 0.70
    mr.inputs['To Min'].default_value = rug * 0.90
    mr.inputs['To Max'].default_value = rug * 1.15
    nt.links.new(ns.outputs['Fac'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], b.inputs['Roughness'])
    return m


def vidrio_arq(nombre, reflejo=0.07):
    """Paños grandes de fachada: transparente + un poco de glossy.

    Un vidrio de refraccion real en un paño de 4 m deja el interior sucio de
    ruido; asi el denoiser ve a traves y el reflejo sigue estando.
    """
    m, nt, b = _nuevo(nombre)
    nt.nodes.remove(b)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    tr.location = (100, 100)
    gl = nt.nodes.new('ShaderNodeBsdfGlossy')
    gl.location = (100, -150)
    gl.inputs['Roughness'].default_value = 0.02
    mx = nt.nodes.new('ShaderNodeMixShader')
    mx.location = (400, 0)
    mx.inputs['Fac'].default_value = reflejo
    nt.links.new(tr.outputs['BSDF'], mx.inputs[1])
    nt.links.new(gl.outputs['BSDF'], mx.inputs[2])
    nt.links.new(mx.outputs['Shader'], out.inputs['Surface'])
    m.use_backface_culling = False
    return m


def vidrio(nombre, tinte=(0.96, 0.99, 0.97), rug=0.0):
    """Vidrio de verdad, para vitrinas, copas y botellas."""
    m, nt, b = _nuevo(nombre)
    _set(b, 'Base Color', (*tinte, 1))
    _set(b, 'Roughness', rug)
    _set(b, 'Transmission Weight', 1.0)
    _set(b, 'IOR', 1.45)
    return m


def emision(nombre, rgb, fuerza):
    m, nt, b = _nuevo(nombre)
    _set(b, 'Base Color', (*rgb, 1))
    _set(b, 'Emission Color', (*rgb, 1))
    _set(b, 'Emission Strength', fuerza)
    _set(b, 'Roughness', 0.4)
    return m


def boucle(nombre, hexcol, rug=0.88):
    """Tejido boucle de la tapiceria: rizo fino en el bump y sheen alto."""
    m, nt, b = _nuevo(nombre)
    _set(b, 'Base Color', (*srgb(hexcol), 1))
    _set(b, 'Roughness', rug)
    _set(b, 'Sheen Weight', 1.0)
    _set(b, 'Sheen Roughness', 0.45)
    vor = nt.nodes.new('ShaderNodeTexVoronoi')
    vor.location = (-600, -200)
    vor.inputs['Scale'].default_value = 430.0
    bm = nt.nodes.new('ShaderNodeBump')
    bm.location = (-350, -200)
    bm.inputs['Strength'].default_value = 0.55
    bm.inputs['Distance'].default_value = 0.0016
    nt.links.new(vor.outputs['Distance'], bm.inputs['Height'])
    nt.links.new(bm.outputs['Normal'], b.inputs['Normal'])
    return m


def calca(nombre, ruta_png, emisivo=0.0, rug=0.45):
    """PNG con alfa sobre un plano: el vinilo de plotter del logo."""
    m, nt, b = _nuevo(nombre)
    im = imagen(ruta_png)
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.location = (-500, 0)
    tex.image = im
    tex.extension = 'CLIP'
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
    _set(b, 'Roughness', rug)
    if emisivo:
        nt.links.new(tex.outputs['Color'], b.inputs['Emission Color'])
        _set(b, 'Emission Strength', emisivo)
    # el alfa del PNG recorta el plano
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    tr.location = (100, 250)
    mx = nt.nodes.new('ShaderNodeMixShader')
    mx.location = (520, 120)
    nt.links.new(tex.outputs['Alpha'], mx.inputs['Fac'])
    nt.links.new(tr.outputs['BSDF'], mx.inputs[1])
    nt.links.new(b.outputs['BSDF'], mx.inputs[2])
    nt.links.new(mx.outputs['Shader'], out.inputs['Surface'])
    return m


# ------------------------------------------------------------------ paleta
def construir():
    """Todos los materiales de la escena, por la clave del generador de planos."""
    M = {
        # --- obra
        'muro':     pbr('Muro enlucido', 'white_plaster_02', 2.6, albedo='EDE6D8', nrm_str=0.55),
        'tabique':  pbr('Tabique', 'white_plaster_02', 2.6, albedo='F0EBE0', nrm_str=0.45),
        'pilar':    pbr('Pilar hormigon', 'plastered_wall', 2.2, albedo='C9C4BA', nrm_str=0.7),
        'forjado':  pbr('Forjado', 'plastered_wall', 2.4, albedo='DCD7CC', nrm_str=0.5),
        'solera':   pbr('Solera', 'concrete_floor_worn_001', 3.0, tint=(0.88, 0.87, 0.85)),
        'falso':    pbr('Falso techo', 'white_plaster_02', 2.6, albedo='F5F2EC', nrm_str=0.25),
        'piedra':   pbr('Piedra', 'granite_tile', 2.3, albedo='9E9A94', coat=0.06, nrm_str=0.8),
        'escalera': pbr('Escalera', 'wood_floor', 1.7, albedo='BE9260', coat=0.10, nrm_str=0.8),

        # --- carpinteria y vidrio
        'vidrio':   vidrio_arq('Vidrio fachada'),
        'carp':     liso('Carpinteria negra', srgb('2A2A28'), 0.40, 0.40),

        # --- maderas
        # OJO: la clave 'madera' del plano la usan la tabla del mostrador, la
        # tabla de P2 y las hojas de puerta. El azzurro va SOLO en los
        # listones del frente de barra, que la escena construye aparte con
        # '_liston_azul'. Pintar aqui de azul dejaba la puerta del bano y las
        # del altillo en azul Napoli.
        'madera':   pbr('Madera de obra', 'oak_veneer_01', 1.35, albedo='C0945F',
                        coat=0.10, nrm_str=0.55),
        'mesa':     pbr('Tablero mesa', 'oak_veneer_01', 1.5, albedo='C79B68', coat=0.10, nrm_str=0.55),
        'silla':    pbr('Madera silla', 'oak_veneer_01', 1.4, albedo='CFA575', nrm_str=0.5),
        'sillon':   boucle('Boucle crema', 'E9DFC9'),

        # --- equipamiento
        'inox':     inox('Acero inoxidable', rug=0.34, aniso=0.28, color='BFC5CA'),
        'aparato':  inox('Aparato inox', rug=0.24, aniso=0.35),
        'frio':     inox('Equipo de frio', rug=0.22, aniso=0.40),
        'encimera': pbr('Encimera marmol', 'marble_01', 2.0, albedo='E6E1D6', coat=0.25, nrm_str=0.35),

        # --- instalaciones
        'luz':      emision('Opal', srgb('FFF4E0'), 2.0),
        'aire':     liso('Aire acondicionado', srgb('EEEEEB'), 0.45),
        'rejilla':  liso('Rejilla', srgb('AAACAE'), 0.50, 0.60),
    }

    # --- materiales que no vienen del plano pero hacen la escena
    # pantallas de luminaria: opal encendido, no plastico gris
    M['_opal'] = emision('Opal encendido', srgb('FFF6E6'), 3.2)
    M['luz'] = emision('Luz de luminaria', srgb('FFF4E0'), 11.0)
    M['_liston'] = pbr('Liston de roble', 'oak_veneer_01', 1.3, albedo='C89C6A', nrm_str=0.6)
    M['_liston_azul'] = madera_tenida('Liston azzurro', AZZURRO, nrm_str=0.40, rug=0.42)
    M['_suelo'] = pbr('Suelo de roble', 'wood_floor', 1.7, albedo='C09563', coat=0.12, nrm_str=0.85)
    M['_pared_napoli'] = pintura('Pared azzurro Napoli', AZZURRO, rug=0.45, coat=0.05)
    M['_vinilo'] = liso('Vinilo de plotter', srgb('222222'), 0.55)
    M['_blanco_lacado'] = liso('Blanco lacado', srgb('F4F4F1'), 0.28, coat=0.35)
    M['_laton'] = liso('Laton', srgb('C69E54'), 0.25, 1.0)
    M['_negro'] = liso('Negro mate', srgb('262524'), 0.55)
    M['_blanco'] = pbr('Blanco roto', 'white_plaster_02', 2.6, albedo='F2EFE8', nrm_str=0.3)
    M['_tela_azul'] = boucle('Boucle azzurro', '9FD3EA')
    M['_terracota'] = liso('Terracota', srgb('A9714F'), 0.72)
    M['_planta'] = liso('Hoja', srgb('5F7F4C'), 0.72)
    M['_vidrio_copa'] = vidrio('Vidrio de copa')
    M['_luz_calida'] = emision('Luz calida', srgb('FFDCA6'), 2.2)
    M['_marmol'] = pbr('Marmol', 'marble_01', 1.6, coat=0.30, nrm_str=0.30)

    # ------------------------------------------------------------ la calle
    # Por un escaparate de doble altura se ve la calle entera, asi que la
    # ciudad no puede ser el HDRI: tiene que estar construida y tener
    # materiales propios.
    M['_acera'] = pbr('Acera', 'large_floor_tiles_02', 2.4, albedo='B9B4AA', nrm_str=0.8)
    M['_asfalto'] = pbr('Asfalto', 'asphalt_02', 3.2, albedo='4A4845', nrm_str=0.9)
    M['_pintura_vial'] = liso('Pintura vial', srgb('D8D4C8'), 0.68)
    M['_tierra'] = liso('Tierra de alcorque', srgb('4A3A2C'), 0.92)
    M['_cornisa'] = pbr('Cornisa', 'white_plaster_02', 1.8, albedo='EDE8DC', nrm_str=0.4)
    M['_teja'] = pbr('Teja', 'clay_roof_tiles', 1.1, albedo='9A5A3C', nrm_str=1.0) \
        if mapas('clay_roof_tiles')['diff'] else liso('Teja', srgb('9A5A3C'), 0.8)
    M['_persiana'] = liso('Persiana', srgb('C8C3B4'), 0.62)
    M['_interior_calle'] = liso('Interior de vivienda', srgb('14100C'), 0.9)
    M['_vidrio_calle'] = vidrio_arq('Vidrio de la calle', reflejo=0.16)
    M['_luz_farola'] = emision('Luz de farola', srgb('FFE2B0'), 6.0)
    # fachadas de la manzana de enfrente, en ocres de Malaga
    M['_fachada'] = [pintura(f'Fachada {i + 1}', c, rug=0.62, coat=0.0,
                             textura='plastered_wall', tam=3.4)
                     for i, c in enumerate(('D9C9A8', 'E6DCC8', 'C9A882', 'EFE7D6',
                                            'D2B896', 'E3D6BC', 'CDBEA4'))]
    M['_bajo'] = [liso(f'Bajo comercial {i + 1}', srgb(c), 0.45, coat=0.15)
                  for i, c in enumerate(('B08A63', '7C6A58', '3E4A52', '8C5C48',
                                         '445048', '9A6A4A', '5A4438'))]
    M['_toldo'] = [liso(f'Toldo {i + 1}', srgb(c), 0.72, sheen_=True)
                   for i, c in enumerate(('8E2F2A', '1F4E3D', 'C8912F', '2B4C7E'))]
    # coches
    M['_luna'] = vidrio_arq('Luna de coche', reflejo=0.34)
    M['_faro'] = liso('Faro', srgb('E8ECEF'), 0.10, coat=0.9)
    M['_piloto'] = liso('Piloto', srgb('8E1410'), 0.20, coat=0.8)
    M['_neumatico'] = liso('Neumatico', srgb('16171A'), 0.82)
    M['_llanta'] = liso('Llanta', srgb('B8BCC0'), 0.24, metal=1.0)
    M['_paragolpes'] = liso('Paragolpes', srgb('2A2C2E'), 0.46)
    M['_rejilla_coche'] = liso('Parrilla', srgb('0E0F11'), 0.38)
    M['_junta_coche'] = liso('Junta de puerta', srgb('141516'), 0.60)
    M['_hueco_rueda'] = liso('Hueco de rueda', srgb('090A0B'), 0.85)
    M['_coche'] = [liso(f'Carroceria {i + 1}', srgb(c), 0.18, metal=0.60, coat=0.95)
                   for i, c in enumerate(('1C2733', 'A8ADB2', '8E1B18', 'E8E9EA',
                                          '2E4636', '3A3F45', 'C2B9A8'))]
    return M
