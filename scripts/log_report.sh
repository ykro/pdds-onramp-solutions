#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]] || [[ ! -f "$1" ]]; then
  echo "Error: log file not found: ${1:-<missing>}" >&2
  exit 1
fi

LOG_FILE="$1"

TOTAL_REQUESTS=$(wc -l < "$LOG_FILE" | tr -d ' ')
ERRORS_5XX=$(awk '$4 ~ /^5[0-9][0-9]$/ { count++ } END { print count + 0 }' "$LOG_FILE")
TOP_ENDPOINTS=$(awk '{ print $3 }' "$LOG_FILE" | sort | uniq -c | sort -nr | head -n 3 | awk '{ printf "%s:%s ", $2, $1 }' | sed 's/ $//')

echo "total_requests=${TOTAL_REQUESTS}"
echo "errors_5xx=${ERRORS_5XX}"
echo "top_endpoints=${TOP_ENDPOINTS}"
