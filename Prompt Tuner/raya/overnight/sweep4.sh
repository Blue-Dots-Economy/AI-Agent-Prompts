#!/bin/bash
cd "/Users/parthbansal/EkStep/Prompt Tuner"
TESTER=f60e0899-aa3a-4be7-9b4f-0296bd28ef48
OUT=raya/overnight/logs
run () {
  python3 scripts/raya_testcall.py lang "$TESTER" "$5" > /dev/null 2>&1
  python3 scripts/raya_testcall.py persona "$TESTER" "raya/personas/$4" > /dev/null 2>&1
  sleep 4
  for w in 1 2 3 4 5 6; do
    echo "[$(date +%H:%M:%S)] $1 wave $w"
    python3 -u scripts/raya_testrun.py "$2" 7946350285 "$3" "$TESTER" "$1" > "$OUT/$1.log" 2>&1
    D=$(grep -oE "outcome=Completed dur=[0-9]+" "$OUT/$1.log" | grep -oE "[0-9]+$" | head -1)
    T=$(grep -c "^\[assistant\]" "$OUT/$1.log")
    if [ -n "$D" ] && [ "$D" -ge 55 ] && [ "$T" -ge 5 ]; then
      U=$(grep -oE "BOT [0-9a-f-]{36}" "$OUT/$1.log" | head -1 | cut -d' ' -f2)
      echo "[$(date +%H:%M:%S)] PASS-USABLE $1 dur=${D}s turns=$T call=$U"
      echo "$1 USABLE ${D}s $T $U" >> raya/overnight/RESULTS4.txt; return 0
    fi
    echo "[$(date +%H:%M:%S)] $1 wave $w unusable (dur=${D:-none} turns=$T)"
  done
  echo "$1 NO-CALL - - -" >> raya/overnight/RESULTS4.txt
}
echo "=== round 4 start $(date +%H:%M:%S) ==="
run kn-precedence-r2 33037201-78ce-405d-b509-a3b6934e20f1 raya/testcases/args/r3/kn-signals-repro.json kn-minimal-caller.md kn
run hi-regression    115b38a5-42ef-4082-be69-84a871bb226a raya/testcases/args/r3/khushboo-repro.json   hi-minimal-caller.md hi
run kn-precedence-r3 33037201-78ce-405d-b509-a3b6934e20f1 raya/testcases/args/r3/kn-signals-repro.json kn-minimal-caller.md kn
echo "=== round 4 done $(date +%H:%M:%S) ==="
cat raya/overnight/RESULTS4.txt
