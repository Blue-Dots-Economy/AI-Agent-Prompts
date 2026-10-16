# Static analysis: kkb-kn-out (up-getjob (ONEST))

**File:** `/Users/parthbansal/EkStep/Prompt Tuner/KKB/KKB Placeholder Kannada.md`
**Family:** kkb (seeker) · **Backend:** up-getjob (ONEST, legacy — NOT Signals)
**Modality:** OUTBOUND (greeting = "ನಾನు ಗವರ್ನಮೆಂಟ್ ಕಡೆಯಿಂದ ಕಾಲ್ ಮಾಡ್ತಾ ಇದ್ದೇನೆ"; `get_profile` gated behind a permission-ask; `new_seeker` DECISIVE ROUTER present).

Archetype matched: **Job-matching / recommendation bot (KKB)**. Because this is the legacy up-getjob backend (`phoneNumber:"+91…"`, `agentId:"up-getjob"`, `apply_job` with `profile_id`+`job_id`), the Signals-specific classes (D33 requirements_snapshot, D35 draft lifecycle, D37 live-item selection, D38 enum-mapping, D39 Signals phone/Latin, D40 location-required) do **not** apply to this file — those are wrong-backend. The already-fixed classes here are in good shape: **G1** binding order (`Consider new_seeker as ${new_seeker}`, lines 63/208), **D22** value-surfaced router + default-to-fetch (line 210), **D31** decoupled create→apply / never-batched (lines 384/887 — catalog records kkb-kn-out as the file this was fixed in), **D28** `profileId` UUID vs numeric `id` (line 874), **D30** verbatim hyphenated `job_id` (line 869), **D16/C7** empty-array → create-first (lines 382/866), **D9** age/gender call-level lock + read-time extraction (lines 357/792), **C9** "Any"/"Not Available" sentinel role (lines 240/785), **D20** APPLY-TURN INTEGRITY block present in this Kannada file (lines 83-85/890-894), **E3** memory-injection block verbatim (lines 189-191), **D15** multi-path apply-failure recovery (lines 993-1030).

Findings below are ordered HIGH → LOW.

---

## [HIGH] Memory-resume opener can stand in for `get_profile` and speaks role/journey from `${contact_memory}` before any fetch (cf. D32 / C5b)

- **Symptom on a call:** For a returning caller, the bot opens by naming their old job/city/employer pulled from injected memory ("ಕಳೆದ ಸಲ [City]ದಲ್ಲಿ [Trade] ಜಾಬ್ಸ್ ನೋಡ್ತಾ ಇದ್ದಿರಿ — ಈಗ ಯಾವುದಾದರೂ ಒಂದಕ್ಕೆ ಅಪ್ಲೈ ಮಾಡೋಣವಾ?"). Because "you MUST resume the previous journey / MUST NOT ask a generic discovery question" competes with the mandatory permission→`get_profile` step, the model can treat the memory blob **as** the fetch — jump from the resume greeting to apply — so `get_profile` never fires, there is no real `profile_id`, and `apply_job` is built from a fabricated/absent id. Even on the benign path it *states* the caller's trade/city as fact from possibly-stale memory (a fabrication per generic §7 / C5b).
- **Evidence:** `## Introduction Priority Rule (Strict Override)` — "If ANY usable prior context exists … → You MUST resume the previous journey → You MUST NOT ask a generic discovery question" (lines 172-187), plus the memory-personalised greeting variants that speak `[Employer]`/`[Job]` and `[City]`/`[Trade]` in the opening turn (lines 195-202), all co-existing with the injected `{${contact_memory}}` block (lines 189-191) and the `get_profile`-driven flow. There is no guard stating "`${contact_memory}` is background only, NOT a fetch — never speak name/role/journey until `get_profile` returns this call."
- **Bug-pattern:** cf. **D32** (memory block used as a substitute for `get_profile` → premature name/role + fetch never fires) — the catalog explicitly flags this as latent: *"the base KKB (Hi+Kn out) and Maya carry the same memory-resume intro block — same latent bug."* Also touches generic checklist §7 / kkb.md "No personal detail spoken before `get_profile` returned." Sub-risk: the `[Employer]`/`[City]`/`[Trade]` fill-ins can leak as literal bracket tokens if memory lacks those sub-fields (generic §1 placeholder-leak).
- **Proven-fix-available?** Yes — the **KKB Kannada Signals clone** fixed exactly this (fixed neutral opener + "`${contact_memory}` is NOT a `get_profile` result" hard guard, 2026-07-29). **Caveat:** the Signals fix removes the personalised resume opener, which is partly *intended* outbound UX here — so this is not a verbatim port; it needs the user's product call on how much resume-personalisation to keep vs. gating all name/role/journey behind a real fetch.
- **needs-transcript-to-confirm?** **Yes.** Repro persona: a returning caller whose `${contact_memory}` carries `actions_taken:"applied"` or `options_presented` + `session_count>1`; grade `tool_calls` — if the bot speaks the old trade/city/job in the opening and `get_profile` fires 0 times before an `apply_job`, it is confirmed.
- **backend-or-tool-adherence?** Prompt-fixable (intro-block redesign + memory-is-not-a-fetch guard), though the residual "does the model actually skip the tool" is a runtime-adherence risk to verify on a live call.

