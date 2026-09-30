# Carteles de Casa Margot

Los cinco carteles de referencia que mando el cliente el 30 set. 2026,
adaptados con el logo horizontal de Casa Margot sobre fondo azzurro
(#12A0D7, Pantone 2995 C), cada uno en los seis acabados del logo de su hoja
de ideas.

| Clave | Cartel | Referencia |
|---|---|---|
| `ovalo` | Ovalo en bandera: marco y fondo azzurro, logo en relieve de 2 cm, pletina a la pared | G's |
| `caja` | Caja de luz en bandera: metacrilato azzurro iluminado, logo en el costado y en la testa | Кицуня |
| `placa` | Placa cuadrada en bandera: dos caras azzurro con el canto retroiluminado | Aesop |
| `colgado` | Caja de luz alargada, colgada de un soporte en un pilar | Jam |
| `barra` | Barra azzurro separada 2 cm de la pared, logo calado con luz y halo arriba y abajo | Watanabe |

Acabados, en el orden de la hoja de ideas: blanco, marmol blanco con vetas de
oro, negro, marmol negro, oro y marmol rosa. En los carteles con luz, el logo
blanco va iluminado (calado o impreso en la caja de luz); los demas son
opacos.

## Como se genera

```
python3 carteles.py [--carteles ovalo,caja] [--acabados blanco,oro]
                    [--spp 48] [--ancho 900] [--salida DIR]
```

Sale un PNG por cartel y acabado (`<cartel>_<acabado>.png`) y una hoja por
cartel con las seis opciones (`<cartel>_opciones.jpg`).

- **Logo**: el PDF vectorial `docs/pared/CASA_MARGOT_LOGO_NERO.pdf` se pasa a
  SVG y Blender lo importa como curvas; el relieve y el calado son el logo
  exacto, sin redibujar.
- **Marmoles**: las tres muestras de la hoja de ideas del cliente. No se
  versionan; se buscan en `$CM_SCRATCH/carteles/texturas/marmol_blanco.jpg`,
  `marmol_negro.jpg` y `marmol_rosa.jpg`.
- **Paredes**: texturas CC0 de Poly Haven (`painted_brick`, `red_brick_03`,
  `plaster_grey_04`, `plastered_wall`) en las carpetas de la escena del
  local; el panel de listones es procedural.
- **Color**: vista *Khronos PBR Neutral*, para que el azzurro salga como es.
  Con AgX las cajas de luz salian lavadas.
