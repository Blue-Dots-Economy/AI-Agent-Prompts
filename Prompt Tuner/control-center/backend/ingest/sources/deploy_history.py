"""Ingest raya/deploy-history.md -> deploys table.

Handles 3 line shapes seen in the file, all ` · `-delimited:
  canonical: TS · env · target · uuid · file · sha256:8 · snapshot:label · result
  legacy:    TS · env · target · uuid · file · verified=True · via=api-patch [· tag]
  config/free-text: "YYYY-MM-DD (config) · env · target · uuid · <prose incl. snapshot:...>"
Positional tokens 0..4 are stable; sha256:/snapshot:/result are found by scanning.
"""
from __future__ import annotations
import re
from config import DEPLOY_HISTORY
from ingest.util import h, upsert, mark_source

TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def parse() -> list[dict]:
    rows = []
    if not DEPLOY_HISTORY.exists():
        return rows
    for line in DEPLOY_HISTORY.read_text().splitlines():
        line = line.strip()
        if not line or not TS_RE.match(line):
            continue
        parts = [p.strip() for p in line.split(" · ")]
        if len(parts) < 4:
            continue
        ts, env, target_id, agent_uuid = parts[0], parts[1], parts[2], parts[3]
        file_path = parts[4] if len(parts) > 4 else ""
        sha8 = snap = result = tag = ""
        for p in parts[4:]:
            if p.startswith("sha256:"):
                sha8 = p.split(":", 1)[1]
            elif p.startswith("snapshot:"):
                snap = p.split(":", 1)[1]
            elif p in ("deployed", "skip-in-sync", "FAILED-readback"):
                result = p
            elif p.startswith("via="):
                result = result or "deployed"
            elif p.startswith("verified="):
                pass
        # free-text snapshot ref (revert lines)
        if not snap:
            m = re.search(r"snapshot:([^\s·]+)", line)
            if m:
                snap = m.group(1)
        if "REVERTED" in line:
            result = result or "reverted"
        rows.append({
            "deploy_id": h(ts, target_id),
            "ts": ts, "env": env, "target_id": target_id, "agent_uuid": agent_uuid,
            "file_path": file_path, "sha256_8": sha8, "snapshot_label": snap,
            "result": result or "deployed", "tag": tag,
        })
    return rows


def ingest(conn) -> int:
    rows = parse()
    n = upsert(conn, "deploys", rows, pk="deploy_id")
    mark_source(conn, DEPLOY_HISTORY, n)
    # roll up last_deploy_at onto bots
    conn.execute(
        "UPDATE bots SET last_deploy_at=(SELECT MAX(ts) FROM deploys d WHERE d.target_id=bots.target_id)"
    )
    return n
