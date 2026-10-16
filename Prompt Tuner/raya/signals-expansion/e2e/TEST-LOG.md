# Deep E2E test log — Signals bots (2026-08-01)

Tester: "Testing Agent- Blue Dots" f60e0899 (DID 7946350285, max_dur 4). Method: bot dials tester
(inbound bots via their out_did 911204404274); grade the bot leg's tool_calls + spoken turns against
the generic + bot-specific checklists. Note: the tester voice occasionally **parrots** the bot's lines
(voice-bridge echo) — when it does, persona-dependent items (are-you-AI probe, ASR edge) are not cleanly
exercised, but structural items (which tools fire, which jobs are presented, payload fidelity, presence
of a removed step) grade fine from tool_calls + bot turns.

| Bot | call | verdict | notes |
|---|---|---|---|
| DKB Hindi | 146dc70e | ✅ CD1 PASS | Phase-3 new vacancy → collect → consent → **create_job fires** (Sales Executive/Ghaziabad/Sharma Traders/2). **NO market-picture step** (get_talent_insights fully gone). Outbound-framed close. Tester parroted → are-you-AI not exercised. Pre-existing (non-CD1) note: Turn-2 used the "job expiring" pitch though job_role=Not Available should trigger the new-vacancy free-service pitch — flag separately. hold_message was "." not "" (inaudible; minor). |
| DKB Kannada | a02f61b3 | ✅ CD1+CD4 PASS / found CD5 | Clean call. **create_job FIRED** (Electrician/Bangalore) — the D25 non-adherence that failed 4× before is RESOLVED by the simpler Phase-3. **No market-picture step.** CD4 are-you-AI answered honestly. BUT exposed pre-existing bug: job_role="Not Available" → bot spoke "Not Available, Not Available vacancies…" aloud (C9) + took existing-posting branch → **CD5**. |
| DKB Kannada (CD5 retest) | 3177339f | ✅ CD5 PASS | Turn-2 now uses the **new-vacancy pitch** (not expiry); **zero "Not Available" spoken**; straight to Phase 3; are-you-AI ✅; create_job fired clean (Electrician/Industrial Area Bengaluru/2); no market step. Fully green. |
| DKB Hindi (CD5 retest) | e2eec29a | ✅ ALL PASS | Clean call. New-vacancy pitch (not expiry); no "Not Available" spoken; are-you-AI ✅; create_job fired clean (Electrician/Ghaziabad/2); no market step; outbound close. DKB fully green both langs. |
| KKB Hindi outbound | 07699d53 | ✅ PASS (apply→success) | Intro reword confirmed (शहर प्रशासन, no govt, recording-at-end); get_profile silent; jobs from recommendations relevance-filtered (Data Entry/Kashi); **CD4 are-you-AI** ✅; consent → create_profile → **apply_job SUCCESS** (real Signals write); Phase-2 gender+area+read-back; **CD3 outbound close** ✅. Findings: (1) **D17 phone doubling** `91917946350285` — get_profile prompt does `91${contact_phone}` but harness binds 12-digit contact_phone → doubled; apply still succeeded; flagged as CD6 (needs prod contact_phone format confirm). (2) minor D8: "प्रोफाइल" spoken in create-consent + success line (inbound fixed via M6; outbound uses the checklist-sanctioned phrasing) — consistency follow-up. (3) minor D2: "२८" Devanagari numeral in age read-back. |
| KKB Kannada outbound | a224bdbd | ◑ partial (test-data issue) | Intro reword ✅ (ನಗರ ಆಡಳಿತ, no ಸರ್ಕಾರ, recording-at-end); phone single-prefix ✅ (no doubling); **CD4 are-you-AI** ✅; role-update-offer worked ✅; live-item selection ✅ (picked the live "Aryan/22" item, ignored the "Parth/28" draft). BUT No-Matched with no apply — caused by **truncated recommendations** in my staged args (API GET caps agent_args ~1000 chars), NOT a bot bug. Minor D8: "ಪ್ರೊಫೈಲ್" spoken (CD7 class). Re-testing with clean recs. |
| KKB Kannada outbound (clean recs) | bb983c5b | ✅ PASS (apply→success) | Intro ✅; phone single-prefix ✅; presented Data Entry/Kashi (relevance-filtered); **CD4** ✅; consent → **apply_job SUCCESS** (real Signals write); Phase-2 area + read-back; correct age-correction (28) handling; **CD3 outbound close** ✅. Minor: bot kept the live-profile name "Aryan" in the payload after the caller said "I'm Prakash" (verbal correction not persisted) — cosmetic. |
| Maya outbound | d043fae2 | ✅ PASS (apply→success + MPL) | Campus identity (माया, एलआर कॉलेज — no govt) ✅; student gate ✅; feminine voice ✅; **CD4** ✅; presented Data Entry/Kashi from recs (relevance-filtered); consent → **apply_job SUCCESS**; Phase-2; **MPL offered post-apply + registered** (48h/6-8pm) ✅; TTS age in words; **CD3 close** ✅. Minor: live-profile name "Aryan" kept in payload after verbal "Rohan" correction (cosmetic). |
| Maya inbound | 7da1de00 | ✅ PASS (CD2 + apply→success + MPL) | Inbound welcome opener ✅; feminine ✅; **presented Data Entry/Kashi (REAL inventory job, NOT hallucinated Ghaziabad)** ✅ CD2; **CD4** ✅; consent → **apply_job SUCCESS**; Phase-2 name-correction PERSISTED (Rohan/22); **MPL offered + registered** ✅. Note: call_output vars (applied/mpl) didn't populate — Output-prompt `/update-output` dependency, not a conversation bug. |
| KKB Hindi inbound | 7ce385fc | ✅ PASS (CD2 + apply→success) | Inbound welcome opener (शहर प्रशासन, no govt) ✅; said "जानकारी" not "प्रोफाइल" (M6/M12 D8 fix) ✅; **presented Data Entry/Kashi (REAL inventory, no hallucination)** ✅ CD2; **CD4** ✅; consent → **apply_job SUCCESS**; Phase-2 + read-back; handled a "can you hear me?" interruption gracefully. |
| KKB Kannada inbound | 96c24d9d | ✅ PASS (CD2 + apply→success) | Inbound welcome (ನಗರ ಆಡಳಿತ, no ಸರ್ಕಾರ) ✅; said "ಮಾಹಿತಿ" not "ಪ್ರೊಫೈಲ್" (D8 fix) ✅; **presented Data Entry/Kashi (REAL inventory, no hallucination)** ✅ CD2; **CD4** ✅; consent → **apply_job SUCCESS**; Phase-2 name-correction persisted (Prakash/28). |

