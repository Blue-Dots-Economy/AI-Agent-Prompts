"""Job orchestrator: spawn (real claude CLI or sim), stream events over WS, persist,
and drive the risk-gated two-job flow (diagnose -> policy -> auto/await -> deploy)."""
from __future__ import annotations
import asyncio
import json
import os
import time
import uuid
from pathlib import Path

from config import REPO, RUNS_DIR, SCRUB_CHILD_ENV
from db import get_conn
from security import scrub
from job_runner import prompts, sim, policy
from job_runner.discovery import engine_status
from job_runner.stage_hook import write_settings

# ---- allowlists per mode (used only for the real CLI path) ----
_READ = ["Read", "Grep", "Glob",
         "Bash(python3 scripts/gsheets.py get:*)", "Bash(python3 scripts/gsheets.py meta:*)",
         "Bash(python3 scripts/raya_call.py:*)",
         "Bash(python3 scripts/raya_deploy.py diff:*)", "Bash(python3 scripts/raya_deploy.py status:*)",
         "Bash(python3 scripts/raya_deploy.py verify:*)"]
_EDIT = _READ + ["Edit", "Write", "MultiEdit",
                 "Bash(bash scripts/prompt-version.sh save:*)",
                 "Bash(python3 scripts/raya_deploy.py pull:*)", "Bash(git:*)"]
_DEPLOY = _EDIT + ["Bash(python3 scripts/raya_deploy.py deploy:*)",
                   "Bash(python3 scripts/raya_testrun.py:*)", "Bash(python3 scripts/raya_testcall.py:*)",
                   "Bash(python3 scripts/gsheets.py update:*)"]
ALLOW = {"diagnose": _EDIT, "propose": _READ, "deploy": _DEPLOY, "voice-test": _DEPLOY}
# propose = default mode + read-only allowlist (edits/deploy simply not allowlisted -> can't mutate);
# plan mode can over-restrict read-only Bash, so default is used for a reliable read-only diagnose.
PERM_MODE = {"diagnose": "acceptEdits", "propose": "default", "deploy": "acceptEdits", "voice-test": "acceptEdits"}


