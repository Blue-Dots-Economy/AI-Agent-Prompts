#!/usr/bin/env bash
# Grade every call a fleet sweep produced. Resolves the full uuid from the per-dial log
# (the results TSV keeps only an 8-char prefix) and runs grade_call.py on each.
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1
TSV="${1:-raya/regression/sweep-results.tsv}"
LOGDIR="${2:-/private/tmp/claude-502/-Users-parthbansal-EkStep-Prompt-Tuner/cad28c14-40a4-477d-993b-eff663bfb052/scratchpad/sweep}"
[ -f "$TSV" ] || { echo "no results yet: $TSV"; exit 0; }

pass=0; fail=0; thin=0; dead=0
while IFS=$'\t' read -r tgt uuid persona fixture call outcome dur turns; do
  [ "$tgt" = "target" ] && continue
  [ "${turns:-0}" -lt 5 ] && { echo "DEAD  $tgt / $persona  (turns=${turns:-0}, never connected)"; dead=$((dead+1)); continue; }
  # the logs collide when one target is dialled more than once in a pass, so ask Raya
  full=$(python3 raya/regression/resolve_uuid.py "$uuid" "$call" 2>/dev/null)
  [ -z "$full" ] && full=$(grep -ohE "BOT ${call}[0-9a-f-]{28}" "$LOGDIR"/*.log 2>/dev/null | head -1 | awk '{print $2}')
  if [ -z "$full" ]; then echo "?     $tgt / $persona  (uuid unresolved)"; continue; fi
  out=$(python3 raya/regression/grade_call.py "$full" 2>&1)
  head=$(printf '%s\n' "$out" | head -1)
  v=$(grep -oE '\b(PASS|FAIL|THIN)\b' <<<"$head" | head -1)
  printf '%-5s %-22s %-32s %s\n' "$v" "$tgt" "$persona" "$call"
  printf '%s\n' "$out" | tail -n +2 | sed 's/^/        /'
  case "$v" in PASS) pass=$((pass+1));; FAIL) fail=$((fail+1));; THIN) thin=$((thin+1));; esac
done < "$TSV"
echo ""
echo "GRADED: $pass pass · $fail fail · $thin thin (too many checks skipped) · $dead never connected"
[ "$fail" -gt 0 ] && exit 1 || exit 0
