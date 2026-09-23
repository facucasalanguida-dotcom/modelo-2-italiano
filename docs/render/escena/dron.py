"""El vuelo de dron por Casa Margot: la trayectoria, sin Blender.

Una sola toma, tranquila: desde lo alto de la calle baja hasta la puerta,
entra, cruza el comedor por encima de la fila del ventanal, se acerca a la
barra y a la pizarra, se mete por el paso de servicio en la cocina, da la
vuelta dentro, sale al comedor, recorre el pasillo del sillon corrido, baja
entre el pilar P3 y la escalera, mira el botellero y sube por la doble altura
por encima del antepecho a la planta alta. Alli pasa entre la mesa de cowork
y el pilar, mira la mesa redonda y acaba asomado sobre el vacio, con el
comedor y el ventanal debajo.

Los baños, el aseo y el almacen tienen la puerta cerrada: el dron pasa por
delante. La puerta de la calle se abre solo en el video (video_blender.py).

Lo importan video.py, con el Python del sistema, para saber cuantos
fotogramas hay, y video_blender.py, dentro de Blender, para poner la camara.

Cada punto de paso:
    p:    donde esta el dron (x, y, z), en metros, coordenadas del local
    m:    a donde mira
    v:    velocidad al pasar por el, en m/s (entre puntos se suaviza)
    exp:  exposicion de la camara; None es la de dentro (0,65). Fuera -1,30,
          como en las fotos, y al cruzar la puerta se abre poco a poco, como
          hace una camara de verdad.
"""
import math

Z_PA = 2.560                  # suelo de la planta alta
LENTE = 20.0                  # mm con sensor de 36: el gran angular de un dron
EXP_DENTRO = 0.65
ARRANQUE = 1.5                # s quieto al principio y al final

PUNTOS = [
    # ---- la calle: de lo alto de la acera de enfrente hasta la puerta
    dict(p=(5.20, -10.20, 4.00), m=(6.60, 1.00, 2.20), v=1.00, exp=-1.30),
    dict(p=(6.30, -6.80, 3.20), m=(7.60, 1.00, 1.90), v=1.00, exp=-1.30),
    dict(p=(7.35, -3.40, 2.20), m=(8.20, 1.20, 1.60), v=0.80, exp=-1.30),
    dict(p=(8.25, -1.10, 1.60), m=(8.35, 2.00, 1.45), v=0.60, exp=-1.30),
    # ---- el cubo de la entrada y la puerta, abierta. Por x = 8,35: la hoja
    #      izquierda abierta llega a 7,87 con su tirador, y la lampara del cubo
    #      cuelga en 8,73..9,07, 20 cm por encima del dron
    dict(p=(8.35, 0.25, 1.50), m=(8.30, 3.00, 1.45), v=0.50, exp=-1.30),
    dict(p=(8.30, 1.40, 1.50), m=(7.20, 3.50, 1.45), v=0.45, exp=-0.30),
    # ---- el comedor, por encima de la fila del ventanal, hacia la barra
    dict(p=(7.70, 2.55, 1.65), m=(4.50, 3.40, 1.30), v=0.45, exp=None),
    dict(p=(6.40, 2.30, 1.95), m=(3.20, 2.90, 1.35), v=0.50, exp=None),
    dict(p=(4.60, 2.25, 2.00), m=(1.60, 3.30, 1.50), v=0.50, exp=None),
    dict(p=(3.15, 2.75, 1.85), m=(0.25, 3.50, 2.55), v=0.45, exp=None),
    # ---- la trasbarra y el paso de servicio
    dict(p=(3.05, 3.75, 1.60), m=(1.00, 4.40, 1.25), v=0.40, exp=None),
    dict(p=(2.95, 4.85, 1.70), m=(0.90, 5.05, 1.40), v=0.35, exp=None),
    dict(p=(1.95, 5.05, 1.70), m=(1.35, 8.20, 1.25), v=0.30, exp=None),
    # ---- la cocina: entra, mira la linea de coccion y da la vuelta
    dict(p=(1.50, 5.75, 1.55), m=(1.30, 8.80, 1.20), v=0.30, exp=None),
    dict(p=(1.55, 7.05, 1.60), m=(1.30, 9.00, 1.30), v=0.20, exp=None),
    dict(p=(1.80, 7.30, 1.60), m=(3.40, 7.60, 1.30), v=0.15, exp=None),
    dict(p=(2.00, 6.60, 1.60), m=(2.00, 4.00, 1.30), v=0.15, exp=None),
    dict(p=(1.60, 5.75, 1.68), m=(2.80, 4.90, 1.40), v=0.25, exp=None),
    # ---- de vuelta al comedor y por el pasillo del sillon corrido. Por el
    #      paso a 1,70: a 1,55 el murete de la L (1,22) llenaba el tercio de
    #      abajo de la imagen; el techo esta a 2,31
    dict(p=(2.20, 5.08, 1.72), m=(4.00, 5.60, 1.30), v=0.30, exp=None),
    dict(p=(3.15, 5.20, 1.62), m=(3.60, 8.50, 1.00), v=0.40, exp=None),
    dict(p=(3.15, 6.75, 1.50), m=(5.50, 8.60, 0.90), v=0.45, exp=None),
    dict(p=(4.90, 6.85, 1.50), m=(6.60, 8.70, 0.85), v=0.45, exp=None),
    # ---- entre el pilar P3 y la escalera, mirando hacia la entrada: el
    #      costado de la escalera es un panel liso, y lo que se ve es su
    #      arranque con los peldaños iluminados y la pared del logo
    dict(p=(7.30, 6.95, 1.50), m=(7.40, 2.00, 1.40), v=0.45, exp=None),
    dict(p=(7.90, 5.90, 1.50), m=(8.60, 2.20, 1.50), v=0.45, exp=None),
    # ---- y el botellero de frente, sin pasar pegado a su costado
    dict(p=(7.75, 4.45, 1.55), m=(5.00, 2.60, 1.20), v=0.40, exp=None),
    dict(p=(6.90, 3.35, 1.75), m=(6.00, 4.30, 1.00), v=0.35, exp=None),
    # ---- sube por la doble altura y pasa por encima del antepecho
    dict(p=(6.10, 2.95, 2.40), m=(5.60, 5.00, 3.40), v=0.35, exp=None),
    dict(p=(5.20, 3.30, Z_PA + 1.59), m=(4.90, 6.80, Z_PA + 1.04), v=0.35, exp=None),
    dict(p=(5.12, 4.50, Z_PA + 1.59), m=(3.00, 5.60, Z_PA + 0.74), v=0.40, exp=None),
    # del cowork a la mesa redonda girando por el lado del vacio, asomado al
    # comedor, y no por el de la pared del aseo
    dict(p=(5.11, 5.40, Z_PA + 1.59), m=(5.50, 2.00, 1.20), v=0.40, exp=None),
    # sigue mirando al vacio hasta dejar atras el pilar: girando a su lado,
    # a medio metro, lo llenaba todo
    dict(p=(5.18, 6.25, Z_PA + 1.59), m=(5.25, 2.00, 1.20), v=0.40, exp=None),
    # ---- la planta alta: el cowork a un lado, la mesa redonda al otro. Por
    #      x = 5,10, entre las sillas del cowork (4,82, y 0,7 m por debajo) y
    #      el pilar P3 (5,62); la mesa redonda se mira desde el Norte del
    #      pilar, que desde mas cerca llenaba la imagen
    dict(p=(5.30, 6.85, Z_PA + 1.59), m=(7.50, 5.40, Z_PA + 0.74), v=0.40, exp=None),
    dict(p=(4.90, 7.00, Z_PA + 1.59), m=(3.00, 5.00, Z_PA + 0.64), v=0.35, exp=None),
    # ---- y el final, asomado sobre el vacio
    dict(p=(3.40, 7.00, Z_PA + 1.64), m=(5.60, 2.20, 2.20), v=0.30, exp=None),
    dict(p=(3.30, 6.95, Z_PA + 1.89), m=(5.80, 2.00, 1.60), v=0.20, exp=None),
]


