"""Ingest versions/<Agent>/HISTORY.md -> versions table.
Line: - **<stamp>** — `<label>` — <description> _(N files)_
The <label> equals deploy-history's snapshot: field (the join key)."""
from __future__ import annotations
import re
from config import VERSIONS
from ingest.util import h, upsert, mark_source

LINE_RE = re.compile(
    r"^-\s*\*\*(?P<ts>[^*]+)\*\*\s*[—-]\s*`(?P<label>[^`]+)`\s*[—-]\s*(?P<desc>.*?)\s*(?:_\((?P<n>\d+)\s*files?\)_)?\s*$"
)


def parse() -> list[dict]:
    rows = []
    for agent in ("KKB", "DKB", "Maya"):
        hist = VERSIONS / agent / "HISTORY.md"
        if not hist.exists():
            continue
        for line in hist.read_text().splitlines():
            m = LINE_RE.match(line.strip())
            if not m:
                continue
            label = m.group("label")
            rows.append({
                "version_id": h(agent, label),
                "agent": agent, "ts": m.group("ts").strip(), "label": label,
                "description": m.group("desc").strip(),
                "file_count": int(m.group("n")) if m.group("n") else None,
            })
    return rows


def ingest(conn) -> int:
    rows = parse()
    n = upsert(conn, "versions", rows, pk="version_id")
    for agent in ("KKB", "DKB", "Maya"):
        mark_source(conn, VERSIONS / agent / "HISTORY.md", n)
    return n
