# Static analysis: kkb-hi-out (up-getjob (ONEST) — NOT Signals; do not port Signals-only fixes blindly)

**File audited:** `/Users/parthbansal/EkStep/Prompt Tuner/KKB/KKB Placeholder Hindi.md` (1379 lines)
**Archetype matched:** Job-matching / recommendation bot (KKB), **OUTBOUND** modality (greeting: "मैं गवर्नमेंट की तरफ से कॉल कर रही हूँ — आपके लिए कुछ जॉब्स हैं"), memory-enabled.
**Backend:** up-getjob / ONEST — `get_profile(phoneNumber:"+91…")`, `create_profile(agentId:"up-getjob")`, `apply_job(profile_id,job_id)`, `update_profile`. Read-only audit; nothing edited.

**Signals-only patterns deliberately NOT flagged** (do not apply to up-getjob): D33 `requirements_snapshot {}`, D37 `lifecycle_status`/live-item selection, D38 enum-mapping, D39 Signals 12-digit-no-`+` phone, D40 Signals `location`-required-for-live. This bot's `+91` phone convention and `profile_id`/`job_id` shapes are correct for up-getjob.

**Well-covered (checked, no flag):** G1 backwards-binding is FIXED — `Consider new_seeker as ${new_seeker}` (label-first) at L64 & L209. D22 value surfaced at decision + default-to-fetch (L211). A8/D18 decisive router, scoped mandate, forceful "yes→fetch FORBIDDEN" (L211-215). D16 empty-array→create_profile explicit at router/NO-branch/apply (L382-383, 868). D28 `profileId` UUID vs numeric `id` (L876). D30 job_id verbatim hyphens (L871,877). D31 create→apply un-batched (L385,387,889). D9 age/gender call-level lock + read-time extraction across all records (L220,358,794). D11 once-per-call create guard (L385). D12 role synonym/family + cashier excluded (L107-109). D13 city-anchor (L111). D15 apply-failure recovery (L1004-1032). C6 "Reading the get_profile response" field map (L781-794). E3 memory-injection block verbatim (L190-192). Hallucination guard strong (L88-115).

---

## [HIGH] `+91` hard-prepend phone template risks double-prefix (`+91+91…`) on the outbound deployment

- **Symptom:** `get_profile` queries `+91+91XXXXXXXXXX` → empty result → a returning caller is misread as new (no profile fetched, no personalisation, age/gender re-asked); and `create_profile` for a new caller fails HTTP 400 "Invalid Indian phone number format: +91+91…" → the apply fails 100% for new callers. Outbound/dialer deployments frequently deliver `${contact_phone}` already carrying the country code, which is exactly when this fires.
- **Evidence:** Literal `+91`-prepend templates at L227 and L770 (`` `get_profile` with `phoneNumber: +91${contact_phone}` ``) and L823 (`"phone": "+91<contact_phone>"`). A prose "do not double-prefix" guard exists (L774: "If `${contact_phone}` already includes a country code, do not double-prefix.") but the literal template sits right next to it.
- **Bug-pattern:** cf. D17 (literal `+91<contact_phone>` / `+91${contact_phone}` template is a landmine that can win even with a prose guard); related C3 (value-format mismatch → empty lookup).
- **proven-fix-available?** YES — **Maya outbound** already fixed this (D17, 2026-07-20: `create_profile` sent `+91+91XXXXXX9115` → 400; templates changed to a "contact_phone with exactly one `+91` prefix — do not double-prefix" placeholder, guard added to BOTH get_profile and create_profile). D17 explicitly names KKB Hi/Kn as latent via this same template. Port the Maya fix (this is an up-getjob `+91` fix, NOT a Signals fix).
- **needs-transcript-to-confirm?** YES — pull a recent outbound call and read `get_profile`/`create_profile` `tool_calls[].arguments`: a `phoneNumber`/`phone` of `+91+91…` (or an empty get_profile for a caller who has a profile) confirms it. Reproduce with a returning caller whose `${contact_phone}` already carries `+91` on this dialer deployment. If this deployment passes a bare 10-digit number, it does not fire — hence transcript-gated.
- **backend-or-tool-adherence?** Prompt-fixable (template change) — not backend, not a tool-adherence miss.

---

## [MED] No `hold_message` rule — platform may speak a fetch/creation narration on the "silent" tools

