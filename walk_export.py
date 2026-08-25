# Exporta la escena del Café Napoli a un formato binario compacto para el
# recorrido virtual en tiempo real (three.js). Fusiona la geometría por
# material, genera UVs por proyección de caja y cuantiza los atributos.
import os, json, struct
os.environ['NAPOLI_NO_RENDER'] = '1'
os.environ['NAPOLI_LOW'] = '1'
import numpy as np

exec(open('/home/user/modelo-2-italiano/blender_scene.py').read())

import bpy
from collections import defaultdict

OUT_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'walk.bin') \
    if '__file__' in globals() else 'walk.bin'
OUT_BIN = os.environ.get('WALK_OUT', 'walk.bin')

# ---------------------------------------------------------------- materiales
def mat_spec(m):
    sp = dict(color=(0.75, 0.73, 0.70), rough=0.6, metal=0.0, alpha=1.0,
              emit=None, tex=None, tile=1.0, uvmode='box')
    if m is None or not m.use_nodes or m.node_tree is None:
        return sp
    nt = m.node_tree
    pr = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if pr is None:                       # vidrio arquitectonico (transparente)
        sp.update(color=(0.86, 0.92, 0.95), alpha=0.07, rough=0.05)
        return sp
    bc = pr.inputs['Base Color']
    col = tuple(bc.default_value)[:3]
    if bc.is_linked:
        fn = bc.links[0].from_node
        if fn.type == 'TEX_IMAGE':
            sp['tex'] = fn.image.name.rsplit('.png', 1)[0]
            col = (1, 1, 1)
        elif fn.type == 'MIX' and getattr(fn, 'blend_type', '') == 'MULTIPLY':
            src = fn.inputs[6]
            if src.is_linked and src.links[0].from_node.type == 'TEX_IMAGE':
                sp['tex'] = src.links[0].from_node.image.name.rsplit('.png', 1)[0]
            col = tuple(fn.inputs[7].default_value)[:3]
        elif fn.type == 'VALTORGB':
            e = fn.color_ramp.elements
            col = tuple((e[0].color[i] + e[1].color[i]) / 2 for i in range(3))
        elif fn.type == 'MIX':
            col = tuple(fn.inputs[6].default_value)[:3]
    sp['color'] = col
    r = pr.inputs['Roughness']
    sp['rough'] = 0.55 if r.is_linked else float(r.default_value)
    sp['metal'] = float(pr.inputs['Metallic'].default_value)
    tw = pr.inputs.get('Transmission Weight')
    if tw is not None and tw.default_value > 0.5:
        sp['alpha'] = 0.22
        sp['rough'] = min(sp['rough'], 0.1)
    es = pr.inputs.get('Emission Strength')
    if es is not None and es.default_value > 0.05:
        ec = tuple(pr.inputs['Emission Color'].default_value)[:3]
        sp['emit'] = [round(ec[0], 3), round(ec[1], 3), round(ec[2], 3),
                      round(float(es.default_value), 2)]
    mpn = next((n for n in nt.nodes if n.type == 'MAPPING'), None)
    if mpn is not None:
        sx = mpn.inputs['Scale'].default_value[0]
        if sx:
            sp['tile'] = round(1.0 / sx, 4)
    tcn = next((n for n in nt.nodes if n.type == 'TEX_COORD'), None)
    if tcn is not None and any(
            l.from_node == tcn and l.from_socket.name == 'Generated'
            for l in nt.links):
        sp['uvmode'] = 'bbox'
    return sp

# ---------------------------------------------------------------- geometria
deps = bpy.context.evaluated_depsgraph_get()
rows_by_mat = defaultdict(list)
specs = {}

def box_uv(P, tn, tile):
    # proyeccion de caja: por triangulo, el eje dominante de la normal decide
    ax = np.abs(tn).argmax(axis=1)             # (ntri,)
    ax3 = np.repeat(ax, 3)
    u = np.where(ax3 == 0, P[:, 1], P[:, 0])
    v = np.where(ax3 == 2, P[:, 1], P[:, 2])
    return np.stack([u, v], axis=1) / tile

