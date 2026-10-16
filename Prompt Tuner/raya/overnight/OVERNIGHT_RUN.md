# OVERNIGHT AUTONOMOUS RUN — state + plan (single source of truth)

Started 2026-07-29 late night (IST). User asleep; autonomous mandate. Resume from **NEXT ACTION**
on every re-invocation (background-task completion OR cron heartbeat). Keep this file updated.

## GOAL (user's words, distilled)
Wake up to: all bots significantly improved + fixed, **nothing broken**; new skills created;
an **Excel report** of issues found / test cases run / what got fixed / what needed recurring
rounds; a separate **open-items list** for the user (only truly-dicey decisions — otherwise just
fix); improvement ideas; all existing skills updated with today's learnings; the whole
test→fix→deploy system coherent and demo-ready.

## SAFETY RULES (never violate — "nothing broken" is the hard constraint)
1. **Snapshot before every prompt edit.** `scripts/raya_deploy.py deploy` auto-snapshots + GET-backup
   + read-back verify. Also `scripts/prompt-version.sh save` for extra safety.
2. **Revert on any regression.** If a deploy read-back fails, or a post-deploy test shows worse
   behavior than before, restore the snapshot and redeploy the known-good version. Log it.
3. **No fix without a reproducing transcript.** Static/analyser findings must be confirmed by a real
   call before editing a live prompt. If no repro, log to open-items (don't guess-fix).
4. **Prefer PORTING proven fixes** (location-required, live-selection D37, enum-mapping D38, phone
   D39, role-update) over reinventing — but ONLY where the backend matches (Signals fixes apply to
   Signals bots only; up-getjob/up-postjob bots are different).
5. **Sync Hindi↔Kannada; never deploy a drifted pair.** Maya is Hindi-only.
6. **Dicey/ambiguous → open-items list, do NOT touch the live prompt.** Cap autonomous fix→deploy
   cycles at 2 per bot to avoid thrashing.
7. **Tool-adherence misses → tool-schema lever, not more prose** (D25/D40). Backend/data issues →
   escalate to open-items, never experiment on the live flow.
8. **Voice tests are SEQUENTIAL** (one tester line; callee gets no agent_args; burst-throttle).
   Approach B (pipeline PATCH→fire→wait-answer→next) only if bridging is behaving; else pure
   sequential. If a call fails to bridge, retry (runner does); after repeated fails, cool down 2+ min.
9. **Never raise tester max_call_duration above 4 min.** May lower temporarily for short smokes.
10. **Changelog + analyser entry for every bug fix** (bug-fix feedback loop).
11. **VOICE-TEST EVERY BOT I CHANGE (mandatory, per user).** For each bot I modify: (a) a PRE-fix
    repro call that confirms the bug via the harness; (b) the fix; (c) a POST-fix verify call that
    confirms the fix AND regression-checks the happy path, graded against generic.md + the bot's
    checklist. Nothing ships without a passing post-fix call. Re-test the language twin too. If a
    call can't bridge after retries, cool down and retry; if truly stuck, mark the fix
    "deployed, verify pending" in the report (never claim verified without a post-deploy transcript).

## INVENTORY
- Tester: "Testing Agent- Blue Dots" `f60e0899-aa3a-4be7-9b4f-0296bd28ef48`, inbound DID `917946350285`
  (dial as 10-digit `7946350285`), non-interruptable, max_dur 4. Persona swapped via
  `scripts/raya_testcall.py persona <uuid> <file>`; language via `... lang hi|kn`.
- Bots (uuid | backend | direction | testable-via-harness?):
  - KKB Hi Signals `115b38a5-42ef-4082-be69-84a871bb226a` | Signals | outbound | YES (primary; heavily tested)
  - KKB Kn Signals `33037201-78ce-405d-b509-a3b6934e20f1` | Signals | outbound | YES (UNTESTED twin — priority)
  - KKB Hi out `da612923-1927-45d7-9ad0-b1c7cbb15294` | up-getjob | outbound | YES
  - KKB Kn out `87ab9108-5d66-4a13-a20a-575eaa9aae36` | up-getjob | outbound | YES
  - DKB Hi `57814ac8-5d79-41f5-bab7-bcfe2d9aac4f` | up-postjob | outbound(employer) | YES (needs employer persona + DKB args)
  - DKB Kn `d1a1614f-fa7e-41c1-8963-e7f3af213a13` | up-postjob | outbound(employer) | YES
  - Maya Hi out `47fdffe6-0cb0-4fcf-8762-135ddadfb194` | up-getjob(campus) | outbound | YES (student persona + college_name)
  - KKB Hi in `b6222233...`, KKB Kn in `4ac90bf1...`, Maya Hi in `df99f501...` | inbound | ??? (can an inbound agent place an outbound call? TEST once; if not, flag not-harness-testable)
- Harness scripts: `scripts/raya_testcall.py` (persona/lang/call/whoami), `scripts/raya_testrun.py`
  (fire+poll+dump, connect-retry), `scripts/raya_call.py` (read past calls).
- Checklists: `.claude/skills/voice-test/reference/checklists/{generic,kkb,dkb,maya}.md`.
- Personas: `raya/personas/*.md`. Scenario catalog: `raya/personas/scenario-catalog.md`.
- Known-good agent_args live in each bot's recent calls (pull via `raya_call.py <uuid>`).
- Signals test profile lives under the tester DID (role drifts as tests update it — fine).

## DELIVERABLES (for the morning)
- [ ] `/voice-test` skill (DONE — SKILL.md + 4 checklists staged).
- [x] `/onboard` skill (DONE — registered).
- [ ] Existing skills updated with today's learnings (Signals mechanics, harness, D40, role-update, 1:1).
- [ ] Excel report: issues found / tests run / fixed / recurring — `reports/overnight-YYYY-MM-DD.xlsx`.
- [ ] Open-items list for the user (dicey/decision bugs + backend escalations) — markdown.
- [ ] Improvement ideas + demo-packaging notes — markdown.
- [ ] All fixes committed + pushed; deploy-history + changelog + analyser updated.

## SCOPE ADDENDUM (user, ~00:05 IST 2026-07-30)
- **"All bots" = the FULL set:** KKB inbound + outbound, Hindi + Kannada; DKB (Hi + Kn); Maya (Hi
  out + in). Inbound must be covered too. Harness reality: it triggers the bot to CALL the tester,
  which tests **outbound** behavior. To test an INBOUND bot properly the tester must DIAL the bot's
  in_did (tester needs an out_did — it has none). PLAN for inbound: (a) static analysis (done in the
  workflow), (b) review historical real inbound transcripts (scenario-catalog + `raya_call.py`),
  (c) PROBE whether the tester can be given an out_did to dial an inbound bot; if infeasible, log to
  open-items and cover inbound via (a)+(b). Do NOT force a broken inbound harness.
- **New auto-variable `${call_direction}`** → "inbound" | "outbound" (Raya replaces it). Useful for
  the combined bots below, and note wherever a prompt should branch on direction.
- **Create-agent API available:** `POST /api/agent` (name, instructions, output_fields,
  output_instructions, dids, language_id, voice_id, tools, durations, say_hello, etc.). Lets us mint
  new agents programmatically. (Auth = same key already in raya/.env; never commit it.)
- **BONUS (only if core is done + time remains; gated on confidence):** build **5 combined
  inbound+outbound bots** — KKB Hi, KKB Kn, DKB Hi, DKB Kn, Maya Hi — each a SINGLE prompt that
  branches on `${call_direction}` (merging today's separate inbound/outbound prompts). These are
  NON-Signals (up-getjob / up-postjob). Test + COMPARE vs the standard split bots; **do NOT migrate
  / replace the live bots** — only report readiness so the user decides. Create them as NEW agents
  (POST /api/agent) so nothing existing is touched.
- **FURTHER BONUS (only if all above done):** port the 5 combined bots to Signals too.

## PLAN / PHASES  (checkbox = done)
### Phase 0 — setup (DONE)
- [x] Approach B chosen; /voice-test skill written; checklists staged; plan file created.
- [x] Cron heartbeat set — job 15487546, fires :13/:43 each hour, ONLY when REPL idle → clean cooldown-resume, no double-dispatch. (Auto-expires after 7 days.)
- [x] /onboard skill authored + registered (SKILL.md + reference/intake-template.md).
- [x] Static-analysis workflow launched (wf_4fd4ce5d) — 8 bots → scratchpad/analysis/<key>.md.
- [x] KKB Kn Signals cooperative test launched (bivpyhtqa) — first Phase-2 call.

### Phase 1 — static analysis (parallel, no calls) → prioritized bug list
- [ ] Analyse each bot's live prompt against analyser bug-patterns + checklists → structured findings
  (severity, symptom, whether a proven sibling fix exists, needs-transcript-to-confirm). Output:
  scratchpad/analysis/<bot>.md + a merged prioritized list scratchpad/PRIORITY_BUGS.md.

### Phase 2 — sequential voice testing (confirm high-priority findings + regression the happy paths)
Test matrix (persona × bot), sequential. Start with the untested/priority:
- [ ] KKB Kn Signals — cooperative(existing), not-interested, wants-different (needs KN personas + lang kn).
- [ ] KKB Hi/Kn out (up-getjob) — cooperative, not-interested (needs up-getjob args + seeker persona).
- [ ] DKB Hi/Kn — employer happy-path, wrong-number, "talk now" (needs DKB args + employer persona).
- [ ] Maya Hi out — student intro/gate (needs college_name + student persona).
- [ ] (one) inbound-agent trigger probe → testable or not.
Log every call (uuid, scenario, pass/fail per checklist, issues) to scratchpad/TEST_LOG.md.

### Phase 3 — fix high-priority (conservative, ported, reverted-on-fail)
- [ ] For each confirmed high-priority bug: port a proven fix or make the smallest surgical edit;
  snapshot→deploy→re-test→revert-on-regress; changelog + analyser. Cap 2 cycles/bot. Dicey→open-items.

### Phase 4 — report + skills + packaging
- [ ] Build the Excel report (xlsx skill). Build open-items + ideas markdown. Update all existing
  skills. Verify system coherence. Commit + push everything. Write a morning summary.

## PROGRESS LOG (append-only; newest at bottom)
- 2026-07-29 ~23:50 IST — Phase 0. /voice-test skill written; checklists staged (generic47/kkb51/dkb39/maya60); runner productionized to scripts/raya_testrun.py. Approach B confirmed.
- 2026-07-30 ~00:05 IST — Phase 0 DONE: cron heartbeat 15487546 set; /onboard skill done+registered; static-analysis workflow wf_4fd4ce5d launched (8 bots); KKB Kn Signals cooperative test launched (bivpyhtqa). Scope expanded (inbound too, ${call_direction}, create-agent API, bonus combined bots).
- KKB HI SIGNALS results already banked today (pre-plan): new-seeker apply bug (location→draft→PROFILE_NOT_LIVE) FIXED (location required on both Signals bots); existing-seeker happy path PASS; not-interested PASS; wants-different PASS; role-mismatch→update-role feature ADDED + verified; 1:1 live-selection verified. Changelog + analyser D40 logged.
- 2026-07-30 ~00:20 IST — KKB Kn Signals cooperative PASS (b3ef7abe; full parity w/ Hindi). Checkpoint committed+pushed (e7663c8: skills, harness scripts, personas, catalog, Signals role-update+1:1, D40). TEST_LOG.md seeded. DKB employer + Maya student personas staged. AWAITING static-analysis workflow to build PRIORITY_BUGS, then targeted confirm-calls + fixes on production bots.

## TEST LOG POINTER → scratchpad/TEST_LOG.md (create + append every call: uuid, bot, scenario, pass/fail per checklist, issues). PRIORITY_BUGS → scratchpad/PRIORITY_BUGS.md (merge from analysis/).

- 2026-07-30 ~00:35 IST — Static analysis DONE (8 bots). HIGH cluster: kkb-hi-in D31 (create→apply batched→empty profile_id, x2), kkb-kn-out D32 (memory substitutes for get_profile), kkb-hi-out + maya-hi +91-double-prefix, kkb-hi-signals stale D39 phone bullet. Merge+ground subagent dispatched (aa81e181) → PRIORITY_BUGS.md with ACTIVE/LATENT classification from real transcripts. **Discovery: production outbound bots pass contact_phone WITH +91 (e.g. +91XXXXXX8821), so the +91-prepend double-prefix finding is likely ACTIVE.** DKB scheduled agent_args are field-misaligned (data/campaign issue, not prompt). Production outbound recent calls mostly outcome=Failure (verify: no-answer vs phone-bug). Tester currently in KANNADA mode + kn cooperative persona.

- 2026-07-30 ~00:45 IST — **RESTART RESILIENCE SET (user warned of imminent usage limit, resets ~03:40 IST).** Canonical state moved to REPO `raya/overnight/` (this file — update HERE going forward, not scratchpad). Mechanisms: (1) durable scheduled task `resume-overnight-run` (~/.claude/scheduled-tasks/, disk-durable, recurring, resumes from raya/overnight/RESUME.md, self-deletes when done); (2) memory `overnight-autonomous-run` + MEMORY.md pointer (auto-loaded → resume); (3) repo anchor committed+pushed (2bada7b). Retired the in-memory cron (superseded). Merge+ground subagent (aa81e181) still running → PRIORITY_BUGS.md.

- 2026-07-30 ~01:00 IST — **Fix A STARTED.** kkb-hi-in D31 two-step (create→WAIT→apply, no batching) **DEPLOYED** (b6222233; rollback snapshot pre-deploy-kkb-hi-in-2026-07-30_003534) — VERIFY-PENDING (inbound, needs a real new-caller call). kkb-kn-in: **reconcile-first required** — live holds a newer real inventory (Burger King/CIEL HR job_ids) the repo lacks; the Kn D31 edit was REVERTED (do NOT deploy the stale repo Kn copy). Changelog updated. Still TODO: add kkb-hi-in/kn-in to analyser D31 "Seen in". Personas hi-employer + hi-student staged.

- 2026-07-30 ~03:15 IST — **NEAR COMPLETE (manual session, auto-restart removed).** Deployed+verified this session: DKB Hi+Kn D5 (close reframe — VERIFIED `90959fdc`) + D34 empty-hold; KKB out Hi+Kn D34 neutral hold (VERIFIED `bz8fjqumk` — hold now "ಒಂದು ನಿಮಿಷ"). DELIVERABLES DONE: REPORT.md + reports/overnight-2026-07-30.xlsx (41 issues/8 tests/8 fixes) + open-items.md + ideas.md; analyser D34 Seen-in; CLAUDE.md registers /voice-test + /onboard. Maya-D31 = false alarm (not present). Maya-out D34 test running (bkk93sfgc, last coverage). REMAINING: grade Maya-out (fix D34 if active); morning summary; (bonus combined ${call_direction} bots = NOT done, out of scope for the night — noted in ideas/open-items). Residuals → open-items (phone-malform, spoken-narration runtime residue, inbound verify-pending, DKB read-back loop).

## NEXT ACTION (grounded 2026-07-30 ~00:50 from raya/overnight/PRIORITY_BUGS.md)
**✅ Fix A+B DONE: KKB inbound PAIR (kkb-hi-in `b6222233` + kkb-kn-in `4ac90bf1`) DEPLOYED both D31 (two-step create→WAIT→apply) + D34 (neutral hold_message); kkb-kn-in reconciled first (real Burger King/CIEL HR inventory preserved). Both VERIFY-PENDING (inbound — need a real inbound call or the tester-out_did probe).**

NEXT: **Fix C (dkb-kn D34/D5 — HARNESS-VERIFIABLE):** make a KN employer persona, pull known-good DKB args, repro→fix (neutral hold on silent create_job; drop the callback-invite close on outbound)→verify call, sync DKB Hi. Then **Maya D31 batching** (analyser flag: Maya out+in still carries "single turn/back to back"; Maya out is harness-testable → repro→fix→verify + Hindi-only). Then **latent findings → open-items.md** (phone double-prefix kkb-hi-out/maya, memory-substitution kkb-kn-out/kkb-hi-in — need a live probe first). Then **Phase 4**: Excel report + open-items + ideas + update existing skills + demo packaging. Also: **run actual voice tests on the outbound production bots** (KKB Hi/Kn out, DKB, Maya out) for regression coverage, sequentially, logging to TEST_LOG.

Merge+ground verdict: MOST static findings are **LATENT** (bots work in real calls) → do NOT edit; log to open-items. Grounded **ACTIVE** fixes, in order:

**A. kkb-hi-in — new-caller apply 404 (D31/D16) [ACTIVE: calls 5449910e, 34f1f587].** New inbound caller: apply_job fired with a FABRICATED profile_id ("up-getjob"/placeholder UUID) and NO create_profile → HTTP 404. (Control 1fde1677 did create→apply → success.) FIX = port kkb-kn-out's D31 two-step (create → WAIT → apply, separate turns) + D16 create-first into kkb-hi-in, sync twin kkb-kn-in. **DECIDE FIRST by reading kkb-hi-in's apply section:** if it ALREADY has the two-step rule → this is runtime tool-adherence (model hallucinated the id) → do NOT pile prose (D25) → OPEN-ITEMS + recommend a tool-schema/platform backstop. If it LACKS the rule → port it (legit additive fix). INBOUND ⇒ cannot harness-verify (tester can't dial the bot) → deploy + mark "verify pending (needs a real inbound call from the user)". Snapshot first.

**B. kkb-hi-in — get_profile hold_message narrates the fetch (D34) [ACTIVE].** hold = "आपकी जानकारी निकल रही है" (spoken). FIX = port the neutral hold ("एक मिनट") from the Signals bots. Safe additive prose swap. Sync twin kkb-kn-in. Inbound ⇒ verify-pending.

**C. dkb-kn — spoken hold on silent create_job (D34) + callback-invite close on outbound (D5) + phoneNumber undeclared [ACTIVE: cf3fc048].** OUTBOUND ⇒ HARNESS-VERIFIABLE (employer persona ready; make a Kannada employer persona). FIX prose (neutral hold; drop callback-invite close for outbound). Sync DKB Hi. Full repro→fix→verify loop. (phoneNumber undeclared returned success → data-quality note, not a break.)

**VERIFY-ONLY (no edit):** kkb-kn-signals D40 location-required — already verified (KN Signals test passed + `location` in create_profile.required).

**CHEAP PROSE HYGIENE (LATENT, optional, snapshot first, both langs):** remove stale "10-digit" phone bullet in kkb-hi/kn-signals (D39 leftover); align maya phone-prefix line. Low-risk hygiene only.

**OPEN-ITEMS (LATENT — do NOT touch live prompts without a live probe):** kkb-hi-out & maya-hi +91 double-prefix; kkb-hi-in & kkb-kn-out memory-substitution. Log with evidence + the port-ready fix so the user can decide.

Then **Phase 4:** Excel report (xlsx) + open-items.md + ideas.md; update existing skills (bug-fix/prompt-analyser with harness + Signals + D40 learnings); commit/push; morning summary. **BONUS only if all done:** 5 combined ${call_direction} bots (NEW agents, don't touch live) → test+compare → report readiness; then port to Signals.

Between voice calls, advance the NON-call deliverables (report, skill updates, open-items) so the slow sequential call pipeline is never the sole bottleneck.
