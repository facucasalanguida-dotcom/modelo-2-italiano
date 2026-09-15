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
python3 build_equipamiento.py   # genera las tres laminas y los dos PDF
```

Necesita `cairosvg` y `pymupdf`. `build_planos.py` por si solo genera
unicamente las dos laminas de estructura.

- `estructura.py` — todas las cotas en metros, una unica fuente de verdad.
- `dibujo.py` — lienzo SVG en milimetros de papel, cotas y tramas.
- `build_planos.py` — montaje de las dos laminas de estructura.
- `equipamiento.py` — anchos y fondos de los muebles y aparatos.
- `build_equipamiento.py` — lamina 03 a 1:25 y union de los PDF.

## Equipamiento (lamina 03)

Dos detalles a 1:25 en la misma hoja, cada uno con su origen de obra y
recortado a su caja de papel.

- **Barra.** Trasbarra contra el muro Oeste, 2,75 m de mueble corrido bajo
  una sola encimera: modulo tecnico de 0,60 bajo la cafetera, lavavajillas,
  fregadero, frigorifico bajo mostrador y cajonera. Encima, cafetera de 2
  grupos, fregadero pequeno, exprimidor y tirador de cerveza. En el
  mostrador delantero, vitrina expositora, caja y mostrador de servicio.
  Paso de servicio de 1,02 m.
- **Cocina.** Linea de coccion completa contra el muro Oeste bajo la campana
  (fuegos, cocedor de pasta, plancha y freidora). Fregadero en la medianera
  Norte. Lavavajillas, horno, mesa refrigerada y apoyo contra la pared en L,
  con encimera corrida de acero inoxidable. Pasillo de trabajo de 0,92 m.

Los anchos son de serie de hosteleria, no medidos sobre aparato: el cuadro
de equipamiento al pie de la lamina esta para sustituirlos por los del
equipo que se acabe eligiendo.
