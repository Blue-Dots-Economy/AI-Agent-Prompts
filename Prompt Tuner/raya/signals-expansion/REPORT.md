# Signals expansion — final report

Migrate all remaining voice agents onto the EkStep Signals DPGs. Done end-to-end 2026-07-31.
Playbook: `docs/signals-migration-guide.md`. Provider discovery: `DKB-provider-discovery.md`. Progress: `PLAN.md`.

## What was done
Recycled the 5 abandoned combined-`${call_direction}` agents (no Raya delete route) + created 1 new agent, so **6 Signals bots** now exist — no console litter:

| Signals bot | agent uuid | source | direction | STATUS |
|---|---|---|---|---|
| Maya Hindi Signals | `904f333f` | repurposed (ex maya-hi-combined) | outbound seeker | ✅ **VOICE-VERIFIED** (b2df2d35) |
| KKB Hindi Inbound Signals | `3f521174` | repurposed (ex kkb-hi-combined) | inbound seeker | ✅ **VOICE-VERIFIED** (1a8deec0) |
| KKB Kannada Inbound Signals | `f38da775` | repurposed (ex kkb-kn-combined) | inbound seeker | ✅ **VOICE-VERIFIED** (8d958447) |
| Maya Inbound Signals | `1c24feda` | NEW (clone df99f501) | inbound seeker | ✅ **VOICE-VERIFIED** (2e0c7014) |
| DKB Hindi Signals | `fabda71d` | repurposed (ex dkb-hi-combined) | provider/employer | ✅ **VOICE-VERIFIED** (09a7b6c8) |
| DKB Kannada Signals | `847a85e2` | repurposed (ex dkb-kn-combined) | provider/employer | ✅ **VOICE-VERIFIED** (a02f61b3, 3177339f) — create_job D25 RESOLVED (see 2026-08-01 deep-E2E pass) |

> **2026-08-01 deep-E2E pass** (see `e2e/DECISIONS-AND-FIXES.md` + `e2e/TEST-LOG.md`): all 8 Signals bots re-tested end-to-end and fixed. **CD1** removed the Dhiway `get_talent_insights` from DKB (no Signals endpoint) + its market-picture flow — this ALSO resolved the DKB-Kannada `create_job` D25 non-adherence (Phase 3 now has one tool). **CD2** rewrote the inbound bots' examples/synonyms to match the real 4-job inventory (killed an E1 hallucination). **CD3** fixed outbound-close modality; **CD4** added an are-you-AI responder to all bots; **CD5** fixed DKB `job_role="Not Available"` misrouting + a sentinel leak. 8/8 green; every apply/create is a real Signals write. Two items flagged for confirmation: **CD6** (get_profile phone can double the 91 prefix — needs the production `${contact_phone}` format confirmed), **CD7** (minor outbound "प्रोफाइल"/D8).

Every bot: prompt built by re-domaining the proven `kkb-hi-signals` structure (9 stabilisation patterns + Signals tool contract) onto the target, preserving each bot's own divergences (Maya campus/feminine/MPL/Experience-Capture/hr_contact; inbound welcome + hardcoded inventory; DKB employer flow). Each reviewed (adversarial), repurposed (PATCH name+instructions+Signals tools), grounded, and tested.

## How each was tested (all apply/create on REAL Signals writes)
- **Seeker bots** (Maya out + 3 inbound): fetch→branch→consent→create-live→**apply_job → 201 SUCCESS** on real Signals job_ids. Inbound bots tested via **the inbound-via-outbound method** (trigger the inbound bot — it has an out_did — to CALL the tester, so it runs its inbound prompt; grade the transcript). No new DIDs needed.
- **DKB provider bots**: employer flow → **create_job → POST /admin/participant (provider job_posting_1.0)**. Curl-grounded (job item `f6c3d7bb` created with a fresh employer phone); DKB-Hi voice-verified end-to-end.

## Provider (DKB) schema — discovered this session
`job_posting_1.0` `item_state` accepts ONLY: `title, role, natureOfJob, positions, jobProviderLocation, lastRoleHeld, hiringManagerName, hiringManagerEmail`. Company → top-level `name`; location → `jobProviderLocation`. **Salary / stipend / task-rate / qualification / experience-years / educational-institute have NO Signals slot** — DKB collects them in conversation but does NOT persist them (flagged in-prompt). Full detail in `DKB-provider-discovery.md`.

## Inventory (inbound + Maya recommendations)
No Signals get-jobs API exists (all endpoints 404). Per your instruction, the inbound bots' hardcoded inventories were populated with the **existing real Signals jobs** (`b7513680` Data Entry, `7dc7f10b` Remote CSE, `da32f92e` EV Tech, `362b0ad9` AC Tech) — real, apply-verified ids, not labelled placeholder. **Replace with the production inventory when ready.**

## Known items / backend dependencies (for you / Srivatsa)
1. **Inventory ids** — the inbound inventories use the 4 real test jobs; swap in the real production job list (data).
2. **DKB Kannada `create_job` adherence (D25) — ✅ RESOLVED 2026-08-01.** Removing `get_talent_insights` (CD1) left Phase 3 with only `create_job`; the reduced tool ambiguity made the Kannada bot fire `create_job` reliably (retests a02f61b3, 3177339f). No platform backstop needed. (Original finding retained below for history.) Across 4 tests on 2026-07-31 the Kannada bot completed the full job capture but did NOT reliably emit `create_job` on the post-consent turn — it either hallucinates "done" with no tool call (`2e350d57`, and `7577055a` even *after* a hard Phase-3 rule) or mis-fires `update_job` with the placeholder `job_id` (`blysb9o81`, 400). The Hindi twin (`09a7b6c8`) fires `create_job` cleanly with the SAME prompt structure. Two prompt fixes shipped (scope per-field `update_job` to Phase 2; hard "Phase 3 = create_job once, never update_job") — they stopped the erroneous `update_job` 400s, but the residual no-tool hallucination is **runtime non-adherence (D25), not prose-fixable**. Needs a platform backstop (Raya forcing the create_job call on the consent turn) or further runtime investigation. Everything else about DKB Kannada (the full flow) and the Hindi twin are verified. Analyser **C11** records the class.
3. **`get_talent_insights`** — ✅ **RESOLVED (removed).** No Signals endpoint exists, so per the 2026-08-01 pass (CD1) the tool + the whole market-picture step were removed from DKB Hi/Kn; the flow goes straight to `create_job`. If Signals later wires a talent-insights endpoint, re-add the tool + step.
4. **DKB job open/closed status** — no confirmed `job_posting_1.0` slot; not persisted.
5. **Output prompts** — `consent_status` (+ inbound `ready_for_interview`) referenced by the Signals prompts but not yet in the KKB/Maya Output prompts → run `/update-output` before production.
6. **`requirements_snapshot`** — resolved (seeker applies succeed).

## Abandoned
The combined `${call_direction}` approach is retired (call_direction not injected on API calls). Their 5 agents were repurposed into the Signals bots above; the v0 combined prompts are archived under `raya/combined/` (do not deploy).
