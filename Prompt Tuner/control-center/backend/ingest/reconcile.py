"""Attach PRIORITY_BUGS.md + open-items.md to Sheet issues as issue_enrichment.
The Sheet row stays the canonical spine; enrichment never overwrites Sheet fields.
Match key: target_id + d_pattern, then title/evidence-uuid overlap."""
from __future__ import annotations
import re
import json
from config import OVERNIGHT

DPAT_RE = re.compile(r"\bD\d{1,3}\b")
UUID_RE = re.compile(r"\b[0-9a-f]{8}\b")
TARGET_RE = re.compile(r"\b(?:kkb|dkb|maya)-[a-z]+-[a-z]+\b")


def _issues_index(conn):
    idx = []
    for r in conn.execute("SELECT issue_id,target_id,d_pattern,title,description FROM issues"):
        idx.append(dict(r))
    return idx


def _best_match(idx, target_id, dpat, text):
    toks = set(re.findall(r"[a-z]{4,}", (text or "").lower()))
    best, score = None, 0
    for it in idx:
        s = 0
        if dpat and it["d_pattern"] == dpat:
            s += 3
        if target_id and it["target_id"] == target_id:
            s += 2
        ittoks = set(re.findall(r"[a-z]{4,}", (it["title"] or "").lower()))
        s += len(toks & ittoks) * 0.3
        if s > score:
            best, score = it, s
    return best if score >= 3 else None   # require a real signal (dpat or target+title)


def _priority_bugs(conn, idx):
    f = OVERNIGHT / "PRIORITY_BUGS.md"
    if not f.exists():
        return []
    rows = []
    for line in f.read_text().splitlines():
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6 or cells[0].lower() in ("#", ""):
            continue
        blob = " ".join(cells)
        tid = (TARGET_RE.search(cells[1]) or TARGET_RE.search(blob))
        tid = tid.group(0) if tid else None
        dp = DPAT_RE.search(blob)
        title = cells[3] if len(cells) > 3 else cells[1]
        m = _best_match(idx, tid, dp.group(0) if dp else None, blob)
        if not m:
            continue
        rows.append({
            "issue_id": m["issue_id"], "source": "priority_bugs",
            "severity": cells[2] if len(cells) > 2 else "",
            "active_latent": next((c for c in cells if "ACTIVE" in c or "LATENT" in c), ""),
            "evidence_call_uuids": sorted(set(UUID_RE.findall(blob))),
            "proven_fix": next((c for c in cells if "port" in c.lower() or "fix" in c.lower()), ""),
            "recommended_action": cells[-1], "raw_excerpt": blob[:500],
        })
    return rows


def _open_items(conn, idx):
    f = OVERNIGHT / "open-items.md"
    if not f.exists():
        return []
    rows = []
    blocks = re.split(r"^##\s+\d+\.", f.read_text(), flags=re.M)
    for b in blocks[1:]:
        title = b.splitlines()[0].strip() if b.strip() else ""
        tid = TARGET_RE.search(b)
        dp = DPAT_RE.search(b)
        m = _best_match(idx, tid.group(0) if tid else None, dp.group(0) if dp else None, title + " " + b[:300])
        if not m:
            continue
        status = re.search(r"\*\*Status:\*\*\s*(.+)", b)
        rows.append({
            "issue_id": m["issue_id"], "source": "open_items",
            "severity": "", "active_latent": status.group(1).strip()[:80] if status else "",
            "evidence_call_uuids": sorted(set(UUID_RE.findall(b))),
            "proven_fix": "", "recommended_action": title, "raw_excerpt": b[:500].strip(),
        })
    return rows


def reconcile(conn) -> int:
    idx = _issues_index(conn)
    rows = _priority_bugs(conn, idx) + _open_items(conn, idx)
    n = 0
    for r in rows:
        conn.execute(
            "INSERT OR REPLACE INTO issue_enrichment"
            "(issue_id,source,severity,active_latent,evidence_call_uuids,proven_fix,recommended_action,raw_excerpt)"
            " VALUES(?,?,?,?,?,?,?,?)",
            (r["issue_id"], r["source"], r["severity"], r["active_latent"],
             json.dumps(r["evidence_call_uuids"]), r["proven_fix"], r["recommended_action"], r["raw_excerpt"]),
        )
        n += 1
    return n