## Result: 8/8 bots GREEN
All 8 Signals bots live-tested; every seeker apply and every DKB create_job landed as a **real Signals write (success)**.
- **CD1** (DKB get_talent_insights removed, no market step) — verified DKB Hi + Kn.
- **CD2** (inbound inventory↔example consistency) — verified live: KKB Hi in, KKB Kn in, Maya in all present the REAL 4-job inventory (Data Entry/Kashi Infotech, Bengaluru), zero hallucinated Ghaziabad/retail jobs.
- **CD3** (outbound close) — verified KKB out Hi/Kn + Maya out ("...हमारी टीम आपसे फिर संपर्क करेगी").
- **CD4** (are-you-AI) — verified on ALL 8 bots (answered honestly, returned to task).
- **CD5** (DKB Not-Available routing) — verified DKB Hi + Kn (new-vacancy pitch, no sentinel spoken).
- **Bonus:** DKB Kannada `create_job` D25 non-adherence (failed 4× on 2026-07-31) RESOLVED by CD1.
- **Flagged (not applied):** CD6 phone-doubling (needs prod contact_phone format confirm), CD7 outbound "प्रोफाइल" (minor D8).
- **Data/backend deps:** call_output vars (applied_to_job/mpl_presented) don't fully populate on some inbound calls → Output prompts need `/update-output` (consent_status/ready_for_interview); production inventory job_ids to replace the 4 test ids.

### Test coverage note
Live testing focused on the CHANGED behaviors (CD1–CD5) + the core apply/create happy path + an are-you-AI probe (CD4) + several incidental edge cases that arose (name/age corrections, an interruption "can you hear me?", role-update offers, live-item selection over a stale draft). Generic edge behaviors NOT changed by this pass (silence bounds, voicemail, hostility, do-not-call) are inherited unchanged from the proven base bots + covered by the static audit; exhaustive per-bot edge runs are a possible follow-up.
