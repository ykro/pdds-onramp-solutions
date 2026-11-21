#!/usr/bin/env bash
# Ejemplo resuelto para el Paso 1.
# Lee un archivo JSON de productos y muestra un resumen limpio por categoría.
# Uso: ./sample_report.sh data/products.json

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Uso: $0 <ruta-al-products.json>" >&2
  exit 1
fi

INPUT_FILE="$1"

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "Error: el archivo '$INPUT_FILE' no existe." >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq no está instalado en el entorno." >&2
  exit 1
fi

TOTAL_PRODUCTS=$(jq 'length' "$INPUT_FILE")
TOTAL_STOCK=$(jq '[.[].stock // 0] | add // 0' "$INPUT_FILE")

echo "Resumen de catálogo ($INPUT_FILE)"
echo "Productos registrados = $TOTAL_PRODUCTS"
echo "Unidades en stock = $TOTAL_STOCK"
echo ""
echo "Conteo por categoría"

jq -r '
  group_by(.category)
  | map({category: .[0].category, count: length})
  | sort_by(.category)
  | .[]
  | "\(.category)\t\(.count)"
' "$INPUT_FILE"
