#!/usr/bin/env bash
# Reproduce todo el proyecto de punta a punta.
# Los pasos 1-3 necesitan el Excel original en data/raw/ (no se distribuye por
# privacidad). Los pasos 4-5 corren sobre el CSV ya anonimizado que SÍ está en
# el repo (data/processed/ventas.csv), así que cualquiera puede regenerar el
# análisis y los gráficos sin la fuente.
set -euo pipefail
cd "$(dirname "$0")"

RAW="data/raw/1.Base de Datos Clientes 2017.xlsx"

if [[ -f "$RAW" ]]; then
  echo "== 1/6  Limpieza del Excel        =="; python3 src/limpieza_clientes.py
  echo "== 2/6  Datos sintéticos          =="; python3 src/generar_sinteticos.py
  echo "== 3/6  Integración + id_cliente  =="; python3 src/integrar_database.py
  echo "== 4/6  Anonimización             =="; python3 src/anonimizar.py
  cp src/salida/analisis_base_2024.md docs/datos_sinteticos_2024.md
else
  echo "!! Sin $RAW  -> se omiten los pasos 1-4 (limpieza/anonimización)."
  echo "   Se regenera solo el análisis sobre data/processed/ventas.csv."
fi

echo "== 5/6  Análisis + gráficos       =="; python3 src/analisis.py
echo "== 6/6  Tablero HTML              =="; python3 src/dashboard.py
echo "listo. Gráficos en reports/figuras/, tablero en dashboard/index.html"
