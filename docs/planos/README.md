# Planos del local

Cuatro laminas tecnicas en A3, pensadas para imprimir y acotar a mano sobre
ellas. Las dos primeras son de estructura a 1:50 —muros, medianeras, pilares
y machones, viga descolgada, forjado del altillo, escalera, carpinteria de
fachada, puntos de luz y aire acondicionado— con el mobiliario de sala y las
reservas de espacio del cliente encima. Las dos ultimas son el equipamiento
de barra y cocina: el detalle a 1:25 y la lista de compra con los enlaces a
las fichas de makro.es.

| Archivo | Contenido |
|---|---|
| `PLANTA_BAJA.pdf` | Lamina 01 · planta baja, cota ±0,00, con mesas e itinerario accesible |
| `PLANTA_ALTA.pdf` | Lamina 02 · altillo, cota +2,56 |
| `EQUIPAMIENTO.pdf` | Lamina 03 · barra y cocina a 1:25, con el cuadro de equipos |
| `LISTA_EQUIPAMIENTO.pdf` | Lamina 04 · lista de compra con los enlaces clicables |
| `Planos_Estructura.pdf` | Las dos plantas en un solo documento |
| `Planos_Completos.pdf` | Las cuatro laminas en un solo documento |
| `LISTA_MAKRO.md` | La misma lista de compra en texto, con los enlaces |

## Sistema de coordenadas

```
X = 0,000    cara exterior del muro OESTE
X = 10,040   cara exterior de la medianera ESTE
Y = 0,000    punto mas al sur del solar (cara sur del pilar de fachada)
Y = 9,156    cara exterior de la medianera NORTE
Z = 0,000    pavimento de planta baja
Z = +2,560   pavimento del altillo (medido en obra)
```

## Origen de las medidas

Las cotas salen del levantamiento previo (planimetria 1:50 y propuesta 1:30),
convertidas a metros con las escalas validadas contra las cotas rotuladas de
los propios planos: aseo 3,92 m2 (rotulado 3,90), almacen 2,59 m2 (rotulado
2,60), huella de peldano 0,260 m, 17 tabicas de 3,00/17 = 0,1765 m. La
geometria se ha contrastado despues con los videos del local en obra.

## Revision del 14 set. 2026 sobre medidas de obra

Sobre el PDF anotado a mano por el cliente se aplicaron:

- **Alturas.** Del pavimento de planta baja al suelo del altillo hay **2,560 m**
  medidos, no los 3,000 supuestos. La tabica de la escalera pasa a 2,560/17 =
  0,151 m. El canto del forjado sigue sin medir, asi que la altura libre de
  planta baja queda como "2,56 menos el canto".
- **Pilares.** P1 0,30 x 0,60 · P2 0,58 x 0,45 llegando ya hasta el ventanal ·
  P3 0,65 x 1,07 · P5 0,60 x 1,00. Aparece **P1b**, el machon de 1,83 x 0,25
  que sube de P1 al forjado y que antes se dibujaba como viga descolgada.
- **Pared en L nueva.** Tramo largo de 3,60 a 2,22 m de la cara interior del
  muro Oeste, con doblez de 0,74 hacia el Oeste. Sostiene un panel de vidrio
  de 1,35 m de alto.
- **Fachada.** El ventanal sur queda partido por P2: pano de 0,78 al Oeste y
  pano de 4,00 al Este. En el escaparate se situa la puerta de acceso, de
  2,10 de ancho y 1,00 de barrido, pegada a P5.
- **Reservas de espacio.** En trazos y en color aparte, sin ser estructura: la
  barra (3,40 a lo largo de la pared en L), el paso de personal y el sillon
  corrido de 4,89 contra la medianera norte.

## Revision del 15 set. 2026 sobre el segundo croquis

(Superada en parte por la revision de la tarde, mas abajo.)

- **Pared en L de 4,22** (antes 3,60) y 1,22 de alto; paso de personal de
  0,60; la barra queda en 2,63 (medida 2,80). P1b pasa a dibujarse como viga:
  si fuera macizo la cocina no tendria entrada.
- **Bano nuevo** en el rincon NE, entre la medianera Norte, la Este y el
  desembarco de la escalera, con puerta de 0,70 hacia dentro.
- **Puerta a la derecha** (contra la medianera Este) y escaparate a la
  izquierda, pegado a P5.
- **Mesas** con medidas promedio: 9 en planta baja (32 plazas, tres de ellas
  contra el sillon corrido) y en el altillo una mesa de cowork de 2,40 x 1,00
  con 8 puestos mas dos redondas. `mobiliario.py`.
