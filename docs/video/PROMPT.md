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

## Fotogramas clave (16:9 · 1664x936 · sin rótulos)

| Beat del vuelo | Archivo | Estado |
|---|---|---|
| 1 · Exterior soleado en la entrada | `fpv_01_*.jpg` | pendiente |
| 2 · Cruzando la puerta, el interior se abre | `fpv_02_puerta_interior.jpg` | listo |
| 3 · Serpenteando entre las mesas | `fpv_03_entre_mesas.jpg` | listo |
| 4 · Rozando la barra y la cafetera | `fpv_04_*.jpg` | pendiente |
| 5 · Subiendo hacia las lámparas | `fpv_05_*.jpg` | pendiente |
| 6 · Plano general del café | `fpv_05_vista_general.jpg` | listo (renumerar al completar) |

## Uso sugerido

- **Kling / Runway / Luma con keyframes**: cargar los fotogramas en orden de
  vuelo como frames inicial/finales de cada tramo (1→2, 2→3, …) y generar los
  tramos con el prompt; montar los clips seguidos.
- El vapor, el latte art y el movimiento de las personas los aporta el
  generador desde el prompt: los fotogramas fijan geometría, luz y encuadre.
