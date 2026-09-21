# Abrir Casa Margot en Blender

El fichero `CASA_MARGOT_revision.blend` es la escena entera: obra, los 24
aparatos a escala 1:1, mobiliario, luminarias, decoracion y la calle. Lleva
las texturas **empaquetadas dentro**, asi que no hay que descargar nada mas
ni colocar carpetas: se abre y ya esta.

## 1. Instalar Blender

Descargalo de la pagina oficial, nunca de un espejo:

    https://www.blender.org/download/

- **Windows**: baja el `.msi` (Windows Installer) y siguiente-siguiente. Si
  prefieres no instalar nada, baja el `.zip` (Portable), descomprimelo y
  ejecuta `blender.exe` de dentro.
- **Mac**: baja el `.dmg` y arrastra Blender a Aplicaciones. Ojo con elegir
  bien **Apple Silicon** (M1/M2/M3/M4) o **Intel**.

**Version: la 5.0 o posterior.** El fichero se genero con la 5.0.1. Una
version anterior lo abrira mal o no lo abrira.

Pide poco: cualquier portatil de los ultimos años lo mueve. Lo unico
exigente es el render, y para revisar no hace falta renderizar.

## 2. Abrirlo

Doble clic en el `.blend`, o dentro de Blender `File > Open` (Ctrl+O). Tarda
unos segundos en cargar porque son 5.293 objetos.

## 3. Moverse

| Que quieres | Como |
|---|---|
| Girar alrededor | Boton central del raton, arrastrando |
| Desplazarte | Mayusculas + boton central |
| Acercar / alejar | Rueda del raton |
| Volar en primera persona | Mayusculas + ` (tilde). W/A/S/D para andar, Q/E para subir y bajar. Clic para salir |
| Encuadrar lo seleccionado | Tecla `.` del teclado numerico |
| Ver por la camara | Tecla `0` del teclado numerico |

Si tu raton no tiene boton central: `Edit > Preferences > Input >` marca
**Emulate 3 Button Mouse**; entonces Alt + clic izquierdo gira.

## 4. Verlo como lo veo yo

Arriba a la derecha del visor hay cuatro bolitas. De izquierda a derecha:

1. **Wireframe** — solo aristas
2. **Solid** — gris, rapido, para mirar geometria
3. **Material Preview** — con materiales y texturas, **instantaneo**
4. **Rendered** — Cycles de verdad, igual que los renders que te mando

Para revisar usa la **3ª (Material Preview)**: se ve con sus materiales y
va fluida. La 4ª es la buena pero en CPU tarda, asi que dejala para mirar
un rincon concreto, no para pasearte.

## 5. Las 24 camaras

En el panel de la derecha (el *Outliner*) esta la coleccion **Camaras** con
las mismas vistas de los renders:

- `CAM general`, `CAM barra`, `CAM sala`, `CAM escaparate`, `CAM cocina`...
- `CAM fachada` y `CAM calle` (exteriores)
- `CAM alta`, `CAM alta_vacio`... (planta alta)
- `ORTO planta_baja`, `ORTO planta_alta`, `ORTO axonometrica`, `ORTO axono_alta`

Para mirar por una: **seleccionala en el Outliner** y pulsa
**Ctrl + `0` del teclado numerico**. Asi ves exactamente el encuadre del
render correspondiente.

## 6. Las colecciones

En el Outliner puedes apagar el ojo de cada coleccion para quitarla de en
medio:

| Coleccion | Que lleva |
|---|---|
| `Obra` | muros, forjados, escalera, carpinteria, puertas |
| `Planta alta` | todo lo del altillo |
| `Aparatos` | los 24 equipos de Makro, a escala 1:1 |
| `Mobiliario` | mesas y sillas |
| `Luces` | luminarias, led de peldaños, apliques |
| `Decoracion` | botellas, vajilla, cestas, plantas |
| `Ciudad` | la calle, la manzana de enfrente, el arbolado y los coches |
| `_moldes` | copias maestras de los objetos importados, **oculta a proposito** |

Apagar `Ciudad` va muy bien para moverte por dentro sin arrastrar seis
millones de triangulos.

## 7. Como mandarme las correcciones

Lo que mas me ayuda: **haz clic en la pieza** que este mal y dime **el
nombre que sale** en el Outliner o arriba a la izquierda del visor. Con el
nombre voy directo; con una descripcion tengo que adivinar cual es.

Si ademas abres el panel lateral con la tecla **N**, en la pestaña *Item*
salen su posicion y sus dimensiones exactas, que tambien me valen.

## 8. Dos avisos

- Las texturas de este fichero estan a **1K** para que pese 173 MB en vez
  de 741. Se ve perfectamente para revisar; los renders finales se generan
  aparte, con los mapas a 2K y el HDRI a 8K.
- Si tocas algo y lo guardas, **no me sirve de vuelta**: yo regenero la
  escena desde `docs/render/escena/escena.py`, que es el origen de todo.
  Dime los cambios y los hago ahi, que es lo que garantiza que se apliquen
  a las 24 vistas.
