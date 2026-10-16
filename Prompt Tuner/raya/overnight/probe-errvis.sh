#!/bin/bash
# DECISIVE TEST: can the conversation model see the tool error body at all?
# The prompt now says, as its FIRST instruction on a failed apply: if the result text contains
# ACTION_LIMIT_REACHED or "already exists", say the already-applied line. Every apply in this fixture
# is a known duplicate, so the API will return exactly that. If the already-applied line appears, the
# model CAN read the error and every previous conclusion of mine is wrong.
cd "/Users/parthbansal/EkStep/Prompt Tuner"
TESTER=f60e0899-aa3a-4be7-9b4f-0296bd28ef48
python3 scripts/raya_testcall.py lang "$TESTER" hi > /dev/null 2>&1
python3 scripts/raya_testcall.py persona "$TESTER" raya/personas/hi-minimal-caller.md > /dev/null 2>&1
sleep 4
for w in 1 2 3 4; do
  echo "[$(date +%H:%M:%S)] errvis wave $w"
  python3 -u scripts/raya_testrun.py 115b38a5-42ef-4082-be69-84a871bb226a 7946350285 \
    raya/testcases/args/r3/khushboo-repro.json "$TESTER" errvis > raya/overnight/logs/errvis.log 2>&1
  D=$(grep -oE "outcome=Completed dur=[0-9]+" raya/overnight/logs/errvis.log | grep -oE "[0-9]+$" | head -1)
  T=$(grep -c "^\[assistant\]" raya/overnight/logs/errvis.log)
  if [ -n "$D" ] && [ "$D" -ge 55 ] && [ "$T" -ge 5 ]; then
    echo "[$(date +%H:%M:%S)] USABLE errvis dur=${D}s turns=$T"; break
  fi
  echo "[$(date +%H:%M:%S)] wave $w unusable (dur=${D:-none} turns=$T)"
done
echo "--- did it read the error? ---"
grep -h "^\[assistant\]" raya/overnight/logs/errvis.log | grep -cF "पहले से लगी हुई है" || true
echo "ERRVIS DONE $(date +%H:%M:%S)"