# ------------------------------------------------------------ la curva
def _catmull(p0, p1, p2, p3, t):
    """Catmull-Rom centripeta entre p1 y p2 (sin lazos ni sobrepasos)."""
    def d(a, b):
        return max(1e-4, math.dist(a, b) ** 0.5)
    t0, t1 = 0.0, d(p0, p1)
    t2 = t1 + d(p1, p2)
    t3 = t2 + d(p2, p3)
    u = t1 + (t2 - t1) * t

    def lerp(a, b, ta, tb):
        k = (u - ta) / (tb - ta)
        return tuple(x + (y - x) * k for x, y in zip(a, b))
    a1, a2, a3 = lerp(p0, p1, t0, t1), lerp(p1, p2, t1, t2), lerp(p2, p3, t2, t3)
    b1, b2 = lerp(a1, a2, t0, t2), lerp(a2, a3, t1, t3)
    return lerp(b1, b2, t1, t2)


def _en(puntos, u):
    """Punto de la curva que pasa por puntos, en el parametro u (0..n-1)."""
    n = len(puntos)
    i = min(int(u), n - 2)
    t = u - i
    p0 = puntos[max(i - 1, 0)]
    p3 = puntos[min(i + 2, n - 1)]
    if i == 0:                               # extremos: punto fantasma simetrico
        p0 = tuple(2 * a - b for a, b in zip(puntos[0], puntos[1]))
    if i + 2 > n - 1:
        p3 = tuple(2 * a - b for a, b in zip(puntos[-1], puntos[-2]))
    return _catmull(p0, puntos[i], puntos[i + 1], p3, t)


