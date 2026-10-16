"""Ingest fleet data into control.db.

Usage (from backend/):
  python -m ingest --all            # everything (offline files + sheet + live sync)
  python -m ingest --offline        # only the repo-file sources (no network/secrets)
  python -m ingest agents deploys   # named sources
"""
from __future__ import annotations
import sys
from db import init_db, get_conn

# name -> (module, needs) ; needs: 'file'|'sheet'|'live'
from ingest.sources import agents_json, deploy_history, versions_history, changelog

OFFLINE = {
    "agents": agents_json,
    "deploys": deploy_history,
    "versions": versions_history,
    "fixes": changelog,
}
# lazily-imported network sources (need secrets / raya)
NETWORK = {"test_log", "scenarios", "issues", "live"}


def _load_network():
    mods = {}
    try:
        from ingest.sources import test_log
        mods["test_log"] = test_log
    except Exception as e:
        print("  (test_log unavailable:", e, ")")
    try:
        from ingest.sources import scenario_catalog
        mods["scenarios"] = scenario_catalog
    except Exception as e:
        print("  (scenarios unavailable:", e, ")")
    try:
        from ingest.sources import sheet
        mods["issues"] = sheet
    except Exception as e:
        print("  (issues/sheet unavailable:", e, ")")
    try:
        from ingest.sources import live_status
        mods["live"] = live_status
    except Exception as e:
        print("  (live status unavailable:", e, ")")
    return mods


def run(selected: list[str], include_network: bool):
    init_db()
    sources = dict(OFFLINE)
    if include_network:
        sources.update(_load_network())
        # reconcile enrichment after issues load
    order = ["agents", "deploys", "versions", "fixes", "test_log", "scenarios", "issues", "live"]
    with get_conn() as conn:
        for name in order:
            if selected and name not in selected:
                continue
            mod = sources.get(name)
            if not mod:
                continue
            try:
                n = mod.ingest(conn)
                print(f"  {name:10s} -> {n} rows")
            except Exception as e:
                print(f"  {name:10s} FAILED: {e}")
        if include_network and (not selected or "issues" in selected):
            try:
                from ingest.reconcile import reconcile
                m = reconcile(conn)
                print(f"  reconcile  -> {m} enrichment rows")
            except Exception as e:
                print(f"  reconcile  FAILED: {e}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    if "--all" in args:
        run([], include_network=True)
    elif "--offline" in args:
        run([], include_network=False)
    else:
        named = [a for a in args if not a.startswith("--")]
        run(named, include_network=bool(set(named) & NETWORK))
    # summary
    with get_conn() as c:
        for t in ("bots", "issues", "deploys", "versions", "fixes", "test_runs", "scenarios"):
            n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"    {t}: {n}")
