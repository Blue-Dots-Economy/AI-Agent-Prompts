"""Read-model queries over control.db for the cockpit API."""
from __future__ import annotations
import json
from db import get_conn


def _rows(cur):
    return [dict(r) for r in cur.fetchall()]


def _jloads(v, default):
    try:
        return json.loads(v) if v else default
    except Exception:
        return default


def list_bots():
    with get_conn() as c:
        bots = _rows(c.execute("""
            SELECT b.*,
              (SELECT COUNT(*) FROM issues i WHERE i.target_id=b.target_id
                 AND i.status IN ('Open','Accepted to Fix')) AS open_issues,
              (SELECT COUNT(*) FROM issues i WHERE i.target_id=b.target_id
                 AND i.status='Open' AND i.priority LIKE 'P1%') AS open_p1,
              (SELECT COUNT(*) FROM test_runs t WHERE t.bot_target_id=b.target_id) AS test_count
            FROM bots b ORDER BY b.agent, b.direction, b.language
        """))
    for b in bots:
        b["expected_name_contains"] = _jloads(b.get("expected_name_contains"), [])
    return bots


def get_bot(target_id):
    with get_conn() as c:
        b = c.execute("SELECT * FROM bots WHERE target_id=?", (target_id,)).fetchone()
        if not b:
            return None
        b = dict(b)
        b["expected_name_contains"] = _jloads(b.get("expected_name_contains"), [])
        b["deploys"] = _rows(c.execute("SELECT * FROM deploys WHERE target_id=? ORDER BY ts DESC LIMIT 40", (target_id,)))
        b["issues"] = _rows(c.execute("SELECT * FROM issues WHERE target_id=? ORDER BY status, priority", (target_id,)))
        b["test_runs"] = _rows(c.execute("SELECT * FROM test_runs WHERE bot_target_id=? ORDER BY rowid DESC LIMIT 40", (target_id,)))
        agent = b.get("agent")
        b["versions"] = _rows(c.execute("SELECT * FROM versions WHERE agent=? ORDER BY ts DESC LIMIT 40", (agent,)))
        b["fixes"] = _rows(c.execute("SELECT * FROM fixes WHERE agent=? ORDER BY date DESC LIMIT 40", (agent,)))
    for f in b["fixes"]:
        for k in ("files", "deployed_targets", "snapshot_labels", "d_patterns"):
            f[k] = _jloads(f.get(k), [])
    for t in b["test_runs"]:
        t["d_patterns"] = _jloads(t.get("d_patterns"), [])
    return b


def list_issues(status=None, bot=None, owner=None, priority=None):
    q = "SELECT * FROM issues WHERE 1=1"
    args = []
    if status:
        q += " AND status=?"; args.append(status)
    if bot:
        q += " AND target_id=?"; args.append(bot)
    if owner:
        q += " AND owner=?"; args.append(owner)
    if priority:
        q += " AND priority LIKE ?"; args.append(priority + "%")
    q += " ORDER BY status, priority, date DESC"
    with get_conn() as c:
        issues = _rows(c.execute(q, args))
        enr = {}
        for e in c.execute("SELECT * FROM issue_enrichment"):
            enr.setdefault(e["issue_id"], []).append(dict(e))
    for i in issues:
        i["enrichment"] = enr.get(i["issue_id"], [])
        for e in i["enrichment"]:
            e["evidence_call_uuids"] = _jloads(e.get("evidence_call_uuids"), [])
    return issues


def list_scenarios(agent=None):
    q = "SELECT * FROM scenarios"
    args = []
    if agent:
        q += " WHERE agent=?"; args.append(agent)
    q += " ORDER BY agent, title"
    with get_conn() as c:
        return _rows(c.execute(q, args))


def list_table(table, order="rowid DESC", limit=500):
    allowed = {"deploys", "fixes", "versions", "test_runs"}
    if table not in allowed:
        return []
    with get_conn() as c:
        return _rows(c.execute(f"SELECT * FROM {table} ORDER BY {order} LIMIT {int(limit)}"))


def stats():
    with get_conn() as c:
        def one(sql, *a):
            return c.execute(sql, a).fetchone()[0]
        return {
            "bots": one("SELECT COUNT(*) FROM bots"),
            "bots_deployable": one("SELECT COUNT(*) FROM bots WHERE deploy=1"),
            "bots_drifted": one("SELECT COUNT(*) FROM bots WHERE sync_state='drifted'"),
            "issues_open": one("SELECT COUNT(*) FROM issues WHERE status IN ('Open','Accepted to Fix')"),
            "issues_p1_open": one("SELECT COUNT(*) FROM issues WHERE status='Open' AND priority LIKE 'P1%'"),
            "issues_flagged_backend": one("SELECT COUNT(*) FROM issues WHERE status='Flagged - Backend Issue'"),
            "deploys_total": one("SELECT COUNT(*) FROM deploys"),
            "fixes_total": one("SELECT COUNT(*) FROM fixes"),
            "scenarios": one("SELECT COUNT(*) FROM scenarios"),
            "test_runs": one("SELECT COUNT(*) FROM test_runs"),
            "status_breakdown": {r[0]: r[1] for r in c.execute(
                "SELECT status,COUNT(*) FROM issues GROUP BY status ORDER BY 2 DESC")},
        }


def test_matrix():
    """bots x scenarios coverage grid (from test_runs joined by bot)."""
    with get_conn() as c:
        bots = [r["target_id"] for r in c.execute(
            "SELECT target_id FROM bots WHERE kind='conversation' ORDER BY agent,direction,language")]
        runs = _rows(c.execute(
            "SELECT bot_target_id,result,notes,call_uuid FROM test_runs WHERE bot_target_id IS NOT NULL"))
    cover = {}
    for r in runs:
        cover.setdefault(r["bot_target_id"], []).append(r)
    return {"bots": bots, "coverage": cover}
