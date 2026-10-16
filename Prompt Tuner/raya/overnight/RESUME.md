# RESUME — autonomous overnight run (durable restart anchor)

**If you are a fresh Claude Code session (or a scheduled/cron wake-up) and see this: the user
(Parth) set an autonomous overnight mandate and went to sleep. RESUME THE RUN. Do NOT wait for the
user.** A usage limit may have paused/killed the previous session; the timer was said to reset ~3h
after ~00:40 IST 2026-07-30 (so ≈ 03:40 IST). When quota is back, continue.

## How to resume (do this)
1. Read `raya/overnight/OVERNIGHT_RUN.md` (this dir) — the single source of truth: GOAL, SAFETY
   RULES, INVENTORY (all uuids/paths), PLAN with checkboxes, PROGRESS LOG, and **NEXT ACTION**.
   (A copy also lives in the session scratchpad; the repo copy here is the durable one.)
2. Read `raya/overnight/TEST_LOG.md` and `raya/overnight/PRIORITY_BUGS.md` (if present) for what's
   tested/found so far.
3. Continue from **NEXT ACTION**, obeying every SAFETY RULE (snapshot before edits; revert on
   regression; NO fix without a reproducing transcript; voice-test EVERY bot you change — repro
   call then verify call, graded against `.claude/skills/voice-test/reference/checklists/`; sync
   Hindi↔Kannada; prefer PORTING proven fixes; dicey→open-items; sequential voice tests; never raise
   tester max_call_duration above 4 min; changelog + analyser on every fix).
4. Keep the PROGRESS LOG + NEXT ACTION updated here in the repo (not just scratchpad) so the next
   restart is clean. Commit + push at checkpoints.

## Deliverables owed by morning (see OVERNIGHT_RUN.md → DELIVERABLES)
Test all bots (KKB in+out Hi/Kn, DKB Hi/Kn, Maya Hi in+out, 2 Signals); fix high-priority issues
safely (port proven fixes, revert on fail, nothing broken); Excel report of issues/tests/fixes;
open-items list for the user; improvement ideas; update existing skills; keep the system coherent
+ demo-ready. Bonus (only if time): 5 combined `${call_direction}` bots (new agents, don't touch
live); then port those to Signals.

## Fast facts
- Tester agent `f60e0899-aa3a-4be7-9b4f-0296bd28ef48`, inbound DID `917946350285` (dial 10-digit
  `7946350285`). Persona swap: `scripts/raya_testcall.py persona <uuid> <file>`; language:
  `... lang hi|kn`. Fire+grade a call: `scripts/raya_testrun.py <bot_uuid> 7946350285 <args.json>
  <tester_uuid> "<label>"`.
- Bot uuids + backends + arg shapes are in OVERNIGHT_RUN.md (INVENTORY + the merge findings).
- Restart mechanisms in place: recurring cron (session-only), a durable scheduled task (fires ~after
  reset), and a saved memory pointing here. Any of them (or the user returning) should land you here.
- Secrets live in git-ignored `raya/.env` / `raya/snapshots/` — never commit them.
