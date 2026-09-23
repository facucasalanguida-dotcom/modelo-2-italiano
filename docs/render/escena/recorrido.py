"""El recorrido de Casa Margot en fotos, en el orden en que se visita.

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
    calle:   True si por algun hueco se puede ver la calle: solo entonces se
             monta. Ante la duda, True: cuesta un poco mas montarla, y sin
             ella por el ventanal se veria una calle vacia
    exp:     exposicion; None deja la de siempre (0,65). Fuera -1,30.
    despl:   (opcional) desplazamiento vertical de la optica, para enseñar mas
             arriba sin inclinar la camara: las verticales siguen rectas

Despues de las 20 van seis mas (21-26): la barra y la cocina por dentro y
dos planos cenitales, uno por planta. Esos llevan tipo='planta': camara
ortografica mirando hacia abajo desde el centro 'centro', con 'ancho_m'
metros de lado, que corta el edificio a la cota 'corte' -todo lo que queda
por encima desaparece para la camara, no para la luz- y sale cuadrada.

Solo las nuevas, sin repetir las que ya estan hechas:
    python lote.py --vistas 21_barra_dentro,22_trasbarra,23_cocina_fondo,24_cocina_linea,25_planta_baja,26_planta_alta --gpu --spp 512 --salida .\\recorrido
"""

Z_PA = 2.560          # suelo de la planta alta (el mismo que escena.Z_PA)

RECORRIDO = [
    # ------------------------------------------------------------ la calle
    dict(nombre='01_calle', calle=True, exp=-1.30,
         ojo=(6.20, -9.20, 1.700), mira=(5.60, 1.60, 2.600), lente=28.0),
    # el porche cubierto y el ventanal, desde nuestra acera, en escorzo (a la
    # derecha de la farola de x = 2,0: desde detras tapaba un sexto de la foto)
    dict(nombre='02_porche', calle=True, exp=-1.30,
         ojo=(1.20, -1.60, 1.600), mira=(4.60, 1.30, 2.000), lente=18.0),
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
    dict(nombre='08_pizarra', calle=True, exp=None,
         ojo=(3.90, 2.35, 1.650), mira=(0.25, 3.50, 2.450), lente=24.0),
    # el paso de servicio desde dentro de la barra, hacia la cocina
    dict(nombre='09_paso', calle=True, exp=None,
         ojo=(1.42, 2.35, 1.560), mira=(1.05, 4.70, 1.150), lente=22.0),
    # la cocina, con la campana y la linea de coccion
    dict(nombre='10_cocina', calle=False, exp=None,
         ojo=(2.16, 5.90, 1.600), mira=(1.05, 8.70, 1.120), lente=21.0),
    # el centro de la sala: el pilar P3 con el botellero y las mesas del medio
    dict(nombre='11_centro', calle=True, exp=None,
         ojo=(7.20, 2.50, 1.600), mira=(5.95, 5.00, 1.300), lente=22.0),
    # el sillon corrido contra la medianera Norte
    dict(nombre='12_sillon', calle=True, exp=None,
         ojo=(7.90, 6.20, 1.520), mira=(3.20, 8.30, 1.150), lente=24.0),
    # el baño de planta baja, por dentro
    dict(nombre='13_bano', calle=False, exp=None,
         ojo=(7.62, 8.05, 1.550), mira=(9.85, 8.55, 1.150), lente=16.0),
    # la escalera desde la sala, subiendo contra la medianera Este
    dict(nombre='14_escalera', calle=True, exp=None,
         ojo=(8.05, 1.95, 1.640), mira=(9.35, 6.30, 1.500), lente=21.0),
    # ------------------------------------------------------- planta alta
    # la llegada: junto a los ultimos peldaños, la planta alta entera hacia el
    # Oeste (la vista 'alta' de la serie). Desde el rellano, la pared y la
    # puerta del almacen ocupaban un tercio de la foto a un metro
    dict(nombre='15_llegada', calle=True, exp=None,
         ojo=(8.45, 6.95, Z_PA + 1.580), mira=(3.55, 5.60, Z_PA + 1.120), lente=20.0),
    # la mesa larga de cowork
    dict(nombre='16_cowork', calle=True, exp=None,
         ojo=(6.60, 6.80, Z_PA + 1.540), mira=(3.60, 5.00, Z_PA + 1.100), lente=24.0),
    # la mesa redonda, desde el Noroeste, con el antepecho y las lamas detras.
    # Desde el Oeste el pilar P3 quedaba a 0,9 m, justo en medio
    dict(nombre='17_redonda', calle=True, exp=None,
         ojo=(6.30, 7.20, Z_PA + 1.500), mira=(7.60, 5.00, Z_PA + 0.850), lente=24.0),
    # asomado al vacio, la planta baja desde arriba
    dict(nombre='18_vacio', calle=True, exp=None,
         ojo=(3.35, 5.20, Z_PA + 1.620), mira=(5.60, 2.20, 0.900), lente=22.0),
    # el aseo de arriba, con la puerta del inodoro
    dict(nombre='19_aseo', calle=False, exp=None,
         ojo=(2.72, 7.75, Z_PA + 1.550), mira=(4.40, 8.75, Z_PA + 1.100), lente=16.0),
    # el almacen
    dict(nombre='20_almacen', calle=False, exp=None,
         ojo=(7.25, 7.76, Z_PA + 1.550), mira=(5.70, 8.75, Z_PA + 1.100), lente=16.0),
    # ------------------------------------------------- la barra por dentro
    # como la ve el camarero: por encima de las vitrinas, la sala y el ventanal
    dict(nombre='21_barra_dentro', calle=True, exp=None,
         ojo=(1.20, 3.05, 1.600), mira=(5.60, 3.40, 1.300), lente=20.0),
    # la trasbarra: la cafetera con sus tazas, el estante de botellas y tarros,
    # las jarras y la pizarra de la carta encima
    dict(nombre='22_trasbarra', calle=True, exp=None,
         ojo=(1.80, 2.60, 1.600), mira=(0.25, 3.70, 1.600), lente=16.0, despl=0.10),
    # ------------------------------------------------ la cocina por dentro
    # desde el fondo, junto a la campana, hacia el paso: la mesa de trabajo con
    # la fruta delante, las neveras a la derecha y el vidrio de la L a la izquierda
    dict(nombre='23_cocina_fondo', calle=False, exp=None,
         ojo=(2.20, 7.55, 1.620), mira=(0.70, 5.40, 1.200), lente=18.0),
    # la linea de coccion de frente, bajo la campana
    dict(nombre='24_cocina_linea', calle=False, exp=None,
         ojo=(1.45, 6.45, 1.600), mira=(1.35, 9.00, 1.250), lente=20.0),
    # ---------------------------------------------- planos cenitales, cuadrados
    # la planta baja entera, cortada a 2,00 (debajo de la campana y de los
    # dinteles, que asi salen como huecos; encima de las lamparas)
    dict(nombre='25_planta_baja', tipo='planta', calle=True, exp=None,
         centro=(5.02, 4.15), ancho_m=10.40, corte=2.00),
    # la planta alta entera, cortada a 2,00 de su suelo; por el vacio se ve la
    # planta baja
    dict(nombre='26_planta_alta', tipo='planta', calle=True, exp=None,
         centro=(5.02, 4.15), ancho_m=10.40, corte=Z_PA + 2.00),
]

NOMBRES = [t['nombre'] for t in RECORRIDO]
NUEVAS = NOMBRES[20:]
assert len(NOMBRES) == len(set(NOMBRES)) == 26
