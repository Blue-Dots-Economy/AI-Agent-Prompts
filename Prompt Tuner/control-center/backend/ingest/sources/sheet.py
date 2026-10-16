"""Ingest the Google Sheet 'All Issues' tab -> issues table (canonical spine).
Shells the existing scripts/gsheets.py (reuses its service-account auth)."""
from __future__ import annotations
import json
import re
import subprocess
from config import PY, SCRIPTS, REPO, SHEET_ID, SHEET_TAB, SHEET_COLS
from ingest.util import h, upsert

DPAT_RE = re.compile(r"\bD\d{1,3}\b")


def _fetch_values() -> list[list[str]]:
    out = subprocess.run(
        [PY, str(SCRIPTS / "gsheets.py"), "--sheet-id", SHEET_ID, "get", f"'{SHEET_TAB}'!A2:L"],
        cwd=str(REPO), capture_output=True, text=True, timeout=60,
    )
    if out.returncode != 0:
        raise RuntimeError(f"gsheets.py get failed: {out.stderr.strip()[:200]}")
    return json.loads(out.stdout or "[]")


def parse(values, label_map: dict) -> list[dict]:
    rows = []
    for i, raw in enumerate(values):
        row = (raw + [""] * len(SHEET_COLS))[: len(SHEET_COLS)]
        rec = dict(zip(SHEET_COLS, row))
        if not any(v.strip() for v in rec.values()):
            continue
        if not rec["status"].strip() and not rec["title"].strip():
            continue
        bot_label = rec["bot_label"].strip()
        target_id = label_map.get(bot_label) or _fuzzy_target(bot_label, label_map)
        blob = f"{rec['title']} {rec['description']} {rec['comments']}"
        dpat = DPAT_RE.search(blob)
        rows.append({
            "issue_id": h(rec["date"], bot_label, rec["title"]),
            "sheet_row": i + 2,   # A2 == row 2
            "date": rec["date"], "status": rec["status"].strip(), "bot_label": bot_label,
            "target_id": target_id, "agent": _agent_of(target_id),
            "title": rec["title"], "type": rec["type"], "description": rec["description"][:2000],
            "owner": rec["owner"], "priority": rec["priority"], "eta": rec["eta"],
            "call_ids_raw": rec["call_ids_raw"], "comments": rec["comments"][:2000],
            "fixed_note": rec["fixed_note"], "d_pattern": dpat.group(0) if dpat else None,
            "updated_at": None, "dirty": 0,
        })
    return rows


def _agent_of(target_id):
    if not target_id:
        return None
    return {"kkb": "KKB", "dkb": "DKB", "maya": "Maya"}.get(target_id.split("-")[0])


def _fuzzy_target(label: str, label_map: dict):
    if not label:
        return None
    norm = re.sub(r"\(.*?\)", "", label).lower()
    for known, tid in label_map.items():
        kn = re.sub(r"\(.*?\)", "", known).lower()
        if kn.split()[0] in norm and any(tok in norm for tok in ("kannada", "inbound", "he")) == \
           any(tok in kn for tok in ("kannada", "inbound", "he")):
            return tid
    if "he" in norm.split():
        return "maya-hi-out"
    return None


def ingest(conn) -> int:
    label_map = {r["label"]: r["target_id"] for r in conn.execute("SELECT label,target_id FROM bot_label_map")}
    values = _fetch_values()
    rows = parse(values, label_map)
    n = upsert(conn, "issues", rows, pk="issue_id")
    conn.execute(
        "INSERT INTO source_files(path,sha256,mtime,last_ingested_at,row_count) "
        "VALUES('sheet:All Issues','','',datetime('now'),?) "
        "ON CONFLICT(path) DO UPDATE SET last_ingested_at=datetime('now'), row_count=excluded.row_count",
        (n,),
    )
    return n