- **Luces** replanteadas sobre el mobiliario: un colgante por mesa, tres sobre
  la barra y empotrados en pasillos, cocina, bano y escalera.
- **Equipamiento con productos de Makro** (`equipamiento.py`): cada maquina
  lleva el enlace a su ficha y sus medidas. La web de Makro bloquea el acceso
  directo desde servidores, asi que las medidas salen de las fichas tal y como
  las indexa su buscador; confirmar antes de comprar. Coccion corrida en la
  medianera Norte bajo campana de 2,00; horno, lavavajillas bajo tabla,
  fregadero y dos armarios frigorificos en el muro Oeste; nevera corrida de
  acero como mesada en la pared en L. En la barra, dos vitrinas con lavavasos
  y barriles debajo, barra de madera con tablet y chopera, y en la trasbarra
  cafetera, lavamanos, hielera con licuadora y exprimidor.

## Revision del 15 set. 2026 (tarde) sobre el tercer croquis

Croquis `Planos_Ya.pdf` con las medidas en rojo de planta baja, mas la foto
de referencia de la mesa refrigerada (METRO GCF3100BS, 179,5 x 70 x 85).

- **Pared en L de 3,66 + doblez de 0,74** (antes 4,22): termina en y=5,35.
  La barra sube hasta 4,75 (3,19 de mostrador) y entre ambas queda el paso de
  personal de 0,60. Cocina entre x 0,25..2,37 e y 5,45..9,01.
- **Mesas** separadas del ventanal (0,52 libres junto al vidrio) y de la
  barra (1,13); 32 plazas. Luces replanteadas otra vez sobre las mesas.
- **Cocina.** Campana de 2,00 x 1,20 corrida sobre K1 a K4 (induccion,
  cocedor de pasta, freidora y plancha) en la medianera Norte. Se quita la
  cortadora de fiambre, que no se habia pedido. K10 y K11 pasan a ser UNA sola
  mesa refrigerada de acero, la mas larga que lista makro.es (Infrico 4
  puertas, 2,54 x 0,60 x 0,85; ninguna ficha pasa de 2,545), pegada al
  doblez de la L (16 set.); los 0,42 libres quedan junto a la coccion. La tabla sobre el lavavajillas se dibuja maciza.
  Los dos armarios frigorificos pasan a inox (Edenox APS-451 I, 0,626 x
  0,74): en makro.es no hay armario refrigerado inox de puerta ciega mas
  estrecho, asi que el fregadero baja a 0,60 (Distform gama 600) para que
  los cinco modulos del muro Oeste sumen 3,01 en los 3,05 que hay hasta P1.
  Pasillo de cocina de 0,78 (frente a los frigorificos) a 0,92.
- **Medidas verificadas** con un segundo pase de agentes sobre el buscador de
  makro.es (la web devuelve 403 a servidores, tambien con Playwright): se
  corrigio el alto del lavavajillas (0,863) y se descarto el AR400L por ser
  lacado blanco. Sin dato en ficha: alto de la columna de cerveza (Makro no
  lista columna de 2 grifos; se deja la de 3 con bandeja 40 x 40).
- **`LISTA_MAKRO.md`**: lista de compra con enlace a cada ficha, medidas y
  sitio en el plano, generada por `lista_makro.py` a partir de
  `equipamiento.py`. Incluye alternativas (mesa Vaiotec de 2,23 x 0,70, METRO
  GCC3100, frigorifico Diamond, AR400L, fregadero 70 x 70).
- **`makro_fichas.py`**: script para descargar las fichas desde un ordenador
  con conexion normal (Playwright) y devolver `makro_fichas.json`.
- **Mesa M3** (doble): estaba delante del arranque de la escalera y se lleva
  junto a M2, con 0,30 entre cantos, para dejar libre el camino de la puerta
  a la escalera (2,29 hasta la medianera). Los dos empotrados de esa zona se
  recolocan en ese camino (x 8,30) y el rotulo DOBLE ALTURA se mueve.
- **Accesibilidad (16 set.)**: se retiran las dos mesas dobles (la del
  ventanal junto a la entrada y la de junto a la caja de escalera) para abrir
  un itinerario accesible de 1,20 (CTE DB-SUA) desde la puerta a la barra, al
  bano y a una plaza de silla de ruedas entre M1 y M2, con giros de 1,50 en
  la entrada y ante el bano. La fila del ventanal baja 0,15 (1,26 hasta las
  sillas de la fila central) y la mesa central Este se corre 0,10 al Oeste
  (1,36 hasta la caja de escalera). Quedan 28 plazas y las mesas se
  renumeran M1 a M7. El itinerario, los giros y la plaza PMR se dibujan en la
  lamina 01 (`ACC_*` en `mobiliario.py`) y se comprueban con un chequeo de
  holgura de 0,60 a cada lado del trazo. El bano dibujado (2,49 x 1,28) no
  tiene el giro de 1,50 de un aseo accesible: queda anotado.
