# -*- coding: utf-8 -*-
"""
Piezas comunes de maquinaria de hosteleria, parametrizadas en metros.
Todas devuelven la lista de mallas creadas y respetan las convenciones de
lib.py (frente a -Y, z = 0 en la base, se cuelgan del Empty raiz).
"""
import math
import bmesh
import bpy
import lib as L
from mathutils import Vector


# ------------------------------------------------------------- patas
def pata_regulable(nombre, pos, h, d_tubo=0.040, d_pie=0.050, h_pie=0.030,
                   mat_tubo=None, mat_pie=None, parent=None):
    """Pata de tubo inox con pie regulable: pie de plastico/inox de
    d_pie x h_pie abajo, esparrago y tubo encima hasta h. `pos` = centro
    de la huella de la pata en el suelo."""
    mat_tubo = mat_tubo or L.mat_inox()
    mat_pie = mat_pie or L.mat_plastico('Plastico gris', (0.30, 0.30, 0.30))
    x, y, z = pos
    out = [L.cilindro(nombre + ' pie', d_pie / 2, h_pie, (x, y, z), r=0.004,
                      segs=48, mat=mat_pie, parent=parent),
           L.cilindro(nombre + ' rosca', d_tubo * 0.32, 0.02, (x, y, z + h_pie),
                      segs=24, mat=L.mat_inox_pulido(), parent=parent),
           L.cilindro(nombre + ' tubo', d_tubo / 2, h - h_pie - 0.015,
                      (x, y, z + h_pie + 0.015), segs=48, mat=mat_tubo, parent=parent)]
    return out


def patas_bastidor(nombre, w, d, h, inset=0.045, **kw):
    """Cuatro patas regulables en las esquinas de una huella w x d."""
    out = []
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        out += pata_regulable(f'{nombre} {i + 1}', (sx * (w / 2 - inset), sy * (d / 2 - inset), 0), h, **kw)
    return out


def pie_goma(nombre, pos, d=0.030, h=0.012, mat=None, parent=None):
    """Pie de goma de aparato de sobremesa."""
    return L.cilindro(nombre, d / 2, h, pos, r=0.003, segs=32,
                      mat=mat or L.mat_goma(), parent=parent)


def pies_goma(nombre, w, fondo, inset=0.030, **kw):
    return [pie_goma(f'{nombre} {i + 1}', (sx * (w / 2 - inset), sy * (fondo / 2 - inset), 0), **kw)
            for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1)))]


# ------------------------------------------------------------- tiradores
def tirador_barra(nombre, centro, largo, orient='H', d=0.020, saliente=0.040,
                  separadores=None, mat=None, parent=None, normal='-Y'):
    """Tirador de barra (tubo) con dos soportes, sobre una cara vertical.
    `centro` es el punto de la cara donde va el centro del tirador. `orient`
    H (horizontal) o V. La barra queda separada `saliente` de la cara."""
    mat = mat or L.mat_inox_pulido()
    cx, cy, cz = centro
    sep = separadores if separadores is not None else largo - 0.06
    n = {'-Y': Vector((0, -1, 0)), '+Y': Vector((0, 1, 0)),
         '+X': Vector((1, 0, 0)), '-X': Vector((-1, 0, 0))}[normal]
    out = []
    lado = Vector((1, 0, 0)) if normal in ('-Y', '+Y') else Vector((0, 1, 0))
    if orient == 'V':
        lado = Vector((0, 0, 1))
    eje_barra = 'X' if (orient == 'H' and normal in ('-Y', '+Y')) else ('Y' if orient == 'H' else 'Z')
    p_barra = Vector(centro) + n * (saliente - d / 2) - lado * (largo / 2)
    out.append(L.cilindro(nombre, d / 2, largo, tuple(p_barra), eje=eje_barra, r=d * 0.45,
                          r_segs=4, segs=40, mat=mat, parent=parent))
    eje_sop = {'-Y': 'Y', '+Y': 'Y', '+X': 'X', '-X': 'X'}[normal]
    for i, s in enumerate((-1, 1)):
        base = Vector(centro) + lado * (s * sep / 2)
        if normal in ('+Y', '+X'):
            p = base
        else:
            p = base + n * (saliente - d / 2)
        out.append(L.cilindro(f'{nombre} soporte {i + 1}', d * 0.42, saliente - d / 2,
                              tuple(p), eje=eje_sop, segs=32, mat=mat, parent=parent))
    return out


