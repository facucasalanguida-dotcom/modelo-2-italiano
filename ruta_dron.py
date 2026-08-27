"""Trayectoria del dron por la planta baja + comprobacion de colisiones."""
import json, math, os

SP = os.path.dirname(os.path.abspath(__file__))

# Estaciones del vuelo: (x, y, z de camara) -> (x, y, z del punto mirado)
# Recorre: entrada -> ventanal -> sala -> cocina -> barra -> escalera -> vista alta
ESTACIONES = [
    ((8.30, 1.30, 2.25), (4.60, 3.30, 1.40)),   # 1  entrada, en el vacio de doble altura
    ((6.35, 1.96, 1.94), (3.20, 3.10, 1.30)),   # 2  baja entre el cristal y el arbol
    ((4.80, 2.35, 1.72), (1.90, 4.30, 1.30)),   # 3  ventanal, gira al oeste
    ((3.05, 3.30, 1.68), (2.10, 6.30, 1.35)),   # 4  entra en la sala hacia el norte
    ((2.48, 5.35, 1.54), (1.70, 7.90, 1.45)),   # 5  mampara, cocina al fondo
    ((3.20, 6.15, 1.75), (5.80, 6.85, 1.10)),   # 6  gira al este, frente de barra
    ((4.90, 6.10, 1.82), (7.20, 6.75, 1.15)),   # 7  sobrevuela la barra
    ((6.20, 6.30, 1.95), (7.90, 5.40, 1.30)),   # 8  rodea el pilar por el norte
    ((7.75, 4.95, 2.00), (6.10, 3.70, 1.35)),   # 9  pasa alto sobre el arbol
    ((7.68, 3.45, 2.05), (5.20, 3.90, 1.40)),   # 10 cruza bajo el canto del altillo
    ((7.50, 2.55, 3.10), (4.60, 4.30, 1.35)),   # 11 ya en el vacio, empieza a subir
    ((7.20, 2.00, 4.10), (3.20, 4.60, 1.20)),   # 12 plano final alto y abierto
]


def catmull(ps, t):
    """Catmull-Rom sobre una lista de puntos 3D, t en [0,1]."""
    n = len(ps) - 1
    x = max(0.0, min(0.999999, t)) * n
    i = int(x)
    f = x - i
    p0 = ps[max(i - 1, 0)]
    p1 = ps[i]
    p2 = ps[min(i + 1, n)]
    p3 = ps[min(i + 2, n)]
    out = []
    for k in range(3):
        a, b, c, d = p0[k], p1[k], p2[k], p3[k]
        out.append(0.5 * ((2 * b) + (-a + c) * f +
                          (2 * a - 5 * b + 4 * c - d) * f * f +
                          (-a + 3 * b - 3 * c + d) * f * f * f))
    return tuple(out)


def suave(t):
    """Arranque y frenada suaves (smoothstep)."""
    return t * t * (3 - 2 * t)


POS = [e[0] for e in ESTACIONES]
MIRA = [e[1] for e in ESTACIONES]


def camara(t):
    """Devuelve (posicion, objetivo) para t en [0,1]."""
    u = suave(t)
    return catmull(POS, u), catmull(MIRA, u)


def cajas():
    """AABB de cada solido del modelo (poligono extruido por su normal)."""
    out = []
    for s in json.load(open(os.path.join(SP, 'solids.json'))):
        if s.get('tag') == '27 Iluminacion':
            continue
        poly = json.loads(s['poly']) if isinstance(s['poly'], str) else s['poly']
        nrm = json.loads(s['n']) if isinstance(s['n'], str) else s['n']
        d = s['d']
        pts = [p for p in poly] + [[p[k] + nrm[k] * d for k in range(3)] for p in poly]
        mn = [min(p[k] for p in pts) for k in range(3)]
        mx = [max(p[k] for p in pts) for k in range(3)]
        out.append((mn, mx, s['name']))
    return out


if __name__ == '__main__':
    import sys
    CLARO = float(sys.argv[1]) if len(sys.argv) > 1 else 0.35          # holgura minima alrededor de la camara, en metros
    N = 240
    cjs = cajas()
    choques = {}
    for i in range(N + 1):
        p, _ = camara(i / N)
        for mn, mx, nom in cjs:
            if all(mn[k] - CLARO <= p[k] <= mx[k] + CLARO for k in range(3)):
                choques.setdefault(nom, []).append(round(i / N, 3))
    if choques:
        print('COLISIONES:')
        for nom, ts in sorted(choques.items(), key=lambda x: -len(x[1]))[:12]:
            print(f'  {nom:42s} t={ts[0]}..{ts[-1]}  ({len(ts)} muestras)')
    else:
        print('RUTA LIMPIA: sin colisiones en', N + 1, 'muestras')
    malos = []
    for i in range(N + 1):
        p, _ = camara(i / N)
        if p[1] > 3.85 and p[2] > 2.35:
            malos.append((round(i / N, 3), round(p[1], 2), round(p[2], 2)))
    print('BAJO FORJADO demasiado alto:', malos[:6] if malos else 'ninguno')
    zs = [camara(i / N)[0][2] for i in range(N + 1)]
    print(f'altura camara: {min(zs):.2f} .. {max(zs):.2f} m')
