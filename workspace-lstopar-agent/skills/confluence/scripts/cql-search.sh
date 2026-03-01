#!/usr/bin/env bash
# Confluence CQL Search
# Usage: cql-search.sh <cql-query> [--limit N] [--start N] [--expand fields]
#
# Examples:
#   cql-search.sh 'type=page AND space=DEV'
#   cql-search.sh 'text ~ "deployment guide"' --limit 5
#   cql-search.sh 'label = "architecture" AND type = page' --expand body.storage
#   cql-search.sh 'creator = currentUser() AND created > "2025-01-01"'

set -euo pipefail

CONFIG="${HOME}/.confluence-cli/config.json"
if [[ ! -f "$CONFIG" ]]; then
  echo "Error: Config not found at $CONFIG. Run 'confluence init' first." >&2
  exit 1
fi

DOMAIN=$(jq -r '.domain' "$CONFIG")
EMAIL=$(jq -r '.email' "$CONFIG")
TOKEN=$(jq -r '.token' "$CONFIG")

if [[ -z "$1" ]]; then
  echo "Usage: cql-search.sh <cql-query> [--limit N] [--start N] [--expand fields]" >&2
  exit 1
fi

CQL="$1"
shift

LIMIT=25
START=0
EXPAND=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit) LIMIT="$2"; shift 2 ;;
    --start) START="$2"; shift 2 ;;
    --expand) EXPAND="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

URL="https://${DOMAIN}/wiki/rest/api/search?cql=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''${CQL}'''))")&limit=${LIMIT}&start=${START}"

if [[ -n "$EXPAND" ]]; then
  URL="${URL}&expand=${EXPAND}"
fi

RESPONSE=$(curl -s -w "\n%{http_code}" \
  -u "${EMAIL}:${TOKEN}" \
  -H "Accept: application/json" \
  "$URL")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" != "200" ]]; then
  echo "Error: HTTP $HTTP_CODE" >&2
  echo "$BODY" >&2
  exit 1
fi

echo "$BODY" | jq '.'