---

## [MED] `hold_message` platform param can narrate the silent `get_profile`/`create_profile` (cf. D34)

- **Symptom on a call:** The caller hears a lookup narration ("ಸ್ವಲ್ಪ ಕಾಯಿರಿ, ನಿಮ್ಮ ಮಾಹಿತಿಯನ್ನು ನೋಡುತ್ತಿದ್ದೇನೆ" / "…ರಚಿಸುತ್ತಿದ್ದೇನೆ") right before a tool result — even though every silent-fetch rule forbids narration — because Raya injects a universal spoken `hold_message` param into every tool call and the model populates it.
- **Evidence:** The Tool-call silence rule (lines 758-760) and Profile Wording Rules (line 752 bans "ದಯವಿಟ್ಟು ಸ್ವಲ್ಪ ಕಾಯಿರಿ"/"ಒಂದು ನಿಮಿಷ" as spoken lines) forbid *narration*, but **no rule anywhere names `hold_message`** or sets it to empty/neutral for `get_profile`/`create_profile`/`update_profile`. Grepping the prompt for the phrase finds nothing precisely because the words come from the platform param, not a spoken turn.
- **Bug-pattern:** cf. **D34** — "*a silence rule that never mentions `hold_message` is insufficient … **Flag:** every get_profile-driven agent (KKB in/out, Maya in/out) is exposed.*" Also generic §10 / kkb.md "`get_profile`'s `hold_message` is the neutral hold only."
- **Proven-fix-available?** Yes — the **KKB Kannada Signals clone** added an explicit rule naming `hold_message` and setting it to a neutral "ಒಂದು ನಿಮಿಷ" (one moment) for the silent tools (2026-07-29). Port it.
- **needs-transcript-to-confirm?** **Yes.** Repro: any `new_seeker="no"` call; read `get_profile`/`create_profile` `tool_calls[].function.arguments.hold_message` — a non-empty revealing string = confirmed.
- **backend-or-tool-adherence?** Platform-param behaviour, but **prompt-fixable** via an explicit empty/neutral-`hold_message` rule for the named silent tools (not a pure backend escalation).

---

## [MED] Literal `+91` phone templates can double-prefix on an already-prefixed outbound `contact_phone` (cf. D17 / C3)

