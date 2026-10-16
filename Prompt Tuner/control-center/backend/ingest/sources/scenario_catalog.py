"""Ingest raya/personas/scenario-catalog.md (+ personas/*.md) -> scenarios table.
Family headers `# KKB — …`; entries `## Scenario: <title>` with a 6-field body."""
from __future__ import annotations
import re
from config import SCENARIO_CATALOG, PERSONAS
from ingest.util import h, upsert, mark_source

FAMILY_RE = re.compile(r"^#\s+(KKB|DKB|Maya)\b")
SCEN_RE = re.compile(r"^##\s+Scenario:\s*(?P<title>.+?)\s*$")
UUID_RE = re.compile(r"`([0-9a-fA-F]{6,})`")


def parse():
    rows = []
    if not SCENARIO_CATALOG.exists():
        return rows
    family = None
    cur = None
    for line in SCENARIO_CATALOG.read_text().splitlines():
        fm = FAMILY_RE.match(line)
        if fm:
            family = fm.group(1)
        sm = SCEN_RE.match(line)
        if sm:
            if cur:
                rows.append(cur)
            title = sm.group("title")
            cur = {"scenario_id": h(family or "?", title), "agent": family, "family": family,
                   "title": title, "situation": "", "backing_call_uuid": None,
                   "persona_file": "", "language": "", "checklist_ref": "",
                   "source_file": "raya/personas/scenario-catalog.md", "_body": []}
        elif cur is not None and not line.startswith("# "):
            cur["_body"].append(line)
    if cur:
        rows.append(cur)
    # finalize
    persona_names = [p.name for p in PERSONAS.glob("*.md")] if PERSONAS.exists() else []
    for r in rows:
        body = "\n".join(r.pop("_body", []))
        r["situation"] = body[:600].strip()
        us = UUID_RE.findall(body)
        r["backing_call_uuid"] = us[0][:8] if us else None
        # best-effort persona link by keyword overlap
        toks = re.findall(r"[a-z]+", r["title"].lower())
        best = next((pn for pn in persona_names
                     if sum(t in pn for t in toks) >= 2), "")
        r["persona_file"] = best
    return rows


def ingest(conn) -> int:
    rows = parse()
    n = upsert(conn, "scenarios", rows, pk="scenario_id")
    mark_source(conn, SCENARIO_CATALOG, n)
    return n
