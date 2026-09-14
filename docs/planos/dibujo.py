# -*- coding: utf-8 -*-
"""
Utilidades de dibujo tecnico: un lienzo SVG en milimetros de papel con
conversion directa desde metros de obra, grosores de linea normalizados,
cotas con trazos a 45 grados y tramas.
"""

TRAZO = {          # grosores en mm de papel
    'corte':      0.50,   # muros y pilares seccionados
    'tabique':    0.35,   # particiones seccionadas
    'medio':      0.25,   # peldanos, barandillas, carpinteria
    'fino':       0.18,   # vidrio, proyecciones
    'cota':       0.13,
    'auxiliar':   0.10,
}

TINTA     = '#111111'
POCHE     = '#6f6f6f'     # muros de carga y medianeras
POCHE_PIL = '#2b2b2b'     # pilares y machones de hormigon
POCHE_TAB = '#a8a8a8'     # tabiqueria
VIDRIO    = '#7fb4c9'
COTA_COL  = '#9a2b2b'


class Lienzo:
    """Lienzo SVG en mm de papel. escala = mm de papel por metro de obra."""

    def __init__(self, ancho_mm, alto_mm, escala, ox, oy):
        self.w, self.h = ancho_mm, alto_mm
        self.e = escala                 # 20 mm/m = 1:50
        self.ox, self.oy = ox, oy       # papel del origen de obra (0,0)
        self.capas = {}
        self.orden = []

    # ---- conversion obra -> papel
    def px(self, x):  return self.ox + x * self.e
    def py(self, y):  return self.oy - y * self.e
    def mm(self, m):  return m * self.e

    # ---- gestion de capas
    def capa(self, nombre):
        if nombre not in self.capas:
            self.capas[nombre] = []
            self.orden.append(nombre)
        return self.capas[nombre]

    def _add(self, capa, s):
        self.capa(capa).append(s)

    # ---- primitivas en coordenadas de OBRA (metros)
    def rect(self, capa, x0, y0, x1, y1, relleno='none', trazo=None, w='corte',
             extra=''):
        X, Y = self.px(min(x0, x1)), self.py(max(y0, y1))
        W, H = abs(x1 - x0) * self.e, abs(y1 - y0) * self.e
        st = f' stroke="{trazo}" stroke-width="{TRAZO[w]}"' if trazo else ' stroke="none"'
        self._add(capa, f'<rect x="{X:.3f}" y="{Y:.3f}" width="{W:.3f}" '
                        f'height="{H:.3f}" fill="{relleno}"{st}{extra}/>')

    def poly(self, capa, pts, relleno='none', trazo=None, w='corte', extra='',
             cerrar=True):
        d = ' '.join(f'{self.px(x):.3f},{self.py(y):.3f}' for x, y in pts)
        tag = 'polygon' if cerrar else 'polyline'
        st = f' stroke="{trazo}" stroke-width="{TRAZO[w]}"' if trazo else ' stroke="none"'
        self._add(capa, f'<{tag} points="{d}" fill="{relleno}"{st}{extra}/>')

    def linea(self, capa, x0, y0, x1, y1, trazo=TINTA, w='medio', extra=''):
        self._add(capa, f'<line x1="{self.px(x0):.3f}" y1="{self.py(y0):.3f}" '
                        f'x2="{self.px(x1):.3f}" y2="{self.py(y1):.3f}" '
                        f'stroke="{trazo}" stroke-width="{TRAZO[w]}"{extra}/>')

    def circulo(self, capa, cx, cy, r_m, relleno='none', trazo=TINTA, w='fino',
                extra=''):
        self._add(capa, f'<circle cx="{self.px(cx):.3f}" cy="{self.py(cy):.3f}" '
                        f'r="{r_m * self.e:.3f}" fill="{relleno}" stroke="{trazo}" '
                        f'stroke-width="{TRAZO[w]}"{extra}/>')

    def texto(self, capa, x, y, txt, alto=2.2, anclaje='middle', color=TINTA,
              peso='normal', rot=0, dx=0, dy=0, extra=''):
        X, Y = self.px(x) + dx, self.py(y) + dy
        r = f' transform="rotate({rot} {X:.3f} {Y:.3f})"' if rot else ''
        self._add(capa, f'<text x="{X:.3f}" y="{Y:.3f}" font-size="{alto}" '
                        f'text-anchor="{anclaje}" fill="{color}" '
                        f'font-family="Liberation Sans, Arial, sans-serif" '
                        f'font-weight="{peso}"{r}{extra}>{txt}</text>')

    # ---- primitivas en coordenadas de PAPEL (mm)
    def p_linea(self, capa, x0, y0, x1, y1, trazo=TINTA, w='cota', extra=''):
        self._add(capa, f'<line x1="{x0:.3f}" y1="{y0:.3f}" x2="{x1:.3f}" '
                        f'y2="{y1:.3f}" stroke="{trazo}" '
                        f'stroke-width="{TRAZO[w]}"{extra}/>')

    def p_rect(self, capa, x0, y0, x1, y1, relleno='none', trazo=None,
               w='medio', extra=''):
        st = f' stroke="{trazo}" stroke-width="{TRAZO[w]}"' if trazo else ' stroke="none"'
        self._add(capa, f'<rect x="{min(x0,x1):.3f}" y="{min(y0,y1):.3f}" '
                        f'width="{abs(x1-x0):.3f}" height="{abs(y1-y0):.3f}" '
                        f'fill="{relleno}"{st}{extra}/>')

    def p_texto(self, capa, x, y, txt, alto=2.5, anclaje='start', color=TINTA,
                peso='normal', rot=0, familia='Liberation Sans, Arial, sans-serif',
                espaciado=None):
        r = f' transform="rotate({rot} {x:.3f} {y:.3f})"' if rot else ''
        ls = f' letter-spacing="{espaciado}"' if espaciado else ''
        self._add(capa, f'<text x="{x:.3f}" y="{y:.3f}" font-size="{alto}" '
                        f'text-anchor="{anclaje}" fill="{color}" '
                        f'font-family="{familia}" font-weight="{peso}"{r}{ls}>{txt}</text>')

    # ---- cotas
    @staticmethod
    def _fmt(v):
        return f'{v:.2f}'.replace('.', ',')

    def cota_h(self, capa, xs, y_papel, alto=2.0, color=COTA_COL, ext_desde=None):
        """Cadena horizontal de cotas. xs en metros, y_papel en mm."""
        xs = sorted(xs)
        self.p_linea(capa, self.px(xs[0]), y_papel, self.px(xs[-1]), y_papel,
                     color, 'cota')
        for x in xs:
            X = self.px(x)
            self.p_linea(capa, X - 1.1, y_papel + 1.1, X + 1.1, y_papel - 1.1,
                         color, 'cota')
            if ext_desde is not None:
                y0 = self.py(ext_desde)
                self.p_linea(capa, X, y0, X, y_papel + (1.6 if y_papel > y0 else -1.6),
                             color, 'auxiliar')
        for a, b in zip(xs, xs[1:]):
            d = b - a
            if d < 0.001:
                continue
            self.p_texto(capa, (self.px(a) + self.px(b)) / 2, y_papel - 1.0,
                         self._fmt(d), alto, 'middle', color)

    def cota_v(self, capa, ys, x_papel, alto=2.0, color=COTA_COL, ext_desde=None):
        """Cadena vertical de cotas. ys en metros, x_papel en mm."""
        ys = sorted(ys)
        self.p_linea(capa, x_papel, self.py(ys[0]), x_papel, self.py(ys[-1]),
                     color, 'cota')
        for y in ys:
            Y = self.py(y)
            self.p_linea(capa, x_papel - 1.1, Y + 1.1, x_papel + 1.1, Y - 1.1,
                         color, 'cota')
            if ext_desde is not None:
                x0 = self.px(ext_desde)
                self.p_linea(capa, x0, Y, x_papel + (1.6 if x_papel > x0 else -1.6),
                             Y, color, 'auxiliar')
        for a, b in zip(ys, ys[1:]):
            d = b - a
            if d < 0.001:
                continue
            Y = (self.py(a) + self.py(b)) / 2
            self.p_texto(capa, x_papel - 1.0, Y, self._fmt(d), alto, 'middle',
                         color, rot=-90)

    def absorber(self, otro, clip=None):
        """Funde las capas de otro lienzo del mismo papel en este.

        `clip` recorta lo absorbido a un rectangulo de papel: es lo que
        permite montar varios detalles a distinta escala en una hoja sin
        que cada uno se salga por encima del de al lado.
        """
        ini = fin = ''
        if clip:
            cid = f'clip{len(self.capas)}_{id(otro) % 10000}'
            x0, y0, x1, y1 = clip
            self.capa('_defs').append(
                f'<clipPath id="{cid}"><rect x="{min(x0,x1):.2f}" '
                f'y="{min(y0,y1):.2f}" width="{abs(x1-x0):.2f}" '
                f'height="{abs(y1-y0):.2f}"/></clipPath>')
            ini, fin = f'<g clip-path="url(#{cid})">', '</g>'
        for n in otro.orden:
            if not otro.capas[n]:
                continue
            capa = self.capa(n)
            if ini:
                capa.append(ini)
            capa.extend(otro.capas[n])
            if fin:
                capa.append(fin)

    # ---- salida
    def svg(self, defs=''):
        if '_defs' in self.capas:
            defs += '\n<defs>' + '\n'.join(self.capas['_defs']) + '</defs>'
            self.orden.remove('_defs')
        cuerpo = '\n'.join(
            f'<g id="{n}">\n' + '\n'.join(self.capas[n]) + '\n</g>'
            for n in self.orden)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{self.w}mm" height="{self.h}mm" '
                f'viewBox="0 0 {self.w} {self.h}">\n'
                f'<rect width="{self.w}" height="{self.h}" fill="white"/>\n'
                f'{defs}\n{cuerpo}\n</svg>')
