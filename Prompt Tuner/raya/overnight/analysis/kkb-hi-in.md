# Static analysis: kkb-hi-in (up-getjob (ONEST) inbound)

**File:** `/Users/parthbansal/EkStep/Prompt Tuner/KKB/KKB Placeholder Inbound.md`
**Family:** KKB seeker (job-matching / recommendation archetype) · **Backend:** up-getjob (ONEST) **legacy**, inbound (get_profile-driven, hardcoded Job Inventory, no `get_jobs`).

**Scope note (important):** This is the **legacy up-getjob** backend, **not Signals**. So the Signals-only failure classes — D33 `requirements_snapshot {}`, D37 multi-item live-selection, D38 enum `item_state`, D39 Signals phone/Latin, D40 `location`-required-for-live — do **not** apply here and are deliberately **not** flagged. The apply payload here is `{profile_id, job_id}` with `profile_id` = get_profile top-level `id` (returning) or create_profile `profileId` UUID (new). Confirmed already-fixed in this file and NOT flagged: D8 (profile-wording bans), D24 (outbound-residue neutralised), D26-section-exists, D27 (apply-failure bridge/refire guards), D28 (`profileId` UUID vs numeric `id`), D29 (two-turn greet/fetch un-bundle present), D30 (`job_id` verbatim hyphens), C6/C9/D9 (response field-map, "Any" sentinel, age/gender read-time lock), A6/A7 (one-question-per-turn, present-content-before-interest).

---

## [HIGH] D31 — new-caller `create_profile`→`apply_job` told to run "in a single turn / back to back" → `apply_job` sent an empty `profile_id`

- **Symptom:** For a brand-new caller (no fetched profile), the model emits `create_profile` and `apply_job` in the **same turn/batch**, so `apply_job`'s arguments are built before `create_profile`'s result exists. The only source of a new caller's `profile_id` is the `create_profile` response, so `apply_job` goes out with `profile_id: ""` and the application FAILS (404 "Invalid or missing profile_id"). New callers can't actually apply.
- **Evidence:**
  - Line 605: *"Run the application as ONE clean sequence **in a single turn**: say the bridge line ONCE → make the tool call(s) silently (returning caller … `apply_job` alone; brand-new caller: `create_profile` then `apply_job`, **back to back**) → then speak the result once."*
  - Line 1095 (apply_job rules): *"For a brand-new caller: say the bridge line once → call `create_profile` silently → call `apply_job` silently → speak the result. The bridge is said once **for the whole sequence**…"*
  - Line 601's NO branch says "…then call `apply_job` with the `profile_id` it returns" (good intent), but the "single turn / back to back / whole sequence" wording (605, 1095) is exactly the batching the catalog names as the bug and overrides it.
- **Bug-pattern:** **D31** (verbatim: grep the apply-sequence for "single turn" / "back to back" / "whole sequence" applied to a `create_profile`→`apply_job` pair). Adjacent to D20 (bundled create+apply) — note the APPLY-TURN INTEGRITY block (lines 1062-1066) covers D20's *hallucination* guards but does **not** fix D31's empty-`profile_id`/batching problem.
- **proven-fix-available?** **Yes — port from KKB base `kkb-kn-out` (fixed 2026-07-27, D31 "Seen in").** Split the new-caller apply into two steps crossing a tool-result boundary: `create_profile` FIRST → WAIT for its result → then as the NEXT action read `profile_id` from that result and call `apply_job`; explicitly forbid emitting create+apply in the same turn/batch and forbid `apply_job` with an empty `profile_id`. The catalog explicitly lists "Maya (out+in) and the Signals clone carry the same batching language" — this inbound file was **not** in D31's fixed set, so it is a live, un-applied fix. Language-agnostic (verbatim H↔K).
- **needs-transcript-to-confirm?** **Yes.** Reproduce with a **new inbound caller (no existing profile) who selects a job and consents to apply** → read `apply_job` `tool_calls[].function.arguments`: `profile_id: ""` right after a same-turn `create_profile` confirms it.
- **backend-or-tool-adherence?** No — prose-fixable (structural sequence change). Platform response-variable capture is a durable backstop but the two-step split holds instruction-only.

---

## [HIGH] D32 — memory-resume opening ("MUST resume the previous journey" + greeting variants that speak prior journey) runs BEFORE `get_profile` → fetch-substitution / personal detail spoken pre-fetch

