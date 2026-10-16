"""Refresh live per-bot sync-state via scripts/raya_deploy.py status --all.
Best-effort: network + slow; never fails the whole ingest. Output lines are
'<target-id> <state>' with state in {in-sync,drifted,unmapped,missing-file,unreachable}."""
from __future__ import annotations
import re
import subprocess
from config import PY, SCRIPTS, REPO

STATES = {"in-sync", "in sync", "drifted", "unmapped", "missing-file", "missing file", "unreachable"}
LINE_RE = re.compile(r"^\s*(?P<id>[a-z0-9-]+)\s+(?P<state>in[- ]sync|drifted|unmapped|missing[- ]file|unreachable)\b", re.I)


def fetch() -> dict:
    out = subprocess.run(
        [PY, str(SCRIPTS / "raya_deploy.py"), "--env", "prod", "status", "--all"],
        cwd=str(REPO), capture_output=True, text=True, timeout=180,
    )
    states = {}
    for line in (out.stdout or "").splitlines():
        m = LINE_RE.match(line)
        if m:
            states[m.group("id")] = m.group("state").replace(" ", "-").lower()
    return states


def ingest(conn) -> int:
    try:
        states = fetch()
    except Exception as e:
        print("   (live status skipped:", str(e)[:80], ")")
        return 0
    n = 0
    for tid, st in states.items():
        conn.execute(
            "UPDATE bots SET sync_state=?, last_synced_at=datetime('now') WHERE target_id=?",
            (st, tid),
        )
        n += 1
    return n
