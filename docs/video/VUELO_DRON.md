# Vuelo de dron por la planta baja — estado y cómo retomarlo

**Estado: PARADO** a petición del cliente (27/08), a la espera de una
reorganización de objetos del modelo prevista para el sábado.
El render se detuvo en 5 de 1800 fotogramas; no se conserva nada de esa
tanda porque el modelo va a cambiar.

## Qué hay hecho y sirve igual tras el cambio

- `ruta_dron.py` — trayectoria del dron (12 estaciones con interpolación
  Catmull-Rom y arranque/frenada suaves) **y el comprobador de colisiones**
  contra `solids.json`. Ejecutarlo imprime los pasos más justos del vuelo.
- `render_dron.py` — render reanudable: salta los fotogramas ya escritos,
  usa datos persistentes de Cycles (solo se mueve la cámara) y calcula en
  **orden de bisección progresiva**, de modo que en cualquier instante los
  fotogramas listos están repartidos por todo el vuelo y ya forma un vídeo
  completo, cada vez más fluido.
- `montar_video.py` — monta el MP4 con los fotogramas que haya, rellenando
  huecos con el fotograma válido más cercano, y aplica la misma gradación
  cálida que los renders de la galería (`postfx.py`).
- `previsualizacion_dron.mp4` — cómo queda la coreografía (validada por el
  cliente el 27/08).

## El recorrido

Entrada → ventanal → sala → cocina tras la mampara → barra de punta a punta
→ rodea el pilar central → baja por el lado este → sube al vacío de doble
altura para un plano final alto y abierto.

## Restricción de la sección (IMPORTANTE)

El forjado de la planta alta cubre **y ≥ 3,94 m a z = 2,70 m**, y el canto
del altillo arranca en z = 2,48. Solo se puede volar alto en la franja sur
(el vacío de doble altura). La ruta guardada respeta un máximo de 2,35 m
bajo el forjado y tiene **0,40 m de holgura mínima** con toda la geometría.

## Al retomar, en este orden

1. Reexportar `solids.json` desde el `.rb` ya reorganizado.
2. **Volver a pasar el comprobador de colisiones** (`python3 ruta_dron.py`):
   si los objetos se han movido, la trayectoria puede haber quedado dentro
   de algo. Ajustar estaciones hasta que la holgura mínima sea ≥ 0,35 m.
3. Lanzar el render y montar el vídeo:

```
setsid env NAP_OUT="$PWD/video60_frames" NAP_W=1280 NAP_H=720 \
  NAP_SMP=32 NAP_N=1800 python3 render_dron.py > video60.log 2>&1 &

python3 montar_video.py video60_frames 1800 vuelo_dron.mp4 60
```

## Coste medido (4 núcleos, sin GPU)

- **95 s por fotograma** a 1280×720 y 32 muestras.
- 1800 fotogramas (30 s a 60 fps) → **~47 h**. A 1920×1080 serían ~99 h.
- 32 muestras equivalen visualmente a 64 (solo el 1,66 % de los píxeles
  difieren de forma apreciable): no merece la pena subirlas.
- `imageio-ffmpeg` hay que instalarlo (`pip install imageio-ffmpeg`); el
  módulo `bpy` de pip no trae salida de vídeo, solo de imagen.