- **Symptom:** On a returning caller with prior-call memory, turn 1 speaks a personalised **resume line built from `${contact_memory}`** — a city/trade/employer/job the caller "was looking at last time" — before `get_profile` has fired this call. Two harms: (a) the model can treat the memory read AS the fetch and **skip `get_profile`** entirely (→ no live `profile_id` → later `apply_job` fabricated/404), and (b) it asserts a journey from possibly-stale memory rather than a real fetch result (a §7 / kkb.md opening fail).
- **Evidence:**
  - Lines 405-418 — **Introduction Priority Rule (Strict Override):** *"If ANY usable prior context exists, you MUST NOT use a generic or open-ended opening… → You MUST resume the previous journey → You MUST NOT ask a generic discovery question. This rule overrides all default opening fallbacks."*
  - Line 427 — variant speaks memory in the opening: *"…आपने **[Employer]** में **[Job]** के लिए अप्लाई किया था — कोई सवाल है…"*
  - Line 430 — *"…पिछली बार **[City]** में **[Trade]** की जॉब्स देख रहे थे — क्या अब किसी में अप्लाई करना है…"*
  - The two-turn router (lines 435, 443-449) correctly puts `get_profile` on turn 2 — but turn 1's opening is chosen from `${contact_memory}` and speaks the prior journey *before* that fetch.
- **Bug-pattern:** **D32** ("Memory block used as a substitute for `get_profile`"; detection: *"Any opening that can speak name/role/journey BEFORE a `get_profile` result exists = flag"*). Catalog explicitly names the residue: *"the base KKB (Hi+Kn out) and Maya carry the same memory-resume intro block — same latent bug."* Also fails kkb.md opening items 1-2 ("NOTHING personal… no 'last time you were looking in [city]' resume line"; "No personal detail spoken before `get_profile` has actually returned").
- **proven-fix-available?** **Yes — the KKB Kannada Signals clone (D32, 2026-07-29) already fixed this:** replace the memory-personalised variants + "MUST resume" override with a **fixed neutral greeting + one qualifying question**, and add the guard "`${contact_memory}` is background context only, NOT a `get_profile` result — name/role/journey may be spoken ONLY after the fetch returns THIS call; reading memory is NOT a fetch." Keep the memory-injection block itself verbatim.
- **needs-transcript-to-confirm?** **Yes** (partly mitigated by the strong two-turn fetch mandate, so confirm empirically). Reproduce with a **returning caller who has prior-call memory (options_presented / actions_taken="applied")**: check `tool_calls` — if the bot speaks the resume line and `get_profile` fires **0 times**, the substitution is live; if the fetch still fires, the remaining harm is the stale-memory resume assertion.
- **backend-or-tool-adherence?** No — prose-fixable (opening redesign + memory-is-not-a-fetch guard).

---

## [MED] D34 — tool-silence rule never names/empties `hold_message`; platform speaks a revealing hold over the "silent" `get_profile`/`create_profile`

- **Symptom:** Raya injects a universal `hold_message` (spoken filler) into every tool call. The model writes a natural sentence into it and Raya **speaks it**, so a `get_profile`/`create_profile` the prompt insists is silent gets announced aloud ("…आपकी जानकारी देख रही हूँ" / "…बना रही हूँ"). The words never appear in the prompt (they come from the platform param), so the narration bans don't catch them.
- **Evidence:** The tool-call silence section (lines 964-966) is a **prose narration ban only** — *"Before, during, and immediately after get_profile / create_profile / update_profile / apply_job — no waiting message, no status narration…"* — and never mentions the `hold_message` parameter or sets it to empty/neutral for the silent tools. Same for lines 449 and 958 (all prohibit *spoken* lines, none address the platform param).
- **Bug-pattern:** **D34** (detection: *"a silence rule that never mentions `hold_message` is insufficient"*; *"every get_profile-driven agent (KKB in/out, Maya in/out) is exposed"*). Also generic §10 / kkb.md "get_profile's `hold_message` is the neutral hold only" item.
- **proven-fix-available?** **Yes — KKB Kannada Signals clone (D34, 2026-07-29):** add an explicit rule naming `hold_message` and setting it to a **neutral hold** ("एक मिनट" / one moment) for `get_profile` + `create_profile` (things that must not announce their action), listing the reveal phrases never to put in it; allow a genuinely-spoken bridge only on `apply_job`.
- **needs-transcript-to-confirm?** **Yes.** Any inbound call — read `get_profile`/`create_profile` `tool_calls[].function.arguments.hold_message`; a non-empty revealing value = confirmed.
- **backend-or-tool-adherence?** Platform-param behaviour, but the **fix is a prompt rule** (name + neutralise `hold_message`), so it is prose-fixable — not a pure backend escalation.

---

## [LOW] D26 — Canonical Location Spellings list is incomplete vs the Job Inventory (most inventory places unpinned)

