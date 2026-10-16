# Static analysis: kkb-kn-signals (Signals)

**File:** `/Users/parthbansal/EkStep/Prompt Tuner/KKB/KKB Placeholder Kannada Signals.md` (1408 lines)
**Family:** KKB seeker · **Backend:** Signals · **Modality:** outbound (greeting "ನಾನು ಗವರ್ನಮೆಂಟ್ ಕಡೆಯಿಂದ ಕಾಲ್ ಮಾಡ್ತಾ ಇದ್ದೇನೆ"; apply-failure line 1028 "ನಾವು … ವಾಪಸ್ call ಮಾಡ್ತೀವಿ" = WE call YOU)
**Archetype matched:** Job-matching / recommendation bot (KKB) + Universal core.

## Parity check of today's (2026-07-29) Signals fixes — PASS

All of the current-day Signals patterns are present in this Kannada twin:

- **D32** (memory ≠ fetch): present and strong — lines 177, 198 ("reading `${contact_memory}` is NOT a fetch").
- **D34** (neutral `hold_message` for silent tools): present — get_profile/create_profile = "ಒಂದು ನಿಮಿಷ" (line 755); update_profile = "ಒಂದು ಕ್ಷಣ." (line 936).
- **D35** (draft: reuse fields + consent HARD BLOCK): present — lines 336, 354.
- **D36** (relevance filter, no padding): present — lines 105–109, 262.
- **D37** (multi-profile: select `live` by `lifecycle_status`, never `items[0]`): present throughout — lines 366–368, 776–788, 841, 861.
- **D38** (Signals enum mapping workExperience/gender/nature): present — lines 827–834.
- **D31** (decouple create→apply, never same turn): present — lines 374–378, 839, 875.
- **D30** (job_id verbatim hyphens): present — lines 856, 863.
- **D33** (no `requirements_snapshot` in apply payload): apply payload lists only profile_id/acting_as_user_id/job_id (lines 860–865) — snapshot correctly absent.
- **E3** (memory-injection block verbatim): present — lines 179–181.

The findings below are residual gaps, not regressions of the above.

---

## Findings (HIGH → LOW)

