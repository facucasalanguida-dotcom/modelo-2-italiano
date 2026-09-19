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
    'K1': 'Cocina · cocción, medianera Norte, bajo la campana, 1º desde el Oeste',
    'K2': 'Cocina · cocción, bajo la campana, 2º',
    'K3': 'Cocina · cocción, bajo la campana, 3º',
    'K4': 'Cocina · cocción, bajo la campana, 4º, contra la pared en L',
    'KC': 'Cocina · campana mural corrida sobre K1 a K4, borde inferior a +2,00',
    'K5': 'Cocina · muro Oeste, esquina Norte, sobre soporte',
    'K6': 'Cocina · muro Oeste, bajo el escurridor del fregadero K7 (hueco de lavavajillas)',
    'K7': 'Cocina · muro Oeste, entre el horno y los frigoríficos; cuba al Sur, escurridor al Norte',
    'K8': 'Cocina · muro Oeste, vertical, al Sur del fregadero',
    'K9': 'Cocina · muro Oeste, vertical, contra P1',
    'K10': 'Cocina · pared en L, de una pieza, pegada al doblez; 0,33 libres junto a la cocción',
    'A1': 'Barra · trasbarra, sobre la mesada, pegada a P1 (extremo Norte)',
    'A2': 'Barra · trasbarra, en el hueco de 0,20 a la derecha de la cafetera',
    'A3': 'Barra · trasbarra, sobre la mesada, a la derecha del molinillo',
    'A4': 'Barra · trasbarra, sobre la mesada, pegado a P2 (extremo Sur); debajo, nada',
    'A5': 'Barra · trasbarra, debajo de la mesada, bajo el hueco libre',
    'A6': 'Barra · trasbarra, estante mural sobre la mesada (2 piezas, 2,50 en total)',
    'V2': 'Barra · mostrador delantero, junto al zócalo del ventanal (Sur); lavavasos debajo',
    'V1': 'Barra · mostrador delantero, al Norte de V2',
    'B1': 'Barra · bajo la vitrina V2',
    'B2': 'Barra · debajo de la tabla de P2',
    'B3': 'Barra · barra de madera del mostrador (única cosa que queda en ella)',
    'B4': 'Barra · encima de la tabla de P2',
}