- **Symptom on a call:** If the outbound dialer's `${contact_phone}` already carries `+91`, the literal templates build `+91+91XXXXXXXXXX` → `get_profile` returns empty (returning callers mis-read as new) and/or `create_profile` 400s "Invalid Indian phone number format". A prose "don't double-prefix" guard is present but the literal template is the landmine that can win.
- **Evidence:** `get_profile` call template `phoneNumber: +91${contact_phone}` (lines 226, 768); `create_profile` payload `"phone": "+91<contact_phone>"` (lines 813, 818-824). Prose guard exists ("If `${contact_phone}` already includes a country code, do not double-prefix", line 772) but D17's lesson is that the hard-prepend template overrides it.
- **Bug-pattern:** cf. **D17** ("*latent in KKB Hi/Kn + both inbounds via the same JSON template*") / **C3** value-format mismatch.
- **Proven-fix-available?** Yes — **Maya outbound** replaced the literal `+91…` templates with an exactly-one-`+91` construction ("use as-is if already prefixed; prepend only if bare 10-digit") on both `get_profile` and `create_profile`. Port it.
- **needs-transcript-to-confirm?** **Yes** (and a backend/deployment check). Repro: read a real outbound call's `get_profile`/`create_profile` args — a `+91+91…` value, or empty fetches for callers who provably have a profile, confirms it. Depends entirely on whether this dialer deployment passes `contact_phone` with a leading `+91`. **Escalates to HIGH** if it does (every returning-caller fetch would fail).
- **backend-or-tool-adherence?** Prompt-template fix; the trigger is a deployment/config fact (contact_phone shape) that must be confirmed.

---

## [MED] Presentation ranks but never *filters* by relevance — a known-role seeker's batch is padded to 3 with unrelated roles (cf. D36)

- **Symptom on a call:** A caller with a confirmed/known role (e.g. data-entry) is shown 3 options where the pool has <3 same-role/family jobs, so the model fills the remaining slots with clearly unrelated roles (an EV-charging-technician offered as option one or as filler) → mismatch / drop-off.
- **Evidence:** Default Presentation Rule "present the 3 best-fit valid jobs" + "A role-matched job must be presented before an unrelated one" (line 104) and Step 2 "Present the 3 best-fit valid jobs … by default" (line 290). This is ranking + "role-matched first," but there is **no relevance FILTER** ("when role is known, show ONLY role-relevant jobs; do NOT pad to N"). Line 120 only filters on *validity*, not relevance.
- **Bug-pattern:** cf. **D36** — "*a bare 'present the 3 best-fit' with only a 'role-matched first' sort is insufficient.*" Also kkb.md "the batch is NEVER padded to three with unrelated roles."
- **Proven-fix-available?** Yes — the **KKB Kannada Signals clone** added a role-known relevance filter + no-pad rule (1 relevant → show 1; keep the "ask for more → draw from the rest" fallback) to the Default Presentation Rule and Step 2 (2026-07-29). Port it (adapt to up-getjob spoken format).
- **needs-transcript-to-confirm?** **Yes.** Repro: a caller with a narrow known role against a `${recommendations}` pool holding only 1–2 same-family jobs; grade whether an unrelated role appears as option one or filler.
- **backend-or-tool-adherence?** Prose-fixable (add relevance filter to the presentation rule).

---

## [MED] Apply-failure turn lacks the "don't re-speak the bridge" guard; same-job re-fire guard is scoped to the alternate path only (cf. D27)

- **Symptom on a call:** On a failed `apply_job`, the bot re-speaks the pre-tool apply bridge/reassurance ("ಸರಿ, ನಿಮ್ಮ ಪರವಾಗಿ ಅಪ್ಲೈ ಮಾಡ್ತೇನೆ") at the head of the failure message with no new tool call; and if the caller re-requests the SAME already-failed job, nothing call-wide stops a re-fire of that `job_id` (which will just fail again).
- **Evidence:** Apply Failure Handling gives the base failure line "say once" (line 997) but has **no** rule "begin the failure message DIRECTLY with the base failure line; do not re-speak the bridge/hold on the failure turn" (D27 guard (a) is absent). The same-job guard exists — "Do NOT retry the SAME failed job in the same call" (line 1011) — but it sits under Path 1 (the alternate-job offer), not as a standalone call-wide "an already-failed `job_id` is DONE this call" rule that also covers a caller re-requesting the original job.
- **Bug-pattern:** cf. **D27** ("*confirm BOTH (a) … do not re-speak the bridge/hold on the failure turn, AND (b) a call-wide already-failed job_id is DONE … Cross-agent: confirm both guards exist in EVERY agent that has `apply_job` (KKB out/in H+K, Maya out+in)*"). D27 was seen/fixed in KKB inbound + Maya on 2026-07-27; this outbound file did not clearly receive guard (a).
- **Proven-fix-available?** Yes — **KKB inbound (Hi+Kn)** and **Maya** carry both guards; port the English scaffolding (translate only the quoted bridge example).
- **needs-transcript-to-confirm?** **Yes.** Repro: force an `apply_job` error (backend `apply_failed`) then have the caller re-request the same job; grade whether the failure turn re-speaks the bridge and whether `apply_job` re-fires the same `job_id`.
- **backend-or-tool-adherence?** Prose-fixable (add both guards to Apply Failure Handling).

