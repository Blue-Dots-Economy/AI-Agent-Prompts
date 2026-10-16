#!/bin/bash
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
      echo "$1 USABLE ${D}s $T $U" >> raya/overnight/RESULTS7.txt; return 0
    fi
    echo "[$(date +%H:%M:%S)] $1 wave $w unusable (dur=${D:-none} turns=$T)"
  done
  echo "$1 NO-CALL - - -" >> raya/overnight/RESULTS7.txt
}
echo "=== round 7 start $(date +%H:%M:%S) ==="
run dkbhi-v1 fabda71d-af75-4ddd-8cf1-fa35c827f753 raya/testcases/args/r3/dkb-new-provider.json hi-employer-cooperative.md hi
run dkbhi-v2 fabda71d-af75-4ddd-8cf1-fa35c827f753 raya/testcases/args/r3/dkb-new-provider.json hi-employer-cooperative.md hi
run dkbhi-v3 fabda71d-af75-4ddd-8cf1-fa35c827f753 raya/testcases/args/r3/dkb-new-provider.json hi-employer-cooperative.md hi
echo "=== round 7 done $(date +%H:%M:%S) ==="
cat raya/overnight/RESULTS7.txt