# Titulo literal de cada ficha tal y como lo devuelve el buscador de makro.es al
# buscar su identificador (verificacion del 15/09/2026: los 21 identificadores
# devuelven su ficha con este titulo).
TITULOS_MAKRO = {
    '623ef78b-af50-4e27-a2c5-b3a45089ba59': 'Placa de inducción eléctrica de acero inoxidable 2 x (Ø)230 mm, independiente, 6000 W, 400 V - TRI',
    '85f3fb44-3f09-463c-ab29-53822c8c1ce7': 'METRO Professional Cocedor de pasta eléctrico GNC1008, acero inoxidable, 47 x 55 x 38 cm, 4 cestos, 8 L',
    '57e9d9ed-d483-4f88-a049-5597b3a7ad18': 'Freidora profesional para hostelería, 1 cuba de 7 litros de aceite, eléctrica',
    'acd212b2-73a4-42bc-bea7-329d5ab4771d': 'Cleiton® Plancha Industrial de Acero Inoxidable Eléctrica 50 cm Sobremesa Top, placa de 8 mm',
    'a8240770-cb5f-491b-926d-83b1e1e00a22': 'Campana Extractora Industrial Recta Sin Turbina 2000x1200x500 Acabado satinado',
    'e3c35b3b-14d3-4e2b-a109-373a863ddff9': 'Horno industrial de conveccion electrico 4 bandejas 45x33cm',
    'b6893f6e-6c55-499e-8e8b-4e246d107961': 'Lavavajillas industrial cesta 50x50 cm monofásico - trifásico ST500',
    '3efac5b4-e702-4af6-9dd9-533709488190': 'Fregadero Industrial de Acero Inox 1 Cubeta con Puerta Gama 600 Distform (600x600x850, cubeta 500x400x250)',
    '2e636462-1801-45f6-a3d8-15413909cb8c': 'Armario refrigerado APS-451 I (626 x 740 x 1865 mm, 395 L)',
    '764bc52f-1287-4e08-89dc-c2e453dfea49': 'Mesa Refrigerada de 4 puertas - 350W - 2542x600x850mm',
    '6105678f-3159-4172-a17a-f400760f0b35': 'Lavamanos De Acero Inoxidable Con Grifo Y Pulsador De Pedal Cuba Circular 340 X 130Mm Y Medidas 400 X 400 X 850Mm',
    'e3db53e1-8f64-4495-bb2c-59fe355a32e2': 'Fabricador de cubitos de hielo 28Kg/24Hr Gastro M CT694',
    '2b8d9850-b422-4738-b716-c30da9857300': 'Licuadora de frutas industrial Li-240 de Sammic',
    'a7c3e878-0cdd-4f7e-b013-897ae4f6120d': 'Exprimidor De Naranjas Profesional Mizumo Next Gen Negro (48 x 35 x 73,5 cm)',
    'e858e346-8373-4e64-aa03-6f9a559e168e': 'Lavavasos industrial cesta 40x40 Elettrobar FAST 40',
    'f2d9d7ba-6f4f-4feb-b032-641cc4d828fe': 'Columna tirador completo para dispensar bebidas modelo en Te de 3 grifos',
    '230e627d-7291-43e0-a2b4-ebbf6e783f27': 'Mesa refrigerada de 4 puertas, acero inoxidable, refrigeración por aire, 85 x 223 x 70 cm, GN1/1, 380 W, EASYLINE, 553L, Vaiotec',
    '176b30f1-81b0-4a52-916e-80722d9a9240': 'METRO Professional Mesa refrigerada GCC3100, Inox, 179.5 x 70 x 85 cm, 334 L, refrigeración por ventilación, 400 W',
    '8969b667-b5cb-4e83-b599-3dd45c112547': 'Armario frigorífico, ventilado, 400 litros. acero inoxidable (626 x 740 x 1925 mm)',
    'd48c3c0c-7975-4c22-89c7-64676c23681f': 'Armario Refrigerado Ar400l Clima Hostelería',
    'c0cd57f0-35a2-485a-98f4-5dffc628d84e': 'Fregadero con bastidor con hueco lavavajillas cuba izquierda 1200x600x850 mm · Ref. AAA0045913963 (ficha facilitada por el cliente)',
    '1acedc0e-199c-449c-b390-a8626c771613': 'Lavavajillas industrial 50x50 - 575x600x820 mm - 3500 W 230/1V - 46278719 Eurast',
    '31bf0e3c-d322-4e34-a968-9bd9ace2024d': 'Cleiton® - Fregadero con 1 Seno con Estante 600x600x850 mm | Fregadero Industrial de Acero Inoxidable Profesional de 1 mm de Grosor',
    '77c7b69b-09e0-4c28-878e-9454ffff60ec': 'Botellero frigorífico para bebidas BTL1000 1040X580X850MM',
    '95121b55-b486-4a76-a3de-ed7874e75876': 'Fregadero industrial acero inoxidable 1 cuba 700x600x850mm',
    'a046bf7e-9d25-4304-9593-1cd32668e47f': 'Botellero inox ext-int 2 puertas 200 litros - 1020x550x850 mm - 110 W 230/1V - 74699209 Eurast',
    '6589602e-de66-484c-871f-68f83b182638': 'Botellero refrigerado bar, acero inox. 2 puertas, largo 100 cm. Yostin®',
    'f2df0f65-b185-40b2-b2e2-2cd42fb2eefd': 'Molinillo de café Cunil TRANQUILO de ABC (17 x 34 x 41 cm, 275 W)',
    'e4ddc7ec-739d-4b14-968b-1d230076b476': 'Máquina de helado y crema fría B-CREAM1HD de Bras (200 x 490 x 620 mm, 6 L)',
    'e826e334-3cba-44fc-a530-627af1dabaf6': 'Granizadora Industrial 1 Cuba 10Ltr GRANICREAM 1S Eurofred (200 x 500 x 790 mm)',
    '635e0924-0d3e-42ca-965e-e66eb41cdee1': 'Granizadora Industrial 1 Cuba 5Ltr GRANISMART 5x1 Eurofred (260 x 400 x 630 mm)',
    '8af91e42-ebf3-4239-8e01-9b6b82b73120': 'Estante mural cartelas compacto 1250x400x245 mm. Fabricante: Fricosmos. Referencia: 011410',
    '15f4f100-83b5-4f51-a383-11acf9989372': 'Estante en inox de pared (2000 x 400 x 250 mm)',
}


