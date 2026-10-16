#!/bin/bash
# deploy_check.sh <target...> — deploy and report a correct verdict per target.
#
# Why: `raya_deploy.py deploy | grep -c DEPLOYED` is wrong in BOTH directions. It reads an
# idempotent "diff: none — Skipping PUT" as FAILED (false alarm, seen on Maya 2026-09-04), and
# earlier in the same session it masked a genuine transient failure because a later line happened
# to contain the word. Match the real outcomes instead.
cd "$(dirname "$0")/.."
rc=0
for t in "$@"; do
  out=$(python3 scripts/raya_deploy.py deploy "$t" --yes 2>&1)
  if   grep -q "DEPLOYED" <<<"$out";                    then v="DEPLOYED"
  elif grep -q "Skipping PUT" <<<"$out";                then v="already current"
  # Match the deploy script's OWN refusal wording, anchored, not any line containing the word
  # "placeholder" -- every KKB file is called "KKB Placeholder ...", so the old pattern labelled a
  # transient network failure on those bots as "REFUSED (guard)" and sent the reader looking for a
  # guard that had not fired. Seen on kkb-kn-signals and kkb-hi-in-signals, 2026-09-08.
  elif grep -qiE "REFUS(ING|ED) TO DEPLOY|placeholder job_id|PLACEHOLDER SAMPLE DATA" <<<"$out"; then
    v="REFUSED (guard)"; rc=1
  else v="FAILED"; rc=1; fi
  printf "%-22s %s\n" "$t" "$v"
  [ "$v" = "FAILED" ] && echo "$out" | tail -4 | sed 's/^/      /'
done
exit $rc