- **Symptom:** Raya injects a universal `hold_message` spoken-filler param into every tool call. With no rule pinning it, the model writes a natural sentence (e.g. "आपकी जानकारी देख रही हूँ" / "प्रोफ़ाइल तैयार कर रही हूँ") into `get_profile`/`create_profile`'s `hold_message`, and the platform SPEAKS it — violating the silent-fetch rule and the "never say प्रोफाइल aloud" rule, even though no such line appears in the prompt (grepping the prompt finds nothing, because the words come from the platform param).
- **Evidence:** `grep hold_message` on the file returns **zero** matches. The prompt bans spoken narration only (Profile Wording Rules L754,760-762; Tool Call General L1114) — it never names `hold_message` or sets it to `""`/neutral for the silent tools. This is exactly the "silence rule that never mentions hold_message is insufficient" gap.
- **Bug-pattern:** cf. D34 (platform `hold_message` narrates a step the prompt says is silent); related B2/D8.
- **proven-fix-available?** YES — the **KKB Kannada Signals clone** fixed this on 2026-07-29 (explicit empty/neutral `hold_message` rule naming `get_profile`/`create_profile`). D34 explicitly flags "every get_profile-driven agent (KKB in/out, Maya in/out) is exposed — the platform param is universal," so porting the `hold_message` rule here is appropriate (it is a universal-platform fix, not Signals-specific machinery).
- **needs-transcript-to-confirm?** YES — read `get_profile`/`create_profile` `tool_calls[].arguments.hold_message`; a non-empty reveal phrase there confirms it. Any returning-caller outbound call (the get_profile turn) reproduces it.
- **backend-or-tool-adherence?** Root cause is a platform param, but the **fix is a prompt rule** (name `hold_message`, set neutral/empty for the silent tools) → prompt-fixable, not an escalation.

---

## [MED] Memory-resume "Strict Override" opening + Example 2 model skipping `get_profile` → `apply_job` with no `profile_id`

- **Symptom:** On a returning caller the bot resumes from injected `${contact_memory}` in the opening (names prior Employer/Job/City/Trade), then — following Example 2 — goes straight to the deep-dive and `apply_job` with **no `get_profile` and no `create_profile` shown**, so there is no `profile_id` source → `apply_job` fails "Invalid or missing profile_id". The "Strict Override" actively pushes toward skipping discovery/fetch.
- **Evidence:** L173-188 "Introduction Priority Rule (Strict Override) … If ANY usable prior context exists … → You MUST resume the previous journey → You MUST NOT ask a generic discovery question"; memory-personalised greeting variants speak `[Employer]`/`[Job]`/`[City]`/`[Trade]` before any fetch (L197,200). **Example 2 (L1235-1245)**: greeting resumes mid-journey → user picks a job → agent jumps straight to deep-dive then `*(calls apply_job)*` with NO permission-ask, NO `get_profile`, NO `create_profile` — contradicting the canonical flow the examples claim to follow (L1157: "greeting → (new_seeker 'no') profile-permission → `get_profile` → …"). (Examples 3/5 at L1281/L1336 at least note "*profile fetch done*"; Example 2 shows nothing.)
- **Bug-pattern:** cf. D32 (memory block used as a substitute for `get_profile` → fetch never fires / premature name-role; catalog explicitly flags "base KKB (Hi+Kn out) … same latent bug"); cf. E1 (few-shot example skips a mandatory step → model mimics the shortcut); consequence class C7/D16 (`apply_job` without a `profile_id`).
- **proven-fix-available?** PARTIAL — the D32 fix pattern (fixed neutral opener + "`${contact_memory}` is background context, NOT a fetch" guard) was applied on the Signals clone; but note the **outbound archetype legitimately uses prior-call memory in the opening** (checklist: "Introduction priority rule — opening line chosen from prior-call memory state"), so the right fix here is narrower than the inbound D32 fix: keep the resume greeting but (a) forbid the resume path from skipping the mandatory `get_profile`/`create_profile` before `apply_job`, and (b) repair Example 2 to show the fetch. No sibling has this exact outbound repair yet.
- **needs-transcript-to-confirm?** YES — read `tool_calls` on a returning-caller outbound call: if the bot speaks a resumed role/employer and reaches `apply_job` with `get_profile` firing 0 times (id fabricated), it is confirmed. Persona: returning caller, `session_count>1`, `actions_taken=applied`, who says "हाँ, उसी में अप्लाई कर दो" at the resume greeting.
- **backend-or-tool-adherence?** Prompt-fixable (repair the example + gate the resume path so `apply_job` always has a real `profile_id`).

---

