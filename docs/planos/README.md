# Planos de estructura del local

Planos tecnicos en A3 a escala 1:50, pensados para imprimir y acotar a mano
sobre ellos. Se dibuja **solo la estructura**: muros, medianeras, pilares y
machones, viga descolgada, forjado del altillo, escalera, carpinteria de
fachada y puntos de luz del techo. No hay mobiliario, barra, cocina ni
equipamiento.

| Archivo | Contenido |
|---|---|
| `PLANTA_BAJA.pdf` | Planta baja, cota ±0,00 |
| `PLANTA_ALTA.pdf` | Altillo, cota +3,00 |
| `EQUIPAMIENTO.pdf` | Barra y cocina a 1:25, con el cuadro de equipos |
| `Planos_Estructura.pdf` | Las dos plantas en un solo documento |
| `Planos_Completos.pdf` | Las tres laminas en un solo documento |

## Sistema de coordenadas

```
X = 0,000    cara exterior del muro OESTE
X = 10,040   cara exterior de la medianera ESTE
Y = 0,000    punto mas al sur del solar (cara sur del pilar de fachada)
Y = 9,156    cara exterior de la medianera NORTE
Z = 0,000    pavimento de planta baja
Z = +3,000   pavimento del altillo
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
  puertas, 2,54 x 0,60 x 0,85; ninguna ficha pasa de 2,545); quedan 0,42
  libres junto al doblez. La tabla sobre el lavavajillas se dibuja maciza.
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
  escalera y la otra pasa a diametro 1,20 con cuatro sillas en diagonal,
  colocada para no estrechar los pasos: 1,09 al Norte hacia el aseo y el
  almacen, 0,53 junto a P3 y junto a la caja de escalera, 0,79 hasta la
  barandilla Sur. La mesa de cowork baja 0,20 y se corre 0,10 al Oeste
  (1,01 de paso al Norte, 0,59 hasta P3, 0,42 hasta la barandilla Oeste).
  Todos los pasos libres se acotan en azul en la lamina 02 (`PASOS_PA` en
  `mobiliario.py`, dibujados por `cotas_paso`). 12 puestos.
- **Lamina 04** (`LISTA_EQUIPAMIENTO`): toda la maquinaria con medidas, sitio
  en el plano y la ficha de makro.es, con los enlaces clicables en el PDF
  (anotaciones anadidas con pymupdf tras exportar el SVG; cairosvg no las
  genera). Las cuatro laminas van en `Planos_Completos.pdf`.

## Comprobar en obra

Las dos laminas llevan al pie un bloque **COMPROBAR EN OBRA** con los puntos
en los que los videos del local grabados en obra no cuadran con el
levantamiento, o que el levantamiento no recoge (retranqueo entre el ventanal
y el escaparate, frente real a la calle, puerta de acceso, chapados de piedra,
alturas de coronacion, puntos de luz). Se dibuja siempre el levantamiento por
ser la unica fuente acotada; esos puntos se miden en obra y se corrigen sobre
el papel.

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
  medida de 2,12 x 0,60, bajo la campana corrida de 2,00 x 1,20: placa de
  induccion, cocedor de pasta, freidora y plancha (K1 a K4). Muro Oeste de
  Norte a Sur: horno de conveccion, lavavajillas bajo una tabla de madera que
  enlaza con el fregadero, fregadero y dos armarios frigorificos verticales
  inox hasta P1 (3,01 en 3,05). Pared en L: mesa refrigerada de una sola
  pieza de 2,54 x 0,60 usada como mesada, con 0,42 libres junto al doblez.
  Pasillo de 0,78 a 0,92; entrada de 1,18 bajo la viga P1b.
- **Barra.** Trasbarra de 2,75 contra el muro Oeste bajo una unica encimera:
  cafetera de 1,20 x 0,60 sobre el modulo tecnico de 0,60 (Norte), lavamanos,
  hielera con la licuadora encima y exprimidor (Sur). Mostrador delantero de
  3,19 en la linea de la pared en L: dos vitrinas de 1,00 x 0,70 con el motor
  de 0,30 x 0,30 abajo a la izquierda, lavavasos bajo la vitrina junto a P2 y
  barriles bajo la otra; barra de madera de 1,19 con la tablet al Norte y la
  columna de cerveza al Sur; tabla de P2 al muro. Paso de servicio de 1,02.