class Manager:
    def __init__(self):
        self.subs: dict[str, set[asyncio.Queue]] = {}   # job_id (and "*") -> queues
        self.pending: dict[str, dict] = {}               # operation_id -> {scope, decision, diagnose_job}
        self.lanes = {"voice-test": asyncio.Semaphore(1), "deploy": asyncio.Semaphore(1)}

    # ---------- WS pub/sub ----------
    def subscribe(self, key: str) -> asyncio.Queue:
        q = asyncio.Queue()
        self.subs.setdefault(key, set()).add(q)
        return q

    def unsubscribe(self, key: str, q: asyncio.Queue):
        self.subs.get(key, set()).discard(q)

    async def _emit(self, job_id: str, event: dict):
        event = {**event, "job_id": job_id, "t": time.strftime("%H:%M:%S")}
        # persist
        with get_conn() as c:
            seq = (c.execute("SELECT COALESCE(MAX(seq),0)+1 FROM job_events WHERE job_id=?", (job_id,)).fetchone()[0])
            c.execute("INSERT INTO job_events(job_id,seq,ts,kind,stage,payload) VALUES(?,?,?,?,?,?)",
                      (job_id, seq, event["t"], event.get("kind"), event.get("stage"), json.dumps(event)))
        for key in (job_id, "*"):
            for q in list(self.subs.get(key, ())):
                q.put_nowait(event)

    def _set_state(self, job_id, state, exit_reason=None):
        with get_conn() as c:
            c.execute("UPDATE jobs SET state=?, exit_reason=COALESCE(?,exit_reason), updated_at=datetime('now') WHERE job_id=?",
                      (state, exit_reason, job_id))

    # ---------- job records ----------
    def _new_job(self, kind, mode, scope, operation_id, session_id=None) -> str:
        job_id = f"{operation_id}-{kind[:3]}"
        with get_conn() as c:
            c.execute("INSERT OR REPLACE INTO jobs(job_id,type,mode,scope,state,session_id,operation_id,created_at,updated_at)"
                      " VALUES(?,?,?,?,?,?,?,datetime('now'),datetime('now'))",
                      (job_id, kind, mode, json.dumps(scope), "queued", session_id, operation_id))
        return job_id

    # ---------- driver (real CLI or sim) ----------
    async def _run(self, job_id: str, kind: str, mode: str, scope: dict):
        run_dir = RUNS_DIR / job_id
        art = run_dir / "artifacts"
        art.mkdir(parents=True, exist_ok=True)
        eng = engine_status()
        self._set_state(job_id, "running")
        await self._emit(job_id, {"kind": "state", "state": "running", "engine": eng["mode"]})

        if eng["mode"] == "sim":
            async for ev in sim.simulate(kind, scope, art):
                await self._pipe(job_id, ev)
        else:
            await self._run_real(job_id, kind, scope, run_dir, art, eng["claude_bin"])

    async def _pipe(self, job_id, ev):
        # tool events with a stage double as stage-rail advances
        await self._emit(job_id, ev)
        if ev.get("kind") == "tool" and ev.get("stage"):
            await self._emit(job_id, {"kind": "stage", "stage": ev["stage"]})

    async def _run_real(self, job_id, kind, scope, run_dir, art, claude_bin):
        prompt = prompts.PROMPT_FN[kind](job_id, scope, str(art))
        (run_dir / "prompt.txt").write_text(prompt)
        settings = run_dir / "settings.json"
        events_file = run_dir / "stage-events.jsonl"
        write_settings(settings, Path(__file__).parent / "stage_hook.py", events_file)
        argv = [claude_bin, "-p", prompt, "--output-format", "stream-json", "--verbose",
                "--permission-mode", PERM_MODE[kind], "--add-dir", str(REPO),
                "--allowedTools", ",".join(ALLOW[kind]), "--settings", str(settings)]
        env = {k: v for k, v in os.environ.items() if k not in SCRUB_CHILD_ENV}
        env["CC_JOB_EVENTS"] = str(events_file)
        proc = await asyncio.create_subprocess_exec(
            *argv, cwd=str(REPO), env=env,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        from job_runner.stream import parse_stream
        async for ev in parse_stream(proc):
            await self._pipe(job_id, ev)
        await proc.wait()

    # ---------- orchestration ----------
    async def start(self, kind: str, mode: str, scope: dict) -> dict:
        """kind: 'bugfix' | 'propose' | 'voice-test'. Returns {operation_id, job_id}."""
        op = "op-" + uuid.uuid4().hex[:8]
        if kind == "voice-test":
            jid = self._new_job("voice-test", mode, scope, op)
            asyncio.create_task(self._finish_single(jid, "voice-test", mode, scope))
            return {"operation_id": op, "job_id": jid}
        first = "propose" if (kind == "propose" or mode == "propose-only") else "diagnose"
        jid = self._new_job(first, mode, scope, op)
        asyncio.create_task(self._finish_diagnose(op, jid, first, mode, scope))
        return {"operation_id": op, "job_id": jid}

    async def _finish_single(self, jid, kind, mode, scope):
        await self._run(jid, kind, mode, scope)
        self._set_state(jid, "done")
        await self._emit(jid, {"kind": "state", "state": "done"})

    async def _finish_diagnose(self, op, jid, kind, mode, scope):
        await self._run(jid, kind, mode, scope)
        verdict_path = RUNS_DIR / jid / "artifacts" / "verdict.json"
        decision = policy.decide(verdict_path)
        with get_conn() as c:
            c.execute("INSERT OR REPLACE INTO job_artifacts(job_id,name,path,kind) VALUES(?,?,?,?)",
                      (jid, "verdict.json", str(verdict_path), "verdict"))
        await self._emit(jid, {"kind": "verdict", "decision": decision})
        if kind == "propose":
            self._set_state(jid, "done", "propose-only")
            await self._emit(jid, {"kind": "state", "state": "done"})
            return
        if decision["auto"] and mode not in ("checkpoint", "always-checkpoint"):
            self._set_state(jid, "done")
            await self._emit(jid, {"kind": "state", "state": "done"})
            await self._deploy(op, scope, auto=True)
        else:
            self._set_state(jid, "awaiting-approval", decision["reason"])
            self.pending[op] = {"scope": scope, "decision": decision, "diagnose_job": jid}
            await self._emit(jid, {"kind": "state", "state": "awaiting-approval",
                                   "reason": decision["reason"], "flags": decision["flags"]})

    async def _deploy(self, op, scope, auto=False):
        jid = self._new_job("deploy", "auto" if auto else "approved", scope, op)
        async with self.lanes["deploy"]:
            await self._emit(jid, {"kind": "state", "state": "running", "trigger": "auto" if auto else "approved"})
            await self._run(jid, "deploy", "deploy", scope)
        self._set_state(jid, "done")
        await self._emit(jid, {"kind": "state", "state": "done"})
        return jid

    async def approve(self, op):
        p = self.pending.pop(op, None)
        if not p:
            return {"ok": False, "reason": "no pending operation"}
        jid = await self._deploy(op, p["scope"], auto=False)
        return {"ok": True, "deploy_job": jid}

    async def reject(self, op):
        p = self.pending.pop(op, None)
        if not p:
            return {"ok": False, "reason": "no pending operation"}
        self._set_state(p["diagnose_job"], "cancelled", "rejected by user")
        await self._emit(p["diagnose_job"], {"kind": "state", "state": "cancelled",
                                             "note": "rejected — restore the pre-fix snapshot to roll back"})
        return {"ok": True}


MANAGER = Manager()
