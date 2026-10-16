#!/bin/bash
# Overnight Signals sweep — 2026-09-02. Every Signals bot, serially (one tester line), each bot
# retried until a USABLE call lands or the wave budget runs out. Logs per bot under logs/.
cd "/Users/parthbansal/EkStep/Prompt Tuner"
TESTER=f60e0899-aa3a-4be7-9b4f-0296bd28ef48
DID=7946350285
OUT=raya/overnight/logs
mkdir -p "$OUT"
WAVES=${WAVES:-4}

run () {  # 1=label 2=uuid 3=args-path 4=persona 5=lang
  python3 scripts/raya_testcall.py lang "$TESTER" "$5" > /dev/null 2>&1
  python3 scripts/raya_testcall.py persona "$TESTER" "raya/personas/$4" > /dev/null 2>&1
  sleep 4
  for w in $(seq 1 "$WAVES"); do
    echo "[$(date +%H:%M:%S)] $1 wave $w"
    python3 -u scripts/raya_testrun.py "$2" "$DID" "$3" "$TESTER" "$1" > "$OUT/$1.log" 2>&1
    D=$(grep -oE "outcome=Completed dur=[0-9]+" "$OUT/$1.log" | grep -oE "[0-9]+$" | head -1)
    T=$(grep -c "^\[assistant\]" "$OUT/$1.log")
    if [ -n "$D" ] && [ "$D" -ge 55 ] && [ "$T" -ge 5 ]; then
      U=$(grep -oE "BOT [0-9a-f-]{36}" "$OUT/$1.log" | head -1 | cut -d' ' -f2)
      echo "[$(date +%H:%M:%S)] PASS-USABLE $1 dur=${D}s turns=$T call=$U"
      echo "$1 USABLE ${D}s $T $U" >> raya/overnight/RESULTS.txt
      return 0
    fi
    echo "[$(date +%H:%M:%S)] $1 wave $w unusable (dur=${D:-none} turns=$T)"
  done
  echo "[$(date +%H:%M:%S)] NO-USABLE-CALL $1"
  echo "$1 NO-CALL - - -" >> raya/overnight/RESULTS.txt
}

echo "=== overnight sweep start $(date +%H:%M:%S) ==="
run kn-signals      33037201-78ce-405d-b509-a3b6934e20f1 raya/testcases/args/r3/kn-signals-repro.json      kn-minimal-caller.md kn
run trrain-hi       cf39a59a-3b24-4842-ba03-4248ec245aa1 raya/testcases/args/r3/trrain-hi.json             hi-trrain-accepts.md hi
run trrain-kn       dfeda883-3d2d-4a74-a0b5-1a47fdde2282 raya/testcases/args/r3/trrain-kn.json             kn-trrain-accept-then-asks.md kn
run maya-hi         904f333f-1919-4523-a51d-b22ba382dd22 raya/testcases/args/r3/khushboo-repro.json        hi-minimal-caller.md hi
run maya-hi-in      1c24feda-a584-4012-a865-fa8f950089df raya/testcases/args/r3/inbound-probe.json         hi-minimal-caller.md hi
run dkb-hi          fabda71d-af75-4ddd-8cf1-fa35c827f753 raya/testcases/args/r3/dkb-new-provider.json      hi-employer-cooperative.md hi
run dkb-kn          847a85e2-c5c8-4727-9918-f1db9efad05d raya/testcases/args/r3/dkb-kn-new-provider.json   kn-employer-cooperative.md kn
run kkb-hi-signals  115b38a5-42ef-4082-be69-84a871bb226a raya/testcases/args/r3/khushboo-repro.json        hi-minimal-caller.md hi
run kkb-hi-in       3f521174-574d-43ca-a9be-081849373c18 raya/testcases/args/r3/inbound-probe.json         hi-minimal-caller.md hi
run kkb-kn-in       f38da775-c572-4a50-9340-fe1f42c43901 raya/testcases/args/r3/inbound-probe.json         kn-minimal-caller.md kn
echo "=== overnight sweep done $(date +%H:%M:%S) ==="
cat raya/overnight/RESULTS.txt
