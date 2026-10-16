#!/bin/bash
# Runs the location write-back for both KKB Slim bots (launchd, every 15 min). Agreed 2026-10-13:
# landmark + area + city + state + PIN go into the profile's single location field after each call.
cd "$(dirname "$0")/.." || exit 1
LOG=raya/location-writeback.log
for agent in 140d13ca-c80f-47c4-9454-5edb3fd38c96 bd4dfd44-a0c5-4d37-9b49-f8c186c901c1; do
  echo "== $(date -u '+%F %T') agent ${agent:0:8}" >> "$LOG"
  /usr/bin/python3 scripts/location_writeback.py apply --agent "$agent" --limit 100 2>&1 \
    | grep -v "skip — already processed" | sed -E 's/91[0-9]{10}/91XXXXXXXXXX/g' >> "$LOG"
done
