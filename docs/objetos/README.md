# Biblioteca de objetos 1:1 para el render final

Cada aparato del local (los de Makro y los que ya tiene el cliente) se
modela en Blender/Cycles a escala 1:1, con materiales PBR, y se guarda como
un `.blend` autocontenido listo para enlazar en la escena del render final.

## Convenciones

- **Unidades**: metros. Las medidas salen de `../planos/equipamiento.py`
  (ancho × fondo × alto), que es la única fuente de verdad. El verificador
  de `lib.comprobar_medidas` para la construcción si la caja envolvente se
  desvía más de 1,5 mm o si el origen no está donde debe.
- **Origen**: centro de la huella, `z = 0` en la base (el aparato apoya en
  z = 0, sea suelo o encimera). **Frente hacia −Y**, ancho en X, fondo en Y,
  alto en Z. Para colocarlo en el local basta con mover y girar su Empty.
- **Estructura**: una colección `<TAG>` con un Empty raíz `<TAG>` (lleva
  como propiedades el nombre, las medidas y el enlace de Makro) y todas las
  piezas como mallas hijas con nombre propio.
- **Materiales**: procedurales (inox cepillado anisótropo, inox satinado,
  inox pulido, cromo, aluminio, chapa lacada, plástico, goma, vidrio,
  policarbonato, LED). No dependen de texturas externas; las calcas
  (serigrafía, pantallas, logos) van como PNG empaquetados en el `.blend`.
- **Piezas comunes** (`partes.py`): patas regulables, pies de goma,
  tiradores de barra y embutidos, mandos, botones, pilotos, rejillas de
  lamas y perforadas, cubas, grifos, bisagras, juntas, petos, cables,
  parrillas.
- **Salida**: `blend/<TAG>.blend` (comprimido, texturas empaquetadas, sin
  plató) y `preview/<TAG>.png` (hoja de 4 vistas: 3/4, frente, lateral,
  trasera) + `preview/<TAG>_34.png`.

## Uso

```bash
python3 construir.py K1              # medidas + 4 vistas + blend
python3 construir.py K1 --rapido     # una vista pequeña, para iterar
python3 construir.py K1 --sin-render # solo medidas + blend
python3 construir.py todos
```

Cada objeto vive en `obj_<TAG>.py` con una función `build()`; el lanzador
pone el documento nuevo, la raíz, el control de medidas, el plató (HDRI de
estudio de Polyhaven + tres luces de área + ciclorama), el render y el
guardado. El plató no viaja en el `.blend` del objeto.

Necesita el módulo `bpy` (Blender 5.0), `Pillow` y el HDRI
`studio_small_09_2k.hdr` de Polyhaven en `$OBJ_SCRATCH/ph/` (solo para las
vistas de control; sin él el plató usa un fondo gris).

## Referencias

Makro bloquea el acceso desde servidores, así que cada producto se
documentó con fotos y fichas de las webs del fabricante o de distribuidores
(carpeta de trabajo, no se sube al repositorio). Lo que no se pudo confirmar
está anotado en la cabecera de cada `obj_<TAG>.py`.