- **Sillon corrido (16 set.)**: tres cuadruples; las de los extremos pegadas
  a la pared en L y al tabique del bano (0,03) y la central centrada (0,63 a
  cada lado). Se retiran los tres colgantes de la barra (quedan los tres
  empotrados de la trasbarra). 28 plazas; mesas M1 a M7. El rotulo de la
  pared en L pasa al lado de la cocina.
- **Planta alta (16 set.)**: se quita la redonda del desembarco de la
  escalera y la otra pasa a diametro 1,20 con seis sillas a 60 grados (N, S
  y cuatro a 30 grados del eje Este-Oeste, la orientacion que menos ocupa a
  lo ancho), colocada para que el paso Norte hacia el aseo y el almacen
  quede en 1,01; a los lados quedan 0,26 hasta P3 y 0,26 hasta la caja de
  escalera (accesos a sillas) y 0,37 de la silla Sur a la barandilla. La mesa de cowork baja 0,20 y se corre 0,10 al Oeste
  (1,01 de paso al Norte, 0,85 hasta P3, 0,42 hasta la barandilla Oeste).
  Todos los pasos libres se acotan en azul en la lamina 02 (`PASOS_PA` en
  `mobiliario.py`, dibujados por `cotas_paso`). 14 puestos.
- **Luces (16 set.)**: se retiran todos los puntos de luz replanteados sobre
  el mobiliario y vuelven a dibujarse solo los del proyecto de reforma
  original (`EMPOTRADOS` y `COLGANTES` de `estructura.py`, planta baja);
  la planta alta queda sin puntos de luz, como en el original.
- **Fregadero con hueco de lavavajillas (16 set.)**: K7 pasa a ser el
  fregadero con bastidor y hueco de lavavajillas, cuba izquierda,
  1200 x 600 x 850 que eligio el cliente en makro.es (Ref. AAA0045913963,
  395 EUR mas IVA). Mirando al muro, la cuba queda al Sur y el escurridor al
  Norte con el lavavajillas K6 debajo; desaparece la tabla de madera. Muro
  Oeste: 0,59 + 1,20 + 0,63 + 0,63 = 3,04 en 3,05. El buscador de Makro no
  indexa esa ficha; el enlace lo facilito el cliente
  (`c0cd57f0-35a2-485a-98f4-5dffc628d84e`).
  El ST500 mide 0,83 de alto (la ficha tambien dice 863 mm) frente a los
  0,85 totales del fregadero: hay que confirmar el hueco libre o regular las
  patas; como alternativa se lista un Eurast de 575 x 600 x 820.
  En la barra, la encimera unica va de A2 a A4 (1,28) y se quita el rotulo
  ENTRADA 1,18 de la cocina (la cota de 1,18 sigue en la cadena inferior).
- **Pilar P3 (16 set.)**: el cliente marco en su plano corregido 2,35 de la
  cara Este del pilar a la escalera en planta baja (2,50 en el altillo), 3,20
  desde la linea de la pared en L (medido en el altillo desde el borde del
  forjado), 3,25 de la cara Norte a la medianera Norte y 0,70 de la cara Sur
  a la barandilla. Tres agentes auditaron las medidas: uno midio el
  levantamiento vectorial (da el pilar en 5,62..6,22, a 2,54 de la caja y
  3,15 de la pared en L: la correccion del 14/09 lo habia movido en sentido
  contrario, a 5,41), otro leyo todas las anotaciones manuscritas del cliente
  y el tercero comprobo las 120 cotas de las laminas. Resultado: P3 pasa a
  x 5,670..6,320, y 4,688..5,758 (3,20 / 3,25 / 0,70), y el cerramiento de
  la escalera en planta baja se dibuja con su cara Oeste en 8,670, a 2,35 del
  pilar (`CAJA_ESC_PB`, 0,14 de espesor en plano frente a la barandilla del
  altillo en 8,759..8,811, a 2,44 del pilar y 2,49 al primer peldaño). Asi
  cuadran las cuatro medidas del cliente; queda por medir el espesor de ese
  cerramiento (COMPROBAR 6). Consecuencias: las dos cuadruples de la fila
  central pasan al Oeste del pilar (al Este ya no cabe mesa mas itinerario de
  1,20), la fila del ventanal baja 0,09 para mantener 1,21 entre sus sillas y
  el pilar, la redonda del altillo se centra entre el pilar y la caja (0,26 a
  cada lado, 0,85 de la mesa de cowork al pilar) y las cadenas de cotas se
  leen del propio `PILARES`.