## [MED] Outbound bot invites callbacks — no ban on inbound-framed closings

- **Symptom:** An outbound (bot-calls-user) agent ends by inviting the user to call/reach out, which trained call-center endings encourage and which mis-sets the modality (there is no guaranteed inbound line on an outbound dialer).
- **Evidence:** Example 4 closing L1322 "बिल्कुल। जब भी तैयार हों, **call कीजिए**। Goodbye" (explicit callback invite); do-not-call closings L1099/L1379 "…कभी ज़रूरत हो, आप **खुद संपर्क कर सकते हैं**"; repeated "…**बात कीजिए**। Goodbye" (L1133,1269,1295,1371). Graceful Exit (L1120-1135) supplies a closing script but has **no ban** on "call me/us back"-type phrasing.
- **Bug-pattern:** cf. D5 (modality leak — outbound bot invites callbacks; needs a closing script + an explicit ban on callback phrasing). Generic checklist §11 treats an outbound "you can call me back" ending as a fail.
- **proven-fix-available?** Partially — D5 is catalogued from the Purple Dots review with the standard fix (closing matched to true modality + prohibition on callback phrasing); no seeker sibling is cited as having a clean fixed-form fix to port verbatim.
- **needs-transcript-to-confirm?** NO to confirm the text is present (it is, in the prompt's own example/closing lines); YES only if you want to confirm the model actually emits it live. **Lower confidence / product question:** confirm whether KKB actually supports an inbound helpline number — if it does, "call कीजिए" may be acceptable and this drops to LOW.
- **backend-or-tool-adherence?** Prompt-fixable (add callback-phrasing ban to Graceful Exit + repair the example closings).

---

## [LOW] Apply-failure section lacks an explicit "do not re-speak the bridge at the failure-turn head"

- **Symptom:** On an `apply_job` error, the failure message could begin by re-speaking the pre-tool apply bridge ("अप्लाई कर देती हूँ") with no new tool call, sounding like it is retrying when it is not.
- **Evidence:** Apply Failure Handling (L995-1032) gives the base failure line "say once" (L999) and hard bans (L1022-1028) but has **no** explicit "begin directly with the base failure line; do not re-speak the bridge/hold on the failure turn." The call-wide bridge rule (L887 "Once you have said it, never say it again") mostly covers this, so the gap is a polish/sync gap, not an open hole. Guard (b) of D27 IS present (L1013 "Do NOT retry the SAME failed job in the same call").
- **Bug-pattern:** cf. D27 (apply-failure turn re-speaks the bridge / re-fires the same failed job — wants BOTH guards; guard (a) is the one not stated in the failure section here).
- **proven-fix-available?** YES — **KKB inbound (Hi+Kn) + Maya (Hi + Inbound)** got both D27 guards on 2026-07-27; D27 says to confirm both exist in EVERY apply_job agent incl. **KKB outbound** — this outbound file is the missing-parity case. Straight port.
- **needs-transcript-to-confirm?** YES — a call where `apply_job` errors and the failure turn opens by re-speaking the bridge. Low priority given the L887 call-wide rule already largely holds.
- **backend-or-tool-adherence?** Prompt-fixable (add the one-line guard to Apply Failure Handling).

---

## [LOW] Glossary fragment `${new_seeker} as new_seeker` is placeholder-first (corrective binding present)

- **Symptom:** A placeholder-first binding interpolates to "no as new_seeker" (value presented as if it were the label), the G1 shape that once broke the KKB fork.
- **Evidence:** L64 bullet begins "**`${new_seeker}`** as new_seeker — …". Same glossary shape for L61-63 (`${contact_name}` as contact_name, etc.). **Mitigated:** the correct label-first binding "Consider new_seeker as `${new_seeker}`" follows immediately (L64) and again at L209, and the value is surfaced at the decision (L211), so the fork binds cleanly today.
- **Bug-pattern:** cf. G1 (placeholder-before-label binding; the catalog itself notes it is "lower for glossary lines that have a description to disambiguate," which is the case here).
- **proven-fix-available?** YES — trivial: flip to label-first, matching the already-correct `Consider new_seeker as ${new_seeker}` lines. Low urgency since a corrective binding is present.
- **needs-transcript-to-confirm?** NO — pure static/templating nit; the branch already works because the corrective binding exists.
- **backend-or-tool-adherence?** Prompt-fixable (cosmetic hardening).

---

**Count by severity: HIGH = 1, MED = 3, LOW = 2.**
