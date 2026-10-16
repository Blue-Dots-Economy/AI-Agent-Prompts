"""Ingest raya/agents.json -> bots table (the fleet spine)."""
from __future__ import annotations
import json
from config import AGENTS_JSON
from ingest.util import upsert, mark_source


def parse() -> list[dict]:
    data = json.loads(AGENTS_JSON.read_text())
    rows = []
    for t in data.get("targets", []):
        rid = t.get("raya_agent_id") or {}
        prod = rid.get("prod") if isinstance(rid, dict) else rid
        rows.append({
            "target_id": t["id"],
            "agent": t.get("agent"),
            "language": t.get("language"),
            "direction": t.get("direction"),
            "kind": t.get("kind"),
            "profile": t.get("profile"),
            "file_path": t.get("file"),
            "raya_agent_id_prod": prod or "",
            "raya_name": t.get("raya_name") or "",
            "expected_name_contains": t.get("expected_name_contains") or [],
            "deploy": 1 if t.get("deploy") else 0,
            "experimental": 1 if t.get("experimental") else 0,
        })
    return rows


def ingest(conn) -> int:
    rows = parse()
    n = upsert(conn, "bots", rows, pk="target_id")
    mark_source(conn, AGENTS_JSON, n)
    return n