- **Correcciones de la auditoria (16 set.)**: se quita una cota huerfana de
  3,30 en la medianera Este; el mostrador, la reserva de barra y la tabla de
  P2 arrancan en la cara interior del vidrio (1,621), asi que el mostrador
  mide 3,13 y la barra de madera 1,13; notas y comentarios con cifras
  antiguas (3,01; 0,80; 0,40/0,39/0,59; 1,19) puestas al dia; rotulo de la
  escalera fuera del bano; cota 3,25 fuera del texto 0,65; cota 0,30 de P1
  fuera del poche en la lamina 03.
- **Lamina 04** (`LISTA_EQUIPAMIENTO`): toda la maquinaria con medidas, sitio
  en el plano y la ficha de makro.es, con los enlaces clicables en el PDF
  (anotaciones anadidas con pymupdf tras exportar el SVG; cairosvg no las
  genera). Las cuatro laminas van en `Planos_Completos.pdf`.

## Revision del 19 set. 2026 sobre el plano marcado en rojo y morado

El cliente devolvio la lamina 01 con catorce cotas en rojo, un hundimiento en
morado y un encargo nuevo para las mesas y la trasbarra. Las cotas se leyeron
del PDF pixel a pixel (cada linea roja se localizo y se convirtio a
coordenadas de obra), no a ojo.

### Cadena Este-Oeste: cierra exacta

    0,250 (cara interior del muro Oeste)
      + 2,18  hundimiento de la medianera Norte      -> 2,430
      + 0,13  pano de pared normal (deducido)        -> 2,560
      + 0,10  pared en L                             -> 2,660
      + 3,01  a P3                                   -> 5,670
      + 0,65  P3                                     -> 6,320
      + 2,33  a la caja de escalera                  -> 8,650
      + 0,16  cerramiento de la escalera (deducido)  -> 8,811 = primer peldano

Las cinco medidas del cliente cierran contra el primer peldano de la escalera
con dos incognitas: el pano de pared entre el hundimiento y la pared en L
(0,13, el "poco a su lado" que menciona) y el espesor del cerramiento de la
escalera (0,16, coherente con los 2,33 de planta baja y los 2,50 que midio en
el altillo hasta el peldano). **P3 no se mueve**: queda donde lo dejo la
revision del 16 set.

### Hundimiento de la medianera Norte

El pano de 2,18 que va del muro Oeste hasta la pared en L esta **0,275 metido
hacia el Norte**. Lo confirman las dos medidas del cliente: de la cara del
hundimiento a la base de la pared en L hay 3,575 y del arranque de la pared en
L (que apoya en el pano normal) 3,30; la diferencia es exactamente 0,275. La
bancada de coccion y la campana se meten en ese hueco, como pidio el cliente.
Con el espesor del levantamiento (0,148) la cara exterior se saldria del
solar: en ese tramo la medianera es mas gruesa o hay un hueco detras, y asi
queda anotado.

### Zocalo del ventanal

Los 2,72 de P3 al ventanal no eran al vidrio sino **al zocalo que hay en el
suelo**: con P3 en 4,688 la cara interior del zocalo queda en 1,968, o sea
**0,347 de fondo** contados desde el vidrio, o sea 0,16 por delante de la
cara interior del muro del ventanal, que ya tiene 0,25 de espesor. El ventanal no se mueve.
La barra arranca en ese zocalo y mide los 2,79 medidos, con lo que termina
justo en la cara Sur de P1 y deja 0,95 de paso de personal hasta la base de la
pared en L.

### Resto de cotas del cliente

| Medida | Donde | Antes | Ahora |
|---|---|---|---|
| 2,18 | hundimiento de la medianera Norte | 2,12 | 2,18 |
| 3,01 | pared en L a P3 | 3,20 | 3,01 |
| 2,33 | P3 a la caja de escalera | 2,35 | 2,33 |
| 3,23 | P3 a la medianera Norte | 3,25 | 3,25 (2 cm) |
| 3,65 | P3 a P5 | 3,69 | 3,69 (4 cm) |
| 2,72 | P3 al zocalo del ventanal | — | zocalo de 0,347 |
| 2,79 | largo de la barra | 3,13 | 2,79 |
| 1,65 | muro Oeste al arranque de la barra | 1,62 | 1,65 |
| 1,31 | P5 a la jamba del vestibulo | 1,28 | 1,31 |
| 2,23 | jamba del vestibulo al muro Este | 2,28 | 2,25 (2 cm) |
| 2,06 | ancho de la puerta de entrada | 2,10 | 2,06 |

