#!/usr/bin/env bash
# Fleet happy-path sweep: one live call per conversation target.
# Sets the tester persona, dials, waits for a terminal outcome, logs one TSV row.
# Retries once when the tester leg never answers (0 turns) -- bridge contention is common.
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1

TESTER=f60e0899-aa3a-4be7-9b4f-0296bd28ef48
DID=7946350285
OUT="${SWEEP_OUT:-raya/regression/sweep-results.tsv}"
LOGDIR="${SWEEP_LOGS:-/private/tmp/claude-502/-Users-parthbansal-EkStep-Prompt-Tuner/cad28c14-40a4-477d-993b-eff663bfb052/scratchpad/sweep}"
mkdir -p "$LOGDIR"
[ -f "$OUT" ] || printf 'target\tbot_uuid\tpersona\tfixture\tcall\toutcome\tdur\tturns\n' > "$OUT"

# target | persona | fixture   (outbound targets only; inbound needs the reverse leg)
ROWS=(
"kkb-hi-signals|hi-loc-then-apply|sweep/kkb-hi-signals.json"
"kkb-kn-signals|kn-seeker-cooperative|sweep/kkb-kn-signals.json"
"kkb-hi-out|hi-seeker-cooperative-existing|sweep/kkb-hi-out.json"
"kkb-kn-out|kn-seeker-cooperative|sweep/kkb-kn-out.json"
"maya-hi-signals|hi-student-cooperative|sweep/maya-hi-signals.json"
"maya-hi-out|hi-student-cooperative|sweep/maya-hi-out.json"
"dkb-hi-signals|hi-employer-cooperative|sweep/dkb-hi-signals.json"
"dkb-kn-signals|kn-employer-cooperative|sweep/dkb-kn-signals.json"
"dkb-hi-out|hi-employer-cooperative|sweep/dkb-hi-out.json"
"dkb-kn-out|kn-employer-cooperative|sweep/dkb-kn-out.json"
"trrain-hi-out|hi-trrain-accepts|sweep/trrain-hi-out.json"
"trrain-kn-out|kn-trrain-accept-then-asks|sweep/trrain-kn-out.json"
"kkb-hi-signals-slim|hi-loc-then-apply|sweep/kkb-hi-signals.json"
# --- edge cases ---
"kkb-hi-signals|hi-force-apply|sweep/kkb-hi-signals-DUPAPPLY.json"
"kkb-hi-signals|hi-force-apply|r5/named-error-row2a.json"
"kkb-kn-signals|kn-force-apply|r5/named-error-row2a.json"
"kkb-hi-signals|hi-not-interested|sweep/kkb-hi-signals.json"
"kkb-hi-signals|hi-asks-for-all-jobs|sweep/kkb-hi-signals.json"
"kkb-hi-signals|hi-cannot-hear|sweep/kkb-hi-signals.json"
"kkb-kn-signals|kn-declines-each-set|sweep/kkb-kn-signals.json"
"kkb-hi-signals|hi-role-change-then-apply|sweep/kkb-hi-signals.json"
"maya-hi-signals|hi-student-probe|sweep/maya-hi-signals.json"
"dkb-hi-signals|hi-employer-probe|sweep/dkb-hi-signals.json"
"trrain-hi-out|hi-trrain-wrong-person|sweep/trrain-hi-out.json"
)

uuid_for() {
  python3 - "$1" <<'PY'
import json,sys
for t in json.load(open('raya/agents.json'))['targets']:
    if t['id']==sys.argv[1]:
        a=t.get('raya_agent_id') or {}
        print(a.get('prod') or ''); break
PY
}

for row in "${ROWS[@]}"; do
  IFS='|' read -r tgt persona fixture <<<"$row"
  bot=$(uuid_for "$tgt")
  if [ -z "$bot" ]; then echo "SKIP $tgt (no prod uuid)"; continue; fi
  pf="raya/personas/${persona}.md"
  if [ ! -f "$pf" ]; then echo "SKIP $tgt (no persona $pf)"; continue; fi
  fx="raya/testcases/args/${fixture}"
  if [ ! -f "$fx" ]; then echo "SKIP $tgt (no fixture $fx)"; continue; fi

  for attempt in 1 2; do
    python3 scripts/raya_testcall.py persona "$TESTER" "$pf" >/dev/null 2>&1
    L="$LOGDIR/${tgt}-a${attempt}.log"
    python3 -u scripts/raya_testrun.py "$bot" "$DID" "$fx" "$TESTER" "$tgt" > "$L" 2>&1
    line=$(grep -oE "TESTER leg [0-9a-f]{8}: outcome=[A-Za-z-]+ dur=[0-9]+ turns=[0-9]+" "$L" | tail -1)
    call=$(grep -oE "BOT [0-9a-f]{8}" "$L" | tail -1 | awk '{print $2}')
    outcome=$(sed -E 's/.*outcome=([A-Za-z-]+).*/\1/' <<<"$line")
    dur=$(sed -E 's/.*dur=([0-9]+).*/\1/' <<<"$line")
    turns=$(sed -E 's/.*turns=([0-9]+).*/\1/' <<<"$line")
    [ -z "${turns:-}" ] && turns=0
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$tgt" "${bot:0:8}" "$persona" "$fixture" "${call:-none}" "${outcome:-none}" "${dur:-0}" "$turns" >> "$OUT"
    echo "SWEEP $tgt call=${call:-none} turns=$turns attempt=$attempt"
    # a call that actually talked is done; 0 turns means the tester never answered
    [ "${turns:-0}" -gt 4 ] && break
  done
done
echo "SWEEP COMPLETE"
