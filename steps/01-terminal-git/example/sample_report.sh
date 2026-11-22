#!/usr/bin/env bash
# Ejemplo resuelto para el Paso 1.
# Lee el CSV de productos y muestra un resumen por categoría principal.
# Uso: ./sample_report.sh data/products.csv

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Uso: $0 <ruta-al-products.csv>" >&2
  exit 1
fi

INPUT_FILE="$1"

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "Error: el archivo '$INPUT_FILE' no existe." >&2
  exit 1
fi

# Columnas: sku,name,category,price_cents,stock. NR > 1 salta el encabezado.
TOTAL_PRODUCTS=$(awk -F',' 'NR > 1 { n++ } END { print n + 0 }' "$INPUT_FILE")
TOTAL_STOCK=$(awk -F',' '{ sub(/\r$/, "") } NR > 1 && $5 ~ /^[0-9]+$/ { s += $5 } END { print s + 0 }' "$INPUT_FILE")

echo "Resumen de catálogo ($INPUT_FILE)"
echo "Productos registrados = $TOTAL_PRODUCTS"
echo "Unidades en stock = $TOTAL_STOCK"
echo ""
echo "Conteo por categoría principal"

# split() corta "ropa/hombre/camisas" y se queda con "ropa".
awk -F',' 'NR > 1 && $3 != "" { split($3, parts, "/"); print parts[1] }' "$INPUT_FILE" \
  | sort | uniq -c | sort -rn
