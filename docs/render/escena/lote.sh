#!/bin/bash
# Renderiza las vistas una a una, cada una en su proceso: asi un fallo de
# memoria solo se lleva una vista y no el lote entero, y la memoria se
# devuelve al sistema entre vista y vista.
#
#   ./lote.sh SALIDA ANCHO ALTO SPP vista1 vista2 ...
SAL=${1:?salida}; W=${2:-2560}; H=${3:-1440}; SPP=${4:-96}; shift 4
cd "$(dirname "$0")"
mkdir -p "$SAL"
for v in "$@"; do
  if [ -f "$SAL/CM_$v.png" ]; then echo "[$v] ya estaba"; continue; fi
  echo "[$v] $(date +%H:%M:%S) render ${W}x${H} ${SPP}spp"
  t0=$SECONDS
  python3 escena.py --vista "$v" --spp "$SPP" --ancho "$W" --alto "$H" --salida "$SAL" \
      2>&1 | grep -viE "numpy|deprecat|cuew|^\s*$" | tail -4
  if [ ! -f "$SAL/CM_$v.png" ]; then
    # Se reintenta bajando muestras, no resolucion: si se baja la resolucion
    # la entrega sale con vistas de dos tamaños distintos y no casan.
    echo "[$v] fallo; reintento con $((SPP/2)) muestras a la misma resolucion"
    python3 escena.py --vista "$v" --spp $((SPP/2)) --ancho "$W" --alto "$H" \
        --salida "$SAL" 2>&1 | grep -viE "numpy|deprecat|cuew|^\s*$" | tail -3
  fi
  echo "[$v] $((SECONDS-t0)) s"
done
echo "LOTE TERMINADO $(date +%H:%M:%S)"