Las de 3,23 y 3,65 se dejan como estaban: mueven P3 dos y cuatro centimetros
en sentidos contrarios, asi que se mantiene la posicion que ya cerraba con las
cuatro medidas del 16 set. La diferencia queda anotada en COMPROBAR EN OBRA.
El "2,00" que marco junto al muro Este era la puerta: el cliente aclaro que
son 2,06 de ancho y 1,00 de barrido.

### Muro Norte, pared en L y hundimiento (correccion del 19 set., noche)

El cliente corrige la cadena del lado Oeste: entre la barra y la pared en L
tiene que haber **0,60 de paso**, la **L arranca en el inicio de P1** y mide
**3,60**, y el muro Norte no lleva nada por delante (el trasdosado que se
habia supuesto no existe). El tamano del hundimiento queda a nuestro criterio.

Cadena resultante, de Sur a Norte por la linea de la barra:

    1,968  cara interior del zocalo del ventanal
     +2,79  barra                      ->  4,759   cara SUR de P1
     +0,60  paso de personal           ->  5,357   cara NORTE de P1 = base de la L
     +3,60  pared en L                 ->  8,957   cara interior del muro Norte
     +0,05  hundimiento                ->  9,008   pared hundida de la cocina
     +0,15  espesor del muro           ->  9,156   borde del solar

Con la L en 3,60 todo cuadra a la vez:

| | Valor | Comprobacion |
|---|---|---|
| Paso barra - pared en L | **0,598** | los 0,60 pedidos |
| Base de la pared en L | **5,357** | cara Norte de P1, exacta |
| Pared en L | **3,60** | llega al muro Norte |
| Hundimiento | **0,05** | escalon del muro, no un hueco |
| Espesor del muro en la cocina | **0,148** | el del levantamiento |
| Espesor del muro en el resto | **0,199** | |
| De la pared hundida a P1 | **3,651** | los 3,65 que midio el cliente en el muro Oeste, hundimiento incluido |

El muro Norte es **macizo** desde su cara interior hasta el borde del solar:
no hay trasdosado ni nada por delante. Lo unico que cambia con el hundimiento
es su espesor, y en la cocina sale justo el 0,148 del levantamiento. El
espesor real queda en COMPROBAR EN OBRA.

**Lo que arrastra**, respecto del plano del 19 set. por la manana:

- El sillon corrido y con el las mesas M7, M10 y M11 pasan a 7,657-8,357.
- El camino de la puerta a la barra, que con la nevera A7 puesta va por el
  Norte de la fila central, queda en **0,70**.
- La bancada de coccion y la campana quedan en 8,408-9,008.
- La linea del muro Oeste de la cocina **vuelve a caber**: entre la cara
  Norte de P1 y la bancada hay 3,05 y los cuatro aparatos suman 3,04.

Superficies: 75,25 m2 utiles en planta baja, 37,79 m2 de doble altura y
33,36 m2 de forjado.

### Mesas: ocho dobles de 0,70 x 0,70

Reparto del 19 set. (tarde), con M6 y M9 eliminadas y las dos cuadruples
formadas juntando dos mesas:

- **Fila del ventanal.** M1, M3 y M2 en vertical (sillas al Norte y al Sur),
  **a 0,60 entre mesas**, que son **0,88 entre sillas**: por ahi pasa una
  persona de frente. Posiciones: M1 3,530-4,230, M3 4,830-5,530 y
  M2 6,130-6,830; los dos huecos van acotados en la lamina.

  La fila mide 3,30 y es lo que deja el local sin tocar nada de lo demas:

  - delante del mostrador quedan **1,00 justos** (M1 arranca en 3,530);
  - la silla Norte de M2 arranca en 6,270, 5 mm despues de donde acaba la
    nevera A7 (6,265), asi que no entra en el barrido de su puerta;
  - M2 acaba en 6,830, a 0,81 de la jamba del vestibulo: usa el hueco de P5,
    el sitio que el cliente habia pedido aprovechar, sin meterse en la puerta.

  M1 y M3 se sirven desde el pasillo del ventanal (1,20 entre las dos filas
  de sillas) y M2 desde el lado de la entrada, donde hay 1,16 libres.

- **Fila central.** M5 y M4, con **M4 pegada a la cara Oeste de P3**. M6 se
  quita. Al Oeste de M5 no va ninguna mesa: ahi esta la unica salida del
  personal de la barra a la sala, que queda en 1,31.
- **Fila del sillon corrido.** M7+M8 y M11+M12 juntas, dos cuadruples de 1,40
  **pegadas a sus paredes** (0,02 a la pared en L y al tabique del bano), y
  M10 centrada entre las dos, con 0,665 a cada lado. M9 se quita.