def tirador_embutido(nombre, centro, largo, alto=0.030, fondo=0.018, cuerpo=None,
                     normal='-Y', mat=None, parent=None):
    """Tirador embutido: hueco rectangular en la cara (booleana sobre
    `cuerpo`) con una pestana superior. Devuelve la pestana."""
    cx, cy, cz = centro
    if cuerpo is not None:
        cortador = L.caja(nombre + ' corte', largo, fondo * 2, alto,
                          (cx, cy, cz - alto / 2), r=0.004)
        L.sustraer(cuerpo, cortador)
    pest = L.caja(nombre, largo, fondo, 0.004, (cx, cy - fondo / 2 + 0.001, cz + alto / 2 - 0.004),
                  r=0.001, mat=mat or L.mat_inox(), parent=parent)
    return [pest]


# ------------------------------------------------------------- mandos
def mando_ruleta(nombre, centro, d=0.040, alto=0.022, normal='-Y', mat=None,
                 marca=True, parent=None, faldon=True):
    """Mando giratorio: faldon conico + cuerpo cilindrico + indicador.
    `centro` = punto en la cara donde apoya."""
    mat = mat or L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02))
    eje = 'Y' if normal in ('-Y', '+Y') else 'X'
    n = {'-Y': Vector((0, -1, 0)), '+Y': Vector((0, 1, 0)),
         '+X': Vector((1, 0, 0)), '-X': Vector((-1, 0, 0))}[normal]
    c = Vector(centro)
    out = []
    if normal in ('+Y', '+X'):
        base = c
    else:
        base = c + n * alto
    if faldon:
        f = c + (n * 0.006 if normal in ('-Y', '-X') else Vector((0, 0, 0)))
        out.append(L.cilindro(nombre + ' faldon', d * 0.62, 0.006, tuple(f), eje=eje,
                              segs=48, mat=mat, parent=parent, radio2=d * 0.5))
    out.append(L.cilindro(nombre, d / 2, alto, tuple(base), eje=eje, r=0.003,
                          segs=48, mat=mat, parent=parent))
    if marca:
        # linea indicadora blanca en la cara vista, del centro al borde
        p = c + n * (alto + 0.0003)
        if normal in ('-Y', '+Y'):
            ind = L.caja(nombre + ' indice', 0.003, 0.0006, d * 0.38, (p.x, p.y, p.z + d * 0.06),
                         mat=L.mat_plastico('Plastico blanco', (0.85, 0.85, 0.82)), parent=parent, suave=False)
        else:
            ind = L.caja(nombre + ' indice', 0.0006, 0.003, d * 0.38, (p.x, p.y, p.z + d * 0.06),
                         mat=L.mat_plastico('Plastico blanco', (0.85, 0.85, 0.82)), parent=parent, suave=False)
        out.append(ind)
    return out


def boton(nombre, centro, d=0.012, alto=0.004, normal='-Y', mat=None, parent=None):
    eje = 'Y' if normal in ('-Y', '+Y') else 'X'
    n = {'-Y': Vector((0, -1, 0)), '+Y': Vector((0, 1, 0)),
         '+X': Vector((1, 0, 0)), '-X': Vector((-1, 0, 0))}[normal]
    c = Vector(centro)
    base = c if normal in ('+Y', '+X') else c + n * alto
    return L.cilindro(nombre, d / 2, alto, tuple(base), eje=eje, r=0.001, segs=32,
                      mat=mat or L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02)), parent=parent)


def piloto(nombre, centro, d=0.010, color=(1.0, 0.25, 0.05), normal='-Y', parent=None, fuerza=4.0):
    return boton(nombre, centro, d, 0.002, normal, L.mat_led(f'LED {color}', color, fuerza), parent)