# Donde iria cada alternativa, por identificador de ficha
UBICACION_ALT = {
    '230e627d-7291-43e0-a2b4-ebbf6e783f27': 'Cocina · pared en L, en lugar de K10, pegada al doblez; fondo 0,70; 0,73 libres',
    '176b30f1-81b0-4a52-916e-80722d9a9240': 'Cocina · pared en L, en lugar de K10, pegada al doblez; deja 1,16 libres',
    '8969b667-b5cb-4e83-b599-3dd45c112547': 'Cocina · muro Oeste, en lugar de K8 y K9; misma huella que el Edenox',
    'd48c3c0c-7975-4c22-89c7-64676c23681f': 'Cocina · muro Oeste, en lugar de K8 y K9 (0,60 de ancho, lacado blanco)',
    '1acedc0e-199c-449c-b390-a8626c771613': 'Cocina · en lugar de K6 si el ST500 no entra bajo el escurridor (0,82 de alto)',
    'e3db53e1-8f64-4495-bb2c-59fe355a32e2': 'Sin sitio en la trasbarra nueva: decidir dónde va',
    'a7c3e878-0cdd-4f7e-b013-897ae4f6120d': 'Sin sitio en la trasbarra nueva: cabría en el hueco libre de mesada',
    '6105678f-3159-4172-a17a-f400760f0b35': 'Sin sitio: lo sustituye el fregadero A4, pegado a P2',
    '2b8d9850-b422-4738-b716-c30da9857300': 'Sin sitio en la trasbarra nueva: decidir dónde va',
    '3efac5b4-e702-4af6-9dd9-533709488190': 'Barra · alternativa al fregadero A4, con puerta (mismo hueco)',
    '95121b55-b486-4a76-a3de-ed7874e75876': 'Barra · alternativa al fregadero A4 en AISI-304, 0,10 más ancho',
    'a046bf7e-9d25-4304-9593-1cd32668e47f': 'Barra · alternativa a la nevera A5 (1,02, inox interior y exterior)',
    '6589602e-de66-484c-871f-68f83b182638': 'Barra · alternativa a la nevera A5 (1,00 exactos, fabricación nacional)',
    'e826e334-3cba-44fc-a530-627af1dabaf6': 'Barra · alternativa a A3: misma anchura, 10 L, pero 0,79 de alto',
    '635e0924-0d3e-42ca-965e-e66eb41cdee1': 'Barra · alternativa a A3: cuba de 5 L, 0,26 de ancho y solo 0,40 de fondo',
    '15f4f100-83b5-4f51-a383-11acf9989372': 'Barra · alternativa a A6: una sola pieza de 2,00 en vez de dos de 1,25',
}


def donde(p):
    """Texto de ubicacion de un producto dibujado o de una alternativa."""
    if p['tag'] in UBICACION:
        return UBICACION[p['tag']]
    return UBICACION_ALT.get((p.get('url') or '').rsplit('/', 1)[-1], '')


def fmt(v):
    return f'{v:.2f}'.replace('.', ',')


A_MEDIDA = [
    f"Bancada de apoyo de la línea de cocción, dentro del hundimiento: "
    f"{fmt(Q.BANCADA_COCCION['x1'] - Q.BANCADA_COCCION['x0'])} × "
    f"{fmt(Q.BANCADA_COCCION['y1'] - Q.BANCADA_COCCION['y0'])}, acero inoxidable.",
    f"Mesada única de la trasbarra, de P1 a P2: "
    f"{fmt(Q.TRASBARRA_Y[1] - Q.TRASBARRA_Y[0])} × {fmt(Q.MESADA_FONDO)}.",
    f"Hueco de {fmt(Q.HUECO_MOLINILLOS)} para el molinillo A2 y los utensilios, "
    'a la derecha de la cafetera.',
    'Barra de madera del mostrador delantero: '
    f"{fmt(Q.BARRA_MADERA['y1'] - Q.BARRA_MADERA['y0'])} × {fmt(Q.MOSTRADOR_X[1] - Q.MOSTRADOR_X[0])}.",
    f"Tabla de P2 al muro: {fmt(Q.TABLA_P2['x1'] - Q.TABLA_P2['x0'])} × {fmt(Q.TABLA_P2['y1'] - Q.TABLA_P2['y0'])}"
    ' (chopera B4 encima, barril B2 debajo).',
    f"Mostrador delantero: {fmt(Q.MOSTRADOR_Y[1] - Q.MOSTRADOR_Y[0])} × "
    f"{fmt(Q.MOSTRADOR_X[1] - Q.MOSTRADOR_X[0])} de fondo, del zócalo del ventanal a P1.",
]


