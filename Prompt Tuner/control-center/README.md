# Bot Control Center

A mission-control cockpit over the Prompt Tuner bot fleet, plus a **Fix/Test engine that drives Claude Code itself** — no Anthropic API. One place to see every bot's state, open issues by priority, test coverage, drift-vs-live, and deploy/version history; one click to run the full `/bug-fix` or `/voice-test` loop with live "what stage is happening now" streaming.

## Why it must run locally

The Fix/Test engine works by **spawning the `claude` CLI headless** (`claude -p … --output-format stream-json`), which runs in *this* repo with *these* skills + `CLAUDE.md` — i.e. it *is* the Prompt Tuner, non-interactive. It authenticates via **your existing Claude Code login (your plan)**, not an API key. So:

- Run the backend **as the same macOS user** that is logged into Claude Code (not a daemon, not another uid, not a container), or the login isn't visible.
- The spawner **strips `ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN`** from the child env so auth always resolves to your subscription login.
- It also reaches `raya/.env` + `secrets/gsheets-sa.json`, so it can't be pure-serverless (Vercel). A read-only view *can* deploy to Vercel; the Fix buttons only work on the local machine.

## Layout

```
backend/          FastAPI app (reuses ../scripts/*.py + ../raya/.env in place)
  ingest/         one parser per data source → control.db  ("port all bot data")
  job_runner/     the headless-claude engine (spawn, stream→stages, risk-gate, scheduler)
  api/            REST + WebSocket
frontend/         Vite + React + Tailwind + Recharts cockpit (kkb-dashboard-style)
runs/<job_id>/    per-job prompt, settings/hook, raw stream, stage events, artifacts  (gitignored)
control.db        SQLite cache + job/history store  (gitignored)
```

## Setup / run

1. `cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r ../requirements.txt`
2. Ensure `../secrets/gsheets-sa.json` exists and `../raya/.env` has `RAYA_ENV=prod`.
3. Ingest the fleet data:  `python -m ingest --all`  (populates `../control-center/control.db`)
4. `uvicorn app:app --port 8787 --reload`
5. `cd ../frontend && npm i && npm run dev`  → open the cockpit (proxies to `:8787`).

## Data model

The Google Sheet `All Issues` stays the **canonical issue tracker** — the cockpit reads and writes it. `control.db` is a cache/read-model + the job/history store. Everything joins on `target_id` (from `raya/agents.json`), plus three cross-source keys: **call_uuid**, **d_pattern**, **snapshot_label**.

See `../../.claude/plans/synthetic-nibbling-ladybug.md` for the full design.
