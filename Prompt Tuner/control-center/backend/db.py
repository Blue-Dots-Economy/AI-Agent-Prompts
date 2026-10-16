"""SQLite store for the Bot Control Center.

control.db is a CACHE + read-model of the fleet data (the Google Sheet stays the
canonical issue tracker) plus the job-runner/history store. Everything joins on
target_id; three cross-source keys recur: call_uuid, d_pattern, snapshot_label.
"""
from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from config import CONTROL_DB, BOT_LABEL_MAP

SCHEMA = """
-- ---- dimensions / provenance ----
CREATE TABLE IF NOT EXISTS bot_label_map (
    label TEXT PRIMARY KEY, target_id TEXT, note TEXT
);
CREATE TABLE IF NOT EXISTS source_files (
    path TEXT PRIMARY KEY, sha256 TEXT, mtime REAL,
    last_ingested_at TEXT, row_count INTEGER
);

-- ---- bots (canonical: raya/agents.json; live fields refreshed) ----
CREATE TABLE IF NOT EXISTS bots (
    target_id TEXT PRIMARY KEY,
    agent TEXT, language TEXT, direction TEXT, kind TEXT, profile TEXT,
    file_path TEXT, raya_agent_id_prod TEXT, raya_name TEXT,
    expected_name_contains TEXT,           -- JSON array
    deploy INTEGER, experimental INTEGER,
    -- live / derived (refreshed):
    sync_state TEXT, live_name TEXT, local_sha TEXT, remote_sha TEXT,
    last_call_at TEXT, last_deploy_at TEXT, last_test_at TEXT,
    last_test_result TEXT, last_edit_at TEXT, last_synced_at TEXT
);

-- ---- issues (canonical spine = Google Sheet; enrichment is additive) ----
CREATE TABLE IF NOT EXISTS issues (
    issue_id TEXT PRIMARY KEY,             -- hash(date|bot_label|title)
    sheet_row INTEGER,                     -- re-resolved before any write, never trusted blind
    date TEXT, status TEXT, bot_label TEXT, target_id TEXT,
    agent TEXT, title TEXT, type TEXT, description TEXT,
    owner TEXT, priority TEXT, eta TEXT,
    call_ids_raw TEXT, comments TEXT, fixed_note TEXT,
    d_pattern TEXT, updated_at TEXT, dirty INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_issues_target ON issues(target_id);
CREATE INDEX IF NOT EXISTS ix_issues_status ON issues(status);
CREATE INDEX IF NOT EXISTS ix_issues_dpat ON issues(d_pattern);

CREATE TABLE IF NOT EXISTS issue_enrichment (
    issue_id TEXT, source TEXT,            -- 'priority_bugs' | 'open_items'
    severity TEXT, active_latent TEXT,
    evidence_call_uuids TEXT,              -- JSON array
    proven_fix TEXT, recommended_action TEXT, raw_excerpt TEXT,
    PRIMARY KEY (issue_id, source)
);

-- ---- scenarios / test-cases ----
CREATE TABLE IF NOT EXISTS scenarios (
    scenario_id TEXT PRIMARY KEY,
    agent TEXT, family TEXT, persona_file TEXT, language TEXT,
    title TEXT, situation TEXT, backing_call_uuid TEXT,
    checklist_ref TEXT, source_file TEXT
);

-- ---- test runs ----
CREATE TABLE IF NOT EXISTS test_runs (
    call_uuid TEXT PRIMARY KEY,            -- full uuid (API) or 8-char prefix (TEST_LOG)
    bot_target_id TEXT, agent_uuid TEXT, scenario_id TEXT,
    result TEXT, d_patterns TEXT,          -- JSON array
    outcome TEXT, duration INTEGER,
    notes TEXT, is_test INTEGER, source TEXT, started_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_testruns_bot ON test_runs(bot_target_id);

-- ---- deploys (canonical: deploy-history.md; joins versions via snapshot_label) ----
CREATE TABLE IF NOT EXISTS deploys (
    deploy_id TEXT PRIMARY KEY,            -- hash(ts|target_id)
    ts TEXT, env TEXT, target_id TEXT, agent_uuid TEXT, file_path TEXT,
    sha256_8 TEXT, snapshot_label TEXT, result TEXT, tag TEXT
);
CREATE INDEX IF NOT EXISTS ix_deploys_target ON deploys(target_id);
CREATE INDEX IF NOT EXISTS ix_deploys_snap ON deploys(snapshot_label);

-- ---- fixes / prompt-edits (canonical: <Agent>/CHANGELOG.md) ----
CREATE TABLE IF NOT EXISTS fixes (
    fix_id TEXT PRIMARY KEY,               -- hash(agent|date|title)
    date TEXT, agent TEXT, title TEXT, feedback TEXT, change_desc TEXT,
    files TEXT, deployed_targets TEXT, snapshot_labels TEXT,
    ported_from TEXT, d_patterns TEXT, source_file TEXT
);

-- ---- versions (versions/<Agent>/HISTORY.md; label == snapshot_label) ----
CREATE TABLE IF NOT EXISTS versions (
    version_id TEXT PRIMARY KEY,           -- hash(agent|label)
    agent TEXT, ts TEXT, label TEXT, description TEXT, file_count INTEGER
);
CREATE INDEX IF NOT EXISTS ix_versions_label ON versions(label);

-- ---- job runner ----
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    type TEXT, mode TEXT, scope TEXT,      -- scope JSON {bot|issue_id|scenario_id}
    state TEXT, session_id TEXT, operation_id TEXT,
    exit_reason TEXT, created_at TEXT, updated_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_jobs_state ON jobs(state);
CREATE TABLE IF NOT EXISTS job_events (
    job_id TEXT, seq INTEGER, ts TEXT, kind TEXT, stage TEXT, payload TEXT,
    PRIMARY KEY (job_id, seq)
);
CREATE TABLE IF NOT EXISTS job_artifacts (
    job_id TEXT, name TEXT, path TEXT, kind TEXT,
    PRIMARY KEY (job_id, name)
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(CONTROL_DB, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    CONTROL_DB.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as c:
        c.executescript(SCHEMA)
        # seed bot_label_map from config (idempotent)
        for label, tid in BOT_LABEL_MAP.items():
            c.execute(
                "INSERT INTO bot_label_map(label,target_id,note) VALUES(?,?,?) "
                "ON CONFLICT(label) DO UPDATE SET target_id=excluded.target_id",
                (label, tid, "seed:bug-fix-skill"),
            )
    return CONTROL_DB


if __name__ == "__main__":
    p = init_db()
    print("initialised", p)