n_obj = 0
for ob in bpy.data.objects:
    if ob.type not in ('MESH', 'FONT', 'CURVE'):
        continue
    ev = ob.evaluated_get(deps)
    try:
        me = ev.to_mesh()
    except Exception:
        continue
    if me is None or len(me.polygons) == 0:
        ev.to_mesh_clear(); continue
    mat = me.materials[0] if me.materials else (
        ob.material_slots[0].material if ob.material_slots else None)
    mname = mat.name if mat else '_none'
    if mname not in specs:
        specs[mname] = mat_spec(mat)
    sp = specs[mname]

    me.calc_loop_triangles()
    nl = len(me.loops); nv = len(me.vertices); nt_ = len(me.loop_triangles)
    if nt_ == 0:
        ev.to_mesh_clear(); continue
    pos = np.empty(nv * 3, 'f4'); me.vertices.foreach_get('co', pos)
    pos = pos.reshape(-1, 3)
    M = np.array(ob.matrix_world, 'f8')
    R = M[:3, :3]
    lvi = np.empty(nl, 'i4'); me.loops.foreach_get('vertex_index', lvi)
    try:
        lnr = np.empty(nl * 3, 'f4')
        me.corner_normals.foreach_get('vector', lnr)
        lnr = lnr.reshape(-1, 3)
    except Exception:
        vn = np.empty(nv * 3, 'f4')
        me.vertex_normals.foreach_get('vector', vn)
        lnr = vn.reshape(-1, 3)[lvi]
    tri = np.empty(nt_ * 3, 'i4'); me.loop_triangles.foreach_get('loops', tri)
    tnl = np.empty(nt_ * 3, 'f4'); me.loop_triangles.foreach_get('normal', tnl)
    tn_local = tnl.reshape(-1, 3)

    li = tri                                   # indices de loop por esquina
    P_local = pos[lvi[li]]
    N_local = lnr[li]
    if sp['tex'] is not None and sp['uvmode'] == 'bbox':
        bmin = P_local.min(axis=0); bsize = np.maximum(P_local.max(axis=0) - bmin, 1e-6)
        Pn = (P_local - bmin) / bsize
        uv = box_uv(Pn, tn_local, 1.0)
    else:
        Pw_all = pos @ R.T + M[:3, 3]
        tn_world = tn_local @ np.linalg.inv(R).T if abs(np.linalg.det(R)) > 1e-9 else tn_local
        uv = box_uv(Pw_all[lvi[li]], tn_world, sp['tile'] if sp['tex'] else 1.0)
    Pw = P_local @ R.T + M[:3, 3]
    Nw = N_local @ np.linalg.inv(R).T if abs(np.linalg.det(R)) > 1e-9 else N_local
    nrm = Nw / np.maximum(np.linalg.norm(Nw, axis=1, keepdims=True), 1e-9)
    rows_by_mat[mname].append((Pw.astype('f4'), nrm.astype('f4'), uv.astype('f4')))
    n_obj += 1
    ev.to_mesh_clear()

print('objetos exportados:', n_obj, '· materiales:', len(rows_by_mat))

# ------------------------------------------------- cuantizacion y dedupe
mats_meta = []
buffers = []
for mname, chunks in rows_by_mat.items():
    P = np.concatenate([c[0] for c in chunks])
    N = np.concatenate([c[1] for c in chunks])
    UV = np.concatenate([c[2] for c in chunks])
    pmin = P.min(axis=0); psize = np.maximum(P.max(axis=0) - pmin, 1e-6)
    uvmin = UV.min(axis=0); uvsize = np.maximum(UV.max(axis=0) - uvmin, 1e-6)
    qp = np.round((P - pmin) / psize * 65535).astype('u2')
    qn = np.clip(np.round(N * 127), -127, 127).astype('i1')
    qu = np.round((UV - uvmin) / uvsize * 65535).astype('u2')
    rec = np.concatenate([qp.view('u1').reshape(len(P), -1),
                          qn.view('u1').reshape(len(P), -1),
                          qu.view('u1').reshape(len(P), -1)], axis=1)
    recv = np.ascontiguousarray(rec).view([('b', 'u1', rec.shape[1])]).ravel()
    uniq, inv = np.unique(recv, return_inverse=True)
    urec = uniq['b'].reshape(len(uniq), -1)
    vpos = urec[:, 0:6].copy().view('u2').reshape(-1, 3)
    vnrm = urec[:, 6:9].copy().view('i1').reshape(-1, 3)
    vuv = urec[:, 9:13].copy().view('u2').reshape(-1, 2)
    idx = inv.astype('u4')
    mats_meta.append(dict(
        name=mname, spec=specs[mname], nv=int(len(uniq)), ni=int(len(idx)),
        pmin=[round(float(v), 4) for v in pmin],
        psize=[round(float(v), 4) for v in psize],
        uvmin=[round(float(v), 4) for v in uvmin],
        uvsize=[round(float(v), 4) for v in uvsize]))
    buffers.append((np.ascontiguousarray(vpos), np.ascontiguousarray(vnrm),
                    np.ascontiguousarray(vuv), idx))

