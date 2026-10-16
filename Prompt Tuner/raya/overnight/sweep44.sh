#!/bin/bash
# Measure the fabricated-apply rate after the availability cut. Needs volume: the rate is ~11%.
cd "/Users/parthbansal/EkStep/Prompt Tuner"
TESTER=f60e0899-aa3a-4be7-9b4f-0296bd28ef48
OUT=raya/overnight/logs
RES=raya/overnight/RESULTS45.txt
run () {
  python3 scripts/raya_testcall.py lang "$TESTER" "$5" > /dev/null 2>&1
  python3 scripts/raya_testcall.py persona "$TESTER" "raya/personas/$4" > /dev/null 2>&1
  sleep 4
  for w in 1 2 3; do
    python3 -u scripts/raya_testrun.py "$2" 7946350285 "$3" "$TESTER" "$1" > "$OUT/$1.log" 2>&1
    D=$(grep -oE "outcome=Completed dur=[0-9]+" "$OUT/$1.log" | grep -oE "[0-9]+$" | head -1)
    T=$(grep -c "^\[assistant\]" "$OUT/$1.log")
    if [ -n "$D" ] && [ "$D" -ge 55 ] && [ "$T" -ge 5 ]; then
      U=$(grep -oE "BOT [0-9a-f-]{36}" "$OUT/$1.log" | head -1 | cut -d' ' -f2)
      echo "$1 USABLE ${D}s $T $U" >> "$RES"; return 0
    fi
  done
  echo "$1 NO-CALL - - -" >> "$RES"
}
G=raya/testcases/args/r3/gzb-validated-12.json
M=raya/testcases/args/signals-prod/maya-hi-signals.json
for n in 1 2 3; do
  run fab-hi-$n  115b38a5-42ef-4082-be69-84a871bb226a $G hi-gzb-accepts-any.md hi
  run fab-may-$n 904f333f-1919-4523-a51d-b22ba382dd22 $M hi-gzb-accepts-any.md hi
done
cat "$RES"
