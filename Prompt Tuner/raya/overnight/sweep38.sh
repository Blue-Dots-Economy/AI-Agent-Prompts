#!/bin/bash
# Verify the two families that had no post-fix call: DKB (write-tool narration guard) and Maya.
cd "/Users/parthbansal/EkStep/Prompt Tuner"
TESTER=f60e0899-aa3a-4be7-9b4f-0296bd28ef48
OUT=raya/overnight/logs
RES=raya/overnight/RESULTS39.txt
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
  done
  echo "$1 NO-CALL - - -" >> "$RES"
}
A=raya/testcases/args/signals-prod
run vfy-dkb-hi  fabda71d-af75-4ddd-8cf1-fa35c827f753 $A/dkb-hi-signals.json     hi-employer-cooperative.md hi
run vfy-maya-hi 904f333f-1919-4523-a51d-b22ba382dd22 $A/maya-hi-signals.json    hi-student-cooperative.md  hi
run vfy-dkb-kn  847a85e2-c5c8-4727-9918-f1db9efad05d $A/dkb-kn-signals.json     kn-employer-cooperative.md kn
run vfy-maya-in 1c24feda-a584-4012-a865-fa8f950089df $A/maya-hi-in-signals.json hi-student-cooperative.md  hi
cat "$RES"