- **Symptom:** Places spoken in the flow/examples that are NOT pinned get re-transliterated dynamically/phonetically, so TTS can mispronounce them or render them inconsistently across calls.
- **Evidence:** The Canonical Location Spellings section (lines 650-660) pins only **five** names (Ghaziabad, Indirapuram, Mohan Nagar, Rajendra Nagar, Sector 5). But the Job Inventory and examples speak many more: **Noida, Greater Noida (Knowledge Park II / Sector Alpha II), Meerut, Nehru Nagar, Raj Nagar Extension, PVR Indirapuram, Padmana Naidu Marg, Crossings Republik, Wave City / Aditya World City, Sector 81, Noida SEZ Phase 2** — e.g. Example 1 line 1392 "राज नगर एक्सटेंशन", Example 5 lines 1555/1561 "वेव सिटी"/"आदित्य वर्ल्ड सिटी", Example 3 "ग्रेटर नोएडा". Per D26: *"any place name that appears in the call flow / inventory / example dialogues but is NOT in the canonical list = flag."*
- **Bug-pattern:** **D26.**
- **proven-fix-available?** **Yes — D26 fix (KKB + Maya, 2026-07-24):** extend the "## Canonical Location Spellings" list to cover every inventory place with its exact Devanagari form; mirror script-adapted to the Kannada twin.
- **needs-transcript-to-confirm?** **No** for the completeness gap (statically verifiable against the inventory); a call would only be needed to demonstrate a specific mispronunciation.
- **backend-or-tool-adherence?** No — prose/data fix.

---

## [LOW] D16 — Step-4 apply router keys on "return a profile" vs "returned nothing" but does not explicitly enumerate the empty-array `[]` / zero-records case

- **Symptom:** If `get_profile` returns an **empty array `[]`** for a new caller, a router that only says "returned nothing / a profile was found" could mis-read `[]` as "profile exists → returning path → `apply_job` only", skipping `create_profile` → no `profile_id` → 404.
- **Evidence:** Step 4 checkpoint (lines 598-601): *"Did the `get_profile` call … return a profile? YES → `apply_job` ONLY … NO → `create_profile`, then `apply_job`."* It never spells out "empty array `[]` / empty object / zero records = NOT a profile = NO" (D16's required enumeration). **Largely mitigated** here: the checkpoint ties YES to *"Its result, **containing the profile's `id`**, is still visible above"* (line 598), and lines 466/986/1008 consistently say "returns nothing / no valid profile" — so an empty array reasonably reads as NO. Hardening, not a confirmed break.
- **Bug-pattern:** **D16.**
- **proven-fix-available?** **Yes — D16 fix (Maya outbound, 2026-07-20):** state at the router + NO branch + `apply_job` rules that empty `[]` / zero records = no profile = `create_profile` first.
- **needs-transcript-to-confirm?** **Yes** — a new-caller call where `get_profile` returns `[]`; check whether `apply_job` fires without a preceding `create_profile`.
- **backend-or-tool-adherence?** No — prose fix.

---

## [LOW] D17 — `create_profile` minimum-payload literal template hard-prepends `+91<contact_phone>` (double-prefix landmine)

- **Symptom:** A literal template that unconditionally prepends `+91` can produce `+91+91…` if `${contact_phone}` ever already carries a country code → HTTP 400 / wrong-record lookup.
- **Evidence:** Line 1026 minimum payload: `"phone": "+91<contact_phone>"`; get_profile call template `phoneNumber: +91${contact_phone}` (lines 446, 974). A prose double-prefix guard exists (lines 64, 978, 1018), but D17 explicitly warns *"the literal template is a landmine that can win"* even with a prose guard. **Likely mitigated on this inbound deployment** — Input Variables (line 63) treats caller-ID `${contact_phone}` as bare 10-digit and D17's confirmed breakage was on outbound (where `${contact_phone}` already had `+91`); still the flagged shape per D17.
- **Bug-pattern:** **D17** (also C3 format class).
- **proven-fix-available?** **Yes — D17 fix (2026-07-20):** change templates to an "exactly one `+91`" placeholder (use as-is if already prefixed, prepend only if bare) on BOTH `get_profile` and `create_profile`.
- **needs-transcript-to-confirm?** **Yes** — read `create_profile`/`get_profile` args on a live inbound call and confirm the composed phone is exactly one `+91XXXXXXXXXX`.
- **backend-or-tool-adherence?** No — prose/template fix.

---

## Minor / verify (not full findings)
- **D1 (LOW):** No concrete **banned-hard-word → preferred-simple substitution table** — only a promotional-phrase ban (lines 847-858) plus an allowed-loanword list (624-640). No hard tatsama observed in the spoken lines, so low risk; adding a do/don't lexicon would harden it.
- **E4 / age hard-stop (VERIFY):** Age is collected (Step 3.5) but there is no explicit **minimum-age / eligibility hard-stop**. Universal-core lists one; may be handled backend or intentionally absent for this inventory — verify against a sibling KKB before treating as a gap.

---

**Count by severity: HIGH=2, MED=1, LOW=3** (highest: D31 — new-caller create→apply batched "in a single turn / back to back" → empty `profile_id` → apply fails).
