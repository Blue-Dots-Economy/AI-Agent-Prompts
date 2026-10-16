"""Ingest <Agent>/CHANGELOG.md -> fixes table (the prompt-edit log).
Entry: ## YYYY-MM-DD — <title>  then bullets **Feedback/bug:** **Change:** **Files:** **Ported from:**"""
from __future__ import annotations
import re
from config import AGENT_DIRS
from ingest.util import h, upsert, mark_source

HEAD_RE = re.compile(r"^##\s+(?P<date>\d{4}-\d{2}-\d{2})\s*[—-]\s*(?P<title>.+?)\s*$")
FIELD_RE = re.compile(r"\*\*(?P<k>[^:*]+):\*\*\s*(?P<v>.+)")
DPAT_RE = re.compile(r"\bD\d{1,3}\b")
TARGET_RE = re.compile(r"\b(?:kkb|dkb|maya)-[a-z]+-[a-z]+\b")
SNAP_RE = re.compile(r"pre-[a-z0-9._-]+")


def _blocks(text: str):
    cur = None
    for line in text.splitlines():
        m = HEAD_RE.match(line)
        if m:
            if cur:
                yield cur
            cur = {"date": m.group("date"), "title": m.group("title").strip(), "body": []}
        elif cur is not None:
            cur["body"].append(line)
    if cur:
        yield cur


def parse() -> list[dict]:
    rows = []
    for agent, adir in AGENT_DIRS.items():
        cl = adir / "CHANGELOG.md"
        if not cl.exists():
            continue
        text = cl.read_text()
        for b in _blocks(text):
            body = "\n".join(b["body"])
            fields = {}
            for line in b["body"]:
                fm = FIELD_RE.search(line)
                if fm:
                    fields[fm.group("k").strip().lower()] = fm.group("v").strip()
            rows.append({
                "fix_id": h(agent, b["date"], b["title"]),
                "date": b["date"], "agent": agent, "title": b["title"],
                "feedback": fields.get("feedback/bug") or fields.get("feedback") or "",
                "change_desc": fields.get("change") or "",
                "files": sorted(set(TARGET_RE.findall(body))),
                "deployed_targets": sorted(set(TARGET_RE.findall(body))),
                "snapshot_labels": sorted(set(SNAP_RE.findall(body))),
                "ported_from": fields.get("ported from") or "",
                "d_patterns": sorted(set(DPAT_RE.findall(body))),
                "source_file": str(cl.relative_to(adir.parent)),
            })
    return rows


def ingest(conn) -> int:
    rows = parse()
    n = upsert(conn, "fixes", rows, pk="fix_id")
    for agent, adir in AGENT_DIRS.items():
        mark_source(conn, adir / "CHANGELOG.md", n)
    # roll up last_edit_at onto bots by agent
    conn.execute(
        "UPDATE bots SET last_edit_at=(SELECT MAX(date) FROM fixes f WHERE f.agent=bots.agent)"
    )
    return n