def titulo(p):
    return TITULOS_MAKRO.get((p.get('url') or '').rsplit('/', 1)[-1], '')


def main():
    lineas = ['# Lista de compra · equipamiento Makro', '',
              'Medidas en metros, ancho × fondo × alto, tomadas de la ficha de makro.es. ',
              'La web de Makro bloquea el acceso directo desde servidores: las medidas se ',
              'leyeron de las fichas tal y como las indexa su buscador y se verificaron una ',
              'por una con un segundo pase. Confirmar en la ficha antes de comprar. ',
              'La misma lista está en la lámina 04 de `Planos_Completos.pdf`, con los ',
              'enlaces clicables.', '',
              '| Rótulo | Producto | Medidas | Dónde va | Ficha |',
              '|---|---|---|---|---|']
    for p in Q.todos():
        enlace = f"[makro.es]({p['url']})" if p.get('url') else 'ya comprado / medida promedio'
        lineas.append(f"| {p['tag']} | {p['nombre']} | {fmt(p['a'])} × {fmt(p['f'])} × {fmt(p['h'])} "
                      f"| {UBICACION.get(p['tag'], '')} | {enlace} |")
    lineas += ['', '## Alternativas con la misma función (no dibujadas)', '',
               'Por si se prefiere otro fondo, otro acabado o el modelo de la foto de referencia. ',
               'Mismas fuentes y mismas reservas que la tabla anterior.', '',
               '| Sustituye a | Producto | Medidas | Dónde iría | Ficha |', '|---|---|---|---|---|']
    for p in Q.ESTE_ALT + Q.OESTE_ALT + Q.ALT_BARRA + Q.SIN_SITIO:
        lineas.append(f"| {p['tag'].replace(' alt', '')} | {p['nombre']} | {fmt(p['a'])} × {fmt(p['f'])} × {fmt(p['h'])} "
                      f"| {donde(p)} | [makro.es]({p['url']}) |")
    lineas += ['', '## A medida, no se compran en Makro', ''] + \
              ['- ' + t for t in A_MEDIDA]
    lineas += ['', '## Enlaces verificados el 15/09/2026', '',
               'makro.es devuelve 403 a cualquier petición desde un servidor (curl, Playwright o ',
               'un navegador real en la nube), así que los enlaces no se pueden abrir desde aquí. ',
               'La verificación se hizo buscando cada identificador de ficha con el buscador ',
               'restringido a makro.es: todos los identificadores devuelven exactamente su URL con ',
               'este título, salvo la ficha del fregadero K7 (Ref. AAA0045913963), que el buscador no ',
               'indexa y cuyo enlace facilitó el propio cliente desde la web de Makro. Si un enlace ',
               'fallara al abrirlo, buscar el título en makro.es.', '',
               '| Rótulo | Título literal de la ficha en makro.es | Enlace |', '|---|---|---|']
    for p in Q.todos() + Q.ESTE_ALT + Q.OESTE_ALT + Q.ALT_BARRA + Q.SIN_SITIO:
        if p.get('url'):
            lineas.append(f"| {p['tag']} | {titulo(p)} | {p['url']} |")
    salida = os.path.join(AQUI, 'LISTA_MAKRO.md')
    open(salida, 'w', encoding='utf-8').write('\n'.join(lineas) + '\n')
    print('LISTA_MAKRO.md ·', len(Q.todos()), 'productos')


if __name__ == '__main__':
    main()