---

## [LOW] Canonical Location Spellings list is UP/Ghaziabad-centric but the flow/examples use Karnataka place names not in the list (cf. D26)

- **Symptom on a call:** Karnataka place names spoken throughout the flow (ಹೊಸಕೆರೆಹಳ್ಳಿ, ಪೀಣ್ಯ, ಯಶವಂತಪುರ, ನಂಜನಗೂಡು, ತುಮಕೂರು, ಹಾಸನ, ರಾಮನಗರ, ಬೆಳಗಾವಿ, ಧಾರವಾಡ …) have no pinned canonical spelling, so TTS may render them inconsistently across calls.
- **Evidence:** The Canonical Location Spellings section (lines 445-455) pins only Ghaziabad/Indirapuram/Mohan Nagar/Rajendra Nagar/Sector 5 (UP inventory), while every Example dialogue (lines 1178-1369) and the pool-overview flow use Karnataka locations absent from the list. D26 detection: "any place name that appears in the call flow / inventory / example dialogues but is NOT in the canonical list = flag."
- **Bug-pattern:** cf. **D26**.
- **Proven-fix-available?** The canonical-spellings mechanism itself is the proven fix (KKB/Maya, 2026-07-24); it just needs the *actual* up-getjob inventory locations added.
- **needs-transcript-to-confirm?** **Verify the inventory first, not a transcript.** Because the backend is up-getjob (UP), the real runtime inventory may genuinely be Ghaziabad-area (in which case the list is correct and the Karnataka examples are just illustrative placeholders in this "Placeholder" file). Confirm which location set `${recommendations}` actually serves before acting — do not add Karnataka pins if the live inventory is UP.
- **backend-or-tool-adherence?** Prompt-fixable once the real inventory location set is known; low risk.

---

## [LOW] Apply consent is action-consent only; no explicit "your details will be shared with the employer" data-share line (cf. E2 / generic §9)

- **Symptom on a call:** The caller consents to *applying* ("ನಾನు ನಿಮ್ಮ ಪರವಾಗಿ ಅಪ್ಲೈ ಮಾಡಲಾ?", lines 720-721) but is never told, before the tool fires, that applying shares their personal details with the company.
- **Evidence:** Action and Consent Rule (lines 715-726) covers apply-consent; there is no data-share consent line. The kkb.md checklist ("Before applying, the consent/data-share line is spoken") expects one — **but that checklist is Signals-framed** (Signals has an explicit consent-gating requirement per Srivatsa's rule); the legacy up-getjob model may treat apply-consent as sufficient.
- **Bug-pattern:** cf. **E2** / generic §9 (asterisked as a Signals expectation).
- **Proven-fix-available?** The Signals bots have the explicit data-share consent line, if the product decides up-getjob needs it too.
- **needs-transcript-to-confirm?** No — this is a product/consent-policy question for the up-getjob backend, not a reproducible runtime bug. Confirm whether up-getjob requires an explicit data-share consent; if not, no change.
- **backend-or-tool-adherence?** Policy question, then prose-fixable if required.

---

## Cross-language pointer (F)
The HIGH (memory-resume intro block), D34 (`hold_message`), D17 (phone template), D36 (relevance filter), and D27 (apply-failure guards) findings are all **language-agnostic logic** — any fix must be mirrored to `KKB/KKB Placeholder Hindi.md` (the source of truth) and re-run through `/sync-check`. Route all fixes via `/update-prompt`, not hand-edits.

---

**Count by severity: HIGH=1, MED=4, LOW=2.**
