#!/bin/bash
# Final round: DKB Kannada token fix + regression across the four main Signals bots.
cd "/Users/parthbansal/EkStep/Prompt Tuner"
TESTER=f60e0899-aa3a-4be7-9b4f-0296bd28ef48
OUT=raya/overnight/logs
run () {
  python3 scripts/raya_testcall.py lang "$TESTER" "$5" > /dev/null 2>&1
  python3 scripts/raya_testcall.py persona "$TESTER" "raya/personas/$4" > /dev/null 2>&1
  sleep 4
  for w in 1 2 3 4 5; do
    echo "[$(date +%H:%M:%S)] $1 wave $w"
    python3 -u scripts/raya_testrun.py "$2" 7946350285 "$3" "$TESTER" "$1" > "$OUT/$1.log" 2>&1
    D=$(grep -oE "outcome=Completed dur=[0-9]+" "$OUT/$1.log" | grep -oE "[0-9]+$" | head -1)
    T=$(grep -c "^\[assistant\]" "$OUT/$1.log")
    if [ -n "$D" ] && [ "$D" -ge 55 ] && [ "$T" -ge 5 ]; then
      U=$(grep -oE "BOT [0-9a-f-]{36}" "$OUT/$1.log" | head -1 | cut -d' ' -f2)
      echo "[$(date +%H:%M:%S)] PASS-USABLE $1 dur=${D}s turns=$T call=$U"
      echo "$1 USABLE ${D}s $T $U" >> raya/overnight/RESULTS6.txt; return 0
    fi
    echo "[$(date +%H:%M:%S)] $1 wave $w unusable (dur=${D:-none} turns=$T)"
  done
  echo "$1 NO-CALL - - -" >> raya/overnight/RESULTS6.txt
}
echo "=== final round start $(date +%H:%M:%S) ==="
run fin-dkb-kn 847a85e2-c5c8-4727-9918-f1db9efad05d raya/testcases/args/r3/dkb-kn-new-provider.json kn-employer-cooperative.md kn
run fin-maya   904f333f-1919-4523-a51d-b22ba382dd22 raya/testcases/args/r3/khushboo-repro.json      hi-minimal-caller.md hi
run fin-in-hi  3f521174-574d-43ca-a9be-081849373c18 raya/testcases/args/r3/inbound-probe.json       hi-minimal-caller.md hi
run fin-in-kn  f38da775-c572-4a50-9340-fe1f42c43901 raya/testcases/args/r3/inbound-probe.json       kn-minimal-caller.md kn
run fin-dkb-hi fabda71d-af75-4ddd-8cf1-fa35c827f753 raya/testcases/args/r3/dkb-new-provider.json    hi-employer-cooperative.md hi
echo "=== final round done $(date +%H:%M:%S) ==="
cat raya/overnight/RESULTS6.txt
