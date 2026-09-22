"""El recorrido de Casa Margot en 20 fotos, en el orden en que se visita.

Primero la calle, luego la puerta y despues todos los espacios, uno detras
de otro: el recibidor con el logo, el comedor, el ventanal, la barra, la
trasbarra con la pizarra, el paso de servicio, la cocina, el centro de la
sala, el sillon corrido, el baño, la escalera y, arriba, la llegada, las
dos mesas, el vacio, el aseo y el almacen.

Solo datos, sin Blender: lo importa escena.py para montar las camaras y
lote.py, que corre con el Python del sistema, para saber que renderizar y en
que orden. Cada foto sale como CM_<nombre>.png y el numero delante hace que
en la carpeta queden en el orden del recorrido.

Cada toma:
    nombre:  01_calle, 02_porche...
    ojo:     donde esta la camara (x, y, z), en metros, coordenadas del local
    mira:    el punto al que apunta
    lente:   focal en mm, con sensor de 36 mm (18 = gran angular)
    calle:   True si por algun hueco se ve la calle: solo entonces se monta
    exp:     exposicion; None deja la de siempre (0,65). Fuera -1,30.
"""

Z_PA = 2.560          # suelo de la planta alta (el mismo que escena.Z_PA)

RECORRIDO = [
    # ------------------------------------------------------------ la calle
    dict(nombre='01_calle', calle=True, exp=-1.30,
         ojo=(6.20, -9.20, 1.700), mira=(5.60, 1.60, 2.600), lente=28.0),
    # el porche cubierto y el ventanal, desde nuestra acera, en escorzo
    dict(nombre='02_porche', calle=True, exp=-1.30,
         ojo=(1.60, -2.20, 1.600), mira=(4.60, 1.30, 2.000), lente=18.0),
    # la puerta, metida en su cubo, con el escaparate al lado
    dict(nombre='03_puerta', calle=True, exp=-1.30,
         ojo=(8.70, -1.60, 1.620), mira=(7.60, 1.05, 1.250), lente=24.0),
    # ------------------------------------------------------- planta baja
    # nada mas entrar: la pared azzurro con el logo y la puerta a la derecha
    dict(nombre='04_recibidor', calle=True, exp=None,
         ojo=(6.35, 1.95, 1.680), mira=(9.88, 2.78, 1.470), lente=26.0),
    # el comedor entero desde la esquina de la entrada
    dict(nombre='05_comedor', calle=True, exp=None,
         ojo=(9.30, 1.70, 2.150), mira=(3.40, 6.60, 1.250), lente=18.0),
    # las mesas del ventanal y el escaparate de doble altura
    dict(nombre='06_ventanal', calle=True, exp=None,
         ojo=(4.60, 6.30, 1.580), mira=(6.10, 1.30, 1.900), lente=24.0),
    # la barra en diagonal, con el mostrador huyendo
    dict(nombre='07_barra', calle=True, exp=None,
         ojo=(4.90, 1.95, 1.520), mira=(1.35, 4.30, 1.060), lente=24.0),
    # la trasbarra y la pizarra de la carta, entre los dos colgantes
    dict(nombre='08_pizarra', calle=False, exp=None,
         ojo=(3.90, 2.35, 1.650), mira=(0.25, 3.50, 2.450), lente=24.0),
    # el paso de servicio desde dentro de la barra, hacia la cocina
    dict(nombre='09_paso', calle=False, exp=None,
         ojo=(1.42, 2.35, 1.560), mira=(1.05, 4.70, 1.150), lente=22.0),
    # la cocina, con la campana y la linea de coccion
    dict(nombre='10_cocina', calle=False, exp=None,
         ojo=(2.16, 5.90, 1.600), mira=(1.05, 8.70, 1.120), lente=21.0),
    # el centro de la sala: el pilar P3 con el botellero y las mesas del medio
    dict(nombre='11_centro', calle=True, exp=None,
         ojo=(7.20, 2.50, 1.600), mira=(5.95, 5.00, 1.300), lente=22.0),
    # el sillon corrido contra la medianera Norte
    dict(nombre='12_sillon', calle=False, exp=None,
         ojo=(7.90, 6.20, 1.520), mira=(3.20, 8.30, 1.150), lente=24.0),
    # el baño de planta baja, por dentro
    dict(nombre='13_bano', calle=False, exp=None,
         ojo=(7.62, 8.05, 1.550), mira=(9.85, 8.55, 1.150), lente=16.0),
    # la escalera desde la sala, subiendo contra la medianera Este
    dict(nombre='14_escalera', calle=False, exp=None,
         ojo=(8.05, 1.95, 1.640), mira=(9.35, 6.30, 1.500), lente=21.0),
    # ------------------------------------------------------- planta alta
    # la llegada de la escalera
    dict(nombre='15_llegada', calle=True, exp=None,
         ojo=(8.20, 8.10, Z_PA + 1.580), mira=(4.60, 5.40, Z_PA + 1.150), lente=21.0),
    # la mesa larga de cowork
    dict(nombre='16_cowork', calle=True, exp=None,
         ojo=(6.60, 6.80, Z_PA + 1.540), mira=(3.60, 5.00, Z_PA + 1.100), lente=24.0),
    # la mesa redonda
    dict(nombre='17_redonda', calle=True, exp=None,
         ojo=(4.90, 4.80, Z_PA + 1.540), mira=(7.60, 5.60, Z_PA + 1.120), lente=26.0),
    # asomado al vacio, la planta baja desde arriba
    dict(nombre='18_vacio', calle=True, exp=None,
         ojo=(3.35, 5.20, Z_PA + 1.620), mira=(5.60, 2.20, 0.900), lente=22.0),
    # el aseo de arriba, con la puerta del inodoro
    dict(nombre='19_aseo', calle=False, exp=None,
         ojo=(2.72, 7.75, Z_PA + 1.550), mira=(4.40, 8.75, Z_PA + 1.100), lente=16.0),
    # el almacen
    dict(nombre='20_almacen', calle=False, exp=None,
         ojo=(7.25, 7.76, Z_PA + 1.550), mira=(5.70, 8.75, Z_PA + 1.100), lente=16.0),
]

NOMBRES = [t['nombre'] for t in RECORRIDO]
assert len(NOMBRES) == len(set(NOMBRES)) == 20
