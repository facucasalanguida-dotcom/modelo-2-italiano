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
| `Planos_Estructura.pdf` | Los dos planos en un solo documento |

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

## Regenerar

```bash
python3 build_planos.py      # necesita cairosvg y pymupdf
```

- `estructura.py` — todas las cotas en metros, una unica fuente de verdad.
- `dibujo.py` — lienzo SVG en milimetros de papel, cotas y tramas.
- `build_planos.py` — montaje de las dos laminas y exportacion a PDF y PNG.
