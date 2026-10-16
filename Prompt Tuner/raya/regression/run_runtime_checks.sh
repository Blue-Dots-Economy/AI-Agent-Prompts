#!/bin/bash
# run_runtime_checks.sh — every RUNTIME (behaviour) detector in one command.
#
# These read real Raya call transcripts, so they need raya/.env and CANNOT run in the
# zero-secrets GitHub Actions daily job. That is exactly why a behaviour regression
# (e.g. the 2026-09-01 location-reconfirm and already-applied misses) never appeared in
# the daily email: the daily suite is STATIC only. Run this after any behaviour change,
# and see README "Runtime checks are not in the daily digest yet" for the standing gap.
#
# Usage: raya/regression/run_runtime_checks.sh [--since YYYY-MM-DD] [--agent <id>]
set -uo pipefail
cd "$(dirname "$0")/../.."
ARGS=("$@")
FAIL=0

# Tool SCHEMA parity, not just prompt text. Two live bugs on 2026-09-03 came from a fix that lived
# in a tool schema and was applied to one bot only -- duplicate_check on 1 of 12, and the
# ACTION_LIMIT_REACHED mapping on 1 of 6 -- while the prompt text was mirrored everywhere. Replayed
# against that state this check flags it and exits 1.
echo ""
echo "================================================================ toolschema_parity"
python3 scripts/toolschema_parity.py || FAIL=1

# Every shipped fix, on every bot that needs it. Three fixes have half-landed on their mirrors
# (duplicate_check 1/12, the ACTION_LIMIT mapping 1/6, the TRRAIN naming Hindi-only) and none of
# the other checks knows what we FIXED. Static and secret-free, so it also belongs in the daily
# cloud job.
echo ""
echo "================================================================ fix_presence"
python3 raya/regression/fix_presence.py || FAIL=1

# Is the bot USING what the campaign sends it? Maya was sent `location` on every call and named it
# nowhere, so its area question could only ever be asked from scratch (D68). Nothing in the prompt
# was wrong -- something was absent, which no amount of reading the prompt finds.
echo ""
echo "================================================================ input_coverage"
python3 raya/regression/input_coverage.py || FAIL=1

# Added 2026-09-08. spoken_form catches a stored value read out in its WRITTEN form (Latin script,
# a PIN as a quantity, a field label, a placeholder) -- the class behind QA calls 5035574 and
# 5061404, and behind DKB greeting owners as "Not Available" on seven calls. location_said asks a
# narrower question the others cannot: WHICH place did the bot name? That one sentence produces four
# outcomes -- correct, the raw argument, a DIFFERENT place it happened to know, or nothing at all --
# and only two of them look like failures to any other check.
for chk in already_applied_rate offarray_jobs bracket_leak spoken_form location_said dkb_employer_integrity inbound_location_consent nojobs_integrity jobs_presented consent_before_apply location_chain location_reconfirm apply_result_integrity apply_failure_wording location_integrity apply_outcomes; do
  echo ""
  echo "================================================================ $chk"
  python3 "raya/regression/$chk.py" "${ARGS[@]:-}" || FAIL=1
done
echo ""
if [ "$FAIL" -eq 0 ]; then echo "ALL RUNTIME CHECKS CLEAN"; else echo "RUNTIME FINDINGS PRESENT (exit 1)"; fi
exit "$FAIL"