def _suave(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _angulos():
    """Rumbo y cabeceo de la mirada en cada punto, sin saltos de 360 grados.

    La camara no se interpola por el punto al que mira sino por el angulo:
    si el punto mirado cruzaba cerca del dron, la mirada daba un latigazo.
    Cada rumbo se toma por el lado corto respecto del anterior.
    """
    rumbos, cabeceos = [], []
    for q in PUNTOS:
        d = [b - a for a, b in zip(q['p'], q['m'])]
        r = math.atan2(d[1], d[0])
        if rumbos:
            while r - rumbos[-1] > math.pi:
                r -= 2 * math.pi
            while r - rumbos[-1] < -math.pi:
                r += 2 * math.pi
        rumbos.append(r)
        cabeceos.append(math.atan2(d[2], math.hypot(d[0], d[1])))
    return rumbos, cabeceos


_RC = None


def direccion(u):
    """Vector unitario de la mirada en el parametro u."""
    global _RC
    if _RC is None:
        _RC = _angulos()
    r = _en([(x,) for x in _RC[0]], u)[0]
    c = _en([(x,) for x in _RC[1]], u)[0]
    return (math.cos(c) * math.cos(r), math.cos(c) * math.sin(r), math.sin(c))


def _tabla(paso=0.01):
    """(u, s): la curva muestreada cada ~1 cm con su longitud acumulada."""
    P = [q['p'] for q in PUNTOS]
    n = len(P)
    us, ss = [0.0], [0.0]
    ant = P[0]
    for i in range(n - 1):
        k = max(8, int(math.dist(P[i], P[i + 1]) / paso))
        for j in range(1, k + 1):
            u = i + j / k
            q = _en(P, u)
            ss.append(ss[-1] + math.dist(ant, q))
            us.append(u)
            ant = q
    return us, ss


def _velocidad(u):
    """Velocidad de crucero en u: la de cada punto, fundida con la siguiente."""
    i = min(int(u), len(PUNTOS) - 2)
    t = _suave(u - i)
    return PUNTOS[i]['v'] + (PUNTOS[i + 1]['v'] - PUNTOS[i]['v']) * t


def _exposicion(u):
    def e(q):
        return EXP_DENTRO if q['exp'] is None else q['exp']
    i = min(int(u), len(PUNTOS) - 2)
    t = _suave(u - i)
    return e(PUNTOS[i]) + (e(PUNTOS[i + 1]) - e(PUNTOS[i])) * t


GIRO_MAX = math.radians(20.0)   # rad/s: lo mas rapido que gira la camara
ACEL_MAX = 0.12                 # m/s2: arranca y frena como un dron con calma


def _tiempos():
    """Tiempo en cada muestra de la curva.

    La velocidad es la de crucero de cada tramo, pero nunca tanta que la
    mirada gire mas de GIRO_MAX, y con la aceleracion limitada a ACEL_MAX en
    las dos direcciones: parte de parado, frena antes de cada giro y acaba
    parado. Asi el ritmo sale solo de la curva y no hay tirones.
    """
    us, ss = _tabla()
    n = len(ss)
    dirs = [direccion(u) for u in us]
    lim = []
    for k in range(n):
        a, b = max(k - 1, 0), min(k + 1, n - 1)
        ds = max(1e-6, ss[b] - ss[a])
        c = sum(x * y for x, y in zip(dirs[a], dirs[b]))
        dth = math.acos(max(-1.0, min(1.0, c)))
        lim.append(min(_velocidad(us[k]), GIRO_MAX * ds / max(dth, 1e-9)))
    v = lim[:]
    v[0] = 0.0
    for k in range(1, n):                    # acelerando hacia delante
        v[k] = min(v[k], math.sqrt(v[k - 1] ** 2 + 2 * ACEL_MAX * (ss[k] - ss[k - 1])))
    v[-1] = 0.0
    for k in range(n - 2, -1, -1):           # y frenando hacia atras
        v[k] = min(v[k], math.sqrt(v[k + 1] ** 2 + 2 * ACEL_MAX * (ss[k + 1] - ss[k])))
    ts = [0.0]
    for k in range(1, n):
        ts.append(ts[-1] + 2 * (ss[k] - ss[k - 1]) / max(1e-4, v[k] + v[k - 1]))
    return us, ss, ts


def fotogramas(fps=60):
    """La camara en cada fotograma: [(ojo, direccion, exposicion)].

    Quieto ARRANQUE segundos al principio y al final; entre medias, el ritmo
    de _tiempos().
    """
    us, ss, ts = _tiempos()
    T = ts[-1]
    total = int(math.ceil((T + 2 * ARRANQUE) * fps)) + 1
    P = [q['p'] for q in PUNTOS]
    out, k = [], 0
    for n in range(total):
        t = min(max(n / fps - ARRANQUE, 0.0), T)
        while k < len(ts) - 2 and ts[k + 1] < t:
            k += 1
        a = (t - ts[k]) / max(1e-9, ts[k + 1] - ts[k])
        u = us[k] + (us[k + 1] - us[k]) * min(1.0, max(0.0, a))
        out.append((_en(P, u), direccion(u), _exposicion(u)))
    return out


def resumen(fps=60):
    us, ss, ts = _tiempos()
    n = int(math.ceil((ts[-1] + 2 * ARRANQUE) * fps)) + 1
    return {'metros': round(ss[-1], 1), 'fotogramas': n, 'segundos': round(n / fps, 1)}


if __name__ == '__main__':
    print(resumen())
