# Café Napoli · Recorrido FPV — paquete de generación de vídeo

## Prompt (en inglés, tal como se usará)

> FPV drone shot smoothly flying through a cozy modern coffee shop. Starting
> outside at the sunlit entrance, gliding smoothly through the glass doorway
> into the interior. The camera seamlessly weaves between rustic wooden
> tables, lush indoor plants, and patrons enjoying their coffee. Moving close
> past the espresso bar, capturing steam rising from the coffee machine and a
> barista pouring latte art, before gently rising toward warm hanging lights
> for an overview of the full ambient café. Cinematic lighting,
> photorealistic, 8k resolution, fluid motion, shallow depth of field.

## Fotogramas clave, en orden de vuelo (16:9 · 1664x936 · sin rótulos)

| # | Beat del vuelo | Archivo |
|---|---|---|
| 1 | Entrando: la puerta queda atrás, la barra al fondo | `fpv_01_entrada.jpg` |
| 2 | Serpenteando entre las mesas hacia el escaparate | `fpv_02_entre_mesas.jpg` |
| 3 | Acercándose a la barra, vitrinas y estantería | `fpv_03_barra.jpg` |
| 4 | Rozando las vitrinas de cristal curvo con la bollería | `fpv_04_vitrinas.jpg` |
| 5 | Pasando ante la mampara con la cocina detrás | `fpv_05_cocina_mampara.jpg` |
| 6 | Elevándose bajo las lámparas: plano general del café | `fpv_06_vista_general.jpg` |

## Uso sugerido

- **Kling / Runway / Luma con keyframes**: generar cada tramo con el par de
  fotogramas inicial→final (1→2, 2→3, 3→4, 4→5, 5→6) y el prompt de arriba,
  y montar los cinco clips seguidos.
- El beat inicial exterior del prompt puede generarse desde el fotograma 1
  pidiendo al modelo un arranque en retroceso ("pull-back reveal") o
  simplemente empezar el vuelo ya dentro.
- El vapor, el latte art y el movimiento de las personas los aporta el
  generador desde el prompt: los fotogramas fijan geometría, luz y encuadre.
