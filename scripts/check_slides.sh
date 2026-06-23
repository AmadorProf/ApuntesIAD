#!/usr/bin/env bash
# Check slide count in all UD presentations.
# Usage: bash scripts/check_slides.sh [min_slides]
# Prints files with fewer than min_slides (default 18).

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
MIN="${1:-18}"

echo "Contando diapositivas en presentaciones UD (mínimo: $MIN)"
echo "------------------------------------------------------------"

PASS=0
FAIL=0

while IFS= read -r f; do
  # Count slide separators (lines that are exactly "---")
  count=$(grep -cE '^---$' "$f" 2>/dev/null || echo 0)
  rel="${f#$REPO/}"
  if [ "$count" -lt "$MIN" ]; then
    printf "  REVISAR (%2d diap.)  %s\n" "$count" "$rel"
    FAIL=$((FAIL+1))
  else
    PASS=$((PASS+1))
  fi
done < <(find "$REPO" -name "index.md" \
  -not -path "*/.github/*" \
  -not -path "*/.claude/*" \
  -not -path "*/node_modules/*" \
  | grep -E "UD[0-9]+" | sort)

echo "------------------------------------------------------------"
echo "OK: $PASS  |  Revisar: $FAIL"
