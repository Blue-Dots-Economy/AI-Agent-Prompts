#!/bin/bash
# sanity-signals.sh — one happy-path call per Signals bot, all eight, on the tester DID only.
# Tier-3 style standing check. Never a real user's number (voice-test rule 0).
cd "/Users/parthbansal/EkStep/Prompt Tuner"
TESTER=f60e0899-aa3a-4be7-9b4f-0296bd28ef48
OUT=raya/overnight/logs
RES=raya/overnight/RESULTS-SANITY.txt
run () {
  python3 scripts/raya_testcall.py lang "$TESTER" "$5" > /dev/null 2>&1
  python3 scripts/raya_testcall.py persona "$TESTER" "raya/personas/$4" > /dev/null 2>&1
  sleep 4
  for w in 1 2 3; do
    echo "[$(date +%H:%M:%S)] $1 wave $w"
    python3 -u scripts/raya_testrun.py "$2" 7946350285 "$3" "$TESTER" "$1" > "$OUT/$1.log" 2>&1
    D=$(grep -oE "outcome=Completed dur=[0-9]+" "$OUT/$1.log" | grep -oE "[0-9]+$" | head -1)
    T=$(grep -c "^\[assistant\]" "$OUT/$1.log")
    if [ -n "$D" ] && [ "$D" -ge 55 ] && [ "$T" -ge 5 ]; then
      U=$(grep -oE "BOT [0-9a-f-]{36}" "$OUT/$1.log" | head -1 | cut -d' ' -f2)
      echo "[$(date +%H:%M:%S)] USABLE $1 dur=${D}s turns=$T call=$U"
      echo "$1 USABLE ${D}s $T $U" >> "$RES"; return 0
    fi
    echo "[$(date +%H:%M:%S)] $1 wave $w unusable (dur=${D:-none} turns=$T)"
  done
  echo "$1 NO-CALL - - -" >> "$RES"
}
A=raya/testcases/args/signals-prod
echo "=== signals sanity start $(date +%H:%M:%S) ==="
run san-kkb-hi     115b38a5-42ef-4082-be69-84a871bb226a $A/kkb-hi-signals.json     hi-seeker-cooperative-existing.md hi
run san-kkb-kn     33037201-78ce-405d-b509-a3b6934e20f1 $A/kkb-kn-signals.json     kn-seeker-cooperative.md          kn
run san-kkb-hi-in  3f521174-574d-43ca-a9be-081849373c18 $A/kkb-hi-in-signals.json  hi-minimal-caller.md              hi
run san-kkb-kn-in  f38da775-c572-4a50-9340-fe1f42c43901 $A/kkb-kn-in-signals.json  kn-minimal-caller.md              kn
run san-dkb-hi     fabda71d-af75-4ddd-8cf1-fa35c827f753 $A/dkb-hi-signals.json     hi-employer-cooperative.md        hi
run san-dkb-kn     847a85e2-c5c8-4727-9918-f1db9efad05d $A/dkb-kn-signals.json     kn-employer-cooperative.md        kn
run san-maya-hi    904f333f-1919-4523-a51d-b22ba382dd22 $A/maya-hi-signals.json    hi-student-cooperative.md         hi
run san-maya-hi-in 1c24feda-a584-4012-a865-fa8f950089df $A/maya-hi-in-signals.json hi-student-cooperative.md         hi
echo "=== signals sanity done $(date +%H:%M:%S) ==="
cat "$RES"
