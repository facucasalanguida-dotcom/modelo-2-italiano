"""Trayectoria del dron por la planta baja + comprobacion de colisiones."""
import json, math, os

SP = '/tmp/claude-0/-home-user-modelo-2-italiano/30d2763c-3169-519a-ac78-c5a47134634b/scratchpad'

# Estaciones del vuelo: (x, y, z de camara) -> (x, y, z del punto mirado)
# Recorre: entrada -> ventanal -> sala -> cocina -> barra -> escalera -> vista alta
ESTACIONES = [
    ((8.30, 1.30, 2.25), (3.50, 4.50, 1.40)),   # 1  entrada, en la doble altura
    ((6.30, 2.00, 1.90), (3.20, 3.20, 1.30)),   # 2  baja y avanza junto al ventanal
    ((4.40, 2.30, 1.75), (2.50, 4.00, 1.10)),   # 3  encara la barra
    ((3.60, 3.60, 1.70), (2.40, 5.50, 1.05)),   # 4  recorre el frente de barra
    ((3.45, 5.60, 1.70), (2.20, 7.60, 1.20)),   # 5  pasa el extremo norte de la barra
    ((2.70, 6.70, 1.65), (1.70, 8.20, 1.30)),   # 6  se asoma a la cocina
    ((4.50, 6.95, 1.80), (7.00, 6.00, 1.20)),   # 7  gira al este por el fondo
    ((7.25, 5.85, 1.72), (8.60, 4.30, 1.40)),   # 8  rodea el pilar por el norte
    ((7.55, 4.60, 1.70), (8.20, 3.40, 1.35)),   # 9  libra el arbol por el oeste
    ((7.90, 3.05, 1.80), (5.50, 3.00, 1.30)),   # 10 baja bajo los colgantes
    ((7.60, 2.40, 2.90), (4.20, 4.00, 1.30)),   # 11 entra en el vacio y sube
    ((7.20, 1.95, 4.10), (3.00, 4.60, 1.10)),   # 12 plano final alto y abierto
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
