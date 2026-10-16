"""Ingest raya/overnight/TEST_LOG.md -> test_runs table.
Sections:  ## <bot label> — `<agent_uuid8>`   then  | scenario | call | result | notes |
The `call` cell is a Raya call uuid (prefix) or a harness pseudo-id in (parens)."""
from __future__ import annotations
import re
from config import OVERNIGHT
from ingest.util import h, upsert, mark_source

SECTION_RE = re.compile(r"^##\s+(?P<label>.+?)\s*[—-]\s*(?P<uuids>.+)$")
UUID_RE = re.compile(r"`([0-9a-fA-F]{6,})`")
DPAT_RE = re.compile(r"\bD\d{1,3}\b")
PSEUDO_RE = re.compile(r"^\((?P<id>[a-z0-9]+)\)$")

TEST_LOG = OVERNIGHT / "TEST_LOG.md"


def _result_token(cell: str) -> str:
    c = cell.replace("*", "").strip()
    if "FAIL" in c and "FIXED" in c:
        return "fail→fixed"
    if "FIXED" in c or "✅" in c and "FIXED" in c:
        return "fixed"
    if "PASS" in c:
        return "pass"
    if "partial" in c or "⚠️" in c:
        return "partial"
    if "🐛" in c:
        return "findings"
    return c[:40] or "?"


def parse():
    """Returns (rows, section_uuids) where rows carry a temp `_section_uuid8`."""
    rows = []
    if not TEST_LOG.exists():
        return rows
    section_uuid = None
    for line in TEST_LOG.read_text().splitlines():
        line = line.rstrip()
        ms = SECTION_RE.match(line)
        if ms:
            us = UUID_RE.findall(ms.group("uuids"))
            section_uuid = us[0][:8] if us else None
            continue
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0].lower() == "scenario":
            continue
        scenario, call, result, notes = cells[0], cells[1], cells[2], cells[3]
        pm = PSEUDO_RE.match(call.strip())
        call_uuid = pm.group("id") if pm else call.strip().strip("`")
        if not call_uuid or call_uuid in ("—", "-"):
            call_uuid = h(scenario, notes[:20])  # synthetic key so nothing is lost
        rows.append({
            "call_uuid": call_uuid,
            "_section_uuid8": section_uuid,
            "scenario_title": scenario,
            "result": _result_token(result),
            "d_patterns": sorted(set(DPAT_RE.findall(notes))),
            "notes": notes[:1000],
            "is_test": 1,
            "source": "TEST_LOG",
        })
    return rows


def ingest(conn) -> int:
    rows = parse()
    # resolve section uuid8 -> target_id via bots
    prefix_map = {r["raya_agent_id_prod"][:8]: r["target_id"]
                  for r in conn.execute("SELECT target_id,raya_agent_id_prod FROM bots").fetchall()
                  if r["raya_agent_id_prod"]}
    out = []
    for r in rows:
        r = dict(r)
        r["bot_target_id"] = prefix_map.get(r.pop("_section_uuid8") or "", None)
        r["agent_uuid"] = None
        r["scenario_id"] = None
        r["outcome"] = None
        r["duration"] = None
        r["started_at"] = None
        r.pop("scenario_title", None)
        out.append(r)
    n = upsert(conn, "test_runs", out, pk="call_uuid")
    mark_source(conn, TEST_LOG, n)
    conn.execute(
        "UPDATE bots SET last_test_result=(SELECT result FROM test_runs t WHERE t.bot_target_id=bots.target_id "
        "ORDER BY t.rowid DESC LIMIT 1) WHERE EXISTS(SELECT 1 FROM test_runs t WHERE t.bot_target_id=bots.target_id)"
    )
    return n
