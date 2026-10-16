"""Central paths + constants for the Bot Control Center backend.

All paths resolve relative to the Prompt Tuner repo root so the backend reuses the
existing scripts, raya/.env, secrets/, and data files IN PLACE (no copies).
"""
from __future__ import annotations
import os
from pathlib import Path

# backend/ -> control-center/ -> repo root
BACKEND_DIR = Path(__file__).resolve().parent
CC_DIR = BACKEND_DIR.parent
REPO = CC_DIR.parent

# --- reused repo assets ---
SCRIPTS = REPO / "scripts"
RAYA_DIR = REPO / "raya"
AGENTS_JSON = RAYA_DIR / "agents.json"
DEPLOY_HISTORY = RAYA_DIR / "deploy-history.md"
OVERNIGHT = RAYA_DIR / "overnight"
PERSONAS = RAYA_DIR / "personas"
SCENARIO_CATALOG = PERSONAS / "scenario-catalog.md"
CHECKLISTS = REPO / ".claude" / "skills" / "voice-test" / "reference" / "checklists"
VERSIONS = REPO / "versions"
SECRETS = REPO / "secrets"
GSHEETS_SA = SECRETS / "gsheets-sa.json"

AGENT_DIRS = {"KKB": REPO / "KKB", "DKB": REPO / "DKB", "Maya": REPO / "Maya"}

# --- control-center local store ---
CONTROL_DB = CC_DIR / "control.db"
RUNS_DIR = CC_DIR / "runs"

# --- external services ---
SHEET_ID = "1cqT9EVk_vap16wJ3fQM7txLklf-kbMDHdYWsiHImbHU"
SHEET_TAB = "All Issues"
# Sheet columns A..L (see .claude/skills/bug-fix/SKILL.md)
SHEET_COLS = ["date", "status", "bot_label", "title", "type", "description",
              "owner", "priority", "eta", "call_ids_raw", "comments", "fixed_note"]
SHEET_STATUS_VOCAB = [
    "Open", "Accepted to Fix", "Fixed for UAT",
    "Flagged - Backend Issue", "Rejected / Not an Issue", "Closed",
]

# Voice-test harness identity (from .claude/skills/voice-test/SKILL.md)
TESTER_UUID = "f60e0899-aa3a-4be7-9b4f-0296bd28ef48"
TESTER_DID_10 = "7946350285"   # 91 prepended via country_code
TESTER_MAX_CALL_MIN = 4         # never raise

# Sheet "Bot" label -> agents.json target id (bug-fix SKILL.md table).
# Seeds bot_label_map; user-extensible in the DB.
BOT_LABEL_MAP = {
    "KKB (Ghaziabad)": "kkb-hi-out",
    "KKB Kannada": "kkb-kn-out",
    "KKB placeholder Inbound": "kkb-hi-in",
    "KKB Kannada Inbound": "kkb-kn-in",
    "KKB HE": "maya-hi-out",
    "KKB HE Inbound": "maya-hi-in",
    "DKB (Ghaziabad)": "dkb-hi-out",
    "DKB": "dkb-hi-out",
    "DKB Kannada": "dkb-kn-out",
    "KKB": "kkb-hi-out",
    "Maya": "maya-hi-out",
}

# Env keys the child claude process must NOT see, so auth resolves to the login.
SCRUB_CHILD_ENV = [
    "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN",
    "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX",
]

PY = os.environ.get("CC_PYTHON", "python3")
CLAUDE_BIN = os.environ.get("CC_CLAUDE_BIN", "claude")
