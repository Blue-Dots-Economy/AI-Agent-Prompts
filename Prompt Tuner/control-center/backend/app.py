"""Bot Control Center — FastAPI backend.

Read API over control.db + ingest refresh. Job endpoints are added by the
job_runner phase. Runs LOCALLY (it later spawns the `claude` CLI + reaches secrets)."""
from __future__ import annotations
import asyncio
import json
import subprocess
import threading
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import queries
from config import BACKEND_DIR, CC_DIR, PY, RUNS_DIR
from db import init_db, get_conn
from job_runner.manager import MANAGER
from job_runner.discovery import engine_status

app = FastAPI(title="Bot Control Center", version="0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"], allow_headers=["*"],
)

_ingest_lock = threading.Lock()
_ingest_state = {"running": False, "last": None}


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/api/health")
def health():
    return {"ok": True, "ingest": _ingest_state}


@app.get("/api/stats")
def stats():
    return queries.stats()


@app.get("/api/bots")
def bots():
    return queries.list_bots()


@app.get("/api/bots/{target_id}")
def bot(target_id: str):
    b = queries.get_bot(target_id)
    if not b:
        raise HTTPException(404, "unknown bot")
    return b


@app.get("/api/issues")
def issues(status: str = Query(None), bot: str = Query(None),
           owner: str = Query(None), priority: str = Query(None)):
    return queries.list_issues(status, bot, owner, priority)


@app.get("/api/scenarios")
def scenarios(agent: str = Query(None)):
    return queries.list_scenarios(agent)


@app.get("/api/test-matrix")
def test_matrix():
    return queries.test_matrix()


@app.get("/api/deploys")
def deploys():
    return queries.list_table("deploys", order="ts DESC")


@app.get("/api/fixes")
def fixes():
    return queries.list_table("fixes", order="date DESC")


@app.get("/api/versions")
def versions():
    return queries.list_table("versions", order="ts DESC")


def _do_ingest(mode: str):
    try:
        subprocess.run([PY, "-m", "ingest", mode], cwd=str(BACKEND_DIR),
                       capture_output=True, text=True, timeout=300)
    finally:
        with _ingest_lock:
            _ingest_state.update(running=False, last=mode)


@app.post("/api/ingest/refresh")
def ingest_refresh(mode: str = Query("--all")):
    with _ingest_lock:
        if _ingest_state["running"]:
            return {"queued": False, "reason": "already running"}
        _ingest_state["running"] = True
    threading.Thread(target=_do_ingest, args=(mode,), daemon=True).start()
    return {"queued": True, "mode": mode}


# ---------------- Fix / Test engine ----------------
@app.get("/api/engine")
def engine():
    return engine_status()


@app.post("/api/jobs")
async def start_job(body: dict = Body(...)):
    kind = body.get("kind", "bugfix")          # bugfix | propose | voice-test
    mode = body.get("mode", "autonomous")       # autonomous | checkpoint | propose-only
    scope = body.get("scope") or {}
    if body.get("issue_id"):
        with get_conn() as c:
            r = c.execute("SELECT * FROM issues WHERE issue_id=?", (body["issue_id"],)).fetchone()
            if r:
                scope = {"target_id": r["target_id"], "issue": dict(r)}
    if not scope.get("target_id"):
        raise HTTPException(400, "scope.target_id or a known issue_id required")
    return await MANAGER.start(kind, mode, scope)


@app.get("/api/jobs")
def list_jobs():
    with get_conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT job_id,type,mode,state,operation_id,exit_reason,created_at,updated_at "
            "FROM jobs ORDER BY created_at DESC LIMIT 60")]


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    with get_conn() as c:
        j = c.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if not j:
            raise HTTPException(404, "unknown job")
        j = dict(j)
        j["scope"] = json.loads(j.get("scope") or "{}")
        j["events"] = [json.loads(e["payload"]) for e in c.execute(
            "SELECT payload FROM job_events WHERE job_id=? ORDER BY seq", (job_id,))]
        j["artifacts"] = [dict(a) for a in c.execute(
            "SELECT name,kind FROM job_artifacts WHERE job_id=?", (job_id,))]
    vp = RUNS_DIR / job_id / "artifacts" / "verdict.json"
    j["verdict"] = json.loads(vp.read_text()) if vp.exists() else None
    return j


@app.post("/api/operations/{op}/approve")
async def approve(op: str):
    return await MANAGER.approve(op)


@app.post("/api/operations/{op}/reject")
async def reject(op: str):
    return await MANAGER.reject(op)


@app.websocket("/ws/jobs/{key}")
async def ws_jobs(ws: WebSocket, key: str):
    await ws.accept()
    q = MANAGER.subscribe(key)   # key = job_id, or "*" for the global feed
    try:
        # replay existing events for a specific job so late subscribers catch up
        if key != "*":
            with get_conn() as c:
                for e in c.execute("SELECT payload FROM job_events WHERE job_id=? ORDER BY seq", (key,)):
                    await ws.send_text(e["payload"])
        while True:
            ev = await q.get()
            await ws.send_text(json.dumps(ev))
    except WebSocketDisconnect:
        pass
    finally:
        MANAGER.unsubscribe(key, q)


# Serve the cockpit (mounted last so /api/* routes win). Same-origin -> no CORS needed.
_frontend = CC_DIR / "frontend"
if _frontend.exists():
    app.mount("/", StaticFiles(directory=str(_frontend), html=True), name="cockpit")