# ------------------------------------------------------------- rejillas
def rejilla_ranuras(nombre, centro, w, h, normal='-Y', n=None, paso=0.012, ranura=0.006,
                    fondo=0.004, mat=None, parent=None, orient='H'):
    """Rejilla de ventilacion embutida en una cara: lamas a haces con la
    cara (nada sobresale) y una placa oscura detras. `centro` = centro del
    borde superior de la rejilla sobre la cara. orient H: lamas
    horizontales; V: verticales."""
    mat = mat or L.mat_inox()
    oscuro = L.mat_plastico('Interior oscuro', (0.01, 0.01, 0.01), rug=0.9)
    cx, cy, cz = centro
    # direccion hacia dentro del cuerpo
    dx, dy = {'-Y': (0, 1), '+Y': (0, -1), '+X': (-1, 0), '-X': (1, 0)}[normal]
    out = []
    if normal in ('-Y', '+Y'):
        out.append(L.caja(nombre + ' fondo', w, 0.002, h, (cx, cy + dy * (fondo + 0.002), cz - h / 2),
                          mat=oscuro, parent=parent, suave=False))
    else:
        out.append(L.caja(nombre + ' fondo', 0.002, w, h, (cx + dx * (fondo + 0.002), cy, cz - h / 2),
                          mat=oscuro, parent=parent, suave=False))
    cuenta = n or int((h if orient == 'H' else w) / paso)
    for i in range(cuenta):
        off = -(cuenta - 1) / 2 * paso + i * paso
        lw = paso - ranura
        if orient == 'H':
            if normal in ('-Y', '+Y'):
                out.append(L.caja(f'{nombre} lama {i + 1}', w, fondo, lw,
                                  (cx, cy + dy * fondo / 2, cz - h / 2 + off + paso / 2 - lw / 2 - 0.0),
                                  r=0.0008, segs=2, mat=mat, parent=parent))
            else:
                out.append(L.caja(f'{nombre} lama {i + 1}', fondo, w, lw,
                                  (cx + dx * fondo / 2, cy, cz - h / 2 + off + paso / 2 - lw / 2),
                                  r=0.0008, segs=2, mat=mat, parent=parent))
        else:
            if normal in ('-Y', '+Y'):
                out.append(L.caja(f'{nombre} lama {i + 1}', lw, fondo, h,
                                  (cx + off, cy + dy * fondo / 2, cz - h), r=0.0008, segs=2, mat=mat, parent=parent))
            else:
                out.append(L.caja(f'{nombre} lama {i + 1}', fondo, lw, h,
                                  (cx + dx * fondo / 2, cy + off, cz - h), r=0.0008, segs=2, mat=mat, parent=parent))
    return out


def rejilla_agujeros(nombre, centro, w, h, normal='-Y', d=0.004, paso=0.008, mat=None, parent=None):
    """Chapa perforada: placa oscura detras y una malla con agujeros
    (booleana). Para superficies pequenas."""
    mat = mat or L.mat_inox()
    cx, cy, cz = centro
    if normal in ('-Y', '+Y'):
        placa = L.caja(nombre, w, 0.0015, h, (cx, cy, cz - h / 2), mat=mat, parent=parent, suave=False)
    else:
        placa = L.caja(nombre, 0.0015, w, h, (cx, cy, cz - h / 2), mat=mat, parent=parent, suave=False)
    bm = bmesh.new()
    nx, nz = int(w / paso), int(h / paso)
    for i in range(nx):
        for j in range(nz):
            x = -(nx - 1) / 2 * paso + i * paso
            z = -(nz - 1) / 2 * paso + j * paso
            r = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=d / 2, radius2=d / 2, depth=0.01)
            vs = r['verts']
            if normal in ('-Y', '+Y'):
                bmesh.ops.rotate(bm, cent=(0, 0, 0), verts=vs, matrix=L._rot('X', 90))
                bmesh.ops.translate(bm, vec=(cx + x, cy, cz + z), verts=vs)
            else:
                bmesh.ops.rotate(bm, cent=(0, 0, 0), verts=vs, matrix=L._rot('Y', 90))
                bmesh.ops.translate(bm, vec=(cx, cy + x, cz + z), verts=vs)
    me = bpy.data.meshes.new(nombre + ' agujeros')
    bm.to_mesh(me)
    bm.free()
    cort = bpy.data.objects.new(nombre + ' agujeros', me)
    bpy.context.scene.collection.objects.link(cort)
    L.sustraer(placa, cort)
    oscuro = L.mat_plastico('Interior oscuro', (0.01, 0.01, 0.01), rug=0.9)
    if normal in ('-Y', '+Y'):
        fondo = L.caja(nombre + ' fondo', w, 0.002, h, (cx, cy + (0.004 if normal == '-Y' else -0.004), cz - h / 2),
                       mat=oscuro, parent=parent, suave=False)
    else:
        fondo = L.caja(nombre + ' fondo', 0.002, w, h, (cx + (-0.004 if normal == '+X' else 0.004), cy, cz - h / 2),
                       mat=oscuro, parent=parent, suave=False)
    return [placa, fondo]


