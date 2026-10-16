# Signals expansion — migrate all remaining agents onto Signals DPGs

Durable plan + progress tracker (survives context limits). Playbook: `docs/signals-migration-guide.md`.
Reference bots (the pattern to replicate): **kkb-hi-signals** `115b38a5`, **kkb-kn-signals** `33037201`.
Migration = (A) swap 3 tools to Signals endpoints + (B) apply the 9 structural patterns (§C) + consent_status output var.
"Consistent results" bar = fetch→branch-on-result→consent→create-LIVE→apply-201 (current KKB Signals applies succeed: `12cc6a48`, `51b605a2`).

## User decisions (2026-07-31)
- **Job ids:** SEED throwaway Signals `job_posting_1.0` items via the provider API; use those ids to validate apply end-to-end.
- **Inbound testing:** BUILD an inbound harness (tester agent gets an out_did / dials the inbound bot's in_did). NOTE: new inbound Signals agents will need in_dids assigned (DID provisioning — flag to user).
- Combined ${call_direction} bots: REPURPOSE their uuids as the new Signals bots (user 2026-07-31: 'instead of deleting them, repurpose them for the new bots'). 5 agents recycled + 1 new (Maya inbound).

## Phase 0 — Repurpose combined bots  [status: DONE]
5 experimental agents to retire (deploy=false, keep uuids for manual console deletion):
- kkb-hi-combined 3f521174 · kkb-kn-combined f38da775 · maya-hi-combined 904f333f · dkb-hi-combined fabda71d · dkb-kn-combined 847a85e2
Actions: mark abandoned in agents.json; archive raya/combined/ prompts; note in report/open-items.

## Phase 1 — Signals seeker bots  [status: TODO]
Per bot (handover §D): build prompt (base + 9 patterns + Signals tools) → create Raya agent (POST /api/agent, Signals tools) → curl-ground create-live+apply-201 → deploy → test to parity → changelog.
- [x] Maya Hindi Signals — DONE + VOICE-VERIFIED (call b2df2d35: apply 201, MPL, feminine campus). Agent 904f333f repurposed.
- [ ] KKB Hindi Inbound Signals   (base KKB Placeholder Inbound.md; inbound; hardcoded inventory needs Signals job_ids)
- [ ] KKB Kannada Inbound Signals (base KKB Placeholder Inbound Kannada.md; inbound twin; languageSpoken ["Kannada"])
- [ ] Maya Inbound Signals (base Maya/Maya Inbound.md; inbound + Maya divergences; NEW agent cloned from maya-hi-in df99f501). RE-ADDED (user: 'we have a maya inbound- migrate that too').
Prereqs: (a) provider-side Signals API to SEED job_posting items (partial DKB discovery); (b) inbound harness + in_dids for the 3 inbound bots.

## Phase 2 — DKB Signals discovery (separate)  [status: TODO]
DKB = provider/employer side (create/verify job postings, not seeker profiles) → different endpoints, integration, workflow.
- [x] provider create_job schema mapped -> raya/signals-expansion/DKB-provider-discovery.md (title/role/natureOfJob/positions/jobProviderLocation/lastRoleHeld/hiringManager*; salary/qual DROPPED). TODO: talent-insights endpoint.
- [ ] write DKB-Signals discovery doc (employer twin of the handover)
- [ ] build DKB Hi/Kn Signals → curl-ground → deploy → test

## Dependencies / blockers
- Signals job_id inventory (inbound hardcoded + Maya recommendations) — using seeded test ids for validation; production wiring separate (Srivatsa).
- in_dids for the 3 new inbound Signals agents (DID provisioning) — needed to voice-test inbound.
- Signals x-api-key (Srivatsa) lives only in tool headers / git-ignored — never commit.
- requirements_snapshot: RESOLVED (applies succeed now).

## Discovery log (2026-07-31)
- Signals creds/endpoints pulled from live kkb-hi-signals into `raya/snapshots/_signals-tools-ref.json` (git-ignored; has x-api-key). Tools: get_profile GET /admin/participant · create_profile POST /admin/participant · apply_job POST /action/perform · update_profile POST /admin/participant.
- Provider job-create endpoint CONFIRMED: POST /admin/participant with domain=provider, item_type=job_posting_1.0 (400 INVALID_ITEM_STATE on guessed fields — the job_posting_1.0 item_state schema needs full discovery = Phase 2 DKB work).
- GET-by-item-id NOT exposed (tried 9 paths, all 404/400). Job fetch is phone-keyed (seeker) only.
- Real apply-verified Signals job_ids available for Phase-1 apply testing (from the live feed): 362b0ad9-fa21-4261-be1f-9582c0cc03a9 (apply succeeded on call 12cc6a48). Use these for now; seed controlled test jobs in Phase 2.
- DECISION: Phase 1 uses existing real Signals job_ids for apply validation; full provider job_posting schema + seeding -> Phase 2 (DKB), which is the provider side anyway.

## Progress
- [x] Phase 0 — combined bots abandoned (agents.json + raya/combined/ABANDONED.md)
- [~] Phase 1 — foundational discovery done; building Maya Hindi Signals first (re-domain kkb-hi-signals -> Maya)

## Repurpose map (uuids reused)
- maya-hi-combined 904f333f -> maya-hi-signals (Maya Hindi Signals, out)
- kkb-hi-combined 3f521174 -> kkb-hi-in-signals (KKB Hindi Inbound Signals)
- kkb-kn-combined f38da775 -> kkb-kn-in-signals (KKB Kannada Inbound Signals)
- dkb-hi-combined fabda71d -> dkb-hi-signals (Phase 2)
- dkb-kn-combined 847a85e2 -> dkb-kn-signals (Phase 2)
- NEW agent -> maya-hi-in-signals (Maya Inbound Signals, cloned from df99f501)
Repurpose = PATCH instructions+tools+name on the reused uuid (voice/language already match).

## RESUMPTION STATE (2026-07-31, session usage limit hit — resets 3:30pm IST)
Bot 1/4 DONE. Subagent builds rate-limited; resume the SAME proven recipe when the limit resets.

DONE:
- [x] Maya Hindi Signals — 904f333f, voice-verified (call b2df2d35). Committed.

NEXT (exact steps — resume here):
1. KKB Hi + Kn Inbound Signals — re-run the build workflow:
   Workflow({scriptPath:".../workflows/scripts/build-kkb-inbound-signals-wf_3be2af3c-a2e.js", resumeFromRunId:"wf_3be2af3c-a2e"})
   → review → repurpose 3f521174 (Hi) / f38da775 (Kn) via scratchpad/repurpose_agent.py
     (for Kn pass src=33037201 so languageSpoken=["Kannada"]) → curl-ground → mark inbound voice-test VERIFY-PENDING (needs in_did).
2. Maya Inbound Signals — build from Maya/Maya Inbound.md + kkb-hi-signals ref; CREATE a NEW agent (clone df99f501 config) via scratchpad/create_combined_agent.py (drop memory_enabled key); repurpose-style PATCH Signals tools + instructions.
3. Phase 2 DKB — discover provider job_posting_1.0 item_state schema (POST /admin/participant domain=provider); write DKB-signals discovery doc; build DKB Hi/Kn Signals → repurpose fabda71d / 847a85e2.

Repurpose tool: scratchpad/repurpose_agent.py <target_uuid> <instructions_file> "<name>" [signals_src_uuid].
Real Signals job_ids for grounding/tests: 362b0ad9-fa21-4261-be1f-9582c0cc03a9 (AC Tech), b7513680-6b2f-4223-bba5-893143c949b9 (Data Entry), 7dc7f10b-a42b-4132-ae58-4455f518a37f (Remote CSE) — all apply-verified.
DEPENDENCY: in_dids for the 3 inbound Signals agents (3f521174, f38da775, + Maya inbound) to voice-test inbound.

## Phase 1 progress (2026-07-31 PM)
- [x] Maya Hindi Signals — 904f333f — VOICE-VERIFIED (b2df2d35)
- [x] KKB Hindi Inbound Signals — 3f521174 — VOICE-VERIFIED (call 1a8deec0): inbound welcome, Signals get_profile, real-inventory job presented, apply_job 201 SUCCESS. Inbound-via-outbound method WORKS.
- [x] KKB Kannada Inbound Signals — f38da775 — built (review PASS)+repurposed; inventory=real Signals jobs; TEST-PENDING
- [x] Maya Inbound Signals — 1c24feda (NEW agent, clone df99f501) — built (PASS)+repurposed+out_did; inventory=real Signals jobs; TEST running
Inbound test method: trigger the inbound bot (has out_did) to CALL the tester via POST /api/call + agent_args{contact_phone}; grade the inbound flow.
FOLLOW-UP (cross-cutting): /update-output add consent_status + confirm ready_for_interview in KKB/Maya Output prompts.

## Inbound-via-outbound test method VALIDATED (2026-07-31)
Trigger the inbound bot to CALL the tester (POST /api/call agent_id=inbound-bot to_number=tester + agent_args{contact_phone}); it runs its inbound prompt; grade the transcript. WORKS on out_did 911204404274. The 918037006352 DID does NOT bridge outbound -> re-pointed f38da775 + 1c24feda to 911204404274.

## ALL 4 seeker Signals bots VERIFIED (2026-07-31): maya-hi-signals(b2df2d35), kkb-hi-in-signals(1a8deec0), kkb-kn-in-signals(8d958447), maya-hi-in-signals(2e0c7014) — all apply_job 201 on real Signals jobs. DKB Hi/Kn repurposed; employer create_job test next.