# ---------------------------------------------------------------- colisiones
def bb(s):
    xs = [p[0] for p in s['poly']]; ys = [p[1] for p in s['poly']]
    zs = [p[2] for p in s['poly']]
    n, d = s['n'], s['d']
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    z0, z1 = min(zs), max(zs)
    return (min(x0, x0 + n[0]*d), min(y0, y0 + n[1]*d), min(z0, z0 + n[2]*d),
            max(x1, x1 + n[0]*d), max(y1, y1 + n[1]*d), max(z1, z1 + n[2]*d))

cols = []
for s in S:
    if is_pa(s):
        continue
    nm = s['name'] or ''
    if nm.startswith(('Escalera', 'Toldo', 'Cuadro', 'Carta', 'LED',
                      'Pavimento', 'Empotrado', 'Lampara', 'Cable', 'Aro',
                      'Pantalla', 'Foco', 'Aplique')):
        continue
    x0, y0, z0, x1, y1, z1 = bb(s)
    if z0 > 1.35 or z1 < 0.55:
        continue
    if max(x1 - x0, y1 - y0) < 0.15:
        continue
    cols.append([round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3)])

# mobiliario parametrico
for mx, my in MESAS_R:
    cols.append([mx - 0.32, my - 0.32, mx + 0.32, my + 0.32])
    if (mx, my) == (9.00, 2.75):
        for dy in (-0.63, 0.63):
            cols.append([mx - 0.28, my + dy - 0.28, mx + 0.28, my + dy + 0.28])
    else:
        for dx in (-0.63, 0.63):
            cols.append([mx + dx - 0.28, my - 0.28, mx + dx + 0.28, my + 0.28])
for tx in (6.55, 7.15, 7.75):
    cols.append([tx - 0.2, 6.12 - 0.2, tx + 0.2, 6.12 + 0.2])
cols.append([2.69, 8.21, 3.21, 8.83])          # carro bandejero
cols.append([8.28, 3.85, 9.80, 7.95])          # escalera: planta alta cerrada
for tx in (5.85, 10.15):                       # terraza
    cols.append([tx - 0.95, -2.25, tx + 0.95, -0.35])

meta = dict(
    mats=mats_meta,
    lights=[[round(c[0], 3), round(c[1], 3), round(c[2], 3), round(c[3], 3)]
            for c in lamparas],
    cols=cols,
    spawn=[7.95, 1.05, 118.0],                  # x, y, rumbo en grados
    bounds=[0.42, 0.50, 9.52, 8.82])

blob = bytearray()
js = json.dumps(meta, separators=(',', ':')).encode()
blob += b'NAP1' + struct.pack('<I', len(js)) + js
while len(blob) % 4:
    blob += b'\0'
offs = []
for vpos, vnrm, vuv, idx in buffers:
    o = {}
    for key, arr in (('p', vpos), ('n', vnrm), ('u', vuv), ('i', idx)):
        while len(blob) % 4:
            blob += b'\0'
        o[key] = len(blob)
        blob += arr.tobytes()
    offs.append(o)
with open(OUT_BIN, 'wb') as f:
    f.write(bytes(blob))
with open(OUT_BIN + '.offsets.json', 'w') as f:
    json.dump(offs, f)
print('walk.bin:', len(blob) // 1024, 'KB · grupos:', len(buffers))
tot_v = sum(m['nv'] for m in mats_meta); tot_i = sum(m['ni'] for m in mats_meta)
print('vertices:', tot_v, '· triangulos:', tot_i // 3)
print('EXPORT DONE')