# ------------------------------------------------------------- cubas y grifos
def cuba(nombre, cuerpo, centro_sup, w, d, prof, r_esq=0.03, r_fondo=0.02,
         mat=None, parent=None, espesor=0.0012, desague=True):
    """Cuba de fregadero: vacia un hueco en `cuerpo` (la encimera) y pone
    dentro la chapa de la cuba con esquinas redondeadas. `centro_sup` =
    centro del hueco en la cara superior (z = cota de la encimera)."""
    mat = mat or L.mat_inox()
    cx, cy, cz = centro_sup
    cort = L.caja(nombre + ' corte', w, d, prof + 0.02, (cx, cy, cz - prof), r_vert=r_esq, r=0.0, segs=6)
    L.sustraer(cuerpo, cort)
    # chapa de la cuba: caja exterior redondeada menos interior
    ext = L.caja(nombre, w, d, prof, (cx, cy, cz - prof), r_vert=r_esq, r=r_fondo, segs=6, mat=mat, parent=parent)
    inte = L.caja(nombre + ' hueco', w - 2 * espesor, d - 2 * espesor, prof, (cx, cy, cz - prof + espesor),
                  r_vert=max(r_esq - espesor, 0.002), r=max(r_fondo - espesor, 0.002), segs=6)
    L.sustraer(ext, inte)
    out = [ext]
    if desague:
        out.append(L.cilindro(nombre + ' desague', 0.045, 0.002, (cx, cy, cz - prof + espesor), segs=48,
                              r=0.001, mat=L.mat_inox_pulido(), parent=parent))
        out.append(L.cilindro(nombre + ' valvula', 0.030, 0.003, (cx, cy, cz - prof + espesor + 0.002), segs=48,
                              r=0.001, mat=L.mat_cromo(), parent=parent))
    return out


def grifo_monomando(nombre, base, alto=0.30, alcance=0.20, d=0.030, mat=None, parent=None):
    """Grifo de fregadero industrial: columna vertical, cano curvado hacia
    -Y (el frente) y maneta. `base` = punto de apoyo en la encimera."""
    mat = mat or L.mat_cromo()
    bx, by, bz = base
    out = [L.cilindro(nombre + ' roseta', d * 0.9, 0.008, (bx, by, bz), r=0.002, segs=48, mat=mat, parent=parent),
           L.cilindro(nombre + ' columna', d / 2, alto - d, (bx, by, bz + 0.008), r=0.0, segs=48, mat=mat, parent=parent)]
    # cano: arco de cuarto de toro + tramo recto descendente
    R = d * 2.2
    perfil_toro = L.toro(nombre + ' codo', R, d * 0.36, (bx, by - R, bz + alto - d), segs=48, segs_r=20, mat=mat, parent=parent)
    # recortar el toro a un cuarto (y <= by, z >= centro)
    cort = L.caja(nombre + ' corte', R * 4, R * 4, R * 4, (bx, by + R, bz + alto - d - 2 * R))
    L.sustraer(perfil_toro, cort)
    cort2 = L.caja(nombre + ' corte2', R * 4, R * 4, R * 2, (bx, by - R, bz + alto - d - 2 * R))
    L.sustraer(perfil_toro, cort2)
    out.append(perfil_toro)
    largo_h = max(alcance - R, 0.02)
    out.append(L.cilindro(nombre + ' cano', d * 0.36, largo_h, (bx, by - R, bz + alto - d + R), eje='Y', segs=40,
                          mat=mat, parent=parent))
    # el cilindro en Y crece hacia +Y desde pos; lo queremos hacia -Y
    out[-1].location = (0, -largo_h, 0)
    out.append(L.cilindro(nombre + ' boca', d * 0.40, 0.035, (bx, by - R - largo_h, bz + alto - d + R - 0.035),
                          segs=40, r=0.002, mat=mat, parent=parent))
    out.append(L.cilindro(nombre + ' aireador', d * 0.30, 0.004, (bx, by - R - largo_h, bz + alto - d + R - 0.039),
                          segs=32, mat=L.mat_plastico('Plastico negro', (0.02, 0.02, 0.02)), parent=parent))
    # maneta: palanca hacia el frente, inclinada
    out.append(L.cilindro(nombre + ' maneta', 0.006, 0.09, (bx, by, bz + alto - d - 0.02), eje='Y', segs=24, r=0.003,
                          mat=mat, parent=parent))
    out[-1].location = (0, -0.09, 0)
    out[-1].rotation_euler = (math.radians(-25), 0, 0)
    return out