Ocho mesas y **20 plazas sentadas**.

### Nevera de bebidas en P3 y lo que le hace al paso

El cliente pidio una nevera expositora "estilo las de Pepsi" en la cara de P3
que mira al ventanal. Se busco en Makro la mas estrecha que cabe en esa cara
de 0,65: **Gasfrit de 0,54 x 0,58 x 1,92, 400 L** (A7 en la lamina 04, con su
enlace). Se dibuja centrada, con 0,055 a cada lado.

El paso no se estima: se calcula con el mayor circulo que va de la puerta a
cada sitio sobre la planta entera con el mobiliario puesto, en malla de 1 cm.

| Nevera | Paso por delante de P3 | Camino puerta -> barra |
|---|---|---|
| sin nevera | 1,04 | **1,04**, por el Sur |
| en la cara Sur de P3 (lo pedido) | **0,45** | **0,74**, dando la vuelta por el Norte |
| girada a la cara Este de P3 | 1,04 | **1,04**, por el Sur |

Entre el frente de la nevera (4,108) y las sillas de M2 (3,658) quedan 0,45:
por delante del pilar ya no se pasa. El camino de la puerta a la barra tiene
que rodear la fila central por el Norte, donde el hueco entre sus sillas y las
del sillon es de 0,74. El pasillo del ventanal, de 1,20 entre las dos filas de
sillas, se queda comunicado solo por su extremo Oeste: en la lamina se dibuja
como ramal sin salida. Todo eso esta acotado (0,45 y 0,74) y escrito en las
notas de la lamina 01.

Girar la nevera a la cara Este de P3 devuelve el paso a 1,04 sin mover ninguna
mesa y sin que la nevera deje de verse desde la entrada: es la alternativa que
se propone. En la lamina 04 van ademas las dos alternativas de Makro que se
encontraron, la de menos fondo (Cleiton 0,55 -> paso 0,48) y la mas estrecha
(Polar slimline 0,45 de ancho pero 0,68 de fondo -> paso 0,35); ninguna
resuelve el problema, porque lo que lo causa es el fondo.

### Trasbarra nueva

Mesada corrida de 0,60 de fondo en toda la pared entre P1 y P2 (2,75). Encima,
de P1 hacia P2: cafetera de 1,00, hueco de 0,20 para el molinillo y los
utensilios, la maquina de crema fria de cafe, 0,75 de hueco libre y, pegado a
P2, un fregadero de 0,60. Debajo: nada bajo el fregadero y la nevera inox de
1,04 bajo el hueco libre. Sobre los aparatos, estante mural corrido (dos
piezas de 1,25). La chopera pasa a la tabla de P2, con el barril debajo, y en
el mostrador solo queda la tablet de cobro. El exprimidor, el fabricador de
hielo, el lavamanos y la licuadora se quedan **sin sitio** con esta
distribucion: van listados aparte en la lamina 04 para que el cliente decida.

### Aire acondicionado (correccion del 20 set.)

**Hay una sola maquina**, no dos: el cliente lo corrige sobre las fotos. Es el
cassette de 4 vias que en ellas se ve como un cuadrado blanco con rejillas.

- Va **a la izquierda del pilar central mirando el plano al Norte**, es decir
  al Oeste de P3: panel de **0,84 x 0,84** centrado en (4,570 / 5,223), a la
  misma altura que P3 en Y y con 0,68 libres hasta su cara Oeste.
- Va **empotrado en el techo de planta baja, que es el suelo del altillo**. El
  panel enrasa con el intrados del forjado (2,310) y el chasis sube dentro
  del canto del forjado, de 2,310 a 2,510. No queda ningun descuelgue.
- El chasis es de 0,57 x 0,57 x 0,20, asi que **quedan 0,050 de forjado por
  encima**: no asoma en el suelo del altillo. El rebaje hay que dejarlo al
  hormigonar; va anotado en CONFLICTOS de la cabecera del `.rb`.

La posicion sale de las fotos y queda por medir en obra.

## Comprobar en obra

Las dos laminas llevan al pie un bloque **COMPROBAR EN OBRA** con los puntos
en los que los videos del local grabados en obra no cuadran con el
levantamiento, o que el levantamiento no recoge (retranqueo entre el ventanal
y el escaparate, frente real a la calle, puerta de acceso, chapados de piedra,
alturas de coronacion, puntos de luz). Se dibuja siempre el levantamiento por
ser la unica fuente acotada; esos puntos se miden en obra y se corrigen sobre
el papel.

## Modelo 3D para SketchUp

`MODELO_3D.rb` construye el local entero en SketchUp desde la consola Ruby:

```ruby
load "C:/ruta/al/repo/docs/planos/MODELO_3D.rb"
```

Tambien se puede pegar el fichero entero en la consola. Se construye al
cargarlo; `Local3D.build` lo rehace y `Local3D.clear` lo borra. Volver a
cargarlo no duplica geometria: borra el grupo anterior antes de montar.

- **Unidades**: metros. Cada numero va con `.m`, asi que el modelo sale a
  milimetro exacto sobre las cotas del plano.
- **Origen**: esquina interior Suroeste del local (0,0,0), X al Este, Y al
  Norte, Z hacia arriba. Es el mismo origen de obra que usan las laminas.
- **Organizacion**: cada solido es un grupo con nombre propio, dentro de un
  grupo raiz "Local de hosteleria", repartidos en 15 capas (01 Solera,
  02 Muros, 03 Pilares, 04 Carpinteria, 05 Pared en L, 06 Zocalo, 07 Bano,
  08 Escalera, 09 Forjado, 10 Cocina, 11 Barra, 12 Sala, 13 Instalaciones,
  14 Planta alta, 15 Techo). La capa del techo se crea apagada.
- **De donde sale**: lo genera `export_sketchup.py` importando `estructura.py`,
  `mobiliario.py` y `equipamiento.py`, las mismas fuentes que dibujan las
  cuatro laminas. **Ninguna coordenada esta escrita a mano**: si cambia el
  plano, se vuelve a lanzar el generador y el 3D cambia con el.

En planta esta todo medido. En altura el levantamiento solo da el suelo a
suelo (2,560), asi que el resto de cotas verticales van declaradas una sola
vez en la cabecera del `.rb`, cada una con su origen (medida, estandar o
SUPUESTA). Las supuestas son el canto del forjado (0,250), el intrados de la
viga P1b (2,100), el alto del zocalo del ventanal (0,130) y el sillon.

**Aire acondicionado.** **Una sola maquina** (el cliente corrige el 20 set.
que solo hay una, no dos): un cassette de 4 vias, el cuadrado blanco con
rejillas de sus fotos. Va **a la izquierda del pilar central mirando el plano
al Norte**, es decir al Oeste de P3, a su misma altura en Y: panel de
**0,84 x 0,84** entre x 4,150-4,990 e y 4,803-5,643, con 0,680 libres hasta la
cara Oeste de P3. Es la misma medida que lleva la lamina 01, asi que plano y
3D coinciden.

Va **empotrado en el techo de planta baja, que es el suelo del altillo**, como
pide el cliente. El panel enrasa con el intrados del forjado: cara vista en
2,280-2,310, con la rejilla de retorno de 0,45 y las cuatro lamas de 0,09
asomando 0,015 por debajo. El chasis (0,57 x 0,57 x 0,20) sube **dentro** del
canto del forjado, de 2,310 a 2,510. Ni descuelga bajo el techo ni **asoma en
el suelo del altillo**: quedan 0,050 de forjado por encima.

En obra hay que dejar ese rebaje de 0,200 en un forjado de 0,250 y revisarlo
con el calculista; queda anotado en CONFLICTOS del `.rb`.

**Pared en L.** El vidrio va solo sobre el tramo largo. Sobre la base de la L
(el doblez de 0,74) no hay vidrio: ese hueco queda libre.

**Sillas.** El respaldo se pone contra el **borde** de la mesa junto al que
esta la silla, no contra el centro de la mesa. Mirando al centro, en una mesa
larga el vector apunta en diagonal y las sillas de los extremos salian giradas
90 grados: se veia en C1, la mesa de cowork de planta alta. Las mesas redondas
siguen con el criterio radial, que ahi si es el bueno.

**Pared de la caja de escalera.** El tabique que cierra la escalera por el
Oeste (x 8,650-8,811) **no es un rectangulo**: su coronacion **acompana la
subida de la escalera**. Arranca en 1,209 sobre el primer peldano, sube con la
misma pendiente que la escalera —un peldano de 0,2599 de huella por 0,1506 de
tabica— manteniendose 1,00 por encima de la linea de mamperlanes, y al llegar
a y=5,840 alcanza el intrados del forjado (2,310) y sigue recta hasta el
desembarco. Se genera como poligono en el plano Y-Z extruido en X, no como
caja, para que el corte sea exacto.

**Frente de la barra.** El mostrador lleva en su cara Este —la que ve el
cliente, y en toda su longitud— un revestimiento de madera de 0,03, con un
retranqueo de 0,05 en la parte baja para la tira de LED. Es donde iran el
logo y las luces. Se resuelve como los ultimos 3 cm del propio mostrador, asi
que la cara acabada sigue cayendo en 2,530, en la linea de la pared en L, y
el mostrador no crece.

