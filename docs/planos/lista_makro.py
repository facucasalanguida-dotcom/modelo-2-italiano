# -*- coding: utf-8 -*-
"""
Genera LISTA_MAKRO.md: la lista de compra del equipamiento con el enlace a
cada ficha de makro.es, sus medidas y donde va cada cosa en el plano.

    python3 lista_makro.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import equipamiento as Q

AQUI = os.path.dirname(os.path.abspath(__file__))

UBICACION = {
    'K1': 'Cocina · línea de cocción, medianera Norte, bajo la campana (1º desde el Oeste)',
    'K2': 'Cocina · línea de cocción, bajo la campana (2º)',
    'K3': 'Cocina · línea de cocción, bajo la campana (3º)',
    'K4': 'Cocina · línea de cocción, bajo la campana (4º, contra la pared en L)',
    'KC': 'Cocina · campana mural corrida sobre K1 a K4, borde inferior a +2,00',
    'K5': 'Cocina · muro Oeste, esquina Norte, sobre soporte',
    'K6': 'Cocina · muro Oeste, bajo la tabla que enlaza fregadero y horno',
    'K7': 'Cocina · muro Oeste, al Sur de la tabla (baja a 0,60 para que entren los dos frigoríficos inox)',
    'K8': 'Cocina · muro Oeste, vertical, al Sur del fregadero',
    'K9': 'Cocina · muro Oeste, vertical, contra P1',
    'K10': 'Cocina · pared en L, de una sola pieza (2,54) usada como mesada; 0,42 libres junto al doblez',
    'A1': 'Barra · trasbarra, extremo Norte, sobre el módulo técnico T1',
    'A2': 'Barra · trasbarra, al Sur de la cafetera',
    'A3': 'Barra · trasbarra, bajo la encimera, al Sur del lavamanos',
    'A3b': 'Barra · trasbarra, sobre la encimera, encima de la hielera',
    'A4': 'Barra · trasbarra, extremo Sur',
    'V2': 'Barra · mostrador delantero, junto a P2 (Sur); lavavasos debajo',
    'V1': 'Barra · mostrador delantero, al Norte de V2; barriles debajo',
    'B1': 'Barra · bajo la vitrina V2',
    'B2': 'Barra · bajo la vitrina V1',
    'B3': 'Barra · barra de madera, extremo Norte (junto a la viga P1b)',
    'B4': 'Barra · barra de madera, extremo Sur',
}


def fmt(v):
    return f'{v:.2f}'.replace('.', ',')


def main():
    lineas = ['# Lista de compra · equipamiento Makro', '',
              'Medidas en metros, ancho × fondo × alto, tomadas de la ficha de makro.es. ',
              'La web de Makro bloquea el acceso directo desde servidores: las medidas se ',
              'leyeron de las fichas tal y como las indexa su buscador y se verificaron una ',
              'por una con un segundo pase. Confirmar en la ficha antes de comprar.', '',
              '| Rótulo | Producto | Medidas | Dónde va | Ficha |',
              '|---|---|---|---|---|']
    for p in Q.todos():
        enlace = f"[makro.es]({p['url']})" if p.get('url') else 'ya comprado / medida promedio'
        lineas.append(f"| {p['tag']} | {p['nombre']} | {fmt(p['a'])} × {fmt(p['f'])} × {fmt(p['h'])} "
                      f"| {UBICACION.get(p['tag'], '')} | {enlace} |")
    lineas += ['', '## Alternativas con la misma función (no dibujadas)', '',
               'Por si se prefiere otro fondo, otro acabado o el modelo de la foto de referencia. ',
               'Mismas fuentes y mismas reservas que la tabla anterior.', '',
               '| Sustituye a | Producto | Medidas | Ficha |', '|---|---|---|---|']
    for p in Q.ESTE_ALT + Q.OESTE_ALT:
        lineas.append(f"| {p['tag'].replace(' alt', '')} | {p['nombre']} | {fmt(p['a'])} × {fmt(p['f'])} × {fmt(p['h'])} "
                      f"| [makro.es]({p['url']}) |")
    lineas += ['', '## A medida, no se compran en Makro', '',
               '- Bancada de apoyo de la línea de cocción: 2,12 × 0,60, acero inoxidable.',
               '- Tabla de madera sobre el lavavajillas K6, del fregadero al horno: 0,57 × 0,66.',
               '- Encimera única de la trasbarra: 2,75 × 0,60.',
               '- Barra de madera del mostrador delantero: '
               f"{fmt(Q.BARRA_MADERA['y1'] - Q.BARRA_MADERA['y0'])} × 0,60.",
               '- Tabla de P2 al muro: 0,78 × 0,45.',
               '- Módulo técnico T1 bajo la cafetera: 0,60 de ancho.']
    salida = os.path.join(AQUI, 'LISTA_MAKRO.md')
    open(salida, 'w', encoding='utf-8').write('\n'.join(lineas) + '\n')
    print('LISTA_MAKRO.md ·', len(Q.todos()), 'productos')


if __name__ == '__main__':
    main()