### [MED] create_profile phone spec self-contradicts (10-digit vs 12-digit) — D39 fix left one stale bullet
- **Symptom:** on the new-caller / draft path, `create_profile` may be sent the bare 10-digit number, producing a malformed E.164 (tool template is `"+{{phone}}"`, so 10 digits → `+XXXXXX0249`, missing the `91`). Result per D39: the write resolves/creates the **wrong user** (`user_existed:false`) or 403 `ITEM_NOT_OWNED_BY_USER` — the profile the bot just gathered is lost, and a returning caller (whose `get_profile` used the 12-digit key) gets a mismatched record. Borderline HIGH: it is a payload contradiction on a **required** write field.
- **Evidence:** line 818 (Payload list) says `phone` = "the caller's **10-digit** mobile number, digits only, **no country code and no `+`**"; line 832 (dropdown/enum block) says the exact opposite — "ALWAYS the caller's **12-digit** number = `91` + `${contact_phone}` … **Do NOT pass the bare 10-digit number (it would resolve the wrong record)**." Two directly conflicting specs for the same field in the same section.
- **bug-pattern:** cf. **D39** (Signals write fails/duplicates on bad phone) + **A4** (intra-section contradiction) + **C3** (value-format mismatch). Related landmine: `get_profile` uses the literal hard-prefix template `phone_number: 91${contact_phone}` (lines 198, 763) — guarded by the anti-double-prefix prose at line 767, but per **D17** a literal hard-prepend can still win if `${contact_phone}` ever carries a country code.
- **proven-fix-available?** Yes — the D39 fix (2026-07-29) standardized on ONE 12-digit `91`+number convention with template `"+{{phone}}"`. Reconcile line 818 to the 12-digit form already stated at line 832 (and sync-check the Hindi Signals twin, which the D39 note says was fixed "Kn + Hi" — verify line 818's equivalent there too).
- **needs-transcript-to-confirm?** Yes — read a new-caller `create_profile` `tool_calls[].arguments.phone`: a 10-digit value (→ `+XXXXXX0249`) or a `user_existed:false`/403 on the write reproduces it. Persona: brand-new caller, no profile, applies to a job → forces `create_profile`.
- **backend-or-tool-adherence?** No — prose contradiction, prose-fixable.

### [MED] Outbound bot invites callbacks in closings — modality leak
- **Symptom:** an outbound government-dialer that itself promises "ನಾವು … ವಾಪಸ್ call ಮಾಡ್ತೀವಿ" (we'll call you back, line 1028) also tells callers to call/reach back in its closings — inbound-framed endings the bot's own modality contradicts.
- **Evidence:** Example 4 close line 1343 "ಯಾವಾಗ ತಯಾರಾದ್ರೂ **ಕಾಲ್ ಮಾಡಿ**. Goodbye" and line 1339 "…ಅವರೇ **ಕಾಲ್ ಮಾಡಬಹುದು**"; Example 3 close line 1314 "ಯಾವಾಗ ತಯಾರಾದ್ರೂ ಮಾತಾಡಿ. Goodbye"; do-not-call line 1111 "ನೀವೇ ಸಂಪರ್ಕ ಮಾಡಬಹುದು". The Graceful Exit section (lines 1132–1147) has **no** modality-appropriate closing script and **no** ban on "call us back" phrasing — exactly the D5 precondition.
- **bug-pattern:** cf. **D5** (modality leak — outbound bot invites callbacks) + **E1** (examples model the leaked behavior).
- **proven-fix-available?** Partially — the base/legacy KKB seeker bots carry the D5 closing discipline ("the center will contact you"-style, no callback invite); port that closing rule + callback-phrasing ban into Graceful Exit and repair the example closings to "ನಾವು ನಿಮಗೆ ವಾಪಸ್ ತಿಳಿಸ್ತೀವಿ"-style.
- **needs-transcript-to-confirm?** Recommended yes (confirm a live call actually closes with a callback invite before editing) — though the examples are strong static evidence. Persona: any caller who defers ("ಯೋಚಿಸ್ತೇನೆ") or a proxy who says "we'll do it later" → the bot reaches the example-modeled close.
- **backend-or-tool-adherence?** No — prompt/example prose, prose-fixable.

### [LOW] D40 durable fix (location as a REQUIRED create_profile param) is not verifiable in the prompt
- **Symptom:** if `location` is only optional in the `create_profile` tool schema, a new caller's profile can still be minted `draft` (Signals promotes to `live` only when `location` is present) → `apply_job` 422 `PROFILE_NOT_LIVE`. The prompt's Phase-1 prose gate already lists Location (lines 311–314, 334, 336, 812) but D40's own root cause is that the prose gate did NOT hold at runtime — the reliable fix is schema-level.
- **Evidence:** prompt-side is correct (location is a Phase-1 minimum-required field), but the fix lever (`create_profile.parameters.required` ⊇ `location`) lives in the agent's Raya tool config, not this file — so parity can't be confirmed statically.
- **bug-pattern:** cf. **D40** (create omits location → draft → PROFILE_NOT_LIVE).
- **proven-fix-available?** Yes — D40 (2026-07-29) says `location` was made required on "both agents (Kn + Hi)"; just confirm it stuck on the Kannada Signals agent config.
- **needs-transcript-to-confirm?** Yes — a new-caller `create_profile` with missing/empty `location` + a `draft` create-response + a following `apply_job` 422 `PROFILE_NOT_LIVE`.
- **backend-or-tool-adherence?** **Yes — NOT prose-fixable** (tool-schema / runtime-adherence). Escalate/verify the tool config; do not add more prose (D25).

### [LOW] Pre-check "check recommendations before greeting" vs "call ALWAYS opens with the greeting" — mild ordering contradiction
- **Symptom:** ambiguity about whether an empty-`recommendations` call should speak the fixed greeting first or jump straight to the No-Match line; both outcomes are safe (a graceful message), so low impact.
- **Evidence:** line 175 "The call ALWAYS opens with the SAME neutral greeting…" vs lines 228–229 "**Before greeting the user** or fetching a profile, check `job_recommendations` … skip all steps and trigger No-Match Fallback immediately." Also note two near-duplicate No-Match Fallback sections (lines 123–136 and 384–394) — harmless redundancy, not a bug.
- **bug-pattern:** cf. **A4** (header/instruction contradiction), minor.
- **proven-fix-available?** N/A — reconcile to one order (recommended: keep the greeting, then No-Match on empty), matching whatever the Hindi twin does.
- **needs-transcript-to-confirm?** No (static wording issue); low priority.
- **backend-or-tool-adherence?** No — prose-fixable.

---

**Count:** HIGH=0 · MED=2 · LOW=2
