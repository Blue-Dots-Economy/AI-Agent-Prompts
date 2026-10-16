#!/bin/bash
# pending-verifications.sh — the live calls that are OWED before anything here may be called "fixed".
#
# Every one of these is a change that is DEPLOYED and read-back verified but has never been observed
# on a real call. Per the repo's rule, that means it is VERIFY-PENDING, not done. Run one when
# telephony is healthy; on 2026-09-01 the tester number failed 8 consecutive dials from 17:37 IST,
# which is why they are still owed.
#
#   ./pending-verifications.sh mismatch   location='Delhi' + Ghaziabad jobs
#                                         EXPECT Turn A sentence 2, with [जगह]=दिल्ली and [शहर]=गाज़ियाबाद:
#                                         "आपके लिए दिल्ली में अभी कोई जॉब नहीं है — जो जॉब्स हैं वो गाज़ियाबाद में हैं।
#                                          गाज़ियाबाद में देखना चलेगा?"   (template lives in the prompt as
#                                          "आपके लिए [जगह] में अभी कोई जॉब नहीं है" — grep that, not the filled form)
#   ./pending-verifications.sh chain      location='Ghaziabad' + Ghaziabad jobs
#                                         EXPECT: confirm -> yes -> ONE bus-stop question -> jobs
#                                         (already verified once on 6620c025; this is the regression)
#   ./pending-verifications.sh skip       production shape, no contact_memory arg
#                                         EXPECT: no bus-stop question at all. NOTE: ungradeable while
#                                         stored memory is unreadable — see open item
#                                         kkb-hi-signals-memory-gated-unverifiable.
#
# Grade every result mechanically, never by reading the transcript charitably:
#   python3 raya/regression/location_chain.py       --agent kkb-hi-signals --since <YYYY-MM-DDTHH:MM:SS>
#   python3 raya/regression/apply_result_integrity.py --agent kkb-hi-signals --since <...>
#   python3 raya/regression/location_reconfirm.py   --agent kkb-hi-signals --since <...>
set -uo pipefail
cd "$(dirname "$0")/../.."
BOT=115b38a5-42ef-4082-be69-84a871bb226a
TESTER=f60e0899-aa3a-4be7-9b4f-0296bd28ef48
DID=7946350285
PERSONA=raya/personas/hi-loc-confirm-then-landmark.md
case "${1:-}" in
  mismatch) ARGS=raya/testcases/args/r3/loc-mismatch-delhi.json ;;
  chain)    ARGS=raya/testcases/args/r3/loc-chain-first-call.json ;;
  skip)     ARGS=raya/testcases/args/r3/loc-chain-platform-memory.json ;;
  *) sed -n '2,30p' "$0"; exit 2 ;;
esac
echo "persona -> $PERSONA"
python3 scripts/raya_testcall.py persona "$TESTER" "$PERSONA" | head -1
sleep 4
echo "dialling $1 with $ARGS"
python3 -u scripts/raya_testrun.py "$BOT" "$DID" "$ARGS" "$TESTER" "pending-$1"