# ------------------------------------------------------------- bisagras y varios
def bisagra(nombre, centro, alto=0.060, saliente=0.012, mat=None, parent=None):
    mat = mat or L.mat_inox_pulido()
    cx, cy, cz = centro
    return [L.caja(nombre, 0.014, saliente, alto, (cx, cy - saliente / 2, cz - alto / 2), r=0.003, mat=mat, parent=parent)]


def junta_puerta(nombre, w, h, centro, normal='-Y', ancho=0.012, grosor=0.004, mat=None, parent=None):
    """Burlete/junta de goma perimetral de una puerta (marco plano)."""
    mat = mat or L.mat_goma()
    cx, cy, cz = centro
    if normal in ('-Y', '+Y'):
        marco = L.caja(nombre, w, grosor, h, (cx, cy, cz - h / 2), mat=mat, parent=parent, suave=False)
        cort = L.caja(nombre + ' corte', w - 2 * ancho, grosor * 3, h - 2 * ancho, (cx, cy, cz - h / 2 + ancho))
    else:
        marco = L.caja(nombre, grosor, w, h, (cx, cy, cz - h / 2), mat=mat, parent=parent, suave=False)
        cort = L.caja(nombre + ' corte', grosor * 3, w - 2 * ancho, h - 2 * ancho, (cx, cy, cz - h / 2 + ancho))
    L.sustraer(marco, cort)
    return [marco]


def peto(nombre, w, alto, fondo, pos, r=0.006, mat=None, parent=None):
    """Peto trasero de encimera (chapa vertical con canto superior
    redondeado). `pos` = centro de la base del peto."""
    return L.caja(nombre, w, fondo, alto, pos, r=r, segs=4, mat=mat or L.mat_inox(), parent=parent)


def cable(nombre, inicio, largo=0.25, d=0.008, parent=None):
    """Cable de alimentacion saliendo por la trasera (+Y) y cayendo."""
    mat = L.mat_goma('Cable negro', (0.01, 0.01, 0.012))
    ix, iy, iz = inicio
    out = [L.cilindro(nombre, d / 2, largo * 0.35, (ix, iy, iz), eje='Y', segs=16, mat=mat, parent=parent)]
    out.append(L.cilindro(nombre + ' caida', d / 2, largo * 0.65, (ix, iy + largo * 0.35, iz - largo * 0.65),
                          segs=16, mat=mat, parent=parent))
    return out


def estante_rejilla(nombre, centro, w, d, n_barras=None, paso=0.03, d_barra=0.005, mat=None, parent=None):
    """Parrilla de varillas (estante de nevera / rejilla de plancha):
    varillas longitudinales en Y sobre dos travesanos en X."""
    mat = mat or L.mat_cromo()
    cx, cy, cz = centro
    n = n_barras or int(w / paso)
    out = []
    for i in range(n):
        x = -(n - 1) / 2 * paso + i * paso
        out.append(L.cilindro(f'{nombre} varilla {i + 1}', d_barra / 2, d, (cx + x, cy - d / 2, cz), eje='Y', segs=12,
                              mat=mat, parent=parent))
    for j, y in enumerate((-d / 2 + 0.02, d / 2 - 0.02)):
        out.append(L.cilindro(f'{nombre} travesano {j + 1}', d_barra * 0.7, w, (cx - w / 2, cy + y, cz - d_barra * 0.8),
                              eje='X', segs=12, mat=mat, parent=parent))
    return out