**Conflictos que el 3D deja a la vista.** Son del proyecto, no del modelo, y
por eso no se arreglan inventando: van listados en la cabecera del `.rb`. Los
importantes: el vidrio de la pared en L corona en 2,570 y el forjado arranca
en 2,310 (ya estaba en COMPROBAR); la viga P1b muere en el aire al haberse
movido la pared en L a y=5,357; el lavavajillas K6 es mas alto y mas hondo que
el fregadero K7 bajo el que va; el lavavasos B1 (0,670) no cabe en el hueco de
0,600 de la vitrina; las vitrinas de 0,70 vuelan sobre un mostrador de 0,63; y
el machon P4 deja la escalera en 0,878 de ancho libre en vez de 1,079; y el
cuerpo del aire AC1, al ir empotrado como pide el cliente, ocupa el canto
entero del forjado.

`MODELO_3D_vista.png` y `MODELO_3D_vista_alta.png` son dos axonometrias de
control, con los muros cortados para ver cada planta por dentro. Las genera
`vista_3d.py` leyendo el mismo generador (no son renders, son un dibujo de
comprobacion):

```bash
python3 vista_3d.py 1.60 MODELO_3D_vista.png             # planta baja
PLANTA=alta python3 vista_3d.py 1.20 MODELO_3D_vista_alta.png
```

## Regenerar

```bash
python3 build_equipamiento.py   # genera las cuatro laminas y los dos PDF
```

Necesita `cairosvg` y `pymupdf`. `build_planos.py` por si solo genera
unicamente las dos laminas de estructura.

- `estructura.py` — todas las cotas en metros, una unica fuente de verdad.
- `dibujo.py` — lienzo SVG en milimetros de papel, cotas y tramas.
- `build_planos.py` — montaje de las dos laminas de estructura.
- `equipamiento.py` — anchos y fondos de los muebles y aparatos.
- `build_equipamiento.py` — lamina 03 a 1:25 y union de los PDF.
- `lista_makro.py` — genera `LISTA_MAKRO.md` y aporta los textos de la
  lamina 04 (ubicaciones, titulos de ficha, elementos a medida).
- `makro_fichas.py` — descarga las fichas de Makro desde un PC normal.

## Equipamiento (laminas 03 y 04)

Dos detalles a 1:25 en la misma hoja, cada uno con su origen de obra y
recortado a su caja de papel. Cada aparato es un producto real de makro.es
(`equipamiento.py`, enlaces en `LISTA_MAKRO.md`); las dos vitrinas y la
cafetera ya estan compradas y llevan las medidas del cliente.

- **Cocina.** Linea de coccion en la medianera Norte sobre una bancada a
  medida de **2,18 x 0,60 metida en el hundimiento**, bajo la campana corrida
  de 2,00 x 1,20: placa de induccion, cocedor de pasta, freidora y plancha
  (K1 a K4). Muro Oeste de Norte a Sur: horno de conveccion, fregadero de
  1,20 con hueco de lavavajillas (cuba al Sur, escurridor al Norte con el
  lavavajillas debajo) y dos armarios frigorificos verticales inox hasta P1
  (3,04 en 3,33). Pared en L: mesa refrigerada de una sola pieza de
  2,54 x 0,60 usada como mesada, pegada al doblez, con 0,33 libres junto a la
  bancada de coccion. **Pasillo de 0,84 a 0,98**; entrada bajo la viga P1b.
- **Barra.** Trasbarra de **2,75 contra el muro Oeste con mesada corrida de
  0,60**, de P1 a P2: cafetera de 1,00, hueco de 0,20 para molinillo y
  utensilios, maquina de crema fria de cafe de 0,20, **0,75 de hueco libre**
  y, pegado a P2, un fregadero de pie de 0,60. Debajo: nada bajo el fregadero
  y la nevera inox de 1,04 bajo el hueco libre. Estante mural corrido de 2,50
  (dos piezas de 1,25) sobre los aparatos. Mostrador delantero de
  **2,79 x 0,63** en la linea de la pared en L: dos vitrinas de 1,00 x 0,70
  con el motor de 0,30 x 0,30 abajo a la izquierda y el lavavasos bajo la
  vitrina junto a P2; barra de madera de 0,79 con **solo la tablet de cobro**;
  tabla de P2 al muro con la chopera encima y el barril debajo. Paso de
  servicio de 1,05.
- **Sala.** Nevera expositora de bebidas A7 (0,54 x 0,58 x 1,92) contra la
  cara Sur de P3. Ver el apartado de la revision del 19 set. para lo que le
  hace al paso.
