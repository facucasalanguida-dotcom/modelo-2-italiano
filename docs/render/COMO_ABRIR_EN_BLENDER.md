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


## 9. Renderizar en tu ordenador

Se puede, y en una maquina con tarjeta grafica es entre 5 y 10 veces mas
rapido que el contenedor donde se monto esto. Lo que manda **no es la RAM**:
alli hay 15 GB y no es el cuello de botella. Manda la **tarjeta**, y en su
defecto los nucleos de CPU: alli hay 4 nucleos y ninguna tarjeta.

**No hace falta que nadie te mande ningun fichero.** Todo lo que no cabe en
el repositorio -1,5 GB de texturas y modelos de Poly Haven, mas el coche- es
CC0 y se baja de su fuente con un script que si esta en el repositorio.

### 1. Preparar

    git clone <el repositorio>
    cd modelo-2-italiano/docs/render/escena
    pip install pymupdf pillow numpy          # solo para rehacer el logo

    export CM_SCRATCH=~/casa_margot_activos   # Windows: set CM_SCRATCH=...
    python3 preparar_activos.py

Baja los 34 activos de Poly Haven, el coche y rehace el vinilo del logo
desde el PDF del repositorio. Son 1,5 GB y tarda segun la linea. Es
idempotente: si se corta, se relanza y sigue donde iba.

### 2. Lanzar una vista

    blender --background --python escena.py -- \
        --vista alta --spp 96 --ancho 3840 --alto 2160 \
        --salida ./renders --gpu

`--gpu` enciende la tarjeta: prueba OptiX y CUDA (NVIDIA), HIP (AMD), Metal
(Mac) y oneAPI (Intel), y usa la primera que encuentre junto con la CPU. Al
arrancar imprime cual ha cogido:

    GPU: OPTIX -> NVIDIA GeForce RTX 5050

Si dice que no hay tarjeta que Cycles sepa usar, es el driver o la version
de Blender; renderiza igual, pero por CPU.

### 3. Las 15 de la serie, de una tirada

    ./lote.sh ./renders 3840 2160 96 \
        fachada logo escalera escaparate sillon trasbarra cocina barra \
        barra_frente chopera alta alta_cowork alta_vacio general entrada

`lote.sh` lanza un proceso por vista -si una se queda sin memoria se pierde
esa y no el lote entero-, se salta las que ya esten hechas y reintenta con
la mitad de muestras la que falle. Para pasarle `--gpu` hay que añadirlo a
la linea de `python3 escena.py` que hay dentro del script.

### 4. Sacar el .blend para abrirlo a mano

    blender --background --python escena.py -- \
        --vista general --spp 8 --ancho 640 --alto 360 \
        --guardar-blend CASA_MARGOT.blend --salida /tmp

Monta la escena, la guarda y hace un render minusculo para no esperar.

### Tres avisos

- **VRAM.** Las vistas de interior caben en 8 GB de sobra. `fachada` carga
  ademas la ciudad y un HDRI de 8K, y ahi 8 GB se quedan justos; si Cycles
  se queda sin memoria de tarjeta tira de la del sistema y se vuelve lento.
  Esa conviene lanzarla sin `--gpu`.
- **Un render a la vez.** Montar la escena se come casi 6 GB. Dos procesos
  a la vez en una maquina de 16 GB se matan entre ellos: pasa exactamente
  eso, el sistema mata uno y el lote lo reintenta con la mitad de muestras.
  `lote.sh` ya los encadena de uno en uno.
- **Las texturas van a 2K** salvo que pongas `CM_4K=1`. No es un recorte de
  calidad: a 3840x2160 no se distingue, porque la proyeccion de caja reparte
  cada mapa en tramos de 1,5 a 3 m. A 4K son ~120 mapas de 4096x4096 y el
  proceso pasa de 13 GB.
